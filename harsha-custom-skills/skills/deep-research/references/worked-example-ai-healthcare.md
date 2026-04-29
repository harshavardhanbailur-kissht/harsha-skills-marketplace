# Worked Example: "AI in Healthcare 2025"

A topic flowing through every phase of the pipeline. Use this when you want to see what each phase's output actually looks like in practice.

**Topic**: How is AI transforming healthcare in 2025?

---

## Phase 1 Output: Query Plan

```
1. "AI healthcare 2025 applications"
2. "machine learning clinical diagnosis"
3. "AI drug discovery pipeline"
4. "healthcare AI regulatory challenges"
5. "AI hospital workflow efficiency"
6. "AI healthcare bias discrimination"
7. "medical imaging AI diagnostics"
8. "AI patient outcomes evidence"
```

---

## Phase 2 Output: Theme Map

```
Themes Identified:
1. Diagnostic AI (6 sources)
   - Medical imaging analysis
   - Lab result interpretation
2. Drug Discovery Acceleration (5 sources)
   - Molecule screening
   - Clinical trial design
3. Administrative Efficiency (7 sources)
   - Scheduling
   - Billing automation
   - Note generation
4. Regulatory & Safety (4 sources)
   - FDA approval process
   - AI safety standards
5. Bias & Equity (6 sources)
   - Racial bias in models
   - Access disparities
6. Controversy: Claims of superhuman performance vs. actual limitations
```

---

## Phase 3 Sample Entries

```
Entry 1: Medical Imaging AI Performance
Title: "Deep Learning in Radiology: Current Performance & Limitations"
Source: Nature Medicine, 2025
Key Claim: "AI matches radiologist performance on chest X-rays but fails on rare pathologies"
Authority: Tier 1 (peer-reviewed journal)
Confidence: HIGH (verified in 3+ studies)
Related to: Entry 5 (AI bias in radiology)

Entry 2: Pharma AI Cost Savings
Title: "AI Accelerates Drug Discovery: Cost Analysis 2025"
Source: McKinsey Healthcare Report
Key Claim: "AI can reduce early-stage discovery costs by 30-50%"
Authority: Tier 2 (reputable consulting)
Confidence: MEDIUM (estimates vary 20-60%)
Related to: Entry 8 (approval timeline)

Entry 3: AI Bias in Healthcare
Title: "Racial Disparities in Clinical Decision AI"
Source: JAMA Medicine, 2024
Key Claim: "Models trained on majority-white datasets show 20% higher error rates on Black patients"
Authority: Tier 1 (peer-reviewed)
Confidence: HIGH (replicated in multiple systems)
Related to: Entry 1 (limitations)
Conflict: Contradicts vendor claims of universal accuracy
```

---

## Phase 3.5 Graph Output

```json
{
  "nodes": [
    {"id": "entry-imaging", "title": "Medical Imaging AI", "category": "diagnostics", "connections": 5},
    {"id": "entry-bias", "title": "AI Bias in Diagnostics", "category": "equity", "connections": 4},
    {"id": "entry-drug", "title": "AI Drug Discovery", "category": "research", "connections": 3},
    {"id": "entry-admin", "title": "Administrative Efficiency", "category": "operations", "connections": 2},
    {"id": "entry-regulatory", "title": "FDA Approval Process", "category": "governance", "connections": 3}
  ],
  "edges": [
    {"source": "entry-imaging", "target": "entry-bias", "type": "dependency", "strength": 0.9},
    {"source": "entry-imaging", "target": "entry-regulatory", "type": "causal", "strength": 0.7},
    {"source": "entry-drug", "target": "entry-regulatory", "type": "hierarchical", "strength": 0.8}
  ]
}
```

---

## Phase 4 Evidence Chains

```
Claim: "AI matches radiologist performance on chest X-rays"
├─ Primary: Stanford study (2024) "AI in Radiology Benchmarking"
│  └─ Methodology: 1000 chest X-rays, blinded comparison
│  └─ Finding: AI 94% accuracy, radiologists 92%
├─ Secondary: Nature Medicine editorial citing Stanford
└─ Derivative: News article on AI "beating" doctors (oversimplified)

Confidence: HIGH (primary source strong, methodology sound)
But Note: Study used selected X-rays, not all presentations
```

---

## Phase 4.5 QA Scores

```
Entry: Medical Imaging AI
- Accuracy: 9/10 ✓
- Completeness: 7/10 (misses ophthalmology imaging)
- Depth: 8/10 ✓
- Recency: 9/10 ✓
- Consistency: 8/10 ✓
TOTAL: 41/50 ✓ PASS

Entry: "AI Replaces Doctors Soon" (hypothetical)
- Accuracy: 3/10 ✗ (contradicts evidence)
- Completeness: 4/10
- Depth: 2/10
- Recency: 5/10
- Consistency: 1/10 ✗ (conflicts heavily with entries)
TOTAL: 15/50 ✗ FAIL — DO NOT INCLUDE
```

---

## Phase 5 Ingestion Report

```
HEALTHCARE AI KNOWLEDGE BASE
Total Entries: 34
Pass Rate: 88%
Source Tiers: Tier 1 (62%), Tier 2 (28%), Tier 3 (10%)

Categories:
- Diagnostics (12 entries)
- Research (8 entries)
- Operations (7 entries)
- Governance (5 entries)
- Equity (6 entries)

Confidence: HIGH (22), MEDIUM (8), LOW (4)
```

---

## Phase 6 Visualization

- D3 graph showing 34 nodes
- Clusters: Diagnostics (hub, 8 connections), Equity (6 connections), Research (isolated, 3 connections)
- Search: Full-text on titles + summaries
- Export: SVG graph, bibliography (CSV)
