# Compliance Mapping Template

**Framework**: {{COMPLIANCE_FRAMEWORK}} | **Version**: {{FRAMEWORK_VERSION}} | **Scope**: {{SCOPE}}

**Project**: {{PROJECT_NAME}} | **Assessment Date**: {{DATE}} | **Assessor**: {{NAME}}

---

## Executive Summary

{{2-3 paragraph overview of compliance status}}

**Overall Compliance Score**: {{SCORE}}/10 ({{PERCENTAGE}}%)

**Status**:
- ✓ {{COMPLIANT_COUNT}} Requirements Met
- ⚠️ {{PARTIAL_COUNT}} Partial Implementations
- ✗ {{NON_COMPLIANT_COUNT}} Not Compliant
- — {{NOT_APPLICABLE_COUNT}} Not Applicable

---

## Compliance Framework Overview

**Framework**: {{FRAMEWORK_NAME}} ({{FRAMEWORK_ACRONYM}})

**Scope of Framework**: {{What does this framework apply to?}}

**Regulatory Authority**: {{Authority}}

**Applicability to This Project**: {{Why this framework applies}}

---

## Regulatory Requirements → Code Mapping

### Requirement 1: {{REQUIREMENT_NAME}}

| Aspect | Details |
|--------|---------|
| **Framework Reference** | {{Reference section/article}} |
| **Requirement Text** | "{{Verbatim requirement from framework}}" |
| **Applicability** | {{Always / Conditional / N/A}} |

#### Code Implementation

**Mapping Status**: ✓ **COMPLIANT** | ⚠️ **PARTIAL** | ✗ **NON-COMPLIANT** | — **N/A**

**Location(s)**:
- File: `src/{{path}}/{{file}}.{{ext}}`, Line {{START}}–{{END}}
- Class: `{{ClassName}}.{{MethodName}}`
- Configuration: `{{CONFIG_FILE}}`

**Implementation Details**:

```{{LANGUAGE}}
// Code snippet demonstrating compliance
{{CODE_SAMPLE}}
```

**Evidence**:
- ✓ Unit test: `tests/{{test_file}}.test.js`
- ✓ Integration test: `tests/integration/{{test_file}}.test.js`
- ✓ Audit log: Can verify in {{MONITORING_SYSTEM}}
- ✓ Configuration: Hardcoded in {{CONFIG_FILE}}

**Verification Process**:
1. {{Step 1}}: {{How to verify this requirement}}
2. {{Step 2}}: {{How to verify this requirement}}
3. {{Step 3}}: {{How to verify this requirement}}

**Control Strength**: {{Automated / Manual / Compensating / Design-level}}

---

### Requirement 2: {{REQUIREMENT_NAME}}

| Aspect | Details |
|--------|---------|
| **Framework Reference** | {{Reference}} |
| **Requirement Text** | "{{Requirement}}" |

#### Code Implementation

**Mapping Status**: ✓ **COMPLIANT**

**Location(s)**: `src/{{path}}`

**Implementation Details**: {{Explanation}}

**Verification**: {{How to verify}}

---

## Gap Analysis

### Gap 1: {{GAP_DESCRIPTION}}

| Aspect | Details |
|--------|---------|
| **Requirement** | {{Which requirement is not met}} |
| **Current State** | {{What's currently in place}} |
| **Expected State** | {{What should be in place}} |
| **Risk Level** | {{CRITICAL | HIGH | MEDIUM | LOW}} |
| **Business Impact** | {{What could go wrong}} |
| **Audit Risk** | {{What auditor might flag}} |

**Remediation Plan**:
1. {{Action 1}}: {{Description}}, Owner: {{Person}}, Timeline: {{Date}}
2. {{Action 2}}: {{Description}}, Owner: {{Person}}, Timeline: {{Date}}
3. {{Action 3}}: {{Description}}, Owner: {{Person}}, Timeline: {{Date}}

**Workaround** (temporary):
```
{{Temporary mitigation while permanent fix is being implemented}}
```

**Success Criteria**:
- [ ] {{Criterion 1}}
- [ ] {{Criterion 2}}
- [ ] {{Criterion 3}}

---

### Gap 2: {{GAP_DESCRIPTION}}

| Aspect | Details |
|--------|---------|
| **Requirement** | {{Requirement}} |
| **Current State** | {{Current}} |
| **Expected State** | {{Expected}} |
| **Risk Level** | {{CRITICAL | HIGH | MEDIUM | LOW}} |

**Remediation Plan**: {{Steps to close gap}}

---

## Compliance Dashboard

### Requirement Coverage by Category

| Category | Met | Partial | Missing | N/A | Score |
|----------|-----|---------|---------|-----|-------|
| {{Category 1}} | {{#}} | {{#}} | {{#}} | {{#}} | {{%}} |
| {{Category 2}} | {{#}} | {{#}} | {{#}} | {{#}} | {{%}} |
| {{Category 3}} | {{#}} | {{#}} | {{#}} | {{#}} | {{%}} |
| **TOTAL** | {{#}} | {{#}} | {{#}} | {{#}} | {{%}} |

### Trend

```
Compliance Score Over Time:

v1.0 (Jan 2024):  ████░░░░░░░░░░░░░░░ 45%
v1.5 (Apr 2024):  ████████░░░░░░░░░░░░ 60%
v2.0 (Jul 2024):  ███████████░░░░░░░░░ 75%
v2.5 (Oct 2024):  ██████████████░░░░░░ 85%
Current (Now):    ████████████████░░░░ 92%

Target: ██████████████████░░ 95%
```

---

## Risk Assessment

### High-Risk Gaps

| Gap | Likelihood | Impact | Overall Risk | Timeline to Fix |
|-----|-----------|--------|--------------|-----------------|
| {{Gap}} | High | Critical | 🔴 {{CRITICAL}} | {{Date}} |
| {{Gap}} | Medium | Critical | 🔴 {{HIGH}} | {{Date}} |
| {{Gap}} | Medium | High | 🟠 {{HIGH}} | {{Date}} |

### Medium-Risk Gaps

| Gap | Likelihood | Impact | Overall Risk | Timeline to Fix |
|-----|-----------|--------|--------------|-----------------|
| {{Gap}} | Medium | Medium | 🟠 {{MEDIUM}} | {{Date}} |
| {{Gap}} | Low | High | 🟠 {{MEDIUM}} | {{Date}} |

### Low-Risk Gaps

| Gap | Status | Timeline |
|-----|--------|----------|
| {{Gap}} | 🟡 {{LOW}} | {{Date}} |

---

## Audit Trail & Monitoring

### Automated Monitoring

| Control | Check | Frequency | Alert |
|---------|-------|-----------|-------|
| {{Control}} | {{What's monitored}} | {{Frequency}} | {{Alert condition}} |
| {{Control}} | {{What's monitored}} | {{Frequency}} | {{Alert condition}} |

**Monitoring Dashboard**: {{LINK_TO_MONITORING}}

### Manual Audits

| Control | Audit Procedure | Frequency | Owner | Last Verified |
|---------|---------|-----------|-------|---|
| {{Control}} | {{Procedure}} | Quarterly | {{Person}} | {{Date}} |
| {{Control}} | {{Procedure}} | Annually | {{Person}} | {{Date}} |

### Audit Log Access

**Who Can Review Audit Logs**: {{Roles/Teams}}

**Retention Policy**: {{Duration}} ({{Legal basis}})

**Immutability**: {{Guaranteed by}}: {{Mechanism}}

---

## Evidence & Documentation

### Supporting Documentation

| Document | Location | Updated | Owner |
|----------|----------|---------|-------|
| {{Document}} | {{Link}} | {{Date}} | {{Person}} |
| {{Document}} | {{Link}} | {{Date}} | {{Person}} |
| {{Document}} | {{Link}} | {{Date}} | {{Person}} |

### Evidence Artifacts

**Policy Documents**:
- [{{Policy Name}}]({{LINK}}) — {{Description}}
- [{{Policy Name}}]({{LINK}}) — {{Description}}

**Test Evidence**:
- Unit test coverage: {{LINK_TO_REPORT}}
- Integration test results: {{LINK_TO_REPORT}}
- Penetration test report: {{LINK_TO_REPORT}}

**Configuration Evidence**:
- IaC code: `{{PATH}}`
- Config files: `{{PATH}}`
- Secrets management: {{LOCATION}}

---

## Compliance Roadmap

### Q1 2025

- [ ] {{Action}} — Owner: {{Person}}, Target: {{Date}}
- [ ] {{Action}} — Owner: {{Person}}, Target: {{Date}}

### Q2 2025

- [ ] {{Action}} — Owner: {{Person}}, Target: {{Date}}
- [ ] {{Action}} — Owner: {{Person}}, Target: {{Date}}

### Q3–Q4 2025

- [ ] {{Action}} — Owner: {{Person}}, Target: {{Date}}

---

## Pre-Audit Checklist

Before formal audit, verify:

- [ ] All requirements have been assessed (mapped/compliant/gap)
- [ ] All gaps have remediation plans
- [ ] All critical gaps have workarounds in place
- [ ] Monitoring is active and alerting
- [ ] Documentation is up-to-date and linked
- [ ] Evidence artifacts are accessible and current
- [ ] Audit logs are immutable and accessible
- [ ] Team is trained on compliance requirements
- [ ] Incidents have been investigated and documented
- [ ] Third-party integrations have been verified for compliance

---

## Compliance Contacts

| Role | Name | Email | Slack |
|------|------|-------|-------|
| **Compliance Owner** | {{Name}} | {{Email}} | {{Slack}} |
| **Security Lead** | {{Name}} | {{Email}} | {{Slack}} |
| **Audit Coordinator** | {{Name}} | {{Email}} | {{Slack}} |
| **Legal/Regulatory** | {{Name}} | {{Email}} | {{Slack}} |

---

## Related Compliance Mappings

- [{{Framework 1}} Mapping](./compliance-{{framework1}}.md)
- [{{Framework 2}} Mapping](./compliance-{{framework2}}.md)

---

## Appendix: Framework Definition

### {{FRAMEWORK_NAME}} Overview

{{Description of the framework, its history, applicability, and importance}}

**Key Principles**:
1. {{Principle 1}}: {{Explanation}}
2. {{Principle 2}}: {{Explanation}}
3. {{Principle 3}}: {{Explanation}}

**Key Requirements**:
1. {{Requirement 1}}: {{Explanation}}
2. {{Requirement 2}}: {{Explanation}}
3. {{Requirement 3}}: {{Explanation}}

**External Reference**: {{LINK_TO_OFFICIAL_DOCUMENTATION}}

---

**Assessment Date**: {{DATE}} | **Assessor**: {{NAME}} | **Next Review**: {{DATE}} | **Status**: {{CURRENT | OUTDATED}}
