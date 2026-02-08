# Recommended Workflow

## Quick Start (Single Person Analysis)

```
1. Export WhatsApp chat → Save to data/chats/[name]/
2. cd ~/Desktop/chat-analyzer
3. claude (start Claude Code session)
4. /analyze-chat
5. /profile-person
6. /sales-insights
7. Ask follow-up questions
```

## Multi-Agent Architecture

### Main Agent (You interact with this)
- Orchestrates analysis
- Synthesizes results from sub-agents
- Answers your questions
- Generates final reports

### Sub-Agent Types & When to Use

| Agent | Subagent Type | Use For |
|-------|---------------|---------|
| Explorer | `Explore` | Finding files, cataloging data, understanding structure |
| Analyzer | `general-purpose` | Processing chat data, pattern detection |
| Researcher | `general-purpose` | Web searches for frameworks, validation |
| Planner | `Plan` | Designing complex multi-step analyses |

### Parallel Processing Pattern

For large datasets, run agents in parallel:

```
User: Analyze this 10,000 message chat history

Claude orchestrates:
├── Agent 1: Analyze messages Jan-Mar
├── Agent 2: Analyze messages Apr-Jun
├── Agent 3: Analyze messages Jul-Sep
└── Agent 4: Analyze messages Oct-Dec

Then synthesizes all results into unified profile
```

### Research Enhancement Pattern

For deeper insights:

```
User: Create a sales strategy for this person

Claude orchestrates:
├── Agent 1: Analyze their expressed interests
├── Agent 2: WebSearch for "selling to [personality type]"
├── Agent 3: WebSearch for "[interest category] trending products"
└── Agent 4: Research objection handling techniques

Then combines into personalized strategy
```

## Session Management

### Starting Fresh (New Person)

```bash
# Archive current data
mkdir -p data/archive/$(date +%Y%m%d)-current
mv data/chats/* data/archive/$(date +%Y%m%d)-current/
mv data/media/* data/archive/$(date +%Y%m%d)-current/

# Start new Claude session
claude

# Load new data and analyze
```

### Comparing People

```
1. Ensure both profiles exist in analysis/profiles/
2. /compare-sessions
3. Select profiles to compare
```

## Example Prompts

### Initial Analysis
- "Analyze all chat data in the data folder"
- "Create a comprehensive profile of this person"
- "What are their main interests and pain points?"

### Sales Focus
- "What products would this person be interested in?"
- "How should I pitch [specific product] to them?"
- "What objections might they raise about [topic]?"
- "When is the best time to reach out?"

### Deep Dive
- "How has their communication style changed over time?"
- "What triggers positive responses from them?"
- "What topics should I avoid?"
- "How do they make decisions?"

### Research Enhancement
- "Research effective sales techniques for their personality type"
- "Find trending products in [their interest area]"
- "What psychological frameworks explain their behavior?"

## Data Privacy Best Practices

1. **Don't sync to cloud**: Keep folder local or use encrypted storage
2. **Delete after analysis**: Remove raw chat exports when done
3. **Anonymize profiles**: Replace names with codes for sensitive analysis
4. **Review before sharing**: Profiles contain inferred personal data
