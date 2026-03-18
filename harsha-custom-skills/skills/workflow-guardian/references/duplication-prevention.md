# Duplication Prevention Reference

**Purpose**: Prevent creating duplicate components, pages, and logic blocks. Detect duplication patterns before code is written.

**Trigger**: Before creating any new file that serves a similar purpose to an existing component.

---

## 1. Duplication Detection Protocol

Execute this checklist **before** creating any new file:

### 1.1 Purpose Search
1. Identify what the new file does (e.g., "form for loan issues")
2. List existing files that serve similar purposes (e.g., forms, pages, list views)
3. Search codebase:
   - `grep -r "form\|Form\|PAGE" --include="*.tsx" --include="*.ts" src/`
   - Check `/pages`, `/components`, `/features` directories first

### 1.2 Field List Comparison
1. Extract all form fields from your proposed component
2. For each existing similar component, list its fields
3. Calculate shared field percentage: `(shared_fields / total_fields) × 100`
4. **Decision rule**: If ≥50% field overlap, DO NOT CREATE - extend existing instead

Example:
```
Proposed LoanIssueFormPage fields: entity, issueType, opportunityId, lsqUrl, notes, attachments
Existing SubmitPage fields: actionable, detailedActionable, lsqLink, comments, attachments

Shared logic: attachments handling, lsqLink field
Overlap: ~33% - BUT combined with function similarity = extend SubmitPage
```

### 1.3 Logic Comparison
Search for these patterns in existing files:
- **File upload handlers** - Search: `handleFileChange`, `processFiles`, `removeAttachment`
- **Validation logic** - Search: `validate`, `required`, `pattern`, `validator`
- **API calls** - Search: `fetch(`, `client.`, `axios` with similar endpoints
- **State patterns** - Search: `useState<Form`, `useReducer` with same structure
- **Toast/error handling** - Search: `toast.error`, `showError`, `onError`

### 1.4 Duplication Scoring System

Assign points for each match found:
- File upload logic identical: +20 points
- Validation patterns ≥80% similar: +15 points
- State structure identical: +15 points
- Success screen ≥90% similar: +10 points
- Error handling pattern identical: +10 points
- Same API endpoints: +10 points

**Scoring Decision**:
- **50+ points**: EXTEND existing component - do not duplicate
- **30-50 points**: Extract shared logic into hook or utility - create both
- **<30 points**: Safe to create new file independently

---

## 2. Component Extraction Patterns

When duplication is detected (score ≥50), follow this refactoring flow:

### 2.1 Extract Shared Form Container

Create a generic wrapper component that both forms use:

**Before** (two 400-600 line pages):
```typescript
// SubmitPage.tsx - 390 lines with full form, upload, success screen
// LoanIssueFormPage.tsx - 603 lines, 65% duplicated from SubmitPage
```

**After** (generic container + role-specific pages):
```typescript
// FormContainer.tsx - 80 lines, shared layout and success screen
// SubmitPage.tsx - 120 lines, role-specific fields only
// LoanIssueFormPage.tsx - 140 lines, role-specific fields only
```

**Pattern**:
```typescript
// src/components/forms/SubmissionFormContainer.tsx
interface SubmissionFormContainerProps {
  title: string;
  description: string;
  children: ReactNode;  // Pass role-specific form fields
  onSubmit: (e: React.FormEvent) => Promise<void>;
  isSubmitting: boolean;
  success: SuccessData | null;
  onSubmitAnother: () => void;
  uploadProgress?: UploadProgress | null;
}

export function SubmissionFormContainer({
  title,
  description,
  children,
  onSubmit,
  isSubmitting,
  success,
  onSubmitAnother,
  uploadProgress,
}: SubmissionFormContainerProps) {
  // Shared layout: container, card, header
  // Shared success screen: green checkmark, submission ID
  // Shared upload progress bar
  // Children injected for role-specific fields
  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{title}</h1>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
      {success ? renderSuccess(success, onSubmitAnother) : renderForm()}
      {/* ... */}
    </div>
  );
}
```

### 2.2 Extract Shared Hooks

Move identical state logic into hooks:

**useFormSubmission hook** - handles loading, errors, success state:
```typescript
// src/hooks/useFormSubmission.ts
export function useFormSubmission<T>(
  submitFn: (data: T, onProgress: (p: UploadProgress) => void) => Promise<any>
) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState<any>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);

  const handleSubmit = async (formData: T) => {
    try {
      setIsSubmitting(true);
      await submitFn(formData, setUploadProgress);
      setSuccess({ submissionId: /* from response */ });
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsSubmitting(false);
      setUploadProgress(null);
    }
  };

  return { isSubmitting, success, uploadProgress, setUploadProgress, handleSubmit };
}
```

**useAttachmentHandling hook** - file upload, size validation, preview management:
```typescript
// src/hooks/useAttachmentHandling.ts
export function useAttachmentHandling() {
  const [attachmentFiles, setAttachmentFiles] = useState<File[]>([]);
  const [attachmentPreviews, setAttachmentPreviews] = useState<Map<string, string>>(new Map());
  const [fileSizeWarning, setFileSizeWarning] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFiles = (newFiles: File[]) => {
    const allFiles = [...attachmentFiles, ...newFiles];
    const validation = validateTotalFileSize(allFiles);

    if (!validation.valid) {
      toast.error(validation.message!);
      return;
    }

    setAttachmentFiles(allFiles);
    // Create previews...
  };

  const removeAttachment = (fileId: string) => {
    setAttachmentFiles(prev => prev.filter(f => f.name !== fileId));
    setAttachmentPreviews(prev => {
      const next = new Map(prev);
      next.delete(fileId);
      return next;
    });
  };

  const handlePaste = (e: ClipboardEvent) => {
    const items = e.clipboardData?.items;
    const imageFile = Array.from(items || []).find(item => item.type.startsWith('image/'));
    if (imageFile) {
      processFiles([imageFile as any]);
    }
  };

  return {
    attachmentFiles,
    attachmentPreviews,
    fileSizeWarning,
    fileInputRef,
    processFiles,
    removeAttachment,
    handlePaste,
  };
}
```

### 2.3 Use Props for Role-Specific Variations

Instead of duplicating, pass configuration as props:

```typescript
// src/pages/SubmitPage.tsx
export function SubmitPage() {
  const { handleSubmit, isSubmitting, success, uploadProgress } = useFormSubmission(
    createSubmission  // Role-specific API function
  );
  const { attachmentFiles, processFiles, removeAttachment } = useAttachmentHandling();
  const [formData, setFormData] = useState<SubmissionFormData>({ /* role-specific fields */ });

  return (
    <SubmissionFormContainer
      title="Submit Action"
      description="Document an actionable item"
      onSubmit={async (e) => {
        e.preventDefault();
        await handleSubmit(formData);
      }}
      isSubmitting={isSubmitting}
      success={success}
      onSubmitAnother={() => resetForm()}
      uploadProgress={uploadProgress}
    >
      {/* Role-specific fields only */}
      <Select name="actionable" value={formData.actionable} options={ACTIONABLE_OPTIONS} />
      <Textarea name="detailedActionable" value={formData.detailedActionable} />
      {/* ... */}
    </SubmissionFormContainer>
  );
}

// src/pages/LoanIssueFormPage.tsx
export function LoanIssueFormPage() {
  const { handleSubmit, isSubmitting, success, uploadProgress } = useFormSubmission(
    createLoanIssueSubmission  // Different API function
  );
  const { attachmentFiles, processFiles, removeAttachment } = useAttachmentHandling();
  const [formData, setFormData] = useState<LoanIssueFormData>({ /* different fields */ });

  return (
    <SubmissionFormContainer
      title="Submit Loan Issue"
      description="Report a loan-related issue"
      onSubmit={async (e) => {
        e.preventDefault();
        await handleSubmit(formData);
      }}
      isSubmitting={isSubmitting}
      success={success}
      onSubmitAnother={() => resetForm()}
      uploadProgress={uploadProgress}
    >
      {/* Role-specific fields only */}
      <Select name="entity" value={formData.entity} options={ENTITY_OPTIONS} />
      <Select name="issueType" value={formData.issueType} options={ISSUE_TYPE_OPTIONS} />
      {/* ... */}
    </SubmissionFormContainer>
  );
}
```

### 2.4 Use Composition for Layout Variations

Create a shared attachment component:

```typescript
// src/components/forms/AttachmentInput.tsx
interface AttachmentInputProps {
  files: File[];
  previews: Map<string, string>;
  onFilesAdded: (files: File[]) => void;
  onFileRemoved: (fileId: string) => void;
  onPaste: (e: ClipboardEvent) => void;
  maxSizeWarning?: string | null;
}

export function AttachmentInput({
  files,
  previews,
  onFilesAdded,
  onFileRemoved,
  onPaste,
  maxSizeWarning,
}: AttachmentInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="space-y-3">
      <div
        className="border-2 border-dashed rounded-lg p-4 text-center hover:bg-gray-50"
        onPaste={onPaste}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={(e) => onFilesAdded(Array.from(e.target.files || []))}
          className="hidden"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="text-sm text-ring-600 hover:underline"
        >
          Click to upload or paste screenshots
        </button>
      </div>

      {maxSizeWarning && (
        <div className="p-3 bg-yellow-50 text-yellow-700 text-xs rounded">
          {maxSizeWarning}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {files.map((file, idx) => (
          <div key={idx} className="relative">
            {previews.get(file.name) && (
              <img src={previews.get(file.name)} alt={file.name} className="h-16 w-16 object-cover rounded" />
            )}
            <button
              type="button"
              onClick={() => onFileRemoved(file.name)}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 3. Telltale Signs of Impending Duplication

Watch for these red flags when creating new files:

### 3.1 File-Level Red Flags
- **Copying entire files**: "I'll copy SubmitPage.tsx and rename it LoanIssueFormPage.tsx"
  - Fix: Extract container, keep role-specific logic only
- **Same import list**: `import { useState, useRef, useEffect } from 'react';` appears identically in two files
  - Fix: Both files likely share state management - extract hook
- **Same component imports**: Both import `Select`, `Textarea`, `Input` from same path
  - Fix: Safe if using different fields, but check field count overlap

### 3.2 State Declaration Red Flags
- **Identical useState patterns**:
  ```typescript
  const [formData, setFormData] = useState<FormData>({ /* field1, field2, field3 */ });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  ```
  Both appearing in two files = extract into hook
- **Same validation state**: `const [errors, setErrors] = useState({});` in multiple places
  - Fix: Create `useFormValidation` hook

### 3.3 Function-Level Red Flags
- **Identical function implementations**: `processFiles()`, `removeAttachment()`, `handleFileChange()`
  - Fix: Move to hook immediately
- **Same API call pattern**: Both calling `fetch('/api/submit')` or `client.post(endpoint)`
  - Fix: Create shared API client or wrapper function
- **Same error handling**: `catch (error) { toast.error(...) }` appearing identically
  - Fix: Wrap in custom hook or utility function

### 3.4 UI/Layout Red Flags
- **Identical card structures**: Both rendering `<div className="card p-6">` with same children order
  - Fix: Extract component
- **Duplicate success screens**: Both showing green checkmark, submission ID, "Submit Another" button
  - Fix: Create `SuccessScreen.tsx` component
- **Same button styling**: Identical className strings for submit button
  - Fix: Use component instead of duplicating className

---

## 4. Decision Tree: Create or Extend?

```
START: Do you need to add a new file/component?
│
├─ Is it a form, page, or list view?
│  │
│  ├─ YES → Does a similar component already exist?
│  │  │
│  │  ├─ YES → Do they share ≥50% of fields/logic?
│  │  │  │
│  │  │  ├─ YES → EXTEND existing
│  │  │  │         Step 1: Extract shared logic to hooks
│  │  │  │         Step 2: Create generic container component
│  │  │  │         Step 3: Create role-specific pages with container
│  │  │  │         ✓ Result: DRY, maintainable, single source of truth
│  │  │  │
│  │  │  └─ NO → Can they share ≥70% of UI/layout?
│  │  │           │
│  │  │           ├─ YES → Extract layout into container component
│  │  │           │         Create separate pages for field logic
│  │  │           │         ✓ Result: Shared layout, different data
│  │  │           │
│  │  │           └─ NO → OK to create new file independently
│  │  │                   But still check for extractable hooks
│  │  │
│  │  └─ NO → OK to create new file independently
│  │           Check for reusable patterns (useAttachmentHandling, etc.)
│  │
│  └─ NO (not form/page/list) → Check if similar utility/hook exists
│     │
│     ├─ YES → Extend or wrap it
│     └─ NO → Create independently
│
END: File created with minimal duplication
```

---

## 5. Real-World Example: SubmitPage vs LoanIssueFormPage

### 5.1 The Problem

**SubmitPage.tsx** (390 lines):
- File upload with validation (43 lines)
- Form state management (12 lines)
- Submission logic (42 lines)
- Success screen (22 lines)
- Various validation helpers

**LoanIssueFormPage.tsx** (603 lines):
- File upload logic **COPIED** from SubmitPage (42 lines, identical)
- Form state **SIMILAR STRUCTURE** (11 lines, different fields)
- Submission logic **COPIED PATTERN** (47 lines, different API call)
- Success screen **NEARLY IDENTICAL** (46 lines, same layout)
- Same validation patterns

**Result**: 65% code duplication
- Bug in file upload handling fixed in one file, other breaks
- UI framework update requires changes in two places
- Paste screenshot feature added to LoanIssueForm only, SubmitPage lacks it

### 5.2 What Should Have Happened

**Step 1: Extract Hooks**
```typescript
// useFormSubmission.ts - handles all submission states and flow
// useAttachmentHandling.ts - handles file upload, validation, preview
// useFormValidation.ts - if validation logic is shared
```

**Step 2: Create Container Component**
```typescript
// SubmissionFormContainer.tsx
// - Shared form layout (card, max-width, header)
// - Shared success screen (green checkmark, ID, button)
// - Shared upload progress bar
// - Accepts children for role-specific fields
```

**Step 3: Create Role-Specific Pages**
```typescript
// SubmitPage.tsx (120 lines)
// - Uses SubmissionFormContainer
// - Declares role-specific form fields (actionable, detailedActionable, lsqLink, comments)
// - Calls hooks with createSubmission function

// LoanIssueFormPage.tsx (130 lines)
// - Uses SubmissionFormContainer
// - Declares role-specific form fields (entity, issueType, opportunityId, etc.)
// - Calls hooks with createLoanIssueSubmission function
// - Optional: renderDecisionTree content slot
```

### 5.3 The Refactoring Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total Lines | 993 | ~450 | -55% |
| Duplicated Lines | 650 | 0 | -100% |
| Files to Update on Bug Fix | 2-3 | 1 | -50-67% |
| Maintenance Cost | High | Low | Critical |
| Time to Add New Form | 20 min (copy+modify) | 5 min (extend container) | 4x faster |

### 5.4 Bonus: Fixing ModifySubmissionPage

Because both forms were duplicated, ModifySubmissionPage.tsx had to handle both:

```typescript
// BEFORE: 605 lines with massive if/else
if (type === 'submit') {
  // Handle SubmitPage data
  const [formData, setFormData] = useState<SubmissionFormData>({...});
} else {
  // Handle LoanIssueFormPage data
  const [formData, setFormData] = useState<LoanIssueFormData>({...});
}
```

**AFTER**: With shared container, ModifySubmissionPage becomes:

```typescript
export function ModifySubmissionPage({ id, type }: Props) {
  const submission = useSubmission(id);

  return type === 'submit' ? (
    <SubmitPage initialData={submission} />
  ) : (
    <LoanIssueFormPage initialData={submission} />
  );
}
```

One page becomes a simple router to the shared form pages.

---

## 6. Quick Reference Checklist

Before committing code, ask:

- [ ] Does this file share >50% logic with an existing file?
- [ ] Are there identical functions (file upload, validation, API calls)?
- [ ] Does the success screen look the same as another file?
- [ ] Would a bug fix in one place need fixing in another?
- [ ] Can I extract a hook instead of duplicating state logic?
- [ ] Can I create a container component instead of duplicating layout?
- [ ] Did I copy an entire file and just rename variables?

**If YES to any**: Stop and refactor before committing.
