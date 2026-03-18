# Verification Rubric Templates

Ready-to-use rubrics for the Opus 4.6 verification judge.

---

## General Code Quality Rubric

```
Evaluate this code output against the original requirements.

## Evaluation Criteria

### 1. Completeness (0-1)
Does the output implement ALL requirements from the original request?
- 1.0: All requirements fully implemented
- 0.7: Most requirements implemented, minor gaps
- 0.4: Significant requirements missing
- 0.0: Output doesn't address the requirements

### 2. Correctness (0-1)
Is the implementation logically and syntactically correct?
- 1.0: No bugs, clean syntax, sound logic
- 0.7: Minor issues that don't affect core functionality
- 0.4: Significant bugs or logical errors
- 0.0: Fundamentally broken

### 3. Consistency (0-1)
Is the code style uniform and does it follow conventions?
- 1.0: Consistent naming, formatting, patterns throughout
- 0.7: Mostly consistent with minor deviations
- 0.4: Inconsistent style across sections
- 0.0: No discernible style consistency

### 4. Integration Compatibility (0-1)
Can this output be merged with other agent outputs seamlessly?
- 1.0: Clean interfaces, no conflicts, ready to integrate
- 0.7: Minor adjustments needed for integration
- 0.4: Significant rework needed to integrate
- 0.0: Incompatible with other outputs

### 5. Performance (0-1)
Is the code efficient and free of performance anti-patterns?
- 1.0: Optimal resource usage, no jank, minimal memory footprint
- 0.7: Minor inefficiencies (e.g., some uncached objects)
- 0.4: Clear performance issues (excessive rebuilds, unpaused animations, bloated assets)
- 0.0: Will cause visible jank, memory leaks, or excessive app size

## Output Format

Return JSON:
{
  "verdict": "PASS" or "FAIL",
  "overall_score": 0.0-1.0,
  "criteria": {
    "completeness": {"score": 0.0-1.0, "reasoning": "..."},
    "correctness": {"score": 0.0-1.0, "reasoning": "..."},
    "consistency": {"score": 0.0-1.0, "reasoning": "..."},
    "integration": {"score": 0.0-1.0, "reasoning": "..."},
    "performance": {"score": 0.0-1.0, "reasoning": "..."}
  },
  "issues": ["Issue 1 description", "Issue 2 description"],
  "suggestions": ["Fix suggestion 1", "Fix suggestion 2"]
}

PASS threshold: overall_score >= 0.7 AND no criterion below 0.5
```

---

## API Completeness Rubric

```
Evaluate this API implementation for completeness.

### Endpoints Coverage
- Are all CRUD operations implemented?
- Are authentication endpoints present?
- Are error responses standardized?

### Request/Response Validation
- Input validation on all endpoints?
- Proper HTTP status codes?
- Consistent response format?

### Documentation
- OpenAPI/Swagger spec included?
- Request/response examples?
- Error codes documented?

Return JSON with verdict, scores per criterion, and specific gaps found.
```

---

## Performance Review Rubric

```
Evaluate this code output for performance efficiency.

### Resource Efficiency (0-1)
- Are animations merged/minimized (max 2-3 controllers)?
- Are CustomPainter shouldRepaint conditions optimized (not always true)?
- Are Paint objects static/cached (not created per-frame)?
- Are particle counts device-adaptive (100-500 based on tier)?
- 1.0: Exemplary resource efficiency
- 0.7: Minor inefficiencies
- 0.4: Significant performance issues
- 0.0: Will cause visible jank

### Memory Management (0-1)
- Are subscriptions, controllers, timers properly disposed?
- Are listeners removed when no longer needed?
- Is setState avoided for high-frequency updates (use ValueNotifier)?
- Are images/assets lazily loaded?
- 1.0: No memory leaks or waste
- 0.7: Minor disposal issues
- 0.4: Clear memory leak patterns
- 0.0: Critical memory management failures

### App Size Impact (0-1)
- Are bundled assets minimized (prefer CDN/lazy loading)?
- Are video/image formats optimized (WebP, H.265)?
- Are dependencies lightweight (no unnecessary heavy packages)?
- 1.0: Minimal size impact
- 0.7: Some oversized assets
- 0.4: Significant bloat (>20MB unnecessary)
- 0.0: Extreme bloat

### Platform Optimization (0-1)
- Are platform-specific APIs used where beneficial?
- Is Impeller/Metal rendering considered?
- Are sensor/hardware APIs used efficiently?
- 1.0: Full platform optimization
- 0.7: Mostly platform-aware
- 0.4: Platform-agnostic with missed opportunities
- 0.0: Fighting against the platform

Return JSON with verdict, scores per criterion, and specific performance fixes.
PASS threshold: overall_score >= 0.7 AND no criterion below 0.5
```

---

## Security Review Rubric

```
Evaluate this code for security issues.

### Input Validation
- SQL injection protection?
- XSS prevention?
- CSRF tokens?

### Authentication & Authorization
- Proper password hashing?
- Token validation?
- Role-based access control?

### Data Protection
- No hardcoded secrets?
- Proper error messages (no stack traces leaked)?
- Sensitive data encrypted?

Return JSON with verdict, severity ratings (critical/high/medium/low),
and specific remediation steps for each issue.
```

---

## Skill Quality Rubric

```
Evaluate this Claude skill for quality and effectiveness.

### Description Quality (0-1)
- Does the description clearly explain WHEN to trigger?
- Does it cover all relevant use cases?
- Is it "pushy" enough to prevent undertriggering?

### Instruction Clarity (0-1)
- Are instructions in imperative form?
- Do they explain WHY, not just WHAT?
- Are examples included?

### Architecture (0-1)
- Is SKILL.md under 500 lines?
- Are references properly organized?
- Is progressive disclosure used effectively?

### Completeness (0-1)
- Does it handle edge cases?
- Are error scenarios addressed?
- Is the output format specified?

Return JSON with verdict, scores, and specific improvement suggestions.
```
