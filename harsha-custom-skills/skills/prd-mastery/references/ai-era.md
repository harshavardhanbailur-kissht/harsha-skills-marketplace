# AI-Era PRD Practices

Complete guide for AI product requirements and AI-assisted PRD creation.

---

## AI Product Requirements

### AI-Specific PRD Sections

Every AI/ML product PRD should include these additional sections:

```markdown
## AI Implementation Constraints

### Model Requirements
- Model type: [Classification | Generation | Embedding | etc.]
- Input specifications: [format, size, modality]
- Output specifications: [format, structure, length]
- Accuracy target: [metric and threshold]
- Latency requirement: [P50/P99 targets]
- Cost per inference: [budget limit]

### Training Data Requirements
- Data sources: [list sources]
- Data volume: [minimum samples needed]
- Labeling methodology: [process]
- Data quality standards: [specifications]
- Data freshness: [how often to retrain]
- Bias considerations: [known risks]

### Evaluation Criteria
- Primary metric: [accuracy, F1, BLEU, etc.]
- Secondary metrics: [list]
- Benchmark datasets: [which ones]
- A/B testing methodology: [approach]
- Continuous monitoring: [what to track]

### Safety & Ethics
- Bias testing: [methodology]
- Explainability: [requirements]
- Hallucination handling: [strategy]
- Adversarial robustness: [testing approach]
- Human oversight: [when required]
- Fail-safe behavior: [fallback when uncertain]
```

---

## OpenAI PRD Template (Miqdad Jaffer)

### Structure

```markdown
# [Feature Name] AI Product Spec

## Executive Summary
[One paragraph overview]

## Strategic Context
- How this fits company strategy
- Market opportunity
- Competitive landscape

## Customer Outcomes
- Primary job-to-be-done
- Success from customer perspective
- Value proposition

## Non-Functional Requirements
- Latency: [targets]
- Accuracy: [targets]
- Scale: [requirements]
- Cost: [constraints]

## AI-Specific Considerations

### Model Selection
- Model options considered
- Selected model and rationale
- Fine-tuning requirements

### Edge Cases
- Low confidence handling
- Out-of-distribution inputs
- Adversarial inputs
- Rate limiting behavior

### Evaluation
- Offline evaluation plan
- Online evaluation plan
- Human evaluation requirements
- Regression testing

### Safety
- Harmful content handling
- Bias mitigation
- Privacy protection
- Compliance requirements
```

---

## Microsoft Responsible AI Standard v2

### Requirements for AI Products

**Impact Assessment (Required in Vision/Requirements Phase)**
- Stakeholder impact analysis
- Potential harms identification
- Risk mitigation strategies

**Transparency Notes (Required)**
- How AI system works
- Intended use cases
- Limitations and known issues
- Best practices for use

**Use Classifications:**
| Classification | Description | Requirements |
|----------------|-------------|--------------|
| Restricted Use | High risk of harm | Prohibited or heavy oversight |
| Sensitive Use | Moderate risk | Additional review required |
| General Use | Low risk | Standard requirements |

### Responsible AI Principles
1. Fairness
2. Reliability & Safety
3. Privacy & Security
4. Inclusiveness
5. Transparency
6. Accountability

---

## AI Agent Requirements

### Anthropic Framework for AI Agents

**Distinguish:**
- **Workflows**: Predefined paths, deterministic
- **Agents**: LLM-directed, dynamic decisions

### Agent Specification Template

```markdown
## Agent Requirements

### Agent Behavior
- Goal definition: [what agent tries to accomplish]
- Autonomy level: [how much independent action allowed]
- Decision boundaries: [what it can/cannot decide]

### Tool Specifications
- Available tools: [list with exact API structure]
- Tool selection logic: [how agent chooses tools]
- Tool error handling: [fallback behavior]

### Guardrails
- Sandboxed testing: [environment specs]
- Human checkpoints: [when human approval required]
- Interruptibility: [how to stop agent]
- Infinite loop prevention: [safeguards]
- Budget limits: [API calls, compute, cost]

### Monitoring
- Logging requirements: [what to track]
- Alerting: [when to notify humans]
- Rollback criteria: [when to disable]
```

---

## AI Safety Requirements

### Categories to Address

```markdown
## AI Safety Specifications

### Content Safety
- Harmful content filtering: [approach]
- Toxicity thresholds: [if applicable]
- Jailbreak prevention: [methods]
- Output validation: [checks before showing to user]

### Accuracy & Truthfulness
- Hallucination detection: [methods]
- Source citation: [if applicable]
- Uncertainty expression: [how model expresses uncertainty]
- Factual grounding: [requirements]

### Privacy
- PII handling: [detection and redaction]
- Data retention: [inference data retention policy]
- User data in training: [opt-out mechanisms]
- Anonymization: [requirements]

### Security
- Prompt injection prevention: [methods]
- Data extraction prevention: [safeguards]
- Model extraction prevention: [protections]
- Access controls: [who can use]

### Bias & Fairness
- Protected attributes: [list]
- Fairness metrics: [which ones]
- Testing methodology: [approach]
- Mitigation strategies: [how to address discovered bias]
```

---

## Prompt Engineering as Requirements

### Prompt Requirements Document Concept

**Emerging Practice:**
> "PRDs are becoming intellectual property of the next era in software—structured prompts serve as product requirements for AI outputs."

### System Prompt as Spec

```markdown
## System Prompt Specification

### Role Definition
- AI persona: [description]
- Expertise domain: [areas of knowledge]
- Communication style: [tone, format]

### Behavior Constraints
- Topics to avoid: [list]
- Required disclaimers: [when to include]
- Escalation triggers: [when to refer to human]

### Output Format
- Structure requirements: [format specifications]
- Length constraints: [min/max]
- Citation requirements: [when/how to cite]

### Verification Standards
- Accuracy requirements: [standards]
- Hallucination handling: [approach]
- Uncertainty expression: [how to express]
```

### Prompt Version Control

```markdown
## Prompt Management

### Versioning
- Version format: [semantic versioning]
- Change log: [required]
- Rollback capability: [requirements]

### Testing
- Regression tests: [test cases]
- A/B testing: [methodology]
- Performance benchmarks: [metrics]

### Monitoring
- Prompt drift detection: [methods]
- Performance degradation alerts: [thresholds]
- User feedback integration: [process]
```

---

## AI-Assisted PRD Creation

### Tools Landscape

| Tool | Approach | Price |
|------|----------|-------|
| ChatPRD | Document mode PRD generation | From $5/month |
| Miro AI | Visual PRD generation | Included in Miro |
| Notion AI | Section generation, summarization | Included in Notion |
| Beam.ai | Multi-agent PRD workflows | Enterprise |
| Copilot4DevOps | Azure DevOps integration | Enterprise |

### Productivity Impact
- Surveys suggest **6-9 hours/week saved** (Atlassian, Productboard)
- 72% of companies use AI in at least one business function
- 65% of product professionals integrating AI into workflows

### Best Practices for AI-Assisted PRDs

**Do:**
- Use AI for first drafts
- Let AI generate edge case lists
- Use AI to check completeness
- AI for formatting and structure
- AI for competitive research summaries

**Don't:**
- Accept AI output without editing
- Skip domain expertise review
- Ignore context AI lacks
- Trust AI for strategic decisions
- Let AI replace customer research

**Risk Warning:**
> "AI creates overly long documents that say nothing—requires human editing for context, product thinking, strategy."

---

## Agentic AI Development Requirements

### Agentic Workflow Specifications

```markdown
## Agentic System Requirements

### Workflow vs Agent Decision
- Use workflow when: deterministic paths, known steps
- Use agent when: dynamic decisions, complex reasoning

### Agent Architecture
- Orchestration pattern: [single agent | multi-agent | hierarchical]
- Memory requirements: [short-term | long-term | both]
- Tool integration: [available tools and APIs]

### Autonomy Boundaries
| Action Type | Autonomy Level | Human Checkpoint |
|-------------|----------------|------------------|
| Information gathering | Full autonomy | None |
| Data modification | Limited | Approval for bulk |
| External communication | None | Always |
| Financial transactions | None | Always |

### Observability
- Step logging: [granularity]
- Decision tracing: [how to trace reasoning]
- Performance metrics: [what to measure]
- Cost tracking: [per-request and aggregate]
```

---

## Machine Learning Feature Requirements

### ML Feature PRD Sections

```markdown
## ML Feature Requirements

### Problem Formulation
- Task type: [classification, regression, generation, etc.]
- Success definition: [what counts as success]
- Baseline: [current solution or heuristic]

### Data Requirements
| Data Type | Source | Volume | Quality Standard |
|-----------|--------|--------|------------------|
| Training | [source] | [size] | [standards] |
| Validation | [source] | [size] | [standards] |
| Test | [source] | [size] | [standards] |

### Model Performance Requirements
- Primary metric: [metric name] >= [threshold]
- Secondary metrics: [list with thresholds]
- Latency: P50 <= [target], P99 <= [target]
- Throughput: [requests/second]
- Memory: [max footprint]

### Deployment Requirements
- Serving infrastructure: [requirements]
- Model versioning: [approach]
- A/B testing: [requirements]
- Rollback: [procedures]

### Monitoring
- Performance drift: [detection method]
- Data drift: [detection method]
- Alerting: [thresholds and notifications]
- Retraining triggers: [conditions]
```

---

## Future-Proofing AI Product PRDs

### Emerging Considerations

**Multimodal AI:**
- Input modalities: [text, image, audio, video]
- Output modalities: [supported formats]
- Cross-modal requirements: [how modalities interact]

**Voice Interfaces:**
- Speech recognition requirements
- Natural language understanding
- Response latency for conversational flow
- Interruption handling

**Spatial Computing (AR/VR):**
- 3D rendering requirements
- Real-time processing
- Spatial awareness
- Gesture recognition

### Machine-Parseable PRDs

**Emerging Practice:**
PRDs structured for both human and AI consumption:
```markdown
<!-- AI-PARSEABLE METADATA
{
  "feature_type": "ai_agent",
  "risk_level": "medium",
  "compliance_requirements": ["GDPR", "SOC2"],
  "launch_date": "2025-Q2"
}
-->
```

---

## AI PRD Template

```markdown
# [Feature Name] AI Product Requirements

## Overview
[Brief description of AI-powered feature]

## Problem Statement
[Problem with evidence]

## Success Metrics
[Metrics with targets]

## User Experience
[How users interact with AI]

## AI Implementation

### Model Requirements
- Type: [model type]
- Performance: [metrics and targets]
- Latency: [requirements]
- Cost: [constraints]

### Data Requirements
- Sources: [list]
- Volume: [requirements]
- Quality: [standards]

### Safety Requirements
- Content safety: [approach]
- Bias mitigation: [approach]
- Privacy: [requirements]

### Evaluation Plan
- Offline testing: [methodology]
- Online testing: [A/B approach]
- Human evaluation: [if applicable]

## Non-AI Requirements
[Standard PRD sections]

## Risks & Mitigations
[AI-specific risks]

## Launch Plan
- Alpha: [criteria]
- Beta: [criteria]
- GA: [criteria]
```
