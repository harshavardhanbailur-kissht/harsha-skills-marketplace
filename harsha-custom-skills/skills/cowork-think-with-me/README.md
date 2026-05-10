# think-with-me

A Claude skill that turns Cowork into a Socratic thinking partner who resists producing artifacts until the option space is exhaustively explored.

## What It Does

When activated, Claude shifts from "build mode" to "think mode." Instead of jumping to a PRD, learning guide, or architecture doc, it first:

1. Reframes the request as a decision space
2. Identifies the axes along which options vary
3. Enumerates options exhaustively (not 3, try 10+)
4. Ranks them with forced downsides and "who would hate this"
5. Produces a **decision document** — a context-rich record that acts as a PRD for Claude itself in future sessions

The actual artifact (PRD, guide, etc.) comes last and only if requested.

## Install

### For Claude Code (CLI)
```bash
# Copy to your skills directory
cp -r cowork-think-with-me ~/.claude/skills/
```

### For Cowork (Cowork Plugin)
Place in your plugin's `skills/` directory or install via marketplace.

## Usage

### Explicit Triggers
- `/think-with-me [topic]`
- "think with me about..."
- "let's explore options for..."
- "before we build, let's think about..."
- "what are all the options for..."

### Example Session
```
You: "Where should I place the Apply Now button on the LAP web journey?"

Claude: "Before we decide placement, let's map the full decision space.
I see 6 independent axes that affect button effectiveness:
1. Location on page
2. Trigger condition
3. Visual prominence
4. Journey stage
5. User eligibility state
6. Placement relative to other CTAs

Let me enumerate options along each axis..."
```

## Folder Structure

```
cowork-think-with-me/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
├── KNOWN_GAPS.md                     # Documented limitations
├── references/
│   ├── methodology.md                # Socratic method for PM
│   ├── expert-panels.md              # 12-expert roster & selection
│   ├── decision-doc-spec.md          # Decision doc specification
│   ├── cross-questioning-protocol.md # Override handling
│   ├── anti-padding-heuristics.md    # Quality vs quantity
│   ├── axis-enumeration.md           # Morphological analysis
│   ├── yield-with-friction.md        # When user says "build now"
│   └── compaction-resilience.md      # Session recovery
├── templates/
│   ├── option-matrix.md              # Option comparison matrix
│   ├── decision-doc.md               # Decision document template
│   ├── ranking-rubric.md             # Scoring rubric
│   ├── axis-decomposition.md         # Axis identification
│   └── rejected-options-log.md       # Rejected options + overrides
├── examples/
│   ├── ai-pm-learning-guide.md       # Worked example: learning guide
│   └── lap-button-placement.md       # Worked example: button placement
└── .deep-think/                      # Build artifacts (design decisions, research)
```

## Key Concepts

**Yield-with-friction**: When you say "build it now," the skill reports coverage status once, then yields immediately. It never refuses or argues. You stay in control.

**Cross-questioning**: When you override an exploration step, the skill asks one targeted question, writes both your reasoning and the question to the record, then moves on. This creates institutional memory.

**Anti-sycophancy**: Every ranked option must have explicit downsides. No "all options have merit." At least one must be called "worst."

**Compaction resilience**: The skill writes to `.think-session/` files as it goes. If context compacts, a fresh session reads SESSION_STATE.md and resumes.

## Relationship to deep-thinker

This skill is a sibling of deep-thinker v4, not a port. Deep-thinker plans code for an executor session. think-with-me explores decisions for a human decision-maker. The terminal artifact is the decision doc, not an implementation plan.

## Author

Built for Harsha @ Kissht/Ring, May 2026.
