---
name: interactive-learning-guide-builder
description: "Build self-contained interactive HTML learning web apps from research files, knowledge bases, or a user-specified topic. Produces a working HTML/React app with sidebar modules, topologically-ordered lessons, MCQs that explain BOTH correct and wrong answers, progressive hints, checkpoint quizzes, notes sandbox, retest mode, and dark/mobile-responsive UI. Boot.dev-inspired pedagogy (text-first, structured progression, interactive assessment) with logical learning paths over gamification. Use when the user wants to CONVERT existing research/documents into a teachable interactive course, or BUILD a new course from scratch. Triggers: 'interactive course', 'learning guide', 'training module', 'MCQ generator', 'quiz app', 'turn this research into a course'. Do NOT use for: static documentation (use codebase-handoff-documenter), slide decks, or non-interactive PDFs."
---

# Interactive Learning Guide Builder

**Status**: v1.0 — Prototype-first approach  
**Last Updated**: 2026-04-10  
**Author**: Harshavardhan Bailur  

## Executive Summary

This skill transforms research files, knowledge bases, or any topic into a structured, interactive learning guide delivered as an HTML web application. Inspired by Boot.dev's pedagogical design (text-first, structured progression, interactive assessment) but focused on **learning quality over gamification** — logical structure, quality MCQs, hints, tips, and the ability to revisit and reinforce prior knowledge.

## When to Use This Skill

- User wants to create an interactive course or learning guide
- User has research files or knowledge bases to convert into teaching material
- User wants to build onboarding/training content for a team
- User mentions "learning path", "MCQ", "quiz", "course", "interactive tutorial"
- User wants to convert documents/research into structured, teachable format

## Core Pipeline (5 Phases)

### Phase 1: Content Ingestion & Analysis
**Goal**: Understand ALL source material and identify what knowledge exists.

1. **Locate source files**: Read the directory/files the user points to
2. **Catalog content**: For each file, extract:
   - Topic/subject covered
   - Key concepts and terminology
   - Relationships to other topics (prerequisites, builds-on)
   - Content richness (is this a deep-dive or overview?)
3. **Identify gaps**: What foundational knowledge is assumed but not explained?
4. **Output**: Content catalog with dependency map

→ Read `references/content-analysis-patterns.md` for ingestion strategies

### Phase 2: Learning Path Auto-Structure
**Goal**: Create a logical, progressive learning sequence.

**Structuring Algorithm**:
1. **Extract all concepts** from ingested content
2. **Build dependency graph**: Concept A requires understanding Concept B first
3. **Topological sort**: Order concepts so prerequisites always come before dependents
4. **Group into modules**: Cluster related concepts (5-8 lessons per module)
5. **Sequence modules**: Foundational → Applied → Advanced → Synthesis
6. **Add reinforcement points**: Every 3rd lesson, include a "checkpoint" that tests prior modules

**Module Structure Template**:
```
Module N: [Title]
├── Lesson N.1: [Foundation concept]
├── Lesson N.2: [Building concept]
├── Lesson N.3: [Applied concept]
├── Checkpoint: [Reinforcement MCQs from Modules 1 to N]
├── Lesson N.4: [Advanced concept]
└── Lesson N.5: [Synthesis/Practice]
```

**Principles**:
- NO random topic ordering — every lesson logically follows the previous
- Start with "What is X?" before "How does X work?" before "When should you use X?"
- Concrete examples before abstract principles
- Real-world scenarios over theoretical definitions

### Phase 3: Content Generation & MCQ Creation
**Goal**: Generate lesson content and high-quality assessments.

**For each lesson, generate**:

1. **Lesson Content** (from source material + web research for gaps):
   - Clear explanation in plain language
   - Key terms with definitions (highlighted)
   - Real-world examples or scenarios
   - "Did you know?" tips and tricks between sections
   - Step-by-step walkthroughs for processes

2. **MCQs** (3-5 per lesson, varying difficulty):
   - **Basic**: Direct recall ("What does LAP stand for?")
   - **Intermediate**: Application ("Given this scenario, which stage comes next?")
   - **Advanced**: Analysis ("Why would a Saral application be rejected at this point?")
   
   Each MCQ MUST include:
   - The question
   - 4 options (1 correct, 3 plausible distractors)
   - Explanation for the correct answer
   - Explanation for EACH wrong answer (why it's wrong — this is where learning happens)
   - Difficulty tag
   - References to prior lessons it builds on

3. **Cross-Module MCQs** (compound questions):
   - "Based on what you learned in Module 2 about LeadGen AND Module 4 about Credit Processing, which scenario is correct?"
   - These appear at checkpoints and at the end of the course

4. **Hints** (per lesson):
   - "If stuck on this concept, revisit Lesson X.Y"
   - "Think about it this way: [analogy]"
   - Progressive hints: Hint 1 (subtle nudge) → Hint 2 (bigger clue) → Hint 3 (near-answer)

5. **Tips & Tricks** (interspersed):
   - Practical tips a real practitioner would share
   - Common mistakes to avoid
   - Shortcuts and pro tips

→ Read `references/mcq-generation-patterns.md` for MCQ best practices
→ Read `references/boot-dev-pedagogy.md` for Boot.dev-inspired patterns

### Phase 4: Interactive Web App Generation
**Goal**: Build the HTML/React web app that delivers the learning experience.

**Core Features**:
- **Sidebar navigation**: Module → Lesson tree with completion indicators
- **Progress bar**: Overall course completion percentage
- **Lesson view**: Clean reading area with formatted content
- **MCQ interaction**: Click answer → immediate feedback (correct/wrong with explanation)
- **Expandable hints**: "Need a hint?" → progressive reveal
- **Show answer**: Full explanation reveal (tracks that you used it)
- **Tips callout boxes**: Styled differently from lesson text
- **Notes sandbox**: Textarea per lesson for personal notes
- **Jump navigation**: Go to any lesson (not locked — learning should be free)
- **Retest mode**: Retake MCQs for any module with shuffled questions
- **Knowledge reinforcement**: Checkpoint MCQs pull from ALL prior modules
- **Keyboard shortcuts**: Arrow keys for prev/next, Enter to submit answer

**UI Design Principles**:
- Clean, professional — not toy-looking
- Dark mode support
- Mobile responsive
- Readable typography (16px+ body, good line height)
- Color-coded feedback (green correct, red wrong, blue hint, yellow tip)

→ Read `templates/webapp-template-spec.md` for the HTML/React template spec

### Phase 5: Gap Filling via Web Research
**Goal**: When source material doesn't cover a topic sufficiently, research it.

1. Identify concepts that are mentioned but not explained in source files
2. Use WebSearch to find authoritative sources
3. Synthesize findings into lesson content
4. Generate MCQs from newly researched content
5. Mark lessons that were web-research-supplemented (for transparency)

This phase can run during Phase 3 when gaps are detected, or as a dedicated pass after initial content generation.

---

## Output Specification

**Primary Output**: Interactive HTML web app saved to a user-specified output directory
**Secondary Output**: Course content JSON (for reprocessing or import)
**Tertiary Output**: Course outline markdown (for review)

### Determining the Output Path (IMPORTANT — do NOT hard-code)

Before generating files, determine `$OUTPUT_DIR` in this order:

1. **If the user specified an output path** in their request (e.g., "save it to ~/courses/lap-guide" or "put it in this repo"), use that path verbatim.
2. **Else if the current working directory is a project root** (has `package.json`, `.git`, or the user is clearly working inside a repo), default to `./learning-guides/[course-name]/` inside that project and confirm with the user before writing.
3. **Else ask the user**: "Where should I save the learning guide? (e.g., `~/Projects/foo/`, current directory, or a custom path)". Wait for their answer before proceeding.
4. **Never** hard-code a path like `~/Projects/` or `Projects/` — respect the user's file-system conventions. Different users organize their work differently; some use `~/Code/`, `~/work/`, `~/Desktop/`, or project-specific parents.

Once `$OUTPUT_DIR` is determined, write the file structure below into `$OUTPUT_DIR/[course-name]-learning-guide/`.

**File Structure**:
```
$OUTPUT_DIR/[course-name]-learning-guide/
├── index.html          # Main interactive web app (or multi-file React)
├── course-content.json # Structured course data
├── course-outline.md   # Human-readable course map
└── README.md           # How to use the guide
```

---

## Quality Checklist

Before delivering the learning guide, verify:

- [ ] Learning path is logical (no concept references something not yet taught)
- [ ] Every MCQ has explanations for ALL options (correct and wrong)
- [ ] Tips and hints are practical, not generic
- [ ] Navigation works (can jump to any lesson, go back/forward)
- [ ] MCQ feedback is immediate and clear
- [ ] Cross-module MCQs actually reference prior knowledge
- [ ] Content is accurate (especially for domain-specific material)
- [ ] UI is clean and readable on desktop and mobile
- [ ] Progress tracking works correctly
- [ ] Retest mode shuffles questions properly

---

## Usage Examples

**Example 1: Convert LAP research into learning guide**
```
User: "Create an interactive learning guide from my LAP research files"
Skill:
1. Reads all files in lap-research-knowledge-base/ and lap-intelligence-hub/
2. Asks user for the output directory (or uses a path they already specified)
3. Auto-structures: Fundamentals → LeadGen → LOS → Credit → Advanced
4. Generates lessons with MCQs from transcriptions and knowledge base
5. Builds interactive HTML app
6. Saves to $OUTPUT_DIR/lap-learning-guide/
```

**Example 2: Create a course on any topic**
```
User: "Build me an interactive course on Kubernetes"
Skill:
1. No source files → launches web research (Phase 5 first)
2. Builds knowledge graph from research findings
3. Auto-structures learning path
4. Generates content + MCQs
5. Builds interactive HTML app
```

**Example 3: Enhance existing course**
```
User: "Add more MCQs to Module 3 and make them harder"
Skill:
1. Reads existing course-content.json
2. Generates additional advanced MCQs for Module 3
3. Regenerates the web app with new content
```

---

## Reference Files

| File | When to Read | Purpose |
|------|-------------|---------|
| `references/content-analysis-patterns.md` | Phase 1 | How to analyze and catalog source content |
| `references/mcq-generation-patterns.md` | Phase 3 | MCQ quality patterns, distractor design, difficulty scaling |
| `references/boot-dev-pedagogy.md` | Phase 2-3 | Boot.dev's educational design patterns to emulate |
| `references/web-app-features.md` | Phase 4 | Detailed spec for interactive features |
| `templates/webapp-template-spec.md` | Phase 4 | HTML/React template specifications |

---

## Future Enhancements (v2.0)

- **AI Chat Integration**: Optional Claude/Cursor API chat panel for asking questions about current lesson
- **Spaced Repetition**: Track which MCQs were answered wrong, resurface them later
- **Code Sandbox**: For technical courses, embed a code editor
- **Export to PDF**: Generate printable study guide
- **Multi-user Progress**: Backend + auth for team training scenarios
