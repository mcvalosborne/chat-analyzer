# Transcribe Media Skill

Process audio and video files for text analysis integration.

## Trigger
- `/transcribe-media`
- "Transcribe the voice notes"
- "Process the media files"

## Supported Formats

| Type | Formats | Notes |
|------|---------|-------|
| Audio | MP3, M4A, WAV, OGG | Voice notes, audio messages |
| Video | MP4, MOV, WebM | Extract audio track for transcription |
| Images | PNG, JPG, HEIC | OCR for text, description for context |

## Workflow

### Phase 1: Media Inventory

Scan `data/media/` and catalog:
```
- File name
- Type (audio/video/image)
- Size
- Duration (for audio/video)
- Associated chat context (if from WhatsApp export)
```

### Phase 2: Processing Strategy

**For Audio/Video:**
Claude Code can directly process audio files. For each file:
1. Read the audio file directly
2. Generate transcription
3. Note speaker identification if possible
4. Capture tone/emotion indicators

**For Images:**
1. Read image file directly (Claude is multimodal)
2. Describe visual content
3. Extract any text (OCR)
4. Note emotional content (facial expressions, etc.)

### Phase 3: Context Integration

For WhatsApp exports, media files are named with timestamps:
- `IMG-20240115-WA0001.jpg`
- `PTT-20240115-WA0001.opus` (voice notes)
- `VID-20240115-WA0001.mp4`

Match these to chat timestamps to understand context:
- What was discussed before/after the media?
- Who sent it?
- What was the response?

### Phase 4: Output Generation

Create `analysis/media-transcripts.md`:

```markdown
# Media Transcriptions
Generated: [date]
Source: [folder]

## Audio Files

### [filename]
- **Sent by**: [if known]
- **Date**: [extracted from filename]
- **Duration**: [length]
- **Transcription**:
> [transcribed text]

- **Tone notes**: [observations about emotion, emphasis]
- **Chat context**: [what was said before/after]

---

## Video Files

### [filename]
- **Duration**: [length]
- **Audio transcription**:
> [transcribed text]

- **Visual notes**: [relevant visual content description]

---

## Images

### [filename]
- **Description**: [what the image shows]
- **Text content**: [any text visible in image]
- **Emotional content**: [if applicable]
- **Context**: [why it was shared, what it relates to]
```

## Integration with Analysis

After transcription, update analysis:
1. Add voice note content to communication style analysis
2. Include image sharing patterns in interest mapping
3. Note tone differences between text and voice
4. Flag significant media for profile updates

## Agent Delegation

For large media collections:
```
Task subagent (general-purpose):
"Process media files in data/media/[subset]:
1. Transcribe audio content
2. Describe images
3. Output structured summary
Focus on: [specific analysis goal]"
```

Run in parallel for different file batches.

## Privacy Note

- Media processing is local
- Transcriptions stay in project folder
- Consider deleting source media after analysis if sensitive
