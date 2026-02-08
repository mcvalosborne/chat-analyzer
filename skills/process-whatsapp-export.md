# Process WhatsApp Export Skill

Handle large WhatsApp exports (100MB+) with mixed media types.

## Trigger
- `/process-export`
- "Process this WhatsApp export"
- "Analyze the full chat folder"

## WhatsApp Export Structure

Standard export contains:
```
WhatsApp Chat - [Name]/
├── _chat.txt           # Main conversation (priority 1)
├── *.jpg               # Photos shared
├── *-GIF-*.mp4         # Animated GIFs stored as MP4
├── *-VIDEO-*.mp4       # Full videos
├── *-AUDIO-*.opus      # Voice notes
├── *.pdf               # Documents shared
├── *.vcf               # Contact cards shared
└── *.webp              # Stickers
```

## File Naming Convention

WhatsApp names files with timestamps:
- `00001308-Recycled & Sustainable Footwear.pdf` → sequence 1308
- `00000508-GIF-2019-11-12-17-30-15.mp4` → sent Nov 12, 2019 at 17:30:15

This lets you correlate media with chat context.

## Processing Strategy by File Type

### 1. Text Chat (`_chat.txt`) - PRIORITY

**Tool:** Read tool directly
**Approach:**
- Read full file (858 KB is easily handled)
- Parse WhatsApp format: `[date, time] Sender: Message`
- Extract media references: `<Media omitted>` or `[filename] (file attached)`

**Analysis:**
- Message frequency and timing
- Who sends more
- Topic detection
- Sentiment over time
- Media sharing patterns (who shares what types)

### 2. Images (JPEG/PNG/WEBP)

**Tool:** Read tool (multimodal)
**Approach for large collections:**

```
Phase 1: Catalog (Explore agent)
- Count images by month/year
- Note file sizes (large = photos, small = screenshots/memes)
- Group by naming pattern

Phase 2: Sample Analysis (general-purpose agents in parallel)
- Agent 1: Analyze 10 random images from Year 1
- Agent 2: Analyze 10 random images from Year 2
- Agent 3: Analyze 10 random images from Year 3
- Each categorizes: personal photo, meme, screenshot, product, other

Phase 3: Deep Dive
- Based on sampling, identify high-value images
- Analyze product images for interest mapping
- Analyze shared screenshots for needs/interests
```

**Categories to detect:**
- Personal photos (builds relationship context)
- Memes/humor (personality indicator)
- Screenshots (often show interests, complaints, desires)
- Product images (direct buying signals)
- Location photos (lifestyle indicators)

### 3. PDFs and Documents

**Tool:** Read tool directly
**Approach:**
- List all PDFs first
- Read each - Claude extracts text and visual content
- Categorize: product brochure, article, receipt, contract, etc.

**High value for sales:** Documents shared reveal researched interests
- Example: "Recycled & Sustainable Footwear.pdf" = eco-conscious, fashion interest

### 4. Video Files (MP4)

**Tool:** Bash with ffmpeg for frame extraction
**Approach:**

```bash
# Extract single frame from each video for visual context
for f in *.mp4; do
  ffmpeg -i "$f" -vframes 1 -q:v 2 "${f%.mp4}-thumb.jpg"
done

# For videos with audio (not GIFs), extract audio
ffmpeg -i video.mp4 -vn -acodec copy audio.m4a
```

**Then:** Read extracted thumbnails with Read tool

**What to look for:**
- GIF type (meme, reaction, funny clip)
- Video content (personal, entertainment, educational)
- Shared video sources (YouTube, TikTok, etc.)

### 5. Audio Files (OPUS/M4A/MP3)

**Tool:** Read tool directly (Claude transcribes audio)
**Approach:**
- Voice notes are high-value - show emotion, tone, spontaneity
- Transcribe and note emotional indicators
- Compare voice note usage vs text patterns

### 6. Contact Cards (VCF)

**Tool:** Read tool (text format)
**Approach:**
- Parse vCard for name, phone, email
- Sharing contacts indicates relationship depth
- Context: why was this contact shared?

## Parallel Processing Architecture

For a 146 MB export with thousands of files:

```
Main Agent (orchestrator)
│
├─ Task 1: Read _chat.txt → extract timeline, media references
│
├─ Task 2 (Explore): Catalog all media files by type and date
│
├─ Task 3-6 (parallel, general-purpose):
│   ├─ Agent A: Analyze images from 2018-2019
│   ├─ Agent B: Analyze images from 2020-2021
│   ├─ Agent C: Analyze images from 2022-2023
│   └─ Agent D: Analyze images from 2024-present
│
├─ Task 7: Read all PDFs, summarize each
│
├─ Task 8: Process videos (extract frames first via Bash)
│
└─ Synthesis: Combine all agent outputs into unified profile
```

## Output: Media Analysis Report

Generate `analysis/reports/media-analysis.md`:

```markdown
# Media Analysis: [Chat Name]
Export size: [X] MB
Date range: [start] - [end]

## Media Inventory
| Type | Count | Size | Date Range |
|------|-------|------|------------|
| Photos | X | X MB | date-date |
| GIFs | X | X MB | date-date |
| Videos | X | X MB | date-date |
| Voice notes | X | X MB | date-date |
| Documents | X | X MB | date-date |

## Sharing Patterns
- **[Person A]** shares mostly: [types]
- **[Person B]** shares mostly: [types]

## Content Categories
| Category | Count | Examples | Insight |
|----------|-------|----------|---------|
| Personal photos | X | [dates] | Relationship depth |
| Memes/humor | X | [themes] | Humor style |
| Product images | X | [categories] | Buying interests |
| Screenshots | X | [types] | Needs/desires |

## High-Value Documents
1. **[filename.pdf]** - [summary, relevance to sales]
2. ...

## Voice Note Analysis
- Total: [X] voice notes
- Average length: [X] seconds
- Key transcriptions: [summaries]
- Emotional patterns: [observations]

## Interest Signals from Media
[What their media sharing reveals about interests, values, needs]

## Recommendations
[How to use media insights for profiling and sales]
```

## Practical Tips

**Start with text:** The `_chat.txt` contains 90% of the insight value. Media adds color.

**Sample before bulk:** Don't analyze 500 images individually. Sample 30-50 strategically.

**Focus on outliers:** Large files, unusual types, or files shared around key dates.

**Use chat context:** The text file tells you WHEN media was shared and often WHY.
