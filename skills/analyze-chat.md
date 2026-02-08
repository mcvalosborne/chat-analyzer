# Analyze Chat Skill

Comprehensive analysis of chat exports with pattern detection and initial profiling.

## Trigger
- `/analyze-chat`
- "Analyze this chat"
- "What patterns do you see?"

## Workflow

### Phase 1: Data Discovery
Use Explore agent to catalog available data:
```
Task: Explore data/ directory
- List all chat files with dates and sizes
- Identify media files and types
- Note any documents or link files
- Report total message count estimates
```

### Phase 2: Content Extraction
Read and process chat content:
1. Parse WhatsApp export format (timestamps, sender, message)
2. Separate messages by participant
3. Extract:
   - Text messages
   - Media references (photos, voice notes, videos)
   - Links shared
   - Deleted message markers
   - Reply references

### Phase 3: Quantitative Analysis
Calculate metrics:
- **Volume**: Messages per day/week, total by person
- **Timing**: Active hours, response latency averages
- **Length**: Average message length, longest messages
- **Media**: Photo/video/voice note ratios
- **Engagement**: Question frequency, reply rates

### Phase 4: Qualitative Analysis
Identify patterns:
- **Topics**: Main subjects discussed, recurring themes
- **Tone**: Emotional valence over time
- **Dynamics**: Who initiates, who responds, power balance
- **Interests**: Products, services, activities mentioned
- **Pain Points**: Complaints, frustrations, needs expressed

### Phase 5: Initial Profile Generation
Create preliminary profile in `analysis/profiles/`:
- Communication style summary
- Key interests and values
- Relationship dynamics
- Notable patterns and anomalies

## Output Format

```markdown
# Chat Analysis: [Person Name]
Date Range: [start] - [end]
Total Messages: [count]

## Communication Patterns
[findings]

## Topic Map
[categorized topics with frequency]

## Emotional Timeline
[sentiment trends]

## Key Insights
[bulleted findings]

## Questions for Deeper Analysis
[suggested follow-ups]
```

## Agent Delegation

For large chat histories (>1000 messages), delegate:
```
Task subagent (general-purpose):
"Analyze messages from [date range] for:
1. Topic categorization
2. Sentiment scoring
3. Interest extraction
Report findings in structured format."
```

Run multiple date-range agents in parallel, then synthesize.
