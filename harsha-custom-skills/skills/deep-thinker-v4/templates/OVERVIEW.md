# OVERVIEW: Scope & Problem Definition

## Goal
**What is the REAL problem we're solving?**

State the underlying business or technical problem, not the surface symptom. This is the "why" that justifies the entire effort.

---

## Success Criteria
**How do we know we've solved it?** (Checklist)

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] Criterion 4
- [ ] Criterion 5

---

## Scope

### In Scope
- Feature/capability 1
- Feature/capability 2
- Integration point A
- Performance requirement X

### Out of Scope
- Feature/capability we explicitly decided NOT to do
- Third-party system we're NOT integrating with
- Migration path we're deferring
- Optional enhancement

---

## Hard Constraints
**Non-negotiable requirements** — breaking these is a project failure.

| Constraint | Impact | Verification |
|-----------|--------|--------------|
| Security (e.g., no PII in logs) | Regulatory/Legal | Automated scan + manual audit |
| Backwards Compatibility (v3.x) | User experience | Regression testing suite |
| Performance (< 500ms response) | UX acceptable | Load testing |
| Compliance (GDPR/SOC2) | Legal risk | Compliance checklist |

---

## Blast Radius
**What breaks if we get this wrong?**

- Downstream system A (depends on our API contract)
- User workflow B (if we change this UX pattern)
- Internal service C (if latency increases)
- Mobile app D (if we break platform integration)

---

## Dependencies

### External
- Third-party service: API endpoint, rate limits, SLA
- Infrastructure: database schema changes, cache layer
- Compliance: regulatory requirement, audit trail

### Internal
- Component X (must update in lockstep)
- Service Y (API contract change required)
- Team Z (review/approval gate)

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Third-party API latency increases | Medium | High | Implement circuit breaker; pre-cache; fallback |
| Database migration deadlocks | Low | Severe | Blue-green schema; run off-peak; dry-run |
| User adoption of new UX pattern | Medium | Medium | Phased rollout; in-app guidance; support plan |
| Backwards compatibility break | Low | Severe | Comprehensive regression suite; canary deploy |
| Performance regression (latency 2x) | Medium | High | Profiling gates; benchmarks in CI; staged rollout |

---

## Next Phase
→ Proceed to **CURRENT_STATE**: What does the existing implementation look like, and what surprised us?
