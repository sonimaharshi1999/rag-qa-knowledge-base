# Author: Maharshi Soni | License: MIT
"""
Shared pytest fixtures for the RAG QA Knowledge Base test suite.
"""

import os
import sys
import tempfile

import pytest

# Add project root to Python path so modules can be imported directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from document_loader import DocumentChunk  # noqa: E402
from retriever import TFIDFRetriever  # noqa: E402


@pytest.fixture
def sample_text():
    """A short sample document for testing."""
    return (
        "The payment module handles credit card transactions and refunds. "
        "It integrates with Stripe and PayPal as payment gateways. "
        "All transactions are logged for audit purposes. "
        "PCI DSS compliance is enforced by masking card numbers in logs."
    )


@pytest.fixture
def sample_chunks():
    """A list of pre-built DocumentChunk objects for testing."""
    return [
        DocumentChunk(
            text="The payment module handles credit card transactions and refunds. "
            "It integrates with Stripe and PayPal as payment gateways.",
            source_file="payment_test_plan.md",
            chunk_index=0,
        ),
        DocumentChunk(
            text="Login test cases cover valid credentials, invalid passwords, "
            "account lockout, and two-factor authentication flows.",
            source_file="login_test_cases.txt",
            chunk_index=0,
        ),
        DocumentChunk(
            text="The regression test suite runs before every production release. "
            "It includes smoke tests, core business logic tests, and secondary feature tests.",
            source_file="regression_guide.md",
            chunk_index=0,
        ),
        DocumentChunk(
            text="API testing requires Bearer token authentication. "
            "Endpoints are tested for correct status codes, response schemas, and rate limiting.",
            source_file="api_runbook.md",
            chunk_index=0,
        ),
        DocumentChunk(
            text="The CI/CD pipeline has six stages: code quality, unit tests, "
            "integration tests, end-to-end tests, security scanning, and deployment.",
            source_file="cicd_docs.md",
            chunk_index=0,
        ),
    ]


@pytest.fixture
def fitted_retriever(sample_chunks):
    """A TFIDFRetriever already fitted on sample chunks."""
    retriever = TFIDFRetriever()
    retriever.index(sample_chunks)
    return retriever


@pytest.fixture
def temp_doc_dir():
    """Create a temporary directory with sample .txt and .md files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample files
        with open(os.path.join(tmpdir, "doc1.txt"), "w", encoding="utf-8") as f:
            f.write("This is a test document about payment processing.\n" * 10)

        with open(os.path.join(tmpdir, "doc2.md"), "w", encoding="utf-8") as f:
            f.write("# Login Testing\nTest cases for the login module.\n" * 10)

        with open(os.path.join(tmpdir, "ignored.pdf"), "w", encoding="utf-8") as f:
            f.write("This PDF should be ignored by the loader.\n")

        yield tmpdir
