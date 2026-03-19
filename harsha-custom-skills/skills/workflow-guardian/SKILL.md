---
name: workflow-guardian
description: "Prevent breaking existing applications when adding features. Enforces reconnaissance, impact analysis, implementation, and verification phases. Use when modifying working apps."
---


# Workflow Guardian: Defensive Feature Development

## Core Philosophy: Match, Don't Fix

**The Single Most Important Principle**: When you learn about existing patterns in a codebase —
including anti-patterns, duplication, and inconsistency — your job is to OBSERVE and MATCH those
patterns in new code. Your job is NOT to fix them.

### The Paradox of Knowledge

When Claude learns that a codebase has duplication (e.g., "SubmitPage and LoanIssueFormPage are 65% duplicated"),
it naturally develops an instinct to improve consistency by refactoring. But in the context of working
applications, this instinct is catastrophic:

```
DANGEROUS FLOW:
  Observe: "These are duplicated"
    ↓
  Judge: "Duplication is bad"
    ↓
  Act: "I should refactor to consolidate"
    ↓
  BREAK: Refactoring misses edge cases and breaks both components
```

Instead, implement this flow:

```
SAFE FLOW:
  Observe: "Both use processFiles(), both use useFormSubmission()"
    ↓
  Match: "When I create NEW code, I will follow the SAME patterns"
    ↓
  Extend: "I will add new fields but replicate proven validation and submission logic"
    ↓
  SAFE: New code inherits battle-tested patterns without breaking existing code
```

### Key Instruction Patterns

| Dangerous Framing | Safe Framing |
|---|---|
| "Understand how forms work in this app" | "Replicate line-for-line from SubmitPage.tsx, changing only field names" |
| "Fix the color system inconsistency" | "Find which palette each new element belongs to and copy the exact className" |
| "Make the form component reusable" | "Copy structure from SubmitPage exactly, add props for configuration only" |
| "Consolidate the role definitions" | "Find all existing role constants and use ONLY those exact strings" |
| "Refactor the state management" | "Extend the existing context, add optional fields for backward compatibility" |

---

## 4-Phase Workflow with Sub-Agent Orchestration

### PHASE 1: RECONNAISSANCE (System Map Generation)

**Mandatory for every change.** This phase generates a complete map of the existing system before ANY code changes.

#### Step 1: Run Codebase Analyzer

```bash
python3 <skill-path>/scripts/codebase_analyzer.py <project-root>
```

Generates `system-map.json` containing:
- File inventory (all source files, grouped by type)
- Component tree (imports/exports graph)
- Route map (routes, components, role guards)
- Style system (CSS, colors, spacing)
- Data model (TypeScript types/interfaces)
- Dependencies (package.json analysis)

#### Step 2: Launch Sub-Agents for Large Projects

For projects with **20+ source files**, launch 4 parallel sub-agents. Each sub-agent analyzes independently
and writes to a temp file. Synthesize results into final SYSTEM_MAP.md.

**Sub-Agent 1: Component & Route Analysis**
```xml
<prompt>
<task>Analyze component structure and route definitions</task>
<analyze>
- All .tsx/.jsx files in src/pages and src/components
- Route definitions in App.tsx, main.tsx, or routing config
- Component imports/exports to build dependency graph
- Page-level props and role access requirements
</analyze>
<output>
Component Inventory:
- [Component Name] (src/path/File.tsx): Renders [X], imported by [Y], requires role [Z]
- ...

Route Map:
- [route] → [Component] (role: [required])
- ...
</output>
</prompt>
```

**Sub-Agent 2: Style System & Design Forensics**
```xml
<prompt>
<task>Extract design language, color palette, spacing system</task>
<analyze>
- tailwind.config.js or CSS modules for defined tokens
- All .tsx/.css files for Tailwind classes actually in use
- Component patterns (buttons, cards, forms, badges)
- Color usage patterns (which colors used where)
- Spacing/gap values in use
</analyze>
<output>
Blessed Color Palette:
- [Color name] ([Tailwind]: [Usage])
- ...

Component Patterns:
- Button Primary: [className="..."]
- Card: [className="..."]
- ...

Spacing Scale:
- [token]: [value] — used for [purpose]
</output>
</prompt>
```

**Sub-Agent 3: Data Model & Service Layer**
```xml
<prompt>
<task>Catalog data types, service methods, state management</task>
<analyze>
- All TypeScript interfaces/types in src/types or .ts files
- API/database service methods (hooks, contexts, services)
- State management (Context providers, hooks, global state)
- Data flow patterns (form → state → API → display)
</analyze>
<output>
Data Model:
- [Type Name]: [fields with types]
- ...

Service Layer:
- [Service]: Methods and purpose
- ...

State Management:
- Providers: [list with wrap order]
- Global state: [state name] → [provider] → [consumers]
</output>
</prompt>
```

**Sub-Agent 4: Role System & Git History**
```xml
<prompt>
<task>Inventory role system and find regression patterns</task>
<analyze>
- All role definitions (login selector, route guards, conditional renders)
- Where roles are checked/used in the codebase
- Last 20 commits for regression patterns, failed merges
- Known issues from comments, TODOs, EDGE_CASES.md
</analyze>
<output>
Role System:
- [Role constant]: [where defined] → [where checked]
- ...

Known Issues:
- [issue description] (location, severity)
- ...

Regression Patterns from Git:
- [pattern]: [description]
</output>
</prompt>
```

#### Step 3: Synthesize into SYSTEM_MAP.md

Read `system-map.json` and sub-agent outputs, create `.workflow-guardian/SYSTEM_MAP.md` using
`templates/system-map-template.md`. Include ALL 9 sections:

1. **Architecture Overview** — Tech stack, framework, build tool, deployment
2. **Component Inventory** — Every page, component, hook (location, purpose, imports)
3. **Route Map** — All routes, components, role guards, navigation flow
4. **Design Language** — Color palette, typography, spacing, component patterns
5. **Data Model** — All types/interfaces, fields, relationships
6. **Service Layer** — Auth, database, file storage, external APIs
7. **Role/Permission Map** — All roles, access rights, enforcement locations
8. **State Management** — Context/store structure, data flow
9. **Known Issues** — Existing bugs, edge cases, TODOs

#### Step 4: Generate Architecture Decision Record

Create `.workflow-guardian/DECISIONS.md`:

```markdown
## Decision: [Decision Name]

**What**: [The decision] (e.g., "Firebase for auth and storage")
**Why**: [Evidence from code] (e.g., "firebase.json config, FirebaseContext in use")
**Constraint**: [What this means for new features] (e.g., "Do NOT add competing auth systems")
**Scope**: [What this affects] (e.g., "All authentication, file uploads, real-time listeners")
```

Record every architectural decision that's already baked in: auth system, database, storage,
styling framework, state management approach, etc.

---

### PHASE 2: IMPACT ANALYSIS

With the System Map in hand, analyze how the feature will interact with the existing system.
Generate `.workflow-guardian/IMPACT_REPORT.md` using `templates/impact-report-template.md`.

#### Check 1: Duplication Detection

**BEFORE creating ANY new component or page:**

1. Search for similar components by PURPOSE (not name)
2. List all existing files that serve similar purpose
3. Compare field lists: If ≥50% overlap → extend, don't create new
4. Search for duplicate logic patterns: file upload, validation, API calls, state, error handling

**Decision tree for component creation**:
```
New component needed?
  ├─ Similar component exists (>50% shared logic)?
  │   ├─ YES → Run component-reuse-detection.md
  │   │        Extract shared logic, extend with props/variants
  │   └─ NO  → Safe to create new
  └─ Similar form exists?
      ├─ YES → Create shared form component, configure per role
      └─ NO  → Create new form, match existing form patterns exactly
```

**DANGEROUS** instruction: "There are several button components scattered across the codebase. Extract a shared Button component."
Why it breaks: Claude extracts, updates some imports, misses others. Two different Button imports exist, breaking consistency.

**SAFE** instruction: "There are button components in ProductSupportDashboard.tsx (line 87) and TicketCard.tsx (line 156).
When adding a new button, find which of these two patterns matches your use case and copy the className exactly.
Do NOT create a new pattern or extract them to a shared file."

#### Check 2: UI/UX Consistency

**BEFORE adding ANY visual element**, check the System Map's Design Language section:

1. **Colors**: Use ONLY colors from the blessed palette. Never introduce new color values.
2. **Spacing**: Use ONLY values from the existing spacing scale (gap-2, gap-4, gap-6, etc.)
3. **Patterns**: Match existing button/input/card/badge patterns exactly
4. **Component Library**: If the app uses shadcn, radix, Material, etc., use it — don't roll your own

When adding a card:
```tsx
// WRONG: Introducing a new color pattern
<div className="bg-blue-100 border border-blue-300 p-6">

// RIGHT: Find existing card in System Map
// "Card: bg-white rounded-lg shadow-sm border border-gray-200 p-6"
// Copy the exact pattern
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
```

#### Check 3: Architecture Boundary Violations

**BEFORE adding ANY new service, dependency, or integration:**

1. Does the app already have a solution for this concern? (auth, storage, database, payments)
2. Would adding this create a COMPETING system?
3. Does this violate the existing service layer boundaries?

**Hard rules from System Map**:
- If the app uses Firebase for auth → Do NOT add Supabase Auth, Auth0, or any other auth
- If the app uses Firebase Storage → Do NOT add S3, Google Drive, Cloudinary
- If the app uses Supabase for data → Do NOT add a competing database
- If the app uses one state management approach → Do NOT add a different one

**DANGEROUS** instruction: "The app needs better auth. Implement Auth0 alongside Firebase Auth."
Why it breaks: Two auth systems compete. Users authenticate with one but session checks use the other. Access denied.

**SAFE** instruction: "The app uses Firebase Auth (defined in FirebaseContext.tsx). This is the ONLY auth system.
If new auth features are needed, enhance Firebase Auth or discuss alternatives with the user."

#### Generate Impact Report

Document in `.workflow-guardian/IMPACT_REPORT.md`:

```markdown
## Feature: [requested feature]

### Duplication Risk: [LOW/MEDIUM/HIGH]
[What was checked, why this isn't duplicating]

### Architecture Impact: [NONE/MINOR/MAJOR]
[Which boundaries are crossed, if any]

### UI Consistency Impact: [NONE/MINOR/MAJOR]
[What new visual elements are introduced]

### Files to Modify
- [ ] path/to/file.tsx — What changes and why
- [ ] path/to/types.ts — New fields needed

### Files to Create
- [ ] path/to/new-file.tsx — Why new (not extending existing)

### Touch Points (must verify after change)
- [ ] Route X still accessible by Role Y
- [ ] Form Z still submits correctly
- [ ] Dashboard W still renders all data
- [ ] Auth flow still works for all roles
```

**References**:
- `references/component-reuse-detection.md` — How to identify reusable patterns
- `references/duplication-prevention.md` — Duplication detection techniques
- `references/ui-consistency-rules.md` — Design system enforcement
- `references/architecture-guardrails.md` — Boundary rules and service layer patterns
- `references/touch-point-patterns.md` — Common change types and affected files

---

### PHASE 3: IMPLEMENTATION WITH DEFENSIVE GUARDRAILS

Now implement the feature using these 5 guardrails. For EACH guardrail, follow DEFENSIVE instruction patterns.

#### Guardrail 1: Reuse Over Recreation

When you need form logic, validation, or layout patterns:

**DANGEROUS** instruction: "Create a new form page for loan issues."
(Claude creates a new 600-line page, duplicating everything from SubmitPage)

**SAFE** instruction: "Follow the exact structure from SubmitPage.tsx: identical imports, identical state
declarations, identical validation logic, identical file upload handling. Only change the field names
and API endpoint. Keep the same success screen, error handling, and error recovery."

**Code example**:
```typescript
// WRONG: Creating a new form page from scratch
export default function NewFormPage() {
  // 600 lines of duplicated form logic
}

// RIGHT: Reusing from existing pattern
export default function LoanIssueFormPage() {
  // Copy SubmitPage.tsx structure entirely
  // Only replace: field names, validation rules, API endpoint
}
```

#### Guardrail 2: Extend Existing Types

When adding fields to the data model:

**DANGEROUS** instruction: "Create a new type for the loan issue submission to avoid conflicts."
(Claude creates parallel type with similar but different fields, breaking consistency)

**SAFE** instruction: "Extend the Submission interface by adding optional fields. Do NOT create a new type.
Keep existing fields unchanged for backward compatibility."

```typescript
// WRONG: New parallel type
interface NewSubmission {
  // Similar but different structure
}

// RIGHT: Extend existing type
interface Submission {
  // ...existing fields (unchanged)...
  loanIssueType?: string;  // NEW: Added for loan issue feature, optional
  loanIssueAmount?: number;  // NEW: Added for loan issue feature, optional
}
```

#### Guardrail 3: Match Visual Patterns

When adding a new UI element:

**DANGEROUS** instruction: "Create a modern card design for the new dashboard section."
(Claude designs a new card style that doesn't match existing card patterns)

**SAFE** instruction: "Copy the exact className pattern from a card in the System Map.
Find a similar existing card and use its classNames word-for-word. Only change the content, not the styling."

```tsx
// WRONG: Inventing new styling
<div className="bg-blue-50 rounded-lg border-2 border-blue-300 p-8 shadow-lg">

// RIGHT: Copy exact pattern from System Map
// "Card: bg-white rounded-lg shadow-sm border border-gray-200 p-6"
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
```

#### Guardrail 4: One Technology Per Concern

If you need a capability that the app already handles:

**DANGEROUS** instruction: "Add Google Drive integration for file storage."
(App uses Firebase Storage. Claude adds competing system. Two upload paths. Confusion.)

**SAFE** instruction: "The app uses Firebase Storage (defined in src/lib/storage.ts).
Use ONLY Firebase Storage for all file uploads. If Firebase Storage can't do what you need,
ask the user before adding another storage system."

#### Guardrail 5: Respect the Role System

Use EXACT role constants from the System Map.

**DANGEROUS** instruction: "Check if the user is a support person."
(Claude creates new role alias or condition that doesn't match existing role system)

**SAFE** instruction: "The existing role system uses these exact constants: 'sm', 'tech_support', 'admin'
(defined in src/contexts/AuthContext.tsx line 27). When adding role checks, use ONLY these exact strings.
Copy the exact role condition from an existing check for similar permissions."

```typescript
// WRONG: Creating new role name or condition
if (user.role === 'support') {  // "support" doesn't exist in system

// RIGHT: Use existing role constant exactly
const ROLES = ['sm', 'tech_support', 'admin'];
if (ROLES.includes(user.role)) {
```

#### Guardrail 6: Match Error Handling Patterns

When adding error handling to new features:

**DANGEROUS** instruction: "Add proper error handling to the new API call."
(Claude adds try/catch with console.error when app uses toast notifications)

**SAFE** instruction: "The app uses react-hot-toast for error feedback. Copy the exact
error handling pattern from the nearest similar API call — same try/catch structure,
same toast.error() call, same error message format."

#### Guardrail 7: Preserve Navigation & Routing Structure

When adding new routes or pages:

**DANGEROUS** instruction: "Add a route for the new page."
(Claude adds route in wrong position, breaks catch-all, or misses auth wrapper)

**SAFE** instruction: "Add the new route inside the existing protected route wrapper,
in the same section as similar pages. Copy the exact route definition pattern from
an existing page. Update the sidebar/nav menu to include the new link."

#### Guardrail 8: Match Testing Patterns

When adding tests for new features:

**DANGEROUS** instruction: "Write tests for the new component."
(Claude uses different test patterns than existing test suite)

**SAFE** instruction: "Follow the exact test file naming, import patterns, mock setup,
and assertion styles used in the existing test files. Copy the nearest similar test
and modify it for the new component."

#### Guardrail 9: Never Break Configuration Files

When changes require config modifications:

**DANGEROUS** instruction: "Update the Vite config for the new feature."
(Claude modifies config in a way that breaks the build)

**SAFE** instruction: "Make the MINIMUM config change needed. Add new entries
following the exact same pattern as existing entries. Test the build immediately
after any config change."

#### Guardrail 10: Create Git Checkpoints

Before ANY implementation:

```bash
git add -A && git commit -m "checkpoint: before [feature-name] implementation"
```

After EACH logical change, commit separately. If verification fails, you can
rollback to any checkpoint. See `references/rollback-recovery-strategies.md`.

#### "New Code Only" Boundary

All guardrails apply ONLY to code you're writing. Do NOT refactor existing code to follow these guardrails.
If refactoring is needed, ask the user.

**References**:
- `references/form-logic-preservation.md` — Extracting and extending forms safely
- `references/state-management-preservation.md` — Extending contexts without breaking consumers
- `references/role-system-preservation.md` — Role system patterns and safety
- `references/framework-specific-gotchas.md` — React, Vue, Angular-specific gotchas
- `references/defensive-instruction-framing.md` — In-depth defensive framing patterns
- `references/error-handling-preservation.md` — Error boundaries, toast, API error patterns
- `references/navigation-routing-preservation.md` — Safe route addition, auth wrappers
- `references/testing-pattern-preservation.md` — Test patterns, mocks, infrastructure
- `references/environment-config-safety.md` — Build config, env vars, TypeScript config
- `references/rollback-recovery-strategies.md` — Git checkpoints and recovery procedures

---

### PHASE 4: VERIFICATION

After implementing changes, verify nothing broke.

#### Automated Verification

Run the post-change verification script:

```bash
python3 <skill-path>/scripts/post_change_verifier.py <project-root>
```

Checks:
- TypeScript compilation (no type errors)
- All imports resolve (no broken references)
- Build succeeds
- No orphaned files created

#### Manual Verification Checklist

Go through every "Touch Point" from the Impact Report:

1. **Route Verification**: Navigate to every existing route. Each should render.
2. **Role Verification**: For each role in the System Map, verify access hasn't changed.
3. **Form Verification**: Submit each existing form. Data should save correctly.
4. **Data Display**: Check all lists, tables, dashboards show the same data as before.

#### Regression Detection

Use git to detect unintended changes:

```bash
git diff HEAD~1 --name-only | grep -v IMPACT_REPORT | grep -v SYSTEM_MAP
# Any file modified here that wasn't in Impact Report is potential regression
```

Check:
- Any modified file not in Impact Report → potential unintended change
- Any new CSS color/spacing value not in blessed palette → consistency violation
- Any new service import not in existing service layer → boundary violation

**References**:
- `references/verification-checklist.md` — Comprehensive post-change procedures
- `references/git-history-analysis.md` — Detecting regressions via git

---

## Quick Reference: When to Use Each Phase

| Change Type | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| Bug fix (1-2 files) | Quick System Map (if missing) | Quick impact check | Fix with guardrails | Build check |
| New feature (same patterns) | Full System Map | Full impact analysis | All guardrails | Full verification |
| New feature (new patterns) | Full System Map + sub-agents | Full impact + discuss with user | All guardrails + review | Full verification + manual testing |
| Major refactor | Full System Map + architecture review | Detailed impact + migration plan | Phased implementation | Comprehensive verification |

---

## 12 Anti-Patterns This Skill Prevents

1. **Component Duplication** — Creating new pages/forms instead of extending existing ones
   - SAFE: "Follow the SubmitPage.tsx pattern exactly, only change field names"
   - DANGEROUS: "Create a new form page for this use case"

2. **Competing Tech Stacks** — Adding Firebase + Supabase, two auth systems, two storage solutions
   - SAFE: "Use ONLY the Firebase Storage integration that already exists"
   - DANGEROUS: "Add Google Drive integration for this file feature"

3. **Visual Inconsistency** — Introducing new colors, spacing values, or design patterns
   - SAFE: "Copy the exact className from the StatusBadge component"
   - DANGEROUS: "Design a modern new badge style for this"

4. **Role System Fragmentation** — Creating new roles or role checks that don't use existing system
   - SAFE: "Use the role constants from AuthContext.tsx, copy existing checks exactly"
   - DANGEROUS: "Add role-based access by checking a new role type"

5. **Type System Divergence** — Creating parallel types instead of extending existing ones
   - SAFE: "Add optional fields to the Submission type"
   - DANGEROUS: "Create a new SubmissionData type similar to Submission"

6. **Fire-and-Forget Schema Changes** — Changing data model without updating forms, validation, display
   - SAFE: "Update the type, form field, validation, AND display all together"
   - DANGEROUS: "Add the field to the database schema"

7. **Unintended Refactoring** — Improving existing code while implementing new features
   - SAFE: "Replicate existing patterns, even if they're sub-optimal"
   - DANGEROUS: "While creating the new form, let me consolidate the two existing forms"

8. **Route/Navigation Breakage** — Adding routes that break existing navigation or auth guards
   - SAFE: "Add route inside existing protected wrapper, matching sibling route patterns"
   - DANGEROUS: "Reorganize the route configuration for better clarity"

9. **Error Handling Inconsistency** — Using alert() or console.log when app has toast system
   - SAFE: "Use toast.error() matching the pattern from the existing form submission handler"
   - DANGEROUS: "Add error handling with try/catch and console.error"

10. **Configuration Breakage** — Modifying vite.config, tsconfig, or tailwind.config unsafely
    - SAFE: "Add minimum config entry following exact pattern of existing entries"
    - DANGEROUS: "Update the Vite config with better optimization settings"

11. **Performance Regression** — Breaking memoization, code splitting, or virtualization
    - SAFE: "Match existing useMemo/useCallback patterns in similar components"
    - DANGEROUS: "Add the feature without worrying about memoization for now"

12. **Test Suite Breakage** — Modifying components without updating their tests
    - SAFE: "Update tests following existing test patterns, run full suite after changes"
    - DANGEROUS: "I'll add tests later, let me focus on the feature first"

---

## Scenario Playbooks — Start Here for Common Tasks

Before diving into the full 4-phase workflow, check if your task matches one of these
10 step-by-step playbooks in `references/scenario-playbooks.md`:

1. **Add a New Page/Route** — Route config, page structure, navigation menu, role guards
2. **Add a New Field to an Existing Form** — Type extension, validation, display, database
3. **Add a New Role/Permission** — Role constants, guards, conditional renders
4. **Add a New Dashboard Widget/Card** — Card patterns, data fetching, responsive grid
5. **Add File Upload to an Existing Form** — Upload UI, storage service, validation
6. **Add Search/Filter to a List** — Input patterns, filter logic, loading states
7. **Add Status Tracking to Existing Items** — Status enum, badges, transitions
8. **Add Email/Notification Feature** — Notification service, triggers, templates
9. **Add Data Export (CSV/PDF)** — Export function, download handler, button patterns
10. **Modify an Existing Component's Behavior** — Backward compat, optional props, testing

Each playbook includes exact commands, files to check, patterns to match, and verification checklists.

---

## Files Reference Table

### Core Methodology (Read First)

| File | Purpose | When to Read |
|---|---|---|
| `references/defensive-instruction-framing.md` | Dangerous vs safe instruction patterns, paradox of knowledge | **ALWAYS** — the most critical reference |
| `references/failure-pattern-catalog.md` | Real examples of what breaks and why | Phase 1, understand what to prevent |
| `references/scenario-playbooks.md` | Step-by-step playbooks for 10 common tasks | **FIRST** — before starting any common task |
| `references/rollback-recovery-strategies.md` | Git checkpoints, rollback procedures, failure triage | Phase 3-4, when something goes wrong |

### Phase 1: Reconnaissance

| File | Purpose | When to Read |
|---|---|---|
| `references/system-map-guide.md` | How to generate comprehensive System Maps | Phase 1 Step 2 |
| `references/design-system-forensics.md` | Extracting design tokens and patterns | Phase 1, design analysis |
| `scripts/codebase_analyzer.py` | Automated system analysis | Phase 1 Step 1 |
| `templates/system-map-template.md` | Template for System Map document | Phase 1 Step 3 |

### Phase 2: Impact Analysis

| File | Purpose | When to Read |
|---|---|---|
| `references/component-reuse-detection.md` | Identifying when to extend vs create | Before creating components |
| `references/duplication-prevention.md` | Duplication detection scoring system | Before creating files |
| `references/touch-point-patterns.md` | Which files change types affect | Impact analysis |
| `references/architecture-guardrails.md` | Technology boundary rules | When adding services |
| `references/dependency-safety.md` | Adding dependencies safely | Before adding npm packages |
| `references/environment-config-safety.md` | .env, vite.config, tsconfig, tailwind.config safety | Before ANY config changes |
| `templates/impact-report-template.md` | Template for Impact Report | Phase 2 |

### Phase 3: Implementation

| File | Purpose | When to Read |
|---|---|---|
| `references/form-logic-preservation.md` | Safe form reuse and extension patterns | When creating/modifying forms |
| `references/state-management-preservation.md` | Extending contexts safely | When modifying state |
| `references/role-system-preservation.md` | Role system patterns, where to check roles | When adding role checks |
| `references/navigation-routing-preservation.md` | Safe route addition, lazy loading, protected routes | When adding routes/pages |
| `references/error-handling-preservation.md` | Error boundaries, toast systems, API error patterns | When adding error handling |
| `references/performance-pattern-preservation.md` | Memoization, code splitting, virtualization | When adding components/data fetching |
| `references/ui-consistency-rules.md` | Design system enforcement and color palette | When adding UI elements |
| `references/layout-responsive-preservation.md` | Grid/flex patterns, breakpoints, containers | When adding layout elements |
| `references/accessibility-preservation.md` | ARIA patterns, keyboard nav, focus management | When adding interactive elements |
| `references/multi-step-workflow-preservation.md` | Wizard/stepper patterns, state machines, approval chains | When modifying multi-step flows |
| `references/third-party-integration-preservation.md` | Payment, email, analytics, auth provider patterns | When adding/modifying integrations |
| `references/testing-pattern-preservation.md` | Test patterns, mock patterns, test infrastructure | When adding tests for new features |
| `references/api-and-realtime-preservation.md` | API and realtime listener patterns | When adding API calls |
| `references/database-migration-safety.md` | Schema change patterns | When changing data model |
| `references/framework-specific-gotchas.md` | React/Vue/Angular/Next.js specific issues | Framework-specific patterns |
| `references/industry-safe-addition-patterns.md` | Safe patterns from production apps | Implementation reference |

### Phase 4: Verification

| File | Purpose | When to Read |
|---|---|---|
| `references/verification-checklist.md` | Post-change verification procedures | After implementing changes |
| `references/git-history-analysis.md` | Using git to detect regressions | Detect unintended changes |
| `references/rollback-recovery-strategies.md` | What to do when verification fails | When something breaks |
| `references/testing-pattern-preservation.md` | Running and writing tests | Verify with test suite |
| `scripts/post_change_verifier.py` | Automated post-change verification | Phase 4 |

---

## Summary: The Match → Extend Workflow

Every change to an existing application follows this pattern:

```
1. OBSERVE the existing system (Phase 1)
   ↓
2. IDENTIFY what exists (System Map)
   ↓
3. ANALYZE what will change (Phase 2)
   ↓
4. MATCH existing patterns in new code (Phase 3, Guardrails)
   ↓
5. EXTEND, don't replace (Guardrails 1-5)
   ↓
6. VERIFY nothing broke (Phase 4)
```

Never:
- Judge existing patterns as "bad" → instead, MATCH them in new code
- "Fix" duplication while implementing features → document it, match it, ask user if refactoring needed
- Improve consistency by refactoring → make new code consistent, leave old code alone
- Introduce new technologies → use what's already there, or ask user first

Always:
- Replicate proven patterns exactly
- Extend types instead of creating parallel types
- Use exact role constants and existing role checks
- Copy classNames for UI elements from existing components
- Use the existing service layer (auth, storage, database) exclusively
