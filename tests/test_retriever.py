# Author: Maharshi Soni | License: MIT
"""
Tests for the retriever module.
"""

import pytest

from document_loader import DocumentChunk
from retriever import TFIDFRetriever


class TestTFIDFRetriever:
    """Tests for the TFIDFRetriever class."""

    def test_initial_state(self):
        r = TFIDFRetriever()
        assert not r.is_fitted
        assert r.document_count == 0
        assert r.get_sources() == []

    def test_index_sets_fitted(self, sample_chunks):
        r = TFIDFRetriever()
        r.index(sample_chunks)
        assert r.is_fitted
        assert r.document_count == len(sample_chunks)

    def test_index_empty_list(self):
        r = TFIDFRetriever()
        r.index([])
        assert not r.is_fitted

    def test_retrieve_returns_results(self, fitted_retriever):
        results = fitted_retriever.retrieve("payment credit card refund")
        assert len(results) > 0
        # Each result is a (DocumentChunk, float) tuple
        chunk, score = results[0]
        assert isinstance(chunk, DocumentChunk)
        assert isinstance(score, float)
        assert score > 0

    def test_retrieve_payment_query(self, fitted_retriever):
        results = fitted_retriever.retrieve("payment gateway Stripe")
        assert len(results) > 0
        # Top result should be from the payment document
        top_chunk, _ = results[0]
        assert "payment" in top_chunk.text.lower()

    def test_retrieve_login_query(self, fitted_retriever):
        results = fitted_retriever.retrieve("login authentication two-factor")
        assert len(results) > 0
        top_chunk, _ = results[0]
        assert "login" in top_chunk.text.lower()

    def test_retrieve_respects_top_k(self, fitted_retriever):
        results = fitted_retriever.retrieve("testing", top_k=2)
        assert len(results) <= 2

    def test_retrieve_empty_query_returns_results(self, fitted_retriever):
        # TF-IDF can still work with common words
        results = fitted_retriever.retrieve("the")
        # May return empty or low-score results depending on stop words
        assert isinstance(results, list)

    def test_retrieve_unfitted_returns_empty(self):
        r = TFIDFRetriever()
        results = r.retrieve("anything")
        assert results == []

    def test_get_sources(self, fitted_retriever):
        sources = fitted_retriever.get_sources()
        assert isinstance(sources, list)
        assert len(sources) == 5
        # Should be sorted
        assert sources == sorted(sources)

    def test_clear(self, fitted_retriever):
        fitted_retriever.clear()
        assert not fitted_retriever.is_fitted
        assert fitted_retriever.document_count == 0
        assert fitted_retriever.get_sources() == []

    def test_add_chunks(self, fitted_retriever):
        initial_count = fitted_retriever.document_count
        new_chunk = DocumentChunk(
            text="Performance testing measures response times under load.",
            source_file="performance_guide.md",
            chunk_index=0,
        )
        fitted_retriever.add_chunks([new_chunk])
        assert fitted_retriever.document_count == initial_count + 1
        assert "performance_guide.md" in fitted_retriever.get_sources()

    def test_relevance_ordering(self, fitted_retriever):
        results = fitted_retriever.retrieve("CI/CD pipeline deployment stages")
        if len(results) >= 2:
            # Scores should be in descending order
            for i in range(len(results) - 1):
                assert results[i][1] >= results[i + 1][1]
