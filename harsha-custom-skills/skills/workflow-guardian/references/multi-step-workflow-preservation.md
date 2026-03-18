# Multi-Step Workflow Preservation Reference

**Purpose**: Comprehensive guide for safely modifying multi-step workflows (wizards, steppers, approval chains) without breaking existing step sequences.

**Status**: Critical safety reference - ZERO coverage currently in workflow-guardian
**Last Updated**: February 2026
**Scope**: React/Vue/vanilla workflows, form wizards, approval chains, state machines

---

## Table of Contents

1. [Workflow Pattern Overview](#workflow-pattern-overview)
2. [Multi-Step Form Patterns](#multi-step-form-patterns)
3. [Workflow State Machine Patterns](#workflow-state-machine-patterns)
4. [Approval/Review Chain Patterns](#approvalreview-chain-patterns)
5. [Data Flow in Multi-Step Processes](#data-flow-in-multi-step-processes)
6. [Progress Tracking Patterns](#progress-tracking-patterns)
7. [Common Multi-Step Breakages](#common-multi-step-breakages)
8. [Safe Modification Strategies](#safe-modification-strategies)
9. [Code Examples & Patterns](#code-examples--patterns)
10. [Testing Multi-Step Workflows](#testing-multi-step-workflows)

---

## Workflow Pattern Overview

### Why Multi-Step Workflows Are Fragile

Multi-step workflows are the most fragile patterns in web applications because:

1. **Step Interdependencies**: Each step depends on the state, data, and validation from previous steps
2. **Implicit Contracts**: UI components often have implicit assumptions about step ordering
3. **Distributed State**: Form data, validation status, and progress tracking exist across multiple components
4. **Hidden Assumptions**: Navigation logic may assume a specific step sequence without explicit guards
5. **Cascading Failures**: Modifying one step's data shape can break validation/display in downstream steps

### Key Terminology

- **Step**: Individual page/section in a multi-step workflow
- **Wizard**: Multi-step form with linear progression
- **Stepper**: Visual component showing step progress
- **State Machine**: Explicit definition of valid states and transitions
- **Guard Condition**: Logic preventing invalid state transitions
- **Partial Save**: Persisting form data at each step without full submission
- **Workflow Engine**: External system managing state transitions
- **Event-Driven**: State changes triggered by external events (not automatic progression)

---

## Multi-Step Form Patterns

### 1. Stepper Component Architecture

Modern stepper components follow a composition pattern with these core elements:

```
Stepper (Container)
├── StepperHeader
│   └── Step (1..N) with indicators, labels, connectors
├── StepperContent
│   └── StepPanel (active step content)
└── StepperFooter (navigation buttons)
```

**Material UI Pattern** (2025 current):
- Horizontal/vertical orientation support
- Linear vs. non-linear modes
- Step completion state tracking
- Active/completed/disabled step states

**Key Pattern Rules**:
- Step index must be immutable (never reorder steps at runtime)
- Step labels/titles can change, but internal step identifiers must remain stable
- Stepper state: `{ activeStep: number, completedSteps: Set<number> }`
- Visual connector between steps: should update count if steps change

**DANGER ZONE**: Changing step count affects:
- Progress bar calculations: `progress = currentStep / totalSteps * 100`
- Step connector width/spacing
- Disabled state logic for non-linear steppers
- Completion percentages in progress tracking

### 2. Form Data Persistence Across Steps

#### Pattern A: Context + Local Storage

```typescript
// SAFE PATTERN: Immutable step data structure
interface StepData {
  step1: { name: string; email: string };
  step2: { phone: string; address: string };
  step3: { preferences: string[]; accepted: boolean };
}

// Store keys are step-indexed: never change existing keys
const STORAGE_KEYS = {
  step1: 'form_step_1_v1',  // v1 versioning allows migrations
  step2: 'form_step_2_v1',
  step3: 'form_step_3_v1'
};

const useWorkflowStore = (initialData) => {
  const [formData, setFormData] = useState(initialData);

  // Save to localStorage at each step
  const saveStep = (stepNumber, data) => {
    const updatedData = { ...formData, [`step${stepNumber}`]: data };
    setFormData(updatedData);

    // Key insight: persist individual step data
    localStorage.setItem(
      STORAGE_KEYS[`step${stepNumber}`],
      JSON.stringify(data)
    );
  };

  // Load persisted data on mount
  useEffect(() => {
    const keys = Object.values(STORAGE_KEYS);
    const loadedData = {};

    keys.forEach((key, idx) => {
      const step = idx + 1;
      const saved = localStorage.getItem(key);
      if (saved) loadedData[`step${step}`] = JSON.parse(saved);
    });

    if (Object.keys(loadedData).length > 0) {
      setFormData(prev => ({ ...prev, ...loadedData }));
    }
  }, []);

  return { formData, saveStep };
};
```

**DANGER**: If you add a new step in the middle:
- Don't insert: `steps[1] = newStep` (breaks ordering)
- Instead: add new step at END, then create migration
- Old data has `[step1, step2, step3]` but new code expects `[step1, newStep, step2, step3]`

#### Pattern B: Zustand with Persist Middleware

```typescript
import create from 'zustand';
import { persist } from 'zustand/middleware';

// SAFE: Explicit step schema
const useFormStore = create(
  persist(
    (set) => ({
      currentStep: 1,
      formData: {
        step1: { name: '', email: '' },
        step2: { phone: '', address: '' },
        step3: { preferences: [], accepted: false }
      },

      // Key pattern: mutations are explicit per-step
      updateStep1: (data) => set(
        state => ({
          formData: {
            ...state.formData,
            step1: { ...state.formData.step1, ...data }
          }
        }),
        false,
        'updateStep1'
      ),

      goToStep: (step) => set({ currentStep: step }),

      resetForm: () => set({
        currentStep: 1,
        formData: {
          step1: { name: '', email: '' },
          step2: { phone: '', address: '' },
          step3: { preferences: [], accepted: false }
        }
      })
    }),
    {
      name: 'workflow-form',
      // CRITICAL: whitelist persisted fields
      partialize: (state) => ({
        formData: state.formData,
        currentStep: state.currentStep
      })
    }
  )
);
```

**Safe Modification**: To add step 4, append to formData structure:
```typescript
formData: {
  step1: { ... },
  step2: { ... },
  step3: { ... },
  step4: { ... }  // NEW: append at end, don't insert
}
```

#### Pattern C: React Hook Form with Multi-Step

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

// SAFE: Separate validation per step
const step1Schema = z.object({
  name: z.string().min(2),
  email: z.string().email()
});

const step2Schema = z.object({
  phone: z.string().regex(/^\d{10}$/),
  address: z.string().min(5)
});

const step3Schema = z.object({
  preferences: z.array(z.string()).min(1),
  accepted: z.boolean().refine(v => v === true)
});

// Combine schemas for final validation
const fullSchema = step1Schema.merge(step2Schema).merge(step3Schema);

const useMultiStepForm = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [validatedSteps, setValidatedSteps] = useState(new Set());

  const form = useForm({
    resolver: zodResolver(fullSchema),
    mode: 'onChange',
    defaultValues: {
      name: '',
      email: '',
      phone: '',
      address: '',
      preferences: [],
      accepted: false
    }
  });

  // DANGER: Common mistake
  // const goToStep = (step) => setCurrentStep(step);
  // This allows skipping validation!

  // SAFE: Validate current step before advancing
  const goToNextStep = async () => {
    const currentStepSchema = [step1Schema, step2Schema, step3Schema][currentStep - 1];

    try {
      const currentStepData = getCurrentStepData();
      await currentStepSchema.parseAsync(currentStepData);

      setValidatedSteps(prev => new Set([...prev, currentStep]));
      setCurrentStep(prev => Math.min(prev + 1, 3));
    } catch (error) {
      // Show validation error
      console.error('Step validation failed', error);
    }
  };

  return { form, currentStep, goToNextStep, validatedSteps };
};
```

---

## Workflow State Machine Patterns

### 1. Explicit State Machine Structure (XState Pattern)

XState provides a robust pattern for defining valid state transitions explicitly:

```typescript
import { createMachine, interpret } from 'xstate';

// SAFE: Explicit machine definition
const workflowMachine = createMachine({
  id: 'approvalWorkflow',
  initial: 'draft',
  states: {
    draft: {
      on: {
        SUBMIT: 'pending_review'
        // IMPLICIT: Only transition explicitly defined
      }
    },
    pending_review: {
      on: {
        APPROVE: 'approved',
        REJECT: 'draft',
        REQUEST_CHANGES: 'changes_requested'
      }
    },
    changes_requested: {
      on: {
        RESUBMIT: 'pending_review',
        CANCEL: 'draft'
      }
    },
    approved: {
      on: {
        COMPLETE: 'completed'
      }
    },
    completed: {
      // Terminal state: no transitions
      type: 'final'
    },
    rejected: {
      type: 'final'
    }
  }
});

const service = interpret(workflowMachine);
service.start();

// Safe: Can only transition via defined events
service.send('SUBMIT');      // OK: draft -> pending_review
service.send('WRONG_EVENT'); // Ignored: not defined for current state
service.send('APPROVE');     // Error: not allowed in draft state
```

**Key Safety Principles**:
1. States are explicit and immutable
2. Transitions are event-driven (not automatic)
3. Invalid transitions are rejected (no silent failures)
4. Guards can prevent transitions based on conditions
5. History of transitions is traceable

### 2. Adding a New Step to State Machine (DANGEROUS)

**WRONG WAY** (breaks existing workflows):
```typescript
// BAD: Modifying middle of state chain
const newMachine = {
  ...oldMachine,
  states: {
    ...oldMachine.states,
    draft: { ...oldMachine.draft },
    // NEW STEP INSERTED: breaks workflows that expect draft -> pending_review
    new_step: {
      on: { NEXT: 'pending_review' }
    },
    pending_review: { ... }
  }
};
```

**CORRECT WAY** (append and provide migration):
```typescript
const workflowMachineV2 = createMachine({
  id: 'approvalWorkflow',
  initial: 'draft',
  states: {
    draft: {
      on: {
        SUBMIT: 'pending_review',
        SUBMIT_V2: 'initial_validation' // Support BOTH paths during migration
      }
    },
    // NEW STEP: Append at appropriate location
    initial_validation: {
      on: {
        VALIDATION_PASSED: 'pending_review',
        VALIDATION_FAILED: 'draft'
      }
    },
    pending_review: { ... },
    approved: { ... },
    completed: { ... }
  }
});

// Migration logic: Route old workflows
const routeState = (oldState) => {
  if (oldState === 'pending_review') {
    // Old workflows go directly to pending_review
    return 'pending_review';
  }
  // New workflows go through validation
  return 'initial_validation';
};
```

### 3. Common State Machine Breakages

**Breakage 1: Removing Terminal State Guard**
```typescript
// BEFORE: completed is terminal (cannot re-approve)
states: {
  completed: { type: 'final' }
}

// AFTER: Removed 'type: final' - now CAN re-approve!
states: {
  completed: {
    on: { REOPEN: 'pending_review' } // BREAKS: old code assumes final
  }
}
```

**Breakage 2: Conditional Transitions Without Guards**
```typescript
// BEFORE: Simple direct transition
pending_review: {
  on: { APPROVE: 'approved' }
}

// AFTER: Added conditional logic, but forgot old code
pending_review: {
  on: {
    APPROVE: {
      target: 'approved',
      cond: (ctx) => ctx.hasPermission === true // NEW CONDITION!
    }
  }
}
// BREAKS: Workflows that APPROVE without permission now silently fail
```

**SAFE ALTERNATIVE**:
```typescript
pending_review: {
  on: {
    APPROVE: {
      target: 'approved',
      cond: (ctx) => ctx.hasPermission === true
    },
    APPROVE_LEGACY: 'approved' // Support old code path
  }
}
```

**Breakage 3: Context Mutation During Transition**
```typescript
// BEFORE: Clean context update
submit: (ctx, event) => ({ ...ctx, submittedData: event.data })

// AFTER: Changed context shape
submit: (ctx, event) => ({
  ...ctx,
  submittedData: event.data,
  metadata: { timestamp: Date.now() } // NEW FIELD
})
// BREAKS: Code expecting ctx.submittedData.field still works, but other code fails
```

---

## Approval/Review Chain Patterns

### 1. Multi-Role Approval Chain

```typescript
// SAFE: Immutable approval step sequence
interface ApprovalChain {
  steps: ApprovalStep[];
  currentStepIndex: number;
  status: 'pending' | 'approved' | 'rejected';
}

interface ApprovalStep {
  id: string;
  role: 'manager' | 'director' | 'admin';
  status: 'pending' | 'approved' | 'rejected' | 'skipped';
  approver?: string;
  approvedAt?: Date;
  comment?: string;
}

// CRITICAL: Never reorder steps, never remove steps from middle
const APPROVAL_CHAIN_V1 = [
  { id: 'step_1', role: 'manager' },
  { id: 'step_2', role: 'director' },
  { id: 'step_3', role: 'admin' }
];

// SAFE: Add new step at END with migration
const APPROVAL_CHAIN_V2 = [
  { id: 'step_1', role: 'manager' },
  { id: 'step_2', role: 'director' },
  { id: 'step_3', role: 'admin' },
  { id: 'step_4', role: 'compliance' } // NEW
];

// Migration: Old workflows skip new step
const getApprovalChain = (createdAt: Date) => {
  if (createdAt < new Date('2026-02-01')) {
    return APPROVAL_CHAIN_V1; // Old workflows use old chain
  }
  return APPROVAL_CHAIN_V2; // New workflows use new chain
};
```

**DANGER ZONE**: Permission checks at each step
```typescript
// WRONG: Checking permission inside approval
const approve = async (stepId, userId) => {
  const step = chain.steps.find(s => s.id === stepId);

  // BREAKS: If this check fails, user thinks step is done!
  const hasPermission = await checkPermission(userId, step.role);
  if (!hasPermission) throw new Error('No permission');

  markStepApproved(stepId);
};

// SAFE: Check permission BEFORE presenting approval
const canApproveStep = async (stepId, userId) => {
  const step = chain.steps.find(s => s.id === stepId);
  const hasPermission = await checkPermission(userId, step.role);
  return hasPermission && step.status === 'pending';
};

// Only show approve button if canApproveStep is true
const ApprovalButton = ({ stepId, userId }) => {
  const [canApprove, setCanApprove] = useState(false);

  useEffect(() => {
    canApproveStep(stepId, userId).then(setCanApprove);
  }, [stepId, userId]);

  if (!canApprove) return null; // Don't show button at all

  return <button onClick={() => approve(stepId, userId)}>Approve</button>;
};
```

### 2. Notification Triggers at Each Step

```typescript
// SAFE: Explicit notification mapping
const APPROVAL_NOTIFICATIONS = {
  step_1_approved: {
    recipient: 'director',
    template: 'manager_approved',
    delay: 0 // immediate
  },
  step_2_approved: {
    recipient: 'admin',
    template: 'director_approved',
    delay: 0
  },
  step_3_approved: {
    recipient: 'requester',
    template: 'admin_approved',
    delay: 3600000 // 1 hour later
  }
};

// DANGER: Changing notification recipient
const approveStep = async (stepId) => {
  const step = findStep(stepId);
  markApproved(step);

  // BREAKS: If notification config changes, old workflows don't get notification
  const notificationConfig = APPROVAL_NOTIFICATIONS[`${stepId}_approved`];
  if (!notificationConfig) {
    console.error(`Missing notification config for ${stepId}`);
    return;
  }

  await sendNotification(notificationConfig);
};

// SAFE: Add new notification without removing old
const APPROVAL_NOTIFICATIONS_V2 = {
  step_1_approved: {
    // EXISTING: keep unchanged
    recipient: 'director',
    template: 'manager_approved',
    delay: 0
  },
  step_2_approved: {
    // EXISTING: keep unchanged
    recipient: 'admin',
    template: 'director_approved',
    delay: 0
  },
  step_2_approved_slack: {
    // NEW: don't remove old, add new
    recipient: 'admin_slack_channel',
    template: 'director_approved_slack',
    delay: 0
  },
  step_3_approved: {
    recipient: 'requester',
    template: 'admin_approved',
    delay: 3600000
  }
};
```

### 3. Conditional Step Skipping

```typescript
// SAFE: Explicit skip logic
interface ApprovalStep {
  id: string;
  role: 'manager' | 'director' | 'admin';
  shouldSkip?: (ctx: ApprovalContext) => boolean;
  status: 'pending' | 'approved' | 'rejected' | 'skipped';
}

const APPROVAL_CHAIN = [
  {
    id: 'step_1',
    role: 'manager',
    shouldSkip: undefined // Always required
  },
  {
    id: 'step_2',
    role: 'director',
    shouldSkip: (ctx) => ctx.amount < 50000 // Skip for small amounts
  },
  {
    id: 'step_3',
    role: 'admin',
    shouldSkip: (ctx) => ctx.requestType !== 'access_grant' // Skip for other types
  }
];

const processApproval = async (chain, context) => {
  for (const step of chain.steps) {
    if (step.shouldSkip?.(context)) {
      markSkipped(step);
      notifySkipped(step); // CRITICAL: notify that step was skipped
      continue;
    }

    // Wait for actual approval
    await waitForApproval(step);
  }
};

// DANGER: Adding new skip condition
const APPROVAL_CHAIN_V2 = [
  {
    id: 'step_1',
    role: 'manager',
    shouldSkip: (ctx) => ctx.isAutoApproved === true // NEW CONDITION
  },
  // BREAKS: Existing workflows that expect step_1 to always run!
  { ... }
];
```

---

## Data Flow in Multi-Step Processes

### 1. How Data Flows Between Steps

```typescript
// SAFE PATTERN: Immutable data pipeline
interface WorkflowContext {
  // Step 1 outputs
  personalInfo: {
    firstName: string;
    lastName: string;
    email: string;
  };

  // Step 2 outputs - depends on Step 1
  contactInfo: {
    phone: string;
    address: string;
  };

  // Step 3 outputs - depends on Step 1 & 2
  preferences: {
    newsletter: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
  };

  // File uploaded in Step 2, referenced in Step 4
  documentUrl?: string;
}

// DANGER: Changing Step 1 output shape
// OLD:
// personalInfo: { firstName, lastName, email }

// NEW:
// personalInfo: { firstName, lastName, email, middleName } // Added field

// SAFE: Backward compatible addition
interface PersonalInfo {
  firstName: string;
  lastName: string;
  email: string;
  middleName?: string; // Optional: old data still works
}

// DANGER: Removing field from Step 1 output
// OLD:
interface PersonalInfo {
  firstName: string;
  lastName: string;
  email: string; // Used in Step 3
}

// NEW:
interface PersonalInfo {
  firstName: string;
  lastName: string;
  // Removed email - BREAKS Step 3
}

// SAFE: Mark deprecated, provide migration
interface PersonalInfo {
  firstName: string;
  lastName: string;
  email: string; // @deprecated in v2, use emailAddress
  emailAddress?: string; // @new
}

// Migration in Step 3
const getEmail = (info: PersonalInfo) => {
  return info.emailAddress || info.email || ''; // Fallback chain
};
```

### 2. Partial Save Patterns

```typescript
// SAFE: Save at each step, maintain history
interface SaveHistory {
  step: number;
  data: any;
  timestamp: Date;
  saved: boolean;
  error?: string;
}

const usePartialSave = () => {
  const [saveHistory, setSaveHistory] = useState<SaveHistory[]>([]);

  const saveStep = async (stepNumber, stepData) => {
    try {
      await api.saveStep(stepNumber, stepData);

      setSaveHistory(prev => [
        ...prev,
        {
          step: stepNumber,
          data: stepData,
          timestamp: new Date(),
          saved: true
        }
      ]);

      return true;
    } catch (error) {
      setSaveHistory(prev => [
        ...prev,
        {
          step: stepNumber,
          data: stepData,
          timestamp: new Date(),
          saved: false,
          error: error.message
        }
      ]);

      return false;
    }
  };

  // DANGER: Assume all steps saved successfully
  const canSubmit = () => {
    // WRONG:
    // return currentStep === 3;

    // SAFE: Verify all required steps were saved
    return saveHistory.filter(s => s.saved).length === totalSteps;
  };

  return { saveStep, canSubmit, saveHistory };
};
```

### 3. Validation Cascade (Step Dependencies)

```typescript
// SAFE: Explicit validation dependencies
interface ValidationDependency {
  step: number;
  dependsOn: number[];
  validator: (ctx: WorkflowContext) => boolean;
}

const VALIDATION_RULES = [
  {
    step: 1,
    dependsOn: [],
    validator: (ctx) => ctx.personalInfo?.email?.length > 0
  },
  {
    step: 2,
    dependsOn: [1],
    validator: (ctx) => {
      // Can only validate step 2 if step 1 is valid
      if (!VALIDATION_RULES[0].validator(ctx)) return false;
      return ctx.contactInfo?.phone?.length > 0;
    }
  },
  {
    step: 3,
    dependsOn: [1, 2],
    validator: (ctx) => {
      if (!VALIDATION_RULES[0].validator(ctx)) return false;
      if (!VALIDATION_RULES[1].validator(ctx)) return false;
      return ctx.preferences?.frequency !== undefined;
    }
  }
];

// DANGER: Adding validation without tracking dependencies
const canAccessStep = (stepNumber, context) => {
  // WRONG:
  // return stepNumber <= currentStep;

  // SAFE: Check dependency validation
  const rule = VALIDATION_RULES[stepNumber - 1];
  return rule.dependsOn.every(depStep => {
    const depRule = VALIDATION_RULES[depStep - 1];
    return depRule.validator(context);
  });
};

// DANGER: Changing validation condition mid-process
const VALIDATION_RULES_V2 = [
  {
    step: 1,
    dependsOn: [],
    // CHANGE: Now requires phone also
    validator: (ctx) =>
      ctx.personalInfo?.email?.length > 0 &&
      ctx.personalInfo?.phone?.length > 0 // NEW!
  },
  // BREAKS: Old workflows were allowed with just email
];
```

### 4. File Upload in Multi-Step Flows

```typescript
// SAFE: Upload at specific step, reference in later steps
interface WorkflowContext {
  step2UploadUrl?: string; // Uploaded in step 2
  step2FileName?: string;
}

const Step2Component = () => {
  const { updateContext } = useWorkflow();

  const handleUpload = async (file) => {
    try {
      // Upload to temporary location
      const uploadResponse = await api.uploadFile(file, {
        temporary: true,
        expiresIn: 3600 // 1 hour
      });

      updateContext({
        step2UploadUrl: uploadResponse.url,
        step2FileName: file.name
      });

      return true;
    } catch (error) {
      console.error('Upload failed:', error);
      return false;
    }
  };

  return <FileUploader onUpload={handleUpload} />;
};

const Step4Component = () => {
  const { context } = useWorkflow();

  // DANGER: Assume file still exists
  // WRONG:
  // const fileUrl = context.step2UploadUrl;

  // SAFE: Validate file still accessible
  const validateFileAccess = async () => {
    if (!context.step2UploadUrl) return false;

    try {
      const response = await fetch(context.step2UploadUrl, { method: 'HEAD' });
      return response.ok;
    } catch {
      return false;
    }
  };

  return (
    <>
      {context.step2FileName && (
        <VerifyUploadedFile
          fileName={context.step2FileName}
          validateAccess={validateFileAccess}
        />
      )}
    </>
  );
};
```

---

## Progress Tracking Patterns

### 1. Progress Bar Calculation

```typescript
// SAFE: Explicit progress calculation
const useProgressTracking = (totalSteps) => {
  const [completedSteps, setCompletedSteps] = useState(new Set());

  const progressPercentage = (completedSteps.size / totalSteps) * 100;

  // DANGER: Hardcoded step count
  // WRONG:
  // const progress = (currentStep / 3) * 100; // What if we add step 4?

  // SAFE: Dynamic step count
  const markStepComplete = (stepNumber) => {
    setCompletedSteps(prev => new Set([...prev, stepNumber]));
  };

  return {
    progressPercentage,
    markStepComplete,
    completedSteps
  };
};

// DANGER: Adding step in middle breaks progress math
// BEFORE: 3 steps: (1/3)*100 = 33%, (2/3)*100 = 66%, (3/3)*100 = 100%
// AFTER: 4 steps added in middle!
// Old workflows: (2/4)*100 = 50% (was 66%)
// New workflows expect different percentages at each step

// SAFE: Versioned progress calculation
const getProgressPercentage = (currentStep, createdAt) => {
  const chain = getApprovalChain(createdAt);
  return (currentStep / chain.length) * 100;
};
```

### 2. Step Completion Indicators

```typescript
// SAFE: Explicit completion status per step
interface StepStatus {
  stepId: string;
  completed: boolean;
  attempted: boolean;
  errors?: string[];
  lastUpdated: Date;
}

const StepIndicator = ({ step, status }) => {
  // DANGER: Only check visited
  // WRONG:
  // const className = currentStep > step ? 'completed' : 'pending';

  // SAFE: Check explicit completion marker
  const className = status.completed
    ? 'completed'
    : status.attempted
      ? 'attempted'
      : 'pending';

  return (
    <div className={className}>
      {status.completed && <CheckIcon />}
      {status.attempted && !status.completed && <AlertIcon />}
      {!status.attempted && <PendingIcon />}
    </div>
  );
};
```

### 3. Breadcrumb-Style Navigation

```typescript
// SAFE: Explicit step metadata for breadcrumbs
interface BreadcrumbStep {
  id: string;
  label: string;
  icon?: string;
  accessible: boolean; // Can user navigate to this step?
  completed: boolean;
}

const Breadcrumbs = ({ steps, currentStep, onNavigate }) => {
  return (
    <nav>
      {steps.map((step, idx) => (
        <button
          key={step.id}
          disabled={!step.accessible}
          className={currentStep === idx + 1 ? 'active' : ''}
          onClick={() => step.accessible && onNavigate(idx + 1)}
        >
          {step.label}
        </button>
      ))}
    </nav>
  );
};

// DANGER: Changing step labels
// BEFORE: 'Personal Info', 'Contact Details', 'Preferences'
// AFTER: 'Name & Email', 'Phone & Address', 'Settings' // NEW LABELS
// BREAKS: User tracking, analytics, user support docs reference old labels

// SAFE: Use step IDs internally, map to labels
const STEP_LABELS = {
  'v1': {
    'step_1': 'Personal Info',
    'step_2': 'Contact Details',
    'step_3': 'Preferences'
  },
  'v2': {
    'step_1': 'Name & Email',
    'step_2': 'Phone & Address',
    'step_3': 'Settings'
  }
};

const getStepLabel = (stepId, schemaVersion) => {
  return STEP_LABELS[schemaVersion]?.[stepId] || stepId;
};
```

---

## Common Multi-Step Breakages

### Breakage 1: Adding Step That Breaks Step Counter

```typescript
// BEFORE: 3-step wizard
const steps = ['step1', 'step2', 'step3'];

// AFTER: Inserted new step in middle
const steps = ['step1', 'newstep', 'step2', 'step3'];

// CODE THAT BREAKS:
const currentStepName = steps[currentStep - 1]; // Was steps[1] = 'step2', now = 'newstep'!

// Also breaks:
const isLastStep = currentStep === 3; // Now it's === 4!
const progressBar = (currentStep / 3) * 100; // Now / 4!
const stepperConnector width = 100 / 2; // Was 2 connectors, now 3!
```

### Breakage 2: Modifying Shared State Other Steps Depend On

```typescript
// BEFORE: Step 1 collects user type (individual/business)
const step1 = {
  userType: 'individual' | 'business'
};

// Step 3 depends on userType
const step3Validator = (ctx) => {
  if (ctx.step1.userType === 'business') {
    return ctx.step3.businessTaxId?.length > 0;
  }
  return ctx.step3.ssn?.length > 0;
};

// AFTER: Step 1 now collects additional info
const step1 = {
  userType: 'individual' | 'business' | 'nonprofit' // ADDED TYPE!
};

// BREAKS: Step 3 validator doesn't handle 'nonprofit' case!
// Workflows with nonprofit type reach step 3 but validator returns false
```

### Breakage 3: Breaking Validation Chain

```typescript
// BEFORE: Step 2 validates phone
const step2Validator = (phone) => /^\d{10}$/.test(phone);

// Step 3 uses phone without re-validating
const step3Processor = (ctx) => {
  const phone = ctx.step2.phone; // Assumed valid
  return dialPhone(phone); // Crashes if phone invalid!
};

// AFTER: Step 2 changed to optional phone
const step2Schema = z.object({
  phone: z.string().regex(/^\d{10}$/).optional() // NOW OPTIONAL!
});

// BREAKS: Step 3 assumes phone exists
const step3Processor = (ctx) => {
  const phone = ctx.step2.phone; // Could be undefined!
  return dialPhone(phone); // Crashes!
};

// SAFE FIX: Update downstream validators
const step3Processor = (ctx) => {
  if (!ctx.step2.phone) {
    return handlePhonelessFlow();
  }
  return dialPhone(ctx.step2.phone);
};
```

### Breakage 4: Changing Step Order Without Updating Navigation

```typescript
// BEFORE: step 1 -> step 2 -> step 3
const navigation = {
  1: { next: 2, prev: null },
  2: { next: 3, prev: 1 },
  3: { next: null, prev: 2 }
};

// AFTER: Reordered to step 1 -> step 3 -> step 2 (for some reason)
const navigation = {
  1: { next: 3, prev: null }, // CHANGED
  3: { next: 2, prev: 1 },     // CHANGED
  2: { next: null, prev: 3 }   // CHANGED
};

// BREAKS: Data flow assumes step 2 happens before step 3
// step 2 collects phone, step 3 uses phone for verification
// Now step 3 runs first with no phone!
```

### Breakage 5: Breaking Conditional Step Logic

```typescript
// BEFORE: Step 2 only shows if userType === 'business'
const shouldShowStep2 = (ctx) => ctx.step1.userType === 'business';

// AFTER: Changed condition without updating skip logic
const shouldShowStep2 = (ctx) =>
  ctx.step1.userType === 'business' && ctx.step1.approved === true; // NEW CONDITION

// BREAKS: Old workflows with userType='business' but approved=false
// They expect step 2 to show, but now it doesn't
```

### Breakage 6: Losing Form Data When Navigating

```typescript
// DANGER: Component remounts when step changes
const StepComponent = ({ step }) => {
  const [formData, setFormData] = useState({});

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // BREAKS: If parent re-mounts this component, formData is lost!
  return <form>{/* form fields */}</form>;
};

// SAFE: Persist state outside component
const useWorkflowForm = () => {
  const store = useFormStore(); // Zustand/Redux outside component

  const updateField = (field, value) => {
    store.updateField(field, value);
  };

  return { formData: store.formData, updateField };
};

const StepComponent = ({ step }) => {
  const { formData, updateField } = useWorkflowForm();

  // formData persists even if component remounts
  return <form>{/* form fields */}</form>;
};
```

---

## Safe Modification Strategies

### Strategy 1: Always Append, Never Insert

```typescript
// NEVER DO THIS:
const addNewStep = (steps) => {
  steps.splice(2, 0, newStep); // Inserts at position 2, shifts others
  return steps;
};

// ALWAYS DO THIS:
const addNewStep = (steps) => {
  return [...steps, newStep]; // Append at end
};

// Then handle routing:
const getStepSequence = (createdAt) => {
  if (createdAt < new Date('2026-02-01')) {
    return originalSteps; // Old workflows
  }
  return [...originalSteps, newStep]; // New workflows
};
```

### Strategy 2: Versioned Data Schemas

```typescript
// Version each data schema explicitly
interface PersonalInfoV1 {
  firstName: string;
  lastName: string;
  email: string;
}

interface PersonalInfoV2 extends PersonalInfoV1 {
  middleName?: string; // Added in v2
  preferredName?: string; // Added in v2
}

// Migration function
const migratePersonalInfo = (data: PersonalInfoV1): PersonalInfoV2 => {
  return {
    ...data,
    middleName: undefined,
    preferredName: data.firstName
  };
};

// Use version-aware code
const getPersonalInfo = (data: PersonalInfoV1 | PersonalInfoV2, version: number) => {
  if (version === 1) {
    return data as PersonalInfoV1;
  }
  return migratePersonalInfo(data as PersonalInfoV1) as PersonalInfoV2;
};
```

### Strategy 3: Feature Flags for Conditional Logic

```typescript
// SAFE: Toggle new behavior without breaking old
const useWorkflowFeatures = () => {
  const features = {
    validatePhoneOptional: isFeatureFlagEnabled('PHONE_OPTIONAL'),
    showComplianceStep: isFeatureFlagEnabled('COMPLIANCE_STEP'),
    newProgressCalculation: isFeatureFlagEnabled('NEW_PROGRESS_CALC')
  };

  return features;
};

const Step2Validator = (ctx) => {
  const features = useWorkflowFeatures();

  if (features.validatePhoneOptional) {
    // New validation: phone is optional
    return true; // Skip phone validation
  }

  // Old validation: phone is required
  return ctx.step2.phone?.length > 0;
};

// Rollout plan:
// 1. Feature flag off - old code path
// 2. Feature flag on (10% users) - test new code path
// 3. Feature flag on (50% users) - monitor metrics
// 4. Feature flag on (100% users) - full rollout
// 5. Remove old code path after stability period
```

### Strategy 4: Explicit Data Migration on Load

```typescript
// SAFE: Migrate old workflows to new schema
const loadWorkflow = async (workflowId) => {
  const workflow = await db.getWorkflow(workflowId);

  // Detect schema version
  const schemaVersion = detectSchema(workflow.data);

  // Apply migrations if needed
  if (schemaVersion === 1) {
    workflow.data = await migrationV1ToV2(workflow.data);
  }
  if (schemaVersion === 2) {
    workflow.data = await migrationV2ToV3(workflow.data);
  }

  return workflow;
};

// Explicit migration with logging
const migrationV1ToV2 = async (data: V1Schema): Promise<V2Schema> => {
  logger.info(`Migrating workflow to V2`, { schemaVersion: 1 });

  const migrated: V2Schema = {
    ...data,
    complianceApproved: false, // Default for new field
    migratedAt: new Date(),
    migratedFrom: 1
  };

  return migrated;
};
```

### Strategy 5: Backward Compatibility Shims

```typescript
// SAFE: Support both old and new code simultaneously
const getApprovalStatus = (workflow) => {
  // New field
  if (workflow.status !== undefined) {
    return workflow.status;
  }

  // Old field - provide shim
  if (workflow.approvalStep === 3) {
    return 'approved';
  }

  return 'pending';
};

const submitWorkflow = async (workflow) => {
  // Normalize to new schema before sending to API
  const normalizedWorkflow = {
    ...workflow,
    // New fields
    submittedAt: new Date(),
    submittedBy: getCurrentUser().id,
    // Keep old fields for backward compatibility
    data: workflow.data
  };

  // API accepts both old and new formats
  return await api.submitWorkflow(normalizedWorkflow);
};
```

---

## Code Examples & Patterns

### Complete Safe Multi-Step Form Example

```typescript
// 1. Define schema versions with explicit versioning
const formSchemaV1 = z.object({
  personalInfo: z.object({
    name: z.string().min(2),
    email: z.string().email()
  }),
  contactInfo: z.object({
    phone: z.string().regex(/^\d{10}$/)
  }),
  preferences: z.object({
    newsletter: z.boolean()
  })
});

// 2. Create state machine with explicit transitions
const formMachine = createMachine({
  id: 'multiStepForm',
  initial: 'step1',
  context: {
    data: {},
    validation: {}
  },
  states: {
    step1: {
      on: {
        NEXT: {
          target: 'step2',
          cond: (ctx) => formSchemaV1.shape.personalInfo.safeParse(ctx.data.personalInfo).success
        }
      }
    },
    step2: {
      on: {
        NEXT: {
          target: 'step3',
          cond: (ctx) => formSchemaV1.shape.contactInfo.safeParse(ctx.data.contactInfo).success
        },
        PREV: 'step1'
      }
    },
    step3: {
      on: {
        SUBMIT: {
          target: 'submitted',
          cond: (ctx) => formSchemaV1.safeParse(ctx.data).success
        },
        PREV: 'step2'
      }
    },
    submitted: {
      type: 'final'
    }
  }
});

// 3. Use Zustand for state persistence
const useFormStore = create(
  persist(
    (set) => ({
      currentStep: 'step1',
      data: {
        personalInfo: { name: '', email: '' },
        contactInfo: { phone: '' },
        preferences: { newsletter: false }
      },

      updateData: (path, value) =>
        set((state) => ({
          data: setIn(state.data, path, value)
        })),

      goToStep: (step) => set({ currentStep: step }),

      reset: () =>
        set({
          currentStep: 'step1',
          data: {
            personalInfo: { name: '', email: '' },
            contactInfo: { phone: '' },
            preferences: { newsletter: false }
          }
        })
    }),
    {
      name: 'form-store',
      partialize: (state) => ({
        data: state.data,
        currentStep: state.currentStep
      })
    }
  )
);

// 4. Implement safe navigation
const useFormNavigation = () => {
  const store = useFormStore();
  const [state, send] = useMachine(formMachine);

  const goToStep = async (step) => {
    // Don't skip validation
    const event = step === 'step2' ? 'NEXT' : step === 'step3' ? 'NEXT' : 'SUBMIT';
    send(event);

    if (state.value === step) {
      store.goToStep(step);
    }
  };

  return { goToStep, currentStep: state.value };
};
```

### Complete Approval Chain Example

```typescript
// 1. Define approval state machine
const approvalMachine = createMachine({
  id: 'approvalChain',
  initial: 'draft',
  context: {
    request: {},
    approvals: {}
  },
  states: {
    draft: {
      on: {
        SUBMIT: {
          target: 'manager_review',
          actions: assign({
            'approvals.submittedAt': () => new Date()
          })
        }
      }
    },
    manager_review: {
      on: {
        APPROVE: {
          target: 'director_review',
          actions: assign({
            'approvals.manager': (ctx, event) => ({
              approvedBy: event.approver,
              approvedAt: new Date(),
              status: 'approved'
            })
          })
        },
        REJECT: {
          target: 'draft',
          actions: assign({
            'approvals.manager': (ctx, event) => ({
              status: 'rejected',
              comment: event.comment
            })
          })
        }
      }
    },
    director_review: {
      on: {
        APPROVE: {
          target: 'admin_review',
          actions: assign({
            'approvals.director': (ctx, event) => ({
              approvedBy: event.approver,
              approvedAt: new Date(),
              status: 'approved'
            })
          })
        },
        REQUEST_CHANGES: {
          target: 'manager_review',
          actions: assign({
            'approvals.director': (ctx, event) => ({
              status: 'changes_requested',
              comment: event.comment
            })
          })
        }
      }
    },
    admin_review: {
      on: {
        APPROVE: {
          target: 'approved',
          actions: assign({
            'approvals.admin': (ctx, event) => ({
              approvedBy: event.approver,
              approvedAt: new Date(),
              status: 'approved'
            })
          })
        },
        REJECT: {
          target: 'draft',
          actions: assign({
            'approvals.admin': (ctx, event) => ({
              status: 'rejected',
              comment: event.comment
            })
          })
        }
      }
    },
    approved: {
      type: 'final',
      actions: () => {
        // Send completion notification
      }
    }
  }
});

// 2. Create approval store
const useApprovalStore = create(
  persist(
    (set) => ({
      requestId: '',
      currentState: 'draft',
      approvals: {},

      sendEvent: (event) =>
        set((state) => {
          const nextState = approvalMachine.transition(state.currentState, event);
          return {
            currentState: nextState.value,
            approvals: {
              ...state.approvals,
              ...nextState.context.approvals
            }
          };
        }),

      canApprove: (role) => (state) => {
        const permissions = {
          manager_review: ['manager'],
          director_review: ['director'],
          admin_review: ['admin']
        };

        return permissions[state.currentState]?.includes(role) || false;
      }
    }),
    {
      name: 'approval-store'
    }
  )
);
```

---

## Testing Multi-Step Workflows

### 1. Unit Test Pattern for Each Step

```typescript
describe('Step 1: Personal Information', () => {
  test('should validate required fields', () => {
    const schema = formSchemaV1.shape.personalInfo;

    expect(schema.safeParse({ name: '', email: '' }).success).toBe(false);
    expect(schema.safeParse({ name: 'John', email: 'john@example.com' }).success).toBe(true);
  });

  test('should persist data to store', () => {
    const { result } = renderHook(() => useFormStore());

    act(() => {
      result.current.updateData(['personalInfo', 'name'], 'John Doe');
    });

    expect(result.current.data.personalInfo.name).toBe('John Doe');
  });

  test('should maintain data after component remount', () => {
    const { result, unmount, rerender } = renderHook(() => useFormStore());

    act(() => {
      result.current.updateData(['personalInfo', 'name'], 'John Doe');
    });

    unmount();

    // Simulate page refresh by creating new store instance with persisted data
    const newResult = renderHook(() => useFormStore());
    expect(newResult.result.current.data.personalInfo.name).toBe('John Doe');
  });
});
```

### 2. Integration Test Pattern for Flow

```typescript
describe('Multi-Step Form Flow', () => {
  test('should complete full flow with valid data', async () => {
    const { result } = renderHook(() => ({
      store: useFormStore(),
      navigation: useFormNavigation()
    }));

    // Step 1: Enter personal info
    act(() => {
      result.current.store.updateData(['personalInfo'], {
        name: 'John Doe',
        email: 'john@example.com'
      });
    });

    // Navigate to step 2
    act(() => {
      result.current.navigation.goToStep('step2');
    });

    expect(result.current.store.currentStep).toBe('step2');

    // Step 2: Enter contact info
    act(() => {
      result.current.store.updateData(['contactInfo'], {
        phone: '5551234567'
      });
    });

    // Navigate to step 3
    act(() => {
      result.current.navigation.goToStep('step3');
    });

    expect(result.current.store.currentStep).toBe('step3');
  });

  test('should prevent forward navigation without valid data', async () => {
    const { result } = renderHook(() => useFormNavigation());

    // Try to go to step 2 without completing step 1
    act(() => {
      result.current.goToStep('step2');
    });

    // Should still be on step 1
    expect(result.current.currentStep).toBe('step1');
  });

  test('should maintain data when navigating backward', async () => {
    const { result } = renderHook(() => ({
      store: useFormStore(),
      navigation: useFormNavigation()
    }));

    // Complete step 1 and 2
    act(() => {
      result.current.store.updateData(['personalInfo'], {
        name: 'John Doe',
        email: 'john@example.com'
      });
    });

    // Assume navigation to step 2 succeeds...
    const originalPersonalInfo = result.current.store.data.personalInfo;

    // Go back
    act(() => {
      result.current.navigation.goToStep('step1');
    });

    // Data should still be there
    expect(result.current.store.data.personalInfo).toEqual(originalPersonalInfo);
  });
});
```

### 3. State Machine Test Pattern

```typescript
describe('Approval State Machine', () => {
  test('should follow valid state transitions', () => {
    const service = interpret(approvalMachine).start();

    expect(service.state.value).toBe('draft');

    // Valid: draft -> manager_review
    service.send('SUBMIT');
    expect(service.state.value).toBe('manager_review');

    // Valid: manager_review -> director_review
    service.send({
      type: 'APPROVE',
      approver: 'manager@example.com'
    });
    expect(service.state.value).toBe('director_review');
  });

  test('should prevent invalid transitions', () => {
    const service = interpret(approvalMachine).start();

    // Invalid: draft doesn't have APPROVE event
    service.send('APPROVE');

    // Should stay in draft
    expect(service.state.value).toBe('draft');
  });

  test('should handle complex approval chain', async () => {
    const service = interpret(approvalMachine).start();

    // Complete workflow
    service.send('SUBMIT');
    service.send({ type: 'APPROVE', approver: 'manager@example.com' });
    service.send({ type: 'APPROVE', approver: 'director@example.com' });
    service.send({ type: 'APPROVE', approver: 'admin@example.com' });

    expect(service.state.value).toBe('approved');
    expect(service.state.done).toBe(true);
  });

  test('should reject and return to draft', async () => {
    const service = interpret(approvalMachine).start();

    service.send('SUBMIT');
    service.send({
      type: 'REJECT',
      comment: 'Need more information'
    });

    expect(service.state.value).toBe('draft');
  });
});
```

---

## Related Resources

### Web Search Sources

- [Material UI Stepper Component](https://mui.com/material-ui/react-stepper/) - Current stepper patterns (2025)
- [CoreUI React Stepper Documentation](https://coreui.io/react/docs/forms/stepper/) - Linear/non-linear stepper modes
- [State Management Trends in React 2025](https://makersden.io/blog/react-state-management-in-2025) - Zustand vs XState comparison
- [XState Catalogue - Multi-Step Form](https://xstate-catalogue.com/machines/multi-step-form) - Production state machine examples
- [React Hook Form Multi-Step Tutorial](https://www.buildwithmatija.com/blog/master-multi-step-forms-build-a-dynamic-react-form-in-6-simple-steps) - Zustand + Zod patterns
- [Dapr Workflow Patterns](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/) - Enterprise workflow patterns
- [AWS Step Functions Human Approval](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-human-approval.html) - Multi-role approval chains
- [localStorage Persistence Guide](https://blog.logrocket.com/localstorage-javascript-complete-guide/) - Client-side data persistence
- [XState Documentation](https://stately.ai/docs/xstate) - Official state machine library

---

## Summary: Key Principles for Safety

1. **NEVER INSERT steps into the middle** - Always append new steps to the end
2. **ALWAYS version your data schemas** - Track migrations explicitly
3. **ALWAYS validate at step boundaries** - Don't assume downstream has correct data
4. **ALWAYS use feature flags for behavioral changes** - Allow safe rollout and rollback
5. **ALWAYS document step dependencies** - Make implicit contracts explicit
6. **ALWAYS persist state outside components** - Use Zustand/Redux/Context + localStorage
7. **ALWAYS test backward navigation** - Ensure data persists when going back
8. **ALWAYS handle conditional steps explicitly** - Use state machine guards, not inline logic
9. **ALWAYS provide migration paths** - Support old workflow versions during transition
10. **ALWAYS log state transitions** - Enable debugging when workflows break

---

**Document Status**: Comprehensive reference for workflow-guardian skill development
**Next Steps**: Integrate patterns into workflow-guardian detection rules and safety checks
**Ownership**: Workflow safety task force
**Version**: 1.0 (February 2026)
