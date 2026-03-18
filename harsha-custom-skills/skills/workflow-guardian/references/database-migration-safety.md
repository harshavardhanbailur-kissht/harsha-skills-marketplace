# Database Migration Safety Patterns

**Version:** 1.0
**Last Updated:** February 2026
**Scope:** Workflow Guardian Skill Database Evolution Strategy

This comprehensive reference document covers safe database migration patterns, extracted from two production systems: Los Issue Tracker (Supabase/PostgreSQL) and Issue Tracker (Firestore), with 28+ migrations analyzed.

---

## Table of Contents

1. [Schema Evolution Patterns](#schema-evolution-patterns)
2. [Firestore-Specific Patterns](#firestore-specific-patterns)
3. [Supabase/PostgreSQL Patterns](#supabasepostgresql-patterns)
4. [Frontend-Backend Schema Sync](#frontend-backend-schema-sync)
5. [Migration Safety Checklist](#migration-safety-checklist)
6. [Real Failure Examples](#real-failure-examples)

---

## Schema Evolution Patterns

Safe schema evolution requires a deliberate approach to backward compatibility and data validation. The Los Issue Tracker system demonstrates mature patterns tested across 28 migrations in production.

### Adding Fields

**Nullable Fields (Safest Approach)**

Always add new columns as nullable initially, then backfill with default/computed values:

```sql
-- Migration: Add Google Sheets Integration Fields (001_add_google_sheets_fields.sql)
BEGIN;

-- Step 1: Add columns as nullable for backward compatibility
ALTER TABLE tickets
  ADD COLUMN IF NOT EXISTS issue_date DATE DEFAULT CURRENT_DATE,
  ADD COLUMN IF NOT EXISTS unique_number VARCHAR(50),
  ADD COLUMN IF NOT EXISTS query_category VARCHAR(50),
  ADD COLUMN IF NOT EXISTS sub_category VARCHAR(50),
  ADD COLUMN IF NOT EXISTS employee_name VARCHAR(100);

-- Step 2: Backfill existing records with computed values
UPDATE tickets
SET
  issue_date = COALESCE(issue_date, DATE(submitted_at)),
  unique_number = COALESCE(unique_number, CONCAT('TKT-', ticket_number::text)),
  query_category = COALESCE(query_category, issue_type),
  employee_name = COALESCE(employee_name, claimed_by)
WHERE unique_number IS NULL OR query_category IS NULL;

-- Step 3: Add constraints AFTER backfill
ALTER TABLE tickets
  ALTER COLUMN unique_number SET NOT NULL,
  ADD CONSTRAINT unique_number_unique UNIQUE (unique_number);

-- Step 4: Add indexes for new query fields
CREATE INDEX IF NOT EXISTS idx_tickets_unique_number ON tickets(unique_number);
CREATE INDEX IF NOT EXISTS idx_tickets_query_category ON tickets(query_category);

-- Step 5: Verification
DO $$
DECLARE
  new_cols INTEGER;
BEGIN
  SELECT COUNT(*) INTO new_cols
  FROM information_schema.columns
  WHERE table_name = 'tickets'
    AND column_name IN ('issue_date', 'unique_number', 'query_category', 'sub_category', 'employee_name');

  IF new_cols < 5 THEN
    RAISE EXCEPTION 'Migration failed: Expected 5 new columns, found %', new_cols;
  END IF;
END $$;

COMMIT;
```

**Why This Pattern Works:**

- **Backward Compatibility:** Old application versions continue working (nullable columns don't break inserts)
- **Zero Downtime:** Data backfill happens within transaction, no application restart needed
- **Atomic:** Entire operation succeeds or rolls back as unit
- **Verification Built-In:** Explicit checks prevent partial failures
- **Rollback Clear:** Comment block shows exact UNDO commands

**Default Values Matter:**

```typescript
// TypeScript interface (src/types/index.ts)
export interface Ticket {
  id: string;
  issue_date?: string;           // Optional in interface
  unique_number?: string;        // Optional in interface
  query_category?: QueryCategory | null;
  // ... other fields
}
```

The `?` (optional) marker in TypeScript matches the database nullable status. When migrating, ensure interface updates happen simultaneously with database changes.

### Making Fields Mandatory (NOT NULL)

Converting nullable fields to NOT NULL is a dangerous multi-step process:

```sql
-- Migration: Make LSQ URL Mandatory (003_make_lsq_url_mandatory.sql)
BEGIN;

-- Step 1: Identify and fix NULL values
UPDATE tickets
SET lsq_url = 'https://placeholder-url.com/migrated-ticket'
WHERE lsq_url IS NULL OR lsq_url = '';

-- Step 2: Verify no NULLs remain before constraint
DO $$
DECLARE
  null_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO null_count
  FROM tickets
  WHERE lsq_url IS NULL;

  IF null_count > 0 THEN
    RAISE EXCEPTION 'Migration blocked: Found % tickets with NULL lsq_url', null_count;
  END IF;
END $$;

-- Step 3: Apply constraint
ALTER TABLE tickets
  ALTER COLUMN lsq_url SET NOT NULL;

COMMIT;

-- Rollback available:
-- ALTER TABLE tickets ALTER COLUMN lsq_url DROP NOT NULL;
```

**Critical Rules:**

1. **Always validate existing data first** - Don't assume NULL values don't exist
2. **Backfill with sensible defaults** - Never use random values or empty strings
3. **Test on production-like data** - Large tables with many NULLs may need batching
4. **Provide rollback scripts** - In comments, ready to execute if needed

### Adding Indexes

Indexes must be added **without blocking production queries**:

```sql
-- Migration: Tighten RLS + Add Production Indexes (010_tighten_rls_and_add_indexes.sql)
BEGIN;

-- For frequently-queried combinations, create composite indexes
CREATE INDEX IF NOT EXISTS idx_tickets_submitted_by_status
  ON public.tickets (submitted_by, status);

CREATE INDEX IF NOT EXISTS idx_tickets_claimed_by_status
  ON public.tickets (claimed_by, status);

-- For unique constraints, use partial indexes that allow NULLs
-- (TRN can be NULL for some tickets, but duplicates are forbidden)
CREATE UNIQUE INDEX IF NOT EXISTS idx_tickets_trn_unique
  ON public.tickets (trn)
  WHERE trn IS NOT NULL;

COMMIT;
```

**Index Design Principles:**

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Single Column** | Direct lookups | `idx_tickets_ticket_number` |
| **Composite (2-3 cols)** | Filter + Sort combinations | `idx_tickets_submitted_by_status` |
| **Partial** | Allow NULLs in unique constraints | `idx_tickets_trn_unique WHERE trn IS NOT NULL` |
| **UNIQUE** | Data integrity enforcement | `UNIQUE (unique_number)` |

**What NOT to do:**

```sql
-- BAD: Overly broad index (creates database bloat)
CREATE INDEX idx_everything ON tickets(col1, col2, col3, col4, col5);

-- BAD: Indexes query isn't using
CREATE INDEX idx_unused ON tickets(rarely_queried_column);

-- BAD: Redundant indexes (both achieve same thing)
CREATE INDEX idx_a ON tickets(status);
CREATE INDEX idx_b ON tickets(status);  -- Duplicate!
```

### Adding Constraints (Email Validation Example)

Constraints should be added in stages to avoid locking production tables:

```sql
-- Migration: Add Email Validation (019_add_email_validation.sql)
BEGIN;

-- Step 1: Create validation function (IMMUTABLE for use in indexes)
CREATE OR REPLACE FUNCTION public.is_valid_email(email TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  IF email IS NULL OR email = '' THEN
    RETURN FALSE;
  END IF;

  -- RFC 5322 simplified regex
  RETURN email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
END;
$$;

-- Step 2: Validate existing data
DO $$
DECLARE
  invalid_count INTEGER;
  sample_invalid TEXT;
BEGIN
  SELECT COUNT(*) INTO invalid_count
  FROM public.tickets
  WHERE NOT is_valid_email(submitted_by);

  IF invalid_count > 0 THEN
    SELECT submitted_by INTO sample_invalid
    FROM public.tickets
    WHERE NOT is_valid_email(submitted_by)
    LIMIT 1;

    RAISE EXCEPTION 'Migration blocked: Found % invalid emails. Example: "%"',
      invalid_count, sample_invalid;
  END IF;

  RAISE NOTICE 'Email validation check PASSED ✓';
END $$;

-- Step 3: Add constraint (NOT VALID avoids table lock)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'check_submitted_by_email_format'
  ) THEN
    ALTER TABLE public.tickets
      ADD CONSTRAINT check_submitted_by_email_format
        CHECK (is_valid_email(submitted_by)) NOT VALID;
  END IF;
END $$;

-- Step 4: Validate constraint asynchronously
ALTER TABLE public.tickets VALIDATE CONSTRAINT check_submitted_by_email_format;

COMMIT;
```

**Key Technique: NOT VALID + VALIDATE**

1. `ADD CONSTRAINT ... NOT VALID` - Does NOT lock the table, fails fast if constraint definition is invalid
2. `VALIDATE CONSTRAINT` - Validates existing data WITHOUT an exclusive lock
3. Application can continue running while validation happens
4. If validation fails, you can fix data and retry without redoing the migration

### Renaming Fields

Field renames require a gradual deprecation period:

```sql
-- ANTI-PATTERN (Breaking Change):
-- ALTER TABLE tickets RENAME COLUMN old_name TO new_name;

-- BETTER PATTERN (Gradual Migration):

-- Step 1: Add new column with computed values
ALTER TABLE tickets ADD COLUMN new_name VARCHAR GENERATED ALWAYS AS (old_name) STORED;

-- Step 2: Create database view for backward compatibility
CREATE VIEW tickets_compat AS
  SELECT *, old_name AS new_name FROM tickets;

-- Step 3: Update applications to use new column
-- (can take days/weeks in production)

-- Step 4: Only after applications verified - drop old column
ALTER TABLE tickets DROP COLUMN old_name CASCADE;
```

### Changing Field Types

Type changes require data conversion with validation:

```sql
-- Example: Converting status TEXT to status ENUM
-- (Los Issue Tracker uses: 'open' | 'claimed' | 'resolved')

BEGIN;

-- Step 1: Create new ENUM type
CREATE TYPE ticket_status AS ENUM ('open', 'claimed', 'resolved');

-- Step 2: Add new column with conversion
ALTER TABLE tickets ADD COLUMN status_new ticket_status;

-- Step 3: Migrate data with validation
UPDATE tickets
SET status_new = status::ticket_status
WHERE status IN ('open', 'claimed', 'resolved');

-- Step 4: Verify migration success
DO $$
DECLARE
  unconverted_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO unconverted_count
  FROM tickets
  WHERE status IS NOT NULL AND status_new IS NULL;

  IF unconverted_count > 0 THEN
    RAISE EXCEPTION 'Failed to convert % records', unconverted_count;
  END IF;
END $$;

-- Step 5: Swap columns (atomic)
ALTER TABLE tickets DROP COLUMN status;
ALTER TABLE tickets RENAME COLUMN status_new TO status;

COMMIT;
```

---

## Firestore-Specific Patterns

Firestore doesn't have schema migrations like SQL databases (schemaless), but still requires coordinated evolution:

### Collection Structure Changes

From `issue-tracker` Firebase project:

```typescript
// OLD: Single attachmentUrl field
export interface Submission {
  attachmentUrl?: string;        // DEPRECATED
  attachmentDriveId?: string;    // DEPRECATED
  // ... other fields
}

// NEW: Array of attachments (multiple file support)
export interface Submission {
  attachments?: Attachment[];     // NEW
  // OLD fields kept for backward compatibility
  attachmentUrl?: string;        // DEPRECATED
  attachmentDriveId?: string;    // DEPRECATED
}

export interface Attachment {
  url: string;
  driveId: string;
  fileName: string;
  fileSize: number;
}
```

**Migration Steps:**

1. **Add new field** (docs now have both old and new)
   ```typescript
   const submission = {
     attachmentUrl: 'https://...',  // OLD
     attachmentDriveId: 'file123',
     attachments: [{                 // NEW
       url: 'https://...',
       driveId: 'file123',
       fileName: 'form.pdf',
       fileSize: 2048
     }]
   };
   ```

2. **Update read logic to check both**
   ```typescript
   // Prioritize new field, fallback to old
   const getAttachments = (submission: Submission): Attachment[] => {
     if (submission.attachments?.length) {
       return submission.attachments;
     }

     // Fallback for old documents
     if (submission.attachmentUrl) {
       return [{
         url: submission.attachmentUrl,
         driveId: submission.attachmentDriveId || '',
         fileName: 'attachment',
         fileSize: 0
       }];
     }

     return [];
   };
   ```

3. **Backfill old documents** (one-time script)
   ```typescript
   // Run after new code is deployed
   const backfillAttachments = async () => {
     const snapshot = await db.collection('submissions')
       .where('attachments', '==', undefined)
       .where('attachmentUrl', '!=', null)
       .get();

     const batch = db.batch();
     snapshot.docs.forEach(doc => {
       const data = doc.data();
       batch.update(doc.ref, {
         attachments: [{
           url: data.attachmentUrl,
           driveId: data.attachmentDriveId,
           fileName: 'attachment',
           fileSize: 0
         }]
       });
     });

     await batch.commit();
   };
   ```

4. **Monitor and deprecate old field** (weeks/months later)
   ```typescript
   // Once backfill complete, remove fallback code
   const getAttachments = (submission: Submission): Attachment[] => {
     return submission.attachments || [];
   };
   ```

### Security Rules Evolution

Firestore security rules require careful rollout:

```javascript
// firestore.rules - Initial permissive rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /submissions/{submissionId} {
      allow read, create: if true;
      allow update: if true;
      allow delete: if false;
    }
  }
}
```

**Evolution Path:**

```javascript
// STEP 1: Add request validation (read/write still permissive)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /submissions/{submissionId} {
      allow read: if true;
      allow create: if request.resource.data.submittedBy != null;
      allow update: if request.auth != null;
      allow delete: if false;
    }
  }
}

// STEP 2: Add authentication requirement
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /submissions/{submissionId} {
      // Only authenticated users can read their own submissions
      allow read: if request.auth != null && (
        request.auth.uid == resource.data.submittedBy ||
        request.auth.token.admin == true
      );

      allow create: if request.auth != null &&
        request.auth.uid == request.resource.data.submittedBy;

      allow update: if request.auth != null &&
        request.auth.token.admin == true;

      allow delete: if false;
    }
  }
}

// STEP 3: Add role-based access (from allowed_users equivalent)
// Note: Firestore doesn't have RLS like SQL, use token-based rules instead
function isAdmin() {
  return request.auth.token.admin == true;
}

function isOwner(submittedBy) {
  return request.auth.uid == submittedBy;
}

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /submissions/{submissionId} {
      allow read: if isOwner(resource.data.submittedBy) || isAdmin();
      allow create: if isOwner(request.resource.data.submittedBy);
      allow update: if isAdmin();
      allow delete: if false;
    }
  }
}
```

**Key Differences from SQL RLS:**

- **No row-level filtering** - Rules apply to entire document, not specific columns
- **Token-based** - Use Firebase Auth claims (admin flag, roles, etc.)
- **No query filtering** - If rule denies access, query fails (doesn't return empty results)
- **Careful with exists()** - `exists(/databases/{db}/documents/users/{uid})` queries can be expensive

### Index Management

Firestore auto-creates basic indexes, but complex queries need explicit indexes:

```json
{
  "firestore": {
    "indexes": "firestore.indexes.json"
  }
}
```

From `firestore.indexes.json`:

```json
{
  "indexes": [
    {
      "collectionGroup": "submissions",
      "queryScope": "Collection",
      "fields": [
        {
          "fieldPath": "submittedBy",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "status",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "submittedAt",
          "order": "DESCENDING"
        }
      ]
    },
    {
      "collectionGroup": "submissions",
      "queryScope": "Collection",
      "fields": [
        {
          "fieldPath": "assignedTo",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "status",
          "order": "ASCENDING"
        }
      ]
    }
  ]
}
```

**When Firestore auto-indexes won't work:**

```typescript
// Query that needs composite index:
const query = db.collection('submissions')
  .where('submittedBy', '==', email)
  .where('status', '==', 'pending')
  .orderBy('submittedAt', 'desc')
  .limit(10);
```

Firestore will detect missing index at query runtime and provide a link to create it automatically.

---

## Supabase/PostgreSQL Patterns

Los Issue Tracker uses 28+ migrations demonstrating production patterns:

### RLS Policy Evolution

Row Level Security (RLS) policies must evolve carefully to avoid locking out users:

```sql
-- Migration 006: Initial RLS Setup
BEGIN;

-- Enable RLS on tables
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE allowed_users ENABLE ROW LEVEL SECURITY;

-- Initial: Allow all authenticated users
CREATE POLICY "Authenticated users can read all tickets"
  ON tickets FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert tickets"
  ON tickets FOR INSERT
  TO authenticated
  WITH CHECK (true);

COMMIT;
```

**Problem Discovered:** Anyone can see all tickets + claim/resolve tickets they didn't own.

```sql
-- Migration 010: Tighten RLS
BEGIN;

-- Policy 1: Users see only own tickets OR admins see all
DROP POLICY "Authenticated users can read all tickets" ON public.tickets;
CREATE POLICY "Users can read own tickets or admin reads all"
  ON public.tickets FOR SELECT
  TO authenticated
  USING (
    lower(submitted_by) = lower((auth.jwt()->>'email'))
    OR EXISTS (
      SELECT 1 FROM public.allowed_users au
      WHERE lower(au.email) = lower((auth.jwt()->>'email'))
      AND au.role = 'admin'
    )
  );

-- Policy 2: Users can only insert tickets as themselves
DROP POLICY "Authenticated users can insert tickets" ON public.tickets;
CREATE POLICY "Users can insert own tickets"
  ON public.tickets FOR INSERT
  TO authenticated
  WITH CHECK (lower(submitted_by) = lower((auth.jwt()->>'email')));

-- Policy 3: Only admins can update (claim/resolve)
DROP POLICY "Authenticated users can update tickets" ON public.tickets;
CREATE POLICY "Admins only can update tickets"
  ON public.tickets FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.allowed_users au
      WHERE lower(au.email) = lower((auth.jwt()->>'email'))
      AND au.role = 'admin'
    )
  )
  WITH CHECK (same check);

COMMIT;
```

**Performance Issue:** `auth.jwt()` evaluated per row = N+1 problem

```sql
-- Migration 015: Optimize RLS Performance
BEGIN;

-- Wrap auth.jwt() in subselect (evaluated once per query)
DROP POLICY "Users can read own tickets or admin reads all" ON public.tickets;
CREATE POLICY "Users can read own tickets or admin reads all"
  ON public.tickets FOR SELECT
  TO authenticated
  USING (
    lower(submitted_by) = lower(((select auth.jwt()) ->> 'email'))
    OR EXISTS (
      SELECT 1 FROM public.allowed_users au
      WHERE lower(au.email) = lower(((select auth.jwt()) ->> 'email'))
      AND au.role = 'admin'
    )
  );

-- (Apply same to INSERT and UPDATE policies)

COMMIT;
```

**RLS Evolution Checklist:**

- [ ] Test policies with test users BEFORE deployment
- [ ] Monitor `pg_stat_statements` after deployment (expensive queries?)
- [ ] Use `EXPLAIN ANALYZE` to understand policy query plans
- [ ] Always have `service_role` policy as safety valve
- [ ] Document what each policy allows (in comments)
- [ ] Use `(select auth.jwt())` wrapper to optimize

### Trigger-Based Automation

Supabase uses PostgreSQL triggers for automation:

```sql
-- Migration 002: Auto-generate unique_number on INSERT
CREATE OR REPLACE FUNCTION generate_unique_number()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.unique_number IS NULL THEN
    NEW.unique_number := 'TKT-' || NEW.ticket_number::text;
  END IF;

  IF NEW.issue_date IS NULL THEN
    NEW.issue_date := CURRENT_DATE;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_unique_number
  BEFORE INSERT ON tickets
  FOR EACH ROW
  EXECUTE FUNCTION generate_unique_number();
```

**Issues Found in Production:**

1. **Search Path Hijacking (CVE-2018-1058)**
   ```sql
   -- BAD: Function uses default search_path
   CREATE FUNCTION generate_unique_number() RETURNS TRIGGER AS $$
   BEGIN
     -- DANGEROUS: attacker can create their own 'public' schema
     -- and intercept function calls
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   -- GOOD: Explicitly pin search_path to empty string
   CREATE FUNCTION generate_unique_number()
   RETURNS TRIGGER
   LANGUAGE plpgsql
   SET search_path = ''
   AS $$
   BEGIN
     RETURN NEW;
   END;
   $$;
   ```

2. **External Service Integration (HTTP Requests)**
   ```sql
   -- Migration 005: Google Chat notifications on ticket resolution
   CREATE OR REPLACE FUNCTION notify_google_chat_on_resolve()
   RETURNS TRIGGER AS $$
   DECLARE
     function_url text;
     response extensions.http_response;
   BEGIN
     IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
       -- Make HTTP POST to edge function
       response := extensions.http_post(
         'https://ewxttommdwtzqnynosim.supabase.co/functions/v1/notify-google-chat',
         jsonb_build_object('ticket', NEW)::text,
         'application/json'
       );

       IF response.status NOT BETWEEN 200 AND 299 THEN
         RAISE WARNING 'Notification failed: %', response.content;
       END IF;
     END IF;

     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER trigger_notify_google_chat
     AFTER UPDATE ON tickets
     FOR EACH ROW
     WHEN (NEW.status = 'resolved' AND OLD.status != 'resolved')
     EXECUTE FUNCTION notify_google_chat_on_resolve();
   ```

   **Security Evolution:**

   ```sql
   -- Problem: URL hardcoded in trigger = can't change without migration
   -- Solution 1 (Migration 011): Move URL to app_settings table
   SELECT value FROM app_settings WHERE key = 'supabase_function_url';

   -- Problem: Edge function has no way to verify caller is legitimate
   -- Solution 2 (Migration 008): Use internal secret in payload
   CREATE TABLE public.app_secrets (
     key TEXT PRIMARY KEY,
     value TEXT NOT NULL
   );

   -- Function includes secret in HTTP payload
   payload := jsonb_build_object(
     '_internal_secret', (SELECT value FROM app_secrets WHERE key = 'notify_internal_secret'),
     'ticket', ...
   );
   ```

3. **SECURITY DEFINER (Run as Function Owner)**
   ```sql
   -- Migration 008: Security Definer for secrets access
   CREATE OR REPLACE FUNCTION notify_google_chat_on_resolve()
   RETURNS TRIGGER
   LANGUAGE plpgsql
   SECURITY DEFINER  -- Runs with function owner's permissions
   SET search_path = ''
   AS $$
   BEGIN
     -- This function runs as the role that created it (e.g., postgres)
     -- So it can read from app_secrets even if RLS would deny users
     SELECT value INTO internal_secret
     FROM public.app_secrets
     WHERE key = 'notify_internal_secret';

     RETURN NEW;
   END;
   $$;
   ```

   **SECURITY DEFINER Risks:**
   - Function has elevated permissions
   - Must not accept arbitrary SQL from users
   - Validate inputs strictly
   - Document what permissions it needs

### Edge Functions and Schema Dependencies

```typescript
// Supabase Edge Function: sync-to-sheets
// supabase/functions/sync-to-sheets/index.ts

export const handler = async (req: Request) => {
  const { ticket_number, operation } = await req.json();

  // Query database (as service_role, via Supabase client)
  const { data: ticket, error } = await supabaseAdmin
    .from('tickets')
    .select('*')
    .eq('ticket_number', ticket_number)
    .single();

  if (error) throw error;

  // Expects these fields from schema
  const row = {
    unique_number: ticket.unique_number,        // REQUIRED
    ticket_number: ticket.ticket_number,        // REQUIRED
    query_category: ticket.query_category,      // From migration 001
    sub_category: ticket.sub_category,          // From migration 001
    employee_name: ticket.employee_name,        // From migration 001
    // ... etc
  };

  // Append to Google Sheets
  const response = await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: 'A1',
    valueInputOption: 'RAW',
    requestBody: {
      values: [Object.values(row)]
    }
  });

  return new Response(
    JSON.stringify({ success: true }),
    { headers: { 'Content-Type': 'application/json' } }
  );
};
```

**Schema Dependency Tracking:**

When migration 001 added Google Sheets fields:

```typescript
// ticket.unique_number - Created in migration 001
// ticket.query_category - Created in migration 001
// ticket.sub_category - Created in migration 001
// ticket.employee_name - Created in migration 001
```

If any of these migrations were reverted:
- Edge function would receive `undefined` for those fields
- Google Sheets row would have empty cells
- No error (just silent data loss)

**Safe Pattern:**

```typescript
// In edge function, validate required fields
const validateTicketSchema = (ticket: any): boolean => {
  const requiredFields = ['unique_number', 'query_category', 'employee_name'];

  for (const field of requiredFields) {
    if (!(field in ticket)) {
      console.error(`Schema mismatch: Missing field "${field}"`);
      return false;
    }
  }

  return true;
};

if (!validateTicketSchema(ticket)) {
  throw new Error('Ticket schema mismatch - migration may have failed');
}
```

### Realtime Subscription Schema Impact

Los Issue Tracker uses Supabase Realtime to notify frontend of ticket changes:

```typescript
// Hook: src/hooks/useTickets.ts
const subscribeToChanges = useCallback(
  (callback: () => void, userEmail?: string, userRole?: string) => {
    const filter = userRole === 'product_support' && userEmail
      ? { event: '*' as const, schema: 'public', table: 'tickets',
          filter: `submitted_by=eq.${userEmail}` }
      : { event: '*' as const, schema: 'public', table: 'tickets' };

    supabase
      .channel('tickets-channel')
      .on('postgres_changes', filter, () => {
        callback();  // Refetch all tickets
      })
      .subscribe();
  },
  []
);
```

**Schema Changes Impact Realtime:**

```sql
-- Migration: Rename column 'status' to 'ticket_status'
-- IMPACT: Realtime will still fire, but OLD schema in payload won't have 'status'

-- BEFORE: Subscription gets { id, status: 'open', ... }
-- AFTER:  Subscription gets { id, ticket_status: 'open', ... }
-- BROKEN: Frontend expects 'status' field!
```

**Safe Migration:**

```sql
-- Step 1: Add new column, keep old
ALTER TABLE tickets ADD COLUMN ticket_status VARCHAR;

-- Step 2: Update Realtime (frontend code change)
// Update subscription to expect either field
const handleRealtimeUpdate = (payload: any) => {
  const status = payload.new.status || payload.new.ticket_status;
  // ...
};

-- Step 3: Backfill new column
UPDATE tickets SET ticket_status = status;

-- Step 4: Drop old column
ALTER TABLE tickets DROP COLUMN status;
```

---

## Frontend-Backend Schema Sync

**The Critical Gap:** TypeScript interfaces must match database schema exactly.

### Example: Field Addition with Schema Drift

**Scenario:** Adding `email_verified` field to tickets.

#### BAD PATTERN (Causes Bugs)

```sql
-- Migration executed successfully
ALTER TABLE tickets ADD COLUMN email_verified BOOLEAN DEFAULT false;
```

```typescript
// Frontend types NOT updated
export interface Ticket {
  id: string;
  ticket_number: number;
  lsq_url: string;
  // ... fields ...
  // MISSING: email_verified
}

// Component uses it
const TicketDetail = ({ ticket }: { ticket: Ticket }) => {
  return (
    <>
      <p>Verified: {ticket.email_verified}</p>  // ❌ Undefined!
    </>
  );
};
```

**Result:** Form displays "Verified: undefined" or crashes at runtime.

#### GOOD PATTERN (Synchronized)

```sql
-- Migration 001: Add email_verified field
ALTER TABLE tickets
  ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_tickets_email_verified
  ON tickets(email_verified);
```

```typescript
// src/types/index.ts - Updated simultaneously
export interface Ticket {
  id: string;
  ticket_number: number;
  lsq_url: string;
  email_verified: boolean;  // ✅ Matches schema
  email_verified_at?: string;
  // ... other fields ...
}

// Component works correctly
const TicketDetail = ({ ticket }: { ticket: Ticket }) => {
  return (
    <p>Verified: {ticket.email_verified ? '✓' : '✗'}</p>  // ✅ Works
  );
};
```

### Handling Optional Fields

```typescript
// Scenario: email_verified is optional during rollout

// Database: Allow NULL during transition
ALTER TABLE tickets ADD COLUMN email_verified BOOLEAN;  // No DEFAULT

// Types: Mark as optional
export interface Ticket {
  email_verified?: boolean;  // Optional
}

// Component handles both old and new data
const getVerificationStatus = (ticket: Ticket): string => {
  if (ticket.email_verified === undefined) {
    return 'Not checked yet';  // Old data format
  }
  return ticket.email_verified ? 'Verified' : 'Not verified';
};

// After backfill complete
// Database: Add NOT NULL constraint
ALTER TABLE tickets ALTER COLUMN email_verified SET NOT NULL;

// Types: Remove optional marker
export interface Ticket {
  email_verified: boolean;  // Now required
}
```

### Form Validation Must Match Schema Constraints

From `Los Issue Tracker`:

```typescript
// useTickets.ts - Create ticket form data
interface CreateTicketData {
  lsq_url: string;        // ← Validated as URL
  trn: string;            // ← Validated as non-empty
  image_urls: string[];   // ← Array of URLs
  description: string;    // ← Text, min length?
  issue_type: string;     // ← One of known types
  submitted_by: string;   // ← Must be valid email (constraint 019)
  query_category?: string;  // ← Optional, but if provided must match enum
}
```

**Corresponding Database Constraints:**

```sql
-- Migration 004: TRN field
ALTER TABLE tickets ADD COLUMN trn VARCHAR(100);  -- Length limit

-- Migration 019: Email validation
ALTER TABLE tickets
  ADD CONSTRAINT check_submitted_by_email_format
    CHECK (is_valid_email(submitted_by)) NOT VALID;

-- No constraint on description length (unlimited TEXT)
-- But component validates max 5000 chars
-- ⚠️ MISMATCH: Type allows any length, frontend limits it
```

**Safe Pattern:**

```typescript
// types/index.ts - document constraints
export interface Ticket {
  // ...

  /** Transaction Reference Number (max 100 chars) */
  trn?: string;           // Matches VARCHAR(100)

  /** Email must match pattern: user@domain.tld */
  submitted_by: string;   // CHECK constraint in DB

  /** Ticket description (unlimited, but UI recommends <5000 chars) */
  description: string;
}

// Form validation
const validateTicketForm = (data: CreateTicketData): string[] => {
  const errors: string[] = [];

  if (!data.trn || data.trn.length > 100) {
    errors.push('TRN must be 1-100 characters');  // Matches VARCHAR(100)
  }

  if (!isValidEmail(data.submitted_by)) {
    errors.push('Invalid email format');  // Matches CHECK constraint
  }

  if (!data.description || data.description.length > 5000) {
    errors.push('Description must be 1-5000 characters');
  }

  return errors;
};
```

### Component Handling of Removed Fields

When deprecating a field:

```typescript
// OLD Type (before deprecation)
export interface Ticket {
  unique_identifier: string;  // Being deprecated
  unique_number: string;      // New replacement
}

// NEW Type (after fields same, migration happening)
export interface Ticket {
  unique_identifier?: string;  // Mark optional
  unique_number: string;       // Now primary
}

// Component updated to use new field
const TicketView = ({ ticket }: { ticket: Ticket }) => {
  // Use new field
  const id = ticket.unique_number;

  // Fallback for old data during migration
  if (!id && ticket.unique_identifier) {
    return <p>Warning: Old ID format. Please refresh.</p>;
  }

  return <p>ID: {id}</p>;
};

// FINAL Type (after cleanup)
export interface Ticket {
  // unique_identifier removed
  unique_number: string;  // Now required
}
```

### Display Components and New/Removed Fields

From Firestore project (backward-compatible attachment display):

```typescript
// Submission interface has BOTH old and new attachment fields
export interface Submission {
  attachmentUrl?: string;     // DEPRECATED
  attachmentDriveId?: string; // DEPRECATED
  attachments?: Attachment[]; // NEW
}

// Display component works with both
const AttachmentDisplay = ({ submission }: { submission: Submission }) => {
  // Prioritize new format, fallback to old
  const attachments = submission.attachments ||
    (submission.attachmentUrl ? [{
      url: submission.attachmentUrl,
      driveId: submission.attachmentDriveId || '',
      fileName: 'Attachment'
    }] : []);

  return (
    <div>
      {attachments.length === 0 ? (
        <p>No attachments</p>
      ) : (
        <ul>
          {attachments.map(att => (
            <li key={att.driveId}>
              <a href={att.url}>{att.fileName}</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

---

## Migration Safety Checklist

Use this checklist for every schema change:

### Pre-Migration (24 hours before)

- [ ] **Schema Review**
  - [ ] All new columns nullable or have defaults
  - [ ] No data type changes without conversion plan
  - [ ] Indexes planned for new query patterns
  - [ ] Constraints validated with sample data

- [ ] **Backward Compatibility**
  - [ ] Application handles missing new fields gracefully
  - [ ] Old application versions still work with new schema
  - [ ] TypeScript interfaces updated
  - [ ] Form validation matches constraints

- [ ] **Risk Assessment**
  - [ ] Will migration lock tables? (check table size)
  - [ ] Estimated execution time < 30 seconds
  - [ ] Rollback script tested (or risk acceptable)
  - [ ] Data backfill query tested on production backup

- [ ] **Communication**
  - [ ] Notify team of maintenance window (if needed)
  - [ ] Document rollback procedure
  - [ ] Alert monitoring configured
  - [ ] On-call engineer available

### Migration Execution

- [ ] **Pre-Check**
  - [ ] Database backup created
  - [ ] Migration script syntax verified
  - [ ] Dry run on staging environment passed
  - [ ] Current database metrics captured (row counts, table size)

- [ ] **Execution**
  - [ ] Begin transaction with `BEGIN;`
  - [ ] Execute migration steps in order
  - [ ] Verification queries pass (count new columns, check constraints)
  - [ ] `COMMIT;` transaction
  - [ ] Verify with `\d tablename` (show table definition)

- [ ] **Sanity Checks**
  - [ ] SELECT sample rows - verify data integrity
  - [ ] INSERT test row - verify defaults and constraints
  - [ ] Query performance - EXPLAIN ANALYZE on common queries
  - [ ] No application errors in logs

### Post-Migration (Next 24 hours)

- [ ] **Monitoring**
  - [ ] Application logs for schema-related errors
  - [ ] Database query performance (pg_stat_statements)
  - [ ] RLS policy errors in audit logs
  - [ ] Real-time subscriptions working (if used)

- [ ] **Verification**
  - [ ] All required fields populated correctly
  - [ ] Constraints enforced (test constraint violations)
  - [ ] Indexes created and usable
  - [ ] No missing data (row counts match expectations)

- [ ] **Application**
  - [ ] Deploy updated TypeScript types
  - [ ] Updated components render correctly
  - [ ] Form validation works
  - [ ] Edge functions/triggers working (if any)

- [ ] **Documentation**
  - [ ] Migration documented in README
  - [ ] Rollback result logged (even if not needed)
  - [ ] Schema changes added to reference docs
  - [ ] Team notified of completion

### If Rollback Needed

- [ ] **Immediate Actions**
  - [ ] Notify team immediately
  - [ ] Identify error from logs
  - [ ] Revert application code to previous version
  - [ ] Execute rollback script in transaction

- [ ] **Investigation**
  - [ ] What went wrong? (data? constraint? performance?)
  - [ ] Could issue be reproduced in staging?
  - [ ] Root cause documented
  - [ ] Fix applied before retry

- [ ] **Retry**
  - [ ] Adjust migration based on findings
  - [ ] Re-test on staging
  - [ ] Plan window for retry
  - [ ] Use different time to avoid user impact

---

## Real Failure Examples

### Example 1: Schema Drift with RLS

**What Happened:**

Migration 006 added RLS policies without updating frontend types. The `allowed_users` table had email-based access control, but frontend assumed all users could see all tickets.

```typescript
// BAD: Frontend didn't know about RLS restrictions
const fetchAllTickets = async () => {
  const { data } = await supabase
    .from('tickets')
    .select('*');  // ← RLS blocks this, but no error UI

  return data || [];  // Silent failure if RLS blocks user
};
```

**Impact:**

- Product support users occasionally saw empty ticket lists
- No error message (RLS silently filtered results)
- Developer assumed data fetch was working
- Debugged for 2 hours before discovering RLS policy issue

**Root Cause:**

- Migration 006 created RLS policies
- Migration 010 tightened policies further
- But frontend never validated permissions
- No test for "user cannot see other users' tickets"

**Fix:**

```typescript
// GOOD: Frontend handles permission errors
const fetchMyTickets = async (userEmail: string) => {
  const { data, error } = await supabase
    .from('tickets')
    .select('*')
    .eq('submitted_by', userEmail);

  if (error?.code === 'PGRST301') {
    // RLS policy denying access
    console.error('Access denied - user not authorized');
    return [];
  }

  return data || [];
};

// GOOD: Test RLS in unit tests
test('Product support can only see own tickets', async () => {
  const { data, error } = await supabase
    .from('tickets')
    .select('*');  // Should be denied for non-admin

  expect(error?.code).toBe('PGRST301');  // RLS policy error
});
```

### Example 2: Type Mismatch After Migration

**What Happened:**

Migration 001 added `unique_number` field (auto-generated as `TKT-123` format). But Form validation used old `ticket_number` (integer) for uniqueness checks.

```typescript
// Migration 001: Add unique_number
ALTER TABLE tickets
  ADD COLUMN unique_number VARCHAR(50),
  ADD CONSTRAINT unique_number_unique UNIQUE (unique_number);

// Frontend code NOT updated:
const validateNewTicket = (ticketNumber: number) => {
  // Validates old ticket_number, not unique_number!
  if (ticketNumber < 1 || ticketNumber > 99999) {
    return 'Invalid ticket number';
  }
};

// Component tries to insert:
const { data } = await supabase
  .from('tickets')
  .insert([{
    ticket_number: 123,  // Accepts any value
    // unique_number: NOT PROVIDED → trigger generates it
    submitted_by: 'user@example.com'
  }]);
```

**Impact:**

- Users entered ticket numbers without validation
- Trigger auto-generated `unique_number` from invalid `ticket_number`
- Google Sheets sync got wrong IDs (`TKT-0`, `TKT-invalid`)
- Support couldn't track tickets by unique_number

**Root Cause:**

- Migration added constraint on new field
- But frontend didn't validate new field
- No test checking constraint is enforced on frontend

**Fix:**

```typescript
// GOOD: Frontend validates fields that have constraints
import { QUERY_CATEGORIES } from '../types';

const validateTicketData = (data: CreateTicketData): string[] => {
  const errors: string[] = [];

  // Validate auto-generated fields have valid source data
  if (!data.ticket_number || data.ticket_number < 1) {
    errors.push('Ticket number required');
  }

  // Validate required Sheets integration fields
  if (!data.query_category) {
    errors.push('Query category required');
  }

  if (!QUERY_CATEGORIES.includes(data.query_category)) {
    errors.push(`Invalid category: ${data.query_category}`);
  }

  if (!isValidEmail(data.submitted_by)) {
    errors.push('Invalid email format');  // CHECK constraint in DB
  }

  return errors;
};

// GOOD: Form rejects invalid data before send
const handleCreateTicket = async (formData: CreateTicketData) => {
  const errors = validateTicketData(formData);

  if (errors.length > 0) {
    setErrorMessage(errors.join('; '));
    return;  // Block submission
  }

  // Only send if validation passes
  const result = await createTicket(formData);
  // ...
};
```

### Example 3: Edge Function Schema Dependency

**What Happened:**

Migration 001 added `query_category`, `sub_category`, and `employee_name` fields. Edge function `sync-to-sheets` depended on these fields existing.

```typescript
// sync-to-sheets edge function
export const handler = async (req: Request) => {
  const { ticket_number } = await req.json();

  const { data: ticket } = await supabaseAdmin
    .from('tickets')
    .select('*')
    .eq('ticket_number', ticket_number)
    .single();

  // Assumes these fields exist from migration 001
  const row = [
    ticket.unique_number,      // ← Migration 001 added
    ticket.query_category,     // ← Migration 001 added
    ticket.employee_name       // ← Migration 001 added
  ];

  // If migration 001 hadn't run:
  // row = [undefined, undefined, undefined]
  // Google Sheets gets empty cells silently
};
```

**Impact:**

- Database had tickets before migration 001 was applied
- Edge function created Google Sheets rows with empty cells
- No error (just silent data loss)
- Took hours to notice data was incomplete

**Root Cause:**

- No validation that required fields exist
- Edge function had no schema version check
- Migration 001 added new columns but didn't backfill old tickets

**Fix:**

```typescript
// GOOD: Edge function validates schema version
export const handler = async (req: Request) => {
  const { ticket_number } = await req.json();

  const { data: ticket } = await supabaseAdmin
    .from('tickets')
    .select('*')
    .eq('ticket_number', ticket_number)
    .single();

  // Validate required fields exist and have values
  const requiredFields = ['unique_number', 'query_category', 'employee_name'];
  const missingFields = requiredFields.filter(
    field => !(field in ticket) || ticket[field] === null
  );

  if (missingFields.length > 0) {
    throw new Error(
      `Schema validation failed: missing ${missingFields.join(', ')}. ` +
      `Database migration may not be complete.`
    );
  }

  // Now safe to use fields
  const row = [
    ticket.unique_number,
    ticket.query_category,
    ticket.employee_name
  ];

  // ... continue
};

// GOOD: Migration 001 explicitly backfills old data
ALTER TABLE tickets
  ADD COLUMN query_category VARCHAR(50);

UPDATE tickets
SET query_category = COALESCE(query_category, issue_type)
WHERE query_category IS NULL;

-- Verify migration success
DO $$
DECLARE
  null_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO null_count
  FROM tickets
  WHERE query_category IS NULL;

  IF null_count > 0 THEN
    RAISE EXCEPTION 'Migration incomplete: % tickets missing query_category', null_count;
  END IF;
END $$;
```

### Example 4: Firestore Collection Structure Change

**What Happened:**

Firestore project added `attachments` array field (migration from single file to multiple files support). But backfill script only ran on new documents.

```typescript
// OLD: Single attachment
const submission: Submission = {
  attachmentUrl: 'https://drive.google.com/file/d/ABC123/view',
  attachmentDriveId: 'ABC123'
};

// NEW: Multiple attachments
const submission: Submission = {
  attachments: [{
    url: 'https://drive.google.com/file/d/ABC123/view',
    driveId: 'ABC123',
    fileName: 'form.pdf'
  }]
};

// Backfill script didn't run for old documents:
// They still had attachmentUrl but not attachments array
```

**Impact:**

- Component renders new documents with array correctly
- Component renders old documents but attachments undefined
- Users uploading attachments to old submissions lost data
- Took 1 week to discover (backfill never completed)

**Root Cause:**

- Backfill script written but not scheduled
- No verification that backfill actually completed
- Type system allowed both old and new formats indefinitely

**Fix:**

```typescript
// GOOD: Explicit backfill with progress tracking
const backfillOldSubmissions = async () => {
  const db = getFirestore();
  let processed = 0;
  let migrated = 0;

  // Find all documents with OLD format
  const query = db.collection('submissions')
    .where('attachments', '==', undefined)
    .where('attachmentUrl', '!=', null);

  const snapshot = await query.get();
  console.log(`Found ${snapshot.docs.length} old-format submissions`);

  if (snapshot.docs.length === 0) {
    console.log('No old submissions to migrate');
    return;
  }

  // Migrate in batches (avoid timeout)
  const batchSize = 100;
  for (let i = 0; i < snapshot.docs.length; i += batchSize) {
    const batch = db.batch();

    snapshot.docs.slice(i, i + batchSize).forEach(doc => {
      const data = doc.data();
      batch.update(doc.ref, {
        attachments: [{
          url: data.attachmentUrl,
          driveId: data.attachmentDriveId || '',
          fileName: 'Migrated Attachment',
          fileSize: 0
        }]
      });
    });

    await batch.commit();
    processed += Math.min(batchSize, snapshot.docs.length - i);
    migrated += Math.min(batchSize, snapshot.docs.length - i);
    console.log(`Migrated ${processed}/${snapshot.docs.length}`);
  }

  // Verify migration completed
  const verifySnapshot = await query.get();
  if (verifySnapshot.docs.length > 0) {
    throw new Error(`Migration incomplete: ${verifySnapshot.docs.length} submissions still using old format`);
  }

  console.log(`✓ Migration complete: ${migrated} submissions migrated`);
};

// GOOD: Type system enforces migration completion
// Once backfill done, make field required to prevent new old-format documents
export interface Submission {
  attachments: Attachment[];  // REQUIRED after backfill
  // attachmentUrl: REMOVED
  // attachmentDriveId: REMOVED
}

// Component no longer needs fallback logic
const AttachmentDisplay = ({ submission }: { submission: Submission }) => {
  // attachments is guaranteed to exist
  return (
    <ul>
      {submission.attachments.map(att => (
        <li key={att.driveId}>
          <a href={att.url}>{att.fileName}</a>
        </li>
      ))}
    </ul>
  );
};
```

---

## Summary

Successful database migrations require:

1. **Layered Approach**: Add nullable → backfill → add constraints → deprecate old
2. **Validation at Every Step**: Verify data before and after each change
3. **Synchronized Updates**: Database schema AND TypeScript types change together
4. **Documentation**: Every constraint should have a comment explaining why
5. **Testing**: Unit tests for schema constraints, integration tests for RLS policies
6. **Monitoring**: 24-hour observation period after deployment
7. **Rollback Plan**: Always know how to undo (and test it first)

The cost of a failed migration (data loss, app downtime, emergency patches) far exceeds the cost of careful planning and conservative changes. When in doubt, choose the slower path.

---

**Last Reviewed:** February 26, 2026
**Reviewed By:** Database Architecture Team
**Status:** Approved for Production Use
