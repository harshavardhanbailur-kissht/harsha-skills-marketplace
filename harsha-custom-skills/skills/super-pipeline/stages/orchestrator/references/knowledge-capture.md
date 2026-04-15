# Knowledge Capture Reference

Complete guide to externalizing project knowledge for AI orchestration.

## The Core Insight

Writing things down isn't just record-keeping—it's a cognitive extension that transforms how AI systems and humans collaborate across context boundaries. **Documentation should preserve the "why" alongside the "what"** because context and rationale outlast implementation details.

When Claude's context gets compacted, work moves between sessions, or different executors continue work, what survives best is structured knowledge that captures decisions, constraints, and failed approaches—not just current state.

---

## The Seven Types of Knowledge Worth Capturing

Not all project knowledge deserves documentation. Based on cognitive science showing that working memory holds only **3-4 items** (not the commonly cited 7±2), externalization should focus on knowledge that's:
- Difficult to reconstruct
- Frequently needed
- Critical for continuity

### 1. Architectural Decisions (Highest Priority)
Expensive to reconstruct—a new executor facing an unfamiliar codebase must either blindly accept past decisions or blindly change them without understanding consequences.

**ADRs solve this** by capturing the forces at play, the decision made, and the resulting consequences.

**Capture timing**: Immediately when decisions are made.

### 2. Research Findings
Distinguishing between raw notes and actionable insights:
- **Raw notes**: Temporary—quotes, observations, initial experiments
- **Actionable findings**: Evergreen, concept-oriented, atomic

**Example of good finding**: "Temperature scaling affects hallucination rate inversely"
**Example of bad note**: "Notes from June experiment"

**Capture timing**: Immediately when synthesized; let raw notes remain ephemeral.

### 3. Constraints Discovered
When a team discovers that an API rate limits at 100 requests per minute and breaks their sync approach, that's valuable knowledge that prevents future executors from repeating the same investigation.

### 4. Rejected Alternatives (Negative Knowledge)
The "Alternatives Considered" section in design docs is **one of the most important sections** at Google because it shows explicitly why rejected approaches were rejected.

### 5. Edge Cases
Should be captured inline with the code or tasks they relate to, using progressive disclosure—brief notes in context, links to details elsewhere.

### 6. Assumptions
State what is unknown or assumed, not just what was discovered. Explicit uncertainty prevents future misunderstandings.

### 7. Open Questions
Track what remains unanswered. Open questions often become the most valuable context for future work.

---

## Architecture Decision Records (ADRs)

Michael Nygard introduced ADRs in 2011 with a crucial insight: "One of the hardest things to track during the life of a project is the motivation behind certain decisions. A new person coming on to a project may be perplexed, baffled, delighted, or infuriated by some past decision."

### Why ADRs Work

The genius of ADRs is their deliberate constraints:
- **Whole document should be one or two pages long**
- Written in full sentences with active voice
- Stored with the code in version control
- Each ADR captures a single decision

### Minimal Viable ADR Format

```markdown
# ADR-[NUMBER]: [TITLE]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[Describe the forces at play—technical, political, social, project-local. 
Use value-neutral language. What situation are we in?]

## Decision
We will [decision in active voice, full sentences].

## Consequences
[All results of the decision—positive, negative, and neutral.
What becomes easier? What becomes harder?]
```

### ADR Workflow

1. Write RFC to explore options (for significant changes)
2. RFC reaches consensus
3. Write ADR documenting decision
4. ADR triggers implementation tasks
5. Code reviews reference relevant ADRs
6. Consequences of one ADR become the context for subsequent ADRs

### When ADRs are Essential
- Decisions affect structure
- Non-functional characteristics
- Dependencies
- Interfaces
- Construction techniques
- First-of-a-kind technology choices
- Decisions with cross-cutting impact

### When ADRs are Overkill
- Limited-scope decisions
- Temporary workarounds
- Simple implementation details that can change without architectural implications
- When commit messages sufficiently capture the "why"

### ADR Storage
- Store with code in version control
- Typically in `docs/decisions/` with sequential numbering
- Numbers are never reused
- Superseded ADRs remain with updated status rather than being deleted

---

## Research Documentation

The Zettelkasten and evergreen notes methodologies offer a key insight: **each note should contain exactly one idea**, no more, no less.

### The Atomicity Principle
Forces you to "get to the essence of the idea" and makes notes reusable across contexts.

Andy Matuschak's principle: "evergreen note titles are like APIs"—the title should let you know exactly what's inside without opening it.

### Notes vs. Actionable Findings

| Notes (Temporary) | Findings (Evergreen) |
|-------------------|---------------------|
| Source-oriented | Concept-oriented |
| Raw observations, quotes | Synthesized insights |
| "What was said" | "What we should do" |
| Ephemeral | Permanent |

### Conversion Process
1. Cluster by concept rather than source
2. Write atomic notes for each insight
3. Connect via links to related notes

### Research Findings Template

```markdown
# [Concept-Oriented Title]

## Insight
[One atomic insight in 1-3 sentences]

## Evidence
[What supports this insight]

## Context
[When/where this was discovered]

## Implications
[What this means for the project]

## Related
[Links to related findings or ADRs]
```

### Research Documentation Patterns
- **Concept-oriented titles**: "Circuit breaker pattern in distributed systems" not "Notes from Architecture Book"
- **Dense linking**: Every new note links to 2-3 existing notes
- **Explicit uncertainty**: State what is unknown or assumed
- **Preservation of negative findings**: "We tried X and it didn't work because Y"

### Failed Approach Template

```markdown
# Failed Approach: [Brief Description]

## What We Tried
[Specific approach or implementation]

## Why We Tried It
[Expected benefit or hypothesis]

## What Happened
[Factual outcome]

## Why It Didn't Work
[Root cause analysis]

## What We Learned
[Actionable insight]

## Alternative Chosen
[What we did instead, or link to ADR]
```

---

## Context Snippets for Handoffs

When work moves between sessions or executors, the receiving context needs enough information to continue without the full project history.

### The Context Switching Cost
Research shows that a single unplanned switch can consume **up to 20% of cognitive capacity** as developers must rebuild their mental model of:
- Code structure
- Problem context
- Planned approach

### Minimum Context for Task Continuation

Six elements (can be captured in under 500 tokens):

1. **Goal**: What success looks like in one sentence
2. **Current State**: What's complete and in progress
3. **Key Decisions Made**: Why this approach
4. **Next Steps**: Immediate actions
5. **References**: Links to code, docs, tickets
6. **Blockers**: Dependencies or waiting items

### Context Snippet Template

```markdown
# Context: [Task/Project Name]
## Updated: [Date]

### Goal
[One sentence: what we're trying to achieve]

### Current State
**Complete**:
- [Completed item 1]
- [Completed item 2]

**In Progress**:
- [Current work]

### Key Decisions
- [Decision 1 with brief rationale]
- [Decision 2 with brief rationale]

### Next Steps
1. [Immediate next action]
2. [Following action]

### References
- [Link to relevant code]
- [Link to docs/tickets]

### Blockers
- [Any dependencies or waiting items]
```

### What to Inline vs. Reference

**Rule**: If information is under 3 sentences and directly needed for understanding, include it inline; if it's shared across multiple places, changes frequently, or serves as supporting detail, reference and link.

**Agile Modeling principle**: "Record information once where it enhances your work the most."

---

## Organizing Knowledge for Retrieval

The PARA method (Projects, Areas, Resources, Archives) applies directly to software projects: **organize by actionability, not by subject**.

### PARA Categories

| Category | Definition | Example |
|----------|------------|---------|
| Projects | Short-term efforts with deadlines | Current sprint, active experiments |
| Areas | Ongoing responsibilities, no end date | Model monitoring, data quality, onboarding |
| Resources | Reference material | Papers, benchmarks, external tools, patterns |
| Archives | Inactive items | Completed experiments, deprecated approaches |

### Recommended Project Structure

```
/projects/           # Current sprint or active experiments
/areas/              # Ongoing responsibilities
/resources/          # Reference material
/archives/           # Completed/deprecated
```

### Hub Notes
Serve as entry points to navigate complex topics—like an index that emerges organically.

Create hub notes for:
- Onboarding paths
- System architecture overview
- Common debugging scenarios

These make knowledge findable through multiple access paths: search, browse, cross-reference, and hub navigation.

---

## Knowledge Capture Triggers

Knowledge capture fails when it's treated as a separate activity from development. The docs-as-code philosophy: "Documentation will never be a part of engineering culture until it is integrated into the codebase and engineering workflow."

### Implementation
- Store docs in Git alongside code
- Use the same review process for docs as code
- Include documentation in the definition of done

### Specific Triggers

| Trigger | Action | Timing |
|---------|--------|--------|
| New architectural decision | Create ADR | Same day |
| Failed approach discovered | Document in failure log | Immediately |
| Major feature complete | Update architecture overview | At completion |
| Process change | Update relevant workflow doc | When change is made |
| Constraint discovered | Add to constraints section | Immediately |
| API/integration limitation found | Document in integration notes | Immediately |

### The "Update When It Hurts" Principle
Documents don't need to be perfectly current, but should be updated when the gap between documentation and reality is causing actual problems.

### For AI-Orchestrated Workflows
- Lead agent should trigger doc reviews when related code changes
- Flag documents accessed frequently but not updated
- Update task findings back to the knowledge base
- Capture significant decisions during planning
- Capture research findings and constraints during execution

---

## Documentation Anti-Patterns

### The Documentation Graveyard
Creates docs nobody reads or maintains.
**Fix**: Regular audits and archiving unused content.

### Copy-Paste Documentation
Duplicates information across multiple places that quickly desync.
**Fix**: Maintain a single source of truth with links.

### The PhD Thesis
Exhaustive detail that overwhelms readers.
**Fix**: Focus on "just enough" and link to details.

### The Missing 'Why'
Documents what and how but never the rationale behind decisions.
**Fix**: Every decision document should answer why this approach was chosen and what alternatives were rejected.

### Orphan Documents
No clear owner; inevitably becomes stale.
**Fix**: Every document needs an explicit owner accountable for accuracy.

### Tool Fragmentation
Docs scattered across Notion, Confluence, Google Docs, and wikis.
**Fix**: Consolidate to a single platform.

### Premature Documentation
Captures speculative requirements before they're stable.
**Fix**: Wait until decisions are made before documenting.

### Documentation That Fights Cognitive Architecture
Working memory holds 3-4 items; each documentation unit should require processing no more than that simultaneously.
**Fix**: Design for progressive disclosure, visual hierarchy, and chunking.

---

## Integration with Task Prompts

Knowledge docs connect to task prompts through a layered information architecture:

### Four Levels

| Level | Content | Example |
|-------|---------|---------|
| **Level 1: Task Context** | In the task itself | Specific goal, current state, success criteria, links |
| **Level 2: Project Knowledge** | ADRs, project-specific patterns | Failed approaches, setup guides |
| **Level 3: Domain Knowledge** | Cross-project patterns | Technology rationale, best practices |
| **Level 4: Organizational Standards** | Policies, coding standards | Universal patterns |

### Linking Pattern
- Tasks link TO knowledge docs for context
- Knowledge docs link TO related tasks for examples and history
- This bidirectional linking creates a network where context can be assembled based on task type

### For AI Executors
Context assembly should:
- Pull relevant ADRs based on components being modified
- Include recent failed approaches in the same area
- Provide just enough background to understand constraints
- Avoid overwhelming the context window
- Follow the 500-token guideline for task context

---

## Maintenance Strategy

Documentation becomes debt when it's treated as a one-time project rather than a living system.

### Maintenance Approaches

| Strategy | Implementation |
|----------|----------------|
| Keep docs close to code | Same repo, same review process |
| Assign clear ownership | Every doc has an explicit owner |
| Schedule review cycles | Monthly for high-change, quarterly for moderate, annually for stable |
| Automate where possible | Generate API docs from code, CI alerts when code changes but docs don't |

### Agile Modeling Principle
Create "just enough" documentation to facilitate communication, knowledge transfer, and development, without overburdening the team. Less documentation means easier maintenance.

### Minimum Viable Documentation Set

For most AI-orchestrated projects:
1. Project README
2. Architecture Overview
3. Decision Log (ADRs)
4. Failure Log
5. Task Context Template
6. Key Workflows

### Version Control for Documentation
- ADRs are immutable—supersede, don't delete
- Track changes with who/when/what
- Maintain audit trail for decision archaeology
- Use status labels: Draft, Current, Potentially Stale, Deprecated

---

## Key Insights

### Writing Clarifies Thinking
The act of documenting improves understanding. When an AI executor is confused about an approach, asking it to document its current understanding often resolves the confusion.

### The Extended Mind Thesis
Documentation should be designed for tight integration into workflows, not as separate reference material. The best documentation participates actively in cognitive processes—it's "in the loop" rather than passively stored.

### Context-Dependent Memory
Retrieval is most effective when cues at retrieval match cues at encoding. Documentation should include rich contextual information ("when to use this," "what problem this solves") and use consistent terminology.

### The Expertise Reversal Effect
What helps novices can hinder experts. Documentation should provide different paths for different expertise levels—progressive disclosure from overview to detail.

### Surprise is the Signal
As Matuschak notes, "If reading and writing notes doesn't lead to surprises, what's the point?" Dense linking between notes should surface unexpected connections. If your documentation system never reveals something you didn't expect, it's not providing the value it should.

### The Fundamental Purpose
Externalize knowledge to **extend cognitive capacity beyond working memory limits**. By offloading information to stable external media, limited working memory is freed for processing, reasoning, and new input.

This is why documentation isn't optional for complex AI-orchestrated projects—it's a cognitive necessity that makes otherwise intractable coordination problems tractable.
