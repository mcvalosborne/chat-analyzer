# Profile Person Skill

Generate comprehensive psychological and behavioral profiles from all available data.

## Trigger
- `/profile-person`
- "Create a psychological profile"
- "Who is this person?"

## Prerequisites
- Run `/analyze-chat` first for baseline data
- Ensure media transcriptions are complete if applicable

## Profiling Framework

### 1. Communication Style Analysis

**Linguistic Markers:**
- Vocabulary complexity (simple vs sophisticated)
- Sentence structure (short/direct vs long/elaborate)
- Formality level and register shifts
- Emoji/emoticon usage patterns
- Punctuation habits (!!!  vs .)

**Interaction Patterns:**
- Initiator vs responder tendency
- Question-asking frequency
- Validation-seeking behavior
- Topic steering vs following
- Conflict approach (avoidant, confrontational, diplomatic)

### 2. Big Five Personality Estimation

Rate indicators for each trait:

**Openness:**
- Curiosity indicators (questions, new topics)
- Abstract vs concrete language
- Willingness to discuss hypotheticals
- Interest diversity from topics discussed

**Conscientiousness:**
- Response consistency and timing
- Follow-through on stated plans
- Organization in communication
- Detail orientation

**Extraversion:**
- Initiation frequency
- Enthusiasm markers
- Social activity mentions
- Energy in message tone

**Agreeableness:**
- Accommodation patterns
- Praise and compliment frequency
- Conflict avoidance signals
- Empathy expressions

**Neuroticism:**
- Worry/anxiety expressions
- Mood variability over time
- Reassurance-seeking
- Catastrophizing language

### 3. Attachment Style Indicators

Analyze for:
- **Secure**: Comfortable with closeness, balanced communication
- **Anxious**: Frequent checking in, reassurance needs, quick responses
- **Avoidant**: Delayed responses, topic deflection, independence emphasis
- **Disorganized**: Inconsistent patterns, push-pull dynamics

### 4. Values & Motivations

Extract from content:
- What they praise/criticize
- What they spend time discussing
- Goals and aspirations mentioned
- Fears and concerns expressed
- Heroes/influences referenced

### 5. Cognitive Style

Assess:
- Analytical vs intuitive reasoning
- Detail-focused vs big-picture
- Risk tolerance from decisions discussed
- Information processing speed (response depth vs speed)

## Output: Profile Document

Generate in `analysis/profiles/[name]-profile.md`:

```markdown
# Psychological Profile: [Name]
Generated: [date]
Data Sources: [list]

## Executive Summary
[2-3 sentence overview]

## Communication DNA
- **Style**: [descriptor]
- **Pace**: [descriptor]
- **Preferred Topics**: [list]

## Personality Snapshot
| Trait | Indicator Level | Evidence |
|-------|----------------|----------|
| Openness | High/Med/Low | [quote/pattern] |
| ... | ... | ... |

## Attachment Patterns
[analysis with examples]

## Core Values
1. [value] - [evidence]
2. ...

## Decision-Making Profile
- **Speed**: [quick/deliberate]
- **Style**: [analytical/intuitive/social]
- **Risk Tolerance**: [high/medium/low]
- **Influencers**: [authority/peers/data/emotion]

## Predicted Behaviors
- Under stress: [prediction]
- When excited: [prediction]
- In conflict: [prediction]

## Engagement Recommendations
[how to communicate effectively with this person]

## Confidence Notes
[areas of high/low confidence, data gaps]
```

## Research Agent Support

For validation, spawn research agent:
```
Task: WebSearch for psychological frameworks
- "Big Five personality communication markers"
- "Attachment style text analysis indicators"
- "[specific pattern] psychological interpretation"
```
