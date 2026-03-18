# Operations Runbook Update Template

## Usage
For Ops team. Focuses on deployment, monitoring, rollback, and operational impact.

---

# Release Notes: [PROJECT] [VERSION] — Operations Runbook

**Release Date**: [DATE]
**Deployment Window**: [TIME]
**Risk Level**: [CRITICAL / STANDARD / LOW]
**On-Call**: [NAME]

---

## Deployment Summary

| Item | Detail |
|------|--------|
| Version | [VERSION] |
| Environment | [Production / Staging] |
| Total Tickets | [COUNT] |
| Critical Fixes | [COUNT] |
| Services Affected | [SERVICE_LIST] |
| Downtime Expected | [None / X minutes] |
| Rollback Available | [Yes / No] |

---

## Pre-Deployment Checklist

- [ ] Staging verification complete
- [ ] Database migrations reviewed (if any)
- [ ] Feature flags configured
- [ ] Monitoring dashboards open
- [ ] Rollback plan documented
- [ ] On-call team notified
- [ ] Stakeholders informed of deployment window

---

## Changes with Operational Impact

### [CHANGE_TITLE] ([TICKET_KEYS])

**Impact**: [What ops needs to know]
**Action Required**: [What to do / monitor]
**Escalation**: [Who to contact if issues arise]

---

## Post-Deployment Verification

- [ ] [Service 1] health check passing
- [ ] [Service 2] response times normal
- [ ] [Feature 1] functional verification
- [ ] Error rates within baseline
- [ ] No unexpected alerts triggered
- [ ] User-facing functionality spot-checked

---

## Monitoring Changes

| Service/Metric | Alert | Threshold | Action |
|---------------|-------|-----------|--------|
| [service] | [alert name] | [threshold] | [what to do] |

---

## Rollback Procedure

**Trigger**: Roll back if [conditions]

1. [Step 1]
2. [Step 2]
3. [Step 3]
4. Notify: [PM, Dev lead, Stakeholders]

**Rollback Window**: [Time after which rollback is not recommended]

---

## Known Issues

| Issue | Impact | Workaround | Fix ETA | Ticket |
|-------|--------|-----------|---------|--------|
| [Issue] | [Impact] | [Workaround] | [ETA] | [Key] |

---

## Escalation Matrix

| Area | Primary Contact | Secondary | Slack Channel |
|------|----------------|-----------|--------------|
| [Area 1] | [Name] | [Name] | [#channel] |
| [Area 2] | [Name] | [Name] | [#channel] |

---

## Post-Release Actions

- [ ] [One-time action needed after deployment]
- [ ] Update monitoring thresholds for [service]
- [ ] Close deployment ticket
- [ ] Update release log
