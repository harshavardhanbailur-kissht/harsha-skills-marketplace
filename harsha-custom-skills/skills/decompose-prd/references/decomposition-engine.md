# Epic→Feature→Task Decomposition Engine

## Overview

The decomposition engine transforms a normalized PRD into a hierarchical breakdown of work: Epics → Features → Tasks. This multi-level decomposition enables:

- **Epics**: Large, independently valuable business outcomes aligned with product domains and user capabilities
- **Features**: Independently demonstrable capabilities that can be built, tested, and released
- **Tasks**: Atomic units of work executable by an AI agent in a single session

This document describes the ADaPT framework adapted for PRD decomposition, including identification algorithms, naming conventions, validation rules, and domain-specific patterns.

## The ADaPT Framework Adapted for PRD Decomposition

ADaPT (Artifacts, Dependencies, Phases, Tasks) is a decomposition methodology we adapt as follows:

- **Artifacts**: PRD sections and requirements → mapped to work items
- **Dependencies**: Extracted from PRD sequencing, technical architecture, and user workflows
- **Phases**: Map to our three-level hierarchy (Epic → Feature → Task)
- **Tasks**: AI-executable units with clear objectives and boundaries

Key adaptation: Instead of starting with arbitrary tasks, we start with requirement extraction from the normalized PRD, then structure work around user-facing capabilities (epics) that deliver business value.

## Level 1: EPICS

An Epic is a large body of work representing a major user-facing capability or infrastructure component. Each epic should be independently valuable and roughly achievable in a 4-6 week timeframe.

### Epic Identification Algorithm

#### Step 1: Domain Classification

Categorize the PRD content into functional domains:

```python
DOMAINS = {
    "frontend": "User interface, screens, interactions, client-side logic",
    "backend": "APIs, business logic, services, data processing",
    "infra": "Infrastructure, deployment, CI/CD, monitoring",
    "data": "Data pipelines, analytics, reporting, BI",
    "ml": "Machine learning, models, training, inference",
    "security": "Authentication, authorization, encryption, compliance",
    "compliance": "Regulatory requirements, audit, data governance"
}

def classify_to_domains(requirements: List[Requirement]) -> Dict[str, List[Requirement]]:
    """Classify all requirements into applicable domains"""
    domain_map = {domain: [] for domain in DOMAINS}

    for req in requirements:
        # Look for keywords in requirement text
        text_lower = req.text.lower()
        for domain, keywords in get_domain_keywords().items():
            if any(kw in text_lower for kw in keywords):
                domain_map[domain].append(req)

    # Some requirements may map to multiple domains
    # Architecture requirements often span frontend + backend
    return domain_map
```

#### Step 2: User Capability Mapping

Group requirements that deliver a complete user-facing capability. One epic = one major capability.

```python
def extract_user_capabilities(requirements: List[Requirement]) -> List[str]:
    """
    Extract distinct user capabilities from requirements.
    A capability is something a user can "do" that delivers value.

    Examples:
    - "User can log in securely" (capability: User Authentication)
    - "Admin can configure org permissions" (capability: Permission Management)
    - "System processes data hourly" (capability: Data Synchronization)
    """
    capabilities = []

    # Group requirements by user role or functional area
    role_groups = group_by_user_role(requirements)  # e.g., "End User", "Admin", "System"

    for role, role_reqs in role_groups.items():
        # Within each role, group by action/capability
        sub_groups = group_by_action(role_reqs)  # e.g., "authenticate", "authorize", "profile"

        for action, action_reqs in sub_groups.items():
            capability = f"{role} — {action}".title()
            capabilities.append({
                "name": capability,
                "requirements": action_reqs,
                "domain": infer_domain(action_reqs)
            })

    return capabilities
```

#### Step 3: Infrastructure Epic Generation

Even if not explicitly mentioned in requirements, infrastructure epics are generated for:

- **Authentication & Authorization**: Core security infrastructure (SSO, OAuth, RBAC)
- **CI/CD Pipeline**: Build, test, deploy automation
- **Monitoring & Observability**: Logging, metrics, alerting
- **Data Storage & Migration**: Database setup, schema management
- **API Infrastructure**: Rate limiting, versioning, documentation

```python
def generate_infrastructure_epics(project_scope: str) -> List[Epic]:
    """
    Auto-generate infrastructure epics based on project scope.
    These are required but often implicit in PRDs.
    """
    infra_epics = [
        Epic(
            id="INFRA-001",
            name="Authentication & Authorization Framework",
            domain="security",
            description="Foundational auth system supporting user identity, sessions, and access control"
        ),
        Epic(
            id="INFRA-002",
            name="CI/CD Pipeline & Deployment",
            domain="infra",
            description="Automated build, test, and deployment infrastructure"
        ),
        Epic(
            id="INFRA-003",
            name="Monitoring, Logging, & Alerting",
            domain="infra",
            description="System observability and incident response infrastructure"
        ),
    ]

    # Only include if project is non-trivial size
    if len(project_scope) > 2000:  # meaningful PRD
        infra_epics.extend([
            Epic(id="INFRA-004", name="Database & Data Storage", domain="data"),
            Epic(id="INFRA-005", name="API & Integration Layer", domain="backend"),
        ])

    return infra_epics
```

### Epic Naming Convention

```
[Domain] — [Capability]
```

**Format Rules**:
- Domain from DOMAINS list above
- Capability is a user-facing action or major system component
- Two hyphens with spaces (` — `) as separator
- Title case each part

**Examples**:
- `Frontend — User Authentication UI`
- `Backend — Payment Processing Service`
- `Data — Analytics Dashboard`
- `Security — OAuth 2.0 Integration`
- `Infra — CI/CD Pipeline`

### Epic Decomposition Output

```python
Epic = {
    "id": "E-{number}",  # E-1, E-2, etc.
    "name": str,  # Following naming convention
    "domain": str,  # One of DOMAINS keys
    "description": str,  # What this epic delivers
    "user_capabilities": [str],  # User-facing capabilities within
    "requirements": [Requirement],  # Mapped from PRD
    "success_criteria": [str],  # Epic-level acceptance criteria
    "estimated_duration": "weeks",  # Rough estimate: 2-6 weeks
    "target_feature_count": "2-5",  # Expected number of features
}
```

### Epic Count Target

**Target: 3-7 epics per typical PRD**

- **Under-decomposition** (too few epics): Teams can't work in parallel; unclear priorities
- **Over-decomposition** (too many epics): Excessive fragmentation; hard to coordinate
- **Goldilocks zone**: 3-7 epics allows parallel feature development within each epic

## Level 2: FEATURES

A Feature is an independently demonstrable capability that provides clear value and can be built, tested, and released as a unit. Features are the actual shippable/deployable items.

### Feature Identification Rules

Each feature must satisfy:

1. **Independence**: Can be designed, built, tested, and merged independently
2. **Completeness**: Fully implements one user capability end-to-end
3. **Demonstrability**: Can be demo'd to stakeholders without other features
4. **Acceptance Traceable**: Each feature has AC directly traceable to PRD requirements

### Feature Breakdown Algorithm

```python
def decompose_epic_to_features(epic: Epic) -> List[Feature]:
    """
    For each epic, extract independent capabilities that can be worked on
    in parallel by different sub-teams.
    """
    requirements = epic.requirements
    feature_groups = []

    # Group requirements by coherent sub-capability
    # Example: "User Authentication" epic breaks into:
    # - F-1: Login with email/password
    # - F-2: OAuth provider integration
    # - F-3: Session management

    # Group by technical subsystem if clear
    subsystems = group_by_subsystem(requirements)

    for subsystem_name, subsystem_reqs in subsystems.items():
        # Each subsystem = one feature
        feature = Feature(
            parent_epic=epic.id,
            name=f"{epic.name}: {subsystem_name}",
            requirements=subsystem_reqs,
            acceptance_criteria=extract_acceptance_criteria(subsystem_reqs)
        )
        feature_groups.append(feature)

    # Validate: 2-5 features per epic
    if len(feature_groups) < 2:
        # Epic too small, consider merging with another
        log_warning(f"{epic.name} has only {len(feature_groups)} features")
    if len(feature_groups) > 5:
        # Over-decomposed, some features should merge
        log_warning(f"{epic.name} has {len(feature_groups)} features, target is 2-5")

    return feature_groups
```

### Domain-Specific Feature Patterns

#### Frontend Domain

```
User Authentication Epic
├─ Feature: Login & Session Management
├─ Feature: User Profile Management
├─ Feature: Permission-based UI Rendering
└─ Feature: Navigation & Routing Framework
```

Pattern: Component → Page → Integration

#### Backend Domain

```
Payment Processing Epic
├─ Feature: Payment Model & Persistence
├─ Feature: Payment Service Layer
├─ Feature: Payment REST API
└─ Feature: Payment Integration Tests & Monitoring
```

Pattern: Model → Service → API → Tests

#### Data Domain

```
Analytics Pipeline Epic
├─ Feature: Data Schema & Warehouse
├─ Feature: ETL Pipeline
├─ Feature: Analytics Queries & Dashboards
└─ Feature: Monitoring & Data Quality
```

Pattern: Schema → Pipeline → Visualization → QA

### Feature Naming Convention

```
F-{epic_number}.{feature_number}: [Descriptive Name]
```

**Examples**:
- `F-1.1: User Email Registration`
- `F-1.2: OAuth Provider Integration`
- `F-2.1: Payment Method Management`
- `F-3.2: Admin Dashboard Visualizations`

### Feature Acceptance Criteria

Each feature must have acceptance criteria that can be verified by integration testing:

```gherkin
Feature: F-2.1 Payment Method Management

Scenario: User can add a new payment method
    Given a logged-in user
    When they navigate to Payment Settings
    And enter valid card details
    Then the system validates the card
    And stores it securely
    And displays confirmation

Scenario: User can remove a payment method
    Given a stored payment method
    When they request removal
    And confirm the action
    Then it's deleted from their profile
    And any future charges fail appropriately
```

### Feature Decomposition Output

```python
Feature = {
    "id": "F-{epic_id}.{number}",
    "epic_id": "E-{number}",
    "name": str,  # Following naming convention
    "description": str,
    "requirements": [Requirement],  # From PRD
    "acceptance_criteria": [str],  # BDD-style Given/When/Then
    "task_count": "2-7",  # Expected number of tasks
    "estimated_story_points": "3-13",  # T-shirt: S/M/L/XL
    "dependencies": ["F-{epic}.{feat}"],  # Other features this depends on
    "definition_of_done": [str],  # Code review, tests, docs, merged
}
```

## Level 3: TASKS

A Task is an atomic unit of work executable by a Claude agent in a single session. Each task produces specific, tangible artifacts (files, code, documentation) and has clear acceptance criteria.

### Task Identification Rules

Each task must satisfy:

1. **Single Responsibility**: One clear objective, no mixed concerns
2. **Agent-Executable**: Completable by Claude agent with all necessary context
3. **Output Artifacts**: Produces specific files/code that can be reviewed
4. **Boundary Clarity**: Clear scope limits and explicit non-goals
5. **Session Bounded**: Completable in one agent session (2000-4000 output tokens)

### Task Sizing Guidelines

**Target: 2000-4000 output tokens per task**

This corresponds to:
- ~500-1000 lines of code (depending on verbosity and comments)
- ~30-60 minute focused work for a human developer
- ~5-15 minutes for Claude agent execution

### Task Breakdown Algorithm

```python
def decompose_feature_to_tasks(feature: Feature) -> List[Task]:
    """
    For each feature, identify atomic tasks that Claude agents can execute.
    Uses domain-specific patterns to ensure coherent scoping.
    """
    domain = feature.parent_epic.domain
    tasks = []

    if domain == "frontend":
        # Frontend pattern: Component → Page → Integration
        tasks = decompose_frontend_feature(feature)
    elif domain == "backend":
        # Backend pattern: Model → Service → API → Test
        tasks = decompose_backend_feature(feature)
    elif domain == "data":
        # Data pattern: Schema → Pipeline → Validation
        tasks = decompose_data_feature(feature)
    elif domain == "security":
        # Security pattern: Design → Implementation → Integration → Audit
        tasks = decompose_security_feature(feature)
    else:
        # Default: requirement-driven decomposition
        tasks = decompose_generic_feature(feature)

    # Validate task count: 2-7 per feature
    assert 2 <= len(tasks) <= 7, f"Feature {feature.id} has {len(tasks)} tasks, target 2-7"

    return tasks


def decompose_frontend_feature(feature: Feature) -> List[Task]:
    """Frontend decomposition follows: Component → Page → Integration"""
    # T-N.M.1: Create reusable component(s)
    # T-N.M.2: Build page(s) using components
    # T-N.M.3: Integrate with routing and state management
    # T-N.M.4: Add unit tests for components
    # T-N.M.5: Add integration tests
    pass


def decompose_backend_feature(feature: Feature) -> List[Task]:
    """Backend decomposition follows: Model → Service → API → Test"""
    # T-N.M.1: Define data model and persistence
    # T-N.M.2: Implement service/business logic
    # T-N.M.3: Create REST API endpoints
    # T-N.M.4: Add unit and integration tests
    pass


def decompose_data_feature(feature: Feature) -> List[Task]:
    """Data decomposition follows: Schema → Pipeline → Validation"""
    # T-N.M.1: Design schema or query structure
    # T-N.M.2: Implement ETL pipeline
    # T-N.M.3: Add data quality validation
    # T-N.M.4: Create visualizations or reports
    pass
```

### Task Naming Convention

```
T-{epic_number}.{feature_number}.{task_number}: [Action Verb] [Object]
```

**Guidelines**:
- Start with action verb (Create, Implement, Add, Fix, Refactor, Write, etc.)
- Clear object (Component, Service, Test, Configuration, etc.)
- Specific enough to avoid ambiguity

**Examples**:
- `T-1.1.1: Create LoginForm component`
- `T-1.1.2: Implement email validation service`
- `T-2.3.4: Add unit tests for PaymentProcessor`
- `T-3.2.1: Design analytics dashboard schema`
- `T-INFRA.1.2: Configure GitHub Actions CI pipeline`

### Task Specification Fields

Each task must include these fields (see task-specifications.md for detailed schema):

```python
Task = {
    "id": "T-{epic}.{feature}.{task}",
    "title": str,  # Action verb + Object
    "epic_id": "E-{number}",
    "feature_id": "F-{number}.{number}",

    # Core specification
    "objective": str,  # Exactly what must be produced
    "context": str,  # Project context and conventions
    "inputs": {
        "dependencies": ["T-X.Y.Z"],  # Tasks that must complete first
        "required_files": [str],  # Files needed as input
        "from_prd": [str]  # Requirement IDs
    },
    "expected_output": {
        "files": [str],  # Exact file paths to create/modify
        "format": str,  # Language, framework, data format
        "size_estimate": str  # Lines/tokens
    },
    "technical_requirements": {
        "stack": [str],  # Technologies
        "patterns": [str],  # Design patterns
        "libraries": [str],  # Specific packages
        "constraints": [str]  # Performance, security
    },
    "boundary_conditions": {
        "do_not": [str],  # Out of scope
        "do_not_modify": [str],  # Files owned by other tasks
        "assumptions": [str]  # What to assume about other tasks
    },
    "acceptance_criteria": [str],  # Given/When/Then format
    "verification": {
        "syntax": str,  # Linting, type check, etc.
        "functional": str,  # Unit test, import check, etc.
        "integration": str  # How it connects to adjacent tasks
    },

    # Estimation and priority
    "estimated_effort": "S" | "M" | "L" | "XL",  # T-shirt sizing
    "estimated_tokens": int,  # 500-2000
    "priority": "blocker" | "critical" | "high" | "medium" | "low",
    "prerequisite_tasks": [str],  # Which tasks must complete first
}
```

### Domain-Specific Task Patterns

#### Frontend Tasks

**Component Creation**:
```
T-X.Y.1: Create [ComponentName] component
- Objective: Implement reusable React/Vue/etc component with props
- Output: src/components/[ComponentName].tsx, .test.tsx
- Acceptance: Component renders correctly, props validated, story written
- Do NOT: Handle state management, API calls (those are parent's job)
```

**Page Integration**:
```
T-X.Y.2: Build [PageName] page using components
- Objective: Assemble components into full page, connect to router
- Output: src/pages/[PageName].tsx, .test.tsx
- Acceptance: Page renders, navigation works, responsive design
- Do NOT: Create new components (re-use from prior task)
```

#### Backend Tasks

**Model & Database**:
```
T-X.Y.1: Design and implement [EntityName] model
- Objective: Create entity definition, migrations, ORM setup
- Output: models/[entity].ts, migrations/[timestamp]_create_[entity].sql
- Acceptance: Model validates, migrations apply cleanly, relationships work
- Do NOT: Implement business logic or API endpoints
```

**Service Implementation**:
```
T-X.Y.2: Implement [ServiceName] business logic
- Objective: Core service methods with validation and error handling
- Output: services/[service].ts, services/[service].test.ts
- Acceptance: All methods work, error cases handled, tests pass
- Do NOT: Add API endpoints or HTTP layer
```

#### Data Tasks

**Schema Design**:
```
T-X.Y.1: Design [dataset] schema and data model
- Objective: Create normalized schema, relationships, indices
- Output: schemas/[dataset].sql, design_doc.md
- Acceptance: Schema is normalized, indices optimal, documentation complete
- Do NOT: Load data or create pipelines
```

**ETL Pipeline**:
```
T-X.Y.2: Implement [source] → [destination] ETL pipeline
- Objective: Extract, transform, load data with error handling
- Output: pipelines/[name].py, config/[name].yaml, tests/
- Acceptance: Data loads correctly, transformations applied, errors logged
- Do NOT: Create visualizations or reports
```

## MECE Validation at Every Level

MECE (Mutually Exclusive, Collectively Exhaustive) ensures decomposition is complete and non-overlapping:

### At Epic Level

```python
def validate_epics_mece(epics: List[Epic]) -> bool:
    """
    Epics should be MECE:
    - Mutually Exclusive: Each epic covers distinct user capability or domain
    - Collectively Exhaustive: All PRD requirements mapped to at least one epic
    """
    # Check exclusivity: no requirement appears in multiple epics
    all_reqs = set()
    for epic in epics:
        epic_reqs = set(req.id for req in epic.requirements)
        assert len(all_reqs & epic_reqs) == 0, f"Duplicate requirements in epics"
        all_reqs.update(epic_reqs)

    # Check exhaustiveness: all PRD requirements mapped
    prd_reqs = get_all_prd_requirements()
    unmapped = set(req.id for req in prd_reqs) - all_reqs
    assert len(unmapped) == 0, f"Unmapped requirements: {unmapped}"

    return True
```

### At Feature Level

```python
def validate_features_mece(features: List[Feature]) -> bool:
    """
    Features within an epic should be MECE:
    - Distinct sub-capabilities: each feature = one coherent piece
    - No requirement in multiple features of same epic
    - All epic requirements covered by features
    """
    for epic_features in group_by_epic(features):
        # Exclusivity within epic
        all_feature_reqs = set()
        for feature in epic_features:
            feature_reqs = set(req.id for req in feature.requirements)
            assert len(all_feature_reqs & feature_reqs) == 0, f"Overlapping in {feature.epic_id}"
            all_feature_reqs.update(feature_reqs)

        # Exhaustiveness within epic
        epic = get_epic(epic_features[0].epic_id)
        epic_reqs = set(req.id for req in epic.requirements)
        assert all_feature_reqs == epic_reqs, f"Incomplete feature coverage in {epic.id}"

    return True
```

### At Task Level

```python
def validate_tasks_mece(tasks: List[Task]) -> bool:
    """
    Tasks within a feature should be MECE:
    - Each task produces distinct artifacts
    - No file modified by multiple tasks in same feature
    - All feature work covered by tasks
    """
    for feature_tasks in group_by_feature(tasks):
        # Exclusivity: file ownership
        all_files = set()
        for task in feature_tasks:
            task_files = set(task.expected_output.files)
            assert len(all_files & task_files) == 0, f"File conflict in {task.feature_id}"
            all_files.update(task_files)

        # Exclusivity: no overlapping responsibilities
        # (verify via acceptance criteria — each task's AC must be distinct)

    return True
```

## Granularity Calibration: The "Junior Engineer" Test

The decomposition should be granular enough that a junior engineer (or in our case, a Claude agent) can execute a task without confusion, but not so granular that coordination overhead explodes.

### The Test

For each task, ask: "Could a junior engineer who knows the tech stack but is new to the codebase execute this task completely, with the task spec as their only guidance?"

**If yes**: Task is appropriately scoped.
**If no, it's unclear what to do**: Task is under-specified or over-scoped.

### Specific Indicators

```python
def apply_junior_engineer_test(task: Task) -> bool:
    """
    Score 0-5 on each dimension:
    """
    # 1. Clarity: Are all terms defined? (5 = crystal clear, 0 = vague)
    clarity = assess_clarity(task.objective, task.context)

    # 2. Boundedness: Is scope clearly limited? (5 = obvious limits, 0 = could expand infinitely)
    boundedness = assess_boundedness(task.boundary_conditions)

    # 3. Completeness: Can task be done without asking questions?
    completeness = assess_completeness(task)

    # 4. Testability: Can we verify completion? (5 = objective pass/fail, 0 = subjective)
    testability = assess_testability(task.acceptance_criteria)

    overall_score = (clarity + boundedness + completeness + testability) / 4

    if overall_score < 4.0:
        # Task needs clarification
        return False

    return True
```

## Error Propagation Math

Each level of decomposition introduces a small error rate. This is normal and expected; the goal is to minimize it while keeping decomposition practical.

### Error Rates by Level

- **Level 1 (Epic identification)**: ~5-8% error rate
  - Some epics might be poorly named or contain mixed concerns
  - But high-level structure is usually sound

- **Level 2 (Feature decomposition)**: ~8-12% error rate
  - More detailed analysis means more chances for oversight
  - Some features might be too large or too small
  - Feature dependencies can be missed

- **Level 3 (Task breakdown)**: ~10-15% error rate
  - Most detailed level; most oversight opportunities
  - Task boundaries might not perfectly map to code structure
  - Some tasks might need slight adjustment during execution
  - Estimated effort might be off by one t-shirt size

### Cumulative Error

Naive multiplication would suggest ~15-30% cumulative error, but in practice, it's lower because:

1. **Validation loops**: Each level is validated against PRD requirements
2. **Overlap**: PRD requirements anchor all levels; if epic is wrong, features would catch it
3. **Iterative refinement**: During task execution, tasks can be split or merged

**Expected cumulative error**: 10-18%

### Mitigation Strategies

1. **Requirement traceability**: Every epic, feature, and task mapped back to PRD
2. **Sanity checks**: Epic count (3-7), feature count (2-5 per epic), task count (2-7 per feature)
3. **Domain expertise**: Domain-specific patterns reduce guessing
4. **MECE validation**: Catch overlaps and gaps at every level
5. **Execution feedback**: Track which tasks actually need splitting/merging, feed back into patterns

## Complete Decomposition Example

Given a simplified PRD about building a user authentication system:

**PRD Excerpt**:
- Problem: Users lack secure authentication
- Goal: Support SSO and multi-factor authentication
- Requirement: Support OAuth 2.0, SAML, WebAuthn
- Timeline: Q1-Q2

**Decomposition Output**:

```
E-1: Frontend — User Authentication UI
├─ F-1.1: Login form with email/password
│  ├─ T-1.1.1: Create LoginForm component
│  ├─ T-1.1.2: Add email validation
│  └─ T-1.1.3: Add unit tests
├─ F-1.2: OAuth provider selection UI
│  ├─ T-1.2.1: Create OAuthProviderButtons component
│  └─ T-1.2.2: Add routing to OAuth flow
└─ F-1.3: MFA verification interface
   ├─ T-1.3.1: Create MFAChallenge component
   └─ T-1.3.2: Add challenge submission logic

E-2: Backend — OAuth 2.0 Integration
├─ F-2.1: OAuth authorization code flow
│  ├─ T-2.1.1: Implement OAuth grant handler
│  ├─ T-2.1.2: Create OAuth token service
│  └─ T-2.1.3: Add integration tests
├─ F-2.2: User profile sync from provider
│  ├─ T-2.2.1: Design user profile schema
│  ├─ T-2.2.2: Implement profile sync logic
│  └─ T-2.2.3: Add error handling

E-3: Security — Multi-Factor Authentication
├─ F-3.1: TOTP-based MFA
│  ├─ T-3.1.1: Integrate TOTP library
│  ├─ T-3.1.2: Implement MFA setup flow
│  └─ T-3.1.3: Add MFA verification service
└─ F-3.2: WebAuthn support
   ├─ T-3.2.1: Integrate WebAuthn library
   ├─ T-3.2.2: Implement registration flow
   └─ T-3.2.3: Implement authentication flow

E-INFRA-1: Infrastructure — CI/CD Pipeline
├─ F-INFRA-1.1: GitHub Actions setup
│  ├─ T-INFRA-1.1.1: Create build workflow
│  └─ T-INFRA-1.1.2: Create test workflow
└─ F-INFRA-1.2: Automated deployment
   ├─ T-INFRA-1.2.1: Create deployment script
   └─ T-INFRA-1.2.2: Configure staging environment
```

**Validation**:
- ✓ 4 epics (within 3-7 target)
- ✓ 2-3 features per epic (within 2-5 target)
- ✓ 2-3 tasks per feature (within 2-7 target)
- ✓ All PRD requirements mapped to epics
- ✓ Epics are MECE (no overlapping concerns)
- ✓ Features are MECE within each epic
- ✓ Infrastructure epic auto-generated

This decomposition is ready to be passed to the dependency graph engine.
