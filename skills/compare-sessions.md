# Compare Sessions Skill

Compare analysis results across different data sets or time periods.

## Trigger
- `/compare-sessions`
- "Compare these two chats"
- "How has this person changed?"

## Use Cases

### 1. Same Person, Different Time Periods
Compare how someone's patterns evolved:
- Before/after a significant event
- Seasonal variations
- Relationship progression

### 2. Different People
Compare profiles to identify:
- Similar buyer types
- Contrasting communication styles
- Segment patterns

### 3. Same Person, Different Contexts
Compare behavior across:
- Different chat groups
- Different topics
- Different relationship dynamics

## Comparison Framework

### Quantitative Metrics
| Metric | Session A | Session B | Delta |
|--------|-----------|-----------|-------|
| Message frequency | | | |
| Average response time | | | |
| Average message length | | | |
| Emoji usage rate | | | |
| Question frequency | | | |
| Initiation ratio | | | |

### Qualitative Patterns
| Dimension | Session A | Session B | Change |
|-----------|-----------|-----------|--------|
| Tone | | | |
| Engagement level | | | |
| Trust indicators | | | |
| Interest areas | | | |
| Pain points | | | |

### Profile Comparison
| Trait | Session A | Session B | Shift |
|-------|-----------|-----------|-------|
| Openness | | | |
| Conscientiousness | | | |
| Extraversion | | | |
| Agreeableness | | | |
| Neuroticism | | | |

## Workflow

### Phase 1: Session Identification
List available data sets:
```
- data/chats/[session-a]/
- data/chats/[session-b]/
- analysis/profiles/[existing-profiles]
```

### Phase 2: Parallel Analysis
If both sessions not yet analyzed, run in parallel:
```
Task Agent A: Analyze data/chats/session-a/
Task Agent B: Analyze data/chats/session-b/
```

### Phase 3: Comparison Generation
With both analyses complete:
1. Align comparable metrics
2. Calculate deltas
3. Identify significant changes
4. Generate insights

### Phase 4: Synthesis
Answer key questions:
- What changed significantly?
- What remained consistent?
- What might explain the changes?
- What predictions can we make?

## Output Format

Generate in `analysis/reports/comparison-[a]-vs-[b].md`:

```markdown
# Comparison Report
Sessions: [A] vs [B]
Generated: [date]

## Executive Summary
[Key findings in 2-3 sentences]

## Data Overview
| | Session A | Session B |
|---|-----------|-----------|
| Date Range | | |
| Message Count | | |
| Data Quality | | |

## Significant Changes

### [Change Category 1]
- **Before**: [description]
- **After**: [description]
- **Magnitude**: [high/medium/low]
- **Possible explanation**: [hypothesis]

### [Change Category 2]
...

## Stable Patterns
[What stayed consistent - often core personality]

## Metric Comparison Table
[Full quantitative comparison]

## Profile Evolution
[If same person over time]

## Implications
- For understanding: [insight]
- For engagement: [recommendation]
- For sales: [opportunity/risk]

## Confidence Notes
[Data quality caveats, comparison limitations]
```

## Starting Fresh Sessions

To analyze a new person without prior context pollution:

1. **Clear working data**:
   ```bash
   # Move old data to archive
   mv data/chats/* data/archive/[date]-[name]/
   mv data/media/* data/archive/[date]-[name]/
   ```

2. **Keep profiles for comparison**:
   - Profiles stay in `analysis/profiles/`
   - Reference them in `/compare-sessions`

3. **Load new data**:
   - Fresh chat export to `data/chats/` (any platform)
   - New media to `data/media/`

4. **Run fresh analysis**:
   - `/analyze-chat` starts clean
   - No cross-contamination of patterns

## Multi-Person Segmentation

For analyzing multiple contacts:
```
Task: Compare profiles in analysis/profiles/
- Cluster by communication style
- Identify common buyer types
- Rank by sales receptivity
- Output segmentation matrix
```
