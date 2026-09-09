// Author: Maharshi Soni | License: MIT

document.addEventListener("DOMContentLoaded", () => {
    const questionForm = document.getElementById("question-form");
    const questionInput = document.getElementById("question-input");
    const askBtn = document.getElementById("ask-btn");
    const answerSection = document.getElementById("answer-section");
    const answerText = document.getElementById("answer-text");
    const sourcesList = document.getElementById("sources-list");
    const confidenceFill = document.getElementById("confidence-fill");
    const confidenceLabel = document.getElementById("confidence-label");
    const loading = document.getElementById("loading");

    const uploadForm = document.getElementById("upload-form");
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const uploadBtn = document.getElementById("upload-btn");
    const uploadStatus = document.getElementById("upload-status");
    const sourcesSidebar = document.getElementById("sources-sidebar");
    const reindexBtn = document.getElementById("reindex-btn");

    let selectedFile = null;

    // ------------------------------------------------------------------
    // Ask question
    // ------------------------------------------------------------------

    questionForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        answerSection.classList.add("hidden");
        loading.classList.remove("hidden");
        askBtn.disabled = true;

        try {
            const res = await fetch("/api/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question }),
            });
            const data = await res.json();

            // Display answer
            answerText.textContent = data.answer;

            // Confidence bar
            const pct = Math.round(data.confidence * 100);
            confidenceFill.style.width = pct + "%";
            confidenceLabel.textContent = `Confidence: ${pct}%`;

            if (pct >= 60) {
                confidenceFill.style.background = "var(--color-confidence-high)";
            } else if (pct >= 30) {
                confidenceFill.style.background = "var(--color-confidence-mid)";
            } else {
                confidenceFill.style.background = "var(--color-confidence-low)";
            }

            // Sources
            sourcesList.innerHTML = "";
            if (data.sources && data.sources.length > 0) {
                data.sources.forEach((src) => {
                    const card = document.createElement("div");
                    card.className = "source-card";
                    card.innerHTML = `
                        <span class="source-name">${escapeHtml(src.file)}</span>
                        <span class="source-score">Chunk #${src.chunk_index} &middot; Score: ${src.relevance_score}</span>
                        <div class="source-preview">${escapeHtml(src.preview)}</div>
                    `;
                    sourcesList.appendChild(card);
                });
            }

            answerSection.classList.remove("hidden");
        } catch (err) {
            answerText.textContent = "Error: " + err.message;
            answerSection.classList.remove("hidden");
        } finally {
            loading.classList.add("hidden");
            askBtn.disabled = false;
        }
    });

    // ------------------------------------------------------------------
    // File upload
    // ------------------------------------------------------------------

    uploadArea.addEventListener("click", () => fileInput.click());

    uploadArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadArea.classList.add("dragover");
    });

    uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
    });

    uploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            selectedFile = e.dataTransfer.files[0];
            uploadArea.querySelector("p").textContent = selectedFile.name;
            uploadBtn.disabled = false;
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
            uploadArea.querySelector("p").textContent = selectedFile.name;
            uploadBtn.disabled = false;
        }
    });

    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        uploadBtn.disabled = true;
        uploadStatus.classList.add("hidden");

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData,
            });
            const data = await res.json();

            if (res.ok) {
                showUploadStatus(data.message, "success");
                updateSources(data.sources);
            } else {
                showUploadStatus(data.detail || "Upload failed.", "error");
            }
        } catch (err) {
            showUploadStatus("Error: " + err.message, "error");
        } finally {
            selectedFile = null;
            fileInput.value = "";
            uploadArea.querySelector("p").textContent = "Drag & drop a .txt or .md file here";
            uploadBtn.disabled = true;
        }
    });

    // ------------------------------------------------------------------
    // Re-index
    // ------------------------------------------------------------------

    reindexBtn.addEventListener("click", async () => {
        reindexBtn.disabled = true;
        reindexBtn.textContent = "Re-indexing...";

        try {
            const res = await fetch("/api/reindex", { method: "POST" });
            const data = await res.json();
            showUploadStatus(data.message, "success");
            updateSources(data.sources);
        } catch (err) {
            showUploadStatus("Re-index failed: " + err.message, "error");
        } finally {
            reindexBtn.disabled = false;
            reindexBtn.textContent = "Re-index All";
        }
    });

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    function showUploadStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = "upload-status " + type;
        uploadStatus.classList.remove("hidden");
    }

    function updateSources(sources) {
        sourcesSidebar.innerHTML = "";
        if (sources && sources.length > 0) {
            sources.forEach((s) => {
                const li = document.createElement("li");
                li.textContent = s;
                sourcesSidebar.appendChild(li);
            });
        } else {
            const li = document.createElement("li");
            li.className = "empty";
            li.textContent = "No documents indexed yet.";
            sourcesSidebar.appendChild(li);
        }
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
});
