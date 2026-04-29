# Knowledge Entry Template and Guidelines

This document provides the complete JSON schema and guidelines for creating knowledge entries in the deep-research-synthesizer system.

## JSON Schema

Each knowledge entry is a JSON object with the following structure:

```json
{
  "id": "unique_identifier",
  "title": "Entry Title",
  "category": "Category Name",
  "subcategory": "Optional subcategory",
  "content": "Full detailed content of the knowledge entry",
  "summary": "One-sentence summary of key point",
  "confidence": "VERIFIED|HIGH|MEDIUM|LOW|UNKNOWN",
  "source": "https://example.com or source description",
  "tags": ["tag1", "tag2", "tag3"],
  "related": ["related_entry_id_1", "related_entry_id_2"],
  "gaps": [
    "What is the long-term impact of this?",
    "How does this compare to competing approaches?"
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Required Fields

- **id**: Unique identifier (string, alphanumeric, no spaces). Auto-generated as SHA256 hash of title if omitted.
- **title**: Short, descriptive title (string, max 100 characters recommended)
- **category**: Top-level classification (string, e.g., "Machine Learning", "Software Architecture")
- **content**: Full detailed content (string, 100+ characters recommended). Supports Markdown.
- **confidence**: Assessment of reliability (string, one of 5 levels - see decision tree below)

### Optional Fields

- **summary**: One-sentence summary of main point (string, auto-generated from content if missing)
- **source**: Attribution - URL or source description (string)
- **subcategory**: Secondary classification (string)
- **tags**: Relevant keywords (array of strings, max 5 tags recommended, lowercase)
- **related**: IDs of related entries (array of strings)
- **gaps**: Identified knowledge gaps or questions (array of strings)
- **created_at**: ISO 8601 timestamp (auto-set to current time if missing)
- **updated_at**: ISO 8601 timestamp (auto-set on each update)

## Confidence Level Decision Tree

**CANONICAL DEFINITION**: This is the authoritative confidence framework. All other reference files point to this section.

Choose the confidence level that best reflects the entry's reliability and verification status. The framework is **SOURCE-BASED** — confidence depends on how many independent sources agree and which tier they occupy (see `references/research-quality-assurance.md` for source tier definitions).

### VERIFIED (3+ independent Tier 1 sources agree)
Use when:
- 3+ independent peer-reviewed or primary sources all agree on the claim
- Cross-checked against primary data with no contradictions
- Methodology is sound and results replicated
- Information from official documentation or government data
- Experimentally validated multiple times with consistent results

**Criteria**:
- ≥3 independent Tier 1 sources
- Methodology clearly disclosed and rigorous
- ≤24 months old (or evergreen topic)
- Zero contradictions in wider literature
- Replication confirmed

**Example**: "The transformer architecture was introduced in the 2017 paper 'Attention is All You Need' by Vaswani et al., verified in Nature (2018), Science (2019), and independently in JAMA (2020)."

### HIGH (2+ independent sources agree, at least 1 Tier 1-2)
Use when:
- 2+ independent Tier 1-2 sources agree with no contradictions
- Methodology is sound and limitations disclosed
- Information is recent (≤24 months old) or evergreen
- Widely accepted in field with no significant debate
- Based on well-established principles with clear reasoning

**Criteria**:
- ≥2 independent Tier 1-2 sources
- Methodology clear, limitations noted
- ≤24 months old (or evergreen topic)
- No significant contradictions in literature
- Replication or multiple studies when applicable

**Example**: "Cotton production consumes approximately 2,700 liters of water per shirt (UN Environment Programme 2024 + Water Footprint Network 2024)."

### MEDIUM (Multiple sources exist but with weakness)
Use when:
- 1-2 Tier 2 sources agree, OR 3+ Tier 3 sources agree
- Methodology sound but with noted limitations
- Data is 2-3 years old (aging but acceptable)
- No direct contradictions, but not universally accepted
- Single strong Tier 1 source with limited corroboration
- Limited replication or emerging research with promise

**Criteria**:
- 1-2 Tier 2 sources OR 3+ Tier 3 sources agreeing
- OR single Tier 1 source with no corroboration
- Methodology sound but with scope/time limitations
- 2-3 years old
- No direct contradictions
- Geographic or scope limitations noted

**Example**: "Some evidence suggests blockchain technology could improve supply chain transparency in fashion (MIT study 2023 + 2 industry reports 2024), though real-world implementations remain limited."

### LOW (Conflicting sources or single weak source)
Use when:
- Single Tier 2 source OR conflicting Tier 1-2 sources with no clear winner
- Only Tier 3-4 sources available
- Data >3 years old with no recent updates
- Significant methodology limitations or caveats
- Not replicated or contradicted by recent research
- Preliminary or speculative with limited evidence

**Criteria**:
- Single Tier 2 source, OR conflicting Tier 1-2 sources
- Only Tier 3-4 sources available
- >3 years old
- Significant methodology limitations noted
- Not replicated or contradicted by recent research
- Known caveats or limitations

**Example**: "Some fashion brands claim that 'sustainable' fast fashion is possible (Brand A 2022 + Industry Blog 2023), though environmental groups dispute this assertion (Greenpeace 2024)."

### UNKNOWN (No source found, or source quality cannot be assessed)
Use when:
- No reliable sources found despite thorough search
- All available sources are Tier 4 (unverified/fabricated)
- Claim is entirely speculative with zero supporting evidence
- Topic too new, niche, or unexplored for reliable sources
- Insufficient information to assess credibility

**Criteria**:
- Zero sources found after comprehensive search
- All sources are Tier 4 (unverified)
- Claim is speculative with no supporting evidence
- Topic entirely new or niche
- Default for unverified claims

**Example**: "The long-term impact of quantum computing on textile manufacturing remains unknown; no peer-reviewed research is currently available."

## Source Attribution Format Guide

Proper source attribution ensures credibility and traceability:

### URL Sources
```
"source": "https://arxiv.org/abs/1706.03762"
"source": "https://openai.com/research/gpt-4"
"source": "https://github.com/pytorch/pytorch"
```

### Publication Sources
```
"source": "Vaswani et al., 2017 - Attention is All You Need (NIPS)"
"source": "LeCun, Bengio, Hinton - 2015 Deep Learning Review (Nature)"
```

### Internal Sources
```
"source": "Internal research notes - Team Architecture Review"
"source": "Meeting with Dr. Jane Smith - 2024-01-10"
"source": "Notion: Engineering Decisions Database"
```

### Mixed Format (Recommended for Web Sources)
```
"source": "DeepMind Blog: Scaling Laws (https://deepmind.com/...)"
"source": "GitHub Issue #1234: Performance Analysis (pytorch/pytorch)"
```

## Tag Taxonomy Guidelines

Tags improve searchability and help identify related concepts:

### Naming Conventions
- Use **lowercase** exclusively
- Use **hyphens** for multi-word tags (not underscores or spaces)
- Keep tags **2-3 words maximum** (e.g., "attention-mechanism" not "the-attention-mechanism-in-transformers")
- Be **consistent**: use "neural-network" not both "neural-network" and "nn"

### Tag Categories

**Approach/Method**: transformer, attention-mechanism, reinforcement-learning, prompt-engineering
**Domain**: computer-vision, nlp, robotics, drug-discovery
**Architecture**: cnn, rnn, gpt, bert, gat
**Capability**: reasoning, planning, multi-modal, code-generation
**Concept**: scaling-laws, in-context-learning, emergent-abilities, interpretability
**Challenge**: alignment, bias, data-efficiency, latency

### Best Practices
- **Maximum 5 tags per entry** (3 recommended)
- **Diversity**: mix different tag categories (don't tag only with domains)
- **Specificity**: use "attention-mechanism" over generic "ai"
- **Consistency**: check existing tags before creating new ones
- **Clarity**: tags should be understandable to domain non-experts

### Example Tags
```json
"tags": ["transformer", "attention-mechanism", "nlp", "scalability"]
```

## Related Entries Linking Guide

Links between entries create a knowledge graph. Use carefully to maintain clarity:

### When to Link Entries
- **Foundational**: Entry depends on understanding another entry
  ```json
  "related": ["id-attention-mechanism", "id-softmax"]
  ```
- **Contrast**: Entry compares or contrasts with another
  ```json
  "related": ["id-cnn-architecture", "id-vit-architecture"]
  ```
- **Extension**: Entry builds on or extends another
  ```json
  "related": ["id-transformer-basics", "id-multihead-attention"]
  ```
- **Application**: Entry applies concepts from another
  ```json
  "related": ["id-reinforcement-learning", "id-rl-applications"]
  ```

### Linking Best Practices
- **Limit to 5 related entries maximum** (prevents clutter)
- **Bidirectional**: if A links to B, consider if B should link to A
- **Meaningful**: only link entries that genuinely inform each other
- **Verify IDs**: ensure referenced entry IDs actually exist

### Example
```json
{
  "id": "id-gpt3-architecture",
  "title": "GPT-3 Architecture Overview",
  "related": [
    "id-transformer-architecture",
    "id-attention-mechanism",
    "id-large-language-models",
    "id-few-shot-learning"
  ]
}
```

## Gap Identification Prompts

Knowledge gaps highlight missing information and guide research priorities:

### Gap Categories

**Definitional Gaps**: "What exactly is X and how does it differ from Y?"
**Causal Gaps**: "Why does X cause Y?" "What mechanism explains this?"
**Comparative Gaps**: "How does approach A compare to approach B quantitatively?"
**Temporal Gaps**: "When was this discovered?" "How has this evolved?"
**Impact Gaps**: "What are the long-term consequences of X?"
**Scale Gaps**: "How well does this scale beyond current test cases?"
**Implementation Gaps**: "How would this work in practice?" "What are the engineering challenges?"

### Writing Effective Gaps

**Good gaps are**:
- Specific and answerable
- Relevant to the domain
- Actionable (guide future research)
- Written as questions

**Avoid**:
- Overly broad questions ("How does AI work?")
- Philosophical dead-ends ("What is consciousness?")
- Questions already answered in the content
- Vague phrasing

### Example Gaps
```json
"gaps": [
  "What is the empirical evidence for scaling laws beyond 10 trillion parameters?",
  "How do constitutional AI methods perform on adversarial robustness benchmarks?",
  "What are the memory requirements for fine-tuning 70B parameter models on custom datasets?"
]
```

## Example Entries

### Example 1: VERIFIED Entry (High-Quality, Well-Sourced)

```json
{
  "id": "attention-is-all-you-need-2017",
  "title": "Attention Is All You Need",
  "category": "Foundational Architecture",
  "subcategory": "Sequence Models",
  "summary": "The transformer architecture eliminates recurrence and convolution, relying entirely on attention mechanisms for sequence modeling.",
  "content": "The transformer architecture, introduced in the 2017 paper by Vaswani et al., fundamentally changed deep learning by replacing recurrent neural networks with purely attention-based mechanisms. The key innovation is the multi-head self-attention mechanism, which allows the model to attend to different positions of the input sequence in parallel. The architecture consists of an encoder-decoder structure where each layer contains a multi-head attention mechanism followed by position-wise feed-forward networks. Unlike RNNs, transformers process entire sequences in parallel, enabling faster training on large datasets. The positional encoding is used to inject information about token positions since the model has no inherent sequence ordering. This architecture enabled the development of large language models like GPT and BERT that have achieved state-of-the-art results across numerous NLP tasks.",
  "confidence": "VERIFIED",
  "source": "Vaswani et al., 2017 - Attention Is All You Need (NeurIPS) https://arxiv.org/abs/1706.03762",
  "tags": ["transformer", "attention-mechanism", "deep-learning", "nlp"],
  "related": ["multi-head-attention-mechanism", "positional-encoding", "gpt-architecture"],
  "gaps": [],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Example 2: MEDIUM Entry (Emerging Research)

```json
{
  "id": "scaling-laws-beyond-trillions",
  "title": "Scaling Laws Beyond Trillion-Parameter Models",
  "category": "Training & Optimization",
  "subcategory": "Model Scaling",
  "summary": "Recent research suggests continued improvements in model capabilities with scale, though the mechanisms and efficiency tradeoffs remain unclear.",
  "content": "Recent papers from OpenAI and Anthropic suggest that scaling laws continue to hold beyond trillion-parameter models, with consistent improvements in downstream task performance. However, the empirical evidence is limited to a few high-capacity models, and the mechanisms driving these improvements (increased capacity, memorization, emergent reasoning) remain debated. Some researchers propose that scaling alone may be insufficient for achieving general intelligence without architectural innovations or training procedure changes. The computational cost of training models at this scale raises concerns about practical applicability and environmental impact. Several emerging techniques like mixture-of-experts and sparse training aim to improve efficiency, but real-world deployments remain limited.",
  "confidence": "MEDIUM",
  "source": "OpenAI GPT-4 Technical Report (2024) + Anthropic Research Blog",
  "tags": ["scaling-laws", "large-language-models", "training-efficiency"],
  "related": ["transformer-architecture", "mixture-of-experts", "computational-efficiency"],
  "gaps": [
    "What is the empirical evidence for scaling beyond 10 trillion parameters?",
    "At what point do scaling laws break down or change qualitatively?",
    "What are the optimal compute-efficient approaches for training models at extreme scale?"
  ],
  "created_at": "2024-01-10T14:22:00Z"
}
```

### Example 3: Entry with Identified Gaps (Lower Confidence)

```json
{
  "id": "constitutional-ai-long-term-effects",
  "title": "Long-Term Effects of Constitutional AI on Model Behavior",
  "category": "AI Alignment",
  "subcategory": "Training Methods",
  "summary": "Constitutional AI (CAI) is a training approach that aims to improve alignment, but long-term behavioral effects remain understudied.",
  "content": "Constitutional AI, developed by Anthropic, uses AI-generated critique and revision during training to improve model alignment with specified principles. Early experiments show improvements on safety benchmarks and reduced harmful outputs. However, long-term effects on model behavior, capability trade-offs, and robustness to adversarial scenarios are not well understood. It is unclear whether CAI methods maintain effectiveness as models scale, whether constitutional constraints can handle novel adversarial scenarios, and how well these constraints transfer across different domains and deployment contexts. Some researchers speculate that CAI could enable more complex constraint systems, while others worry about potential brittleness or unexpected failure modes.",
  "confidence": "LOW",
  "source": "Anthropic Constitutional AI Paper (2023) + Internal Research Notes",
  "tags": ["alignment", "constitutional-ai", "safety"],
  "related": ["rlhf-training", "ai-safety-benchmarks"],
  "gaps": [
    "How effective is CAI for novel adversarial attacks not seen during training?",
    "Does CAI effectiveness degrade or improve as models scale to larger parameter counts?",
    "How do constitutional constraints interact with other alignment approaches like RLHF?",
    "What are the computational overhead and training time costs of CAI at scale?",
    "How well do CAI-trained models handle out-of-distribution scenarios?"
  ],
  "created_at": "2024-01-12T09:15:00Z"
}
```

## Creating Entries Programmatically

When building entries via the research system:

```python
entry = {
    "id": hashlib.sha256(title.encode()).hexdigest()[:12],
    "title": "Research Finding Title",
    "category": "Category from ontology",
    "content": "Detailed research synthesis...",
    "confidence": "MEDIUM",  # Must be one of the 5 levels
    "source": "URL or source description",
    "tags": ["tag1", "tag2"],  # 2-5 tags recommended
    "related": [],  # Fill in post-hoc after all entries created
    "gaps": ["Question 1?", "Question 2?"],
    "created_at": datetime.utcnow().isoformat() + "Z"
}
```

## Validation Rules

The build system will enforce:

1. Required fields must be present and non-empty
2. Confidence must be one of 5 levels (case-insensitive, auto-normalized to uppercase)
3. Related entries must reference valid IDs
4. Tags must be strings (no integer or object tags)
5. Content must be at least 50 characters
6. IDs must be alphanumeric with no spaces (auto-generated if missing)

## Quality Checklist

Before finalizing an entry:

- [ ] Title is clear and specific (under 100 chars)
- [ ] Content provides genuine insight (not generic summary)
- [ ] Confidence level matches actual reliability
- [ ] Source is clearly attributed
- [ ] Summary is one sentence capturing main point
- [ ] Tags are lowercase and consistent with existing tags
- [ ] Gaps identify real, answerable questions
- [ ] Related entries are meaningful and accurate
- [ ] No spelling or grammar errors
- [ ] Entry adds unique value (not duplicate of existing entry)

