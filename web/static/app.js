const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

let sessionId = null;
let selectedType = null;
let rawMarkdown = "";
let activeHistoryId = null;

// --- Sidebar ---

const sidebar = $("#sidebar");
const sidebarList = $("#sidebar-list");

$("#sidebar-open").addEventListener("click", () => sidebar.classList.remove("collapsed"));
$("#sidebar-close").addEventListener("click", () => sidebar.classList.add("collapsed"));

function loadHistoryList() {
    fetch("/api/history")
        .then((r) => r.json())
        .then((entries) => {
            if (!entries.length) {
                sidebarList.innerHTML = '<p class="sidebar-empty">No saved analyses yet.</p>';
                return;
            }
            sidebarList.innerHTML = entries
                .map((e) => {
                    const date = new Date(e.timestamp * 1000);
                    const dateStr = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
                    const typeLabel = e.analysis_type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
                    return `<button class="sidebar-item${e.id === activeHistoryId ? " active" : ""}" data-id="${e.id}">
                        <div class="sidebar-item-title">${escapeHtml(e.title)}</div>
                        <div class="sidebar-item-meta">
                            <span class="badge ${e.platform}">${e.platform}</span>
                            <span>${typeLabel}</span>
                            <span>${dateStr}</span>
                            <button class="sidebar-item-delete" data-id="${e.id}" title="Delete">&times;</button>
                        </div>
                    </button>`;
                })
                .join("");

            // Click to load
            sidebarList.querySelectorAll(".sidebar-item").forEach((btn) => {
                btn.addEventListener("click", (e) => {
                    if (e.target.classList.contains("sidebar-item-delete")) return;
                    loadHistoryEntry(btn.dataset.id);
                });
            });

            // Delete buttons
            sidebarList.querySelectorAll(".sidebar-item-delete").forEach((btn) => {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    deleteHistoryEntry(btn.dataset.id);
                });
            });
        });
}

function loadHistoryEntry(id) {
    fetch(`/api/history/${id}`)
        .then((r) => r.json())
        .then((data) => {
            if (data.error) return;

            // Set active state
            activeHistoryId = id;
            sessionId = id;
            rawMarkdown = data.analysis_md;

            // Show results
            resultsSection.classList.add("visible");
            resultsContent.innerHTML = renderMarkdown(rawMarkdown);

            // Show file info
            dropZone.classList.add("has-file");
            fileInfo.classList.add("visible");
            $(".file-info .filename").textContent = data.filename || data.title;
            let metaHTML = `<span class="badge ${data.platform}">${data.platform}</span>`;
            if (data.detection?.message_count_estimate) {
                metaHTML += `<span>${data.detection.message_count_estimate.toLocaleString()} messages</span>`;
            }
            if (data.detection?.participants?.length) {
                metaHTML += `<span>${data.detection.participants.join(", ")}</span>`;
            }
            $(".file-info .meta").innerHTML = metaHTML;
            $(".drop-prompt").style.display = "none";

            // Hide analysis type selector (already analyzed)
            analysisSection.classList.remove("visible");
            analyzeBtn.classList.remove("visible");

            // Show follow-up chat and restore prior follow-ups
            const followupSection = $(".followup-section");
            followupSection.classList.add("visible");
            followupThread.innerHTML = "";

            if (data.followups && data.followups.length) {
                for (const msg of data.followups) {
                    const div = document.createElement("div");
                    div.className = `followup-msg ${msg.role === "user" ? "user" : "assistant"}`;
                    div.innerHTML = msg.role === "user" ? escapeHtml(msg.content) : renderMarkdown(msg.content);
                    followupThread.appendChild(div);
                }
            }

            $("#followup-input").focus();

            // Highlight in sidebar
            loadHistoryList();

            // Collapse sidebar on mobile
            if (window.innerWidth < 768) {
                sidebar.classList.add("collapsed");
            }
        });
}

function deleteHistoryEntry(id) {
    fetch(`/api/history/${id}`, { method: "DELETE" }).then(() => {
        if (activeHistoryId === id) {
            activeHistoryId = null;
            resetUI();
        }
        loadHistoryList();
    });
}

// Load history on startup
document.addEventListener("DOMContentLoaded", loadHistoryList);

// --- Drop Zone ---

const dropZone = $(".drop-zone");
const fileInput = $("#file-input");
const fileInfo = $(".file-info");
const analysisSection = $(".analysis-section");
const analyzeBtn = $(".analyze-btn");
const resultsSection = $(".results-section");
const resultsContent = $(".results-content");
const statusEl = $(".status");
const errorEl = $(".error");

["dragenter", "dragover"].forEach((e) =>
    dropZone.addEventListener(e, (ev) => {
        ev.preventDefault();
        dropZone.classList.add("dragover");
    })
);

["dragleave", "drop"].forEach((e) =>
    dropZone.addEventListener(e, () => dropZone.classList.remove("dragover"))
);

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length) handleFiles(files);
});

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) handleFiles(fileInput.files);
});

$(".clear-btn").addEventListener("click", (e) => {
    e.stopPropagation();
    resetUI();
});

async function handleFiles(fileList) {
    const formData = new FormData();
    for (const f of fileList) {
        formData.append("files", f);
    }

    showStatus("Detecting format...");
    hideError();

    try {
        const res = await fetch("/api/upload", { method: "POST", body: formData });
        const data = await res.json();

        if (!res.ok) {
            showError(data.error || "Upload failed");
            hideStatus();
            return;
        }

        sessionId = data.session_id;
        showFileInfo(data);
        hideStatus();
    } catch (err) {
        showError("Upload failed: " + err.message);
        hideStatus();
    }
}

function showFileInfo(data) {
    dropZone.classList.add("has-file");
    fileInfo.classList.add("visible");

    $(".file-info .filename").textContent = data.filename;

    const det = data.detection;
    let metaHTML = `<span class="badge ${det.platform}">${det.platform}</span>`;
    if (det.message_count_estimate) {
        metaHTML += `<span>${det.message_count_estimate.toLocaleString()} messages</span>`;
    }
    if (det.date_range?.start) {
        metaHTML += `<span>${det.date_range.start} — ${det.date_range.end}</span>`;
    }
    if (det.participants?.length) {
        metaHTML += `<span>${det.participants.join(", ")}</span>`;
    }
    if (data.additional_files_count > 0) {
        metaHTML += `<span>+${data.additional_files_count} additional file${data.additional_files_count > 1 ? "s" : ""}</span>`;
    }
    $(".file-info .meta").innerHTML = metaHTML;

    analysisSection.classList.add("visible");
    analyzeBtn.classList.add("visible");

    // Hide the drop prompt text
    $(".drop-prompt").style.display = "none";
}

// --- Analysis Type Selection ---

$$(".type-card").forEach((card) => {
    card.addEventListener("click", () => {
        $$(".type-card").forEach((c) => c.classList.remove("selected"));
        card.classList.add("selected");
        selectedType = card.dataset.type;
    });
});

// Default selection
document.addEventListener("DOMContentLoaded", () => {
    const first = $(".type-card");
    if (first) {
        first.classList.add("selected");
        selectedType = first.dataset.type;
    }
});

// --- Analyze ---

analyzeBtn.addEventListener("click", startAnalysis);

function startAnalysis() {
    if (!sessionId || !selectedType) return;

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";
    rawMarkdown = "";

    resultsSection.classList.add("visible");
    resultsSection.classList.add("streaming");
    resultsContent.innerHTML = "";
    hideError();

    const source = new EventSource(
        `/api/analyze?session=${encodeURIComponent(sessionId)}&type=${encodeURIComponent(selectedType)}`
    );

    source.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "content") {
            rawMarkdown += data.text;
            resultsContent.innerHTML = renderMarkdown(rawMarkdown);
            // Auto-scroll to bottom
            resultsContent.scrollTop = resultsContent.scrollHeight;
        } else if (data.type === "done") {
            source.close();
            onAnalysisComplete();
        } else if (data.type === "error") {
            source.close();
            showError(data.text);
            onAnalysisComplete();
        }
    };

    source.onerror = () => {
        source.close();
        showError("Connection lost. Check that the server is running.");
        onAnalysisComplete();
    };
}

function onAnalysisComplete() {
    resultsSection.classList.remove("streaming");
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze";
    resultsContent.innerHTML = renderMarkdown(rawMarkdown);

    // Show follow-up chat
    $(".followup-section").classList.add("visible");
    $("#followup-input").focus();

    // Refresh sidebar with new entry
    activeHistoryId = sessionId;
    loadHistoryList();
}

// --- Copy / Download ---

$("#copy-btn")?.addEventListener("click", () => {
    navigator.clipboard.writeText(rawMarkdown).then(() => {
        const btn = $("#copy-btn");
        btn.textContent = "Copied!";
        setTimeout(() => (btn.textContent = "Copy"), 1500);
    });
});

$("#download-btn")?.addEventListener("click", () => {
    const blob = new Blob([rawMarkdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analysis-${selectedType}-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
});

// --- Follow-up Chat ---

const followupForm = $("#followup-form");
const followupInput = $("#followup-input");
const followupThread = $("#followup-thread");
const followupBtn = $("#followup-btn");

followupForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = followupInput.value.trim();
    if (!question || !sessionId) return;

    // Add user message to thread
    const userMsg = document.createElement("div");
    userMsg.className = "followup-msg user";
    userMsg.textContent = question;
    followupThread.appendChild(userMsg);

    // Clear input
    followupInput.value = "";
    followupBtn.disabled = true;

    // Add streaming assistant message
    const assistantMsg = document.createElement("div");
    assistantMsg.className = "followup-msg assistant streaming";
    followupThread.appendChild(assistantMsg);

    let followupMd = "";

    const source = new EventSource(
        `/api/followup?session=${encodeURIComponent(sessionId)}&q=${encodeURIComponent(question)}`
    );

    source.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "content") {
            followupMd += data.text;
            assistantMsg.innerHTML = renderMarkdown(followupMd);
            assistantMsg.scrollIntoView({ behavior: "smooth", block: "end" });
        } else if (data.type === "done") {
            source.close();
            assistantMsg.classList.remove("streaming");
            assistantMsg.innerHTML = renderMarkdown(followupMd);
            followupBtn.disabled = false;
            followupInput.focus();
        } else if (data.type === "error") {
            source.close();
            assistantMsg.classList.remove("streaming");
            assistantMsg.innerHTML = `<p style="color: var(--red)">Error: ${escapeHtml(data.text)}</p>`;
            followupBtn.disabled = false;
        }
    };

    source.onerror = () => {
        source.close();
        assistantMsg.classList.remove("streaming");
        assistantMsg.innerHTML = `<p style="color: var(--red)">Connection lost.</p>`;
        followupBtn.disabled = false;
    };
});

// --- Markdown Renderer ---

function renderMarkdown(md) {
    let html = escapeHtml(md);

    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");

    // Tables
    html = html.replace(
        /^(\|.+\|)\n(\|[\s\-:|]+\|)\n((?:\|.+\|\n?)+)/gm,
        (_, header, separator, body) => {
            const headers = header.split("|").filter(Boolean).map((h) => `<th>${h.trim()}</th>`).join("");
            const rows = body.trim().split("\n").map((row) => {
                const cells = row.split("|").filter(Boolean).map((c) => `<td>${c.trim()}</td>`).join("");
                return `<tr>${cells}</tr>`;
            }).join("");
            return `<table><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`;
        }
    );

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Bold and italic
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Blockquotes
    html = html.replace(/^&gt; (.+)$/gm, "<blockquote>$1</blockquote>");

    // Horizontal rules
    html = html.replace(/^---$/gm, "<hr>");

    // Unordered lists
    html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
    html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, "<ul>$1</ul>");

    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

    // Paragraphs (lines not already wrapped)
    html = html.replace(/^(?!<[huptblod]|<li|<hr|<blockquote|<pre)(.+)$/gm, "<p>$1</p>");

    // Clean up extra newlines
    html = html.replace(/\n{2,}/g, "\n");

    return html;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// --- UI Helpers ---

function resetUI() {
    sessionId = null;
    rawMarkdown = "";
    dropZone.classList.remove("has-file");
    fileInfo.classList.remove("visible");
    analysisSection.classList.remove("visible");
    analyzeBtn.classList.remove("visible");
    resultsSection.classList.remove("visible");
    resultsSection.classList.remove("streaming");
    $(".followup-section").classList.remove("visible");
    followupThread.innerHTML = "";
    $(".drop-prompt").style.display = "";
    fileInput.value = "";
    hideError();
    hideStatus();
}

function showStatus(msg) {
    $(".status-text").textContent = msg;
    statusEl.classList.add("visible");
}

function hideStatus() {
    statusEl.classList.remove("visible");
}

function showError(msg) {
    errorEl.textContent = msg;
    errorEl.classList.add("visible");
}

function hideError() {
    errorEl.classList.remove("visible");
}
