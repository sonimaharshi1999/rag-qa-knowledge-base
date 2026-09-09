# Author: Maharshi Soni | License: MIT
"""
RAG QA Knowledge Base -- FastAPI Application

A retrieval-augmented generation system for QA teams. Upload test
documentation, runbooks, and test plans, then ask natural-language
questions and get grounded answers with source citations.

Usage:
    uvicorn main:app --reload
"""

import os
import shutil
from typing import List

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from answer_generator import generate_answer
from document_loader import DocumentChunk, load_directory, load_document
from retriever import TFIDFRetriever

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_docs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
ALLOWED_EXTENSIONS = {".txt", ".md"}

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="RAG QA Knowledge Base",
    description="Retrieval-Augmented Generation system for QA teams",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Global retriever instance
retriever = TFIDFRetriever()


# ---------------------------------------------------------------------------
# Startup: index sample documents
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def startup_index():
    """Load sample documents and any previously uploaded files on startup."""
    all_chunks: List[DocumentChunk] = []

    # Load sample docs
    sample_chunks = load_directory(SAMPLE_DIR)
    all_chunks.extend(sample_chunks)

    # Load previously uploaded docs
    upload_chunks = load_directory(UPLOAD_DIR)
    all_chunks.extend(upload_chunks)

    if all_chunks:
        retriever.index(all_chunks)
        print(
            f"[startup] Indexed {retriever.document_count} chunks "
            f"from {len(retriever.get_sources())} documents."
        )
    else:
        print("[startup] No documents found. Upload files to get started.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main UI."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "sources": retriever.get_sources(),
            "doc_count": retriever.document_count,
        },
    )


@app.post("/api/ask")
async def ask_question(request: Request):
    """
    Answer a natural-language question using the knowledge base.

    Request body (JSON):
        {"question": "What is the regression suite for payment module?"}

    Response (JSON):
        {"answer": "...", "sources": [...], "confidence": 0.82, "query": "..."}
    """
    body = await request.json()
    question = body.get("question", "").strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not retriever.is_fitted:
        return JSONResponse(
            {
                "answer": "The knowledge base is empty. Please upload documents first.",
                "sources": [],
                "confidence": 0.0,
                "query": question,
            }
        )

    # Retrieve relevant chunks
    results = retriever.retrieve(query=question, top_k=5)

    # Generate grounded answer
    answer_result = generate_answer(query=question, retrieved=results)

    return JSONResponse(
        {
            "answer": answer_result.answer,
            "sources": answer_result.sources,
            "confidence": answer_result.confidence,
            "query": answer_result.query,
        }
    )


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a .txt or .md document to the knowledge base.

    The file is saved to the uploads/ directory, chunked, and added to
    the retrieval index immediately.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save file
    dest_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Index new document
    new_chunks = load_document(dest_path)
    if new_chunks:
        retriever.add_chunks(new_chunks)

    return JSONResponse(
        {
            "message": f"Uploaded and indexed '{file.filename}' ({len(new_chunks)} chunks).",
            "total_chunks": retriever.document_count,
            "sources": retriever.get_sources(),
        }
    )


@app.get("/api/sources")
async def list_sources():
    """List all indexed document sources."""
    return JSONResponse(
        {
            "sources": retriever.get_sources(),
            "total_chunks": retriever.document_count,
        }
    )


@app.delete("/api/clear")
async def clear_index():
    """Clear the retrieval index (does not delete files)."""
    retriever.clear()
    return JSONResponse({"message": "Index cleared.", "total_chunks": 0})


@app.post("/api/reindex")
async def reindex():
    """Rebuild the index from sample_docs/ and uploads/."""
    all_chunks: List[DocumentChunk] = []
    all_chunks.extend(load_directory(SAMPLE_DIR))
    all_chunks.extend(load_directory(UPLOAD_DIR))

    if all_chunks:
        retriever.index(all_chunks)

    return JSONResponse(
        {
            "message": f"Re-indexed {retriever.document_count} chunks from {len(retriever.get_sources())} documents.",
            "sources": retriever.get_sources(),
            "total_chunks": retriever.document_count,
        }
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
