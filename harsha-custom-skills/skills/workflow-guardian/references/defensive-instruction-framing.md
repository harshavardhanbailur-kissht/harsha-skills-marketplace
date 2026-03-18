# Defensive Instruction Framing Guide

**CRITICAL DOCUMENT**: This guide is the most important reference in the Workflow Guardian skill. It documents the paradox of knowledge and how to frame every instruction defensively to prevent Claude from breaking existing applications.

---

## The Deadly Paradox

When Claude learns about code patterns—especially anti-patterns or duplication—it develops an instinct to **fix** them. But in the context of existing, working applications, this instinct is catastrophic.

**The Pattern**:
1. Claude reads codebase analysis showing "65% duplication between SubmitPage and LoanIssueFormPage"
2. Claude thinks: "I should fix this by extracting shared components"
3. Claude refactors both forms into a shared container
4. Both forms break because the refactoring removed edge-case handling one of them had
5. User reports "Claude broke my app"

**What Actually Happened**:
Claude correctly identified a problem but incorrectly assumed it should be solved immediately. The knowledge itself triggered the harmful behavior.

**The Solution**:
Every instruction must explicitly separate three mental operations that Claude naturally conflates:

1. **OBSERVE**: Recognize existing patterns
2. **MATCH**: Replicate those patterns in new code
3. **FIX**: Only refactor when explicitly asked, and do it separately

This document teaches you how to write instructions that activate OBSERVE and MATCH while permanently suppressing FIX in the context of adding features.

---

## 1. The Paradox of Knowledge

### 1.1 Why Identifying Problems Does NOT Mean Fixing Them

When you tell Claude "The codebase has inconsistent color usage," you're giving it information that naturally triggers an instinct to improve consistency. But in a working system, consistency with an imperfect pattern is better than introducing a different pattern alongside it.

**Example: Color System Inconsistency**

Project 1 Code Analysis reveals:
```
- Dashboard uses: bg-amber-100, text-amber-800
- Forms use: bg-ring-100, text-ring-800
- Cards use: bg-gray-50, text-gray-900

This is inconsistent! Multiple color systems.
```

**WRONG interpretation** (Claude fixes it):
"I should update all cards to use amber-100 for consistency."
- Result: Cards now look different than before
- User reports: "Something changed visually"
- Real problem: Two different color palettes exist, changing one breaks existing look

**RIGHT interpretation**:
"The app uses THREE separate color palettes. When I add a NEW card, I must determine which palette it belongs to and match EXACTLY. I will NOT change existing colors."
- Result: New card follows one of three existing patterns
- User experiences: Consistent NEW behavior
- Real improvement: New code doesn't add a fourth palette

**The Key Distinction**:
- **Knowledge**: "There are 3 color palettes in this codebase"
- **Dangerous Action**: "I should consolidate to 1 palette"
- **Safe Action**: "I should identify which palette a new element belongs to and copy it exactly"

---

### 1.2 The Difference Between "Understand This Pattern" vs "Apply This Pattern"

These sound similar but are fundamentally different instructions that trigger completely different behaviors in Claude.

**DANGEROUS**: "There's a form pattern used in SubmitPage. Here's what it does: [description]. Create a new form page for LoanIssues."

Claude reads the description, thinks about the pattern, and applies its *understanding* of what makes a good form. This is creative but risky because Claude might "improve" the pattern while implementing it.

**SAFE**: "There's a form pattern used in SubmitPage. Copy the exact file structure: identical imports, identical state declarations, identical validation logic. Only change the field names and API endpoint."

The second instruction sets a constraint: exact replication. Claude copies rather than interprets.

**Translation Guide**:

| Dangerous Framing | Safe Framing |
|------------------|--------------|
| "Understand how forms work in this app" | "Replicate the form in SubmitPage.tsx line-for-line, changing only field names" |
| "Learn the color system and use it" | "Find the most common color pattern and copy the exact className strings" |
| "Fix the role system inconsistency" | "Find all existing role constants in ROLES.ts and use only those strings" |
| "Make the component reusable" | "Copy the component structure, add a props parameter for the variant" |
| "Improve the state management" | "Extend the existing context by adding a new optional field to the provider" |

---

### 1.3 How to Frame "This Is a Bad Pattern" Without Triggering Refactoring

The most dangerous instruction is one that tells Claude something is "bad" or "broken" or "inconsistent" without also telling it exactly what NOT to do.

**BROKEN INSTRUCTION**:
```
"The role system is a mess. Roles are defined in three places:
1. SimpleAuthContext.tsx line 27
2. Dashboard.tsx line 15
3. Submission.ts line 88

All three define slightly different role lists."
```

Claude reads this and thinks: "I should consolidate roles to one place. Let me extract them all into roles.ts."

Claude then refactors, and the refactoring goes:
- Extracts roles correctly ✓
- Updates imports in some files ✗ (misses one)
- Other file still uses old location ✗
- Type checking passes (backwards compatible) ✓
- But runtime now has two role sources (new and old) ✗
- Auth logic checks new location, form checks old location
- Users with certain roles suddenly can't access forms
- Regression

**SAFE INSTRUCTION**:
```
"The role system defines roles in three places. When adding role checks:
1. DO NOT consolidate them
2. DO NOT refactor existing role definitions
3. INSTEAD: Search for ALL existing role constants: grep -r "ROLES\." src/
4. Use ONLY the role strings that appear in multiple places already
5. When adding new role checks, copy the exact condition from an existing check
6. If a new role is needed, ask the user first rather than creating it yourself"
```

The second instruction is explicit: you can identify fragmentation, but your job is to MATCH it, not FIX it.

---

### 1.4 Critical Distinction: OBSERVE Existing Patterns → MATCH Them in New Code (Even if They're "Wrong")

This is the core principle that prevents breakage.

When you write analysis like "SubmitPage and LoanIssueFormPage are 65% duplicated," Claude's mind naturally goes:

```
Observe: "These are duplicated"
↓
Judge: "Duplication is bad"
↓
Act: "I should refactor to remove duplication"
↓
BREAK: Refactoring introduces subtle bugs
```

Instead, you want:

```
Observe: "These are duplicated (both use processFiles, both use useFormSubmission, etc.)"
↓
Match: "When I create a NEW form page, I will copy the exact same patterns"
↓
Extend: "I will add new fields but keep the identical validation, submission, and state logic"
↓
SAFE: New code uses proven patterns
```

**The Phrase That Matters**:

Instead of: "Fix the duplication"
Use: "Follow the same pattern from SubmitPage, even though it's duplicated elsewhere"

Instead of: "Consolidate the inconsistency"
Use: "Match the most common approach you find in the codebase"

Instead of: "Refactor for consistency"
Use: "Replicate the existing approach exactly, even if it could be better"

---

## 2. Defensive Instruction Patterns

For **every category of instruction** in the skill, show the dangerous version and the SAFE version. This is your reference sheet when writing prompts to Claude.

### 2.1 Component & Layout Patterns

#### DANGEROUS:
"There are several button components scattered across the codebase. Extract a shared Button component to consolidate them."

Why it breaks: Claude extracts the component, updates some imports, misses others. Different parts of the app now import from different places.

#### SAFE:
"There are button components in ProductSupportDashboard.tsx (line 87) and TicketCard.tsx (line 156). When adding a new button, find which of these two patterns matches your use case and copy the className exactly. Do NOT create a new pattern or extract them to a shared file."

---

#### DANGEROUS:
"Make the form component reusable so it can be used for both Submit and LoanIssue submissions."

Why it breaks: "Reusable" means different things. Claude might add complex prop logic that doesn't account for edge cases.

#### SAFE:
"Copy the form structure from SubmitPage.tsx exactly. Keep the same imports, same state declarations, same validation functions. Add a props parameter for roleSpecificFields but keep the success screen, error handling, and file upload logic identical."

---

#### DANGEROUS:
"Create a card component wrapper for all the dashboard cards that are currently inline."

Why it breaks: Inline cards might have subtle differences that become apparent only after extraction.

#### SAFE:
"Find all cards in the dashboard (search 'rounded-lg border shadow-sm'). Document their common className pattern. When styling a new dashboard element, use the most common className exactly. Do NOT extract them to a component unless explicitly asked."

---

### 2.2 Styling, Colors, and Visual Design

#### DANGEROUS:
"The UI uses inconsistent colors. Create a color palette configuration and apply it everywhere."

Why it breaks: "Everywhere" means refactoring existing components, which can introduce subtle visual regressions.

#### SAFE:
"Document the color palette used in existing components:
- Status badges: amber-100/amber-800, ring-100/ring-800, green-100/green-800
- Background: bg-white, bg-gray-50, bg-ring-50
When adding new elements, use ONE of these exact color pairs. Copy the complete className from an existing element that uses it. Do NOT introduce new color values."

---

#### DANGEROUS:
"Fix the inconsistent spacing. The app uses gap-2, gap-3, gap-4, gap-6. Standardize to gap-4."

Why it breaks: Changing spacing in existing components changes their visual appearance. Users notice and report it as a regression.

#### SAFE:
"The app uses multiple spacing values: gap-2 (8px), gap-3 (12px), gap-4 (16px), gap-6 (24px). Each is used for specific layout patterns. When adding new spacing, identify the MOST COMMON value (likely gap-4) and use it. Copy the complete spacing className from a similar existing element rather than inventing new spacing values."

---

#### DANGEROUS:
"The typography is all over the place. Headers use text-2xl and text-3xl. Standardize them."

Why it breaks: Changing text sizes breaks visual hierarchy in existing components. What looked like a subheading now looks like a heading.

#### SAFE:
"Document the heading hierarchy in use:
- Page titles: text-3xl font-bold
- Section headers: text-2xl font-bold
- Subsection headers: text-xl font-semibold
When adding headers, identify the hierarchy level of your new header and use the exact size from an existing header at that level. Do NOT adjust sizes in existing headers."

---

### 2.3 Role Systems and Access Control

#### DANGEROUS:
"The role system has confusion between 'sm' and 'product_support'. Clean this up."

Why it breaks: Role changes require coordinated updates across multiple files. Missing even one location creates security holes or access failures.

#### SAFE:
"The existing role system uses these constants: ROLES.SM, ROLES.PRODUCT_SUPPORT, ROLES.TECH_SUPPORT. These are defined in src/types/roles.ts. When adding role checks:
1. ONLY use these exact role constants
2. Search for where each role is checked in the codebase
3. When adding a NEW role check, copy the exact condition from an existing check for a similar permission
4. Do NOT create new role names or aliases
5. If a new role is truly needed, ask the user first"

---

#### DANGEROUS:
"Some pages check role differently. Create a single roleCheckService that all pages use."

Why it breaks: Extracting role checks can change behavior subtly. For example, if one check uses `.includes()` and another uses `===`, extracting them incorrectly changes security.

#### SAFE:
"When adding role-based access control, find an existing page that protects the same data type. Copy its role check exactly. If the new route needs different permissions, ask the user how to reconcile the difference rather than creating a new check yourself."

---

#### DANGEROUS:
"Refactor the role names to be more semantic (e.g., 'support_admin' instead of 'sm')."

Why it breaks: Role names are used in localStorage, session tokens, database queries, and auth contexts. Changing them breaks every user's session.

#### SAFE:
"When checking roles, use ONLY the exact string values that currently exist in the auth context. Even if the names seem unclear, using the exact existing values guarantees compatibility. Do NOT rename roles."

---

### 2.4 Database Schemas and Data Models

#### DANGEROUS:
"The Ticket type has optional fields that should be required. Clean up the data model."

Why it breaks: Making optional fields required breaks existing code that checks for optional values. Queries that assume the field might be null now fail.

#### SAFE:
"Document the Ticket type exactly as it exists, including which fields are optional and why. When adding new ticket fields:
1. If the field applies to all tickets, add it as OPTIONAL first (backward compatibility)
2. Copy the field pattern from an existing optional field
3. Do NOT change required/optional status of existing fields
4. When using the field, check if it's present before accessing it"

---

#### DANGEROUS:
"The schema is inconsistent. Some IDs use uuid, some use number. Standardize on uuid."

Why it breaks: Changing primary key types requires migrating all data, updating all foreign key references, and coordinating with database constraints.

#### SAFE:
"When adding new entities, use the same ID type as existing entities of that type. If the system mixes ID types (some uuid, some number), don't try to standardize. Instead, use the ID type appropriate for the entity category."

---

#### DANGEROUS:
"Consolidate the timestamp handling. Some records use created_at, some use createdAt."

Why it breaks: Timestamp field names are hardcoded in queries. Changing them silently breaks queries.

#### SAFE:
"Document the exact timestamp field names used by each table. When adding new timestamp fields, use the exact naming convention that table already uses. Do NOT change naming conventions in existing tables."

---

### 2.5 State Management (Context, Hooks, Redux)

#### DANGEROUS:
"The auth state is scattered between Context and localStorage. Consolidate it into a single source of truth."

Why it breaks: State synchronization between Context and localStorage is fragile. If you consolidate them, you can miss edge cases where localStorage is the authority (e.g., page refresh).

#### SAFE:
"Document how auth state currently flows:
- Context holds: currentUser
- localStorage holds: auth token
- Session storage holds: [anything else?]
When adding new auth-related state, check where the source of truth currently lives and add to that location. Do NOT consolidate existing state sources unless explicitly asked and reviewed."

---

#### DANGEROUS:
"The useTickets hook is too large. Extract the filtering logic into a separate hook."

Why it breaks: Consumers of useTickets depend on its current return type. Extracting logic changes the hook's contract.

#### SAFE:
"If you need to add filtering functionality to useTickets:
1. Check the current return type
2. Add new filter methods as additional return properties (additive, not breaking)
3. Keep all existing methods unchanged
4. Do NOT remove or rename existing methods
5. Do NOT restructure the return object"

---

#### DANGEROUS:
"Add memoization to these hooks to prevent unnecessary re-renders."

Why it breaks: Adding memoization changes when components re-render. Dependent components might miss updates or show stale state.

#### SAFE:
"If performance is an issue:
1. Measure before optimizing (use React DevTools Profiler)
2. Document exactly which re-renders are excessive
3. Only memoize if the developer agrees it won't change update behavior
4. Test that all components still update when data changes
5. This is not a 'add feature' task—it's a separate optimization that needs verification"

---

### 2.6 Routes and Navigation

#### DANGEROUS:
"Create a centralized route configuration to replace the scattered Route elements in App.tsx."

Why it breaks: Centralizing routes changes how they're evaluated. If the new config is slightly wrong, route matching breaks.

#### SAFE:
"Document the current route structure in App.tsx. When adding a new route:
1. Add it to App.tsx alongside existing routes using the exact same pattern
2. Copy the route syntax from a similar existing route
3. Do NOT consolidate routes into a separate config file
4. Do NOT change how existing routes are defined"

---

#### DANGEROUS:
"Refactor navigation to use a route map object instead of hardcoded paths."

Why it breaks: Hardcoded paths are scattered across the app. Changing how they're defined can cause some parts to update and others not to.

#### SAFE:
"When adding navigation links, use the exact same pathname format as existing links to the same destination. Search for existing navigation to [destination], copy the path string exactly. Do NOT create new path formats."

---

### 2.7 Form Validation

#### DANGEROUS:
"Create a validation schema library to consolidate validation logic."

Why it breaks: Validation libraries often change error message formats or validation rules slightly. Consolidating can introduce unexpected failures.

#### SAFE:
"When adding form validation:
1. Find an existing form with similar fields
2. Copy its validation function exactly
3. Adapt the field-specific checks but keep the overall validation structure
4. Use the same error message strings as existing similar validations
5. Do NOT create a validation library unless explicitly asked"

---

#### DANGEROUS:
"Improve error messages to be more descriptive and helpful."

Why it breaks: Error message text is sometimes hardcoded into error handling logic. Changing messages can break tests or user workflows that depend on specific text.

#### SAFE:
"When adding error handling, use error message patterns from existing similar validations. Copy the exact message text from an existing validation and adapt only the specific field name."

---

### 2.8 Type Definitions and TypeScript

#### DANGEROUS:
"Add strict TypeScript typing to improve code safety. Add non-null assertions, narrow types, make optional fields required."

Why it breaks: Making optional types required breaks code that checks if they exist. Non-null assertions hide potential null pointer issues.

#### SAFE:
"When adding new types:
1. Copy the structure of similar existing types
2. Keep optional fields optional (maintain backward compatibility)
3. Don't change existing type definitions
4. Add new fields to existing types instead of creating new types
5. Do NOT add strict typing to existing code unless explicitly requested as a separate refactoring task"

---

#### DANGEROUS:
"Use discriminated unions to make the state machine more type-safe."

Why it breaks: Changing type structures requires updating all consumers. Discriminated unions change how the type is used in every component.

#### SAFE:
"When extending a type to support a new variant, document the current type structure and add the new variant alongside existing ones. Keep the same overall structure; don't change how existing variants are used."

---

### 2.9 API Calls and Service Integration

#### DANGEROUS:
"Create an API client class to wrap all Supabase/Firebase calls and improve consistency."

Why it breaks: API client abstractions can hide edge cases or rate limiting logic. Wrapping existing calls requires coordinating all call sites.

#### SAFE:
"When calling external services:
1. Find an existing service call for a similar operation
2. Copy the call pattern exactly (same error handling, same parameters)
3. Do NOT create a service wrapper unless the existing pattern proves insufficient
4. Do NOT change how existing services are called"

---

#### DANGEROUS:
"Migrate from Firebase Storage to S3 to improve cost efficiency."

Why it breaks: Storage migrations require changing field names in the database, updating all upload/download code, handling concurrent access during migration.

#### SAFE:
"When adding file upload capability:
1. Identify the existing storage system (Firebase, S3, Supabase, etc.)
2. Use ONLY that existing storage system
3. Do NOT add a competing storage system
4. If the current system is insufficient, ask the user before considering alternatives"

---

### 2.10 Dependencies and Packages

#### DANGEROUS:
"Add these useful libraries to improve development speed: [list of 5 packages]."

Why it breaks: New dependencies add to bundle size, can have security vulnerabilities, and might conflict with existing packages.

#### SAFE:
"Before adding any dependency:
1. Search the codebase to see if an existing dependency already solves this problem
2. Check package.json for similar packages
3. If a problem exists that no existing dependency solves, ask the user for permission before adding a package
4. Only add packages that are explicitly requested or discussed with the user"

---

## 3. The "Match, Don't Fix" Principle

### 3.1 Why Consistency With Imperfect Patterns is Better Than Introducing "Better" Patterns Alongside Old Ones

This is the core trade-off that Workflow Guardian optimizes for.

**Scenario**: Project has 2 form patterns:
- SubmitPage: Uses `useState` with separate state variables
- ModifySubmissionPage: Uses `useReducer` with a reducer function

Both work. Both are valid. But they're inconsistent.

**The Temptation**:
"I should consolidate these to use one pattern. useReducer is more scalable, so I'll migrate everything to useReducer."

**The Consequence**:
- SubmitPage now uses useReducer
- But the reducer logic is slightly different from ModifySubmissionPage
- The migration misses some edge case SubmitPage had
- SubmitPage breaks for certain inputs
- You've now created a WORSE situation: two broken patterns instead of one working pattern

**The Right Choice**:
"The codebase uses two patterns. When adding a NEW form:
1. Check which pattern is more common (or more recent)
2. Use EXACTLY that pattern, even if the other is theoretically better
3. Do NOT consolidate patterns"

**Why this works**:
- New code uses a proven, tested pattern
- Existing code continues working unchanged
- If you want to migrate, that's a separate project (handled explicitly)

**Real Example from Projects**:

Project 1 had 3 different ways to handle authentication:
1. SimpleAuthContext: password-based, localStorage
2. GoogleDriveContext: OAuth flow
3. LoginPage: hardcoded password check

Instead of "fixing" this by consolidating, Workflow Guardian would say:
"These three auth mechanisms exist. When adding auth checks, use the existing SimpleAuthContext since that's the most used. Do NOT try to consolidate them. If you want to unify auth, that's a separate refactoring project."

---

### 3.2 Why a Codebase With ONE Imperfect Pattern is Better Than a Codebase With TWO Patterns (One "Bad" and One "Good")

This principle prevents the "better pattern alongside old pattern" trap.

**Scenario**: Old form code uses:
```typescript
const [formData, setFormData] = useState<FormData>({...});
```

You think: "This is missing TypeScript strictness. I should add it."

**BAD EXECUTION**:
You create a NEW form with strict typing:
```typescript
interface FormData {
  field1: string;
  field2: number;
  // ... field3 is required, not optional
}
const [formData, setFormData] = useState<FormData>({...});
```

**Result**:
- Old form: flexible typing
- New form: strict typing
- Developers now have TWO ways to write forms
- Next developer picks whichever they like, code diverges further
- Maintenance nightmare: two implementations of the same concept

**GOOD EXECUTION**:
You replicate the OLD pattern:
```typescript
const [formData, setFormData] = useState<FormData>({...});
// Same pattern as existing form, keeps codebase consistent
```

Later, when you explicitly want to refactor ALL forms to use strict typing, you do it as ONE project, all at once.

**The Principle**:
```
Consistency with imperfect pattern (1 pattern, N implementations)
>
Two patterns, each perfect (but competing)
```

---

### 3.3 When (and ONLY When) Refactoring Is Acceptable

The Workflow Guardian skill EXPLICITLY PREVENTS refactoring when adding features. Refactoring is only okay if:

1. **User explicitly asks for it** — "Extract this shared form component"
2. **It's a separate task** — Done BEFORE feature work, not during
3. **It's scoped and understood** — Changes are documented, tests run, manual verification happens
4. **It's not disguised as feature work** — You're not adding a feature while refactoring

**Example Flow**:

**User Request**: "Add a new role called 'supervisor' to the app"

**BAD PLAN**:
- Phase 1: Add 'supervisor' role to auth context
- Phase 1.5: Oh, I should also refactor the role system while I'm at it
- Phase 2: Extract roles to roles.ts
- Phase 3: Update all role checks

**GOOD PLAN**:
- Phase 1: Add 'supervisor' role exactly where existing roles are defined
- Phase 1: Copy existing role checks for similar permissions
- Phase 1: Test that supervisor role works
- [LATER, separate request]: User says "Let's refactor the role system"
- [SEPARATE PROJECT]: Extract roles.ts, coordinate with all files, test thoroughly

---

## 4. The "Observer Mode" Protocol

Before Claude makes ANY changes to the codebase, it should spend time in "Observer Mode" — gathering information about patterns WITHOUT forming opinions about quality.

### 4.1 How to Observe Without Judging

When analyzing the codebase, use neutral language that describes what exists without evaluating it.

**DANGEROUS ANALYSIS** (contains judgment):
"The codebase has:
- Messy role handling (scattered across 3 files)
- Duplicated form validation logic
- Inconsistent spacing values
- Poor component reusability"

This triggers Claude's improvement instinct.

**SAFE ANALYSIS** (neutral, descriptive):
"The codebase structure:
- Role definitions exist in: SimpleAuthContext.tsx (line 27), Dashboard.tsx (line 15), and Submission.ts (line 88)
- Form validation patterns used: inline validation in SubmitPage.tsx and LoanIssueFormPage.tsx
- Spacing values in use: gap-2, gap-3, gap-4, gap-6 (sorted by frequency: gap-4 most common)
- Components used in multiple places: Button (3 locations), Input (2 locations), Card (inline)"

This describes facts without triggering improvement.

---

### 4.2 How to Record Patterns As-Is (Not How They "Should" Be)

When documenting patterns, record them exactly as they exist, including any quirks or inconsistencies.

**WRONG DOCUMENTATION**:
"The form pattern should:
1. Use React hooks for state
2. Validate on submit
3. Show errors inline
4. Display success screen after submission"

This is prescriptive. Claude will apply these "shoulds" to new code.

**RIGHT DOCUMENTATION**:
"Forms in the codebase follow this pattern:
1. SubmitPage.tsx uses useState with separate variables (lines 35-42)
2. LoanIssueFormPage.tsx uses useState with combined object (lines 40-50)
3. Validation happens in both places: one uses a validator function, one uses inline checks
4. Error display varies: some use toast, some use inline error messages
5. Success screen: both show a green checkmark and reload button
6. When creating new form: match the pattern from SubmitPage exactly"

This records actual behavior without prescribing change.

---

### 4.3 How to Suppress the Instinct to Improve/Optimize/Refactor

This is the most important part of Observer Mode. When Claude sees room for improvement, you need to redirect that energy.

**Refactoring Instinct Redirect**:

When Claude thinks: "I should extract the shared validation logic"

Instead say: "The validation logic appears in multiple forms. When adding validation to a new form, search for an existing form with similar validation and copy it exactly. Do NOT extract it to a shared utility."

**Optimization Instinct Redirect**:

When Claude thinks: "I should add memoization to prevent re-renders"

Instead say: "If performance is a concern, we'll address it separately. For now, when adding hooks or state, follow the existing patterns even if they don't use memoization."

**Consistency Instinct Redirect**:

When Claude thinks: "I should standardize the color palette"

Instead say: "The app uses multiple color palettes. Your job is to identify which palette a new element belongs to and match it exactly. Do NOT standardize the palette."

**The Pattern**:
```
When Claude thinks: "I should [improve/optimize/consolidate/extract/standardize]"
Redirect to: "Follow the existing pattern exactly"
```

---

### 4.4 How to Treat Existing Code as the Source of Truth, Not the Ideal

The core of Observer Mode is treating existing code as a spec, not as a draft.

**WRONG MINDSET**:
"Here's the existing code. It's not perfect, but it works. Can you improve it while adding the new feature?"

This activates improvement mode.

**RIGHT MINDSET**:
"Here's the existing code. This IS the spec. When adding new code, match the spec exactly."

This activates matching mode.

**Instruction Template**:
"The existing [component/form/hook/service] uses this pattern: [code snippet]. When adding a new [component/form/hook/service], match this pattern exactly. If the pattern seems suboptimal, that's okay—consistency matters more than perfection."

---

## 5. Instruction Language Guide

### 5.1 Words to AVOID in the Skill

These words trigger Claude's improvement instinct. Remove them from skill instructions:

| Avoid | Why | Safe Alternative |
|-------|-----|-------------------|
| **fix** | Implies something is broken | "follow the existing pattern" |
| **improve** | Triggers optimization instinct | "match the existing approach" |
| **refactor** | Triggers restructuring instinct | "replicate the structure" |
| **optimize** | Triggers performance improvement | "use the same pattern" |
| **clean up** | Triggers simplification instinct | "keep the structure as-is" |
| **modernize** | Triggers version upgrade instinct | "use the existing approach" |
| **consolidate** | Triggers extraction instinct | "replicate the existing pattern" |
| **extract** | Triggers DRY principle instinct | "copy the pattern from an existing component" |
| **DRY** | Triggers de-duplication | "replicate for consistency" |
| **bad** / **ugly** | Triggers improvement | "different from existing code" |
| **should be** | Prescriptive, triggers change | "currently is" |
| **inconsistent** | Triggers standardization | "uses multiple approaches" |

---

### 5.2 Words to USE Instead

Replace dangerous words with safe alternatives:

| Safe Word/Phrase | Context | Example |
|------------------|---------|---------|
| **match** | Replicating patterns | "Match the form pattern from SubmitPage.tsx" |
| **follow** | Using existing approaches | "Follow the authentication pattern used in SimpleAuthContext" |
| **replicate** | Copying structure | "Replicate the button styling from existing buttons" |
| **mirror** | Imitating exactly | "Mirror the success screen structure" |
| **copy pattern from** | Explicit duplication | "Copy the validation pattern from LoginPage" |
| **align with** | Making consistent | "Align with the existing color palette" |
| **extend** | Adding to existing | "Extend the Ticket type with a new optional field" |
| **add to** | Appending without changing | "Add a new optional field to the User context" |
| **use the existing** | No change to what works | "Use the existing role constants" |
| **keep as-is** | Preserve current | "Keep the current state structure as-is" |
| **document** | Record actual behavior | "Document the current button patterns" |
| **identify** | Find existing things | "Identify existing form validation patterns" |
| **search for** | Look before changing | "Search for existing date formatting logic" |

---

### 5.3 Phrase Templates That Are Safe to Use

When framing instructions, use these safe templates:

**For Component Patterns**:
```
"When adding a new [component], find an existing [similar component] and copy its:
- Import structure exactly
- Props interface structure
- JSX element structure
- Styling className exactly
Do NOT create new patterns."
```

**For State Management**:
```
"When adding state for [concern], examine the existing [context/hook] and:
- Extend it with new optional properties, or
- Create a new context following the exact same pattern
Do NOT change existing context structure."
```

**For Styling**:
```
"When styling a new [element], find an existing [similar element] that uses the same pattern and copy:
- The color values exactly
- The className string exactly
- The spacing values exactly
Do NOT introduce new colors or spacing."
```

**For API Calls**:
```
"When calling [service], find an existing call to the same service and:
- Copy the error handling pattern
- Copy the parameter structure
- Copy the return value handling
Do NOT create new calling conventions."
```

**For Roles/Permissions**:
```
"When implementing [permission], find an existing permission that's similar and:
- Use the exact same role constants
- Use the exact same permission check logic
- Use the exact same error messages
Do NOT create new role values or permission types."
```

---

### 5.4 Warning Labels for Instructions That Could Be Misinterpreted

Some instructions are so close to triggering improvement mode that they need explicit warnings.

**When you MUST mention a problem**, use this format:

```
⚠️ WARNING - This instruction mentions a problem. Do NOT try to fix it.

[Problem description]

DO:
- Observe that this pattern exists
- Match it when adding new code
- Document it as-is

DON'T:
- Refactor existing code
- Consolidate the variations
- "Fix" the problem while adding features
```

**Examples**:

⚠️ WARNING - The role system has inconsistent names
```
Role names appear in multiple places:
- SimpleAuthContext uses 'sm', 'product_support'
- Dashboard uses 'sm', 'tech_support_team'
- These don't fully align

When adding role checks:
- DO: Use ONLY the role strings you find in existing checks
- DON'T: Create a unified role system or rename existing roles
```

⚠️ WARNING - Forms have duplicated validation logic
```
SubmitPage and LoanIssueFormPage both validate attachments similarly.

When adding a form:
- DO: Copy the validation from whichever form is most similar
- DON'T: Extract shared validation to a utility
```

---

## 6. The "New Code Only" Boundary

The clearest rule in Workflow Guardian: This skill only governs NEW code. It NEVER tells Claude to modify existing working code.

### 6.1 How to Add Code Next to Existing Code Without Modifying It

**Pattern 1: Add to Existing File Without Changing Existing Code**

```typescript
// SubmitPage.tsx - EXISTING CODE (UNCHANGED)
export function SubmitPage() {
  // ... existing implementation
}

// SubmitPage.tsx - NEW CODE (ADDED BELOW)
export function SubmitPageForNewFeature() {
  // New variant that extends functionality
  // but SubmitPage itself is unchanged
}
```

**Pattern 2: Extend Type Without Changing Existing Usage**

```typescript
// BEFORE - existing type
interface Ticket {
  id: string;
  title: string;
  description: string;
  status: 'open' | 'claimed' | 'resolved';
}

// AFTER - extended type (all new fields optional for backward compatibility)
interface Ticket {
  id: string;
  title: string;
  description: string;
  status: 'open' | 'claimed' | 'resolved';
  priority?: 'low' | 'medium' | 'high';  // NEW, optional
  assignedTo?: string;                    // NEW, optional
}

// Existing code still works because it doesn't require new fields
```

**Pattern 3: Add Routes Without Modifying Existing Routes**

```typescript
// App.tsx - EXISTING ROUTES (UNCHANGED)
<Routes>
  <Route path="/login" element={<LoginScreen />} />
  <Route path="/admin" element={<AdminView />} />
</Routes>

// App.tsx - NEW ROUTES (ADDED)
<Routes>
  <Route path="/login" element={<LoginScreen />} />
  <Route path="/admin" element={<AdminView />} />
  <Route path="/analytics" element={<AnalyticsPage />} />  // NEW
</Routes>
```

---

### 6.2 How to Extend Types Without Breaking Existing Type Usage

**Rule**: When extending a type, add optional fields. Never remove or change existing fields.

```typescript
// SAFE: Extending a type
interface User {
  id: string;
  email: string;
  role: 'admin' | 'user';
  department?: string;        // NEW optional field
  supervisorId?: string;      // NEW optional field
}

// Existing code that uses User still works:
const user: User = { id: '123', email: 'user@example.com', role: 'user' };
// ^ No error, because new fields are optional

// NEW CODE: Can use the new fields
if (user.department) {
  // handle department
}

// UNSAFE: Changing a type
interface User {
  id: string;
  email: string;
  role: 'admin' | 'user' | 'supervisor';  // CHANGED: added new role
  department: string;                      // CHANGED: no longer optional
}
// ^ Breaks existing code that doesn't set department or expects only 3 roles
```

---

### 6.3 How to Add State Without Restructuring Existing State

**Pattern 1: Extend existing context**

```typescript
// EXISTING: AuthContext provides user and login/logout
const AuthContext = createContext<{
  user: User | null;
  login: (creds) => Promise<void>;
  logout: () => void;
}>({...});

// NEW: Add optional field without breaking context
const AuthContext = createContext<{
  user: User | null;
  login: (creds) => Promise<void>;
  logout: () => void;
  theme?: 'light' | 'dark';  // NEW, optional
}>({...});

// Existing consumers still work:
const { user, login, logout } = useAuth();
// ^ theme is ignored, no error

// NEW CODE: Can use theme
const { user, theme } = useAuth();
```

**Pattern 2: Create new context without touching existing contexts**

```typescript
// AuthContext - UNCHANGED
export const AuthContext = createContext({...});

// NEW: Create new context alongside existing
export const ThemeContext = createContext({...});

// App.tsx
<AuthProvider>
  <ThemeProvider>
    <App />
  </ThemeProvider>
</AuthProvider>
```

---

### 6.4 How to Add Styles Without Changing Existing Styles

```typescript
// EXISTING: Card component styled
<div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
  {/* content */}
</div>

// NEW: Add similar card with exact same styling
<div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
  {/* different content, same styling */}
</div>

// WRONG: New card with slightly different styling
<div className="bg-white rounded-lg border border-gray-300 shadow-md p-5">
  {/* This looks different! */}
</div>
```

---

### 6.5 How to Add Behavior Without Changing Existing Behavior

**Pattern**: Additive hooks that extend existing hooks

```typescript
// EXISTING: useTickets hook
export function useTickets() {
  const [tickets, setTickets] = useState([]);
  return {
    tickets,
    claimTicket: (id) => { /* ... */ },
    resolveTicket: (id) => { /* ... */ },
  };
}

// NEW: Extend with new method, don't change existing methods
export function useTickets() {
  const [tickets, setTickets] = useState([]);
  return {
    tickets,
    claimTicket: (id) => { /* ... */ },      // UNCHANGED
    resolveTicket: (id) => { /* ... */ },    // UNCHANGED
    assignTicket: (id, user) => { /* ... */ },  // NEW METHOD
  };
}

// Existing code still works:
const { tickets, claimTicket } = useTickets();
// ^ New method doesn't break existing usage
```

---

## 7. Real Examples of How This Goes Wrong (And How to Fix It)

### 7.1 Example: Form Component Consolidation

**WHAT HAPPENED** (Project 1):
Claude was asked to "add a new form for loan issues" and saw that SubmitPage existed with 65% similar code. Claude consolidated them.

```typescript
// BEFORE: Two separate forms
// SubmitPage.tsx (390 lines)
// LoanIssueFormPage.tsx (603 lines)

// AFTER: Attempted consolidation
// SubmissionFormContainer.tsx (new shared component)
// SubmitPage.tsx (refactored)
// LoanIssueFormPage.tsx (refactored)

// BREAK:
// - SubmitPage lost a piece of validation logic for LSQ URLs
// - Couldn't submit for 3 days
// - Rollback required
```

**HOW TO PREVENT IT**:

**DANGEROUS INSTRUCTION**:
"Consolidate SubmitPage and LoanIssueFormPage. They're 65% duplicated. Extract shared logic into a FormContainer."

**SAFE INSTRUCTION**:
"SubmitPage and LoanIssueFormPage are structurally similar but serve different roles. When adding a NEW form (not modifying existing ones):
1. Identify whether it's more like SubmitPage or LoanIssueFormPage
2. Copy the form structure from whichever is most similar
3. Change only the field names and API endpoint
4. Do NOT refactor existing forms
5. Do NOT create a FormContainer unless the user explicitly requests refactoring as a separate project"

---

### 7.2 Example: Role System Cleanup

**WHAT HAPPENED** (Project 1):
Claude noticed roles were defined in 3 places with inconsistent names. Claude extracted them to roles.ts and updated imports.

```typescript
// BEFORE: Scattered role definitions
// SimpleAuthContext.tsx: ROLES = ['sm', 'product_support', 'tech_support_team']
// Dashboard.tsx: if (role === 'sm') { ... }
// Submission.ts: const SM_ROLE = 'sm'; if (role === SM_ROLE) { ... }

// AFTER: Attempted consolidation
// roles.ts: export const ROLES = { SM: 'sm', ... }
// SimpleAuthContext.tsx: import { ROLES }; // UPDATED
// Dashboard.tsx: import { ROLES }; // UPDATED
// Submission.ts: // FORGOTTEN!

// BREAK:
// - Submission.ts still uses const SM_ROLE = 'sm'
// - SimpleAuthContext.tsx checks import { ROLES }
// - Two role sources of truth
// - Auth works in one place, not the other
```

**HOW TO PREVENT IT**:

**DANGEROUS INSTRUCTION**:
"The role system has confusion between 'sm' and 'tech_support'. Fix it."

**SAFE INSTRUCTION**:
"Roles are defined in multiple places:
- SimpleAuthContext.tsx line 27: 'sm', 'product_support', 'tech_support_team'
- Dashboard.tsx line 15: checks against specific role strings
- Submission.ts line 88: uses SM_ROLE constant

When adding role checks:
1. Search the codebase for existing role checks
2. Use the exact role strings from an existing check
3. Copy the condition structure exactly
4. Do NOT consolidate roles to a single file
5. If asked to fix role system inconsistency, that's a separate refactoring project"

---

### 7.3 Example: File Upload System Unification

**WHAT HAPPENED** (Project 1):
Claude noticed Firebase Storage for some uploads and Google Drive for others. Claude tried to unify on Google Drive.

```typescript
// BEFORE: Two storage systems in use
// imageUpload.ts: uploadToFirebase()
// fileUpload.ts: uploadToDrive()
// submissions.ts: mix of both

// AFTER: Attempted unification
// fileUpload.ts: changed to use ONLY Drive API
// submissions.ts: updated to call uploadToDrive for all uploads

// BREAK:
// - Old code still referenced Firebase Storage
// - New submissions went to Drive
// - Old submissions stayed on Firebase
// - Schema now has both attachmentUrl and attachmentDriveId
// - Query logic broke because it didn't check both fields
// - Recovery: 2 days of debugging
```

**HOW TO PREVENT IT**:

**DANGEROUS INSTRUCTION**:
"Migrate from Firebase Storage to Google Drive for consistency."

**SAFE INSTRUCTION**:
"The app currently uses TWO file storage systems:
- Firebase Storage: for image attachments (used in SubmitPage, Dashboard)
- Google Drive: for document uploads (used in LoanIssueForm, Reports)

When adding file upload functionality:
1. Identify which storage system is used for similar existing uploads
2. Use THAT SAME SYSTEM for your new upload
3. Do NOT add a third storage system
4. Do NOT migrate between storage systems while adding features
5. If migration is needed, that's a separate project requiring data migration planning"

---

### 7.4 Example: TypeScript Strictness Addition

**WHAT HAPPENED** (Project 1):
Claude saw optional fields in types and added strict non-null checking while implementing a feature.

```typescript
// BEFORE: Optional field
interface Ticket {
  id: string;
  title: string;
  description: string;
  priority?: string;  // Optional
}

// Feature: Add priority filtering
// Claude thought: "Priority should be required for filtering"
// Claude changed to: priority: string;

// BREAK:
// - Existing code that creates tickets without priority broke
// - Tests that don't set priority broke
// - Feature worked, but 10 other places broke
```

**HOW TO PREVENT IT**:

**DANGEROUS INSTRUCTION**:
"When implementing priority filtering, add strict types to ensure all data is valid."

**SAFE INSTRUCTION**:
"When adding a priority filter:
1. Examine the Ticket type: priority is optional
2. Handle the optional case: check if priority exists before filtering
3. Do NOT change the type signature
4. Do NOT make optional fields required
5. Maintain backward compatibility with existing tickets that don't have priority set"

---

### 7.5 Example: State Management "Improvement"

**WHAT HAPPENED** (Project 1):
Claude saw useState scattered across components and thought useReducer would be better. Claude refactored while adding a feature.

```typescript
// BEFORE: Using useState
const [formData, setFormData] = useState({ title: '', description: '' });

// Feature: Add validation state
// Claude thought: "I should use useReducer for complex state"
// Claude changed to: const [state, dispatch] = useReducer(reducer, initialState)

// BREAK:
// - Components that set formData with setFormData now fail
// - dispatch() has different semantics
// - Event handlers changed: onChange -> dispatch({ type: 'SET_TITLE', payload })
// - Existing onChange handlers in tests broke
```

**HOW TO PREVENT IT**:

**DANGEROUS INSTRUCTION**:
"Add validation state to forms using a modern state management approach."

**SAFE INSTRUCTION**:
"When adding validation state:
1. Examine existing form state patterns in the codebase
2. If they use useState, add validation using useState
3. If they use useReducer, add validation following that pattern
4. Do NOT switch between patterns while adding features
5. Keep the state shape compatible with existing onChange handlers"

---

## 8. Implementation Checklist for Skill Writers

When writing instructions for the Workflow Guardian skill, verify:

- [ ] No dangerous words (fix, improve, refactor, optimize, consolidate, extract)
- [ ] Explicit instruction: what NOT to do (e.g., "Do NOT consolidate roles")
- [ ] Patterns documented neutrally (describing what exists, not what should be)
- [ ] Examples show exact copying, not "following the pattern"
- [ ] Safety boundaries clear ("This only governs new code, never modify existing")
- [ ] Observer mode activated (gather information, don't judge)
- [ ] Match-not-fix principle applied (replicate exact patterns)
- [ ] Real consequence of violations documented (what breaks if this is violated?)
- [ ] Explicit permission required before breaking this rule
- [ ] New code only boundary enforced (no modifications to existing working code)

---

## 9. Quick Reference: The 4-Word Rule

When in doubt about how to frame an instruction, use this rule:

**Instead of asking Claude to**: "Fix, improve, refactor, or optimize [thing]"

**Ask Claude to**: "Match the existing [thing]"

This one substitution prevents 80% of breakages in Workflow Guardian.

---

## Conclusion

The deadly paradox of knowledge is real: telling Claude about a problem activates the instinct to solve it. Workflow Guardian solves this by never asking Claude to solve problems—only to match existing patterns.

Every instruction in this skill should:

1. **Describe the current state** (no judgment)
2. **Require exact matching** (copy the pattern)
3. **Forbid improvements** (explicit warning against "fixing" things)
4. **Mark refactoring separately** (only when explicitly requested as a separate task)
5. **Verify new code only** (never modify existing working code)

If you follow these principles, Claude will add features without breaking applications.

If you violate these principles, Claude will break applications while trying to help.

---

**Version**: 1.0
**Created**: 2026-02-26
**Last Updated**: 2026-02-26
**Critical Document**: Yes - This is the foundation of Workflow Guardian safety.
