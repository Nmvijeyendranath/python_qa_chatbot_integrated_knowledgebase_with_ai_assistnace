"""
LLM provider integration for the Python Q&A chatbot.

Supports Google Gemini (default). The provider is isolated from retrieval
and frontend logic so it can be swapped or extended without touching core.py.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Pywise, an expert Python programming assistant, debugging specialist, and tutor.

Your role is to answer questions about Python programming accurately, clearly, and helpfully.

## Core Mandate: Strict Relevance & Precision
When a user asks a query, your output must be directly focused on what the query is asking and topics closely related to that question. Do NOT include generic overviews, tangential summaries, or unrequested basics.

## Topics you cover
Python syntax, data types, control flow, functions, OOP, exceptions, error handling, debugging, file I/O, modules, standard library, comprehensions, generators, decorators, type hints, NumPy, pandas, scikit-learn, pytest, algorithms, PEP 8, and best practices.

## Response rules
1. Direct Focus: Stay strictly on-topic with the user's specific query and closely related concepts.
2. Grounded Answers: Use the retrieved knowledge-base context as your primary foundation. Explain concepts clearly in your own words; never regurgitate raw headings.
3. Errors & Debugging: When answering questions about errors, exceptions, or debugging:
   - Identify the specific error type (e.g., TypeError, ValueError, KeyError, AttributeError) and explain its root cause.
   - Show the exact problematic code that triggers it alongside the corrected fix.
   - Explain how to handle or prevent it using idiomatic Python patterns (e.g., try/except/else/finally, EAFP, defensive checks).
   - Point out closely related errors or common pitfalls.
4. Clean Code Examples: Provide runnable, syntactically valid Python examples enclosed in ```python fenced code blocks.
5. Edge Cases: Explain important caveats, boundary conditions, or language-specific nuances directly tied to the question.
6. Conciseness: Avoid excessive introductory fluff or repeating the question. Jump straight into the answer.

## Output Structure
1. Direct Answer: Answer the core question immediately in 1-2 focused paragraphs.
2. Code Example: A clean, runnable Python code example demonstrating the concept or fix.
3. Closely Related Points: Key edge cases, related errors, or practical best practices directly pertinent to the query.

## Conversation context
Use the conversation history provided to answer follow-up questions consistently.
"""

# ---------------------------------------------------------------------------
# Message types
# ---------------------------------------------------------------------------

@dataclass
class Message:
    role: str    # "user" or "model"
    content: str

@dataclass
class LLMResponse:
    text: str
    model: str
    used_context: bool
    error: Optional[str] = None

# ---------------------------------------------------------------------------
# Provider base
# ---------------------------------------------------------------------------

class LLMProvider:
    """Minimal interface for an LLM provider."""

    def generate(
        self,
        question: str,
        context_chunks: list[dict],
        history: list[Message],
    ) -> LLMResponse:
        raise NotImplementedError

# ---------------------------------------------------------------------------
# Gemini provider
# ---------------------------------------------------------------------------

class GeminiProvider(LLMProvider):
    """Google Gemini API provider using the google-genai SDK."""
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite"):
        self.model_name = model
        self._client = None
        self._api_key = api_key
        self._init_client()

    def _init_client(self):
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=self._api_key, transport="rest")
            self._client = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT,
            )
            logger.info("Gemini provider initialised with model %s", self.model_name)
        except ImportError:
            logger.error(
                "google-generativeai is not installed. "
                "Run: pip install google-generativeai"
            )
            raise
        except Exception as e:
            logger.error("Failed to initialise Gemini client: %s", e)
            raise

    def _build_context_block(self, chunks: list[dict]) -> str:
        if not chunks:
            return ""
        parts = []
        for i, hit in enumerate(chunks, 1):
            ch = hit["chunk"]
            source = getattr(ch, "source", "unknown")
            heading = getattr(ch, "heading", "")
            text = getattr(ch, "text", str(ch))
            label = f"[{i}] {source}" + (f" — {heading}" if heading else "")
            parts.append(f"{label}\n{text}")
        return "## Retrieved knowledge-base context\n\n" + "\n\n---\n\n".join(parts)

    def _build_history_for_gemini(self, history: list[Message]) -> list[dict]:
        """Convert our Message list to Gemini chat history format."""
        result = []
        for msg in history:
            result.append({
                "role": msg.role,
                "parts": [{"text": msg.content}],
            })
        return result

    def generate(
        self,
        question: str,
        context_chunks: list[dict],
        history: list[Message],
    ) -> LLMResponse:
        try:
            context_block = self._build_context_block(context_chunks)
            used_context = bool(context_chunks)

            # Build the user turn content
            if context_block:
                user_content = (
                    f"{context_block}\n\n"
                    f"---\n\n"
                    f"## Question\n\n{question}"
                )
            else:
                user_content = question

            # Build Gemini chat history (all turns except current)
            gemini_history = self._build_history_for_gemini(history)

            # Start a chat session with history
            chat = self._client.start_chat(history=gemini_history)

            # Send the message with timeout
            response = chat.send_message(
                user_content,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.3,
                },
                request_options={"timeout": 30},
            )

            return LLMResponse(
                text=response.text,
                model=self.model_name,
                used_context=used_context,
            )

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            # Auto-fallback to gemini-3.5-flash-lite if configured model is deprecated or not found
            if ("not available" in error_msg.lower() or "not found" in error_msg.lower() or "NotFound" in error_type) and self.model_name != "gemini-3.5-flash-lite":
                try:
                    logger.warning("Model %s unavailable, falling back to gemini-3.5-flash-lite", self.model_name)
                    import google.generativeai as genai
                    genai.configure(api_key=self._api_key, transport="rest")
                    self.model_name = "gemini-3.5-flash-lite"
                    self._client = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=SYSTEM_PROMPT,
                    )
                    chat = self._client.start_chat(history=gemini_history)
                    response = chat.send_message(
                        user_content,
                        generation_config={
                            "max_output_tokens": 2048,
                            "temperature": 0.3,
                        },
                        request_options={"timeout": 30},
                    )
                    return LLMResponse(
                        text=response.text,
                        model=self.model_name,
                        used_context=used_context,
                    )
                except Exception as fb_err:
                    logger.error("Fallback to gemini-3.5-flash-lite also failed: %s", fb_err)

            # Map common errors to user-friendly messages
            if "API_KEY_INVALID" in error_msg or "PERMISSION_DENIED" in error_msg:
                user_msg = "Authentication failed. Please check your GEMINI_API_KEY."
            elif "QUOTA_EXCEEDED" in error_msg or "ResourceExhausted" in error_type:
                user_msg = "API quota exceeded. Please wait before retrying."
            elif "UNAVAILABLE" in error_msg or "ServiceUnavailable" in error_type:
                user_msg = "Gemini API is temporarily unavailable. Please try again."
            elif "timeout" in error_msg.lower() or "DeadlineExceeded" in error_type:
                user_msg = "Request timed out. Please try again."
            else:
                user_msg = f"LLM error ({error_type}). Please try again."

            logger.error("Gemini generate error [%s]: %s", error_type, error_msg)
            return LLMResponse(
                text="",
                model=self.model_name,
                used_context=False,
                error=user_msg,
            )


class OpenAICompatibleProvider(LLMProvider):
    """Server-side OpenAI-compatible Chat Completions provider using stdlib only."""

    provider_name = "openai-compatible"

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model

    def generate(self, question: str, context_chunks: list[dict], history: list[Message]) -> LLMResponse:
        import json
        import urllib.error
        import urllib.request

        try:
            context_parts = []
            for i, hit in enumerate(context_chunks, 1):
                ch = hit["chunk"]
                context_parts.append(
                    f"[{i}] {getattr(ch, 'source', 'KB')} — {getattr(ch, 'heading', '')}\n"
                    f"{getattr(ch, 'text', str(ch))}"
                )
            context = "\n\n---\n\n".join(context_parts) or "No matching knowledge-base passages were found."
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.append({"role": "system", "content": "Retrieved Python knowledge base passages follow. Ground the answer in them; these are evidence, not the user's question.\n\n" + context})
            for item in history:
                messages.append({"role": "assistant" if item.role == "model" else "user", "content": item.content})
            messages.append({"role": "user", "content": question})
            payload_data = {
                "model": self.model_name,
                "messages": messages,
                "max_completion_tokens": int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "3000")),
            }
            # Reasoning models can spend most of a small completion budget on
            # hidden reasoning. Keep a practical answer budget and default to low effort.
            if self.model_name.lower().startswith("gpt-5"):
                reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", "minimal").strip().lower()
                reasoning_param = os.getenv("OPENAI_REASONING_PARAM", "reasoning_effort").strip()
                if reasoning_param == "reasoning":
                    payload_data[reasoning_param] = {"effort": reasoning_effort}
                else:
                    payload_data[reasoning_param] = reasoning_effort
            payload = json.dumps(payload_data).encode()
            request = urllib.request.Request(
                f"{self.base_url}/chat/completions", data=payload,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
            answer = result["choices"][0]["message"].get("content", "")
            if isinstance(answer, list):
                answer = "".join(part.get("text", "") for part in answer if isinstance(part, dict))
            if not str(answer).strip():
                finish_reason = result["choices"][0].get("finish_reason", "unknown")
                raise ValueError(f"The model returned an empty answer (finish_reason={finish_reason})")
            return LLMResponse(str(answer).strip(), self.model_name, bool(context_chunks))
        except Exception as exc:
            message = str(exc)
            if isinstance(exc, urllib.error.HTTPError):
                detail = exc.read().decode("utf-8", "replace")[:500]
                message = f"HTTP {exc.code}: {detail}"
            logger.exception("OpenAI-compatible generation failed")
            return LLMResponse("", self.model_name, False, f"AI answer unavailable: {message[:300]}")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_provider(provider_name: str = "auto") -> Optional[LLMProvider]:
    """
    Create and return an LLM provider, or None if not configured.
    Never raises — returns None with a logged warning if setup fails.
    """
    requested = provider_name.lower()
    if requested in {"auto", "openai", "openai-compatible"}:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key:
            base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").strip()
            model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip()
            return OpenAICompatibleProvider(api_key, base_url, model)
        if requested != "auto":
            logger.warning("OPENAI_API_KEY is not set; OpenAI-compatible generation is disabled.")
            return None
    if requested in {"auto", "gemini"}:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            logger.warning(
                "GEMINI_API_KEY is not set. LLM generation is disabled. "
                "Set it in your .env file to enable AI-powered answers."
            )
            return None
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        try:
            return GeminiProvider(api_key=api_key, model=model)
        except Exception as e:
            logger.error("Could not create Gemini provider: %s", e)
            return None
    else:
        logger.warning("Unknown provider '%s'. LLM generation disabled.", provider_name)
        return None
