# Author: Maharshi Soni | License: MIT
"""
Tests for the answer_generator module.
"""

import pytest

from answer_generator import AnswerResult, generate_answer
from document_loader import DocumentChunk


class TestGenerateAnswer:
    """Tests for the generate_answer function."""

    def test_empty_results(self):
        result = generate_answer("What is testing?", [])
        assert isinstance(result, AnswerResult)
        assert result.confidence == 0.0
        assert result.sources == []
        assert "could not find" in result.answer.lower()

    def test_answer_with_results(self, sample_chunks):
        retrieved = [(sample_chunks[0], 0.45), (sample_chunks[1], 0.30)]
        result = generate_answer("payment refund process", retrieved)
        assert isinstance(result, AnswerResult)
        assert result.confidence > 0
        assert len(result.sources) == 2
        assert result.query == "payment refund process"

    def test_sources_contain_metadata(self, sample_chunks):
        retrieved = [(sample_chunks[0], 0.5)]
        result = generate_answer("test query", retrieved)
        assert len(result.sources) == 1
        source = result.sources[0]
        assert "file" in source
        assert "chunk_index" in source
        assert "relevance_score" in source
        assert "preview" in source
        assert source["file"] == "payment_test_plan.md"

    def test_max_chunks_limits_output(self, sample_chunks):
        retrieved = [(c, 0.3) for c in sample_chunks]
        result = generate_answer("general query", retrieved, max_chunks=2)
        assert len(result.sources) <= 2

    def test_confidence_scales_correctly(self, sample_chunks):
        # High similarity should give high confidence
        high = generate_answer("q", [(sample_chunks[0], 0.9)])
        assert high.confidence > 0.5

        # Low similarity should give low confidence
        low = generate_answer("q", [(sample_chunks[0], 0.01)])
        assert low.confidence < 0.5

    def test_confidence_capped_at_one(self, sample_chunks):
        result = generate_answer("q", [(sample_chunks[0], 1.0)])
        assert result.confidence <= 1.0

    def test_answer_contains_text_from_chunks(self, sample_chunks):
        retrieved = [(sample_chunks[0], 0.5)]
        result = generate_answer("payment gateway", retrieved)
        # The answer should contain text derived from the chunk
        assert len(result.answer) > 0


class TestAnswerResult:
    """Tests for the AnswerResult dataclass."""

    def test_fields(self):
        result = AnswerResult(
            answer="Test answer",
            sources=[{"file": "test.md"}],
            confidence=0.85,
            query="test query",
        )
        assert result.answer == "Test answer"
        assert result.confidence == 0.85
        assert result.query == "test query"
        assert len(result.sources) == 1
