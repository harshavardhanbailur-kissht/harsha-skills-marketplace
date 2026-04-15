# Skill Integration Reference for Deep Thinker

## Overview

The Deep Thinker operates as an analysis and architecture engine within a broader skill ecosystem. While the Deep Thinker does not execute skills directly, it must be aware of the available domain skills to produce actionable output that downstream executors can leverage. This reference guides thinkers in annotating their analysis with skill recommendations, enabling seamless handoff to specialized execution skills.

### The Boundary
- **Deep Thinker owns:** Problem analysis, architecture design, implementation strategy, edge case identification
- **Executor owns:** Running the actual skills, routing work to domain specialists
- **Interface:** Annotated output files that signal which skills should activate for each component

---

## The Skill Ecosystem

### Core Domain Skills

| Skill | Primary Domain | Triggers | Executor Activation |
|-------|---|---|---|
| **ui-ux-mastery-modular** | UI/UX design, accessibility, design patterns | "interface", "component", "user experience", "accessibility" | Detailed design specs, wireframes, WCAG compliance |
| **shadcn-ui-mastery** | React + Tailwind CSS, component library | "React", "Tailwind", "component", "form", "interactive" | React implementation, shadcn components, state management |
| **3d-web-graphics-mastery** | WebGL, Three.js, WebXR, shaders | "3D", "graphics", "canvas", "visualization", "immersive" | 3D scene setup, shader writing, performance optimization |
| **gas-debugger** | Debugging, security, code quality | "bug", "security", "vulnerability", "performance issue", "error" | Code review, penetration testing, optimization |
| **project-orchestrator** | Multi-step execution, state tracking, workflow | "execute", "deploy", "integrate", "multi-phase" | Decomposing strategy into ordered tasks, skill routing |
| **frontend-blitz** | Rapid UI prototyping, no-backend demos | "prototype", "MVP", "demo", "speed", "quick iteration" | Quick mockups, interactive demos, user testing |
| **algorithmic-art** | Generative art, creative coding, p5.js | "generative", "art", "animation", "creative", "flow field" | p5.js sketches, procedural generation, visual effects |

---

## Why Thinkers Need Skill Awareness

### Problem
Currently, Deep Thinker output exists in isolation. An IMPLEMENTATION.md file might describe "build a React login form" without signaling that **shadcn-ui-mastery** should handle it. The executor reads the thinker's work and has to infer which skills apply.

### Solution
Thinkers annotate their output with **skill signals**. This creates a direct handoff: executor reads the annotated files, sees the signals, and activates the right skills without ambiguity.

### Benefit
- Thinker output is more complete (it explains the "what" and "which skill handles it")
- Executor has clear routing instructions
- Skills are not left underutilized or duplicated
- Handoff time decreases; quality increases

---

## Annotation Pattern

### Basic Syntax
```
[STEP/SECTION DESCRIPTION]
→ SKILLS: skill-name-1, skill-name-2
→ KEYWORDS: trigger-word-1, trigger-word-2
→ EXECUTOR ACTIONS: [what the executor should do with this skill]
```

### Example Annotation
```
### Step 3: Build Login Form
→ SKILLS: shadcn-ui-mastery, ui-ux-mastery-modular
→ KEYWORDS: React, form, Tailwind, accessibility
→ EXECUTOR ACTIONS:
   - Activate shadcn-ui-mastery for form components (Input, Button, Form wrappers)
   - Activate ui-ux-mastery-modular for accessibility review (ARIA labels, focus management)
   - Ensure password field has strength indicator (design from ui-ux-mastery, implement with shadcn)
```

---

## Skill-Domain Mapping

### Frontend Implementation
- **React components** → shadcn-ui-mastery
- **Design system, layout, accessibility** → ui-ux-mastery-modular
- **Speed/MVP needed** → frontend-blitz (use instead of modular when time is critical)

**Decision Tree:**
- "Need production-quality UI with full accessibility?" → ui-ux-mastery-modular + shadcn-ui-mastery
- "Need a quick demo for user testing?" → frontend-blitz
- "Need Tailwind + component library?" → shadcn-ui-mastery (always needed for React work)

### Graphics & Visualization
- **3D scenes, WebGL, Three.js** → 3d-web-graphics-mastery
- **Generative art, p5.js, creative visuals** → algorithmic-art
- **UI-facing charts/diagrams** → ui-ux-mastery-modular for layout + shadcn-ui-mastery for React wrapper

**Coordination:**
- If UI has both a 3D canvas and interactive controls, activate 3d-web-graphics-mastery for canvas, shadcn-ui-mastery for controls.

### Quality & Security
- **Bug reproduction, performance**, code issues → gas-debugger
- **Security vulnerabilities**, penetration testing → gas-debugger
- **Code quality checks** before handoff → gas-debugger

### Orchestration & Execution
- **Multi-phase project**, state tracking, workflow orchestration → project-orchestrator
- **Long-running execution** with checkpoints → project-orchestrator

---

## Annotation Patterns by Output File Type

### ARCHITECTURE.md
**Purpose:** High-level design that informs skill selection

**Where to Annotate:**
- System components section: note which skill handles implementation
- Technology choices: explain why (e.g., "shadcn-ui-mastery for consistent React components")
- Design constraints: flag accessibility (ui-ux-mastery-modular) or performance (gas-debugger) concerns early

**Example:**
```markdown
### Frontend Architecture
- Components: shadcn-ui + Tailwind CSS
  → SKILL: shadcn-ui-mastery (handles React state + Tailwind integration)
  → SKILL: ui-ux-mastery-modular (validates accessibility, layout patterns)
- 3D Viewer: Three.js canvas with shader support
  → SKILL: 3d-web-graphics-mastery (scene, lighting, shaders)
  → REVIEW: gas-debugger (WebGL error handling, performance profiling)
```

### IMPLEMENTATION.md
**Purpose:** Step-by-step instructions for building the solution

**Where to Annotate:**
- Every major step or feature block
- Dependency chains (e.g., "Step 2 must complete before Step 4 can start")
- Risk areas where gas-debugger should review

**Example:**
```markdown
### Step 2: Implement Authentication Form
→ SKILLS: shadcn-ui-mastery, ui-ux-mastery-modular
→ INPUTS: User credentials (email, password)
→ OUTPUTS: Auth token, session management
→ EXECUTOR ACTIONS:
   - shadcn-ui-mastery: Build form with Input, Password, Button components
   - ui-ux-mastery-modular: Ensure WCAG 2.1 AA compliance, test keyboard navigation
   - gas-debugger: Review password handling (no console logs, secure storage)

### Step 3: Connect to Backend API
→ SKILLS: shadcn-ui-mastery (API integration in React), gas-debugger (security review)
→ RISK: Credential exposure in network calls
→ EXECUTOR ACTIONS:
   - shadcn-ui-mastery: Implement fetch/axios with proper error handling
   - gas-debugger: Verify HTTPS enforcement, inspect headers for leaks, test CORS
```

### EXECUTION_CHECKLIST.md
**Purpose:** Ordered task list for execution

**Where to Annotate:**
- Add a "Skills Required" section at the top
- Tag each checklist item with skill abbreviations
- Group by skill activation order (if sequential)

**Example:**
```markdown
# Execution Checklist

## Skills Required
1. **ui-ux-mastery-modular** (design validation, accessibility)
2. **shadcn-ui-mastery** (React + Tailwind implementation)
3. **gas-debugger** (security & performance review)
4. **project-orchestrator** (if multi-day, multi-person work)

## Phase 1: Design & Architecture [ui-ux-mastery-modular]
- [ ] Review wireframes for accessibility
- [ ] Validate color contrast, font sizes
- [ ] Test focus indicators

## Phase 2: Implementation [shadcn-ui-mastery]
- [ ] Build login form with shadcn components
- [ ] Integrate with API (see Step 3)
- [ ] Add error handling UI

## Phase 3: Review & Hardening [gas-debugger]
- [ ] Security audit (credential handling, CORS, HTTPS)
- [ ] Performance profiling (bundle size, render performance)
- [ ] Final code review
```

### EDGE_CASES.md
**Purpose:** Identify risky scenarios and mitigation strategies

**Where to Annotate:**
- Security edge cases → Flag for gas-debugger
- Complex UI states → Flag for ui-ux-mastery-modular
- 3D rendering edge cases → Flag for 3d-web-graphics-mastery
- Performance concerns → Flag for gas-debugger

**Example:**
```markdown
## Edge Case: Rapid Form Submission (Double-Click)
→ SKILL: shadcn-ui-mastery (disable button during submission)
→ SKILL: gas-debugger (test race conditions)
→ RISK: Duplicate API calls, inconsistent state
→ MITIGATION:
   - shadcn-ui-mastery: Disable submit button during loading
   - gas-debugger: Add request deduplication middleware

## Edge Case: 3D Asset Loading Failure
→ SKILL: 3d-web-graphics-mastery (fallback rendering)
→ SKILL: ui-ux-mastery-modular (error messaging)
→ RISK: Blank screen, poor UX
→ MITIGATION:
   - 3d-web-graphics-mastery: Load low-poly fallback, show error
   - ui-ux-mastery-modular: Display user-friendly error message
```

---

## Cross-Skill Coordination

### Multi-Domain Features
Some features span multiple skill domains. The Deep Thinker must sequence skill activation and flag potential conflicts.

**Example: Interactive 3D Data Visualization**
```
ARCHITECTURE:
→ UI Shell: shadcn-ui-mastery (buttons, controls)
→ 3D Canvas: 3d-web-graphics-mastery (scene rendering)
→ Accessibility: ui-ux-mastery-modular (keyboard controls for 3D)
→ Performance: gas-debugger (WebGL profiling)

SEQUENCE:
1. ui-ux-mastery-modular defines accessible keyboard bindings for 3D rotation
2. 3d-web-graphics-mastery implements camera controls responding to those bindings
3. shadcn-ui-mastery wraps controls in accessible button groups
4. gas-debugger profiles frame rate, WebGL memory usage

POTENTIAL CONFLICT:
- shadcn-ui-mastery wants automatic form labeling
- 3d-web-graphics-mastery needs custom canvas bindings
→ RESOLUTION: Use aria-label on canvas, rely on gas-debugger to test keyboard navigation
```

### Rapid Prototyping vs. Production Quality
When speed and quality are both needed:

```
THINKER DECISION:
"We need MVP in 2 days, then refactor in sprint 2"

ANNOTATION:
→ MVP Phase: frontend-blitz (skip design validation, focus on working demo)
→ Production Phase: ui-ux-mastery-modular + shadcn-ui-mastery (full design system)
→ Transition: gas-debugger reviews MVP code before refactor to catch tech debt

EXECUTOR ACTION:
- Sprint 1: Activate frontend-blitz, build quick prototype
- Sprint 2: Swap to ui-ux-mastery-modular + shadcn-ui-mastery, refactor with full design
```

### Debugging & Optimization
Multiple skills can flag performance issues; gas-debugger coordinates review:

```
THINKER NOTES:
- shadcn-ui-mastery might over-render with unnecessary re-renders
- 3d-web-graphics-mastery canvas might leak WebGL context
- algorithmic-art generative loop might hang the browser

ANNOTATION:
→ SKILLS: shadcn-ui-mastery, 3d-web-graphics-mastery, algorithmic-art, gas-debugger
→ PRIMARY REVIEWER: gas-debugger (performs profiling, identifies bottlenecks)
→ SECONDARY REVIEWERS: Each skill optimizes its own domain per gas-debugger findings

EXECUTOR ACTION:
- gas-debugger profiles entire stack
- Routes specific optimizations to domain skills (e.g., "shadcn, memoize this component")
```

---

## The Thinker-Orchestrator Handoff

### Current State
Deep Thinker produces ARCHITECTURE.md, IMPLEMENTATION.md, etc. The output is thorough but skill-agnostic. Executors must manually infer which skills apply.

### Ideal Pipeline
```
┌─────────────────────────────────────────┐
│  USER REQUEST: "Build login system"     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  DEEP THINKER                          │
│  - Analyzes requirements                │
│  - Designs architecture                 │
│  - Plans implementation steps           │
│  - Annotates with SKILL SIGNALS         │
│  Output: .deep-think/ folder with:     │
│    - ARCHITECTURE.md (skill-annotated)  │
│    - IMPLEMENTATION.md (step w/ skills) │
│    - EXECUTION_CHECKLIST.md (skill seq) │
│    - EDGE_CASES.md (risk + skills)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  PROJECT ORCHESTRATOR                   │
│  - Reads .deep-think/ files            │
│  - Extracts SKILL SIGNALS               │
│  - Decomposes into ordered tasks        │
│  - Maps tasks to domain skills          │
│  Output: Activation sequence            │
│    1. ui-ux-mastery-modular (design)   │
│    2. shadcn-ui-mastery (implement)    │
│    3. gas-debugger (security review)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  DOMAIN SKILL EXECUTORS                 │
│  - ui-ux-mastery-modular: Build design |
│  - shadcn-ui-mastery: Code components   │
│  - gas-debugger: Test & optimize        │
│  Output: Completed feature              │
└─────────────────────────────────────────┘
```

### What Deep Thinker Must Provide for Orchestrator
Currently missing:
- **Explicit skill recommendations** (vs. implicit in prose)
- **Task dependencies** (which steps block which)
- **Skill activation order** (what to do when if multiple skills apply)
- **Risk flagging** (which steps need gas-debugger review)

**Thinker's Responsibility:**
1. Annotate every significant step with skills
2. Flag dependencies (e.g., "Step 3 blocks Step 5")
3. Sequence multi-skill work (design before code, code before security review)
4. Mark high-risk sections for gas-debugger

**Orchestrator's Responsibility:**
1. Parse skill signals from thinker output
2. Build activation sequence
3. Decompose tasks into micro-steps
4. Track state, handle failures, retry logic

### Example Handoff: Login System
**Deep Thinker Output:**
```markdown
# IMPLEMENTATION.md

## Phase 1: Design [ui-ux-mastery-modular]
- Create wireframes, validate accessibility
→ EXECUTOR: ui-ux-mastery-modular

## Phase 2: Build Form [shadcn-ui-mastery]
- Implement React components, integrate API
→ EXECUTOR: shadcn-ui-mastery
→ BLOCKS: Phase 3 (cannot test without form)

## Phase 3: Security & Testing [gas-debugger]
- Review credential handling, CSRF protection, password encryption
→ EXECUTOR: gas-debugger
→ DEPENDS ON: Phase 2
```

**Orchestrator Reads & Routes:**
1. Extract skill signals: ui-ux-mastery-modular → shadcn-ui-mastery → gas-debugger
2. Create task queue respecting dependencies
3. Activate ui-ux-mastery-modular first (no dependencies)
4. Activate shadcn-ui-mastery after (Phase 1 complete)
5. Activate gas-debugger after (Phase 2 complete)

---

## Quick Reference: When to Annotate

| Scenario | Annotation | Example |
|----------|-----------|---------|
| New feature requires React component | → shadcn-ui-mastery | "Login form: shadcn-ui-mastery" |
| Design system, accessibility needed | → ui-ux-mastery-modular | "Wireframe review: ui-ux-mastery-modular" |
| 3D rendering, WebGL, shaders | → 3d-web-graphics-mastery | "Particle effect: 3d-web-graphics-mastery" |
| Security, performance, debugging | → gas-debugger | "Password handling: gas-debugger" |
| Rapid prototype, no backend | → frontend-blitz | "Quick mockup: frontend-blitz" |
| Generative art, p5.js, animations | → algorithmic-art | "Flow field background: algorithmic-art" |
| Multi-day, multi-skill coordination | → project-orchestrator | "End-to-end deployment: project-orchestrator" |

---

## Summary

The Deep Thinker's role is to **think deeply and annotate with skill signals**. By explicitly naming which domain skills handle which parts of the solution, thinker output becomes a blueprint for executor action. This transforms the thinker-executor relationship from implicit inference to explicit coordination.

**Key Principle:**
> "The thinker doesn't execute; it annotates. The executor doesn't think; it activates. Together, the annotated thinking becomes actionable skill activation."
