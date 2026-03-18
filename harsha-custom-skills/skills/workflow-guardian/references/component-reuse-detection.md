# Component Reuse Detection Guide for Workflow Guardian

## Table of Contents

1. [When Similarity Detection Triggers](#when-similarity-detection-triggers)
2. [Similarity Metrics Explained](#similarity-metrics-explained)
3. [Decision Matrix](#decision-matrix)
4. [Safe Extension Patterns](#safe-extension-patterns)
5. [The Copy-Then-Modify Pattern](#the-copy-then-modify-pattern)
6. [Implementation Examples](#implementation-examples)
7. [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)

---

## When Similarity Detection Triggers

The similarity detector runs **automatically before creating ANY new component file**. This is a defensive check to ensure we maximize code reuse and maintain consistency across the codebase.

### Detection Triggers

Similarity detection should be invoked whenever Claude is asked to:

1. **Create a new form component** — Check against existing form components
2. **Create a new modal or dialog** — Check against existing modals
3. **Create a new page or page-like component** — Check against existing pages
4. **Create components with file handling** — Check against file upload components
5. **Create components with validation** — Check against validated form components
6. **Create components with API integration** — Check against data-fetching components
7. **Create components with animations** — Check against animated components
8. **Create any component with 50+ lines of code** — Always run detection

### The Pre-Creation Workflow

Before creating a new component, Claude should:

1. **Run the similarity detector** with the component description
2. **Review the results** — Look at the top 3-5 most similar components
3. **Make a decision** based on the similarity percentage and reuse potential
4. **Either extend** an existing component, **copy-then-modify** an existing one, or **create new**
5. **Document the decision** in a comment if copying/extending

### Example: Detecting a New Form Component

```
User asks: "Create a feedback form component with name, email, message fields and file attachment"

Claude should:
1. Run: similarity_detector.py <project> "Form component with email, message, and file attachment"
2. Get results showing:
   - SubmitPage.tsx: 82% similar (has form, attachments, validation)
   - LoanIssueFormPage.tsx: 78% similar (has form, attachments, validation)
3. Decide: These are very similar. Should extend or copy-then-modify instead of creating new
```

---

## Similarity Metrics Explained

### What Makes Two Components "Similar"?

The detector analyzes **7 key dimensions** of component similarity:

#### 1. **Hook Usage Patterns** (30% weight)

Components that share the same React hooks are likely to have similar state management and lifecycle patterns.

**Matching hooks indicate:**
- `useState` + `useEffect` → Form/page-like components with initialization
- `useCallback` + `useMemo` → Performance-optimized components with complex logic
- `useContext` → Shared state/authentication patterns
- `useRef` → DOM manipulation or file input handling

**Example:**
```typescript
// SubmitPage uses: useState, useRef, useEffect
// LoanIssueFormPage uses: useState, useRef, useEffect
// Commonality: Both manage form state with file input refs

// Decision: High reuse potential - similar hook patterns
```

#### 2. **State Variables and Types** (20% weight)

Similar state variable names and types indicate similar data models and business logic.

**What to look for:**
- `formData` or similar → Form handling
- `attachmentFiles` / `images` → File upload
- `uploadProgress` → Multi-step async operations
- `errors` / `error` → Validation and error handling
- `isSubmitting` / `loading` → Async operation state
- `success` / `completed` → Success states

**Example:**
```typescript
// SubmitPage state:
// - formData: SubmissionFormData
// - attachmentFiles: File[]
// - uploadProgress: UploadProgress | null
// - fileSizeWarning: string | null

// LoanIssueFormPage state:
// - formData: LoanIssueFormData
// - attachmentFiles: File[]
// - uploadProgress: UploadProgress | null
// - fileSizeWarning: string | null

// Decision: ~90% state pattern match - excellent reuse candidate
```

#### 3. **JSX Structure Patterns** (20% weight)

Similar DOM structures indicate similar UI/UX patterns.

**Common patterns detected:**
- `form` + `button` → Form submission pattern
- `input` + `select` + `textarea` → Multi-field form pattern
- `Modal` + `AnimatePresence` → Modal UI pattern
- `flex-layout` + `space-*` → Layout pattern
- `animation` → Framer Motion usage
- `error` display patterns → Validation error handling

**Example:**
```typescript
// SubmitPage JSX patterns:
// - form, input, textarea, button
// - flex-layout, space-y-5
// - animation (success screen), loading states
// - error display

// LoanIssueFormPage JSX patterns:
// - form, input, textarea, select, button
// - flex-layout, space-y-6
// - animation (success screen), loading states
// - error display with modal

// Decision: 85% JSX pattern match - very compatible
```

#### 4. **Import Patterns** (15% weight)

Shared dependencies indicate similar tooling and architecture.

**Common libraries that indicate patterns:**
- `react-hot-toast` → Toast notifications
- `framer-motion` + `AnimatePresence` → Animations
- `lucide-react` → Icon usage
- `supabase` → Backend integration
- Custom context/hooks → Architectural patterns

#### 5. **Form Field Similarity** (10% weight)

The number and types of form fields indicate data complexity.

**Field types tracked:**
- Text inputs (`text`, `email`, `url`, `password`)
- Select dropdowns
- Textarea fields
- File inputs
- Date/time inputs
- Checkbox/radio inputs

**Matching fields suggests:**
- Similar data models
- Similar validation patterns
- Similar submission logic

**Example:**
```typescript
// SubmitPage form fields:
// - actionable (select)
// - detailedActionable (textarea)
// - lsqLink (url input)
// - urn (text input)
// - comments (textarea)
// - attachmentFiles (file input)

// LoanIssueFormPage form fields:
// - entity (select)
// - issueType (select)
// - subIssue (select)
// - actionRequested (select)
// - opportunityId (text input)
// - lsqUrl (url input)
// - name (text input)
// - notes (textarea)
// - attachmentFiles (file input)

// Decision: 6-8 similar form fields = strong reuse candidate
```

#### 6. **Event Handler Patterns** (10% weight)

Similar event handlers indicate similar user interactions.

**Common handlers:**
- `handleSubmit` → Form submission
- `handleInputChange` → Form field updates
- `handleFileChange` → File input changes
- `handleValidation` → Validation logic
- `handleError` → Error handling

#### 7. **Feature Flags** (15% weight)

Boolean features indicate component capabilities:

| Feature | Indicates |
|---------|-----------|
| `has_async_operations` | API calls, async logic, `await` patterns |
| `has_error_handling` | Error states, error messages, error UI |
| `has_validation` | Input validation, constraint checking |
| `has_file_upload` | File handling, file input elements |
| `has_modal_or_dialog` | Modal/overlay UI, backdrop |
| `custom_hooks` | Reusable logic extracted to hooks |

**Example:**
```typescript
// SubmitPage features:
// - has_async_operations: YES (file upload to Google Drive)
// - has_error_handling: YES (try/catch, toast.error)
// - has_validation: YES (required field checks)
// - has_file_upload: YES (attachmentFiles)
// - has_modal_or_dialog: YES (success modal)
// - custom_hooks: useSimpleAuth

// LoanIssueFormPage features:
// - has_async_operations: YES (file upload)
// - has_error_handling: YES (validation errors, try/catch)
// - has_validation: YES (required fields, format checks)
// - has_file_upload: YES (attachmentFiles)
// - has_modal_or_dialog: YES (success display)
// - custom_hooks: useSimpleAuth

// Decision: Perfect feature match (100%) = EXTEND candidate
```

### Similarity Percentage Calculation

```
Similarity % = (Weighted matching features / Total possible features) × 100

Components with 80%+ similarity share ~80% of logic
Components with 60%+ similarity can share 50-60% of code
Components with 40%+ similarity should share utility functions/hooks
Components with <20% similarity are too different
```

---

## Decision Matrix

Use this matrix to decide whether to **CREATE**, **EXTEND**, or **COPY-THEN-MODIFY**.

### Decision Tree

```
similarity_percentage >= 80%
    AND reuse_potential >= 70%
    AND component_complexity >= medium
    └─> DECISION: EXTEND (add props/variants)
        WHY: Similar enough that duplicating is wasteful

similarity_percentage >= 60%
    AND reuse_potential >= 50%
    └─> DECISION: COPY-THEN-MODIFY (safer than extend)
        WHY: Different enough for variants, but copying is safer than refactoring

similarity_percentage >= 40%
    AND reuse_potential >= 30%
    └─> DECISION: EXTRACT SHARED UTILITIES
        WHY: Share validation/helper functions, keep components separate

similarity_percentage < 40%
    OR reuse_potential < 30%
    └─> DECISION: CREATE NEW (safe)
        WHY: Too different to safely reuse
```

### Decision Matrix Table

| Similarity | Reuse Potential | Component Complexity | Recommendation | Risk Level |
|-----------|-----------------|---------------------|----------------|-----------|
| 90%+ | 80%+ | Any | **EXTEND** - parameterize | Very Low |
| 80-89% | 70-79% | Medium+ | **EXTEND** with variants | Low |
| 70-79% | 60-69% | Medium+ | **COPY-THEN-MODIFY** | Low-Medium |
| 60-69% | 50-59% | Medium | **COPY-THEN-MODIFY** | Medium |
| 50-59% | 40-49% | Any | **SHARE UTILS** + create new | Medium |
| 40-49% | 30-39% | Small | **CREATE NEW** safely | Medium |
| <40% | <30% | Any | **CREATE NEW** | Low |

### Examples Applying the Matrix

#### Example 1: Form Components (80% Similar)

```
New component: "Feedback form with email, message, attachment"
Existing: SubmitPage.tsx (82% similar)

Matrix lookup:
- Similarity: 82% (80-89% range)
- Reuse Potential: 75%
- Complexity: Medium (form + file upload)

RECOMMENDATION: EXTEND
ACTION: Add a "variant" prop to control form fields
IMPLEMENTATION: Make SubmitPage generic to accept different form configurations

Risk mitigation:
- Use feature flags/props to customize behavior
- Add clear prop documentation
- Test all variants thoroughly
```

#### Example 2: Modal Components (65% Similar)

```
New component: "Confirmation dialog with form fields"
Existing: ResolveModal.tsx (65% similar)

Matrix lookup:
- Similarity: 65% (60-69% range)
- Reuse Potential: 55%
- Complexity: Medium

RECOMMENDATION: COPY-THEN-MODIFY
ACTION: Copy ResolveModal and modify for new use case
BENEFITS:
- Clear separation of concerns
- No risk of breaking existing modal
- Easier to add variant-specific logic
```

#### Example 3: Utility Extraction (45% Similar)

```
New component: "File validator with drag-drop"
Existing: SubmitPage (50% similar - just file handling)

Matrix lookup:
- Similarity: 50% (50-59% range)
- Reuse Potential: 40%
- Complexity: Small (just files)

RECOMMENDATION: EXTRACT SHARED UTILITIES
ACTION:
1. Create useFileUpload() hook
2. Create validateFiles() utility
3. Both old and new components use the utilities
4. Create new component with different UI
```

---

## Safe Extension Patterns

### When to Extend Existing Components

Extend an existing component **ONLY when**:

1. **Similarity >= 80%** — Components are nearly identical
2. **Reuse potential >= 70%** — Most of the code is reusable
3. **Changes are additive, not subtractive** — You're adding features, not removing them
4. **Clear variant/mode pattern** — Easy to distinguish variants with props
5. **No breaking changes** — Existing code still works exactly the same

### Pattern 1: Variant/Mode Pattern

```typescript
// BEFORE: SubmitPage handles only one type of submission
export default function SubmitPage() {
  // ... component code
}

// AFTER: Support multiple submission types via prop
interface SubmitPageProps {
  variant?: 'issue' | 'feedback' | 'loan';  // Add variant prop
}

export default function SubmitPage({ variant = 'issue' }: SubmitPageProps) {
  const [formFields, setFormFields] = useState(() => {
    switch (variant) {
      case 'feedback':
        return { email: '', message: '', rating: 5 };
      case 'loan':
        return { opportunityId: '', lsqUrl: '', entity: '' };
      default:
        return { actionable: '', detailedActionable: '', lsqLink: '', urn: '' };
    }
  });

  // ... rest of component with variant-aware rendering
}
```

**Advantages:**
- Single source of truth for form logic
- Consistent validation and submission
- Reduced duplication

**Risks to manage:**
- Component becomes more complex
- Variants might diverge over time
- Must test all variant combinations

### Pattern 2: Composition/Slot Pattern

```typescript
// Instead of extending a component, compose from reusable pieces

interface FormWrapperProps {
  children: React.ReactNode;
  onSubmit: (data: any) => Promise<void>;
  submitButtonLabel?: string;
  isLoading?: boolean;
}

export function FormWrapper({
  children,
  onSubmit,
  submitButtonLabel = 'Submit',
  isLoading = false,
}: FormWrapperProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <form onSubmit={handleSubmit} className="card p-6 space-y-5">
        {children}
        <Button type="submit" disabled={isSubmitting} isLoading={isSubmitting}>
          {submitButtonLabel}
        </Button>
      </form>
    </div>
  );
}

// Usage:
export function FeedbackForm() {
  return (
    <FormWrapper onSubmit={handleFeedbackSubmit}>
      <Input label="Email" name="email" type="email" required />
      <Textarea label="Message" name="message" required />
      <Input label="Rating" name="rating" type="number" min={1} max={5} />
    </FormWrapper>
  );
}
```

**Advantages:**
- Each component has single responsibility
- Easy to reuse FormWrapper in new forms
- Minimal coupling

**When to use:**
- Components share structure but not much logic
- Different data models/validation
- Variants differ significantly

### Pattern 3: Configuration Object Pattern

```typescript
// Use config objects to customize behavior without extending

interface FormConfig {
  title: string;
  fields: Array<{
    name: string;
    type: 'text' | 'email' | 'textarea' | 'select';
    label: string;
    required?: boolean;
    validation?: (value: string) => string | null;
  }>;
  onSubmit: (data: Record<string, string>) => Promise<void>;
  submitButtonLabel?: string;
}

export function GenericForm({ config }: { config: FormConfig }) {
  const [formData, setFormData] = useState(
    Object.fromEntries(config.fields.map(f => [f.name, '']))
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};

    for (const field of config.fields) {
      if (field.required && !formData[field.name].trim()) {
        newErrors[field.name] = `${field.label} is required`;
      }
      if (field.validation) {
        const error = field.validation(formData[field.name]);
        if (error) newErrors[field.name] = error;
      }
    }

    if (Object.keys(newErrors).length === 0) {
      await config.onSubmit(formData);
    } else {
      setErrors(newErrors);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <h1>{config.title}</h1>
      {config.fields.map(field => (
        <Input
          key={field.name}
          label={field.label}
          name={field.name}
          type={field.type}
          value={formData[field.name]}
          onChange={e => setFormData(prev => ({ ...prev, [field.name]: e.target.value }))}
          error={errors[field.name]}
          required={field.required}
        />
      ))}
      <Button type="submit">{config.submitButtonLabel ?? 'Submit'}</Button>
    </form>
  );
}

// Usage:
const feedbackConfig: FormConfig = {
  title: 'Send Feedback',
  fields: [
    { name: 'email', type: 'email', label: 'Email', required: true },
    { name: 'message', type: 'textarea', label: 'Message', required: true },
  ],
  onSubmit: async (data) => {
    await api.submitFeedback(data);
  },
};

export function FeedbackForm() {
  return <GenericForm config={feedbackConfig} />;
}
```

**Advantages:**
- Highly reusable across different forms
- Configuration is clear and declarative
- Business logic separated from UI

**When to use:**
- Multiple similar forms with different field sets
- Complex validation that's shared
- Need to generate forms dynamically

---

## The Copy-Then-Modify Pattern

This is the **SAFEST and most pragmatic** approach for reusing components with 60-79% similarity.

### Why Copy-Then-Modify is Better Than Extend

| Aspect | Extend | Copy-Then-Modify |
|--------|--------|------------------|
| Risk of breaking existing code | **HIGH** (shared code) | **ZERO** (separate files) |
| Testing complexity | **HIGH** (many variants) | **MEDIUM** (one variant) |
| Future refactoring | **HARD** (coupled code) | **EASY** (independent) |
| Cognitive load | **MEDIUM** (branching logic) | **HIGH initially, but clear** |
| Maintenance burden | **GROWS** (more variants) | **BOUNDED** (fixed file) |
| When similar components diverge | **RISKY** (forced changes) | **SAFE** (independent evolution) |

### When to Use Copy-Then-Modify

Use copy-then-modify when:

1. **60-75% similar** — Different enough for variants, similar enough to reuse patterns
2. **Different use cases** — Forms serve different business purposes
3. **Likely to diverge** — Future changes might differ between the two
4. **Team wants clarity** — One file per use case is easier to understand

### Copy-Then-Modify Workflow

#### Step 1: Identify Source Component

```
Proposed: "Loan applicant form"
Analysis: 72% similar to LoanIssueFormPage.tsx
Decision: Copy-then-modify
Source: /src/pages/LoanIssueFormPage.tsx
```

#### Step 2: Copy and Rename

```bash
# Copy the source file
cp src/pages/LoanIssueFormPage.tsx src/pages/LoanApplicantFormPage.tsx

# Update component name in the file
# export default function LoanIssueFormPage()
# becomes
# export default function LoanApplicantFormPage()
```

#### Step 3: Document the Copy

Add a comment at the top of the new file:

```typescript
/**
 * Loan Applicant Form Component
 *
 * COPIED FROM: src/pages/LoanIssueFormPage.tsx
 * SIMILARITY: 72% - Shares form structure, file upload, and validation patterns
 * DIVERGENCE POINTS:
 *   - Uses different form fields (applicant data vs. issue reporting)
 *   - Different validation rules (applicant verification vs. issue classification)
 *   - Different submission endpoint and data format
 *
 * MAINTENANCE NOTE:
 * If updating core form logic (file upload, validation), consider:
 * - Can this change apply to both files? (extract to utility)
 * - Or should each file maintain its own version?
 * - Prefer extracting utilities for shared patterns
 */
```

#### Step 4: Customize for New Use Case

```typescript
// Original field
const ENTITY_OPTIONS = ['Applicant', 'Co-applicant'];

// Customize for new form
const APPLICANT_TYPES = ['Individual', 'Sole Proprietor', 'Company'];

// Original state
const [formData, setFormData] = useState<LoanIssueFormData>({
  entity: '',
  issueType: '',
  // ...
});

// Customize state
const [formData, setFormData] = useState<LoanApplicantFormData>({
  applicantType: '',
  firstName: '',
  lastName: '',
  email: '',
  // ...
});
```

#### Step 5: Extract Shared Utilities

As you modify, identify reusable logic:

```typescript
// In original LoanIssueFormPage.tsx and new LoanApplicantFormPage.tsx
// BOTH use similar file upload logic

// EXTRACT: Create a shared hook
// hooks/useFileUpload.ts
export function useFileUpload(maxSize = 200) {
  const [attachmentFiles, setAttachmentFiles] = useState<File[]>([]);
  const [attachmentPreviews, setAttachmentPreviews] = useState<Map<string, string>>(
    new Map()
  );
  const [fileSizeWarning, setFileSizeWarning] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFiles = (newFiles: File[]) => {
    // Shared file processing logic
  };

  return {
    attachmentFiles,
    setAttachmentFiles,
    attachmentPreviews,
    fileInputRef,
    fileSizeWarning,
    processFiles,
  };
}

// BOTH components now use:
const { attachmentFiles, processFiles, fileInputRef } = useFileUpload();
```

#### Step 6: Test Independently

```typescript
// Create separate test file
// src/pages/__tests__/LoanApplicantFormPage.test.tsx

describe('LoanApplicantFormPage', () => {
  it('should render applicant form with correct fields', () => {
    // Test applicant-specific behavior
  });

  it('should validate applicant data correctly', () => {
    // Test applicant-specific validation
  });

  it('should not affect LoanIssueFormPage', () => {
    // Ensure no shared state or side effects
  });
});
```

### Copy-Then-Modify Anti-Patterns to Avoid

#### Anti-Pattern 1: Unmanaged Duplication

```typescript
// BAD: Copied code but didn't extract shared utilities
// Now file upload logic is duplicated in 3 files
// Bug fix must be applied in 3 places

// GOOD: Extract file upload logic to hook
const { attachmentFiles, processFiles } = useFileUpload();
```

#### Anti-Pattern 2: Cross-File Dependencies

```typescript
// BAD: Copied component imports from the original
import { formData } from './LoanIssueFormPage'; // Don't do this!

// GOOD: Each component manages its own state
const [formData, setFormData] = useState<LoanApplicantFormData>({...});
```

#### Anti-Pattern 3: Forgetting to Update Imports

```typescript
// BAD: Original imports not updated
import type { LoanIssueFormData } from '@/types'; // Wrong type!

// GOOD: Use correct types
import type { LoanApplicantFormData } from '@/types';
```

#### Anti-Pattern 4: Losing Copy Traceability

```typescript
// BAD: No comment explaining the copy
export default function LoanApplicantFormPage() {
  // Where did this come from? Why so similar to LoanIssueFormPage?
}

// GOOD: Clear attribution
/**
 * COPIED FROM: LoanIssueFormPage
 * SIMILARITY: 72%
 * DIVERGENCE: Different form fields and validation
 */
export default function LoanApplicantFormPage() {
  // Clear intent and history
}
```

---

## Implementation Examples

### Example 1: Extending a Form Component (80% Similar)

**Scenario:** Need a "quick feedback" form that's 80% similar to existing SubmitPage

**Decision:** EXTEND with a `mode` prop

```typescript
// Original SubmitPage.tsx - BEFORE

export default function SubmitPage() {
  const [formData, setFormData] = useState<SubmissionFormData>({
    actionable: '',
    detailedActionable: '',
    lsqLink: '',
    urn: '',
    attachmentFiles: [],
    comments: '',
  });

  // ... validation and submission logic
}

// MODIFIED SubmitPage.tsx - AFTER

export interface SubmitPageProps {
  mode?: 'issue' | 'feedback';
}

export default function SubmitPage({ mode = 'issue' }: SubmitPageProps) {
  type FormData = mode === 'feedback' ? FeedbackFormData : SubmissionFormData;

  const [formData, setFormData] = useState<FormData>(() => {
    if (mode === 'feedback') {
      return {
        email: '',
        message: '',
        rating: 5,
        attachmentFiles: [],
      } as any;
    }
    return {
      actionable: '',
      detailedActionable: '',
      lsqLink: '',
      urn: '',
      attachmentFiles: [],
      comments: '',
    } as any;
  });

  const issueModeFields = [
    { name: 'actionable', label: 'Actionable Type', required: true },
    { name: 'detailedActionable', label: 'Details', required: true },
    { name: 'lsqLink', label: 'LSQ Link', required: true },
    { name: 'urn', label: 'URN', required: true },
  ];

  const feedbackModeFields = [
    { name: 'email', label: 'Your Email', required: true },
    { name: 'message', label: 'Feedback', required: true },
    { name: 'rating', label: 'Rating', required: true },
  ];

  const fields = mode === 'feedback' ? feedbackModeFields : issueModeFields;

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
          {mode === 'feedback' ? 'Send Feedback' : 'Submit Issue'}
        </h1>
      </div>

      <div className="card p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {fields.map(field => (
            <Input
              key={field.name}
              label={field.label}
              name={field.name}
              required={field.required}
              // ... props
            />
          ))}
          {/* File upload section - shared */}
          {/* Attachments section */}
        </form>
      </div>
    </div>
  );
}
```

**Testing:**
```typescript
describe('SubmitPage', () => {
  describe('issue mode (default)', () => {
    it('should show issue-specific fields', () => {
      render(<SubmitPage mode="issue" />);
      expect(screen.getByLabelText('Actionable Type')).toBeInTheDocument();
    });
  });

  describe('feedback mode', () => {
    it('should show feedback-specific fields', () => {
      render(<SubmitPage mode="feedback" />);
      expect(screen.getByLabelText('Rating')).toBeInTheDocument();
    });
  });

  it('should not break issue mode when adding feedback mode', () => {
    // Ensure backward compatibility
  });
});
```

### Example 2: Copy-Then-Modify a Modal (65% Similar)

**Scenario:** Need a "confirm action" modal, 65% similar to ResolveModal

**Decision:** COPY-THEN-MODIFY

**Step 1: Copy the file**

```bash
cp src/components/ResolveModal.tsx src/components/ConfirmActionModal.tsx
```

**Step 2: Update and customize**

```typescript
// src/components/ConfirmActionModal.tsx

/**
 * Confirm Action Modal
 *
 * COPIED FROM: src/components/ResolveModal.tsx (65% similarity)
 * DIFFERENCES:
 * - Used for general action confirmation, not ticket resolution
 * - Simpler form (action + notes, no recommended actions)
 * - Different callback signatures
 *
 * SHARED PATTERNS:
 * - Modal structure with focus trap
 * - Backdrop and animation patterns
 * - Form validation before submission
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle } from 'lucide-react';
import { useFocusTrap } from '../hooks/useFocusTrap';
import { Button } from './ui/Button';
import { Textarea } from './ui/Input';

interface ConfirmActionModalProps {
  title: string;
  message: string;
  actionLabel?: string;
  onConfirm: (notes: string) => Promise<void>;
  onClose: () => void;
  isDangerous?: boolean;
}

export function ConfirmActionModal({
  title,
  message,
  actionLabel = 'Confirm',
  onConfirm,
  onClose,
  isDangerous = false,
}: ConfirmActionModalProps) {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const modalRef = useRef<HTMLDivElement>(null);

  useFocusTrap(modalRef, {
    enabled: true,
    onEscape: onClose,
  });

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!notes.trim()) {
      setError('Notes are required');
      return;
    }

    setLoading(true);
    try {
      await onConfirm(notes.trim());
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-modal-title"
      >
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
          aria-hidden="true"
        />

        <motion.div
          ref={modalRef}
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          className="relative bg-white rounded-xl shadow-2xl w-full max-w-md p-4"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h2 id="confirm-modal-title" className="text-lg font-semibold">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-neutral-400 hover:text-neutral-600"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Message */}
          <p className="text-sm text-neutral-600 mb-4">{message}</p>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              label="Notes (required)"
              value={notes}
              onChange={e => {
                setNotes(e.target.value);
                setError('');
              }}
              placeholder="Explain why you're performing this action..."
              rows={3}
              error={error}
            />

            {/* Buttons */}
            <div className="flex gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={onClose}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant={isDangerous ? 'danger' : 'primary'}
                loading={loading}
                className="flex-1"
              >
                {actionLabel}
              </Button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
```

**Usage:**
```typescript
// In parent component
const [showConfirm, setShowConfirm] = useState(false);

return (
  <>
    <Button onClick={() => setShowConfirm(true)}>Delete Item</Button>

    {showConfirm && (
      <ConfirmActionModal
        title="Delete Item?"
        message="This action cannot be undone."
        actionLabel="Delete"
        isDangerous
        onConfirm={async (notes) => {
          await api.deleteItem({ id: itemId, reason: notes });
        }}
        onClose={() => setShowConfirm(false)}
      />
    )}
  </>
);
```

### Example 3: Extracting Shared Utilities (45% Similar)

**Scenario:** Both SubmitPage and LoanIssueFormPage have identical file upload logic

**Decision:** EXTRACT SHARED UTILITIES

**Step 1: Create shared hook**

```typescript
// hooks/useFileUpload.ts

import { useState, useRef, useCallback, useEffect } from 'react';
import toast from 'react-hot-toast';
import { validateTotalFileSize, formatFileSize, type UploadProgress } from '@/lib/driveUpload';

interface UseFileUploadOptions {
  maxSize?: number;
  acceptedTypes?: string[];
  onPaste?: boolean;
}

export function useFileUpload({
  maxSize = 200,
  acceptedTypes = ['image/*', 'video/*', '.pdf'],
  onPaste = true,
}: UseFileUploadOptions = {}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [attachmentFiles, setAttachmentFiles] = useState<File[]>([]);
  const [attachmentPreviews, setAttachmentPreviews] = useState<Map<string, string>>(
    new Map()
  );
  const [fileSizeWarning, setFileSizeWarning] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);

  // File processing
  const processFiles = useCallback(
    (newFiles: File[]) => {
      setFileSizeWarning(null);
      const allFiles = [...attachmentFiles, ...newFiles];
      const validation = validateTotalFileSize(allFiles, maxSize);

      if (!validation.valid) {
        toast.error(validation.message!);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }

      if (validation.warning) {
        setFileSizeWarning(validation.message!);
      }

      setAttachmentFiles(allFiles);

      const newPreviews = new Map(attachmentPreviews);
      newFiles.forEach(file => {
        const fileId = `${file.name}-${file.size}-${file.lastModified}`;
        newPreviews.set(fileId, URL.createObjectURL(file));
      });
      setAttachmentPreviews(newPreviews);
    },
    [attachmentFiles, attachmentPreviews, maxSize]
  );

  // Remove attachment
  const removeAttachment = useCallback(
    (fileToRemove: File) => {
      const fileId = `${fileToRemove.name}-${fileToRemove.size}-${fileToRemove.lastModified}`;
      setAttachmentFiles(prev =>
        prev.filter(f => f !== fileToRemove)
      );

      const previewUrl = attachmentPreviews.get(fileId);
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      const newPreviews = new Map(attachmentPreviews);
      newPreviews.delete(fileId);
      setAttachmentPreviews(newPreviews);

      const remainingFiles = attachmentFiles.filter(f => f !== fileToRemove);
      if (remainingFiles.length === 0) {
        setFileSizeWarning(null);
      } else {
        const validation = validateTotalFileSize(remainingFiles, maxSize);
        setFileSizeWarning(validation.warning ? validation.message! : null);
      }
    },
    [attachmentPreviews, attachmentFiles, maxSize]
  );

  // Handle file input change
  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length > 0) {
        processFiles(files);
      }
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    [processFiles]
  );

  // Clipboard paste support
  useEffect(() => {
    if (!onPaste) return;

    const handlePaste = async (e: Event) => {
      const clipboardEvent = e as ClipboardEvent;
      const items = clipboardEvent.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.indexOf('image') !== -1) {
          clipboardEvent.preventDefault();
          const blob = item.getAsFile();
          if (!blob) return;

          const file = new File(
            [blob],
            `screenshot-${Date.now()}.png`,
            { type: blob.type || 'image/png' }
          );

          toast.success('Screenshot pasted!');
          processFiles([file]);
          return;
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, [onPaste, processFiles]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      attachmentPreviews.forEach(url => URL.revokeObjectURL(url));
    };
  }, []);

  return {
    fileInputRef,
    attachmentFiles,
    setAttachmentFiles,
    attachmentPreviews,
    fileSizeWarning,
    uploadProgress,
    setUploadProgress,
    processFiles,
    removeAttachment,
    handleFileChange,
  };
}
```

**Step 2: Use the hook in both components**

```typescript
// In SubmitPage.tsx

import { useFileUpload } from '@/hooks/useFileUpload';

export default function SubmitPage() {
  const {
    fileInputRef,
    attachmentFiles,
    attachmentPreviews,
    fileSizeWarning,
    processFiles,
    removeAttachment,
    handleFileChange,
  } = useFileUpload({
    maxSize: 200,
    acceptedTypes: ['image/*', 'video/*', '.pdf'],
    onPaste: true,
  });

  // ... rest of component - now uses shared file upload logic
}

// In LoanIssueFormPage.tsx - use the same hook
export default function LoanIssueFormPage() {
  const { fileInputRef, attachmentFiles, ...fileUploadProps } = useFileUpload();

  // ... rest of component - now uses shared file upload logic
}
```

**Benefits:**
- Single source of truth for file upload logic
- Bug fixes apply everywhere
- Easy to test in isolation
- Each component focuses on its domain-specific logic

---

## Common Pitfalls to Avoid

### Pitfall 1: Extending When You Should Copy

```typescript
// BAD: Extended component to handle 5 different variants
export default function Form({ variant }: FormProps) {
  if (variant === 'a') {
    // ... 50 lines of variant-a code
  } else if (variant === 'b') {
    // ... 50 lines of variant-b code
  } else if (variant === 'c') {
    // ... 50 lines of variant-c code
  }
  // Component now 500+ lines with branching logic everywhere
}

// BETTER: Separate components when they diverge significantly
export function FormA() { /* 80 lines */ }
export function FormB() { /* 80 lines */ }
export function FormC() { /* 80 lines */ }
```

**Rule of thumb:** If you have more than 2-3 variants or component > 400 lines, consider separate files.

### Pitfall 2: Copy-Paste Without Attribution

```typescript
// BAD: No indication where code came from
export default function NewForm() {
  // ...identical to SubmitPage...
}

// GOOD: Clear attribution and divergence notes
/**
 * COPIED FROM: src/pages/SubmitPage.tsx
 * SIMILARITY: 65%
 * DIVERGENCE:
 * - Different form fields
 * - Custom validation rules
 * - Different submission endpoint
 */
export default function NewForm() {
  // ...
}
```

### Pitfall 3: Breaking Existing Code During Extension

```typescript
// BAD: Changed required prop signature
export default function SubmitPage({ variant }: SubmitPageProps) {
  // Old code: <SubmitPage /> — BREAKS
  // New code: <SubmitPage variant="issue" /> — works
}

// GOOD: Maintain backward compatibility
export default function SubmitPage({ variant = 'issue' }: SubmitPageProps) {
  // Old code: <SubmitPage /> — still works
  // New code: <SubmitPage variant="feedback" /> — also works
}
```

### Pitfall 4: Extracting Utilities That Are Too Specific

```typescript
// BAD: Utility is so specific it's only used in one place
export function validateLoanIssueForm(data: LoanIssueFormData) {
  // Only called from LoanIssueFormPage
  // Why extract?
}

// GOOD: Extract when reused in 2+ places
export function validateFileSize(files: File[], maxMB: number) {
  // Used by SubmitPage, LoanIssueFormPage, and any future file upload
}
```

### Pitfall 5: Uncontrolled Duplication

```typescript
// BAD: Same file upload code copied to 5 files
// Bug discovered: file preview not working in IE
// Must fix in 5 places 😱

// GOOD: Use shared hook from the start
const { attachmentFiles, processFiles } = useFileUpload();
// Bug fix in one place, benefits all 5 files
```

### Pitfall 6: Creating Too Many Variants

```typescript
// BAD: Component becomes a "god component"
<Form
  variant="loan"
  showRating={true}
  hideAttachments={false}
  customValidation={fn}
  theme="dark"
  onCustomSubmit={fn}
  // ... 20 more props
/>

// This component tries to do everything for everyone
// Becomes unmaintainable

// GOOD: Accept some duplication for clarity
<LoanForm />
<FeedbackForm />
<SupportForm />
// Each component is clear about its purpose
// Easier to maintain and extend
```

---

## Summary: Decision Tree

When proposing a new component, follow this flow:

```
1. Run similarity detector
   └─ Get list of similar components

2. Check similarity of top match
   └─ If 80%+: EXTEND (add props/variants)
   └─ If 60-80%: COPY-THEN-MODIFY
   └─ If 40-60%: EXTRACT UTILS + create new
   └─ If <40%: CREATE NEW

3. If extending:
   └─ Use variant pattern or composition
   └─ Maintain backward compatibility
   └─ Extract common logic to hooks

4. If copying:
   └─ Document the copy with comments
   └─ Update all imports and types
   └─ Extract shared utilities
   └─ Test independently

5. If extracting utilities:
   └─ Create hooks or helper functions
   └─ Update all calling code
   └─ Test in isolation

6. Always:
   └─ Don't repeat code in 3+ places
   └─ Mark copied code clearly
   └─ Keep variants <= 2-3 before splitting
   └─ Extract utilities that are used 2+ times
```

---

## FAQ

**Q: How do I know if my component is too similar to extend?**
A: If it has 70%+ similarity and shares 80%+ of the code, it's a good extend candidate. Otherwise, copy-then-modify is safer.

**Q: Should I always extract utilities?**
A: Only if the utility is used 2+ times. One-off utilities add complexity without benefit.

**Q: What if extending a component breaks tests?**
A: That's a sign to copy-then-modify instead. Breaking tests means tight coupling.

**Q: Can I copy a component even if it's only 50% similar?**
A: Yes, if the shared patterns are valuable and the components serve different purposes. Just document it.

**Q: What's the maximum number of variants a component should have?**
A: 2-3 variants is reasonable. Beyond that, separate components are clearer.

**Q: How do I refactor highly duplicated code after copy-pasting?**
A: Extract shared logic to utilities/hooks incrementally. Don't try to refactor a large component at once.

