# Supabase & Database Security Patterns

Based on the official Supabase Agent Skills framework, Supabase MCP safety documentation,
and Postgres best practices for AI agents.

**Sources:**
- Supabase Blog: "Postgres Best Practices for AI Agents"
- Supabase Blog: "Defense in Depth for MCP Servers"
- Supabase Agent Skills: github.com/supabase/agent-skills
- Supabase MCP Documentation: supabase.com/docs/guides/getting-started/mcp

---

## CRITICAL SAFETY REMINDER

**This auditor is READ-ONLY. It inspects code patterns — it does NOT execute queries,
modify schemas, or touch live databases. All findings are recommendations.**

**Any fix involving database changes is ALWAYS `requires_review`.**

---

## Detection: Is This a Supabase Project?

### Primary Signals
```bash
# Supabase client library
grep -rn "@supabase/supabase-js" --include="package.json"
grep -rn "createClient.*supabase" --include="*.ts" --include="*.js" --include="*.tsx"
grep -rn "from.*@supabase" --include="*.ts" --include="*.js" --include="*.tsx"

# Supabase CLI / config
ls supabase/config.toml 2>/dev/null
ls supabase/migrations/ 2>/dev/null

# Supabase environment variables
grep -rn "SUPABASE_URL\|SUPABASE_ANON_KEY\|SUPABASE_SERVICE_ROLE" --include="*.env*" --include="*.ts" --include="*.js"
grep -rn "NEXT_PUBLIC_SUPABASE" --include="*.env*" --include="*.ts" --include="*.tsx"
```

### Secondary Signals
```bash
# Supabase auth
grep -rn "supabase\.auth\." --include="*.ts" --include="*.js" --include="*.tsx"

# Supabase storage
grep -rn "supabase\.storage\." --include="*.ts" --include="*.js" --include="*.tsx"

# Supabase realtime
grep -rn "supabase\.channel\|supabase\.from.*on(" --include="*.ts" --include="*.js" --include="*.tsx"

# Supabase Edge Functions
ls supabase/functions/ 2>/dev/null
```

---

## Domain 15: Database Security (Supabase/Postgres)

### 15.1 Service Role Key Exposure (CRITICAL)

The `service_role` key bypasses ALL Row-Level Security. It must NEVER be exposed to browsers or client code.

**Grep Patterns:**
```bash
# Service role key in client-side code
grep -rn "SUPABASE_SERVICE_ROLE\|service_role" --include="*.tsx" --include="*.jsx" --include="*.vue"
grep -rn "service_role" --include="*.ts" --include="*.js" | grep -v "node_modules" | grep -v ".server."

# Service role in environment that gets bundled
grep -rn "NEXT_PUBLIC.*SERVICE_ROLE\|VITE.*SERVICE_ROLE\|REACT_APP.*SERVICE_ROLE" --include="*.env*"

# Direct key value patterns (Supabase service role keys start with eyJ)
grep -rn "eyJ[a-zA-Z0-9_-]\{50,\}" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.env*"
```

**Severity:** Critical (CVSS 9.8)
**CWE:** CWE-798 (Hardcoded Credentials)
**Impact:** Complete database bypass, full data exfiltration, RLS circumvention

**Non-Invasive Fix:** Move to server-only environment variable, ensure not prefixed with NEXT_PUBLIC_ or VITE_

---

### 15.2 Missing Row-Level Security (HIGH)

Tables without RLS are accessible to any authenticated user via the Supabase API.

**Detection:**
```bash
# Check migration files for tables without RLS
grep -rn "CREATE TABLE" --include="*.sql" | grep -v "enable row level security"

# Check for explicit RLS disable
grep -rn "ALTER TABLE.*DISABLE ROW LEVEL SECURITY" --include="*.sql"

# Check for overly permissive policies
grep -rn "USING\s*(true)" --include="*.sql"
grep -rn "WITH CHECK\s*(true)" --include="*.sql"

# Check for FOR ALL policies (should be separate SELECT/INSERT/UPDATE/DELETE)
grep -rn "FOR ALL" --include="*.sql" | grep -i "policy"
```

**Severity:** High (CVSS 8.1)
**CWE:** CWE-862 (Missing Authorization)
**Impact:** Unauthorized data access, data modification

**Recommendation (requires_review):**
- Enable RLS on every table: `ALTER TABLE tablename ENABLE ROW LEVEL SECURITY;`
- Create 4 separate policies per table (SELECT, INSERT, UPDATE, DELETE)
- Use `auth.uid()` in policy conditions
- Index all columns used in RLS policies

---

### 15.3 Insecure Supabase Client Initialization (HIGH)

**Grep Patterns:**
```bash
# Client created with service role key
grep -rn "createClient.*service_role\|createClient.*SERVICE_ROLE" --include="*.ts" --include="*.js" --include="*.tsx"

# Client with auth disabled or autoRefreshToken disabled
grep -rn "autoRefreshToken.*false\|persistSession.*false" --include="*.ts" --include="*.js"

# Client created in client-side component with server key
grep -rn "createClient" --include="*.tsx" --include="*.jsx" --include="*.vue" | grep -v "createBrowserClient\|createServerClient"
```

**Severity:** High (CVSS 7.5)

---

### 15.4 Unsafe Database Queries (SQL Injection via Supabase)

**Grep Patterns:**
```bash
# Raw SQL via Supabase RPC with string interpolation
grep -rn "\.rpc(.*\`\|\.rpc(.*\+\|\.rpc(.*\${" --include="*.ts" --include="*.js" --include="*.tsx"

# Raw SQL via supabase.from().select() with dynamic columns
grep -rn "\.select(\`\|\.select(.*\+\|\.select(.*\${" --include="*.ts" --include="*.js" --include="*.tsx"

# Raw SQL in migration files without parameterization
grep -rn "EXECUTE.*\|\|" --include="*.sql"
grep -rn "format(.*%s" --include="*.sql"

# Direct SQL in Edge Functions
grep -rn "sql\`\|query\(" --include="*.ts" supabase/functions/ 2>/dev/null
```

**Severity:** Critical (CVSS 9.8) if user input reaches raw SQL
**CWE:** CWE-89

---

### 15.5 Supabase Auth Misconfigurations (MEDIUM-HIGH)

**Grep Patterns:**
```bash
# Auth without email confirmation
grep -rn "emailRedirectTo\|email_confirm" --include="*.ts" --include="*.js"

# OAuth without proper redirect validation
grep -rn "signInWithOAuth\|signInWithIdToken" --include="*.ts" --include="*.js" --include="*.tsx"

# Password reset without rate limiting
grep -rn "resetPasswordForEmail" --include="*.ts" --include="*.js" --include="*.tsx"

# Missing auth state check before data access
grep -rn "supabase\.from(" --include="*.tsx" --include="*.jsx" | grep -v "getSession\|getUser\|auth\."
```

---

### 15.6 Storage Security Issues (MEDIUM)

**Grep Patterns:**
```bash
# Public buckets
grep -rn "createBucket.*public.*true\|public.*true.*bucket" --include="*.ts" --include="*.js" --include="*.sql"

# File upload without type validation
grep -rn "\.upload(" --include="*.ts" --include="*.js" --include="*.tsx" | grep -v "contentType\|type\|accept"

# Storage policies (check in migrations)
grep -rn "storage\.objects\|storage\.buckets" --include="*.sql"
```

---

### 15.7 Realtime Channel Security (MEDIUM)

**Grep Patterns:**
```bash
# Subscribing to all changes without filtering
grep -rn "\.channel(\|\.on('postgres_changes'" --include="*.ts" --include="*.js" --include="*.tsx"

# Broadcasting sensitive data
grep -rn "\.send(\|broadcast(" --include="*.ts" --include="*.js" --include="*.tsx"
```

---

### 15.8 Edge Function Security (MEDIUM)

**Grep Patterns:**
```bash
# CORS misconfiguration in Edge Functions
grep -rn "Access-Control-Allow-Origin.*\*" supabase/functions/ 2>/dev/null

# Missing auth verification in Edge Functions
grep -rn "serve(" supabase/functions/ 2>/dev/null | grep -v "Authorization\|getUser\|auth"

# Environment variable exposure
grep -rn "Deno\.env\.get" supabase/functions/ 2>/dev/null
```

---

### 15.9 Database Connection Security (HIGH)

**Grep Patterns:**
```bash
# Direct connection strings in code
grep -rn "postgresql://\|postgres://\|pg://" --include="*.ts" --include="*.js" --include="*.py" --include="*.env*"

# Connection without SSL
grep -rn "sslmode.*disable\|ssl.*false" --include="*.ts" --include="*.js" --include="*.py"

# Connection pooling issues
grep -rn "max.*connections\|pool.*size\|connectionLimit" --include="*.ts" --include="*.js" --include="*.py"
```

---

### 15.10 Migration Safety (INFO — Documentation)

**Check migration files for:**
```bash
# Destructive operations
grep -rn "DROP TABLE\|DROP COLUMN\|TRUNCATE\|DROP SCHEMA" --include="*.sql" supabase/migrations/ 2>/dev/null

# Missing transaction wrapping
grep -rn "BEGIN\|COMMIT" --include="*.sql" supabase/migrations/ 2>/dev/null

# Missing comments on destructive operations
# (Manual review: every DROP/TRUNCATE should have a comment explaining why)

# Large ALTER TABLE operations (check file size)
find supabase/migrations/ -name "*.sql" -size +10k 2>/dev/null
```

---

## Non-Invasive Fix Patterns for Supabase

### Service Role Key → Server-Only

```diff
# .env.local
- NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY=eyJ...
+ SUPABASE_SERVICE_ROLE_KEY=eyJ...
# (Remove NEXT_PUBLIC_ prefix so it's server-only)
```

**Checklist:** `requires_review` — Requires verifying no client code depends on this key

### Missing RLS → Policy Addition

```sql
-- RECOMMENDATION ONLY (requires_review)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own documents"
  ON public.documents FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents"
  ON public.documents FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

**Checklist:** ALWAYS `requires_review` — Database schema changes

### Raw SQL → Parameterized RPC

```diff
- const { data } = await supabase.rpc('search_users', { query: `%${input}%` })
+ const { data } = await supabase.rpc('search_users', { query: input })
# (And update the SQL function to handle LIKE pattern safely)
```

**Checklist:** `requires_review` — Requires verifying RPC function contract

---

## Severity Classification for Database Issues

| Pattern | Severity | Auto-Apply? |
|---------|----------|-------------|
| Service role key in client code | Critical | NO — requires_review |
| SQL injection via RPC/raw query | Critical | YES (parameterization only) |
| Missing RLS on table with user data | High | NO — requires_review |
| Direct connection string in code | High | YES (move to env var) |
| `FOR ALL` RLS policies | Medium | NO — requires_review |
| Public storage bucket without policy | Medium | NO — requires_review |
| Missing auth check before query | Medium | YES (add guard) |
| Edge function CORS wildcard | Medium | YES (config fix) |
| Missing SSL on connection | Low | YES (config addition) |
| Migration without comments | Info | NO — documentation only |
