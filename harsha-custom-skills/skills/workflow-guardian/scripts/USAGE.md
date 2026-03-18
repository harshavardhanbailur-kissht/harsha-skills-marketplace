# Similarity Detector Usage Guide

## Quick Start

```bash
python3 similarity_detector.py <project_root> "<component_description>"
```

## Examples

### Example 1: Form Component Detection

```bash
python3 similarity_detector.py /path/to/project \
  "A form component for user feedback with email, message, and file attachments"
```

**Output will show:**
- Similarity percentage to existing forms
- Shared features (form handling, validation, file upload)
- Reuse potential
- Recommendation (EXTEND, COPY-THEN-MODIFY, or CREATE NEW)

### Example 2: Modal Component Detection

```bash
python3 similarity_detector.py /path/to/project \
  "A confirmation dialog with form fields and async submission"
```

### Example 3: Page Component Detection

```bash
python3 similarity_detector.py /path/to/project \
  "Admin dashboard with data table, filters, and bulk actions"
```

## Understanding the Output

### Similarity Report

Each matching component shows:

1. **Component Name** - The existing component being compared
2. **Similarity %** - How similar (0-100%)
3. **Reuse Potential %** - Estimated code that could be reused
4. **Shared Features** - What features they have in common
5. **Common Hooks** - React hooks both components use
6. **Recommendation** - Action to take

### Recommendation Types

| Similarity | Recommendation | Action |
|-----------|----------------|--------|
| 80%+ | **EXTEND** | Add props/variants to existing component |
| 60-79% | **COPY-THEN-MODIFY** | Copy the file and customize for new use case |
| 40-59% | **EXTRACT UTILS** | Extract shared logic to hooks/utilities |
| <40% | **CREATE NEW** | Safe to create new component |

## Decision Guide

### When Similarity >= 80%

```
SubmitPage matches 82% of your proposed form
  → EXTEND: Add variant prop to control form fields
  → Keep shared logic in one place
  → Reuse 70% of code
```

### When Similarity 60-79%

```
ResolveModal matches 65% of your proposed modal
  → COPY-THEN-MODIFY: Copy file and customize
  → Independent components, no risk of cross-contamination
  → Document the copy with comments
```

### When Similarity 40-59%

```
SubmitPage matches 50% of your file upload component
  → EXTRACT UTILITIES: Create useFileUpload() hook
  → Both components use the shared hook
  → Bug fixes benefit both components
```

### When Similarity < 40%

```
No significant matches found
  → CREATE NEW: Safe to build from scratch
  → No duplication risk
  → Clear that this is unique
```

## Real Examples from Analysis

### Issue-Tracker Project

```
✓ SubmitPage: 25.5% similar
  - Form handling with fields
  - File upload capability
  - Input validation
  RECOMMENDATION: Use for reference, extract shared utilities

✓ LoanIssueFormPage: 25.5% similar
  - Form handling with 4+ fields
  - File upload capability
  - Input validation
  RECOMMENDATION: Use for reference, extract shared utilities
```

### Los Issue-Tracker Project

```
✓ TicketForm: 25.5% similar
  - File upload capability
  - Input validation
  - Async operations
  RECOMMENDATION: Use for reference, extract shared utilities
```

## Advanced Usage

### Analyzing Multiple Projects

```bash
# Analyze project 1
python3 similarity_detector.py /path/to/project1 "Form component"

# Analyze project 2
python3 similarity_detector.py /path/to/project2 "Form component"

# Compare results to find best practices
```

### Batch Analysis

```bash
#!/bin/bash
for project in /path/to/projects/*; do
  echo "Analyzing: $project"
  python3 similarity_detector.py "$project" "Form with validation"
  echo ""
done
```

### Extracting JSON for Automation

The script outputs JSON at the end. To capture just the JSON:

```bash
python3 similarity_detector.py /path/to/project "Description" 2>/dev/null | tail -20 > results.json
```

## What the Script Analyzes

### 1. Hook Usage (30% weight)
- `useState`, `useEffect`, `useContext`, `useRef`, `useCallback`, etc.
- Similar hooks = similar state management patterns

### 2. State Variables (20% weight)
- Variable names and inferred types
- Examples: formData, errors, loading, attachmentFiles

### 3. JSX Patterns (20% weight)
- DOM elements: form, input, textarea, select, button
- Components: Modal, Button, Card, etc.
- Layouts: flex, grid, spacing patterns

### 4. Imports (15% weight)
- External libraries: react-hot-toast, framer-motion, lucide-react
- Custom hooks and contexts

### 5. Form Fields (10% weight)
- Input types: text, email, textarea, select, file
- Number of fields
- Field names

### 6. Event Handlers (5% weight)
- handleSubmit, handleChange, handleValidate, etc.
- Async patterns

### 7. Feature Flags (varies)
- has_async_operations
- has_validation
- has_file_upload
- has_error_handling
- has_modal_or_dialog

## Tips & Best Practices

### Tip 1: Be Descriptive

Good descriptions:
- "Form component for user feedback with file attachments"
- "Modal dialog for confirming dangerous actions"
- "Page showing list of items with filtering and sorting"

Poor descriptions:
- "Form"
- "Component"
- "New form like the existing one"

### Tip 2: Check Top 5 Results

The script shows top 10 results. Usually the top 3-5 are most relevant.

### Tip 3: Look for Shared Patterns

Even if similarity is low, you might find:
- Shared validation logic
- Shared API patterns
- Shared UI components

### Tip 4: Document Your Decision

When you decide to extend/copy/create, add a comment:

```typescript
/**
 * Based on similarity analysis:
 * - SubmitPage: 82% similar
 * Decision: EXTEND with variant prop
 */
export default function FeedbackForm({ variant = 'feedback' }: Props) {
  // ...
}
```

## Troubleshooting

### No components found

```
Error: No React components found in the project.
```

**Solution:** Check that src/ directory exists and contains .tsx/.jsx files

### Wrong number of components

```
Found 5 components (expected 20)
```

**Solution:** The script skips:
- node_modules/
- dist/
- build/
- .next/

Make sure components are in src/ directory

### No similar components

```
CREATE NEW: No significant similarities found.
```

**Solution:**
- Try a more specific description
- Your component is likely unique
- Safe to create new component

## Need Help?

See the full guide: `component-reuse-detection.md`

Contains:
- Detailed similarity metrics explanation
- Decision matrices with examples
- Safe extension patterns
- Copy-then-modify workflow
- Common pitfalls to avoid
- FAQ section
