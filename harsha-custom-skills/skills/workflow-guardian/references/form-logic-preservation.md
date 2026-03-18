# Form Logic Preservation Patterns for Workflow Guardian

## Critical Context: Why Form Patterns Matter

Forms are where user intent enters a system. When form patterns diverge across an application, it creates maintenance nightmares, inconsistent user experience, and subtle bugs. The Workflow Guardian skill exists to prevent this divergence by teaching **pattern matching** rather than **form creation from scratch**.

This document catalogs form patterns from two real production projects:
- **Ring Kissht Issue Tracker**: Standard and Loan Issue submission forms (390-603 lines each)
- **LOS Issue Tracker**: Ticket creation form with advanced image upload (702 lines)

The core lesson: When adding a new form, copy the EXISTING form's structure completely, then modify only what needs to differ.

---

## 1. Form Pattern Inventory

### How to Catalog Every Form in an Existing App

When joining a new project or adding forms, create this inventory FIRST. Don't start coding until you understand all existing forms.

#### 1.1 The Ring Kissht Issue Tracker Forms

**Project Location**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/`

Two core form types exist in this project:

##### Form A: SubmitPage.tsx (390 lines)
**Purpose**: Submit general issues/actionables
**Location**: `src/pages/SubmitPage.tsx`

**Field Inventory**:
```typescript
interface SubmissionFormData {
  actionable: string;                    // SELECT: required
  detailedActionable: string;            // TEXTAREA: required
  lsqLink: string;                       // INPUT(url): required
  urn: string;                           // INPUT(text): required
  attachmentFiles?: File[];              // FILE: optional, multiple
  comments?: string;                     // TEXTAREA: optional
}

// Field Types in JSX
- Select dropdown: ACTIONABLE_OPTIONS (5 options: Follow up, Data correction, Status update, Documentation, Other)
- Textarea (4 rows): Detailed description
- Input(url): LSQ Link validation
- Input(text): URN identifier
- Optional: File attachments with paste support (Ctrl+V)
- Optional: Comments textarea (3 rows)
```

**Validation Pattern**:
```javascript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Toast-based inline validation (not form-level)
  if (!formData.actionable) { toast.error('Please select an actionable'); return; }
  if (!formData.detailedActionable.trim()) { toast.error('Please provide detailed actionable'); return; }
  if (!formData.lsqLink.trim()) { toast.error('Please provide LSQ Link'); return; }
  if (!formData.urn.trim()) { toast.error('Please provide URN'); return; }
  if (!role) { toast.error('You must be logged in'); return; }

  // Submit after validation passes
  setIsSubmitting(true);
  try {
    const submissionId = await createSubmission(formData, role, (progress) => setUploadProgress(progress));
    setSuccess({ submissionId });
    toast.success(`Submission ${submissionId} created successfully!`);
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to create submission');
  } finally {
    setIsSubmitting(false);
    setUploadProgress(null);
  }
};
```

**Error Display Pattern**: Toast notifications (react-hot-toast), no inline field errors

**File Upload Pattern**:
```javascript
// State management
const [attachmentFiles, setAttachmentFiles] = useState<File[]>([]);
const [attachmentPreviews, setAttachmentPreviews] = useState<Map<string, string>>(new Map());
const [fileSizeWarning, setFileSizeWarning] = useState<string | null>(null);
const fileInputRef = useRef<HTMLInputElement>(null);

// Validation
const processFiles = (newFiles: File[]) => {
  const allFiles = [...formData.attachmentFiles || [], ...newFiles];
  const validation = validateTotalFileSize(allFiles); // 200 MB limit
  if (!validation.valid) {
    toast.error(validation.message!);
    return;
  }
  setFormData(prev => ({ ...prev, attachmentFiles: allFiles }));
  // Create object URLs for image/video previews
  newFiles.forEach(file => {
    const fileId = `${file.name}-${file.size}-${file.lastModified}`;
    newPreviews.set(fileId, URL.createObjectURL(file));
  });
};

// Paste support (Ctrl+V)
useEffect(() => {
  const handlePaste = async (e: Event) => {
    const clipboardEvent = e as ClipboardEvent;
    const items = clipboardEvent.clipboardData?.items;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf('image') !== -1) {
        clipboardEvent.preventDefault();
        const blob = item.getAsFile();
        const file = new File([blob], `screenshot-${Date.now()}.png`, { type: blob.type || 'image/png' });
        toast.success('Screenshot pasted!');
        processFiles([file]);
        return;
      }
    }
  };
  window.addEventListener('paste', handlePaste);
  return () => window.removeEventListener('paste', handlePaste);
}, []);
```

**Success State Pattern**:
- After successful submission, display success card with submission ID
- Show "Submit Another" button to reset form and allow multiple submissions
- Success state returned as: `{ submissionId: string }`

---

##### Form B: LoanIssueFormPage.tsx (603 lines)
**Purpose**: Submit loan-specific issues with decision tree analysis
**Location**: `src/pages/LoanIssueFormPage.tsx`

**Field Inventory**:
```typescript
interface LoanIssueFormData {
  entity: string;                        // SELECT: required (Applicant, Co-applicant)
  issueType: string;                     // SELECT: required (10 options)
  subIssue?: string;                     // SELECT: conditional (depends on issueType)
  actionRequested: string;               // SELECT: required (7 options)
  opportunityId: string;                 // INPUT(text): required, format validation (IDEP[A-Z0-9]+)
  lsqUrl: string;                        // INPUT(url): required
  date: string;                          // INPUT(date): auto-set, disabled
  name: string;                          // INPUT(text): required
  notes?: string;                        // TEXTAREA: conditional required (required if issueType includes 'Other')
  attachmentFiles?: File[];              // FILE: optional, multiple
}

// CRITICAL: Conditional Field Rules
// 1. subIssue only shows if issueType matches keys in SUB_ISSUES_MAP
// 2. notes required=true only if issueType.includes('Other')
// 3. date is auto-set to current date, field is disabled
```

**Conditional Rendering Pattern** (ESSENTIAL):
```javascript
// Track when subIssue should be visible
useEffect(() => {
  const issueType = formData.issueType;
  if (issueType && SUB_ISSUES_MAP[issueType] && SUB_ISSUES_MAP[issueType].length > 0) {
    setShowSubIssue(true);
  } else {
    setShowSubIssue(false);
    setFormData(prev => ({ ...prev, subIssue: '' })); // Clear when hidden
  }
}, [formData.issueType]);

// In JSX, render conditionally:
{showSubIssue && (
  <Select label="Sub-Issue" name="subIssue" value={formData.subIssue} onChange={handleInputChange} required>
    <option value="">Choose an option</option>
    {SUB_ISSUES_MAP[formData.issueType]?.map(option => (
      <option key={option} value={option}>{option}</option>
    ))}
  </Select>
)}

// Date is auto-set and disabled
useEffect(() => {
  const currentDate = new Date().toISOString().split('T')[0];
  setFormData(prev => ({ ...prev, date: currentDate }));
}, []);

// In handler, skip date changes
const handleInputChange = (e: React.ChangeEvent<...>) => {
  const { name, value } = e.target;
  if (name === 'date') return; // NEVER allow manual date changes
  setFormData(prev => ({ ...prev, [name]: value }));
};
```

**Validation Pattern** (DIFFERENT from SubmitPage):
```javascript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Multi-level validation with conditional requirements
  if (!formData.entity) { toast.error('Please select an entity'); return; }
  if (!formData.issueType) { toast.error('Please select an issue type'); return; }
  if (showSubIssue && !formData.subIssue) { toast.error('Please select a sub-issue'); return; }
  if (!formData.actionRequested) { toast.error('Please select an action requested'); return; }

  // Format validation: IDEP[A-Z0-9]+
  const oppIdPattern = /^IDEP[A-Z0-9]+$/i;
  if (!oppIdPattern.test(formData.opportunityId)) {
    toast.error('Opportunity ID must be in format IDEP followed by letters/numbers');
    return;
  }

  if (!formData.lsqUrl.trim()) { toast.error('Please provide LSQ URL'); return; }
  if (!formData.date) { toast.error('Please select a date'); return; }
  if (!formData.name.trim()) { toast.error('Please provide Applicant/Co-Applicant Name'); return; }

  // Conditional validation: notes required if "Other" selected
  if (formData.issueType.includes('Other') && !formData.notes?.trim()) {
    toast.error('Notes are required for "Other" issue type');
    return;
  }

  if (!role) { toast.error('You must be logged in'); return; }

  // Process submission
  try {
    const decisionResult = processLoanIssueDecisionTree(submissionData);
    const submissionId = await createLoanIssueSubmission(submissionData, role, decisionResult, ...);
    setSuccess({ submissionId, decisionResult }); // Different success payload
    toast.success(`Submission ${submissionId} created successfully!`);
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to create submission');
  }
};
```

**Decision Tree Processing** (UNIQUE to LoanIssue):
```javascript
function processLoanIssueDecisionTree(formData: LoanIssueFormData) {
  let recommendedAction = formData.actionRequested;
  let reason = '';
  const nextSteps: string[] = [];

  const issueType = formData.issueType;
  const subIssue = formData.subIssue || '';
  const notes = (formData.notes || '').toLowerCase();

  // Conditional logic based on issue type
  if (issueType.includes('Pan Issue')) {
    if (subIssue === 'Primary PAN Available' || notes.includes('primary')) {
      recommendedAction = 'Reject Lead (full or entity-specific)';
    } else {
      recommendedAction = 'Resolve Mapping (e.g., provide full phone no)';
    }
    reason = 'PAN verification or mapping failure detected.';
    nextSteps.push('Relogin with correct mobile no linked to PAN.');
  } else if (issueType.includes('Swapping')) {
    recommendedAction = 'Reject Lead (full or entity-specific)';
    reason = 'Role swap required (applicant ↔ co-applicant).';
    nextSteps.push('Add entity to target lead as opposite of current entity.');
  }
  // ... more branches ...

  return { recommendedAction, reason, nextSteps };
}
```

**Success State Pattern** (DIFFERENT from SubmitPage):
```javascript
if (success) {
  return (
    <div>
      {/* Display submission ID */}
      <p>{success.submissionId}</p>

      {/* UNIQUE: Show decision tree results */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3>Decision Tree Analysis</h3>
        <div>
          <span>Action: </span>
          <span>{success.decisionResult.recommendedAction}</span>
        </div>
        <div>
          <span>Reason: </span>
          <span>{success.decisionResult.reason}</span>
        </div>
        {success.decisionResult.nextSteps.length > 0 && (
          <div>
            <span>Next Steps:</span>
            <ul>
              {success.decisionResult.nextSteps.map((step: string, idx: number) => (
                <li key={idx}>{step}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
```

**Paste Handling Difference**:
```javascript
// SubmitPage: Simple add
useEffect(() => {
  const handlePaste = async (e: Event) => {
    // ... get blob ...
    toast.success('Screenshot pasted!');
    processFiles([file]);
  };
  window.addEventListener('paste', handlePaste);
  return () => window.removeEventListener('paste', handlePaste);
}, []);

// LoanIssueFormPage: Complex with existing files check
useEffect(() => {
  const handlePaste = async (e: Event) => {
    // ... get blob ...
    const hasExisting = formData.attachmentFiles && formData.attachmentFiles.length > 0;
    if (hasExisting) {
      const shouldAdd = window.confirm(
        `You have ${formData.attachmentFiles!.length} file(s). Click OK to ADD, Cancel to REPLACE.`
      );
      if (shouldAdd) {
        toast.success('Screenshot added!');
        processFiles([file]);
      } else {
        // Replace: clear existing, set new
        attachmentPreviews.forEach(url => URL.revokeObjectURL(url));
        setAttachmentPreviews(new Map());
        // ... set new file as sole attachment ...
        toast.success('Screenshot replaced existing files!');
      }
    } else {
      toast.success('Screenshot pasted!');
      processFiles([file]);
    }
  };
  window.addEventListener('paste', handlePaste);
  return () => window.removeEventListener('paste', handlePaste);
}, [formData.attachmentFiles, attachmentPreviews]); // Note dependency array difference
```

---

##### Form C: ModifySubmissionPage.tsx (605 lines)
**Purpose**: Edit existing submissions with change tracking
**Location**: `src/pages/ModifySubmissionPage.tsx`

**KEY DIFFERENCE**: This form handles BOTH standard and loan issue submissions dynamically.

```typescript
const [submission, setSubmission] = useState<Submission | null>(null);

// Load submission and determine form type
if (data.formType === 'loan_issue') {
  const formValues = {
    entity: data.entity || '',
    issueType: data.issueType || '',
    // ... loan issue fields ...
  };
  setLoanIssueFormData(formValues);
} else {
  const formValues = {
    actionable: data.actionable || '',
    detailedActionable: data.detailedActionable || '',
    // ... standard fields ...
  };
  setStandardFormData(formValues);
}

// Track modified fields
const modifiedFields = useMemo(() => {
  const modified: Set<string> = new Set();
  const isLoanIssue = submission?.formType === 'loan_issue';
  const currentData = isLoanIssue ? loanIssueFormData : standardFormData;

  for (const key of Object.keys(originalData)) {
    if (key === 'attachmentFiles') continue;
    if (currentData[key as keyof typeof currentData] !== originalData[key]) {
      modified.add(key);
    }
  }
  return modified;
}, [submission, loanIssueFormData, standardFormData, originalData]);

// Conditional rendering in JSX
{isLoanIssue ? (
  <>
    {/* Render LoanIssue fields */}
  </>
) : (
  <>
    {/* Render Standard fields */}
  </>
)}
```

---

#### 1.2 The LOS Issue Tracker Form

**Project Location**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/`

##### Form D: TicketForm.tsx (702 lines)
**Purpose**: Create new support tickets with image-heavy requirements
**Location**: `src/components/TicketForm.tsx`

**Field Inventory**:
```typescript
interface TicketFormProps {
  onSubmit: (data: {
    lsq_url: string;                     // INPUT(url): required
    trn: string;                         // INPUT(text): required
    image_urls: string[];                // FILE: REQUIRED minimum 1, maximum 5
    description: string;                 // TEXTAREA: required, min 10 chars
    issue_type: string;                  // HARDCODED: 'other'
    submitted_by: string;                // PASSED: current user email
    query_category?: string;             // SELECT: required
    sub_category?: string;               // SELECT: required
  }) => Promise<void>;
  submitterEmail: string;
}

// Unique aspect: Image files are MANDATORY, not optional
const MIN_IMAGES = 1;
const MAX_IMAGES = 5;
```

**Field State Tracking Pattern** (ADVANCED):
```javascript
interface FieldState {
  touched: boolean;
  valid: boolean;
}

const [fieldStates, setFieldStates] = useState<Record<string, FieldState>>({
  lsqUrl: { touched: false, valid: false },
  trn: { touched: false, valid: false },
  queryCategory: { touched: false, valid: false },
  subCategory: { touched: false, valid: false },
  description: { touched: false, valid: false },
  images: { touched: false, valid: false },
});

// This enables "punish late, reward early" validation UI pattern
// Fields show invalid state only AFTER user touches them
// Fields clear errors immediately when valid
```

**Completion Percentage Pattern** (UNIQUE):
```javascript
const completionPercentage = useMemo(() => {
  let completed = 0;
  const total = 6; // All fields required

  if (lsqUrl && isValidHttpsUrl(lsqUrl)) completed++;
  if (trn.trim()) completed++;
  if (queryCategory) completed++;
  if (subCategory) completed++;
  if (description.trim().length >= 10) completed++;
  if (images.length >= MIN_IMAGES) completed++;

  return Math.round((completed / total) * 100);
}, [lsqUrl, trn, queryCategory, subCategory, description, images.length]);

// Shows progress bar to user: [████░░░░░░] 50%
```

**Image Upload Pattern** (COMPLETELY DIFFERENT):
```javascript
// State for images
interface ImageFile {
  id: string;              // Unique ID
  file: File;              // Original file
  preview: string;         // Object URL for preview
}

const [images, setImages] = useState<ImageFile[]>([]);

// Validation
const addImageFiles = useCallback((files: File[]) => {
  const remainingSlots = MAX_IMAGES - images.length;
  if (remainingSlots <= 0) {
    setErrors((prev) => ({ ...prev, images: `Maximum ${MAX_IMAGES} images allowed` }));
    return;
  }

  const filesToAdd = files.slice(0, remainingSlots);
  const newImages: ImageFile[] = [];

  for (const file of filesToAdd) {
    const validationError = validateImageFile(file); // Checks: type, size, etc.
    if (validationError) {
      setErrors((prev) => ({ ...prev, images: validationError }));
      continue;
    }

    newImages.push({
      id: generateUniqueId(),
      file,
      preview: createPreviewUrl(file),
    });
  }

  if (newImages.length > 0) {
    setImages((prev) => [...prev, ...newImages]);
    setErrors((prev) => {
      const { images: _, ...rest } = prev;
      return rest; // Clear image error when valid
    });
    setFieldStates((prev) => ({
      ...prev,
      images: { touched: true, valid: true },
    }));
  }
}, [images.length]);

// Cleanup on unmount
useEffect(() => {
  return () => {
    imagesRef.current.forEach((img) => revokePreviewUrl(img.preview));
  };
}, []);
```

**Paste + Drag-Drop + Click Pattern**:
```javascript
// 1. Global paste listener
useEffect(() => {
  const handlePaste = (e: ClipboardEvent) => {
    const imageFile = getImageFromClipboard(e);
    if (imageFile) {
      e.preventDefault();
      addImageFiles([imageFile]);
    }
  };
  document.addEventListener('paste', handlePaste);
  return () => document.removeEventListener('paste', handlePaste);
}, [images.length]);

// 2. Drag and drop handlers
const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();
  setIsDragging(true);
};

const handleDrop = (e: React.DragEvent) => {
  e.preventDefault();
  setIsDragging(false);
  const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith('image/'));
  if (files.length > 0) {
    addImageFiles(files);
  }
};

// 3. Click handler
const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
  if (e.target.files) {
    addImageFiles(Array.from(e.target.files));
  }
  e.target.value = ''; // Reset input
};

// Drop zone JSX with visual feedback
<div
  onDragOver={handleDragOver}
  onDragLeave={handleDragLeave}
  onDrop={handleDrop}
  onClick={() => !loading && images.length < MAX_IMAGES && fileInputRef.current?.click()}
  className={`
    border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
    transition-all duration-fast
    ${isDragging ? 'border-primary-500 bg-primary-50/20' : 'border-neutral-300'}
    ${images.length >= MAX_IMAGES ? 'opacity-50 cursor-not-allowed' : ''}
  `}
>
  <Upload className="w-8 h-8 mx-auto mb-2" />
  <p className="text-sm">
    {images.length >= MAX_IMAGES
      ? 'Maximum images reached'
      : isDragging
      ? 'Drop images here'
      : 'Click to upload or drag and drop'}
  </p>
</div>
```

**Upload + Error Handling** (CRITICAL):
```javascript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (submittingRef.current) return; // Prevent double submission
  if (!validate()) return;

  submittingRef.current = true;
  setLoading(true);
  let uploadedImageUrls: string[] = [];

  try {
    // 1. Upload images to Supabase storage
    const ticketContext = `${submitterEmail.replace(/[^a-zA-Z0-9]/g, '_')}_${queryCategory}`;
    setUploadProgress({ current: 0, total: images.length });

    uploadedImageUrls = await uploadImages(
      images.map((img) => img.file),
      ticketContext,
      (current, total) => setUploadProgress({ current, total })
    );

    // 2. Verify all images uploaded
    if (uploadedImageUrls.length === 0) {
      setErrors({ images: 'Failed to upload images. Please try again.' });
      return;
    }

    if (uploadedImageUrls.length < images.length) {
      setErrors({ images: `Only ${uploadedImageUrls.length} of ${images.length} images uploaded. Please try again.` });
      await cleanupUploadedImages(uploadedImageUrls);
      uploadedImageUrls = [];
      return;
    }

    // 3. Create ticket (atomic operation)
    await onSubmit({
      lsq_url: lsqUrl.trim(),
      trn: trn.trim(),
      image_urls: uploadedImageUrls,
      description: description.trim(),
      issue_type: 'other',
      submitted_by: submitterEmail,
      query_category: queryCategory as QueryCategory,
      sub_category: subCategory as SubCategory,
    });

    // 4. Reset form on success
    setLsqUrl('');
    setTrn('');
    // ... reset all fields ...
    images.forEach((img) => revokePreviewUrl(img.preview));
    setImages([]);
    setSuccess(true);
    setTimeout(() => setSuccess(false), 3000);

    uploadedImageUrls = []; // Clear to prevent cleanup
  } catch (err) {
    console.error('Ticket creation error:', err);
    setErrors({ description: 'Failed to create ticket. Please try again.' });

    // 5. Cleanup orphaned images if creation fails
    if (uploadedImageUrls.length > 0) {
      await cleanupUploadedImages(uploadedImageUrls);
    }
  } finally {
    submittingRef.current = false;
    setLoading(false);
    setUploadProgress(null);
  }
};

// Cleanup helper
const cleanupUploadedImages = async (imageUrls: string[]) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return;

  const cleanupPromises = imageUrls.map(async (urlOrPath) => {
    try {
      const match = urlOrPath.match(/ticket-images\/(.+)$/);
      const path = match ? match[1] : urlOrPath;
      const { error } = await supabase.storage
        .from('ticket-images')
        .remove([path]);

      if (error) {
        console.error('Failed to cleanup image:', path, error);
      }
    } catch (err) {
      console.error('Cleanup error:', err);
    }
  });

  await Promise.allSettled(cleanupPromises);
};
```

---

### 1.3 Form Pattern Comparison Matrix

| Aspect | SubmitPage | LoanIssueFormPage | ModifySubmissionPage | TicketForm |
|--------|-----------|------------------|----------------------|-----------|
| **Purpose** | General submissions | Loan issue tracking | Edit existing | Create tickets |
| **Form Lines** | 390 | 603 | 605 | 702 |
| **Primary Fields** | 6 | 9 | Dual (both types) | 8 |
| **Conditional Fields** | None | subIssue, notes | Both types | None |
| **File Type** | Any (img/video/pdf) | Any | Any | Images only |
| **File Requirement** | Optional | Optional | N/A (existing) | REQUIRED (min 1) |
| **Max Files** | 200 MB total | 200 MB total | 200 MB total | 5 images max |
| **Validation UI** | Toast errors | Toast errors | N/A | Field state + touch |
| **Error Display** | Toast, warning banner | Toast, warning banner | N/A | Toast + inline |
| **Success Display** | Card with ID | Card + decision tree | Redirect to detail | Toast (3s) |
| **Paste Support** | Simple add | Add/Replace dialog | Not used | Clipboard API |
| **Image Preview** | Basic (img/video) | Basic (img/video) | Basic | Grid (3 cols) |
| **Progress Bar** | Upload % | Upload % | Upload % | Upload % + Completion % |
| **Decision Tree** | None | Yes (20 branches) | N/A | N/A |
| **Date Field** | None | Auto-set, disabled | N/A | None |
| **Format Validation** | URL pattern | IDEP format regex | N/A | HTTPS URL, min length |

---

## 2. The Duplication Trap: The #1 Form Failure Pattern

### Problem: How SubmitPage and LoanIssueFormPage Diverged (And Shouldn't Have)

These two forms solve 90% the same problem. They share:
- Same file upload logic (validateTotalFileSize, formatFileSize, UploadProgress)
- Same file preview rendering (image/video detection, remove button)
- Same paste handling (Ctrl+V, screenshot detection)
- Same toast-based error handling
- Same success state pattern
- Same attachment state management

**But they diverge in CRITICAL places that could have been unified:**

#### Divergence Point 1: Paste Handling Logic

**SubmitPage (lines 80-108)**: Simple approach
```javascript
useEffect(() => {
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
        return; // IMPORTANT: Exit after first image
      }
    }
  };

  window.addEventListener('paste', handlePaste);
  return () => window.removeEventListener('paste', handlePaste);
}, []); // EMPTY dependency array - potential stale closure bug
```

**LoanIssueFormPage (lines 200-249)**: Complex with file count check
```javascript
useEffect(() => {
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

        const hasExisting = formData.attachmentFiles && formData.attachmentFiles.length > 0;
        if (hasExisting) {
          const shouldAdd = window.confirm(
            `You have ${formData.attachmentFiles!.length} file(s). Click OK to ADD, Cancel to REPLACE.`
          );
          if (shouldAdd) {
            toast.success('Screenshot added!');
            processFiles([file]);
          } else {
            attachmentPreviews.forEach(url => URL.revokeObjectURL(url));
            setAttachmentPreviews(new Map());
            const newPreviews = new Map();
            const fileId = `${file.name}-${file.size}-${file.lastModified}`;
            newPreviews.set(fileId, URL.createObjectURL(file));
            setAttachmentPreviews(newPreviews);
            setFileSizeWarning(null);
            setFormData(prev => ({ ...prev, attachmentFiles: [file] }));
            toast.success('Screenshot replaced existing files!');
          }
        } else {
          toast.success('Screenshot pasted!');
          processFiles([file]);
        }
        return;
      }
    }
  };

  window.addEventListener('paste', handlePaste);
  return () => window.removeEventListener('paste', handlePaste);
}, [formData.attachmentFiles, attachmentPreviews]); // CORRECT: Includes dependencies
```

**Analysis**:
- SubmitPage has a stale closure bug (empty dependency array)
- LoanIssueFormPage has the fix (correct dependencies) BUT adds complexity
- This divergence creates maintenance burden: if you fix SubmitPage, must also fix LoanIssueFormPage
- CORRECT approach: Extract paste handler to shared utility

---

#### Divergence Point 2: File Removal Logic

**SubmitPage (lines 110-132)**:
```javascript
const removeAttachment = (fileToRemove: File) => {
  const fileId = `${fileToRemove.name}-${fileToRemove.size}-${fileToRemove.lastModified}`;

  // Update form data
  setFormData(prev => ({
    ...prev,
    attachmentFiles: (prev.attachmentFiles || []).filter(f => f !== fileToRemove)
  }));

  // Revoke preview
  const previewUrl = attachmentPreviews.get(fileId);
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
  }

  // Update previews map
  const newPreviews = new Map(attachmentPreviews);
  newPreviews.delete(fileId);
  setAttachmentPreviews(newPreviews);

  // Check warning after removal
  const remainingFiles = (formData.attachmentFiles || []).filter(f => f !== fileToRemove);
  if (remainingFiles.length === 0) {
    setFileSizeWarning(null);
  } else {
    const validation = validateTotalFileSize(remainingFiles);
    setFileSizeWarning(validation.warning ? validation.message! : null);
  }
};
```

**LoanIssueFormPage (lines 251-271)**: Identical pattern

**TicketForm (lines 169-183)**: Similar but different
```javascript
const removeImage = (id: string) => {
  setImages((prev) => {
    const imageToRemove = prev.find((img) => img.id === id);
    if (imageToRemove) {
      revokePreviewUrl(imageToRemove.preview);
    }
    const newImages = prev.filter((img) => img.id !== id);
    // Update validity
    setFieldStates((p) => ({
      ...p,
      images: { touched: true, valid: newImages.length >= MIN_IMAGES },
    }));
    return newImages;
  });
};
```

**Analysis**:
- All three are similar but TicketForm uses image IDs instead of file metadata
- Each form has slight variations, making copy-paste maintenance nightmare
- CORRECT approach: Create base `removeFile()` utility with hooks

---

#### Divergence Point 3: Conditional Required Fields

**SubmitPage**: All validation is unconditional
```javascript
if (!formData.actionable) { toast.error(...); return; }
if (!formData.detailedActionable.trim()) { toast.error(...); return; }
// All simple, required
```

**LoanIssueFormPage**: Conditional validation
```javascript
if (showSubIssue && !formData.subIssue) {
  toast.error('Please select a sub-issue');
  return;
}
// ...
if (formData.issueType.includes('Other') && !formData.notes?.trim()) {
  toast.error('Notes are required for "Other" issue type');
  return;
}
```

**TicketForm**: Field state-based validation
```javascript
const validate = () => {
  const newErrors: Record<string, string> = {};

  if (!lsqUrl.trim()) {
    newErrors.lsqUrl = 'LSQ URL is required';
  } else if (!isValidHttpsUrl(lsqUrl)) {
    newErrors.lsqUrl = 'Please enter a valid HTTPS URL';
  }
  // Each field stores error
  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

**Analysis**:
- Three different validation paradigms in one codebase!
- Adds cognitive load: which paradigm to use for new form?
- CORRECT approach: Standardize on ONE validation pattern

---

### 2.1 The SAFE Approach: Copy and Modify

When you need to add a new form to SubmitPage/LoanIssueFormPage codebase:

#### Step 1: Identify the closest existing form
```
New form purpose: "Submit equipment issue with vendor contact"
Closest match: SubmitPage (simple fields, file upload)
```

#### Step 2: Copy the ENTIRE file
```bash
cp src/pages/SubmitPage.tsx src/pages/EquipmentIssuePage.tsx
```

#### Step 3: Modify ONLY the parts that differ
```javascript
// CHANGE: Form type
interface EquipmentIssueFormData {
  issueType: string;          // NEW: Select from equipment options
  vendorName: string;         // NEW: Vendor contact name
  contactEmail: string;       // NEW: Vendor email
  description: string;        // SAME AS detailedActionable
  attachmentFiles?: File[];   // SAME
}

// CHANGE: State initialization
const [formData, setFormData] = useState<EquipmentIssueFormData>({
  issueType: '',
  vendorName: '',
  contactEmail: '',
  description: '',
  attachmentFiles: [],
});

// SAME: Everything else (handleInputChange, processFiles, removeAttachment, paste handler, submit pattern)

// CHANGE: Validation logic (only equipment-specific validations)
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!formData.issueType) {
    toast.error('Please select an issue type');
    return;
  }
  if (!formData.vendorName.trim()) {
    toast.error('Please provide vendor name');
    return;
  }
  if (!formData.contactEmail.trim()) {
    toast.error('Please provide vendor email');
    return;
  }
  if (!formData.description.trim()) {
    toast.error('Please provide description');
    return;
  }

  // SAME: Rest of submit logic
  setIsSubmitting(true);
  try {
    const submissionId = await createEquipmentIssue(formData, role, ...);
    setSuccess({ submissionId });
    toast.success(`Equipment issue ${submissionId} created!`);
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to create issue');
  } finally {
    setIsSubmitting(false);
  }
};

// CHANGE: JSX fields (but keep same structure)
<div className="card p-6">
  <form onSubmit={handleSubmit} className="space-y-5">
    <Select
      label="Issue Type"
      name="issueType"
      value={formData.issueType}
      onChange={handleInputChange}
      required
    >
      {/* Equipment-specific options */}
    </Select>

    <Input
      label="Vendor Name"
      name="vendorName"
      type="text"
      value={formData.vendorName}
      onChange={handleInputChange}
      required
      placeholder="Enter vendor name"
    />

    <Input
      label="Contact Email"
      name="contactEmail"
      type="email"
      value={formData.contactEmail}
      onChange={handleInputChange}
      required
      placeholder="vendor@company.com"
    />

    {/* SAME: File upload section (copy verbatim) */}
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        Attachments <span className="text-gray-400 font-normal">(optional)</span>
      </label>
      {/* ... entire attachment block from SubmitPage ... */}
    </div>

    {/* SAME: Submit button */}
    <Button
      type="submit"
      variant="primary"
      className="w-full"
      disabled={isSubmitting}
      isLoading={isSubmitting}
    >
      {uploadProgress ? 'Uploading...' : 'Submit'}
    </Button>
  </form>
</div>
```

**Key Principles**:
1. Copy the ENTIRE structure, not just functions
2. Change field names and validations
3. Keep attachment handling identical (don't reinvent)
4. Keep error display pattern identical (toast)
5. Keep success state pattern identical
6. Keep loading/progress pattern identical

---

### 2.2 The DANGEROUS Approach: Creating from Scratch

What happens when you DON'T follow the copy-and-modify pattern:

```javascript
// WRONG: Creating form from scratch
export default function NewForm() {
  // Created unique state management (inconsistent with SubmitPage)
  const [state, setState] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  // Different error handling (useCallback instead of useState)
  const [validationErrors, setValidationErrors] = useCallback(() => {}, []);

  // File upload logic rewritten (different from SubmitPage)
  const handleFiles = (files: FileList) => {
    const validFiles = [];
    files.forEach(file => {
      if (file.size < 5000000) validFiles.push(file);
    });
    setState(prev => ({ ...prev, files: validFiles }));
  };

  // Validation written differently
  const validate = () => {
    const errors = [];
    if (!state.field1) errors.push('Field 1 required');
    return errors.length === 0 ? null : errors;
  };

  // Submit written differently
  const handleSubmit = () => {
    const errors = validate();
    if (errors) {
      errors.forEach(err => console.log(err));
      return;
    }
    // ... submit ...
  };
}
```

**Problems introduced**:
1. File size validation (5 MB) differs from existing forms (200 MB) - inconsistency
2. Error handling via console.log vs toast - UX breaks consistency
3. No paste support (Ctrl+V) - users expect this
4. No preview display - users can't see what they uploaded
5. No preview cleanup - memory leaks with Object URLs
6. Different loading state pattern - confusion for maintainers
7. Different success notification - UX inconsistency
8. No file removal capability - users must reload if they add wrong file

**When this happens across a team**: multiply issues by number of forms created from scratch.

---

## 3. Form Extension Patterns: How to Safely Add to Existing Forms

### 3.1 Adding a New Field

**Scenario**: LoanIssueFormPage needs a new "Resolution Status" select field

#### Checklist (4 layers must update):

**Layer 1: TypeScript Type**
```typescript
export interface LoanIssueFormData {
  entity: string;
  issueType: string;
  subIssue?: string;
  actionRequested: string;
  opportunityId: string;
  lsqUrl: string;
  date: string;
  name: string;
  notes?: string;
  resolutionStatus?: string;  // NEW: Add to interface
  attachmentFiles?: File[];
}
```

**Layer 2: Component State**
```javascript
const [formData, setFormData] = useState<LoanIssueFormData>({
  entity: '',
  issueType: '',
  subIssue: '',
  actionRequested: '',
  opportunityId: '',
  lsqUrl: '',
  date: new Date().toISOString().split('T')[0],
  name: '',
  notes: '',
  resolutionStatus: '',  // NEW: Initialize state
  attachmentFiles: [],
});
```

**Layer 3: JSX Rendering**
```javascript
// Add to form, maintaining same structure
<Select
  label="Resolution Status"
  name="resolutionStatus"
  value={formData.resolutionStatus}
  onChange={handleInputChange}
  required // or optional, depending on need
>
  <option value="">Choose an option</option>
  <option value="pending">Pending</option>
  <option value="in_progress">In Progress</option>
  <option value="resolved">Resolved</option>
</Select>
```

**Layer 4: Submit Handler**
```javascript
// Add validation if required
if (!formData.resolutionStatus) {
  toast.error('Please select a resolution status');
  return;
}

// Add to submission data
const submissionData = { ...formData, date: currentDate };
const submissionId = await createLoanIssueSubmission(
  submissionData,
  role,
  decisionResult,
  (progress) => setUploadProgress(progress)
);
```

---

### 3.2 Adding Validation: Don't Mix Paradigms

**WRONG: Mixing validation approaches**
```javascript
// File 1: Form validation via toast (existing pattern)
if (!formData.actionable) {
  toast.error('Please select an actionable');
  return;
}

// File 2: Form validation via inline errors (new pattern)
const [errors, setErrors] = useState({});
if (!formData.newField) {
  setErrors(prev => ({ ...prev, newField: 'Required' }));
}

// Result: Users see BOTH toast and inline errors - confusing UX
```

**RIGHT: Match the existing validation pattern**
```javascript
// If form uses toast errors, add validation as toast
if (!formData.newField) {
  toast.error('Please provide field value');
  return;
}

// If form uses inline errors, add validation as inline
const newErrors = { ...errors };
if (!formData.newField) {
  newErrors.newField = 'Please provide field value';
}
setErrors(newErrors);
if (Object.keys(newErrors).length > 0) return;
```

---

### 3.3 Adding File Upload: Copy Exactly

**Scenario**: A form needs file uploads

**Correct approach**: Copy the ENTIRE upload block from SubmitPage or LoanIssueFormPage:

```javascript
// 1. Copy state
const [attachmentFiles, setAttachmentFiles] = useState<File[]>([]);
const [attachmentPreviews, setAttachmentPreviews] = useState<Map<string, string>>(new Map());
const [fileSizeWarning, setFileSizeWarning] = useState<string | null>(null);
const fileInputRef = useRef<HTMLInputElement>(null);

// 2. Copy processFiles function (no modifications)
const processFiles = (newFiles: File[]) => {
  setFileSizeWarning(null);
  const allFiles = [...(attachmentFiles || []), ...newFiles];
  const validation = validateTotalFileSize(allFiles);

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
};

// 3. Copy removeAttachment function
const removeAttachment = (fileToRemove: File) => {
  const fileId = `${fileToRemove.name}-${fileToRemove.size}-${fileToRemove.lastModified}`;
  setAttachmentFiles(prev => (prev || []).filter(f => f !== fileToRemove));

  const previewUrl = attachmentPreviews.get(fileId);
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
  }
  const newPreviews = new Map(attachmentPreviews);
  newPreviews.delete(fileId);
  setAttachmentPreviews(newPreviews);

  const remainingFiles = (attachmentFiles || []).filter(f => f !== fileToRemove);
  if (remainingFiles.length === 0) {
    setFileSizeWarning(null);
  } else {
    const validation = validateTotalFileSize(remainingFiles);
    setFileSizeWarning(validation.warning ? validation.message! : null);
  }
};

// 4. Copy paste handler
useEffect(() => {
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
}, []);

// 5. Copy handleFileChange
const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const files = Array.from(e.target.files || []);
  if (files.length > 0) {
    processFiles(files);
  }
  if (fileInputRef.current) {
    fileInputRef.current.value = '';
  }
};

// 6. Copy JSX upload section (entire div)
<div>
  <label className="block text-sm font-medium text-gray-700 mb-1.5">
    Attachments <span className="text-gray-400 font-normal">(optional)</span>
  </label>

  {attachmentFiles && attachmentFiles.length > 0 && (
    <div className="space-y-2 mb-3">
      {attachmentFiles.map((file) => {
        const fileId = `${file.name}-${file.size}-${file.lastModified}`;
        const previewUrl = attachmentPreviews.get(fileId);
        const isImage = file.type.startsWith('image/');
        const isVideo = file.type.startsWith('video/');

        return (
          <div key={fileId} className="p-3 border border-gray-200 rounded-md bg-gray-50">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <p className="text-sm text-gray-700 font-medium truncate">{file.name}</p>
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {formatFileSize(file.size)}
                  </span>
                </div>
                {previewUrl && isImage && (
                  <img src={previewUrl} alt={file.name} className="max-h-24 rounded mt-2" />
                )}
                {previewUrl && isVideo && (
                  <video src={previewUrl} controls className="max-h-24 rounded mt-2 w-full" />
                )}
              </div>
              <button
                type="button"
                onClick={() => removeAttachment(file)}
                className="flex-shrink-0 w-5 h-5 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center hover:bg-red-500 hover:text-white transition-colors text-xs"
              >
                x
              </button>
            </div>
          </div>
        );
      })}

      <div className="flex items-center justify-between text-xs text-gray-500 px-1">
        <span>Total: {formatFileSize(attachmentFiles.reduce((sum, f) => sum + f.size, 0))}</span>
        <span>Limit: 200 MB</span>
      </div>

      {fileSizeWarning && (
        <div className="p-2 bg-amber-50 border border-amber-200 rounded-md">
          <p className="text-xs text-amber-800">{fileSizeWarning}</p>
        </div>
      )}
    </div>
  )}

  <button
    type="button"
    onClick={() => fileInputRef.current?.click()}
    className="w-full p-6 border-2 border-dashed border-gray-300 rounded-md text-center hover:border-gray-400 hover:bg-gray-50 transition-colors"
  >
    <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
    <p className="text-sm text-gray-600">Click to upload or drag and drop</p>
    <p className="text-xs text-gray-400 mt-1">Images, Videos, PDFs - Paste screenshots with Ctrl+V</p>
  </button>

  <input
    ref={fileInputRef}
    type="file"
    accept="image/*,video/*,.pdf"
    multiple
    onChange={handleFileChange}
    className="hidden"
  />
</div>
```

DO NOT modify this section. Copy it exactly. If you need different behavior, create a new utility file and import it.

---

### 3.4 Adding Conditional Fields: Follow Existing Pattern

**Scenario**: New field should only appear if another field has specific value

**SubmitPage pattern**: None (all fields unconditional)

**LoanIssueFormPage pattern**: Use in ModifySubmissionPage

```javascript
// 1. Track visibility with useState
const [showSubIssue, setShowSubIssue] = useState(false);

// 2. Update visibility when dependency changes
useEffect(() => {
  const issueType = formData.issueType;
  if (issueType && SUB_ISSUES_MAP[issueType] && SUB_ISSUES_MAP[issueType].length > 0) {
    setShowSubIssue(true);
  } else {
    setShowSubIssue(false);
    setFormData(prev => ({ ...prev, subIssue: '' })); // Clear when hidden
  }
}, [formData.issueType]); // Dependency must include parent field

// 3. Conditional validation in submit
if (showSubIssue && !formData.subIssue) {
  toast.error('Please select a sub-issue');
  return;
}

// 4. Conditional rendering in JSX
{showSubIssue && (
  <Select
    label="Sub-Issue"
    name="subIssue"
    value={formData.subIssue}
    onChange={handleInputChange}
    required
  >
    <option value="">Choose an option</option>
    {SUB_ISSUES_MAP[formData.issueType]?.map(option => (
      <option key={option} value={option}>{option}</option>
    ))}
  </Select>
)}
```

**Pattern checklist**:
- Use `useState` to track visibility (boolean)
- Use `useEffect` with correct dependencies (parent field in dependency array)
- Clear child field value when hidden
- Add conditional validation that checks `showFieldName &&`
- Render field conditionally with `{showFieldName && (<Field />)}`

---

## 4. Form-to-Database Sync: The Full Chain

When adding a form field, ALL FOUR layers must update for the data to flow end-to-end.

### 4.1 The Four Layers

**Layer 1: TypeScript Interface** (Frontend type checking)
```typescript
export interface LoanIssueFormData {
  entity: string;           // Field name matches form state
  issueType: string;
  newField: string;         // NEW FIELD
  attachmentFiles?: File[];
}
```

**Layer 2: Form Component State** (Frontend rendering)
```javascript
const [formData, setFormData] = useState<LoanIssueFormData>({
  entity: '',
  issueType: '',
  newField: '',             // NEW FIELD: must match interface
  attachmentFiles: [],
});

// In JSX:
<Input
  label="New Field"
  name="newField"           // MUST match state key
  value={formData.newField}
  onChange={handleInputChange}
/>
```

**Layer 3: API Call** (Frontend to backend)
```javascript
const handleSubmit = async () => {
  const submissionData = {
    entity: formData.entity,
    issueType: formData.issueType,
    newField: formData.newField,  // NEW FIELD: must be included
    // ... other fields ...
  };

  const submissionId = await createLoanIssueSubmission(submissionData, role, decisionResult);
};

// In lib/submissions.ts:
export async function createLoanIssueSubmission(
  data: LoanIssueFormData,
  // ...
): Promise<string> {
  const submissionData: Record<string, any> = {
    id: submissionId,
    entity: data.entity,
    issueType: data.issueType,
    newField: data.newField,    // NEW FIELD: extract from data
    // ...
  };

  const docRef = doc(db, SUBMISSIONS_COLLECTION, submissionId);
  await setDoc(docRef, submissionData);

  return submissionId;
}
```

**Layer 4: Database Schema** (Backend storage)
```typescript
export interface Submission {
  id: string;
  entity?: string;
  issueType?: string;
  newField?: string;        // NEW FIELD: optional because of backward compatibility
  // ... other fields ...
}
```

### 4.2 The Checklist

When adding a form field, verify:

```
[ ] 1. TypeScript interface includes field
      Location: src/types/index.ts
      Check: interface LoanIssueFormData { newField: string }

[ ] 2. Form state initializes field
      Location: src/pages/LoanIssueFormPage.tsx
      Check: const [formData, setFormData] = useState<LoanIssueFormData>({ ..., newField: '' })

[ ] 3. Form JSX renders field with onChange handler
      Location: src/pages/LoanIssueFormPage.tsx
      Check: <Input name="newField" value={formData.newField} onChange={handleInputChange} />

[ ] 4. Submit handler includes field in submission
      Location: src/pages/LoanIssueFormPage.tsx, handleSubmit()
      Check: await createLoanIssueSubmission(formData, ...)

[ ] 5. API function extracts field from FormData
      Location: src/lib/submissions.ts, createLoanIssueSubmission()
      Check: newField: data.newField,

[ ] 6. Database interface includes field
      Location: src/types/index.ts
      Check: interface Submission { newField?: string }

[ ] 7. Validation added to form submit
      Location: src/pages/LoanIssueFormPage.tsx, handleSubmit()
      Check: if (!formData.newField.trim()) { toast.error(...); return; }
```

### 4.3 Real Example: Adding "Supervisor Approval" to LoanIssueFormPage

**Step 1: Update TypeScript**
```typescript
// src/types/index.ts
export interface LoanIssueFormData {
  entity: string;
  issueType: string;
  subIssue?: string;
  actionRequested: string;
  opportunityId: string;
  lsqUrl: string;
  date: string;
  name: string;
  notes?: string;
  supervisorApproval?: string;   // NEW: Add field
  attachmentFiles?: File[];
}

export interface Submission {
  id: string;
  // ... existing fields ...
  supervisorApproval?: string;   // NEW: Add field
}
```

**Step 2: Update Form State**
```javascript
// src/pages/LoanIssueFormPage.tsx
const [formData, setFormData] = useState<LoanIssueFormData>({
  entity: '',
  issueType: '',
  subIssue: '',
  actionRequested: '',
  opportunityId: '',
  lsqUrl: '',
  date: new Date().toISOString().split('T')[0],
  name: '',
  notes: '',
  supervisorApproval: '',        // NEW: Initialize
  attachmentFiles: [],
});
```

**Step 3: Update Form JSX**
```javascript
// In handleSubmit JSX form section
<Select
  label="Supervisor Approval"
  name="supervisorApproval"
  value={formData.supervisorApproval}
  onChange={handleInputChange}
  required
>
  <option value="">Choose an option</option>
  <option value="approved">Approved</option>
  <option value="pending">Pending</option>
  <option value="rejected">Rejected</option>
</Select>
```

**Step 4: Update Validation**
```javascript
// In handleSubmit()
if (!formData.supervisorApproval) {
  toast.error('Please select supervisor approval status');
  return;
}
```

**Step 5: Update API Call**
```javascript
// In lib/submissions.ts, createLoanIssueSubmission()
const submissionData: Record<string, any> = {
  id: submissionId,
  entity: data.entity,
  issueType: data.issueType,
  subIssue: data.subIssue,
  actionRequested: data.actionRequested,
  opportunityId: data.opportunityId,
  lsqUrl: data.lsqUrl,
  urn: data.opportunityId,
  name: data.name,
  date: data.date,
  supervisorApproval: data.supervisorApproval,  // NEW: Extract field
  // ... rest of fields ...
};
```

Now the field flows: FormData → JSX → Submit → API → Database → TypeScript type-checking.

---

## 5. Error Handling Preservation

### 5.1 The Cardinal Rule: Never Mix Error Display Patterns

Each application uses ONE primary error display pattern. Never mix within the same codebase.

**Ring Kissht Issue Tracker**: Toast notifications (react-hot-toast)
```javascript
// CORRECT: All errors as toast
if (!formData.actionable) { toast.error('Please select an actionable'); return; }
if (!formData.detailedActionable.trim()) { toast.error('Please provide detailed actionable'); return; }

// WRONG: Mixing toast with inline errors
const [errors, setErrors] = useState({});
if (!formData.actionable) {
  toast.error('Required');
  setErrors(prev => ({ ...prev, actionable: 'Required' })); // Don't do this
}
```

**LOS Issue Tracker**: Field state + inline errors
```javascript
// CORRECT: All errors tracked in errors state
const [errors, setErrors] = useState<Record<string, string>>({});
if (!lsqUrl.trim()) {
  newErrors.lsqUrl = 'LSQ URL is required';
}
// Display in JSX:
<Input
  label="LSQ URL"
  value={lsqUrl}
  error={errors.lsqUrl}  // Inline display
/>

// WRONG: Adding toast on top
toast.error(errors.lsqUrl); // Don't mix
```

### 5.2 State Machine: The Complete Error/Loading/Success Pattern

All forms follow this state machine:

```
IDLE
  ↓ (user submits)
VALIDATING
  ↓ (validation fails)
  └→ IDLE (show errors)
  ↓ (validation passes)
UPLOADING (if files present)
  ↓
SUBMITTING
  ↓ (success)
SUCCESS
  ↓ (after delay or user action)
IDLE (reset form)

OR

SUBMITTING
  ↓ (error)
ERROR
  ↓
IDLE (keep form data, show error)
```

**SubmitPage implementation**:
```javascript
const [isSubmitting, setIsSubmitting] = useState(false);
const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);
const [success, setSuccess] = useState<{ submissionId: string } | null>(null);

// State transitions
const handleSubmit = async (e: React.FormEvent) => {
  // VALIDATING (check form)
  if (!formData.actionable) { toast.error(...); return; } // Stay in IDLE

  // UPLOADING (if files)
  setIsSubmitting(true);  // Enter SUBMITTING
  setUploadProgress(null);

  try {
    // SUBMITTING (API call)
    const submissionId = await createSubmission(formData, role, (progress) => setUploadProgress(progress));

    // SUCCESS
    setSuccess({ submissionId });
    toast.success(`Submission ${submissionId} created successfully!`);
  } catch (error) {
    // ERROR
    toast.error(error instanceof Error ? error.message : 'Failed to create submission');
    // Form data remains for retry
  } finally {
    // Return to IDLE (in success callback)
    setIsSubmitting(false);
    setUploadProgress(null);
  }
};

// SUCCESS state UI
if (success) {
  return (
    <div className="max-w-md mx-auto">
      <div className="card p-8 text-center">
        <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-green-600" ...>
            <path ... />
          </svg>
        </div>

        <h2 className="text-xl font-bold text-gray-900 mb-2">Submission Successful</h2>
        <p className="text-sm text-gray-500 mb-6">Your submission has been logged with ID:</p>

        <div className="py-3 px-4 rounded-lg bg-ring-50 border border-ring-200 mb-6">
          <p className="text-2xl font-mono font-bold text-ring-700">{success.submissionId}</p>
        </div>

        <Button onClick={handleSubmitAnother} variant="primary" className="w-full">
          Submit Another
        </Button>
      </div>
    </div>
  );
}

// IDLE/VALIDATING state UI (normal form)
return (
  <div className="max-w-xl mx-auto">
    {/* ... form ... */}
  </div>
);
```

**TicketForm implementation** (different state machine, same principle):
```javascript
const [loading, setLoading] = useState(false);
const [errors, setErrors] = useState<Record<string, string>>({});
const [success, setSuccess] = useState(false);
const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number } | null>(null);

const handleSubmit = async (e: React.FormEvent) => {
  // VALIDATING
  if (!validate()) return;

  submittingRef.current = true;
  setLoading(true);  // Enter SUBMITTING
  let uploadedImageUrls: string[] = [];

  try {
    // UPLOADING
    setUploadProgress({ current: 0, total: images.length });
    uploadedImageUrls = await uploadImages(images.map((img) => img.file), ticketContext, ...);

    // SUBMITTING
    await onSubmit({ ... });

    // SUCCESS
    setSuccess(true);
    setTimeout(() => setSuccess(false), 3000); // Auto-dismiss
    // Reset form
  } catch (err) {
    // ERROR
    setErrors({ description: 'Failed to create ticket. Please try again.' });
    // Don't reset form data
  } finally {
    submittingRef.current = false;
    setLoading(false);
    setUploadProgress(null);
  }
};

// LOADING state UI
if (loading) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-medium text-ring-700">Uploading...</span>
        <span className="text-xs text-ring-600">{uploadProgress?.percentage}%</span>
      </div>
      <div className="w-full bg-ring-200 rounded-full h-1.5">
        <div className="bg-ring-600 h-1.5 rounded-full transition-all" style={{ width: `${uploadProgress?.percentage}%` }} />
      </div>
    </div>
  );
}

// SUCCESS state UI (inline, auto-dismiss)
{success && (
  <motion.div className="p-3 bg-success-50/20 border border-success-200 text-success-700 rounded-lg text-sm flex items-center gap-2">
    <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
    Ticket submitted successfully!
  </motion.div>
)}
```

---

## 6. Real Comparison: SubmitPage vs LoanIssueFormPage Side-by-Side

### 6.1 What's IDENTICAL (Copy These)

| Component | Code | Location |
|-----------|------|----------|
| **State initialization** | `const [attachmentFiles, setAttachmentFiles] = useState<File[]>([])` | Both, lines 22-33 |
| **File processing** | `processFiles()` function | Both, identical logic |
| **File removal** | `removeAttachment()` function | Both, identical logic |
| **Preview rendering** | Map<fileId, URL> + img/video detection | Both, identical JSX |
| **Paste handler** | Ctrl+V clipboard listener + screenshot creation | Both, same pattern |
| **Upload progress** | `UploadProgress` type + progress bar | Both, identical |
| **File size validation** | `validateTotalFileSize()` utility call | Both, same 200 MB limit |
| **Error display** | `toast.error()` for all validation | Both |
| **Submit pattern** | `setIsSubmitting(true)` → call API → `setSuccess()` | Both, identical flow |
| **Success state** | Show card with ID + "Submit Another" button | Both, similar structure |

### 6.2 What's DIFFERENT (Modify These)

| Aspect | SubmitPage | LoanIssueFormPage | Why? |
|--------|-----------|-------------------|------|
| **Form fields** | 6 fields | 9 fields | Different use cases |
| **Conditional fields** | None | subIssue, notes | Loan issues need more logic |
| **Field dependencies** | None | issueType → subIssue | Domain-specific rules |
| **Date field** | Not present | Auto-set, disabled | Loan issues track submission date |
| **Format validation** | URL validation only | IDEP format validation | Loan issues have specific ID format |
| **Paste behavior** | Simple add | Add/Replace dialog | UX choice difference |
| **Success payload** | `{ submissionId }` | `{ submissionId, decisionResult }` | Loan issues show analysis |
| **Decision tree** | None | 20-branch logic | Loan issues auto-recommend actions |
| **Success JSX** | Simple card | Card + decision tree section | Different display |

### 6.3 Correct "Copy and Modify" Approach

If you need to create a third form (e.g., "PropertyIssuePage"):

1. **Check**: Is it more similar to SubmitPage or LoanIssueFormPage?
   - PropertyIssue = general issue → closer to SubmitPage

2. **Copy**: `cp src/pages/SubmitPage.tsx src/pages/PropertyIssuePage.tsx`

3. **Modify only**:
   ```javascript
   // Change 1: Field type
   interface PropertyIssueFormData {
     propertyType: string;      // NEW
     address: string;           // NEW
     detailedDescription: string;  // SAME AS detailedActionable
     attachmentFiles?: File[];  // IDENTICAL
   }

   // Change 2: State (only field names/values)
   const [formData, setFormData] = useState<PropertyIssueFormData>({
     propertyType: '',
     address: '',
     detailedDescription: '',
     attachmentFiles: [],
   });

   // Change 3: Validation (property-specific)
   if (!formData.propertyType) { toast.error('Please select property type'); return; }
   if (!formData.address.trim()) { toast.error('Please provide address'); return; }

   // Change 4: JSX fields (but keep attachment block identical)
   // Change 5: API call function name
   const submissionId = await createPropertyIssue(formData, role, ...);

   // KEEP IDENTICAL: processFiles, removeAttachment, paste handler, file upload JSX, submit pattern, success state
   ```

4. **DO NOT**:
   - Rewrite file upload logic
   - Change error display pattern
   - Modify success state structure
   - Create new validation paradigm
   - Reimplement attachment state management

---

## 7. Summary: The Defensive Framing for Claude

When Workflow Guardian encounters a form addition request, it should:

### Instruction 1: Catalog First
"Before creating any form, show me the existing forms in this project. I need to understand the patterns before adding a new one."

### Instruction 2: Match, Don't Create
"I will copy the closest existing form and modify only the specific fields. I will NOT create a form from scratch."

### Instruction 3: Update the Four Layers
"When I add any form field, I will update: TypeScript interface → Form state → JSX → API call."

### Instruction 4: Preserve Error Patterns
"I will check how this codebase displays errors (toast vs inline). I will use the SAME pattern for my new form."

### Instruction 5: Copy Critical Sections
"File upload, attachment handling, paste support, and success states are identical to existing forms. I copy these verbatim without modification."

### Instruction 6: Document Divergences
"If I see forms with similar functionality but different implementations, I note this as a maintenance issue and flag it for refactoring."

---

## 8. Appendix: Real Code Snippets from Both Projects

### SubmitPage Success Flow (390 lines)
**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/pages/SubmitPage.tsx:192-215`

```javascript
if (success) {
  return (
    <div className="max-w-md mx-auto">
      <div className="card p-8 text-center">
        <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h2 className="text-xl font-bold text-gray-900 mb-2">Submission Successful</h2>
        <p className="text-sm text-gray-500 mb-6">Your submission has been logged with ID:</p>

        <div className="py-3 px-4 rounded-lg bg-ring-50 border border-ring-200 mb-6">
          <p className="text-2xl font-mono font-bold text-ring-700">{success.submissionId}</p>
        </div>

        <Button onClick={handleSubmitAnother} variant="primary" className="w-full">
          Submit Another
        </Button>
      </div>
    </div>
  );
}
```

### LoanIssueFormPage Conditional Rendering (603 lines)
**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/pages/LoanIssueFormPage.tsx:146-154`

```javascript
useEffect(() => {
  const issueType = formData.issueType;
  if (issueType && SUB_ISSUES_MAP[issueType] && SUB_ISSUES_MAP[issueType].length > 0) {
    setShowSubIssue(true);
  } else {
    setShowSubIssue(false);
    setFormData(prev => ({ ...prev, subIssue: '' }));
  }
}, [formData.issueType]);
```

### TicketForm Image Upload (702 lines)
**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/TicketForm.tsx:125-167`

```javascript
const addImageFiles = useCallback(
  (files: File[]) => {
    const remainingSlots = MAX_IMAGES - images.length;
    if (remainingSlots <= 0) {
      setErrors((prev) => ({
        ...prev,
        images: `Maximum ${MAX_IMAGES} images allowed`,
      }));
      return;
    }

    const filesToAdd = files.slice(0, remainingSlots);
    const newImages: ImageFile[] = [];

    for (const file of filesToAdd) {
      const validationError = validateImageFile(file);
      if (validationError) {
        setErrors((prev) => ({ ...prev, images: validationError }));
        continue;
      }

      newImages.push({
        id: generateUniqueId(),
        file,
        preview: createPreviewUrl(file),
      });
    }

    if (newImages.length > 0) {
      setImages((prev) => [...prev, ...newImages]);
      setErrors((prev) => {
        const { images: _, ...rest } = prev;
        return rest;
      });
      setFieldStates((prev) => ({
        ...prev,
        images: { touched: true, valid: true },
      }));
    }
  },
  [images.length]
);
```

---

**This document ensures that form logic is preserved across all projects by teaching pattern recognition and copy-modify workflows rather than from-scratch creation.**
