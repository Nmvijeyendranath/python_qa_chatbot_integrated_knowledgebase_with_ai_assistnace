# Next-Agent Context

This repository is a production-quality, RAG-enabled Python Q&A chatbot built with FastAPI, scikit-learn TF-IDF retrieval, and Google Gemini LLM generation.

## Architecture Highlights
- **Retrieval Engine (`src/qa_chatbot/core.py`)**: Preserved original architecture. Uses word (1-2 gram) and char (3-5 gram) TF-IDF indexing. Atomic fenced code block preservation ensures code snippets are never broken across chunk boundaries.
- **Ingestion (`src/qa_chatbot/ingest.py`)**: Crawls `data/knowledge/` (Markdown & JSON) and compiles `data/index.json`. Run this CLI whenever documents are updated.
- **LLM Integration (`src/qa_chatbot/llm.py`)**: Contains `GeminiProvider` utilizing the `google-generativeai` SDK. Supports system instructions, multi-turn chat, graceful rate-limit/network error fallback, and safe instantiation via `create_provider()`.
- **API Server (`src/qa_chatbot/main.py`)**:
  - `POST /api/chat`: Primary RAG pipeline. Retrieves top chunks, manages in-memory multi-turn session history (`_conversation_store`), and delegates to Gemini with strict citation and context grounding.
  - `POST /api/chat/clear`: Evicts session history.
  - `POST /api/query`: Legacy retrieval-only verbatim endpoint.
  - `GET /health`: Reports index readiness and LLM availability.
- **Frontend UI (`static/index.html`)**: Self-contained single-page application with modern dark glassmorphism design, JetBrains Mono font, markdown rendering, syntax highlighting, copy-code buttons, AI toggle, and citation sources display.
- **Knowledge Base (`data/knowledge/`)**: 16 categorized markdown files covering Python fundamentals, control flow, data structures, functions, OOP, exceptions, modules/venv, advanced features (iterators, generators, decorators), data science (numpy, pandas, scikit-learn), testing (pytest), algorithms, best practices (PEP 8), and common interview traps.

## Design Constraints & Guidance
- **Strict Server-Side Credentials**: Never expose `GEMINI_API_KEY` to client endpoints.
- **Graceful Degradation**: Always preserve retrieval-only fallback if LLM credentials are missing or exceed rate limits.
- **Fenced Code Blocks**: Preserve indentation, syntax, and language annotations during chunking and rendering.
- **Testing**: Tests in `tests/` must mock all external LLM network calls using `unittest.mock`.
