"""Chat format detection and Claude API streaming analysis."""

import base64
import json
import mimetypes
import os
import re
from pathlib import Path

import anthropic

from prompts import SYSTEM_BASE, FORMAT_HINTS, ANALYSIS_FRAMEWORKS

client = anthropic.Anthropic()

# --- Format Detection ---

def detect_format(filename: str, content: bytes) -> dict:
    """Auto-detect chat platform from file content and name."""
    name = filename.lower()
    text = None

    # Try decoding as text
    try:
        text = content.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        pass

    # WhatsApp: _chat.txt or WhatsApp format pattern
    if name == "_chat.txt" or name.endswith("_chat.txt"):
        return _whatsapp_metadata(text)

    # Telegram JSON
    if name.endswith(".json") and text:
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "messages" in data:
                return _telegram_json_metadata(data)
            # Slack: list of objects with "ts" key
            if isinstance(data, list) and len(data) > 0 and "ts" in data[0]:
                return _slack_metadata(data)
            # Discord: dict or list with "Author" or "author"
            if isinstance(data, dict) and "messages" in data:
                msgs = data["messages"]
                if len(msgs) > 0 and "author" in msgs[0]:
                    return _discord_metadata(msgs)
            if isinstance(data, list) and len(data) > 0 and "Author" in data[0]:
                return _discord_metadata(data)
        except json.JSONDecodeError:
            pass

    # Telegram HTML
    if name == "messages.html" or (name.endswith(".html") and text and "tgme" in text):
        return {"platform": "telegram_html", "confidence": "medium", "message_count_estimate": text.count("message default") if text else 0}

    # CSV with Discord headers
    if name.endswith(".csv") and text:
        first_line = text.split("\n")[0] if text else ""
        if "Author" in first_line and "Content" in first_line:
            lines = text.strip().split("\n")
            return {"platform": "discord", "confidence": "high", "message_count_estimate": max(0, len(lines) - 1)}

    # Generic text — check for WhatsApp-like patterns
    if text and name.endswith(".txt"):
        # WhatsApp pattern: [dd/mm/yyyy, hh:mm:ss] or mm/dd/yy
        wa_pattern = re.compile(r"\[\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}")
        wa_matches = wa_pattern.findall(text[:5000])
        if len(wa_matches) > 3:
            return _whatsapp_metadata(text)

        # Generic timestamped text
        lines = text.strip().split("\n")
        return {"platform": "generic", "confidence": "low", "message_count_estimate": len(lines)}

    # Non-text file
    return {"platform": "unknown", "confidence": "low", "message_count_estimate": 0}


def _whatsapp_metadata(text: str) -> dict:
    if not text:
        return {"platform": "whatsapp", "confidence": "high", "message_count_estimate": 0}
    lines = text.strip().split("\n")
    # Count message lines (start with timestamp bracket)
    msg_count = sum(1 for l in lines if l.startswith("[") or re.match(r"\d{1,2}/\d{1,2}/\d{2,4}", l))
    # Extract date range
    dates = re.findall(r"(\d{1,2}/\d{1,2}/\d{2,4})", text[:500] + text[-500:])
    date_range = {"start": dates[0], "end": dates[-1]} if dates else {}
    # Extract participants
    participants = set()
    for match in re.finditer(r"[\]\s]([^:\[\]]+?):\s", text[:10000]):
        name = match.group(1).strip()
        if name and len(name) < 50:
            participants.add(name)
    return {
        "platform": "whatsapp",
        "confidence": "high",
        "message_count_estimate": msg_count,
        "date_range": date_range,
        "participants": list(participants)[:10],
    }


def _telegram_json_metadata(data: dict) -> dict:
    msgs = data.get("messages", [])
    participants = set()
    for m in msgs[:500]:
        if "from" in m:
            participants.add(m["from"])
    dates = [m.get("date", "") for m in msgs if m.get("date")]
    return {
        "platform": "telegram",
        "confidence": "high",
        "message_count_estimate": len(msgs),
        "date_range": {"start": dates[0], "end": dates[-1]} if dates else {},
        "participants": list(participants)[:10],
    }


def _slack_metadata(data: list) -> dict:
    participants = set()
    for m in data[:500]:
        if "user" in m:
            participants.add(m["user"])
    return {
        "platform": "slack",
        "confidence": "high",
        "message_count_estimate": len(data),
        "participants": list(participants)[:10],
    }


def _discord_metadata(data: list) -> dict:
    participants = set()
    key = "Author" if data and "Author" in data[0] else "author"
    for m in data[:500]:
        author = m.get(key)
        if isinstance(author, dict):
            author = author.get("name", author.get("username", ""))
        if author:
            participants.add(str(author))
    return {
        "platform": "discord",
        "confidence": "high",
        "message_count_estimate": len(data),
        "participants": list(participants)[:10],
    }


# --- Analysis Streaming ---

MAX_CHAT_CHARS = 600_000  # ~150k tokens, leaves room for system prompt + response

def stream_analysis(
    chat_content: str,
    analysis_type: str,
    platform: str,
    additional_files: list[dict] | None = None,
):
    """Stream analysis results from Claude API via SSE-compatible generator."""

    framework = ANALYSIS_FRAMEWORKS.get(analysis_type, ANALYSIS_FRAMEWORKS["general_exploration"])
    format_hint = FORMAT_HINTS.get(platform, FORMAT_HINTS["generic"])

    system_prompt = f"""{SYSTEM_BASE}

## Platform Context
{format_hint}

{framework}"""

    # Build messages
    messages_content = []

    # Add chat text
    if len(chat_content) > MAX_CHAT_CHARS:
        # Take first 10% and last 90% for recency bias
        head = chat_content[:MAX_CHAT_CHARS // 10]
        tail = chat_content[-(MAX_CHAT_CHARS * 9 // 10):]
        truncated_text = f"{head}\n\n[... {len(chat_content) - MAX_CHAT_CHARS:,} characters omitted for length — showing earliest and most recent messages ...]\n\n{tail}"
        messages_content.append({"type": "text", "text": f"Analyze this chat export:\n\n<chat_content>\n{truncated_text}\n</chat_content>"})
    else:
        messages_content.append({"type": "text", "text": f"Analyze this chat export:\n\n<chat_content>\n{chat_content}\n</chat_content>"})

    # Add additional files (images, PDFs)
    if additional_files:
        for f in additional_files:
            if f["type"] == "image":
                messages_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f["media_type"],
                        "data": f["data"],
                    },
                })
            elif f["type"] == "document":
                messages_content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": f["data"],
                    },
                })
            elif f["type"] == "text":
                messages_content.append({
                    "type": "text",
                    "text": f"<additional_document name=\"{f['name']}\">\n{f['data']}\n</additional_document>",
                })

    messages = [{"role": "user", "content": messages_content}]

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=12000,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def prepare_file(filename: str, content: bytes) -> dict | None:
    """Prepare a non-chat file for inclusion in the analysis."""
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        return None

    if mime.startswith("image/"):
        return {
            "type": "image",
            "media_type": mime,
            "data": base64.standard_b64encode(content).decode("ascii"),
            "name": filename,
        }
    elif mime == "application/pdf":
        return {
            "type": "document",
            "media_type": mime,
            "data": base64.standard_b64encode(content).decode("ascii"),
            "name": filename,
        }
    else:
        # Try as text
        try:
            text = content.decode("utf-8")
            return {"type": "text", "data": text, "name": filename}
        except (UnicodeDecodeError, ValueError):
            return None
