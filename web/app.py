"""
Chat Analyzer — Lightweight Web UI

Launch:
    cd ~/chat-analyzer/web
    pip install -r requirements.txt
    python app.py

Opens at http://localhost:8420
"""

import json
import os
import uuid

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

from analyzer import detect_format, prepare_file, stream_analysis

app = Flask(__name__)

# In-memory session storage
sessions: dict[str, dict] = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    """Accept files, detect format, return session with metadata."""
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files provided"}), 400

    session_id = uuid.uuid4().hex[:12]
    session = {
        "id": session_id,
        "chat_content": None,
        "chat_filename": None,
        "platform": "unknown",
        "detection": {},
        "additional_files": [],
    }

    # Chat file extensions
    chat_extensions = {".txt", ".json", ".csv", ".html"}

    for f in files:
        content = f.read()
        name = f.filename or "unknown"
        ext = os.path.splitext(name)[1].lower()

        # Try to identify the chat file (first text-like file)
        if ext in chat_extensions and session["chat_content"] is None:
            detection = detect_format(name, content)
            if detection.get("platform") != "unknown":
                try:
                    session["chat_content"] = content.decode("utf-8")
                except UnicodeDecodeError:
                    session["chat_content"] = content.decode("latin-1")
                session["chat_filename"] = name
                session["platform"] = detection["platform"]
                session["detection"] = detection
                continue

        # Otherwise treat as additional context file
        prepared = prepare_file(name, content)
        if prepared:
            session["additional_files"].append(prepared)

    # If no chat file was detected but we have text files, use the first one
    if session["chat_content"] is None:
        for f_data in session["additional_files"]:
            if f_data["type"] == "text":
                session["chat_content"] = f_data["data"]
                session["chat_filename"] = f_data["name"]
                session["platform"] = "generic"
                session["detection"] = {"platform": "generic", "confidence": "low", "message_count_estimate": session["chat_content"].count("\n")}
                session["additional_files"].remove(f_data)
                break

    if session["chat_content"] is None:
        return jsonify({"error": "No readable chat file found. Upload a .txt, .json, .csv, or .html chat export."}), 400

    sessions[session_id] = session

    return jsonify({
        "session_id": session_id,
        "filename": session["chat_filename"],
        "platform": session["platform"],
        "detection": session["detection"],
        "additional_files_count": len(session["additional_files"]),
    })


@app.route("/api/analyze")
def analyze():
    """Stream analysis results via SSE."""
    session_id = request.args.get("session")
    analysis_type = request.args.get("type", "general_exploration")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    session = sessions[session_id]

    def generate():
        try:
            for text in stream_analysis(
                chat_content=session["chat_content"],
                analysis_type=analysis_type,
                platform=session["platform"],
                additional_files=session["additional_files"] or None,
            ):
                yield f"data: {json.dumps({'type': 'content', 'text': text})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠  ANTHROPIC_API_KEY not set. Export it or run inside a Claude Code session.\n")

    print("\n  Chat Analyzer")
    print("  http://localhost:8420\n")
    app.run(host="127.0.0.1", port=8420, debug=False)
