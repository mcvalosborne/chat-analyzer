"""Chat format detection and analysis streaming via Claude API or Claude Code CLI."""

import base64
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile

from prompts import SYSTEM_BASE, FORMAT_HINTS, ANALYSIS_FRAMEWORKS


def _use_cli():
    """Determine whether to use Claude Code CLI (subscription) or direct API."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return False
    # Check if claude CLI is available
    return shutil.which("claude") is not None


def _get_api_client():
    """Lazy-load the Anthropic client only when needed."""
    import anthropic
    return anthropic.Anthropic()


# --- Format Detection ---

def detect_format(filename: str, content: bytes) -> dict:
    """Auto-detect chat platform from file content and name."""
    name = filename.lower()
    text = None

    try:
        text = content.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        pass

    if name == "_chat.txt" or name.endswith("_chat.txt"):
        return _whatsapp_metadata(text)

    if name.endswith(".json") and text:
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "messages" in data:
                msgs = data["messages"]
                if len(msgs) > 0 and isinstance(msgs[0], dict) and "author" in msgs[0]:
                    return _discord_metadata(msgs)
                return _telegram_json_metadata(data)
            if isinstance(data, list) and len(data) > 0 and "ts" in data[0]:
                return _slack_metadata(data)
            if isinstance(data, list) and len(data) > 0 and "Author" in data[0]:
                return _discord_metadata(data)
        except json.JSONDecodeError:
            pass

    if name == "messages.html" or (name.endswith(".html") and text and "tgme" in text):
        return {"platform": "telegram_html", "confidence": "medium", "message_count_estimate": text.count("message default") if text else 0}

    if name.endswith(".csv") and text:
        first_line = text.split("\n")[0] if text else ""
        if "Author" in first_line and "Content" in first_line:
            lines = text.strip().split("\n")
            return {"platform": "discord", "confidence": "high", "message_count_estimate": max(0, len(lines) - 1)}

    if text and name.endswith(".txt"):
        wa_pattern = re.compile(r"\[\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}")
        wa_matches = wa_pattern.findall(text[:5000])
        if len(wa_matches) > 3:
            return _whatsapp_metadata(text)
        lines = text.strip().split("\n")
        return {"platform": "generic", "confidence": "low", "message_count_estimate": len(lines)}

    return {"platform": "unknown", "confidence": "low", "message_count_estimate": 0}


def _whatsapp_metadata(text: str) -> dict:
    if not text:
        return {"platform": "whatsapp", "confidence": "high", "message_count_estimate": 0}
    lines = text.strip().split("\n")
    msg_count = sum(1 for l in lines if l.startswith("[") or re.match(r"\d{1,2}/\d{1,2}/\d{2,4}", l))
    dates = re.findall(r"(\d{1,2}/\d{1,2}/\d{2,4})", text[:500] + text[-500:])
    date_range = {"start": dates[0], "end": dates[-1]} if dates else {}
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

MAX_CHAT_CHARS = 600_000  # ~150k tokens


def _build_prompt(chat_content: str, analysis_type: str, platform: str) -> tuple[str, str]:
    """Build system prompt and user message for analysis."""
    framework = ANALYSIS_FRAMEWORKS.get(analysis_type, ANALYSIS_FRAMEWORKS["general_exploration"])
    format_hint = FORMAT_HINTS.get(platform, FORMAT_HINTS["generic"])

    system_prompt = f"""{SYSTEM_BASE}

## Platform Context
{format_hint}

{framework}"""

    # Truncate if needed
    if len(chat_content) > MAX_CHAT_CHARS:
        head = chat_content[:MAX_CHAT_CHARS // 10]
        tail = chat_content[-(MAX_CHAT_CHARS * 9 // 10):]
        chat_text = f"{head}\n\n[... {len(chat_content) - MAX_CHAT_CHARS:,} characters omitted — showing earliest and most recent messages ...]\n\n{tail}"
    else:
        chat_text = chat_content

    user_message = f"Analyze this chat export:\n\n<chat_content>\n{chat_text}\n</chat_content>"

    return system_prompt, user_message


def stream_analysis(
    chat_content: str,
    analysis_type: str,
    platform: str,
    additional_files: list[dict] | None = None,
):
    """Stream analysis — auto-selects Claude Code CLI or direct API."""
    if _use_cli():
        yield from _stream_via_cli(chat_content, analysis_type, platform, additional_files)
    else:
        yield from _stream_via_api(chat_content, analysis_type, platform, additional_files)


def _stream_via_cli(
    chat_content: str,
    analysis_type: str,
    platform: str,
    additional_files: list[dict] | None = None,
):
    """Stream analysis through the Claude Code CLI (uses subscription credits)."""
    system_prompt, user_message = _build_prompt(chat_content, analysis_type, platform)

    # Add any additional text files inline
    if additional_files:
        for f in additional_files:
            if f["type"] == "text":
                user_message += f"\n\n<additional_document name=\"{f['name']}\">\n{f['data']}\n</additional_document>"

    # Clean environment so claude doesn't think it's nested inside another session
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    proc = subprocess.Popen(
        [
            "claude",
            "-p",                      # print mode (non-interactive, single turn)
            "--output-format", "text",  # plain text output
            "--model", "sonnet",        # fast + capable
            "--append-system-prompt", system_prompt,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # line-buffered
        env=env,
    )

    # Send prompt via stdin
    proc.stdin.write(user_message)
    proc.stdin.close()

    for line in iter(proc.stdout.readline, ""):
        yield line
    proc.wait()

    if proc.returncode != 0:
        stderr = proc.stderr.read()
        if stderr:
            yield f"\n\n---\n**Error from Claude Code:** {stderr.strip()}"


def _stream_via_api(
    chat_content: str,
    analysis_type: str,
    platform: str,
    additional_files: list[dict] | None = None,
):
    """Stream analysis through the Anthropic API directly (uses API key)."""
    system_prompt, user_message = _build_prompt(chat_content, analysis_type, platform)

    messages_content = [{"type": "text", "text": user_message}]

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

    client = _get_api_client()
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=12000,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


# --- Follow-up Streaming ---

def stream_followup(
    chat_content: str,
    platform: str,
    history: list[dict],
    question: str,
):
    """Stream a follow-up response with conversation context."""
    if _use_cli():
        yield from _followup_via_cli(chat_content, platform, history, question)
    else:
        yield from _followup_via_api(chat_content, platform, history, question)


def _followup_system_prompt(platform: str) -> str:
    format_hint = FORMAT_HINTS.get(platform, FORMAT_HINTS["generic"])
    return f"""{SYSTEM_BASE}

## Platform Context
{format_hint}

You are continuing a conversation about a chat export analysis. The user has follow-up questions about your previous analysis. Answer based on the chat data and your prior findings. Be specific and cite evidence from the messages when possible."""


def _followup_via_cli(
    chat_content: str,
    platform: str,
    history: list[dict],
    question: str,
):
    """Follow-up via Claude Code CLI."""
    system_prompt = _followup_system_prompt(platform)

    # Build context: include prior analysis summary + the new question
    # Truncate chat content for context window headroom
    chat_excerpt = chat_content[:MAX_CHAT_CHARS // 2] if len(chat_content) > MAX_CHAT_CHARS // 2 else chat_content

    context_parts = [f"<chat_content>\n{chat_excerpt}\n</chat_content>\n"]
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        context_parts.append(f"<previous_{role.lower()}>\n{msg['content']}\n</previous_{role.lower()}>")
    context_parts.append(f"\nFollow-up question: {question}")

    full_prompt = "\n\n".join(context_parts)

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    proc = subprocess.Popen(
        [
            "claude",
            "-p",
            "--output-format", "text",
            "--model", "sonnet",
            "--append-system-prompt", system_prompt,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    proc.stdin.write(full_prompt)
    proc.stdin.close()

    for line in iter(proc.stdout.readline, ""):
        yield line
    proc.wait()

    if proc.returncode != 0:
        stderr = proc.stderr.read()
        if stderr:
            yield f"\n\n---\n**Error from Claude Code:** {stderr.strip()}"


def _followup_via_api(
    chat_content: str,
    platform: str,
    history: list[dict],
    question: str,
):
    """Follow-up via Anthropic API with proper multi-turn conversation."""
    system_prompt = _followup_system_prompt(platform)

    # Truncate chat for context headroom
    chat_excerpt = chat_content[:MAX_CHAT_CHARS // 2] if len(chat_content) > MAX_CHAT_CHARS // 2 else chat_content

    # Build multi-turn messages: first user msg includes the chat data
    messages = []
    for i, msg in enumerate(history):
        if i == 0 and msg["role"] == "user":
            # First user message — attach the chat content
            messages.append({
                "role": "user",
                "content": f"<chat_content>\n{chat_excerpt}\n</chat_content>\n\n{msg['content']}",
            })
        else:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add the new follow-up question
    messages.append({"role": "user", "content": question})

    client = _get_api_client()
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
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
        try:
            text = content.decode("utf-8")
            return {"type": "text", "data": text, "name": filename}
        except (UnicodeDecodeError, ValueError):
            return None
