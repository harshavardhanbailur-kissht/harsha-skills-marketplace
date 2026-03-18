# Research Spike Template

Use this template for timeboxed research tasks where the output is **knowledge**, not code.
Research spikes are fundamentally different from implementation tasks.

---

## Template

```markdown
## SPIKE: [Question to Answer]

**Timebox**: [Fixed time investment - e.g., 4 hours]
**Phase**: [Project phase]
**Status**: Not Started | In Progress | Complete

### Question
[What specific thing are we trying to learn? Frame as a clear question.]

### Why This Matters
[Why do we need to answer this question? What's blocked without this knowledge?]

### Scope
**In scope**:
- [What to investigate]
- [What to investigate]

**Out of scope**:
- [What NOT to investigate]
- [What NOT to investigate]

### Approach
[How will you investigate? What sources/methods will you use?]

1. [Research step 1]
2. [Research step 2]
3. [Research step 3]

### Output Required
Even if timebox expires, deliver one of:
- [ ] Decision document with recommendation
- [ ] Proof of concept demonstrating feasibility
- [ ] "Need another spike because [specific reason]"

### Evaluation Criteria
[How will you evaluate options? What factors matter?]

| Criterion | Weight | Notes |
|-----------|--------|-------|
| [Factor 1] | High/Med/Low | [What "good" looks like] |
| [Factor 2] | High/Med/Low | [What "good" looks like] |
| [Factor 3] | High/Med/Low | [What "good" looks like] |

### May Spawn
[What follow-up tasks might this spike create?]
- [Potential task 1]
- [Potential task 2]

---

## Findings (Complete After Research)

### Summary
[1-2 sentence answer to the original question]

### Recommendation
[Clear recommendation with brief justification]

### Evidence

#### [Option 1 Name]
- **Pros**: 
- **Cons**: 
- **Score**: [X/5]

#### [Option 2 Name]
- **Pros**: 
- **Cons**: 
- **Score**: [X/5]

### Decision
[Final decision - links to ADR if architectural]

### Spawned Tasks
- Task #XX: [Description]
- Task #YY: [Description]
```

---

## Filled Example

```markdown
## SPIKE: Evaluate State Management Solutions for React Native App

**Timebox**: 4 hours
**Phase**: Phase 1 - Foundation
**Status**: Complete

### Question
Which state management library should we use for our React Native app that requires 
offline-first capabilities with sync?

### Why This Matters
Current useState/useContext approach is becoming unwieldy at ~50 components. Need 
to decide before building new features to avoid rework. Team of 3 mid-level devs 
needs reasonable learning curve.

### Scope
**In scope**:
- Redux Toolkit
- Zustand
- Jotai
- MobX

**Out of scope**:
- Backend state solutions (React Query, SWR)
- Building custom solution
- Deep performance benchmarking

### Approach
1. Review documentation for each option
2. Build minimal todo app with offline persistence in each
3. Evaluate against criteria
4. Write recommendation

### Output Required
- [x] Decision document with recommendation

### Evaluation Criteria

| Criterion | Weight | Notes |
|-----------|--------|-------|
| TypeScript integration | High | Full type safety required |
| Offline persistence | High | Must support local-first with sync |
| DevTools/debugging | Medium | Need visibility into state |
| Bundle size | Medium | Mobile app, size matters |
| Learning curve | Medium | Team has 3 mid-level devs |

### May Spawn
- Migration plan task
- State architecture documentation task
- Team training task

---

## Findings

### Summary
Zustand is the recommended choice, offering the best balance of simplicity, 
TypeScript support, and persistence capabilities for our team size and requirements.

### Recommendation
Use **Zustand** with `zustand/middleware` for persistence. It provides excellent 
TypeScript support, minimal boilerplate, and the `persist` middleware handles 
offline storage elegantly.

### Evidence

#### Redux Toolkit
- **Pros**: Excellent DevTools, large ecosystem, team has some familiarity
- **Cons**: Significant boilerplate, persistence requires additional setup
- **Score**: 3/5

#### Zustand
- **Pros**: Minimal boilerplate, excellent TypeScript, built-in persist middleware, tiny bundle
- **Cons**: Smaller ecosystem, less structured patterns
- **Score**: 5/5

#### Jotai
- **Pros**: Atomic model fits some use cases, minimal bundle
- **Cons**: Persistence is awkward, less documentation
- **Score**: 2/5

#### MobX
- **Pros**: Automatic reactivity, familiar OOP patterns
- **Cons**: Decorators/proxies complicate debugging, larger bundle
- **Score**: 3/5

### Decision
Zustand selected. See ADR-007 for full decision record.

### Spawned Tasks
- Task #31: Set up Zustand with persistence middleware
- Task #32: Create state architecture documentation
- Task #33: Migrate existing context to Zustand stores
```

---

## Research Spike Best Practices

### Before Starting
- [ ] Question is specific and answerable
- [ ] Timebox is realistic (2-8 hours typical)
- [ ] Scope boundaries are clear
- [ ] Evaluation criteria defined upfront

### During Research
- [ ] Track time to respect timebox
- [ ] Take notes as you go (don't rely on memory)
- [ ] If discovering major unexpected info, note it but stay focused
- [ ] Test assumptions with minimal proof-of-concept if feasible

### At Timebox End
- [ ] Produce required output even if incomplete
- [ ] If more time needed, specify exactly what and why
- [ ] Document what was learned, even negative findings
- [ ] Create spawned tasks immediately while context is fresh

### Common Mistakes
| Mistake | Fix |
|---------|-----|
| Unbounded exploration | Set hard timebox, stick to it |
| No required output | Even "need more research" is valid output |
| Investigating everything | Stay within defined scope |
| Premature deep-dive | Breadth first, depth on promising options |
| Forgetting to document | Write findings before moving on |

---

## When Research Invalidates Work

If research proves planned approach wrong:
1. **Don't hoard invalid tasks** - Delete them
2. **Document why** - Important negative knowledge
3. **Re-plan with new knowledge** - Important work will resurface when re-shaped
4. **This is success** - Better to learn now than after implementation
