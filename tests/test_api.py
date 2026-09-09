# Author: Maharshi Soni | License: MIT
"""
Tests for the FastAPI application endpoints.
"""

import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app, retriever  # noqa: E402
from document_loader import load_directory  # noqa: E402


@pytest.fixture(autouse=True)
def setup_retriever():
    """Ensure the retriever has data for API tests."""
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample_docs")
    chunks = load_directory(sample_dir)
    if chunks:
        retriever.index(chunks)
    yield
    # No cleanup needed; index is in-memory


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHomeEndpoint:
    """Tests for the GET / endpoint."""

    def test_home_returns_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "RAG QA Knowledge Base" in response.text


class TestAskEndpoint:
    """Tests for the POST /api/ask endpoint."""

    def test_ask_valid_question(self, client):
        response = client.post("/api/ask", json={"question": "What is the regression suite?"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert "query" in data
        assert data["query"] == "What is the regression suite?"

    def test_ask_payment_question(self, client):
        response = client.post(
            "/api/ask",
            json={"question": "What is the regression suite for payment module?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["answer"]) > 0
        assert data["confidence"] > 0

    def test_ask_empty_question(self, client):
        response = client.post("/api/ask", json={"question": ""})
        assert response.status_code == 400

    def test_ask_missing_question(self, client):
        response = client.post("/api/ask", json={})
        assert response.status_code == 400


class TestUploadEndpoint:
    """Tests for the POST /api/upload endpoint."""

    def test_upload_txt_file(self, client):
        content = b"This is a test document for upload testing."
        response = client.post(
            "/api/upload",
            files={"file": ("test_upload.txt", content, "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test_upload.txt" in data["message"]

        # Clean up uploaded file
        upload_path = os.path.join(
            os.path.dirname(__file__), "..", "uploads", "test_upload.txt"
        )
        if os.path.exists(upload_path):
            os.remove(upload_path)

    def test_upload_unsupported_type(self, client):
        content = b"PDF content here"
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", content, "application/pdf")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]


class TestSourcesEndpoint:
    """Tests for the GET /api/sources endpoint."""

    def test_list_sources(self, client):
        response = client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "total_chunks" in data
        assert isinstance(data["sources"], list)


class TestReindexEndpoint:
    """Tests for the POST /api/reindex endpoint."""

    def test_reindex(self, client):
        response = client.post("/api/reindex")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["total_chunks"] > 0


class TestClearEndpoint:
    """Tests for the DELETE /api/clear endpoint."""

    def test_clear_index(self, client):
        response = client.delete("/api/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["total_chunks"] == 0
