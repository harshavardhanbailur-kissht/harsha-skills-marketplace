# Verification Report Template

Output format for the debugging agent after verifying task execution.

---

# Verification Report: [Task Title]

**Task ID**: #[number]
**Verified**: [YYYY-MM-DD HH:MM]
**Overall Status**: ✅ PASS | ❌ FAIL | ⚠️ PARTIAL
**Confidence**: [0.0-1.0]

---

## Executive Summary

[One paragraph: Did the execution meet the original plan? What's the verdict?]

---

## Automated Check Results

| Check | Status | Details |
|-------|--------|---------|
| Build | ✅/❌ | [Build output summary] |
| Tests | ✅/❌ | [X/Y tests passing] |
| Coverage | ✅/❌ | [X% (threshold: Y%)] |
| Linting | ✅/❌ | [N issues] |
| Security | ✅/❌ | [Scan results] |

---

## Acceptance Criteria Verification

### Criterion 1: [Criterion Text]
**Status**: ✅ PASS | ❌ FAIL | ⚠️ CANNOT_VERIFY

**Evidence**:
[What demonstrates this criterion is met/unmet]

**Gap** (if not PASS):
[What's missing or wrong]

---

### Criterion 2: [Criterion Text]
**Status**: ✅ PASS | ❌ FAIL | ⚠️ CANNOT_VERIFY

**Evidence**:
[Evidence description]

**Gap** (if not PASS):
[Gap description]

---

[Repeat for all criteria]

---

## Scope Analysis

### Missing (Specified but Not Implemented)
| Item | Impact | Recommendation |
|------|--------|----------------|
| [Missing item] | [Critical/High/Medium/Low] | [Action] |

### Extraneous (Implemented but Not Specified)
| Item | Assessment | Recommendation |
|------|------------|----------------|
| [Extra item] | [Beneficial/Neutral/Harmful] | [Keep/Remove/ADR] |

### Deviated (Different from Specification)
| Item | Specification | Implementation | Assessment |
|------|---------------|----------------|------------|
| [Item] | [What was specified] | [What was built] | [Accept/Reject] |

---

## Errors Identified

### Error 1: [Error Title]
**Type**: Missing | Incomplete | Wrong | Deviated | Extraneous | Regression | Integration | Context_Loss
**Severity**: Critical | High | Medium | Low
**Priority**: P1 | P2 | P3 | P4

**Description**:
[Detailed description of the error]

**Root Cause Analysis**:
- **Immediate cause**: [What directly caused it]
- **Contributing factors**: [What enabled it]
- **Root cause**: [Fundamental reason]
- **Category**: Plan_Error | Execution_Error | Environmental | Context_Loss

**Remediation**:
- **Recommendation**: Patch | Replan | Defer
- **Effort estimate**: [Time]
- **Suggested fix**: [Description]

---

[Repeat for additional errors]

---

## Traceability Matrix

| Requirement | Criterion | Implementation | Test | Status |
|-------------|-----------|----------------|------|--------|
| REQ-001 | [G/W/T] | [file:lines] | [test file] | ✅/❌ |
| REQ-002 | [G/W/T] | [file:lines] | [test file] | ✅/❌ |

---

## Recommendations

### Immediate Actions
1. [Critical action required before closing task]
2. [Additional action]

### Follow-up Tasks to Create
- [ ] [New task spawned by this verification]
- [ ] [Another new task]

### Process Improvements
- [Observation about how similar issues could be prevented]

---

## Requires Human Review

| Item | Reason | Reviewer |
|------|--------|----------|
| [Item needing judgment] | [Why AI can't determine] | [Suggested reviewer] |

---

## Verification Metadata

**Verification Method**: Automated + AI-Assisted + Manual Review
**Time Spent**: [Duration]
**Artifacts Reviewed**:
- [List of files, commits, logs reviewed]

**Limitations**:
- [What couldn't be verified and why]

---

## Sign-Off

**Verification Status**: COMPLETE | INCOMPLETE
**Ready for Closure**: YES | NO | CONDITIONAL

**Conditions for Closure** (if conditional):
1. [Condition that must be met]
2. [Another condition]

---

## JSON Output (For Programmatic Processing)

```json
{
  "task_id": "[number]",
  "overall_status": "PASS|FAIL|PARTIAL",
  "confidence": 0.85,
  "criteria_results": [
    {
      "criterion": "[text]",
      "status": "PASS|FAIL|CANNOT_VERIFY",
      "evidence": "[text]",
      "gap_description": null
    }
  ],
  "scope_analysis": {
    "missing": [],
    "extraneous": [],
    "deviated": []
  },
  "errors": [
    {
      "type": "Missing",
      "severity": "Medium",
      "description": "[text]",
      "root_cause": "[text]",
      "remediation": "Patch|Replan|Defer"
    }
  ],
  "recommendations": [],
  "requires_human_review": [],
  "ready_for_closure": true
}
```
