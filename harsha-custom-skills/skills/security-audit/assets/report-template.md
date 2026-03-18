# Security Audit Report

---

**Project:** {{ project_name }}
**Audit Date:** {{ audit_date }}
**Skill Version:** 1.0.0

---

## Executive Summary

**Risk Score:** {{ risk_score }}/100 ({{ risk_level }})

### Finding Summary

| Severity | Count |
|----------|-------|
| Critical | {{ critical_count }} |
| High | {{ high_count }} |
| Medium | {{ medium_count }} |
| Low | {{ low_count }} |
| Info | {{ info_count }} |
| **Total** | **{{ total_count }}** |

### Risk Assessment

{{ risk_assessment_text }}

### Top 5 Issues Requiring Immediate Attention

1. {{ top_issue_1 }}
2. {{ top_issue_2 }}
3. {{ top_issue_3 }}
4. {{ top_issue_4 }}
5. {{ top_issue_5 }}

---

## Findings Overview

| ID | Severity | Domain | Title | CWE | Location | Status |
|----|----------|--------|-------|-----|----------|--------|
{{ findings_table }}

---

## Detailed Findings

### Critical Severity

{{ critical_findings }}

### High Severity

{{ high_findings }}

### Medium Severity

{{ medium_findings }}

### Low Severity

{{ low_findings }}

### Informational

{{ info_findings }}

---

## Finding Detail Template

Use this format for each finding:

```markdown
### {{ finding_id }}: {{ finding_title }}

- **Severity:** {{ severity }}
- **CVSS:** {{ cvss_score }}
- **CWE:** {{ cwe_id }}
- **OWASP:** {{ owasp_category }}
- **Domain:** {{ security_domain }}
- **Location:** `{{ file_path }}:{{ line_number }}`

**Evidence:**
```{{ language }}
{{ code_evidence }}
```

**Impact:** {{ impact_description }}

**Recommended Fix:**
```diff
{{ fix_diff }}
```

**Verification:** {{ verification_steps }}

**Non-Invasive Checklist:**
- [ ] 1. Zero UI/UX changes
- [ ] 2. Identical outputs
- [ ] 3. User flows unchanged
- [ ] 4. API contracts unchanged
- [ ] 5. No performance regression
- [ ] 6. Error messages unchanged
- [ ] 7. Config additive-only
- [ ] 8. No new runtime deps
- [ ] 9. Minimal diff
- [ ] 10. Trivially reversible

**Status:** {{ all_pass | requires_review }}
```

---

## Implementation Roadmap

### Phase 1: Immediate (0-48 hours)
*Configuration and dependency fixes - lowest risk changes*

{{ phase1_items }}

### Phase 2: Short-term (1-2 weeks)
*Validation wrappers and sanitization - moderate complexity*

{{ phase2_items }}

### Phase 3: Medium-term (2-4 weeks)
*Authentication, access control, and business logic - requires more testing*

{{ phase3_items }}

---

## Verification Plan

### Per-Fix Verification

For each fix applied:

1. **Baseline Capture**
   ```bash
   # Capture current state
   curl -s api/endpoint > baseline.json
   npm test > baseline_tests.txt
   ```

2. **Apply Fix**
   - Implement recommended change
   - Commit with clear message

3. **Verify Fix**
   ```bash
   # Compare responses
   curl -s api/endpoint > postfix.json
   diff baseline.json postfix.json

   # Run tests
   npm test

   # Verify security issue resolved
   # (specific verification per fix type)
   ```

4. **Regression Check**
   - Full test suite passes
   - No new errors in logs
   - Performance unchanged

### Overall Verification

```bash
# After all fixes applied
npm test  # All tests pass
npm run lint  # No new warnings
curl -sI https://app.example.com | grep -E "X-Frame|X-Content|Strict-Transport"  # Headers present
```

---

## Appendix

### Severity Definitions

| Severity | CVSS | Description |
|----------|------|-------------|
| Critical | 9.0-10.0 | Immediate exploitation risk, major business impact |
| High | 7.0-8.9 | Significant vulnerability, should fix within days |
| Medium | 4.0-6.9 | Moderate risk, schedule fix within weeks |
| Low | 0.1-3.9 | Minor issue, address during normal maintenance |
| Info | 0 | Best practice recommendation, not a vulnerability |

### Non-Invasive Fix Criteria

All fixes must satisfy these 10 criteria:

1. **Zero UI/UX changes** - No visual, layout, interaction, or rendering modifications
2. **Identical outputs** - Same input produces exactly same output
3. **User flows unchanged** - No new steps, removed steps, or reordering
4. **API contracts unchanged** - Same request/response schemas, status codes, headers
5. **No performance regression** - No observable slowdown (within 10%)
6. **Error messages unchanged** - User-facing errors identical
7. **Config additive-only** - New config with safe defaults, no removed options
8. **No new runtime deps** - Prefer stdlib, existing deps, or dev-only tools
9. **Minimal diff** - Smallest change that addresses the vulnerability
10. **Trivially reversible** - Single git revert undoes the fix

### References

- OWASP Top 10 (2021): https://owasp.org/Top10/
- CWE Top 25 (2023): https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html
- NIST CVE Database: https://nvd.nist.gov/

---

*🤖 Generated with [Claude Code](https://claude.com/claude-code)*
