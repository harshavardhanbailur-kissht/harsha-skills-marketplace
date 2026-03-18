# Research 12: Contradiction Analysis & Resolution

## Methodology
Cross-referenced all 11 research files + 4 reference documents for conflicting claims.
Applied research-analyst-skill Phase 6 protocol: identify, classify, resolve.

## Contradictions Found

### C1: Agent Count — "3-4 max" vs "16 agents built a compiler"
- **Source A**: Claude Code best practices → "Max out at 3-4 specialized agents"
- **Source B**: Anthropic 16-agent C compiler stress test → 2000 sessions, 100K lines
- **Resolution**: Context-dependent. 3-4 is optimal for typical development tasks with
  human oversight. 16+ is viable for massive, well-scoped projects with test harnesses.
  Our skill should recommend 3-7 for most features, allow up to 10 for large projects,
  and document when more is appropriate.

### C2: Adaptive Thinking vs Manual budget_tokens
- **Source A**: Research 01 → "Adaptive thinking replaces manual budget_tokens"
- **Source B**: Our SKILL.md → Recommends manual budget_tokens for Sonnet workers
- **Resolution**: Both are valid. Adaptive thinking (effort parameter) is the new
  recommended approach for Opus. For Sonnet workers on well-scoped tasks, either works.
  Adaptive is simpler; manual gives finer cost control. Update SKILL.md to recommend
  adaptive as default, manual as optimization option.

### C3: Error Propagation Rates Conflict
- **Source A**: Research 03 → Level 3: ~61% success, Level 4+: ~52%
- **Source B**: ADaPT paper → +28.3% improvement with adaptive decomposition
- **Resolution**: No real contradiction. 61% is baseline without adaptive decomposition.
  ADaPT's improvement applies on top. With adaptive decomposition: Level 3 ≈ 78%,
  Level 4 ≈ 67%. Our skill already recommends max 3 layers + adaptive refinement.

### C4: Prompt Caching TTL — "5 minutes" vs "1 hour extended"
- **Source A**: Anthropic docs → Default 5-minute cache TTL
- **Source B**: Research 05 → Extended TTL "1h" for long pipelines
- **Resolution**: Both are correct. Default is 5 min. Extended TTL (1h) available via
  `"ttl": "1h"` parameter. Our skill correctly recommends extended TTL for pipelines.
  Verify this feature is still available in current API version.

### C5: LLM-as-Judge — Binary vs Numeric Scoring
- **Source A**: Research 04 → "Binary PASS/FAIL more stable than numeric"
- **Source B**: KDD 2025 survey → Multi-dimensional scoring with rubrics
- **Resolution**: Both are valid for different purposes. Binary for go/no-go decisions
  (should we ship this?). Numeric for tracking improvement over time and comparing
  skill versions. Our verification pipeline should use binary for the fix loop but
  track numeric scores for observability/improvement.

### C6: Sanitization Effectiveness — "Outperforms all methods" vs "Can be bypassed"
- **Source A**: Minimizer-Sanitizer → "Outperforms all existing methods on all benchmarks"
- **Source B**: Same paper → "Can be bypassed via obfuscation or Braille encoding"
- **Resolution**: No contradiction — defense-in-depth. No single defense is perfect.
  The sanitizer is the best single layer but must be combined with other defenses.
  Our skill uses 4-layer defense which addresses this.

### C7: Token Overhead — "20K per Task" vs Cost Optimization Claims
- **Source A**: Claude Code docs → "Each Task starts with 20K token overhead"
- **Source B**: Our cost optimization stack → Claims significant savings
- **Resolution**: Both true. The 20K overhead is fixed per agent spawn. Cost savings
  come from model selection and caching WITHIN each agent's work, not from reducing
  spawn overhead. For 7 tasks: 140K tokens just in overhead. Our cost optimization
  stack should explicitly account for this fixed cost.

## Reconciled Recommendations
1. Default to adaptive thinking (effort parameter) for all agents, document manual
   budget_tokens as optimization option for high-volume production use
2. Recommend 3-7 parallel tasks for typical features, up to 10 for large projects
3. Use binary PASS/FAIL for verification loop, track numeric scores for observability
4. Account for ~20K token overhead per agent in cost estimates
5. Layer multiple defense strategies — no single sanitization is sufficient
6. Pin model versions for reproducibility, document alias convenience option
