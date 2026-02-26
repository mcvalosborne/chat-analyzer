# Chat Analyzer

A conversation intelligence tool powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that transforms chat exports from **any messaging platform** into psychological profiles, sales strategies, and relationship dynamics reports.

Built as a skill-based Claude Code project — no traditional runtime or dependencies. You bring the data, Claude does the analysis.

---

## Supported Platforms

| Platform | Export Format | Chat File |
|----------|-------------|-----------|
| **WhatsApp** | .zip with media | `_chat.txt` |
| **Telegram** | JSON or HTML (Desktop export) | `result.json` / `messages.html` |
| **iMessage** | Database export via iMazing etc. | `.txt` or `.csv` |
| **Slack** | Workspace JSON export | `*.json` per channel |
| **Discord** | DiscordChatExporter JSON/CSV | `.json` or `.csv` |
| **Signal** | Plaintext backup | `.txt` or `.xml` |
| **Any other** | Timestamped text logs | `.txt`, `.csv`, `.json` |

The system auto-detects the format when you run `/analyze-chat`.

---

## What It Does

Chat Analyzer reads chat exports (text, images, voice notes, videos, PDFs) and produces structured intelligence reports:

- **Psychological Profiles** — Big Five personality estimation, attachment style, cognitive style, communication DNA
- **Sales Strategies** — Buying signal detection, objection prediction, engagement playbooks, product recommendations
- **Relationship Dynamics** — Power balance, communication health, conflict patterns, evolution over time
- **Comparative Analysis** — Cross-person or cross-period behavioral pattern comparison

All analysis runs locally. No data leaves your machine.

---

## How It Works

```
Chat Export (any platform)
        │
        ▼
┌─────────────────────┐
│  Data Organization   │  Drop files into data/chats/[name]/
│  + Format Detection  │  Auto-detect: WhatsApp, Telegram, Slack...
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  /analyze-chat       │  Parse messages, extract patterns,
│                      │  quantify communication metrics
└────────┬────────────┘
         │
    ┌────┴────────────────────────┐
    │              │              │
    ▼              ▼              ▼
┌──────────┐ ┌───────────┐ ┌──────────────┐
│ /profile │ │ /sales-   │ │ /transcribe- │
│ -person  │ │ insights  │ │ media        │
└──────────┘ └───────────┘ └──────────────┘
    │              │              │
    └──────────────┼──────────────┘
                   ▼
         ┌──────────────────┐
         │ /compare-sessions│  Optional cross-analysis
         └──────────────────┘
```

For large chat histories (1000+ messages), the orchestrator delegates date-range chunks to parallel sub-agents, then synthesizes results into a unified report.

---

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- `ffmpeg` (only needed for video frame extraction)

No package managers, no `npm install`, no Python environment. The skills are plain Markdown files that Claude Code interprets at runtime.

For the **web UI** only: Python 3 + pip (auto-creates a venv).

---

## Quick Start

### Option A: Web UI (drag and drop)

```bash
git clone https://github.com/mcvalosborne/chat-analyzer.git
cd chat-analyzer

# Launch the web UI
./web/start.sh
```

Open http://localhost:8420, drag in a chat export, pick an analysis type, and hit Analyze. Results stream in real-time.

The server auto-detects how to connect to Claude:

| You have... | It uses | Cost |
|-------------|---------|------|
| `claude` CLI installed | Claude Code subscription | Included in your plan |
| `ANTHROPIC_API_KEY` set | Anthropic API directly | Per-token API pricing |

If both are available, it prefers the API key. To force subscription mode, just don't set the env var.

The first run creates a Python venv and installs Flask + the Anthropic SDK (~2 deps).

### Option B: Claude Code CLI (full power)

```bash
# 1. Clone the repo
git clone https://github.com/mcvalosborne/chat-analyzer.git
cd chat-analyzer

# 2. Export a chat from your platform of choice:
#    - WhatsApp: Chat → ⋮ → More → Export chat → Include media
#    - Telegram: Desktop app → ⋮ → Export chat history (JSON format)
#    - Slack: Workspace settings → Export data
#    - Discord: Use DiscordChatExporter
#    - Or just grab any text chat log

# 3. Place the export in the data folder
mkdir -p data/chats/jane-doe/media/{photos,videos,audio,documents}
# Drop chat files in the root, media in subfolders

# 4. Start a Claude Code session
claude

# 5. Begin the guided analysis
/start
```

Claude will auto-detect the chat format, ask you to choose an analysis depth and goal, then walk you through the rest.

The web UI is great for quick one-off analysis. The CLI gives you the full skill pipeline, multi-agent parallelism, media transcription, and interactive follow-up questions.

---

## Project Structure

```
chat-analyzer/
├── CLAUDE.md               # Project instructions for Claude Code
├── WORKFLOW.md              # Detailed workflow patterns & example prompts
├── index.json               # Master index of all conversations & analyses
├── scripts/
│   └── extract-video-frames.sh   # ffmpeg helper for video thumbnails
├── skills/
│   ├── start-analysis.md         # Interactive startup wizard
│   ├── analyze-chat.md           # Core chat parsing & pattern detection
│   ├── profile-person.md         # Psychological profiling framework
│   ├── sales-insights.md         # Sales receptivity & strategy generation
│   ├── transcribe-media.md       # Audio/video/image processing
│   ├── process-export.md         # Large export handling (100MB+)
│   └── compare-sessions.md       # Multi-conversation comparison
├── web/
│   ├── app.py                    # Flask server
│   ├── analyzer.py               # Format detection + Claude API streaming
│   ├── prompts.py                # Analysis frameworks from skills
│   ├── start.sh                  # One-command launcher
│   ├── requirements.txt          # flask, anthropic
│   ├── static/                   # CSS + JS
│   └── templates/                # HTML
├── data/                    # Your data goes here (git-ignored)
│   ├── chats/[person]/      #   Chat exports per person
│   ├── media/               #   Standalone media files
│   ├── docs/                #   Additional documents
│   └── links/               #   Saved webpage content
└── analysis/                # Generated reports (git-ignored)
    ├── profiles/[person]/   #   Per-person analysis files
    └── reports/             #   Cross-conversation reports
```

Both `data/` and `analysis/` are git-ignored — your conversations and profiles stay local.

---

## Skills Reference

| Command | Purpose | Output |
|---------|---------|--------|
| `/start` | Interactive guided setup — choose depth + goal | Routes to appropriate skill |
| `/analyze-chat` | Parse messages (any format), compute metrics, detect patterns | `analysis/profiles/[name]/chat-analysis.md` |
| `/profile-person` | Big Five, attachment style, values, cognitive profile | `analysis/profiles/[name]/profile.md` |
| `/sales-insights` | Buying signals, objection prep, engagement playbook | `analysis/reports/[name]-sales-strategy.md` |
| `/transcribe-media` | Process voice notes, images, videos, PDFs | Transcripts added to analysis folder |
| `/process-export` | Handle large exports (100MB+) with mixed media | Organized data + initial analysis |
| `/compare-sessions` | Compare two people or two time periods | `analysis/reports/comparison.md` |

---

## Analysis Depth Options

When you run `/start`, you choose how deep to go:

| Level | What's Analyzed | Best For |
|-------|----------------|----------|
| **Text only** | Chat text messages | Fast pattern scan, communication style |
| **Text + Documents** | Messages + PDFs, shared files | Professional relationships, business context |
| **Full analysis** | Everything — images, voice notes, video frames | Complete psychological profiling |

---

## What Claude Analyzes

### From Text Messages
- Message volume, timing, and response latency
- Topic frequency and sentiment over time
- Linguistic markers (vocabulary complexity, emoji patterns, formality shifts)
- Initiation vs response ratio and power dynamics

### From Media
| File Type | What Claude Extracts |
|-----------|---------------------|
| Images (JPG/PNG/WEBP) | Visual descriptions, context, shared interests |
| Audio (OPUS/OGG/M4A/MP3) | Full transcription, tone analysis |
| Video (MP4/MOV/WebM) | Audio track + extracted frame analysis |
| PDFs | Text extraction, document context |
| vCards (.vcf) | Contact information parsing |

For video files, run the frame extraction script first:

```bash
./scripts/extract-video-frames.sh data/chats/jane-doe/
```

---

## Multi-Agent Architecture

For large datasets, Chat Analyzer uses Claude Code's sub-agent system to parallelize work:

```
Main Agent (orchestrator)
├── Explore Agent     → Catalog files, discover structure
├── Analyzer Agent 1  → Messages Jan–Mar
├── Analyzer Agent 2  → Messages Apr–Jun
├── Analyzer Agent 3  → Messages Jul–Sep
├── Analyzer Agent 4  → Messages Oct–Dec
└── Research Agent    → Web search for psychological frameworks
         │
         ▼
   Synthesized Report
```

This means a 10,000-message history doesn't need to be processed sequentially — it's chunked across agents and recombined.

---

## Example Prompts

Once you're in a Claude Code session with data loaded:

**Initial analysis:**
- "Analyze all chat data in the data folder"
- "Create a comprehensive profile of this person"
- "What are their main interests and pain points?"

**Sales-focused:**
- "What products would this person be interested in?"
- "How should I pitch [product] to them?"
- "What objections might they raise?"
- "When is the best time to reach out?"

**Deep dive:**
- "How has their communication style changed over time?"
- "What triggers positive responses from them?"
- "How do they make decisions?"
- "What topics should I avoid?"

---

## The Index File

`index.json` tracks all conversations and their metadata:

```json
{
  "conversations": [
    {
      "id": "person-name",
      "name": "Person Name",
      "relationship_type": "professional/personal",
      "platform": "whatsapp",
      "data_path": "data/chats/person-name/",
      "analysis_path": "analysis/profiles/person-name/",
      "date_range": { "start": "2020-01-01", "end": "2024-12-31" },
      "stats": {
        "message_count": 5000,
        "media": { "photos": 120, "videos": 15, "audio": 40, "documents": 5 }
      },
      "analyses": [
        {
          "type": "psychological-profile",
          "file": "profile.md",
          "created": "2024-12-15",
          "summary": "Brief description of findings"
        }
      ],
      "tags": ["mentor", "uk", "tech"]
    }
  ]
}
```

The index is updated automatically as you run analyses. Use tags for filtering when comparing across multiple contacts.

---

## Privacy & Ethics

- **Local only** — all processing happens on your machine via Claude Code. No data is uploaded to external services.
- **Git-ignored** — `data/` and `analysis/` are excluded from version control by default.
- **Probabilistic** — profiles are pattern-based estimations, not clinical diagnoses.
- **Your responsibility** — use insights ethically and with awareness of consent. Delete raw exports after analysis if appropriate.

---

## License

MIT
