# Component Similarity Detection System

## Overview

This system enables Workflow Guardian to intelligently detect similar React/TypeScript components and recommend reuse strategies (EXTEND, COPY-THEN-MODIFY, or CREATE NEW).

**Goal:** Maximize code reuse while maintaining clarity and reducing the risk of breaking changes.

## System Components

### 1. Similarity Detector Script
**File:** `scripts/similarity_detector.py` (674 lines)

A Python script that analyzes React/TypeScript components and compares them against a proposed new component.

**Key Features:**
- Analyzes all components in `src/` directory
- Extracts 7 similarity dimensions
- Calculates weighted similarity score (0-100%)
- Estimates reuse potential
- Generates actionable recommendations

**Usage:**
```bash
python3 scripts/similarity_detector.py <project_root> "<component_description>"
```

**Output:**
- Human-readable similarity report
- JSON output for programmatic integration
- Top 10 most similar components with details

### 2. Reference Documentation
**File:** `references/component-reuse-detection.md` (1466 lines)

Comprehensive guide covering:
- When to run similarity detection
- How similarity is calculated
- Decision matrix for choosing reuse strategy
- Safe extension patterns with examples
- Copy-then-modify workflow
- Implementation examples
- Common pitfalls to avoid

### 3. Usage Guide
**File:** `scripts/USAGE.md`

Quick-start guide with examples, troubleshooting, and best practices.

## How It Works

### Step 1: Proposed Component Analysis
When you want to create a component, you provide a description:
```
"A form component for loan applications with file uploads, validation, and async submission"
```

### Step 2: Codebase Analysis
The system scans all existing components and extracts:
- React hooks used
- State variables and types
- JSX structure patterns
- Form fields
- Event handlers
- Feature capabilities

### Step 3: Similarity Calculation
For each existing component, calculates similarity based on:
- **30%** Hook usage patterns
- **20%** State variables and types
- **20%** JSX structure patterns
- **15%** Import patterns and libraries
- **10%** Form field similarity
- **5%** Event handler patterns

### Step 4: Recommendation Generation
Based on similarity score:
- **80%+:** EXTEND - Add props/variants to existing component
- **60-79%:** COPY-THEN-MODIFY - Copy file and customize
- **40-59%:** EXTRACT UTILITIES - Share common logic
- **<40%:** CREATE NEW - Safe to build from scratch

## Decision Matrix

Use this matrix to decide what to do:

```
similarity >= 80% AND reuse_potential >= 70%
└─> EXTEND: Add props/variants to existing component
    Risk: LOW | Benefit: HIGH | Effort: MEDIUM

similarity 60-79% AND reuse_potential >= 50%
└─> COPY-THEN-MODIFY: Independent copy with customization
    Risk: LOW | Benefit: MEDIUM | Effort: MEDIUM

similarity 40-59% AND reuse_potential >= 30%
└─> EXTRACT UTILITIES: Share validation/helper functions
    Risk: LOW | Benefit: MEDIUM | Effort: HIGH

similarity < 40%
└─> CREATE NEW: Build from scratch
    Risk: ZERO | Benefit: N/A | Effort: HIGH
```

## Usage Workflow

### For Components 50+ lines of code:

1. **Run similarity detector**
   ```bash
   python3 scripts/similarity_detector.py /project "description of component"
   ```

2. **Review top 5 results**
   - Check similarity percentage
   - Look at shared features
   - Read recommendation

3. **Make decision**
   - If 80%+ → EXTEND with variant prop
   - If 60-79% → COPY-THEN-MODIFY with attribution
   - If 40-59% → EXTRACT UTILITIES
   - If <40% → CREATE NEW safely

4. **Implement**
   - Follow pattern for chosen strategy
   - Add documentation
   - Test thoroughly

## Key Principles

### 1. Reuse Over Creation
Always check for similar components first. Duplication is the enemy of maintainability.

### 2. Safe Extension
Only extend components when very similar (80%+). Use props/variants for control. Never break existing functionality.

### 3. Pragmatic Copying
Copy-then-modify is safer than refactoring existing code. Document the copy with comments explaining divergence.

### 4. Clear Separation
Keep at most 2-3 variants per component. Beyond that, separate files are clearer.

### 5. Managed Duplication
Never duplicate code in 3+ places. Extract shared logic to utilities and hooks.

## Examples

### Example 1: Form Components (80% Similar)

**Existing:** SubmitPage.tsx (form with file upload, validation, async)
**Proposed:** LoanApplicationForm (form with file upload, validation, async)

**Analysis:**
- Similarity: 82%
- Shared Features: Form handling, file upload, validation, async submission
- Reuse Potential: 70%

**Decision:** EXTEND
**Action:** Add `variant="loan"` prop to SubmitPage
**Result:** Reuse 70% of code, single source of truth for form logic

### Example 2: Modal Dialogs (65% Similar)

**Existing:** ResolveModal.tsx (form modal with async submission)
**Proposed:** ConfirmActionModal (form modal with async submission)

**Analysis:**
- Similarity: 65%
- Shared Features: Modal structure, form handling, async submission
- Reuse Potential: 55%

**Decision:** COPY-THEN-MODIFY
**Action:** Copy ResolveModal, customize for new use case
**Result:** Independent components, zero risk of cross-contamination

### Example 3: Shared Utilities (50% Similar)

**Existing:** SubmitPage.tsx, LoanIssueFormPage.tsx, NewForm.tsx
**Shared:** File upload logic (validation, preview, cleanup)

**Analysis:**
- Similarity: 50% (file handling only)
- Shared Features: File validation, preview generation
- Reuse Potential: 40%

**Decision:** EXTRACT UTILITIES
**Action:** Create `useFileUpload()` hook
**Result:** 3 components share file logic, bug fixes in one place

## File Structure

```
workflow-guardian/
├── scripts/
│   ├── similarity_detector.py     # Main analysis script
│   └── USAGE.md                    # Quick-start guide
├── references/
│   └── component-reuse-detection.md # Comprehensive guide
└── README_SIMILARITY_DETECTION.md   # This file
```

## Integration Points

This system integrates with Claude's component creation workflow:

1. **Pre-creation check:** Before generating any component 50+ lines
2. **Decision making:** Choose between extend/copy/extract/create
3. **Implementation:** Follow recommended pattern
4. **Documentation:** Mark copied code with attribution

## Quick Reference

### When to EXTEND
- Similarity >= 80%
- Same hooks and state patterns
- Same form fields
- Different validation rules only
- Changes are additive, not subtractive

### When to COPY-THEN-MODIFY
- Similarity 60-79%
- Same general structure
- Different business logic
- Likely to diverge in future
- Want clear separation of concerns

### When to EXTRACT UTILITIES
- Similarity 40-59%
- Shared validation/helper logic
- Different UI/structure
- Code used 2+ places
- Can isolate common patterns

### When to CREATE NEW
- Similarity < 40%
- Unique purpose
- Different patterns
- No shared logic to extract
- Confident it's different

## Advanced Features

### Multi-Dimensional Scoring

The similarity score combines:
- Hook compatibility (React APIs used)
- State pattern matching (variable names and types)
- JSX structure similarity (DOM patterns)
- Library alignment (external dependencies)
- Form complexity (field types and count)
- Feature parity (async, validation, etc.)

### Type Inference

The system infers TypeScript types from initial values:
- `useState('')` → `string`
- `useState([])` → `array`
- `useState(false)` → `boolean`
- `useState({})` → `object`

### Custom Hook Detection

Automatically detects custom React hooks:
- `useSimpleAuth`
- `useFocusTrap`
- `useFileUpload`
- etc.

### Pattern Recognition

Recognizes common patterns:
- Form submission patterns
- File upload patterns
- API integration patterns
- Modal/dialog patterns
- Animation patterns

## Limitations & Gotchas

1. **Dynamic Imports** - Can't analyze components imported conditionally
2. **Inline JSX** - Doesn't catch JSX in strings or templates
3. **Styled Components** - Doesn't analyze CSS-in-JS in detail
4. **Complex Types** - Infers types, doesn't fully parse TypeScript
5. **Runtime Logic** - Analyzes static structure only

These are acceptable limitations for the tool's purpose.

## Contributing

To improve the detector:

1. **Add new pattern recognition** in `ComponentAnalyzer` class
2. **Adjust similarity weights** in `SimilarityDetector` class
3. **Improve recommendations** in `_generate_recommendation()` method
4. **Expand examples** in reference documentation

## FAQ

**Q: Why not just refactor all similar components?**
A: Refactoring is risky and breaks existing code. Copy-then-modify is safer.

**Q: What if I disagree with the recommendation?**
A: The recommendation is guidance, not law. Use your judgment based on business context.

**Q: Should I extract utilities for code used only once?**
A: No. Extraction adds complexity without benefit. Wait until it's used 2+ times.

**Q: What's the best way to handle component evolution?**
A: Extract utilities incrementally as patterns emerge. Don't over-engineer upfront.

**Q: How do I maintain copied components?**
A: Document divergence in comments. Extract shared utilities as patterns emerge.

## See Also

- `references/component-reuse-detection.md` - Full detailed guide
- `scripts/USAGE.md` - Quick-start examples
- Individual component files for real examples

---

**Last Updated:** February 2026
**System Status:** Production Ready
**Test Coverage:** Real codebase analysis verified
