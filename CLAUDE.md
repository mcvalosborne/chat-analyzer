# Chat Analyzer Project

Analyze chat exports from any messaging platform — WhatsApp, Telegram, iMessage, Slack, Discord, or plain text logs — for psychological profiling, decision-making patterns, and sales receptivity insights.

## Startup Workflow

**When the user starts a session or says "let's begin", "start", "analyze", or similar:**

1. First, ask: "Do you have a chat export ready to analyze? If so, place it in `data/chats/` and let me know the folder name. I support WhatsApp, Telegram, iMessage, Slack, Discord, and plain text logs. Or drag the export file here and I'll help you set it up."

2. Once data is located, ask using AskUserQuestion:
   - **Question**: "What type of analysis would you like?"
   - **Options**:
     - "Text only (fast)" - Analyze just _chat.txt for conversation patterns
     - "Text + Documents" - Include PDFs and shared files
     - "Full analysis" - Everything including images, voice notes, video frames

3. Then ask:
   - **Question**: "What's your primary goal?"
   - **Options**:
     - "Psychological profile" - Understand personality, communication style, values
     - "Sales insights" - Buying signals, receptivity, how to pitch
     - "Relationship dynamics" - Communication patterns, power balance, history
     - "General exploration" - Open-ended Q&A about the conversation

4. Begin analysis based on selections.

## Project Structure

```
chat-analyzer/
├── index.json              # Master index linking conversations to analyses
├── data/
│   └── chats/
│       └── [person-name]/  # One folder per person/conversation
│           ├── _chat.txt   # Main conversation file
│           └── media/
│               ├── photos/
│               ├── videos/
│               ├── audio/
│               └── documents/
│   ├── media/              # Standalone media files (not from exports)
│   ├── docs/               # Additional documents
│   └── links/              # Saved webpage content
├── analysis/
│   └── profiles/
│       └── [person-name]/  # Mirrors data structure - one folder per person
│           └── *.md        # Analysis files for this person
│   └── reports/            # Cross-conversation or summary reports
├── skills/                 # Custom analysis skills
└── scripts/                # Helper scripts (ffmpeg extraction, etc.)
```

### index.json Structure
The master index links data folders to analysis folders and stores metadata:
- `id`: Folder name (e.g., "paul-stevens")
- `data_path`: Path to raw chat and media
- `analysis_path`: Path to generated analyses
- `date_range`: First and last message dates
- `stats`: Message count, media counts by type
- `analyses`: List of completed analysis files with summaries
- `tags`: For filtering across multiple conversations

**Always update index.json when adding a new conversation or analysis.**

## Data Input Guidelines

### Supported Platforms

| Platform | How to Export | Primary Chat File |
|----------|--------------|-------------------|
| **WhatsApp** | Chat → ⋮ → More → Export chat → Include media | `_chat.txt` |
| **Telegram** | Desktop app → ⋮ → Export chat history → JSON or HTML | `result.json` or `messages.html` |
| **iMessage** | Use iMazing or similar tool to export | `.txt` or `.csv` |
| **Slack** | Workspace admin → Export data | `*.json` per channel |
| **Discord** | Use DiscordChatExporter | `.json` or `.csv` |
| **Signal** | Settings → Chats → Export | `.txt` or backup file |
| **Other** | Any timestamped text log | `.txt`, `.csv`, `.json` |

### Organizing an Export
1. Create a folder: `data/chats/[person-name]/` (lowercase, hyphenated)
2. Place the chat file(s) in the root of the person folder
3. Organize media into subfolders:
   - Images → `media/photos/`
   - Videos → `media/videos/`
   - Audio/voice notes → `media/audio/`
   - Documents → `media/documents/`
4. Create matching analysis folder: `analysis/profiles/[person-name]/`
5. Add entry to `index.json`

The system auto-detects the chat format — just drop the files in and run `/analyze-chat`.

### Media Files
- Supported: Images (PNG, JPG, WEBP), Audio (MP3, M4A, OGG, OPUS), Video (MP4, MOV, WebM)
- Place in `data/media/` with descriptive names
- For transcription needs, note file paths for processing

### Documents & Links
- PDFs and docs go in `data/docs/`
- For links: save as markdown summaries in `data/links/`

## Analysis Capabilities

### Psychological Profiling
- Communication style analysis (formal/informal, emoji usage, response patterns)
- Emotional tone tracking over time
- Attachment style indicators
- Big Five personality trait estimation

### Decision-Making Patterns
- Response latency patterns (quick vs deliberate)
- Information-seeking behavior
- Risk tolerance indicators
- Authority/social proof responsiveness

### Sales Receptivity Analysis
- Product category interests (from shared links/media)
- Price sensitivity signals
- Trust-building progression
- Objection patterns and responses
- Timing preferences for engagement

## Available Skills

- `/start` - **Begin here** - Interactive guided setup with prompts
- `/process-export` - Handle large chat exports (100MB+) with mixed media
- `/analyze-chat` - Full chat analysis with profile generation
- `/profile-person` - Deep psychological profile from all available data
- `/sales-insights` - Sales-focused analysis and recommendations
- `/compare-sessions` - Compare patterns across different data sets
- `/transcribe-media` - Process audio/video for analysis

## Tool Capabilities by File Type

| File Type | Claude Can... | Method |
|-----------|---------------|--------|
| Chat text (`.txt`, `.json`, `.html`, `.csv`) | Read directly | Read tool |
| JPEG/PNG images | View and describe | Read tool (multimodal) |
| PDFs | Extract text + visuals | Read tool |
| MP3/M4A/OPUS/OGG audio | Transcribe directly | Read tool |
| MP4 video | Audio only | Extract frames first (see scripts/) |
| vCard (.vcf) | Parse text | Read tool |

### For Video Files
Run the frame extraction script first:
```bash
./scripts/extract-video-frames.sh data/chats/[export-folder]/
```
Then Claude can analyze the extracted frame images.

## Workflow Commands

### Starting a New Analysis Session
```
1. Place data in appropriate folders under data/
2. Run: /analyze-chat
3. Review generated profile in analysis/profiles/
4. Ask follow-up questions about specific patterns
```

### Multi-Agent Research Workflow
For comprehensive analysis, use this agent delegation pattern:

1. **Data Ingestion Agent** (Explore subagent)
   - Catalog all files in data/
   - Extract text from chats, transcribe media
   - Summarize documents and links

2. **Pattern Analysis Agent** (general-purpose subagent)
   - Identify communication patterns
   - Track sentiment over time
   - Map topic frequencies

3. **Profile Synthesis Agent** (general-purpose subagent)
   - Combine pattern data into profiles
   - Generate psychological assessments
   - Create decision-making models

4. **Research Agent** (general-purpose with WebSearch)
   - Research psychological frameworks
   - Find relevant sales methodologies
   - Validate profile hypotheses

## Privacy & Ethics Note

- All analysis is local; no data leaves your machine
- Profiles are probabilistic assessments, not diagnoses
- Use insights ethically and with consent awareness
- Delete sensitive data after analysis if appropriate

## Quick Start

1. Start Claude Code in this folder: `cd ~/Desktop/chat-analyzer && claude`
2. Say "let's begin" or "start analysis"
3. Claude will prompt you to:
   - Upload/locate your chat export (any platform)
   - Choose analysis depth (text only, text + docs, or full)
   - Choose your goal (profile, sales, relationships, or explore)
4. Follow the guided analysis workflow
5. Ask follow-up questions about anything you discover
