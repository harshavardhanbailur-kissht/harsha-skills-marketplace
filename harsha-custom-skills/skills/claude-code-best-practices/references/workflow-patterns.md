# Workflow Patterns

Proven development methodologies for Claude Code, from simple to advanced.

## Table of Contents
1. Plan-Then-Execute (Official)
2. RPI Workflow (Research-Plan-Implement)
3. Boris Cherny's Production Setup
4. HumanLayer ACE (Advanced Context Engineering)
5. Ralph Wiggum Autonomous Loop
6. CI/CD Integration
7. Choosing a Workflow
8. Source Registry

---

## 1. Plan-Then-Execute (Official)

The simplest and most universal workflow. Start here.

**Steps:**
1. Ask Claude to create a detailed implementation plan (use "think hard" phrasing)
2. Instruct it to pause before writing code
3. Review, question assumptions, and refine the plan
4. Give green light to implement

**Benefits:**
- Halves token consumption for analysis work
- Catches architectural mistakes before code is written
- Creates documentation as a side effect

**Commands:**
```bash
claude --permission-mode plan    # Start in plan mode
```

Or mid-session: `/plan`

**When to use:** Every complex task. Even 30 seconds of planning saves 10 minutes of debugging.

---

## 2. RPI Workflow (Research-Plan-Implement)

Systematic workflow with validation gates between phases. From the community reference repo.

### Directory Structure

```
rpi/{feature-slug}/
├── REQUEST.md             # Initial feature description
├── research/
│   └── RESEARCH.md        # GO/NO-GO analysis
├── plan/
│   ├── PLAN.md
│   ├── product-requirements.md
│   ├── ux-design.md
│   └── technical-specification.md
└── implement/
    └── IMPLEMENT.md       # Implementation record
```

### Phase Gates

1. **Research Phase:** Claude analyzes feasibility, existing patterns, dependencies. Output: GO/NO-GO recommendation with evidence.

2. **Plan Phase:** Detailed plan including product requirements, UX design, and technical spec. Review gate: human approval before implementation.

3. **Implement Phase:** Execute the plan. Record decisions, deviations, and results.

**Benefits:**
- Prevents scope creep through clear phase boundaries
- Creates comprehensive documentation automatically
- Enables clear review gates for team collaboration
- Prevents wasted effort on non-viable features

---

## 3. Boris Cherny's Production Setup

Creator of Claude Code shares his production workflow.

### Key Practices

1. **Parallel sessions:** 10-15 concurrent Claude Code sessions (5 terminal, 5-10 browser)
2. **Plan Mode first:** Iterate until plan is solid, then switch to auto-accept edits
3. **CLAUDE.md as living KB:** Team maintains in git, documenting mistakes and learnings
4. **Wildcard permissions:** Pre-allow safe commands via `/permissions`
5. **Slash commands for daily workflows:** Commits, PRs, simplification, verification
6. **Verification is #1:** "Giving Claude a way to verify its work creates 2-3x quality improvement"

### Daily Workflow

```
Morning:
1. `claude update` (check changelog)
2. Open sessions for each task
3. Start each in plan mode
4. Review plans, then switch to implementation

Implementation:
1. Auto-accept edits mode for trusted work
2. Commit after each completed task
3. Different model for review (Opus reviews Sonnet's code)
4. `/compact` at ~50% context

End of day:
1. Commit all work
2. Update CLAUDE.md with new learnings
3. `/rename` important sessions for future `/resume`
```

---

## 4. HumanLayer ACE (Advanced Context Engineering)

Advanced methodology proven on 300K LOC Rust codebases.

### Core Philosophy

"Instead of reviewing 2,000 lines of code, review 200 lines of specification + 200 lines of plan."

### Frequent Intentional Compaction (FIC)

Structure context feeding throughout development:

1. **Research phase:** Load relevant files, analyze patterns
2. **Plan phase:** Compact research into concise plan
3. **Implement phase:** Work from plan, not raw research
4. **Validate phase:** Verify against original requirements

Target 40-60% context window utilization for optimal reasoning quality.

### Key Principles

- Progressive information disclosure (give Claude what it needs, when it needs it)
- Ephemeral Tasks + persistent specifications (best of both worlds)
- Structured context recovery after compaction
- Specifications as the source of truth (not conversation history)

### Results

- Ship a week's worth of work in a day while maintaining code quality
- Reduced debugging time by 60-70%
- Consistent quality across long sessions

---

## 5. Ralph Wiggum Autonomous Loop

Official Anthropic plugin for hours-long autonomous development.

### How It Works

1. Claude attempts the task
2. Stop hook intercepts exit
3. Re-feeds original prompt with git history of changes
4. Claude reviews its own work, notices issues, fixes them
5. Repeat until success criteria met or iteration limit reached

### Configuration

Enable via plugin or Stop hook:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/ralph-loop.sh"
          }
        ]
      }
    ]
  }
}
```

### When to Use

- Success is objective and verifiable (tests pass, type checks succeed)
- Task is well-defined with clear completion criteria
- You're willing to spend the tokens ($50-100+ for 50 iterations on large codebases)

### When NOT to Use

- Subjective quality (design, UX, writing style)
- Open-ended exploration
- Tasks requiring human judgment at each step

---

## 6. CI/CD Integration

### GitHub Actions (Official)

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Review this PR for code quality, security, and test coverage"
```

Capabilities:
- Automated PR reviews posted as comments
- Unit test generation for changed files
- Test suite running with coverage reporting
- 60%+ of teams using Claude Code in CI use GitHub Actions

### GitLab CI/CD

```yaml
claude-review:
  stage: review
  script:
    - claude -p "Review the changes in this MR" --output-format json
```

### Headless Mode (Any CI)

```bash
# Non-interactive execution for scripting
claude -p "Run tests and report coverage" --max-turns 10 --max-budget-usd 5.00
```

### Dual-Layer Strategy (Cost-Effective)

1. **PR screening (~$8/month):** Quick review on every PR via GitHub Action
2. **Weekly deep audit (~$3/month):** Comprehensive security/quality scan via scheduled job

---

## 7. Choosing a Workflow

| Situation | Recommended Workflow |
|---|---|
| Quick fix or small feature | Plan-Then-Execute |
| New feature (medium complexity) | RPI |
| Large refactoring | HumanLayer ACE |
| Test-driven development | Plan-Then-Execute + TDD |
| Autonomous task (tests exist) | Ralph Wiggum |
| Legacy codebase work | RPI with extended Research phase |
| Team project | Boris Cherny's setup + CI/CD |
| Learning a new codebase | Plan mode with `/context` monitoring |

---

## 8. Source Registry

| Source | Type | URL |
|---|---|---|
| Official Best Practices | Anthropic docs | code.claude.com/docs/en/best-practices |
| Community Reference Repo | GitHub | github.com/shanraisshan/claude-code-best-practice |
| Boris Cherny Workflow | Interview | karozieminski.substack.com |
| HumanLayer ACE | GitHub | github.com/humanlayer/advanced-context-engineering |
| Ralph Wiggum | Plugin | github.com/anthropics/claude-code (plugins) |
| SFEIR Advanced Practices | Blog | institute.sfeir.com/en/claude-code |
| Steve Kinney Course | Tutorial | stevekinney.com/courses/ai-development |
| Agent Skills Standard | Spec | agentskills.io/specification |
