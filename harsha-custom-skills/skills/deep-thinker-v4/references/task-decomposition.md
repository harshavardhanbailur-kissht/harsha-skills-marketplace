# Task Decomposition: MECE & Hierarchical Thinking Networks

## MECE Framework (Mutually Exclusive, Collectively Exhaustive)

**Goal**: Break problem into non-overlapping pieces that cover 100% of scope.

**Mutually Exclusive**: Each piece is standalone; solving one doesn't solve another.
- BAD: [Update auth], [Update email verification], [Update password reset] - all overlap on auth changes.
- GOOD: [Implement new auth mechanism], [Migrate existing users], [Deprecate old mechanism] - distinct phases.

**Collectively Exhaustive**: Together, pieces cover the full solution.
- BAD: [Frontend changes], [Backend changes] - missing migration, monitoring, rollback.
- GOOD: [Frontend], [Backend], [Data migration], [Testing], [Monitoring], [Rollback plan] - complete end-to-end.

**Test MECE**:
- Can pieces be solved in parallel or different sprints? If pieces are tightly coupled, they overlap.
- Is every concern addressed? If you ship just piece #1, can it work alone or does it need pieces #2, #3?
- Are there gaps? After completing all pieces, is the problem fully solved?

## Hierarchical Thinking Networks

Compound analysis (break into sub-analyses) vs Primitive analysis (direct decision):

**Level 1 (Compound)**: "Add mobile number login alongside email"
- Level 2 (Compound): "Implement mobile login flow"
  - Level 3 (Primitive): Update login form UI
  - Level 3 (Primitive): Validate phone format and region code
  - Level 3 (Primitive): Implement SMS OTP sending
  - Level 3 (Primitive): Handle OTP retry logic
- Level 2 (Compound): "Migrate existing email-only users"
  - Level 3 (Primitive): Data migration script
  - Level 3 (Primitive): User notification campaign
  - Level 3 (Primitive): Rollback procedure
- Level 2 (Compound): "Deprecate email login"
  - Level 3 (Primitive): Implement feature flag for email login
  - Level 3 (Primitive): Gradual user migration schedule
  - Level 3 (Primitive): Monitoring/alerting

Push down only to primitives (items <1 day work). Stop at compounds for now.

## Dependency Mapping with DAG Validation

Create Directed Acyclic Graph of task dependencies:

```
[Data Model Update] → [API Contracts] → [Backend Implementation] → [Testing]
                                      ↘                         ↗
[Feature Flag Setup] ─────────────────────→ [Frontend Implementation]
```

**Critical Path**: Longest chain determines project duration. Parallelize non-critical items.

**Adapter Compatibility**: If task is for adapter implementation, validate:
- Dependencies must be resolvable before implementation starts
- No circular dependencies (would block execution)
- Critical path must fit within sprint

**Validation**:
- [ ] No backward edges (would create cycle)
- [ ] All leaf nodes are concrete (no open-ended "later" tasks)
- [ ] Critical path identified explicitly

## Decomposition Prompts

Use these to break down compound analysis:

1. **Sequential Thinking**: "What must be true first for this to work?" Identifies dependency order.
2. **By Lifecycle**: "What phases does this go through?" (Design, Build, Test, Deploy, Monitor)
3. **By Stakeholder**: "Who owns each part?" (Frontend team, Backend team, DevOps, Support)
4. **By Risk**: "What could go wrong?" Separates high-risk items for early validation
5. **By Reversibility**: "What's easy to undo vs hard to undo?" Undo-hard items go first.

## Adapter-Compatible Task Format

Tasks must be decomposable into analyzer's format:

**Each Phase** (e.g., "Design", "Implement Mobile Flow"):
- List of checkbox items (atomic actions)
- File paths affected
- Dependency language ("after Phase X is VERIFIED")
- Verification criteria ("All tests pass", "Code review approved")

**Template**:
```
## Phase: [Name]
Depends on: [Phase X status]

- [ ] [Atomic action]: [file path]
- [ ] [Atomic action]: [file path]

Verification: [how to know this phase is done]
```

## Worked Example: "Add Mobile Number Login Alongside Email"

**Phase 1: Data Model & API Contracts**
Depends on: None (can start immediately)
- [ ] Add phone_number field to User schema: `app/models/user.ts`
- [ ] Define SMS OTP table with expiry: `app/models/otp.ts`
- [ ] Document new auth endpoints: `docs/api/auth.md`

Verification: API contracts reviewed, schema migrations written

**Phase 2: Backend Implementation**
Depends on: Phase 1 VERIFIED
- [ ] Implement phone validation (region code, format): `app/auth/validate-phone.ts`
- [ ] Integrate SMS provider (Twilio/Nexmo): `app/services/sms.ts`
- [ ] Build OTP generation/verification logic: `app/auth/otp.ts`
- [ ] Implement login endpoints: `app/routes/auth-mobile.ts`
- [ ] Add database migration script: `migrations/add_phone_login.sql`

Verification: All unit tests pass, integration tests with SMS provider mock pass

**Phase 3: Frontend Implementation**
Depends on: Phase 2 VERIFIED AND Phase 1 VERIFIED (API contracts stable)
- [ ] Create mobile login form component: `web/components/MobileLoginForm.tsx`
- [ ] Add phone input field with country selector: `web/components/PhoneInput.tsx`
- [ ] Implement OTP input/verification flow: `web/components/OTPInput.tsx`
- [ ] Update login route to show both options: `web/pages/login.tsx`

Verification: E2E tests with real backend pass, responsive design tested

**Phase 4: Testing & Monitoring**
Depends on: Phase 3 VERIFIED
- [ ] Write E2E test suite: `tests/e2e/mobile-login.spec.ts`
- [ ] Add monitoring/alerting for SMS failures: `app/monitoring/sms-alerts.ts`
- [ ] Create runbook for SMS provider outage: `docs/runbooks/sms-outage.md`

Verification: All E2E tests pass, monitoring dashboard shows SMS success rate

**Phase 5: Deployment & Migration**
Depends on: Phase 4 VERIFIED
- [ ] Create feature flag for mobile login: `config/feature-flags.ts`
- [ ] Plan gradual rollout (10% → 50% → 100%): `docs/deployment/mobile-login-rollout.md`
- [ ] Write user notification email: `emails/mobile-login-available.tsx`

Verification: Feature flag deployed and tested in staging, rollout plan approved

## Validation Checklist

Before finalizing decomposition:
- [ ] MECE test passed (no overlaps, complete coverage)
- [ ] DAG is acyclic (no circular dependencies)
- [ ] Critical path identified (longest dependency chain)
- [ ] Each item <1 day (if >1 day, decompose further)
- [ ] Reversibility marked for high-risk items
- [ ] Verification criteria are testable (not vague)
