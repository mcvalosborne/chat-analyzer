# Chat Analyzer

A conversation intelligence tool powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that transforms WhatsApp chat exports into psychological profiles, sales strategies, and relationship dynamics reports.

Built as a skill-based Claude Code project — no traditional runtime or dependencies. You bring the data, Claude does the analysis.

---

## What It Does

Chat Analyzer reads WhatsApp exports (text, images, voice notes, videos, PDFs) and produces structured intelligence reports:

- **Psychological Profiles** — Big Five personality estimation, attachment style, cognitive style, communication DNA
- **Sales Strategies** — Buying signal detection, objection prediction, engagement playbooks, product recommendations
- **Relationship Dynamics** — Power balance, communication health, conflict patterns, evolution over time
- **Comparative Analysis** — Cross-person or cross-period behavioral pattern comparison

All analysis runs locally. No data leaves your machine.

---

## How It Works

```
WhatsApp Export (.zip)
        │
        ▼
┌─────────────────────┐
│  Data Organization   │  Unzip → sort into chats/media/docs
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

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/mcvalosborne/chat-analyzer.git
cd chat-analyzer

# 2. Export a WhatsApp chat (on your phone):
#    Chat → ⋮ → More → Export chat → Include media
#    Transfer the .zip to your machine

# 3. Organize the export
mkdir -p data/chats/jane-doe/media/{photos,videos,audio,documents}
unzip WhatsApp\ Chat.zip -d data/chats/jane-doe/
mv data/chats/jane-doe/*.jpg data/chats/jane-doe/media/photos/
mv data/chats/jane-doe/*.mp4 data/chats/jane-doe/media/videos/
mv data/chats/jane-doe/*.opus data/chats/jane-doe/media/audio/
# Keep _chat.txt in the root of the person folder

# 4. Start a Claude Code session
claude

# 5. Begin the guided analysis
/start
```

Claude will ask you to choose an analysis depth and goal, then walk you through the rest.

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
│   ├── start-analysis.md          # Interactive startup wizard
│   ├── analyze-chat.md            # Core chat parsing & pattern detection
│   ├── profile-person.md          # Psychological profiling framework
│   ├── sales-insights.md          # Sales receptivity & strategy generation
│   ├── transcribe-media.md        # Audio/video/image processing
│   ├── process-whatsapp-export.md # Large export handling (100MB+)
│   └── compare-sessions.md        # Multi-conversation comparison
├── data/                    # Your data goes here (git-ignored)
│   ├── chats/[person]/      #   WhatsApp exports per person
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
| `/analyze-chat` | Parse messages, compute metrics, detect patterns | `analysis/profiles/[name]/chat-analysis.md` |
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
| **Text only** | `_chat.txt` messages | Fast pattern scan, communication style |
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
| Images (JPG/PNG) | Visual descriptions, context, shared interests |
| Audio (OPUS/M4A/MP3) | Full transcription, tone analysis |
| Video (MP4) | Audio track + extracted frame analysis |
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
