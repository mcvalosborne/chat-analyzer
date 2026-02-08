# Start Analysis Skill

Interactive startup workflow for new analysis sessions.

## Trigger
- `/start`
- "Let's begin"
- "Start analysis"
- "Analyze a chat"
- Session start in this project folder

## Workflow

### Step 1: Locate Data

Check `data/chats/` for existing exports:
```bash
ls -la data/chats/
```

**If empty**, prompt:
> "I don't see any data in `data/chats/` yet. Please either:
> 1. Unzip your WhatsApp export there and tell me the folder name, or
> 2. Drag the .zip file into this chat and I'll help extract it"

**If data exists**, confirm:
> "I found [folder name]. Is this the chat you want to analyze?"

### Step 2: Choose Analysis Depth

Use AskUserQuestion tool:

```json
{
  "questions": [{
    "question": "What type of analysis would you like to run?",
    "header": "Depth",
    "options": [
      {
        "label": "Text only (Recommended)",
        "description": "Fast analysis of conversation patterns from _chat.txt. Best for initial insights."
      },
      {
        "label": "Text + Documents",
        "description": "Include PDFs and shared files. Reveals researched interests."
      },
      {
        "label": "Full analysis",
        "description": "Everything: images, voice notes, video frames. Most comprehensive but slower."
      }
    ],
    "multiSelect": false
  }]
}
```

### Step 3: Choose Primary Goal

Use AskUserQuestion tool:

```json
{
  "questions": [{
    "question": "What's your primary goal for this analysis?",
    "header": "Goal",
    "options": [
      {
        "label": "Psychological profile",
        "description": "Personality traits, communication style, values, decision-making patterns"
      },
      {
        "label": "Sales insights",
        "description": "Buying signals, product interests, receptivity, objection patterns"
      },
      {
        "label": "Relationship dynamics",
        "description": "Power balance, communication health, conflict patterns, attachment style"
      },
      {
        "label": "General exploration",
        "description": "Open-ended Q&A - I'll summarize and you ask what interests you"
      }
    ],
    "multiSelect": false
  }]
}
```

### Step 4: Confirm and Begin

Summarize selections:
> "Got it. I'll run a **[depth]** analysis focused on **[goal]**.
>
> Starting with `_chat.txt` to understand the conversation..."

Then execute based on selections:

| Depth | Goal | Skill Sequence |
|-------|------|----------------|
| Text only | Profile | `/analyze-chat` → `/profile-person` |
| Text only | Sales | `/analyze-chat` → `/sales-insights` |
| Text only | Relationship | `/analyze-chat` → focus on dynamics |
| Text only | Explore | `/analyze-chat` → open Q&A |
| Text + Docs | Any | Add PDF reading before profile/sales |
| Full | Any | `/process-export` → then goal-specific |

### Step 5: Offer Next Steps

After initial analysis, prompt:
> "Initial analysis complete. Would you like to:
> - Ask specific questions about what I found
> - Go deeper on [specific area]
> - Generate a formal report
> - Analyze the media files next"

## For Returning Sessions

If `analysis/profiles/` already contains profiles:
> "I see you have existing analysis for [names]. Would you like to:
> - Continue with that analysis
> - Start fresh with new data
> - Compare with a new export"
