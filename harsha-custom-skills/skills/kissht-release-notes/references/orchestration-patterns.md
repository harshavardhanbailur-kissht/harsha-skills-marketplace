# Pipeline Orchestration Patterns

## Table of Contents
1. [State-Driven Pipeline](#state-driven-pipeline)
2. [Sub-Agent Orchestration](#sub-agent-orchestration)
3. [Checkpoint & Recovery](#checkpoint-recovery)
4. [Human Escalation Protocol](#human-escalation)
5. [Quality Scoring Framework](#quality-scoring)
6. [Multi-Pass Generation](#multi-pass)
7. [Conflict Resolution](#conflict-resolution)

---

## State-Driven Pipeline

The release notes pipeline follows a 5-phase state machine. Each phase creates checkpoints enabling resume-after-failure.

### Phase Definitions

```
ACCUMULATE → CLASSIFY → GENERATE → REVIEW → DISTRIBUTE
```

| Phase | Input | Output | Duration | Failure Mode |
|-------|-------|--------|----------|-------------|
| **Accumulate** | Jira API / CSV / Sheet | Raw ticket JSON | 2-5 min | API timeout → retry with backoff |
| **Classify** | Raw tickets | Classified tickets with categories, journeys, confidence | 3-10 min | Low confidence → human escalation |
| **Generate** | Classified tickets | 7 stakeholder guides (MD/HTML) | 5-15 min | Template error → fallback to basic format |
| **Review** | Generated guides | Verified guides (confidence-tagged) | 2-5 min | Verification fails → re-generate specific guide |
| **Distribute** | Verified guides | Slack/email/HTML deployment | 1-3 min | Channel error → retry + notify alternate channel |

### Phase Transition Rules

```python
PHASE_TRANSITIONS = {
    "accumulate": {
        "next": "classify",
        "gate": lambda state: (
            state["total_tickets"] >= 5 and
            state["duplicate_count"] == 0 and
            all(t.get("key") for t in state["tickets"])
        ),
        "on_fail": "Insufficient or malformed ticket data. Check Jira connection."
    },
    "classify": {
        "next": "generate",
        "gate": lambda state: (
            state["high_confidence_pct"] >= 0.80 and
            state["compliance_flags_set"] and
            state["unclassified_count"] <= state["total_tickets"] * 0.05
        ),
        "on_fail": "Too many low-confidence classifications. Escalate to human."
    },
    "generate": {
        "next": "review",
        "gate": lambda state: (
            all(g in state["guides"] for g in ["pm", "qa", "dev", "training", "ba", "ops", "leadership"]) and
            state["ticket_count_matches_source"]
        ),
        "on_fail": "Guide generation incomplete. Check template rendering."
    },
    "review": {
        "next": "distribute",
        "gate": lambda state: (
            state["verification_checklist_passes"] and
            state["pii_check_clean"] and
            state["hallucination_flags"] == 0
        ),
        "on_fail": "Verification failed. Re-generate flagged guides."
    },
    "distribute": {
        "next": "complete",
        "gate": lambda state: state["channels_notified"] >= 1,
        "on_fail": "Distribution failed. Save guides locally, retry channels."
    }
}
```

---

## Sub-Agent Orchestration

When generating guides for 7 stakeholders, use parallel sub-agent dispatch for speed.

### Optimal Agent Count

For release notes generation:
- **Classification**: 1 agent (sequential, needs full context)
- **Guide generation**: Up to 7 agents (one per stakeholder, independent)
- **Review**: 1-2 agents (cross-guide consistency check)

### Dispatch Pattern

```
Wave 1: Classification Agent (1 agent)
    Input: Raw tickets
    Output: Classified tickets with categories + journeys
    ↓ (wait for completion)

Wave 2: Generation Agents (up to 7 in parallel)
    Agent PM: Generate PM guide from classified tickets
    Agent QA: Generate QA guide from classified tickets
    Agent Dev: Generate Dev guide from classified tickets
    Agent Training: Generate Training guide from classified tickets
    Agent BA: Generate BA guide from classified tickets
    Agent Ops: Generate Ops guide from classified tickets
    Agent Leadership: Generate Leadership guide from classified tickets
    ↓ (wait for all to complete)

Wave 3: Review Agent (1 agent)
    Input: All 7 guides + source tickets
    Output: Verified guides with confidence tags
    ↓ (wait for completion)

Wave 4: Distribution (sequential)
    Push to channels
```

### Agent Prompt Template

Each generation agent receives this structured prompt:

```xml
<role>
You are a release notes generator for the {STAKEHOLDER} audience at Kissht.
</role>

<context>
Project: {PROJECT}
Sprint: {SPRINT}
Release Date: {DATE}
Total Tickets: {COUNT} ({BUGS} bugs, {STORIES} features)
</context>

<task>
Generate a {STAKEHOLDER} stakeholder guide from the classified ticket data below.
Use the template structure from templates/{STAKEHOLDER}-guide.md.
Apply the content rules from content-generation.md for the {STAKEHOLDER} audience.
</task>

<tickets>
{CLASSIFIED_TICKETS_JSON}
</tickets>

<output_schema>
Return the complete guide in Markdown format.
Every AI-inferred claim must carry a confidence tag: [✓] [H] [M] [L] [?]
Do not fabricate financial figures, regulatory references, or system behaviors.
</output_schema>

<success_criteria>
- All tickets from source data are accounted for
- Content passes the "Would this reader act on this?" test
- No technical jargon in Training guide
- No business metrics in Dev guide
- Compliance-flagged tickets are highlighted appropriately
</success_criteria>
```

---

## Checkpoint & Recovery

### Checkpoint Creation

At each phase transition, persist state:

```python
import json
from datetime import datetime

def create_checkpoint(phase, data, checkpoint_dir="checkpoints"):
    checkpoint = {
        "id": f"CP-{phase}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "phase": phase,
        "timestamp": datetime.now().isoformat(),
        "ticket_count": len(data.get("tickets", [])),
        "guides_generated": list(data.get("guides", {}).keys()),
        "metadata": data.get("metadata", {}),
    }

    # Save checkpoint metadata
    filepath = f"{checkpoint_dir}/{checkpoint['id']}.json"
    with open(filepath, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    # Save full state
    state_path = f"{checkpoint_dir}/{checkpoint['id']}_state.json"
    with open(state_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    return checkpoint
```

### Recovery Protocol

```
1. Read latest checkpoint from checkpoints/ directory
2. Determine which phase was last completed
3. Load state from checkpoint
4. Resume from next phase
5. If resume fails, roll back to previous checkpoint
```

---

## Human Escalation Protocol

When the pipeline encounters situations it can't resolve autonomously:

### Escalation Triggers

| Situation | Severity | Escalation |
|-----------|----------|-----------|
| Ticket classification confidence < 50% | Medium | Log for manual review, continue with best guess |
| >20% tickets unclassifiable | High | Pause pipeline, generate HUMAN_INPUT_NEEDED.md |
| Financial figure in ticket unclear | High | Tag [?], note in guide, flag for PM verification |
| Compliance trigger detected but uncertain | Critical | Always escalate — false negatives are costly |
| Contradictory tickets (same area, opposite fixes) | Medium | Include both with [?] tag, note contradiction |
| New category not in domain knowledge | Low | Classify as "General Fixes", update domain knowledge |

### Escalation Message Format

```markdown
# Release Notes Pipeline — Human Input Needed

**Pipeline Phase**: Classification
**Timestamp**: 2026-03-07T14:30:00+05:30
**Tickets Processed**: 38/45

## Issue
7 tickets could not be confidently classified (confidence < 50%).

## Tickets Needing Review
| Key | Summary | Best Guess Category | Confidence |
|-----|---------|-------------------|------------|
| LAP-2050 | Update auth dependencies | Integration [L] | 35% |
| LAP-2055 | Fix error message typo | General Fixes [L] | 40% |
| ... | ... | ... | ... |

## Options
1. Accept best-guess classifications and continue
2. Manually classify each ticket (provide mappings)
3. Create new category "Infrastructure" for LAP-2050 type

## How to Resume
Respond with your choice. Pipeline will resume from classification checkpoint.
```

---

## Quality Scoring Framework

### 5-Dimensional Quality Score (0-50 scale)

Adapted from Deep Research Synthesizer v2.5:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| **Accuracy** (0-10) | 20% | Are ticket references correct? Are claims verifiable? |
| **Completeness** (0-10) | 20% | Are all tickets accounted for? All sections populated? |
| **Relevance** (0-10) | 20% | Is content appropriate for the target stakeholder? |
| **Actionability** (0-10) | 20% | Does the reader know what to do after reading? |
| **Compliance** (0-10) | 20% | Are regulated areas properly flagged? |

**Scoring Thresholds**:
- **41-50**: Excellent — Publish as-is
- **35-40**: Good — Minor revisions needed
- **30-34**: Acceptable — PM/BA review required
- **Below 30**: Reject — Re-generate with different approach

### Per-Stakeholder Quality Checks

| Stakeholder | Must Have | Must Not Have |
|------------|-----------|--------------|
| PM | Business impact for every group, metrics where available | Code references, API details |
| QA | Test scenarios with expected results, regression scope | Business strategy, feature narrative |
| Dev | Ticket keys + links, code areas, assignees | Marketing language, user training info |
| Training | Before/After for every change, SOP checklist | Technical jargon, code references |
| BA | Journey stage mapping, integration changes | Deployment procedures, monitoring alerts |
| Ops | Deployment checklist, monitoring changes, rollback plan | Feature narrative, training materials |
| Leadership | Key numbers, top wins/risks, 1-paragraph summary | Any technical details whatsoever |

---

## Multi-Pass Generation

For highest quality output, use a multi-pass approach:

### Pass 1: Draft Generation (Speed-optimized)
- Generate all 7 guides in parallel
- Use template structure + classified ticket data
- Apply COSTAR method for each stakeholder lens
- Output: Draft guides with confidence tags

### Pass 2: Cross-Guide Consistency Check
- Verify ticket counts match across all guides
- Check that the same ticket isn't described contradictorily in different guides
- Ensure compliance flags appear in ALL relevant guides (not just one)
- Output: Consistency report + corrections

### Pass 3: Verification & Polish
- Run pre-publication checklist (9 items from SKILL.md)
- Check hallucination red flags (8 flags)
- Apply anti-slop rules (no vague language, no fabricated metrics)
- Output: Final verified guides ready for distribution

---

## Conflict Resolution

When the same ticket appears different across guides (inevitable with multi-lens generation):

### Resolution Hierarchy

1. **Ticket data is ground truth** — Summary, type, priority from Jira always win
2. **Domain knowledge resolves ambiguity** — kissht-domain.md terminology is authoritative
3. **Higher-confidence interpretation wins** — [✓] beats [H] beats [M]
4. **If unresolvable** — Include both interpretations with [?] tag, flag for human review

### Common Conflicts

| Conflict | Example | Resolution |
|----------|---------|-----------|
| Category disagreement | PM says "Feature", QA says "Fix" | Use issue_type from Jira (Bug=Fix, Story=Feature) |
| Impact assessment differs | PM says "Low impact", Ops says "High risk" | Both valid — PM measures business, Ops measures operational |
| Compliance flag disagreement | BA flags as compliance, Dev doesn't | Always escalate — compliance false negatives are costly |
| Audience attribution | Training says "All users affected", PM says "BCM only" | Use explicit audience field from classification |
