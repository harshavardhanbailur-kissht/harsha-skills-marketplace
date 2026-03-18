# Architecture Boundary Preservation Guide
Reference for workflow-guardian skill to detect and prevent architecture violations.

---

## 1. One Technology Per Concern (CRITICAL RULE)

**The Core Principle:** Each architectural concern (auth, storage, database) must have exactly ONE technology serving it. Adding a second technology creates:
- Redundant configuration
- Inconsistent schema
- Confusing state management
- Maintenance nightmares

### 1.1 Auth: Establish the Source of Truth

**Real-world failure (Project 1):**
```typescript
// SimpleAuthContext.tsx: Password-based role auth
const HARDCODED_PASSWORD = '1111';
if (password === HARDCODED_PASSWORD) {
  setRole(selectedRole);
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ role }));
}

// GoogleDriveContext.tsx: Separate Google OAuth flow
await authenticateGoogleDrive(); // Independent auth system!
```

**Why this broke:** Two authentication systems run independently. A user can be logged into the app but not Google Drive. Or vice versa.

**Guardrails:**
- **Detection:** Search for all authentication mechanisms in project:
  - `firebase.auth()` calls
  - `supabase.auth.*` calls
  - OAuth redirect URLs
  - localStorage keys for auth state
  - Custom password validation
- **Rule:** Only ONE of the above should exist
- **Example - Check package.json:**
  ```json
  {
    "dependencies": {
      "firebase": "^10.0.0"  // ← If Firebase Auth exists
    }
  }
  // INVALID: Adding "auth0": "^2.0.0" or "@supabase/auth-helpers-react"
  ```

### 1.2 Storage: One File Destination

**Real-world failure (Project 1):**
```typescript
// firebase.ts: Firebase Storage declared in ARCHITECTURE_GUIDE
export const uploadToFirebase = (file) => {
  return storage.ref().child(path).put(file);
};

// driveUpload.ts: Google Drive API also uploads files
export const uploadFileToDrive = (file) => {
  return drive.files.create({ requestBody: { /* ... */ } });
};

// submissions.ts: Both are called
submissionData.attachmentUrl = uploadResult.shareableUrl; // Drive
submissionData.attachmentDriveId = uploadResult.fileId;   // Drive
```

**Why this broke:** Schema became inconsistent. Some records have `attachmentUrl`, some have `attachmentDriveId`. Impossible to reason about data durability.

**Guardrails:**
- **Detection:** Search for all file upload APIs:
  - `firebase.storage()` or `ref(storage)`
  - `.put()`, `.upload()` calls
  - AWS S3 SDK: `s3.upload()`
  - Google Drive API: `drive.files.create()`
  - Supabase: `supabase.storage.from()`
- **Rule:** Exactly ONE should have implementations
- **Decision Point:** Check which is referenced in:
  - Production code (src/lib/, src/services/)
  - Environment variables (VITE_STORAGE_BUCKET vs VITE_DRIVE_FOLDER_ID)
  - Database schema (which fields exist for file references?)

### 1.3 Database: Single Source of Data

**Check what's in use:**
```typescript
// Look for these in code:
import { initializeApp } from 'firebase/app';           // ← Firestore
import { createClient } from '@supabase/supabase-js';  // ← Postgres
import { MongoClient } from 'mongodb';                  // ← MongoDB

// Or in package.json:
// "firebase": "^10.0.0"
// "@supabase/supabase-js": "^2.0.0"
// OR "mongoose": "^7.0.0"
```

**Guardrail:** Only ONE of the above imports/packages should exist. If you find two, you've discovered a violation.

---

## 2. Service Layer Boundaries

**The Contract:** Hide technology choices behind well-defined service APIs. Components never import SDK clients directly.

### 2.1 Identify Existing Service Boundaries

**Good pattern (if it exists in the project):**
```typescript
// src/services/auth.ts — THE service boundary for authentication
export const authService = {
  login: async (role: string) => { /* ... */ },
  logout: () => { /* ... */ },
  getCurrentUser: () => { /* ... */ },
  hasRole: (role: string) => { /* ... */ },
};

// src/services/storage.ts — THE service boundary for files
export const storageService = {
  uploadFile: async (file: File, path: string) => { /* ... */ },
  deleteFile: async (fileId: string) => { /* ... */ },
  getDownloadUrl: async (fileId: string) => { /* ... */ },
};

// src/services/submissions.ts — Calls storageService, NOT Firebase directly
import { storageService } from './storage';
export const createSubmission = async (data) => {
  const uploadResult = await storageService.uploadFile(file, path);
  // ... rest of logic
};
```

**Component (GOOD):**
```typescript
import { useSubmissions } from '@/hooks/useSubmissions';

export function SubmissionForm() {
  const { submit } = useSubmissions();
  return <button onClick={submit}>Submit</button>;
}
```

**Component (BAD - ANTI-PATTERN):**
```typescript
import { ref, uploadBytes } from 'firebase/storage';
import { storage } from '@/lib/firebase'; // ← Direct SDK import!

export function SubmissionForm() {
  const handleSubmit = async (file) => {
    await uploadBytes(ref(storage, path), file); // ← Should go through service
  };
}
```

### 2.2 New Features Must Call Existing Services

**Guardrail:** Before creating new functionality:
1. List all existing services (auth, storage, database, external APIs)
2. Check if ANY existing service can be extended
3. If service doesn't exist, create it following existing patterns

**Example:** Adding email notifications
```typescript
// BAD: New service created differently
import nodemailer from 'nodemailer';
export async function sendEmail(to, subject, body) {
  const transporter = nodemailer.createTransport({...});
  return transporter.sendMail({...});
}

// GOOD: Create email service following existing patterns
// src/services/notifications.ts
export const notificationService = {
  sendEmail: async (to, subject, body) => { /* ... */ },
  sendInApp: async (userId, message) => { /* ... */ },
};
// Pattern matches: storage, auth, submissions
```

---

## 3. Role System Integrity

**Problem:** Roles scattered across the codebase make authorization unreliable.

### 3.1 Find ALL Role Definitions

**Real-world example (Project 1) - Scattered roles:**
```typescript
// src/contexts/SimpleAuthContext.tsx:27
if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support')

// src/lib/submissions.ts:109-115
if (role === 'product_support') {
  assignedTo = 'sm';
} else if (role === 'sm') {
  assignedTo = 'product_support';
}

// src/pages/LoginPage.tsx (implied)
const ROLE_OPTIONS = ['sm', 'tech_support_team', 'product_support'];

// src/pages/Dashboard.tsx (hardcoded)
if (userRole === 'sm') { /* show SM dashboard */ }
if (userRole === 'tech_support_team') { /* different content */ }
```

**What went wrong:**
- tech_support_team defined in auth context
- But mapping logic only handles sm/product_support
- New roles scattered everywhere → can't audit access control

### 3.2 Create a Single Source for Role Constants

**Guardrail - Create file:**
```typescript
// src/types/roles.ts — THE source of truth
export const ROLES = {
  SM: 'sm',
  TECH_SUPPORT: 'tech_support_team',
  PRODUCT_SUPPORT: 'product_support',
} as const;

export type Role = typeof ROLES[keyof typeof ROLES];

// What each role can access:
export const ROLE_PERMISSIONS = {
  [ROLES.SM]: ['view_submissions', 'assign_tickets', 'close_tickets'],
  [ROLES.TECH_SUPPORT]: ['view_own_submissions', 'comment'],
  [ROLES.PRODUCT_SUPPORT]: ['create_submissions', 'view_own'],
} as const;
```

**Then use everywhere:**
```typescript
// src/contexts/SimpleAuthContext.tsx
import { ROLES } from '@/types/roles';
if (storedRole === ROLES.SM || storedRole === ROLES.TECH_SUPPORT) {
  // ...
}

// src/lib/submissions.ts
if (role === ROLES.PRODUCT_SUPPORT) {
  assignedTo = ROLES.SM;
}
```

### 3.3 Never Create Aliases

**BAD:**
```typescript
// src/lib/submissions.ts
const SM_ROLE = 'sm'; // ← Alias of the role constant, different location!

// Later in code:
if (role === SM_ROLE) { /* ... */ }
```

**GOOD:**
```typescript
import { ROLES } from '@/types/roles';

if (role === ROLES.SM) { /* ... */ }
```

---

## 4. Dependency Management

**Principle:** Every npm package should have ONE clear purpose. Before adding a package, verify:

### 4.1 Check if Problem is Already Solved

**Real-world example (Project 1):**
```json
{
  "dependencies": {
    "firebase": "^10.7.1",
    "googleapis": "^170.1.0",
    "@vercel/node": "^5.5.25"
  }
}
```

**Questions to ask:**
- Why googleapis? It adds 30KB+ to bundle. Is resumable upload truly required?
- Why @vercel/node in client SPA? It's a server runtime package.
- Are these solving a problem Firebase already solves?

**Guardrail - Before adding package:**
1. Run: `grep -r "problm-we're-solving" src/`
2. Check if existing packages already export it
3. If multiple packages solve it, choose ONE and document why

**Example:**
```typescript
// Check: Do we already have a time library?
import { format } from 'date-fns'; // ← Already using date-fns

// DON'T add moment.js unless date-fns is insufficient
// document WHY in ARCHITECTURE_GUIDE.md

// Example bad decision (competing libraries):
import moment from 'moment'; // ← AND date-fns? Choose one.
```

### 4.2 Match Existing Dependency Philosophy

**Lightweight approach (like los-issue-tracker):**
```json
{
  "dependencies": {
    "react": "^18.0",
    "supabase": "^2.0"
  }
}
// Pattern: Minimal, essential, composable
```

**Full-featured approach (like some Firebase projects):**
```json
{
  "dependencies": {
    "firebase": "^10.0",
    "@mui/material": "^5.0",
    "redux": "^4.0"
  }
}
// Pattern: Batteries-included, integrated
```

**Guardrail:** Don't mix philosophies. If project uses minimal dependencies, adding 50KB library needs strong justification.

---

## 5. Configuration Consistency

**Problem:** Configuration sources scattered across .env files, code constants, and config objects.

### 5.1 Use Existing Env Var Pattern

**Real-world example (Project 1):**
```
VITE_FIREBASE_API_KEY          ← Firebase config
VITE_FIREBASE_PROJECT_ID
VITE_GOOGLE_API_KEY            ← Google Drive config
VITE_GOOGLE_CLIENT_ID
VITE_GOOGLE_DRIVE_FOLDER_ID
```

**Issue:** 9+ variables for essentially 2 services. No validation that all required ones exist.

**Better pattern:**
```typescript
// src/config.ts — Single source for all config
export const config = {
  firebase: {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  },
  auth: {
    hardcodedPassword: import.meta.env.VITE_AUTH_PASSWORD, // ← Single source
  },
} as const;

// Validate at startup
if (!config.firebase.apiKey) {
  throw new Error('Missing VITE_FIREBASE_API_KEY');
}
```

**Guardrail:**
- All env vars should be read in ONE file
- Validation should happen at app startup, not at call-time
- Document required env vars in .env.example

### 5.2 Don't Mix Configuration Sources

**BAD:**
```typescript
// src/lib/firebase.ts
const API_KEY = import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyCYrY93JMKuAol-..."; // ← Fallback!

// src/config.ts
export const FOLDER_ID = "1234567890abcdef"; // ← Hardcoded instead of env
```

**GOOD:**
```typescript
// .env.example
VITE_FIREBASE_API_KEY=
VITE_GOOGLE_DRIVE_FOLDER_ID=

// src/config.ts
export const config = {
  firebase: {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  },
  storage: {
    driveFolderId: import.meta.env.VITE_GOOGLE_DRIVE_FOLDER_ID,
  },
};

if (!config.firebase.apiKey) throw new Error('Missing VITE_FIREBASE_API_KEY');
```

---

## 6. Architecture Decision Record Template

When a boundary MUST be crossed or changed, document it formally:

```markdown
# ADR-001: [Decision Title]

**Status:** Accepted | Proposed | Deprecated

**Decision:** [What we decided to do]

**Context:** [Why this was needed]
- [Constraint 1]
- [Constraint 2]

**Consequences:** [Impact of this decision]
- [Positive impact 1]
- [Tradeoff 1]
- [Maintenance burden]

**Alternatives Considered:**
- [Alternative A]: Why rejected
- [Alternative B]: Why rejected

**Related Decisions:**
- [Link to previous related ADR]

**Reviewed By:** [Team names]
**Date:** YYYY-MM-DD
```

**Example (from Project 1 - should have existed):**
```markdown
# ADR-002: Add Google Drive for Resumable Uploads

**Status:** Accepted

**Decision:** Use Google Drive API alongside Firebase Storage for file attachments

**Context:**
- Firebase Storage lacked resumable upload support for large files
- Users had poor experience with dropped connections
- Google Drive API offers native resumable uploads

**Consequences:**
- Must maintain two storage backends
- Data schema now has both attachmentUrl (Firebase) and attachmentDriveId (Drive)
- Additional OAuth token management required
- Adds googleapis dependency (30KB+)

**Alternatives Considered:**
- Implement resumable uploads with Firebase directly: Too complex, not supported
- Use AWS S3: Would require AWS credentials, outside current stack
- Reduce max file size: Users requested larger attachments

**Tradeoff Accepted:** Maintenance complexity justified by UX improvement
```

---

## Quick Checklist for Violations

Use this when reviewing code changes:

- [ ] Multiple auth systems detected (auth0 + firebase + custom)?
- [ ] Multiple storage backends in use (Firebase + S3 + Drive)?
- [ ] Role constants scattered across files instead of one source?
- [ ] Service layer bypassed (components importing SDK directly)?
- [ ] New npm package added without checking existing solutions?
- [ ] Env vars read in multiple places instead of config.ts?
- [ ] Hardcoded values instead of configuration?
- [ ] New role created without updating all auth checks?
- [ ] Service/feature created without following existing patterns?

**If any are true:** Stop and document in an ADR before proceeding.
