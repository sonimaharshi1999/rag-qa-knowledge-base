# Author: Maharshi Soni | License: MIT
"""
Answer generator module for the RAG QA Knowledge Base.

Generates grounded answers from retrieved document chunks. Uses an
extractive approach: selects and combines the most relevant passages,
highlights key sentences, and provides source citations. No LLM or
paid API is needed -- the system works entirely with retrieval and
rule-based answer synthesis.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple

from document_loader import DocumentChunk


@dataclass
class AnswerResult:
    """Structured answer with sources and confidence."""

    answer: str
    sources: List[dict]
    confidence: float
    query: str


def _score_sentence_relevance(sentence: str, query_words: set) -> float:
    """Score a sentence based on how many query words it contains."""
    sentence_words = set(sentence.lower().split())
    if not query_words:
        return 0.0
    overlap = sentence_words & query_words
    return len(overlap) / len(query_words)


def _extract_key_sentences(text: str, query: str, max_sentences: int = 5) -> str:
    """
    Extract the most relevant sentences from a passage given a query.

    Splits text into sentences, scores each by query-word overlap, and
    returns the top sentences in their original order.
    """
    # Split into sentences (handles ., !, ? and line breaks)
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        return text

    query_words = set(query.lower().split()) - {
        "what", "is", "the", "a", "an", "for", "of", "in", "to",
        "how", "does", "do", "are", "was", "were", "can", "which",
        "where", "when", "why", "who",
    }

    scored = []
    for i, sent in enumerate(sentences):
        score = _score_sentence_relevance(sent, query_words)
        scored.append((i, sent, score))

    # Sort by score descending, take top_n, then reorder by position
    scored.sort(key=lambda x: x[2], reverse=True)
    top = scored[:max_sentences]
    top.sort(key=lambda x: x[0])

    return " ".join(item[1] for item in top)


def generate_answer(
    query: str,
    retrieved: List[Tuple[DocumentChunk, float]],
    max_chunks: int = 3,
) -> AnswerResult:
    """
    Generate a grounded answer from retrieved chunks.

    Combines extractive summarization with source citation. The answer
    is composed of the most relevant sentences from the top-matching
    chunks, along with metadata about each source.

    Args:
        query: The original user question.
        retrieved: List of (DocumentChunk, score) tuples from the retriever.
        max_chunks: Maximum number of chunks to include in the answer.

    Returns:
        An AnswerResult with the synthesized answer, sources, and confidence.
    """
    if not retrieved:
        return AnswerResult(
            answer="I could not find relevant information in the knowledge base to answer your question. "
            "Try uploading more documents or rephrasing your query.",
            sources=[],
            confidence=0.0,
            query=query,
        )

    top_results = retrieved[:max_chunks]
    answer_parts = []
    sources = []
    total_score = 0.0

    for chunk, score in top_results:
        key_text = _extract_key_sentences(chunk.text, query)
        answer_parts.append(key_text)
        total_score += score

        sources.append(
            {
                "file": chunk.source_file,
                "chunk_index": chunk.chunk_index,
                "relevance_score": round(score, 4),
                "preview": chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
            }
        )

    # Combine answer sections
    answer_text = "\n\n".join(answer_parts)

    # Confidence is the average similarity of included chunks, scaled to 0-1
    avg_score = total_score / len(top_results) if top_results else 0.0
    # TF-IDF cosine similarity is already 0-1, but values are typically low;
    # scale so that scores above 0.3 map to high confidence.
    confidence = min(1.0, avg_score / 0.3)

    return AnswerResult(
        answer=answer_text,
        sources=sources,
        confidence=round(confidence, 4),
        query=query,
    )
