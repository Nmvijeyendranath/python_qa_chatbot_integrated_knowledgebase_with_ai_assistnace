# Pywise — Python Knowledge Assistant

An intelligent, retrieval-augmented generation (RAG) question-answering chatbot for Python programming. It combines a curated Python knowledge base with normalized, concept-expanded hybrid retrieval and server-side LLM synthesis to deliver clear answers grounded in source passages.

---

## Architecture Overview

```
                                      +-------------------------+
                                      |   Browser Client (UI)   |
                                      | Minimalist IDE Light Mode |
                                      +------------+------------+
                                                   | HTTP (JSON)
                                                   v
+---------------------------------------------------------------------------------------+
| FastAPI Application Server (main.py)                                                  |
|                                                                                       |
|  +--------------------------+                     +---------------------------------+ |
|  | /api/chat (RAG Pipeline) |                     | /api/query (Retrieval-Only)     | |
|  +------------+-------------+                     +----------------+----------------+ |
|               |                                                    |                  |
|               v                                                    v                  |
|  +---------------------------------------------------------------------------------+  |
|  | Retriever (core.py)                                                             |  |
|  | - Query normalization + Python concept expansion + word/character TF-IDF       |  |
|  | - Atomic code block preservation & metadata enrichment                          |  |
|  | - Confidence thresholding & abstention (default: 0.08)                          |  |
|  +-----------------------------------+---------------------------------------------+  |
|                                      |                                                |
|                                      v                                                |
|                        data/index.json (Chunk Store)                                  |
|                                      |                                                |
+--------------------------------------|------------------------------------------------+
                                       | Context Chunks + History
                                       v
                     +-----------------------------------+
                     | LLM provider (llm.py)             |
                     | OpenAI-compatible or Gemini       |
                     | Grounded answer synthesis         |
                     +-----------------+-----------------+
                                       |
                                       v
                             Configured LLM API
```

### Key Highlights
- **Grounded AI answers**: OpenAI-compatible Chat Completions or Google Gemini synthesizes relevant knowledge-base passages into an explanation; retrieval-only fallback remains available.
- **Query-aware retrieval**: Removes filler words, expands common Python concepts, avoids heading-only hits, suppresses unrelated FAQ passages, and keeps explanatory prose ahead of code for definition questions.
- **Atomic Code Integrity**: The chunking engine guarantees fenced code blocks are never fragmented or mangled during indexing.
- **Session Continuity**: Multi-turn conversation history is tracked per session to enable contextual follow-up questions.
- **Safe & Server-Side Only**: API credentials remain strictly on the backend server and are never exposed to browser clients.
- **High-contrast interface**: Uses an Alabaster Mist canvas with Midnight Slate navigation and headings, Steel Blue Tint dividers, and Python Azure accents. Answers and matching KB excerpts are shown separately.

---

## Knowledge Base Coverage

The chatbot ships with a 29-file Python reference library in `data/knowledge/`:

| Module | Filename | Topics Covered |
|---|---|---|
| **01** | `01-fundamentals.md` | Data types, type casting, arithmetic/bitwise operators, memory model, variable naming |
| **02** | `02-control-flow.md` | Conditionals, pattern matching (`match/case`), loops, `break/continue/else`, comprehensions |
| **03** | `03-data-structures.md` | `list`, `tuple`, `set`, `dict`, time complexities, slicing, operations, mutations |
| **04** | `04-functions.md` | `*args`, `**kwargs`, closures, scope (LEGB), `lambda`, type hints, recursion |
| **05** | `05-strings.md` | f-strings, `format()`, regex integration, string immutability, common utility methods |
| **06** | `06-oop.md` | Classes, `__init__`, inheritance, encapsulation, polymorphism, `@property`, dunder methods, dataclasses |
| **07** | `07-exceptions-debugging.md` | `try/except/else/finally`, custom exceptions, exception chaining, `logging`, `pdb` |
| **08** | `08-files-modules.md` | File I/O, `pathlib.Path`, context managers, `import`, packages, `pip`, `venv` |
| **09** | `09-advanced-python.md` | Iterators, generators (`yield`), decorators, context managers (`@contextmanager`), `typing` |
| **10** | `10-numpy.md` | `ndarray`, broadcasting rules, vectorization, indexing/slicing, linear algebra, performance |
| **11** | `11-pandas.md` | `Series`, `DataFrame`, reading CSV/Excel, filtering, `groupby`, aggregations, merging/joining |
| **12** | `12-sklearn.md` | Model workflows, `Pipeline`, `StandardScaler`, cross-validation, train-test split, metrics |
| **13** | `13-testing-pytest.md` | `pytest` test functions, fixtures, parametrize, mocking with `unittest.mock`, test discovery |
| **14** | `14-algorithms.md` | Two pointers, binary search, sliding window, DFS/BFS, dynamic programming, Big-O notation |
| **15** | `15-best-practices.md` | PEP 8, clean code principles, refactoring, naming conventions, docstrings, typing |
| **16** | `16-interview-errors.md` | Mutable default args, late-binding closures, `is` vs `==`, common interview questions |
| **00** | `00-python-overview.md` | Python language overview, common uses, execution model, first program |
| **Supplemental** | `11-classes-and-objects.md` | Class vs object, object lifecycle, `__new__` vs `__init__`, immutable subclasses, identity/equality, MRO, composition |

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 2. Clone and Setup Environment

#### Windows (PowerShell)
```powershell
# Navigate into repository
cd pywise-python-assistant

# Create virtual environment
py -3.13 -m venv .venv
# Or: python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install package and test dependencies
pip install -e ".[test]"
```

#### macOS / Linux (Bash)
```bash
# Navigate into repository
cd pywise-python-assistant

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install package and test dependencies
pip install -e ".[test]"
```

---

### 3. Configure a server-side AI provider

Pywise uses the knowledge base for retrieval, then asks an LLM to explain the retrieved material in a direct answer. The LLM key stays on the server and is never sent to the browser. Without a key, retrieval mode remains available.

Copy `.env.example` to `.env` and configure **one** provider:

- **OpenAI-compatible API:** set `OPENAI_API_KEY`; optionally set `OPENAI_API_BASE` and `OPENAI_MODEL`.
- **Google Gemini:** set `QA_LLM_PROVIDER=gemini` and `GEMINI_API_KEY`.
- **Automatic selection:** `QA_LLM_PROVIDER=auto` (default) uses OpenAI when `OPENAI_API_KEY` is present, otherwise Gemini when `GEMINI_API_KEY` is present.

Never commit `.env` or expose API keys in frontend code. The assistant receives relevant retrieved passages and is instructed to synthesize an explanation rather than repeat search headings.

---

### 4. Build the Knowledge Index

Before starting the server, run the ingestion process to parse and index all knowledge base documents into `data/index.json`:

```powershell
python -m qa_chatbot.ingest --data data/knowledge --output data/index.json
```
*Expected output: `Indexed approximately 1,000 chunks from data/knowledge -> data/index.json`*

---

### 5. Launch the Server

Start the FastAPI application with Uvicorn:

```powershell
uvicorn qa_chatbot.main:app --app-dir src --reload
```

- Web UI: **http://127.0.0.1:8000**
- Interactive Swagger API Documentation: **http://127.0.0.1:8000/docs**
- Health Check: **http://127.0.0.1:8000/health**

---

## Running the Test Suite

A comprehensive test suite verifies core chunking, retrieval accuracy, threshold calibration, and API endpoints without making external network calls:

```powershell
pytest -v
```

To run with coverage:
```powershell
pytest --cov=src/qa_chatbot tests/
```

---

## REST API Reference

### 1. `POST /api/chat` (RAG Pipeline)
Submits a user question to the RAG pipeline.

**Request Body:**
```json
{
  "question": "What is the difference between deepcopy and shallow copy in Python?",
  "session_id": "session-1234",
  "use_llm": true,
  "top_k": 3
}
```

**Response Body:**
```json
{
  "answer": "In Python, a shallow copy constructs a new collection object and populates it with references to child objects...",
  "sources": [
    {
      "chunk_id": "03-data-structures-chunk-4",
      "source": "data/knowledge/03-data-structures.md",
      "heading": "Copying: Shallow vs Deep",
      "score": 0.42
    }
  ],
  "confidence": 0.42,
  "abstained": false,
  "session_id": "session-1234",
  "used_llm": true
}
```

### 2. `POST /api/chat/clear`
Clears multi-turn conversation memory for a session.

**Request Body:**
```json
{
  "session_id": "session-1234"
}
```

### 3. `POST /api/query`
Direct lexical retrieval query (backward compatible endpoint, returns verbatim chunks without LLM synthesis).

### 4. `GET /health`
Returns service status, total indexed chunks, and LLM provider availability:
```json
{
  "status": "ok",
  "chunks_loaded": 184,
  "retriever_ready": true,
  "llm_available": true,
  "llm_provider": "gemini"
}
```

---

## Security & Privacy

- **No Secret Leakage**: The `.env` file is excluded from Git via `.gitignore`.
- **Server-Side API Calls**: Browser clients never interact with Google Gemini directly.
- **Sandboxed Execution**: Code snippets are presented for educational purposes and are never executed on the host server.

---

## Troubleshooting

- **Server starts with 0 chunks loaded**: Run `python -m qa_chatbot.ingest --data data/knowledge --output data/index.json` and restart Uvicorn.
- **LLM shows "AI Unavailable"**: Check that `GEMINI_API_KEY` in `.env` is valid and contains no quotes or leading/trailing whitespace.
- **Port 8000 already in use**: Start Uvicorn on another port with `--port 8001`.
