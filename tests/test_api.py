"""
Tests for the FastAPI application endpoints.
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ── App fixture ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """Create test client; LLM is not required for these tests."""
    from qa_chatbot.main import app
    return TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
        assert "chunks" in d
        assert "llm_available" in d
        assert "index_loaded" in d

    def test_health_chunks_non_negative(self, client):
        r = client.get("/health")
        assert r.json()["chunks"] >= 0


# ── Static / root ─────────────────────────────────────────────────────────

class TestRoot:
    def test_root_returns_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")


# ── /api/query endpoint (retrieval-only, backward-compatible) ─────────────

class TestQueryEndpoint:
    def test_greeting_faq(self, client):
        r = client.post("/api/query", json={"question": "hello"})
        assert r.status_code == 200
        d = r.json()
        assert d["intent"] == "greeting_or_help"
        assert d["abstained"] is False

    def test_help_faq(self, client):
        r = client.post("/api/query", json={"question": "what can you do"})
        assert r.status_code == 200
        d = r.json()
        assert d["intent"] == "greeting_or_help"

    def test_new_vs_init_override_scenario_is_retrieved(self, client):
        question = "What is the difference between __init__ and __new__, and in what scenario would you actually need to override __new__?"
        r = client.post("/api/query", json={"question": question})
        assert r.status_code == 200
        d = r.json()
        answer = d["answer"].lower()
        assert "allocat" in answer or "creat" in answer
        assert "initial" in answer
        assert "immutable" in answer or "string subclass" in answer or "str" in answer
        assert any("classes-and-objects" in source["source"] or "06-oop.md" in source["source"] for source in d["sources"])

    def test_question_match_returns_explanation_not_heading(self, client):
        r = client.post("/api/query", json={"question": "What is the difference between a list and a tuple?"})
        assert r.status_code == 200
        d = r.json()
        assert d["sources"]
        assert "mutable" in d["answer"].lower()
        assert "Primary Answer: Q:" not in d["answer"]
        assert all(source["kind"] != "heading" for source in d["sources"])

    def test_broad_python_question_returns_definition_not_install_command(self, client):
        r = client.post("/api/query", json={"question": "What is Python?"})
        assert r.status_code == 200
        d = r.json()
        assert "programming language" in d["answer"].lower()
        assert "pip install" not in d["answer"].lower()
        assert d["sources"]
        assert all(source["kind"] != "heading" for source in d["sources"])

    def test_numpy_definition_ranks_explanation_above_install_snippet(self, client):
        r = client.post("/api/query", json={"question": "What is NumPy?"})
        assert r.status_code == 200
        d = r.json()
        assert "numerical computing" in d["answer"].lower()
        assert d["answer"].find("numerical computing") < d["answer"].find("pip install")

    def test_python_question_returns_answer(self, client):
        r = client.post("/api/query", json={"question": "What is a Python list?"})
        assert r.status_code == 200
        d = r.json()
        assert "answer" in d
        assert "sources" in d
        assert "confidence" in d
        assert "abstained" in d
        assert d["llm_used"] is False

    def test_empty_question_rejected(self, client):
        r = client.post("/api/query", json={"question": ""})
        assert r.status_code == 422  # Pydantic validation error

    def test_question_too_long_rejected(self, client):
        r = client.post("/api/query", json={"question": "x" * 4001})
        assert r.status_code == 422

    def test_top_k_out_of_range_rejected(self, client):
        r = client.post("/api/query", json={"question": "Python list", "top_k": 25})
        assert r.status_code == 422

    def test_response_fields_present(self, client):
        r = client.post("/api/query", json={"question": "Python functions"})
        d = r.json()
        assert all(k in d for k in ["answer", "abstained", "confidence", "sources", "llm_used"])


# ── /api/chat endpoint (RAG) ──────────────────────────────────────────────

class TestChatEndpoint:
    def test_greeting_short_circuit(self, client):
        r = client.post("/api/chat", json={"question": "hi there"})
        assert r.status_code == 200
        d = r.json()
        assert d["intent"] == "greeting_or_help"
        assert "session_id" in d

    def test_chat_returns_session_id(self, client):
        r = client.post("/api/chat", json={"question": "Python lists", "use_llm": False})
        assert r.status_code == 200
        d = r.json()
        assert "session_id" in d
        assert isinstance(d["session_id"], str)
        assert len(d["session_id"]) > 0

    def test_chat_without_llm(self, client):
        r = client.post("/api/chat", json={
            "question": "How do Python lists work?",
            "use_llm": False,
        })
        assert r.status_code == 200
        d = r.json()
        assert "answer" in d
        assert d["llm_used"] is False

    def test_chat_with_mocked_llm(self, client):
        """Test that LLM response is returned when provider is available."""
        mock_response = MagicMock()
        mock_response.text = "Python lists are ordered mutable sequences."
        mock_response.model = "gemini-1.5-flash"
        mock_response.used_context = True
        mock_response.error = None

        mock_provider = MagicMock()
        mock_provider.generate.return_value = mock_response

        import qa_chatbot.main as main_module
        original = main_module.llm_provider
        main_module.llm_provider = mock_provider
        try:
            r = client.post("/api/chat", json={
                "question": "How do Python lists work?",
                "use_llm": True,
            })
            assert r.status_code == 200
            d = r.json()
            assert d["answer"] == "Python lists are ordered mutable sequences."
            assert d["llm_used"] is True
        finally:
            main_module.llm_provider = original

    def test_chat_llm_error_fallback(self, client):
        """When LLM returns an error, should fall back to retrieval."""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.model = "gemini-1.5-flash"
        mock_response.used_context = False
        mock_response.error = "Rate limit exceeded"

        mock_provider = MagicMock()
        mock_provider.generate.return_value = mock_response

        import qa_chatbot.main as main_module
        original = main_module.llm_provider
        main_module.llm_provider = mock_provider
        try:
            r = client.post("/api/chat", json={
                "question": "Python lists",
                "use_llm": True,
            })
            assert r.status_code == 200
            d = r.json()
            assert d["llm_used"] is False
            assert "llm_error" in d
        finally:
            main_module.llm_provider = original

    def test_clear_conversation(self, client):
        # First, start a session
        r = client.post("/api/chat", json={"question": "Hello"})
        session_id = r.json()["session_id"]

        # Clear it
        r2 = client.post("/api/chat/clear", json={"session_id": session_id})
        assert r2.status_code == 200
        d = r2.json()
        assert d["cleared"] is True
        assert d["session_id"] == session_id

    def test_clear_nonexistent_session(self, client):
        r = client.post("/api/chat/clear", json={"session_id": "nonexistent-session-xyz"})
        assert r.status_code == 200
        assert r.json()["cleared"] is True

    def test_empty_question_rejected(self, client):
        r = client.post("/api/chat", json={"question": ""})
        assert r.status_code == 422


# ── LLM module unit tests ─────────────────────────────────────────────────

class TestLLMModule:
    def test_create_provider_no_key_returns_none(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        from qa_chatbot.llm import create_provider
        provider = create_provider("gemini")
        assert provider is None

    def test_create_provider_empty_key_returns_none(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "")
        from qa_chatbot.llm import create_provider
        provider = create_provider("gemini")
        assert provider is None

    def test_create_provider_unknown_name_returns_none(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        from qa_chatbot.llm import create_provider
        provider = create_provider("unknown_provider")
        assert provider is None

    def test_system_prompt_not_empty(self):
        from qa_chatbot.llm import SYSTEM_PROMPT
        assert len(SYSTEM_PROMPT) > 100
        assert "Python" in SYSTEM_PROMPT

    def test_gemini_provider_missing_library(self, monkeypatch):
        """GeminiProvider raises ImportError when google-generativeai not installed."""
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "google.generativeai":
                raise ImportError("No module named 'google.generativeai'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        from qa_chatbot.llm import GeminiProvider
        with pytest.raises(ImportError):
            GeminiProvider(api_key="fake")

    def test_message_dataclass(self):
        from qa_chatbot.llm import Message
        m = Message(role="user", content="Hello")
        assert m.role == "user"
        assert m.content == "Hello"


# ── Key configuration tests ───────────────────────────────────────────────

class TestKeyConfig:
    def test_empty_key_rejected(self, client):
        r = client.post("/api/config/key", json={"provider": "gemini", "api_key": ""})
        assert r.status_code == 422

    def test_unsupported_provider_rejected(self, client):
        r = client.post("/api/config/key", json={"provider": "unsupported", "api_key": "some-key"})
        assert r.status_code == 400

    def test_configure_key_success(self, client, monkeypatch):
        mock_provider = MagicMock()
        mock_provider.provider_name = "gemini"
        with patch("qa_chatbot.main.create_provider", return_value=mock_provider):
            r = client.post("/api/config/key", json={"provider": "gemini", "api_key": "test-key-123"})
            assert r.status_code == 200
            d = r.json()
            assert d["status"] == "ok"
            assert d["llm_available"] is True
