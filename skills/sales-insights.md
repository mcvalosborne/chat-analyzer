# Sales Insights Skill

Analyze chat data for sales receptivity, buying signals, and personalized selling strategies.

## Trigger
- `/sales-insights`
- "How can I sell to this person?"
- "What would they buy?"

## Prerequisites
- Run `/analyze-chat` and `/profile-person` first
- Review existing profiles in `analysis/profiles/`

## Analysis Framework

### 1. Interest Mapping

Extract from chat history:
- **Products mentioned**: Items discussed, shared, or linked
- **Services referenced**: Apps, subscriptions, experiences
- **Aspirational content**: What they admire, want, plan
- **Problems expressed**: Frustrations, unmet needs, complaints
- **Questions asked**: Information-seeking reveals interests

### 2. Buying Signal Detection

**Strong Signals:**
- Price inquiries ("How much is...?")
- Comparison shopping mentions
- "I need" or "I want" statements
- Research behavior (sharing reviews, asking opinions)
- Timeline mentions ("By next month I want to...")

**Moderate Signals:**
- Sharing product links
- Discussing others' purchases
- Quality/feature discussions
- Budget mentions

**Weak Signals:**
- General interest expressions
- Window shopping behavior
- "Someday" language

### 3. Receptivity Profile

**Trust Builders for This Person:**
- What validation do they seek? (social proof, expert opinion, data)
- How do they evaluate recommendations?
- What sources do they trust?
- How long is their consideration cycle?

**Resistance Patterns:**
- Common objections raised
- What makes them skeptical?
- Price sensitivity indicators
- Risk aversion level

### 4. Persuasion Style Match

Based on profile, determine optimal approach:

| Profile Type | Approach | Avoid |
|--------------|----------|-------|
| Analytical | Data, comparisons, ROI | Pressure, emotion |
| Driver | Results, efficiency, bottom line | Details, small talk |
| Expressive | Stories, vision, relationships | Dry facts, rigidity |
| Amiable | Consensus, safety, support | Confrontation, risk |

### 5. Timing Analysis

Identify:
- Best times for engagement (when most responsive)
- Buying cycle patterns (payday effects, seasonal)
- Decision-making speed
- Follow-up tolerance

## Output: Sales Strategy Document

Generate in `analysis/reports/[name]-sales-strategy.md`:

```markdown
# Sales Strategy: [Name]
Generated: [date]
Based on: [data sources]

## Quick Profile
- **Buyer Type**: [analytical/driver/expressive/amiable]
- **Decision Speed**: [fast/moderate/slow]
- **Primary Motivator**: [value/status/security/convenience]
- **Price Sensitivity**: [high/medium/low]

## Interest Categories
Ranked by signal strength:

1. **[Category]** - [confidence: high/med/low]
   - Evidence: [quotes/patterns]
   - Product opportunities: [specific suggestions]

2. ...

## Buying Signals Detected
| Signal | Date | Context | Strength |
|--------|------|---------|----------|
| [signal] | [date] | [context] | Strong/Mod/Weak |

## Trust Building Strategy
1. [specific tactic based on their patterns]
2. [specific tactic]
3. [specific tactic]

## Objection Handling Prep
| Likely Objection | Evidence | Response Strategy |
|------------------|----------|-------------------|
| [objection] | [why expected] | [how to address] |

## Engagement Playbook
- **Best contact times**: [times/days]
- **Optimal message length**: [short/medium/long]
- **Tone to use**: [formal/casual/enthusiastic]
- **Proof types needed**: [testimonials/data/demos]

## Product Recommendations
Based on expressed interests and inferred needs:

1. **[Product/Service]**
   - Why it fits: [reasoning]
   - How to position: [angle]
   - Potential objections: [list]

## Conversation Starters
[3-5 natural segues based on their interests]

## Red Flags to Avoid
[approaches that would backfire with this person]
```

## Research Agent Tasks

For market context, spawn agents:
```
Task: Research product categories
- "[interest category] trending products 2024"
- "[demographic] buying behavior [product type]"
- "Sales techniques for [buyer type] personality"
```
