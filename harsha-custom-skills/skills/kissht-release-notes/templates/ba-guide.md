# Business Analyst Impact Analysis Template

## Usage
For BAs. Maps changes to business processes, data flows, and requirements.

---

# Release Analysis: [PROJECT] [VERSION] — Business Analyst View

**Release Date**: [DATE]
**Sprint**: [SPRINT_NAME]
**Total Changes**: [COUNT]

---

## Process Impact Assessment

### [JOURNEY_STAGE]: [CHANGE_SUMMARY]

**Affected Process**: [Business process name from BRD/PRD]
**Change Type**: [New Feature / Modified Process / Bug Fix / Removed Feature]
**Impact Level**: [HIGH / MEDIUM / LOW]

**Impact Analysis**:

| Dimension | Before | After | Impact |
|-----------|--------|-------|--------|
| Data Flow | [How data moved] | [How data moves now] | [Effect] |
| Business Rules | [Old rule] | [New rule] | [Effect] |
| User Experience | [Old UX] | [New UX] | [Effect] |
| Integration | [Old integration] | [New integration] | [Effect] |

**Tickets**: [KEYS with links]

**Requirements Reference**: [BRD/PRD section if traceable]

---

[Repeat per journey stage change]

---

## Journey Stage Impact Matrix

| Journey Stage | Changes | Impact Level | Tickets | Process Owner |
|--------------|---------|-------------|---------|--------------|
| Lead → Valid | [summary] | [H/M/L] | [keys] | [owner] |
| Valid → Onboarded | [summary] | [H/M/L] | [keys] | [owner] |
| Onboarded → CPA | [summary] | [H/M/L] | [keys] | [owner] |
| BRE → Sanction | [summary] | [H/M/L] | [keys] | [owner] |
| Sanction → Disbursal | [summary] | [H/M/L] | [keys] | [owner] |

---

## Integration Changes

| Source System | Target System | Change | Business Impact | Tickets |
|-------------|--------------|--------|----------------|---------|
| [Saral/LSQ] | [LOS/LAP] | [What changed] | [Business effect] | [Keys] |

---

## Business Rule Changes

| Rule | Module | Before | After | Affected Users | Ticket |
|------|--------|--------|-------|---------------|--------|
| [Rule name] | [Module] | [Old logic] | [New logic] | [Roles] | [Key] |

---

## Data Model Observations

| Entity | Field | Change | Business Rule Affected |
|--------|-------|--------|----------------------|
| [Entity] | [Field] | [Change] | [Rule] |

---

## Requirements Traceability

| Requirement (BRD/PRD) | Status | Ticket(s) | Gap Notes |
|-----------------------|--------|-----------|-----------|
| [Requirement text] | [Complete / Partial / Deferred] | [Keys] | [Notes] |

---

## Recommendations

### Process Updates Needed
1. [Process that needs updating based on this release]
2. [Process that needs updating]

### Requirements Gaps Identified
1. [Gap between what was required and what was delivered]

### Follow-up Items
1. [Item needing further analysis or next-sprint attention]
