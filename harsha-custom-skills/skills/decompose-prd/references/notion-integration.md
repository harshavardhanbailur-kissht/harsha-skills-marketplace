# Notion MCP Integration for Task Output

## Overview

The decompose-prd skill can automatically output all decomposed tasks, features, and epics to a Notion database. This creates a living, collaborative workspace where teams can:
- Track progress from design through delivery
- Link tasks to original PRD requirements
- Manage dependencies visually
- Report on status and metrics
- Integrate with existing project management workflows

The Notion database becomes the source of truth for execution, replacing manual copy-paste into other tools.

## Database Schema Design

### Master Database Structure

Create a single database named `"PRD Decomposition — {PRD Title}"` with the schema defined below.

The database uses a hierarchical structure:
```
Epic (parent: none)
  ├─ Feature (parent: Epic)
  │   ├─ Task (parent: Feature)
  │   ├─ Task (parent: Feature)
  │   └─ Task (parent: Feature)
  ├─ Feature (parent: Epic)
  └─ Feature (parent: Epic)
```

### Required Properties

All 14 properties below are essential for effective task tracking and decomposition traceability.

#### 1. Name (Title Property) ⭐ REQUIRED
**Type:** Title
**Description:** The task/feature/epic name
**Example values:**
- `Epic: User Authentication`
- `Feature: Email Login`
- `Task: Implement JWT token generation`

**Guidelines:**
- Be specific and unique
- Include noun + action verb (e.g., "Implement", "Design", "Integrate")
- Avoid generic names ("Fix bugs", "Improve performance")

#### 2. Type (Select)
**Type:** Select
**Options:** Epic / Feature / Task
**Description:** Classification of this item

**Guidance:**
- Epic: Large initiative spanning multiple features (e.g., "Authentication System")
- Feature: Deliverable functionality (e.g., "Email login capability")
- Task: Unit of work for one person/pair (e.g., "Build JWT token service")

#### 3. ID (Rich Text)
**Type:** Rich Text
**Description:** Hierarchical task ID using format `T-{epic}.{feature}.{task}`

**Example IDs:**
```
E-1           (Epic: User Authentication)
E-1.1         (Feature: Email Login under Epic 1)
E-1.1.1       (Task: JWT token generation)
E-1.1.2       (Task: Email provider integration)
E-1.2         (Feature: OAuth Social Login under Epic 1)
E-1.2.1       (Task: Google OAuth implementation)
```

**Benefits:**
- Traceable to PRD sections
- Unique, permanent identifier
- Easy to reference in conversations
- Supports reporting queries

#### 4. Status (Select)
**Type:** Select
**Options:** Not Started / In Progress / Done / Blocked
**Default:** Not Started

**Workflow:**
```
Not Started → In Progress → Done
                    ↓
                  Blocked → (when resolved) → In Progress
```

**Blocked status:** Use when task is waiting on external dependency (another task, external API, stakeholder decision, etc.). Always document blocker in description.

#### 5. Priority (Select)
**Type:** Select
**Options:** P0-Critical / P1-High / P2-Medium / P3-Low
**Default:** P2-Medium

**Definitions:**
- **P0-Critical:** Blocks MVP launch or breaks existing functionality
- **P1-High:** Needed for MVP but could theoretically ship with workaround
- **P2-Medium:** Nice-to-have for MVP, possibly pushed to Phase 2
- **P3-Low:** Optimization, edge case, or post-launch feature

#### 6. Effort (Select)
**Type:** Select
**Options:** XS / S / M / L / XL
**Description:** T-shirt sizing of effort required

**Rough mappings (varies by team):**
```
XS = <4 hours (trivial, automated)
S  = 4-8 hours (one person, one day)
M  = 1-3 days (straightforward)
L  = 3-7 days (complex, some uncertainty)
XL = 1-2 weeks+ (very complex, multiple unknowns)
```

**Note:** Use for Features and Tasks only. Epics should aggregate effort.

#### 7. Parent (Relation)
**Type:** Relation
**Description:** Links tasks to features, features to epics

**Rules:**
- Every Feature must have a Parent Epic
- Every Task must have a Parent Feature
- Epics have no parent (null)
- Each item has at most one parent (tree structure, not DAG)

**Why:**
- Enables hierarchical rollup of status/effort
- Creates navigation in Notion (breadcrumbs)
- Supports filtering by epic/feature

#### 8. Dependencies (Relation)
**Type:** Relation
**Description:** Links to blocking tasks (what must finish before this can start)

**Rules:**
- May be empty (no dependencies)
- Multiple values allowed (this task depends on many)
- No circular dependencies (validation rule)
- Can link across epics/features

**Example:**
```
Task: Integrate Stripe payment API
Dependencies: [
  "T-1.3.2: Define payment data model",
  "T-2.1.1: Set up API gateway"
]
```

**Benefit:** Enables critical path analysis and parallel planning.

#### 9. PRD Requirements (Rich Text)
**Type:** Rich Text
**Description:** Traced requirement IDs from original PRD

**Format:** Comma-separated IDs or section references

**Examples:**
```
REQ-2.3.1, REQ-2.3.2
Section "Payment Processing" → Requirement 5
Requirement ID: R-AUTH-001
```

**Purpose:**
- Traceability: which PRD requirement does this task implement?
- Impact analysis: if PRD requirement changes, which tasks are affected?
- Sign-off: requirements get signed off when linked tasks are Done

#### 10. Assignee (People)
**Type:** People
**Description:** Engineer/designer responsible for this task

**Rules:**
- Optional (can be unassigned)
- Single person per task (use Collaborators relation for additional people)
- Can be empty initially, filled as work is assigned

**Benefit:** Enables personal workload tracking and burndown.

#### 11. Sprint (Select)
**Type:** Select
**Options:** [Backlog, Sprint 1, Sprint 2, Sprint 3, ...]
**Default:** Backlog

**Usage:**
- Backlog: not yet scheduled
- Sprint N: assigned to that sprint
- Useful for sprint planning and burndown charts

**Note:** Optional field. Use only if you do scrum/sprint-based planning.

#### 12. Acceptance Criteria (Rich Text)
**Type:** Rich Text
**Description:** Definition of done for this task

**Format:** Given/When/Then (BDD style) or numbered checklist

**Example 1 (BDD):**
```
Given: User is logged into the app
When: User clicks "Forgot Password"
Then:
  - Password reset email is sent
  - Email arrives within 60 seconds
  - Email contains secure reset link (one-time use)
  - Link expires after 1 hour
```

**Example 2 (Checklist):**
```
- [ ] JWT implementation complete (HS256 algorithm)
- [ ] Token includes user ID, email, roles claims
- [ ] Token expires after 24 hours
- [ ] Refresh token mechanism implemented
- [ ] Unit tests cover token lifecycle (create, validate, refresh, expire)
- [ ] Security review passed (no hardcoded secrets)
- [ ] Performance: token generation <50ms
```

#### 13. Domain (Multi-Select)
**Type:** Multi-Select
**Options:** Frontend / Backend / Infra / Data / ML / Security / Product / Design
**Description:** Functional area(s) this task touches

**Guidance:**
- Most tasks are single domain (task to one team)
- Some cross-domain tasks are possible (e.g., "API contract for payment" → Backend + Frontend)
- Use for filtering by team

#### 14. Layer (Number)
**Type:** Number
**Description:** Execution layer for parallel planning (1 = can start immediately, higher = depends on earlier layers)

**How to compute:**
```
Layer 1: No dependencies, can start day 1
Layer 2: Depends only on Layer 1 tasks
Layer 3: Depends on Layer 1 or Layer 2 tasks
Layer N: Maximum distance in dependency graph
```

**Example (authentication system):**
```
Layer 1:
  - Design authentication system architecture
  - Set up API gateway

Layer 2:
  - Implement JWT token service (depends on API gateway)
  - Design user database schema (depends on auth architecture)

Layer 3:
  - Email login implementation (depends on JWT + DB)
  - Social OAuth (depends on JWT + gateway)
```

**Benefit:** Enables:
- Parallel work scheduling (teams can pick any tasks from same layer)
- Critical path computation
- Risk planning (fewer layers = longer critical path = more risk)

#### 15. Critical Path (Checkbox) ⭐ RECOMMENDED
**Type:** Checkbox
**Description:** Is this task on the critical path to launch?

**Algorithm:**
- A task is critical if: delaying it delays overall project completion
- Non-critical tasks have slack time
- Dashboard shows all critical tasks for focus

**Identify by:**
1. Compute layer for all tasks (see Layer property above)
2. Find longest path through dependency graph
3. Mark all tasks on that path as Critical Path = true

**Benefit:** Focuses team on what actually matters; non-critical tasks can slip without jeopardizing launch.

---

## Step-by-Step Notion MCP Tool Usage

### Phase 1: Create the Database

Use `notion-create-database` to set up the master database with all properties:

```javascript
notion-create-database({
  "title": [{"text": {"content": "PRD Decomposition — MyProject"}}],
  "properties": {
    "Type": {
      "select": {
        "options": [
          {"name": "Epic", "color": "purple"},
          {"name": "Feature", "color": "blue"},
          {"name": "Task", "color": "gray"}
        ]
      }
    },
    "ID": {"rich_text": {}},
    "Status": {
      "select": {
        "options": [
          {"name": "Not Started", "color": "gray"},
          {"name": "In Progress", "color": "yellow"},
          {"name": "Done", "color": "green"},
          {"name": "Blocked", "color": "red"}
        ]
      }
    },
    "Priority": {
      "select": {
        "options": [
          {"name": "P0-Critical", "color": "red"},
          {"name": "P1-High", "color": "orange"},
          {"name": "P2-Medium", "color": "yellow"},
          {"name": "P3-Low", "color": "gray"}
        ]
      }
    },
    "Effort": {
      "select": {
        "options": [
          {"name": "XS", "color": "gray"},
          {"name": "S", "color": "blue"},
          {"name": "M", "color": "green"},
          {"name": "L", "color": "orange"},
          {"name": "XL", "color": "red"}
        ]
      }
    },
    "Parent": {"relation": {}},
    "Dependencies": {"relation": {}},
    "PRD Requirements": {"rich_text": {}},
    "Assignee": {"people": {}},
    "Sprint": {
      "select": {
        "options": [
          {"name": "Backlog", "color": "gray"},
          {"name": "Sprint 1", "color": "blue"},
          {"name": "Sprint 2", "color": "blue"},
          {"name": "Sprint 3", "color": "blue"}
        ]
      }
    },
    "Acceptance Criteria": {"rich_text": {}},
    "Domain": {
      "multi_select": {
        "options": [
          {"name": "Frontend", "color": "blue"},
          {"name": "Backend", "color": "green"},
          {"name": "Infra", "color": "purple"},
          {"name": "Data", "color": "orange"},
          {"name": "ML", "color": "pink"},
          {"name": "Security", "color": "red"},
          {"name": "Product", "color": "yellow"},
          {"name": "Design", "color": "gray"}
        ]
      }
    },
    "Layer": {"number": {}},
    "Critical Path": {"checkbox": {}}
  }
})
```

### Phase 2: Batch-Create All Epics

Create epic pages first (they're the parents). Use `notion-create-pages`:

```javascript
notion-create-pages({
  "parent": {"data_source_id": "[database_data_source_id]"},
  "pages": [
    {
      "properties": {
        "Name": "User Authentication",
        "Type": "Epic",
        "ID": "E-1",
        "Status": "Not Started",
        "Priority": "P0-Critical"
      },
      "content": "# Epic: User Authentication\n\nPrimary user onboarding mechanism. Supports email login and OAuth social login (Google, GitHub). Foundation for authorization system.\n\n## Goals\n- Enable new user signup\n- Support existing user login\n- Integrate with downstream permission system\n\n## Success Criteria\n- Zero authentication failures in production\n- <200ms login latency (p95)\n- Support 10,000 concurrent sessions"
    },
    {
      "properties": {
        "Name": "Payment Processing",
        "Type": "Epic",
        "ID": "E-2",
        "Status": "Not Started",
        "Priority": "P0-Critical"
      },
      "content": "# Epic: Payment Processing\n\nStripe integration for SaaS billing. Supports credit cards, ACH, invoicing. PCI-DSS compliant.\n\n## Goals\n- Collect payment from users\n- Support multiple payment methods\n- Generate invoices for accounting"
    }
    // ... more epics
  ]
})
```

**Important:** Wait for response to get the database data_source_id and epic page IDs (needed for Phase 3).

### Phase 3: Batch-Create All Features

Create feature pages with parent relation to epics:

```javascript
notion-create-pages({
  "parent": {"data_source_id": "[database_data_source_id]"},
  "pages": [
    {
      "properties": {
        "Name": "Email Login",
        "Type": "Feature",
        "ID": "E-1.1",
        "Status": "Not Started",
        "Priority": "P0-Critical",
        "Effort": "M",
        "Parent": ["E-1"],  // Epic ID
        "PRD Requirements": "REQ-2.1",
        "Domain": ["Backend", "Frontend"]
      },
      "content": "# Feature: Email Login\n\nEnable users to sign up and log in with email/password. Classic username/password flow.\n\n## User Flow\n1. User enters email + password\n2. System validates email format\n3. If new email: create account, send verification email\n4. If existing email: verify password\n5. Issue JWT token, redirect to dashboard\n\n## Acceptance Criteria\n- Email validation per RFC 5322\n- Password minimum 8 characters (lowercase, number, special char)\n- Email verification link expires after 24 hours\n- Failed login locked for 5 minutes after 5 attempts"
    },
    {
      "properties": {
        "Name": "Social OAuth Login",
        "Type": "Feature",
        "ID": "E-1.2",
        "Status": "Not Started",
        "Priority": "P1-High",
        "Effort": "L",
        "Parent": ["E-1"],  // Epic ID
        "PRD Requirements": "REQ-2.2",
        "Domain": ["Backend", "Frontend"]
      },
      "content": "# Feature: Social OAuth Login\n\nEnable sign-up/login via Google and GitHub. Reduces friction for developers."
    }
    // ... more features
  ]
})
```

### Phase 4: Batch-Create All Tasks

Create task pages with parent relation to features and dependency relations:

```javascript
notion-create-pages({
  "parent": {"data_source_id": "[database_data_source_id]"},
  "pages": [
    {
      "properties": {
        "Name": "Design JWT token schema",
        "Type": "Task",
        "ID": "E-1.1.1",
        "Status": "Not Started",
        "Priority": "P0-Critical",
        "Effort": "S",
        "Parent": ["E-1.1"],  // Feature ID
        "PRD Requirements": "REQ-2.1.1",
        "Domain": ["Backend"],
        "Layer": 1,
        "Critical Path": true
      },
      "content": "# Task: Design JWT token schema\n\nDefine the structure of JWT tokens issued by the authentication service.\n\n## Acceptance Criteria\n- [ ] Determine algorithm: HS256 or RS256?\n- [ ] Define claims: user_id, email, roles, org_id, scopes\n- [ ] Set token lifetime: 24 hours for access, 30 days for refresh\n- [ ] Define revocation mechanism (token blacklist or versioning)\n- [ ] Design refresh token rotation strategy\n- [ ] Document token format in API spec"
    },
    {
      "properties": {
        "Name": "Implement JWT token generation",
        "Type": "Task",
        "ID": "E-1.1.2",
        "Status": "Not Started",
        "Priority": "P0-Critical",
        "Effort": "M",
        "Parent": ["E-1.1"],  // Feature ID
        "Dependencies": ["E-1.1.1"],  // Depends on design task above
        "PRD Requirements": "REQ-2.1.1",
        "Domain": ["Backend"],
        "Layer": 2,
        "Critical Path": true
      },
      "content": "# Task: Implement JWT token generation\n\nBuild the backend service that creates and signs JWT tokens.\n\n## Acceptance Criteria\n- [ ] Use industry library (jsonwebtoken for Node, PyJWT for Python)\n- [ ] Tokens signed with secure key (never hardcoded)\n- [ ] HS256 or RS256 per design decision\n- [ ] Generate within 50ms (benchmark)\n- [ ] Unit tests: valid token structure, claims present, signature valid\n- [ ] Error cases: invalid inputs, signing failures\n- [ ] Security review: no secrets in logs"
    },
    {
      "properties": {
        "Name": "Add email login UI",
        "Type": "Task",
        "ID": "E-1.1.3",
        "Status": "Not Started",
        "Priority": "P0-Critical",
        "Effort": "M",
        "Parent": ["E-1.1"],  // Feature ID
        "Dependencies": ["E-1.1.2"],  // Depends on backend implementation
        "PRD Requirements": "REQ-2.1.2",
        "Domain": ["Frontend"],
        "Layer": 3,
        "Critical Path": true
      },
      "content": "# Task: Add email login UI\n\nBuild login form and integrate with JWT backend API.\n\n## Acceptance Criteria\n- [ ] Login form: email + password fields\n- [ ] Validation: email format, password strength indicator\n- [ ] Call POST /auth/login with credentials\n- [ ] Handle responses: success (redirect to dashboard), error (show message)\n- [ ] Store JWT in secure httpOnly cookie (not localStorage)\n- [ ] UI/UX: password visibility toggle, remember me option\n- [ ] Error messages: account not found, invalid password (generic for security)\n- [ ] Accessibility: WCAG 2.1 AA compliant"
    }
    // ... more tasks
  ]
})
```

**Important:** After creating all tasks, compute layer numbers and critical path using dependency relations.

---

## Notion Markdown Formatting Patterns

The content field of each page uses Notion Markdown. Follow these patterns:

### Headers (Organization)
```markdown
# Title (page title, included in properties)

## Objective
Clear statement of what this task/feature accomplishes

## User Flow (for features)
Step-by-step narrative of how user interacts

## Acceptance Criteria (for tasks)
Checklist or Given/When/Then statements

## Implementation Notes
Technical guidance, edge cases, gotchas

## Dependencies
Links to blocking tasks or PRD sections

## Assumptions
Explicit assumptions made in design
```

### Checklists (Acceptance Criteria)
```markdown
## Acceptance Criteria

- [ ] Component renders correctly on desktop/mobile
- [ ] Form validation shows errors inline
- [ ] Submit button disabled until all fields valid
- [ ] API call includes auth header
- [ ] Error responses show user-friendly message
- [ ] Performance: <500ms API response
- [ ] Security: no sensitive data in logs
```

### Code Blocks (Technical Specs)
```markdown
## API Specification

```json
POST /auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response 200:
{
  "token": "eyJhbGc...",
  "user": {
    "id": "123",
    "email": "user@example.com",
    "roles": ["user"]
  }
}

Response 401:
{
  "error": "invalid_credentials"
}
```
```

### Callouts (Warnings/Important Notes)
```markdown
> 🔒 SECURITY: Never log passwords or tokens. Use requestId instead for debugging.

> ⚠️ WARNING: This task depends on Stripe API credentials. Ensure these are loaded before running.

> 💡 TIP: Reuse the existing JWT library rather than implementing from scratch.
```

### Links (Cross-References)
```markdown
## Related Tasks
- [Design database schema](notion://link-to-task)
- [Security review](notion://link-to-task)
- [API contract](notion://link-to-task)

## PRD Reference
- Section 2.3: "User Authentication Requirements"
- Requirement REQ-2.1: "Email login support"
```

---

## View Recommendations

After all pages are created, set up views in Notion for different use cases:

### 1. Board View (Status by Task Type)
- Grouping: Status (Not Started | In Progress | Done | Blocked)
- Filter: Type = "Task"
- Sorted by: Priority (descending), Layer (ascending)

**Use case:** Daily standup, progress tracking

### 2. Table View (All Items)
- All 15 properties visible
- Sorted by: Layer (ascending), Priority (descending)
- Filter options: by Assignee, Domain, Status

**Use case:** Sprint planning, workload assessment

### 3. Timeline/Calendar View (if effort estimates available)
- X-axis: Time (based on effort estimate and sprint assignment)
- Grouping: by Domain (Backend, Frontend, Infra, etc.)

**Use case:** Capacity planning, critical path visualization

### 4. Gallery View (by Epic)
- Grouping: Parent (Epic)
- Cards show: Name, Status, Priority, Effort

**Use case:** Epic-level progress, stakeholder updates

### 5. Database Relations (Dependency Visualization)
- View which tasks block which other tasks
- Filter by Critical Path = true

**Use case:** Risk management, dependency coordination

---

## Alternative: Creating Under Existing Notion Page

If you want tasks nested under an existing Notion page (rather than creating a new standalone database), provide the parent page ID:

```javascript
notion-create-database({
  "parent": {"page_id": "existing-page-uuid"},
  "title": [{"text": {"content": "Decomposed Tasks"}}],
  "properties": { /* schema above */ }
})
```

This creates the database as a child of the existing page, useful for:
- Keeping all project info on one page
- Organizing multiple decompositions under project overview

---

## Error Handling: Fallback if Notion MCP Unavailable

If the Notion MCP tool is not available or the user hasn't granted permission:

1. **Detect:** Call to `notion-create-database` returns error or permission denied
2. **Fallback:** Output decomposition as structured Markdown instead:
   ```markdown
   # Epics

   ## E-1: User Authentication
   ### Features
   - E-1.1: Email Login
   - E-1.2: Social OAuth
   ### Tasks
   - E-1.1.1: Design JWT token schema
   - E-1.1.2: Implement JWT generation
   ```
3. **Notify user:** "Notion integration unavailable. Output is Markdown format. Would you like to import this into Notion manually?"

The decomposition is equally complete in Markdown; Notion is just a convenience layer for ongoing project management.

---

## Summary

Notion integration transforms decomposition output from a static document into a living project management workspace. By following the schema above and tool usage patterns, you create:

- **Traceability:** tasks linked to original PRD requirements
- **Progress tracking:** status rollup from tasks → features → epics
- **Dependency visibility:** understand critical path and parallel opportunities
- **Team coordination:** assigned tasks, status updates, blockers
- **Data-driven planning:** effort estimates, layer numbers, priority alignment

The decomposition skill automates creation; teams maintain and update the Notion database through launch.
