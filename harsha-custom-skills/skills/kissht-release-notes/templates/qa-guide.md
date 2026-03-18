# QA Impact Assessment Template

## Usage
This template defines the structure for QA-focused release documentation. Emphasizes test scope, regression risk, and specific test scenarios.

---

# Release Notes: [PROJECT] [VERSION] — QA Impact Assessment

**Release Date**: [RELEASE_DATE]
**Overall Risk Level**: [HIGH / MEDIUM / LOW]
**Changes**: [TOTAL_COUNT] tickets ([CRITICAL_COUNT] critical, [HIGH_COUNT] high priority)

---

## Test Impact Summary

| Module | Changes | Risk Level | Test Priority | Key Tickets |
|--------|---------|-----------|--------------|-------------|
| [Category 1] | [N] | [H/M/L] | [P1/P2/P3] | [Keys] |
| [Category 2] | [N] | [H/M/L] | [P1/P2/P3] | [Keys] |

---

## Priority 1: Critical Test Areas

### [CATEGORY]: [SPECIFIC_CHANGE]

**Tickets**: [TICKET_KEYS with links]
**Risk**: [HIGH/MEDIUM] — [Why this is risky]

**What Changed**:
[Technical description of the change — what was the bug, what was fixed, what logic changed]

**Regression Scope**:
- [Existing functionality that could be affected]
- [Adjacent features sharing data or UI]

**Test Scenarios**:

| # | Scenario | Steps | Expected Result | Priority |
|---|----------|-------|----------------|----------|
| 1 | [Happy path] | [Steps] | [Result] | P1 |
| 2 | [Edge case] | [Steps] | [Result] | P1 |
| 3 | [Boundary] | [Steps] | [Result] | P2 |
| 4 | [Error state] | [Steps] | [Result] | P2 |

**Test Data Requirements**:
- [Specific data setup needed]
- [User role/permissions needed]

---

[Repeat for each critical area]

---

## Priority 2: Standard Test Areas

### [CATEGORY]: [CHANGE]
**Tickets**: [KEYS]
**Quick Tests**:
- [ ] [Test 1]
- [ ] [Test 2]

---

## Regression Checklist

### Must Test (Directly Changed)
- [ ] [Area] — Changed in [TICKET] — [What to verify]
- [ ] [Area] — Changed in [TICKET] — [What to verify]

### Should Test (Potentially Affected)
- [ ] [Area] — Shares data with changed module
- [ ] [Area] — Adjacent UI component

### Smoke Test (Sanity)
- [ ] Login & navigation
- [ ] Core loan journey happy path
- [ ] Document upload/download
- [ ] Search functionality

---

## Journey-Based Test Matrix

| Journey Stage | Changes This Sprint | Test Focus |
|--------------|-------------------|-----------|
| Lead → Applicant Valid | [changes] | [focus] |
| Valid → Onboarded | [changes] | [focus] |
| Onboarded → CPA | [changes] | [focus] |
| BRE → Sanction | [changes] | [focus] |
| Sanction → Disbursal | [changes] | [focus] |

---

## Environment Notes
- [Staging differences from production]
- [Feature flags to enable/disable]
- [Test environment data refresh status]

---

## Known Limitations
| Limitation | Impact | Workaround | Fix Sprint |
|-----------|--------|-----------|-----------|
| [Limitation] | [Impact] | [Workaround] | [Sprint] |
