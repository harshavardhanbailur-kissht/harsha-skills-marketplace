# Content Analysis Patterns Reference

## Phase 1: Content Ingestion Strategy

### Step 1: File Discovery
```
1. List all files in the source directory recursively
2. Categorize by type: .md, .json, .html, .txt, .pdf
3. Sort by modification date (newest = most current)
4. Estimate total content volume (file sizes)
```

### Step 2: Content Categorization Matrix

For each file, determine:

| Attribute | Description | Values |
|-----------|-------------|--------|
| Content Type | What kind of content is this? | glossary, process-flow, architecture, research-finding, transcript, reference |
| Domain | What subject area? | domain-specific, technical, methodology, meta |
| Depth | How detailed? | overview, detailed, deep-dive |
| Teachability | How directly can this become a lesson? | HIGH (direct), MEDIUM (needs synthesis), LOW (background reference) |
| Prerequisites | What must be understood first? | List of concepts |
| Key Concepts | What does this teach? | List of concepts introduced |

### Step 3: Concept Extraction

From each file, extract:
1. **Defined terms** — words/phrases that are explicitly defined
2. **Used terms** — domain-specific terms used without definition (implies prerequisite)
3. **Processes** — step-by-step workflows described
4. **Relationships** — "X depends on Y", "A comes before B", "C is a type of D"
5. **Examples** — real-world instances or scenarios mentioned
6. **Numbers/thresholds** — specific values that matter (e.g., "CIBIL 777 threshold")

### Step 4: Dependency Graph Construction

Build a directed graph where:
- Nodes = concepts
- Edges = "concept A requires understanding concept B"
- Edge weight = strength of dependency (required vs helpful)

Example for LAP:
```
"What is LAP" → "LAP Programs" → "Normal vs Saral"
"What is CIBIL" → "BRE Rules" → "Program Eligibility"
"What is LeadGen" → "SM Role" → "LeadGen Flow"
"What is LOS" → "CPA Role" → "Credit Processing"
```

### Step 5: Gap Analysis

After mapping all concepts:
1. **Undefined prerequisites**: Concepts used but never defined in source material
2. **Orphaned concepts**: Defined but never referenced by other content
3. **Thin topics**: Mentioned frequently but with little detail
4. **Missing connections**: Logical links that should exist but don't

For each gap, determine:
- Can it be filled from other source files?
- Does it need web research?
- Is it critical for the learning path or just nice-to-have?

## Content Quality Assessment

### Richness Score (per topic)
- **Rich** (3+ paragraphs, examples, details): Can become a standalone lesson
- **Moderate** (1-2 paragraphs): Needs supplementation but has core content
- **Thin** (mentioned only): Needs significant research or can be merged with another topic
- **Absent** (implied but not covered): Requires full web research

### Source Authority Tiers
- **Tier 1**: Official documentation, verified transcriptions, production data
- **Tier 2**: Research findings with cited sources, expert analysis
- **Tier 3**: Synthesized/generated content, inferred relationships
- **Tier 4**: Web research supplementation (must cite sources)

## Output: Content Catalog Format

```json
{
  "catalog": [
    {
      "file": "path/to/file.md",
      "contentType": "process-flow",
      "domain": "lap-leadgen",
      "depth": "detailed",
      "teachability": "HIGH",
      "keyConceptsIntroduced": ["SM LeadGen", "OTP verification", "consent capture"],
      "keyConceptsRequired": ["What is LAP", "What is LeadGen", "SM role"],
      "richness": "rich",
      "authority": "tier-1",
      "suggestedModule": "module-2-leadgen",
      "suggestedLessons": ["lesson-2-1-starting-lead", "lesson-2-2-applicant-details"]
    }
  ],
  "gaps": [
    {
      "concept": "BRE scoring algorithm",
      "severity": "medium",
      "recommendation": "web-research",
      "context": "Referenced in Module 3 but not explained in source files"
    }
  ],
  "dependencyGraph": {
    "nodes": ["concept-1", "concept-2"],
    "edges": [{"from": "concept-1", "to": "concept-2", "type": "requires"}]
  }
}
```
