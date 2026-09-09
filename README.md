# RAG QA Knowledge Base

A **Retrieval-Augmented Generation (RAG)** system designed for QA teams. Upload your test documentation, runbooks, and test plans, then ask natural-language questions and receive grounded answers with source citations. Built with scikit-learn TF-IDF retrieval, FastAPI, and a clean HTML frontend -- no paid APIs or GPU required.

---

## Overview

QA teams accumulate vast collections of test plans, runbooks, regression guides, and API documentation. Finding the right information quickly is a constant challenge. **RAG QA Knowledge Base** solves this by indexing your documents and letting you ask questions in plain English:

> "What is the regression suite for the payment module?"

The system retrieves the most relevant passages from your knowledge base, synthesizes an answer from those passages, and cites the exact sources -- so you can trust and verify every response.

---

## Features

- **Natural Language Q&A** -- Ask questions in plain English and get grounded answers extracted from your documents.
- **Source Citations** -- Every answer includes the source file, chunk index, and relevance score so you can verify the information.
- **Confidence Scoring** -- Visual confidence bar shows how strongly the answer is supported by the knowledge base.
- **Document Upload** -- Drag-and-drop `.txt` and `.md` files through the web UI to expand the knowledge base on the fly.
- **TF-IDF + Cosine Similarity Retrieval** -- Lightweight, CPU-only vector search using scikit-learn. No GPU, no embeddings API, no paid services.
- **Pre-loaded Sample Documents** -- Ships with five sample QA documents (payment test plan, API runbook, regression guide, login test cases, CI/CD docs) for immediate demo.
- **Live Re-indexing** -- Rebuild the index from all documents with a single click.
- **REST API** -- Full JSON API for programmatic integration with CI/CD pipelines and chat bots.
- **Responsive Web UI** -- Clean, modern frontend that works on desktop and tablet.

---

## Architecture

```
User Question
      |
      v
+------------------+      +-------------------+      +--------------------+
|  FastAPI Server   | ---> | TF-IDF Retriever  | ---> | Answer Generator   |
|  (main.py)        |      | (retriever.py)    |      | (answer_generator  |
|                   |      |                   |      |  .py)              |
+------------------+      +-------------------+      +--------------------+
      ^                          ^
      |                          |
  Web UI / API             Document Chunks
  (templates/              (document_loader
   static/)                 .py)
                                 ^
                                 |
                          .txt / .md files
                       (sample_docs/ + uploads/)
```

### How It Works

1. **Document Loading** (`document_loader.py`) -- Text files are read, normalized, and split into overlapping word-based chunks. Each chunk retains its source filename and position.

2. **Indexing** (`retriever.py`) -- Chunks are vectorized using TF-IDF (with bigrams and sublinear term frequency). The resulting sparse matrix enables fast cosine-similarity search.

3. **Retrieval** -- When a question arrives, it is vectorized with the same TF-IDF model. Cosine similarity ranks all chunks; the top-k most relevant are returned.

4. **Answer Generation** (`answer_generator.py`) -- The most relevant sentences are extracted from the top chunks using query-word overlap scoring, then combined into a coherent answer. Sources and confidence are attached.

5. **Serving** (`main.py`) -- FastAPI exposes REST endpoints for asking questions, uploading documents, listing sources, re-indexing, and clearing the index. A Jinja2 HTML template provides the web UI.

---

## Tech Stack

| Component         | Technology                            |
|-------------------|---------------------------------------|
| Backend Framework | FastAPI + Uvicorn                     |
| Retrieval Engine  | scikit-learn TF-IDF + cosine similarity |
| Templating        | Jinja2                                |
| Frontend          | Vanilla HTML / CSS / JavaScript       |
| Testing           | pytest + httpx (FastAPI TestClient)   |
| Language          | Python 3.9+                           |

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/sonimaharshi1999/rag-qa-knowledge-base.git
cd rag-qa-knowledge-base

# Create and activate a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the server
python main.py
```

The application will be available at **http://127.0.0.1:8000**.

Alternatively, use Uvicorn directly:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## Usage Examples

### Web Interface

1. Open http://127.0.0.1:8000 in your browser.
2. Type a question in the text area, e.g., "What is the regression suite for the payment module?"
3. Click **Ask** to get a grounded answer with sources and confidence.
4. Upload additional documents using the drag-and-drop area on the right panel.

### REST API

#### Ask a Question

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the regression suite for payment module?"}'
```

#### Upload a Document

```bash
curl -X POST http://127.0.0.1:8000/api/upload \
  -F "file=@my_test_plan.md"
```

#### List Indexed Sources

```bash
curl http://127.0.0.1:8000/api/sources
```

#### Re-index All Documents

```bash
curl -X POST http://127.0.0.1:8000/api/reindex
```

#### Clear the Index

```bash
curl -X DELETE http://127.0.0.1:8000/api/clear
```

---

## Sample Input / Output

### Input

```json
{
  "question": "What is the regression suite for payment module?"
}
```

### Output

```json
{
  "answer": "The payment module handles credit card transactions and refunds. It integrates with Stripe and PayPal as payment gateways. All transactions are logged for audit purposes. Critical path tests include TC-PAY-001 through TC-PAY-005 covering successful payments, expired cards, insufficient funds, full refunds, and partial refunds. Integration tests verify gateway failover and webhook notifications.",
  "sources": [
    {
      "file": "payment_module_test_plan.md",
      "chunk_index": 0,
      "relevance_score": 0.4523,
      "preview": "# Payment Module Test Plan ## Overview The payment module handles all financial transactions..."
    },
    {
      "file": "regression_testing_guide.md",
      "chunk_index": 0,
      "relevance_score": 0.2187,
      "preview": "# Regression Testing Guide ## What is Regression Testing? Regression testing ensures that..."
    }
  ],
  "confidence": 0.7843,
  "query": "What is the regression suite for payment module?"
}
```

### More Example Questions

- "How do I authenticate API requests?"
- "What are the login test cases?"
- "What stages does the CI/CD pipeline have?"
- "What is the exit criteria for the payment test plan?"
- "How does account lockout work?"
- "What browsers are covered in regression testing?"

---

## Project Structure

```
rag-qa-knowledge-base/
|-- main.py                  # FastAPI application entry point
|-- document_loader.py       # Document reading and chunking
|-- retriever.py             # TF-IDF vectorization and cosine similarity search
|-- answer_generator.py      # Extractive answer synthesis with source citations
|-- requirements.txt         # Python dependencies
|-- .gitignore               # Git ignore rules
|-- LICENSE                  # MIT License
|-- README.md                # This file
|-- templates/
|   |-- index.html           # Jinja2 HTML template for the web UI
|-- static/
|   |-- style.css            # Stylesheet
|   |-- app.js               # Frontend JavaScript
|-- sample_docs/
|   |-- payment_module_test_plan.md
|   |-- api_testing_runbook.md
|   |-- regression_testing_guide.md
|   |-- login_test_cases.txt
|   |-- cicd_pipeline_docs.md
|-- uploads/                 # User-uploaded documents (gitignored)
|   |-- .gitkeep
|-- tests/
|   |-- __init__.py
|   |-- conftest.py          # Shared fixtures
|   |-- test_document_loader.py
|   |-- test_retriever.py
|   |-- test_answer_generator.py
|   |-- test_api.py
```

---

## Tests

Run the full test suite with pytest:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short

# Run a specific test file
pytest tests/test_retriever.py -v

# Run a specific test class
pytest tests/test_api.py::TestAskEndpoint -v
```

### Test Coverage

| Module              | Tests                                                    |
|---------------------|----------------------------------------------------------|
| document_loader.py  | Chunking, file reading, directory loading, edge cases    |
| retriever.py        | Indexing, retrieval accuracy, ordering, add/clear ops    |
| answer_generator.py | Empty results, source metadata, confidence scaling       |
| main.py (API)       | All endpoints: ask, upload, sources, reindex, clear, home|

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Make your changes and add tests.
4. Run the test suite: `pytest tests/ -v`.
5. Commit your changes: `git commit -m "Add my feature"`.
6. Push to your fork: `git push origin feature/my-feature`.
7. Open a Pull Request.

Please ensure:
- All tests pass before submitting.
- New features include corresponding tests.
- Code follows PEP 8 style guidelines.

---

## Roadmap

- [ ] **Sentence-Transformers Support** -- Optional upgrade to dense embeddings (all-MiniLM-L6-v2) for higher retrieval accuracy when the package is available.
- [ ] **FAISS Integration** -- Replace brute-force cosine similarity with FAISS approximate nearest neighbor search for large-scale document collections.
- [ ] **PDF and DOCX Support** -- Extend the document loader to handle PDF and Word files.
- [ ] **LLM-Powered Answer Generation** -- Optional integration with local LLMs (Ollama, llama.cpp) for more fluent, abstractive answers.
- [ ] **Document Management UI** -- View, delete, and tag individual documents from the web interface.
- [ ] **User Authentication** -- Role-based access control for multi-team deployments.
- [ ] **Persistent Vector Store** -- Save and load the index to disk so restarts do not require re-indexing.
- [ ] **Chunking Strategies** -- Support semantic chunking (by heading, by paragraph) in addition to fixed-size word windows.
- [ ] **Evaluation Framework** -- Built-in evaluation harness to measure retrieval precision, recall, and answer quality on labeled QA pairs.
- [ ] **Docker Support** -- Dockerfile and docker-compose.yml for one-command deployment.

---

## Author

**Maharshi Soni**

- GitHub: [github.com/sonimaharshi1999](https://github.com/sonimaharshi1999)
- LinkedIn: [linkedin.com/in/maharshi-soni-b56736170](https://linkedin.com/in/maharshi-soni-b56736170)

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) -- Modern, fast web framework for building APIs with Python.
- [scikit-learn](https://scikit-learn.org/) -- Machine learning library providing TF-IDF vectorization and cosine similarity.
- [pytest](https://docs.pytest.org/) -- Testing framework for Python.
- [Uvicorn](https://www.uvicorn.org/) -- ASGI server for running FastAPI applications.
- Inspired by the RAG architecture pattern popularized by modern LLM applications.
