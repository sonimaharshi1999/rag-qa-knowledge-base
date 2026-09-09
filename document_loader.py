# Author: Maharshi Soni | License: MIT
"""
Document loader module for the RAG QA Knowledge Base.

Handles reading and chunking text documents (.txt, .md) into smaller
passages suitable for retrieval. Each chunk retains metadata about its
source file and position so answers can cite their origin.
"""

import os
import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class DocumentChunk:
    """A single chunk of text from a source document."""

    text: str
    source_file: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def read_file(file_path: str) -> str:
    """Read a text file and return its contents."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[str]:
    """
    Split text into overlapping chunks by word count.

    Args:
        text: The full document text.
        chunk_size: Maximum number of words per chunk.
        chunk_overlap: Number of overlapping words between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks


def load_document(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[DocumentChunk]:
    """
    Load a single document and return its chunks.

    Args:
        file_path: Path to the text file (.txt or .md).
        chunk_size: Maximum words per chunk.
        chunk_overlap: Word overlap between chunks.

    Returns:
        List of DocumentChunk objects.
    """
    text = read_file(file_path)
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if not text:
        return []

    raw_chunks = chunk_text(text, chunk_size, chunk_overlap)
    source_name = os.path.basename(file_path)

    return [
        DocumentChunk(
            text=chunk,
            source_file=source_name,
            chunk_index=i,
            metadata={"file_path": file_path},
        )
        for i, chunk in enumerate(raw_chunks)
    ]


def load_directory(
    directory: str,
    extensions: tuple = (".txt", ".md"),
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[DocumentChunk]:
    """
    Load all supported documents from a directory.

    Args:
        directory: Path to the directory containing documents.
        extensions: Tuple of allowed file extensions.
        chunk_size: Maximum words per chunk.
        chunk_overlap: Word overlap between chunks.

    Returns:
        List of DocumentChunk objects from all files.
    """
    all_chunks: List[DocumentChunk] = []

    if not os.path.isdir(directory):
        return all_chunks

    for filename in sorted(os.listdir(directory)):
        if not any(filename.lower().endswith(ext) for ext in extensions):
            continue
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            chunks = load_document(file_path, chunk_size, chunk_overlap)
            all_chunks.extend(chunks)

    return all_chunks
