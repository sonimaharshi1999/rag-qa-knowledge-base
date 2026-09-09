# Author: Maharshi Soni | License: MIT
"""
Tests for the document_loader module.
"""

import os
import tempfile

import pytest

from document_loader import (
    DocumentChunk,
    chunk_text,
    load_directory,
    load_document,
    read_file,
)


class TestChunkText:
    """Tests for the chunk_text function."""

    def test_basic_chunking(self):
        text = " ".join(f"word{i}" for i in range(100))
        chunks = chunk_text(text, chunk_size=30, chunk_overlap=5)
        assert len(chunks) > 1
        # Each chunk should have at most 30 words
        for chunk in chunks:
            assert len(chunk.split()) <= 30

    def test_empty_text(self):
        assert chunk_text("") == []

    def test_text_smaller_than_chunk_size(self):
        text = "Short document with a few words."
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_overlap_creates_shared_words(self):
        words = [f"w{i}" for i in range(20)]
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=10, chunk_overlap=3)
        # Check there is overlap between consecutive chunks
        assert len(chunks) >= 2
        first_words = set(chunks[0].split())
        second_words = set(chunks[1].split())
        overlap = first_words & second_words
        assert len(overlap) > 0

    def test_whitespace_only(self):
        assert chunk_text("   \n\n  \t  ") == []


class TestDocumentChunk:
    """Tests for the DocumentChunk dataclass."""

    def test_char_count(self):
        chunk = DocumentChunk(text="Hello world", source_file="test.txt", chunk_index=0)
        assert chunk.char_count == 11

    def test_word_count(self):
        chunk = DocumentChunk(text="one two three four", source_file="test.txt", chunk_index=0)
        assert chunk.word_count == 4

    def test_metadata_default(self):
        chunk = DocumentChunk(text="text", source_file="f.txt", chunk_index=0)
        assert chunk.metadata == {}


class TestReadFile:
    """Tests for the read_file function."""

    def test_read_existing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Hello test content")
            f.flush()
            path = f.name

        try:
            content = read_file(path)
            assert content == "Hello test content"
        finally:
            os.unlink(path)

    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/path/file.txt")


class TestLoadDocument:
    """Tests for the load_document function."""

    def test_load_returns_chunks(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("This is a test document. " * 50)
            f.flush()
            path = f.name

        try:
            chunks = load_document(path, chunk_size=20)
            assert len(chunks) > 0
            assert all(isinstance(c, DocumentChunk) for c in chunks)
            assert chunks[0].source_file == os.path.basename(path)
            assert chunks[0].chunk_index == 0
        finally:
            os.unlink(path)

    def test_load_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("")
            f.flush()
            path = f.name

        try:
            chunks = load_document(path)
            assert chunks == []
        finally:
            os.unlink(path)


class TestLoadDirectory:
    """Tests for the load_directory function."""

    def test_loads_txt_and_md(self, temp_doc_dir):
        chunks = load_directory(temp_doc_dir)
        sources = set(c.source_file for c in chunks)
        assert "doc1.txt" in sources
        assert "doc2.md" in sources
        # PDF should be ignored
        assert "ignored.pdf" not in sources

    def test_nonexistent_directory(self):
        chunks = load_directory("/nonexistent/dir")
        assert chunks == []

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            chunks = load_directory(tmpdir)
            assert chunks == []
