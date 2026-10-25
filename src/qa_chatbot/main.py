"""
FastAPI application — Personal Python Q&A Chatbot.

Endpoints:
  GET  /              → static UI
  GET  /health        → health check
  POST /api/query     → retrieval-only (backward-compatible)
  POST /api/chat      → RAG: retrieval + LLM generation
  POST /api/chat/clear → clear conversation history for a session
"""
from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .core import Retriever, load_chunks
from .llm import Message, create_provider

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Personal Python Q&A Chatbot",
    description="RAG-powered Python programming assistant with Gemini LLM.",
    version="0.2.0",
)

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[2]
INDEX = Path(os.getenv("QA_INDEX_PATH", "data/index.json"))
if not INDEX.is_absolute():
    INDEX = BASE / INDEX

CONFIDENCE_THRESHOLD = float(os.getenv("QA_CONFIDENCE_THRESHOLD", "0.08"))
TOP_K = int(os.getenv("QA_TOP_K", "5"))
ENABLE_RERANKER = os.getenv("QA_ENABLE_RERANKER", "false").lower() == "true"
LLM_PROVIDER = os.getenv("QA_LLM_PROVIDER", "auto")
# Max conversation turns kept per session (older turns are dropped)
MAX_HISTORY_TURNS = int(os.getenv("QA_MAX_HISTORY_TURNS", "10"))

# ---------------------------------------------------------------------------
# Load retriever
# ---------------------------------------------------------------------------
CHUNKS = load_chunks(INDEX) if INDEX.exists() else []
if not CHUNKS:
    logger.warning(
        "No chunks loaded from %s. Run the ingestion command first: "
        "python -m qa_chatbot.ingest --data data/knowledge --output data/index.json",
        INDEX,
    )

# Headings are metadata, not answer content. Indexing question-style headings as
# passages caused exact question matches to outrank their explanatory paragraphs.
SEARCH_CHUNKS = [
    chunk for chunk in CHUNKS
    if chunk.kind != "heading"
    and chunk.text.strip()
    and not re.fullmatch(r"Source:\s*https?://\S+", chunk.text.strip(), re.I)
]
retriever = Retriever(
    SEARCH_CHUNKS,
    threshold=CONFIDENCE_THRESHOLD,
    rerank=ENABLE_RERANKER,
)

# ---------------------------------------------------------------------------
# LLM provider (optional — degrades gracefully to retrieval-only)
# ---------------------------------------------------------------------------
def reload_llm_provider():
    global llm_provider, LLM_PROVIDER
    env_file = BASE / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
    LLM_PROVIDER = os.getenv("QA_LLM_PROVIDER", "auto")
    llm_provider = create_provider(LLM_PROVIDER)
    return llm_provider

llm_provider = create_provider(LLM_PROVIDER)
if llm_provider:
    logger.info("LLM provider ready (%s)", LLM_PROVIDER)
else:
    logger.info(
        "LLM provider not configured. Set GEMINI_API_KEY for AI-powered answers."
    )

# ---------------------------------------------------------------------------
# In-memory conversation history store  {session_id: [Message, ...]}
# ---------------------------------------------------------------------------
_conversation_store: dict[str, list[Message]] = {}

FAQ = [
    (
        re.compile(r"\b(hello|hi|hey|howdy)\b", re.I),
        "Hello! I'm PyBot, your Python programming assistant. "
        "Ask me anything about Python — syntax, debugging, data structures, "
        "NumPy, pandas, machine learning, or anything else Python-related!",
    ),
    (
        re.compile(r"\b(what can you do|help|capabilities)\b", re.I),
        (
            "I can help you with:\n"
            "• Python syntax, fundamentals, and data types\n"
            "• Functions, OOP, and advanced patterns\n"
            "• Exceptions, debugging, and error messages\n"
            "• NumPy, pandas, and scikit-learn\n"
            "• Algorithms, sorting, and time complexity\n"
            "• Testing with pytest\n"
            "• PEP 8 and best practices\n\n"
            "Just ask your question!"
        ),
    ),
]

# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=TOP_K, ge=1, le=20)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None)
    top_k: int = Field(default=TOP_K, ge=1, le=20)
    use_llm: bool = Field(default=True)


class ClearRequest(BaseModel):
    session_id: str


class KeyConfigRequest(BaseModel):
    provider: str = Field(default="gemini")
    api_key: str = Field(min_length=1)
    model: Optional[str] = None


# ---------------------------------------------------------------------------
# Static files and root
# ---------------------------------------------------------------------------
STATIC_DIR = BASE / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    html = STATIC_DIR / "index.html"
    if not html.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(html))


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    global llm_provider
    if llm_provider is None:
        reload_llm_provider()
    return {
        "status": "ok",
        "chunks": len(CHUNKS),
        "index_loaded": INDEX.exists(),
        "llm_available": llm_provider is not None,
        "llm_provider": getattr(llm_provider, "provider_name", LLM_PROVIDER) if llm_provider else None,
    }


# ---------------------------------------------------------------------------
# Key Configuration Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/config/key")
def configure_key(body: KeyConfigRequest):
    """Dynamically set and persist API key without restarting server."""
    global llm_provider, LLM_PROVIDER
    key = body.api_key.strip()
    provider = body.provider.strip().lower()
    model = (body.model or "").strip()

    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")

    if provider == "gemini":
        os.environ["GEMINI_API_KEY"] = key
        os.environ["QA_LLM_PROVIDER"] = "gemini"
        if model:
            os.environ["GEMINI_MODEL"] = model
    elif provider in {"openai", "openai-compatible"}:
        os.environ["OPENAI_API_KEY"] = key
        os.environ["QA_LLM_PROVIDER"] = "openai"
        if model:
            os.environ["OPENAI_MODEL"] = model
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider. Use 'gemini' or 'openai'.")

    new_provider = create_provider(provider)
    if not new_provider:
        raise HTTPException(status_code=400, detail="Failed to initialize provider with the given key.")

    llm_provider = new_provider
    LLM_PROVIDER = provider

    # Persist into .env file
    env_file = BASE / ".env"
    try:
        lines = []
        if env_file.exists():
            lines = env_file.read_text(encoding="utf-8").splitlines()
        
        target_key = "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"
        target_model = "GEMINI_MODEL" if provider == "gemini" else "OPENAI_MODEL"
        updated_provider = False
        updated_key = False
        updated_model = False
        new_lines = []

        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith("QA_LLM_PROVIDER="):
                new_lines.append(f"QA_LLM_PROVIDER={provider}")
                updated_provider = True
            elif trimmed.startswith(f"{target_key}="):
                new_lines.append(f"{target_key}={key}")
                updated_key = True
            elif model and trimmed.startswith(f"{target_model}="):
                new_lines.append(f"{target_model}={model}")
                updated_model = True
            else:
                new_lines.append(line)

        if not updated_provider:
            new_lines.append(f"QA_LLM_PROVIDER={provider}")
        if not updated_key:
            new_lines.append(f"{target_key}={key}")
        if model and not updated_model:
            new_lines.append(f"{target_model}={model}")

        env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        logger.info("Updated API key configuration in %s", env_file)
    except Exception as exc:
        logger.warning("Could not persist key to .env: %s", exc)

    return {
        "status": "ok",
        "llm_available": True,
        "llm_provider": getattr(new_provider, "provider_name", provider),
    }


# ---------------------------------------------------------------------------
# Query Processing & Retrieval Enhancement
# ---------------------------------------------------------------------------

QUERY_STOPWORDS = {
    "what", "whats", "is", "the", "how", "does", "do", "in", "a", "an", "of",
    "to", "and", "or", "for", "can", "you", "tell", "me", "actually", "work",
    "works", "working", "mean", "means", "explain", "about", "give", "example",
    "examples", "i", "want", "know", "please", "difference", "between", "versus", "vs",
    "used", "use", "using", "with", "why", "when", "where", "which", "are", "was", "were",
    "it", "its", "this", "that", "from", "on", "at", "by", "as", "be", "doesnt",
}


def smart_search(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Normalize question phrasing, expand common Python concepts, and blend word/character
    similarity with passage coverage while excluding heading-only and unrelated FAQ hits.
    """
    clean_query = query.strip()
    if not clean_query or not CHUNKS:
        return []

    tokens = [
        w.lower()
        for w in re.findall(r"\b[\w.-]+\b", clean_query)
        if w.lower() not in QUERY_STOPWORDS and len(w) > 1
    ]
    keywords = " ".join(tokens) or clean_query

    # Lightweight domain query expansion complements lexical matching. It is
    # intentionally additive: the original user terms remain the strongest signal.
    concept_expansions = {
        "python": "python programming language interpreted high-level general-purpose overview",
        "numpy": "numpy numerical computing multidimensional ndarray array library",
        "pandas": "pandas dataframe tabular data analysis library series",
        "decorator": "decorator wrapper function higher-order function functools",
        "decorators": "decorator wrapper function higher-order function functools",
        "tuple": "tuple immutable sequence hashable parentheses",
        "tuples": "tuple immutable sequence hashable parentheses",
        "list": "list mutable ordered sequence brackets",
        "lists": "list mutable ordered sequence brackets",
        "async": "asyncio asynchronous await coroutine event loop",
        "error": "exception try except raise traceback error handling debugging errors",
        "errors": "exception try except raise traceback error handling debugging errors",
        "exception": "exceptions try except finally raise custom exception hierarchy",
        "exceptions": "exception try except finally raise custom exception hierarchy",
        "typeerror": "TypeError type mismatch operand type non-callable NoneType",
        "valueerror": "ValueError invalid literal unpacking length conversion",
        "attributeerror": "AttributeError object has no attribute NoneType method",
        "keyerror": "KeyError dict dictionary key get missing default",
        "indexerror": "IndexError list sequence out of range index boundary",
        "nameerror": "NameError name not defined scope variable LEGB",
        "unboundlocalerror": "UnboundLocalError local variable referenced before assignment global nonlocal",
        "filenotfounderror": "FileNotFoundError file path directory open read",
        "recursionerror": "RecursionError maximum recursion depth exceeded base case",
        "handling": "try except else finally error handling robust defensive",
        "traceback": "traceback stack trace error debugging line number",
        "class": "object-oriented class instance inheritance methods",
        "classes": "object-oriented class instance inheritance methods",
        "__new__": "__init__ object creation allocation instantiate constructor immutable object lifecycle override",
        "__init__": "__new__ object initialization instance attributes constructor lifecycle",
        "override": "subclass customize replace method inherited behavior",
    }
    expansion_terms = " ".join(dict.fromkeys(
        term for token in tokens for term in concept_expansions.get(token, "").split()
    ))
    expanded_query = f"{keywords} {expansion_terms}".strip()
    candidate_k = max(top_k * 8, 40)
    hits_a = {h["chunk"].id: h for h in retriever.search(keywords, top_k=candidate_k)}
    hits_b = {h["chunk"].id: h for h in retriever.search(expanded_query, top_k=candidate_k)} if expansion_terms else {}

    all_ids = set(hits_a.keys()) | set(hits_b.keys())
    combined = []
    for cid in all_ids:
        chunk = hits_a[cid]["chunk"] if cid in hits_a else hits_b[cid]["chunk"]
        sa = hits_a[cid]["score"] if cid in hits_a else 0.0
        sb = hits_b[cid]["score"] if cid in hits_b else 0.0
        base_score = 0.5 * sa + 0.5 * sb

        full_text = f"{chunk.heading} {chunk.text}".lower()
        if tokens:
            matches = sum(1 for t in tokens if t in full_text)
            match_ratio = matches / len(tokens)
            final_score = base_score * (0.75 + 0.25 * match_ratio)

            # Prioritize chunks directly covering non-generic query tokens
            specific_tokens = [t for t in tokens if t not in {"python", "what", "how", "explain", "code", "example"}]
            if specific_tokens:
                specific_matches = sum(1 for t in specific_tokens if t in full_text)
                if specific_matches > 0:
                    final_score *= (1.0 + 0.4 * (specific_matches / len(specific_tokens)))
                else:
                    final_score *= 0.45

            # FAQ documents pack many different Q&As into one chunk. If the
            # embedded question is about another topic, don't let shared generic
            # words such as "difference" or "list" make that whole chunk rank.
            embedded = re.search(r"(?:\*\*)?Q:\s*(.+?)(?:\*\*)?(?:\n|$)", chunk.text, re.I)
            if embedded:
                embedded_text = f"{embedded.group(1)} {chunk.text}".lower()
                q_terms = [t for t in tokens if len(t) > 2]
                q_coverage = sum(1 for t in q_terms if t in embedded_text) / max(1, len(q_terms))
                if q_coverage < 0.75:
                    final_score *= 0.35
        else:
            final_score = base_score

        # Put a matching explanation ahead of its sample code in the answer.
        if chunk.kind == "code":
            asks_for_code = any(term in {"example", "code", "snippet", "install", "command", "run"} for term in tokens)
            final_score *= 0.90 if asks_for_code else 0.55
        if tokens == ["python"] and chunk.source.endswith("00-python-overview.md"):
            if chunk.heading in {"What Python is", "Why people use Python", "How a Python program runs"}:
                final_score *= 2.0
        combined.append({"chunk": chunk, "score": round(min(final_score, 1.0), 4)})

    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined[:top_k]


def format_retrieval_answer(accepted: list[dict]) -> str:
    """Format retrieved chunks into a clear, structured markdown answer."""
    if not accepted:
        return (
            "I don't have enough information in the knowledge base to answer that "
            "confidently. Try rephrasing your question or checking Python documentation."
        )

    sections = []
    for i, h in enumerate(accepted):
        chunk = h["chunk"]
        heading = chunk.heading.strip()
        if not heading:
            src_stem = Path(chunk.source).stem
            heading = src_stem.replace("-", " ").title()

        # A question-shaped section heading is useful as a source label, but
        # repeating it as if it were an answer is confusing. Keep headings concise.
        display_heading = re.sub(r"^Q:\s*", "", heading, flags=re.I).strip()
        if i == 0:
            sections.append(f"### Knowledge-base answer\n\n{chunk.text}")
        else:
            sections.append(f"### Supporting reference: {display_heading}\n\n{chunk.text}")

    return "\n\n---\n\n".join(sections)


# ---------------------------------------------------------------------------
# /api/query — backward-compatible retrieval-only endpoint
# ---------------------------------------------------------------------------

@app.post("/api/query")
def query(body: QueryRequest):
    """Retrieval-only endpoint (structured knowledge excerpts, no LLM generation)."""
    for pattern, response in FAQ:
        if pattern.search(body.question):
            return {
                "answer": response,
                "abstained": False,
                "confidence": 1.0,
                "sources": [],
                "matches": [],
                "intent": "greeting_or_help",
                "llm_used": False,
            }

    hits = smart_search(body.question, body.top_k)
    top_score = hits[0]["score"] if hits else 0.0
    min_thresh = (
        max(CONFIDENCE_THRESHOLD, min(0.12, top_score * 0.45))
        if top_score >= CONFIDENCE_THRESHOLD
        else CONFIDENCE_THRESHOLD
    )
    accepted = [h for h in hits if h["score"] >= min_thresh]

    if not accepted:
        return {
            "answer": "I don't have enough information in the available knowledge base to answer that confidently.",
            "abstained": True,
            "confidence": top_score,
            "sources": [],
            "matches": [],
            "intent": "knowledge_query",
            "llm_used": False,
        }

    refs = [
        {
            "id": h["chunk"].id,
            "source": h["chunk"].source,
            "heading": h["chunk"].heading,
            "score": round(h["score"], 4),
            "kind": h["chunk"].kind,
            "language": h["chunk"].language,
            "version": getattr(h["chunk"], "version", ""),
        }
        for h in accepted
    ]
    answer = format_retrieval_answer(accepted)
    return {
        "answer": answer,
        "abstained": False,
        "confidence": round(top_score, 4),
        "sources": refs,
        "matches": refs,
        "intent": "knowledge_query",
        "llm_used": False,
    }


# ---------------------------------------------------------------------------
# /api/chat — RAG endpoint (retrieval + LLM)
# ---------------------------------------------------------------------------

@app.post("/api/chat")
def chat(body: ChatRequest):
    """
    RAG endpoint: retrieve relevant knowledge then generate an LLM answer.
    Falls back to structured retrieval-only if LLM is unavailable or errors.
    """
    question = body.question.strip()

    # --- FAQ short-circuit (no LLM call for greetings) ---
    for pattern, response in FAQ:
        if pattern.search(question):
            return {
                "answer": response,
                "abstained": False,
                "confidence": 1.0,
                "sources": [],
                "llm_used": False,
                "session_id": body.session_id or str(uuid.uuid4()),
                "intent": "greeting_or_help",
            }

    # --- Session management ---
    session_id = body.session_id or str(uuid.uuid4())
    if session_id not in _conversation_store:
        _conversation_store[session_id] = []
    history = _conversation_store[session_id]

    # --- Retrieval ---
    hits = smart_search(question, body.top_k)
    top_score = hits[0]["score"] if hits else 0.0
    min_thresh = (
        max(CONFIDENCE_THRESHOLD, min(0.12, top_score * 0.45))
        if top_score >= CONFIDENCE_THRESHOLD
        else CONFIDENCE_THRESHOLD
    )
    accepted = [h for h in hits if h["score"] >= min_thresh]

    sources = [
        {
            "id": h["chunk"].id,
            "source": h["chunk"].source,
            "heading": h["chunk"].heading,
            "score": round(h["score"], 4),
            "kind": h["chunk"].kind,
            "language": h["chunk"].language,
        }
        for h in accepted
    ]
    confidence = round(top_score, 4)

    # --- LLM generation ---
    global llm_provider
    if llm_provider is None:
        reload_llm_provider()
    use_llm = body.use_llm and llm_provider is not None

    if use_llm:
        # Pass accepted hits (or all hits if none passed threshold, so LLM still has context)
        context_for_llm = accepted if accepted else hits[:3]
        response = llm_provider.generate(question, context_for_llm, history)

        if response.error:
            # LLM failed — fall back to structured retrieval
            logger.warning("LLM error, falling back to retrieval: %s", response.error)
            answer = format_retrieval_answer(accepted)
            return {
                "answer": answer,
                "abstained": not accepted,
                "confidence": confidence,
                "sources": sources,
                "llm_used": False,
                "llm_error": response.error,
                "knowledge_context": [{"heading": h["chunk"].heading, "source": h["chunk"].source, "text": h["chunk"].text} for h in accepted],
                "session_id": session_id,
                "intent": "knowledge_query",
            }

        answer = response.text
        llm_used = True

        # Update conversation history
        history.append(Message(role="user", content=question))
        history.append(Message(role="model", content=answer))

        # Trim history to max turns (each turn = 2 messages)
        max_msgs = MAX_HISTORY_TURNS * 2
        if len(history) > max_msgs:
            _conversation_store[session_id] = history[-max_msgs:]

    else:
        # Structured retrieval-only fallback
        answer = format_retrieval_answer(accepted)
        llm_used = False

    return {
        "answer": answer,
        "abstained": not accepted and not llm_used,
        "confidence": confidence,
        "sources": sources,
        "knowledge_context": [{"heading": h["chunk"].heading, "source": h["chunk"].source, "text": h["chunk"].text} for h in accepted],
        "llm_used": llm_used,
        "session_id": session_id,
        "intent": "knowledge_query",
    }


# ---------------------------------------------------------------------------
# /api/chat/clear
# ---------------------------------------------------------------------------

@app.post("/api/chat/clear")
def clear_chat(body: ClearRequest):
    """Clear the conversation history for a session."""
    if body.session_id in _conversation_store:
        del _conversation_store[body.session_id]
    return {"cleared": True, "session_id": body.session_id}


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )
