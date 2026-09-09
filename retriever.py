# Author: Maharshi Soni | License: MIT
"""
Retriever module for the RAG QA Knowledge Base.

Uses scikit-learn TF-IDF vectorization and cosine similarity to perform
fast, lightweight semantic search over document chunks. No GPU or paid
API required -- runs entirely on CPU with pure Python dependencies.
"""

from typing import List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from document_loader import DocumentChunk


class TFIDFRetriever:
    """
    TF-IDF based document retriever.

    Builds an inverted index using TF-IDF vectors and retrieves the most
    relevant chunks for a given query using cosine similarity.
    """

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.chunks: List[DocumentChunk] = []
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    @property
    def document_count(self) -> int:
        return len(self.chunks)

    def index(self, chunks: List[DocumentChunk]) -> None:
        """
        Build the TF-IDF index from a list of document chunks.

        Args:
            chunks: List of DocumentChunk objects to index.
        """
        if not chunks:
            self.chunks = []
            self._is_fitted = False
            return

        self.chunks = chunks
        corpus = [chunk.text for chunk in chunks]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=10000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self._is_fitted = True

    def add_chunks(self, new_chunks: List[DocumentChunk]) -> None:
        """
        Add new chunks and rebuild the index.

        Args:
            new_chunks: Additional DocumentChunk objects to add.
        """
        all_chunks = self.chunks + new_chunks
        self.index(all_chunks)

    def retrieve(
        self, query: str, top_k: int = 5, threshold: float = 0.05
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieve the top-k most relevant chunks for a query.

        Args:
            query: The natural language query.
            top_k: Number of top results to return.
            threshold: Minimum similarity score to include a result.

        Returns:
            List of (DocumentChunk, similarity_score) tuples, sorted by
            descending similarity.
        """
        if not self._is_fitted or self.vectorizer is None:
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Get top-k indices sorted by similarity (descending)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                results.append((self.chunks[idx], score))

        return results

    def get_sources(self) -> List[str]:
        """Return a sorted list of unique source filenames in the index."""
        return sorted(set(chunk.source_file for chunk in self.chunks))

    def clear(self) -> None:
        """Clear the index and all stored chunks."""
        self.vectorizer = None
        self.tfidf_matrix = None
        self.chunks = []
        self._is_fitted = False
