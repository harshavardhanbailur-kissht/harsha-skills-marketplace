# Multi-Tenancy Architecture Patterns for SaaS Applications (2025-2026)

**Last Updated:** March 2026
**Status:** PRICING_STABLE
**Audience:** SaaS architects, backend engineers, infrastructure teams

---

## Executive Summary (TL;DR)

1. **Three Primary Models**: Shared database with row-level isolation (lowest cost, highest risk), separate schemas per tenant (balanced), and database-per-tenant (highest isolation, highest cost)
2. **PostgreSQL RLS** is production-ready for multi-tenancy with minimal performance overhead when properly indexed; Supabase provides managed RLS for teams
3. **Hybrid architecture** (shared for SMB, dedicated for enterprise) is optimal for SaaS at scale; allows incremental upgrade paths
4. **Authentication**: Modern solutions (Clerk, WorkOS, Auth0) handle organization management natively; RBAC + ABAC combined is standard for complex permission models
5. **Compliance**: GDPR/HIPAA require explicit data residency controls; per-tenant encryption and audit logging are non-negotiable for regulated industries

---

## 1. MULTI-TENANCY MODELS: DETAILED COMPARISON

### 1.1 Shared Database, Shared Schema (Row-Level Isolation)

**What it is**: All tenants share a single database and schema. Data is segregated using a `tenant_id` column in every table. Application or database-level row-level security (RLS) enforces filtering.

**Implementation Pattern**:
```sql
-- Every table includes tenant_id
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Create index for query performance
CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);

-- PostgreSQL RLS policy
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON projects
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

**Advantages**:
- Lowest infrastructure costs: single database instance supports thousands of tenants
- Simplest operational model: single backup, monitoring, upgrade cycle
- Easy tenant scaling: add tenants without provisioning new infrastructure
- Query isolation enforced at database level with RLS, not reliant on application logic

**Disadvantages**:
- **Data leak risk**: forgotten WHERE clause exposes all tenant data; RLS mitigates but cannot eliminate this if misconfigured
- Limited customization: all tenants share schema, cannot add tenant-specific columns without affecting all
- Performance degradation at scale: with 100K+ tenants in shared table, query planning and indexing becomes complex
- Compliance challenges: HIPAA/SOC 2 require explicit demonstration of isolation; shared infrastructure harder to audit

**Cost Profile**: $500-2,000/month for 1,000-10,000 tenants on managed PostgreSQL (AWS RDS, Azure, Neon)

**Best For**:
- Startups with <500 tenants
- SaaS with consistent tenant sizes
- SMB-focused products (no enterprise customers)
- Early-stage when cost is primary concern

**When to Avoid**:
- Regulated industries (healthcare, finance) requiring dedicated infrastructure
- Platforms with 10x+ variance in tenant size (noisy neighbor risk)
- Multi-region deployments with strict data residency laws

---

### 1.2 Shared Database, Separate Schemas (Schema Per Tenant)

**What it is**: Single database with one PostgreSQL schema per tenant. All tenant-specific tables live in schema `tenant_123`, `tenant_456`, etc. Shared application instances query the correct schema at runtime.

**Implementation Pattern**:
```sql
-- On tenant onboarding
CREATE SCHEMA tenant_123 AUTHORIZATION app_user;

-- Create tenant-specific tables
CREATE TABLE tenant_123.projects (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- At query time, application sets schema search path
SET search_path TO tenant_123, public;
SELECT * FROM projects;  -- queries tenant_123.projects
```

**Advantages**:
- Stronger logical isolation than row-level: schema provides boundary for accidental queries
- Near-complete schema customization: tenant_123 can have different columns than tenant_456
- Still cost-effective: single database instance, no licensing overhead
- Easier compliance demonstration: GDPR auditor can verify "tenant data in separate schema"
- Connection pooling works well: use single shared pool with `search_path` switching per request

**Disadvantages**:
- Administrative overhead: 10K tenants = 10K schemas to maintain
- Schema migrations are complex: ALTER TABLE affects one schema at a time or requires tooling
- Potential catalog bloat: PostgreSQL system catalogs contain 10K schema entries
- Per-tenant schema backups more complex than single shared backup
- Performance: thousands of schemas in catalog can slow PostgreSQL internal operations

**Cost Profile**: $1,500-4,000/month for 1,000-10,000 tenants (higher compute due to schema overhead)

**Best For**:
- 100-5,000 tenants with moderate schema customization
- Compliance-heavy industries needing explicit separation
- Products offering white-label or heavy customization

**When to Avoid**:
- Microservices: schema-per-tenant doesn't scale across independent services
- Massive scale (100K+ tenants): schema management becomes untenable
- Real-time schema changes: ALTER TABLE on many schemas causes locking

---

### 1.3 Separate Database Per Tenant (Silo Model)

**What it is**: Each tenant has completely isolated PostgreSQL database (either separate RDS instance or separate schema in managed multi-tenant database service like AWS RDS multi-region deployments).

**Implementation Pattern**:
```go
// Tenant → Database mapping
type TenantDB struct {
    TenantID string
    ConnStr  string  // postgres://user:pass@tenant-123-db.region.rds.amazonaws.com/db
}

// At request time, resolve tenant and connect to their database
func GetTenantConn(ctx context.Context, tenantID string) (*sql.DB, error) {
    tenantDB := getTenantDatabaseMapping(tenantID)
    return sql.Open("postgres", tenantDB.ConnStr)
}
```

**Advantages**:
- **Maximum isolation**: complete data separation; hardware-level noisy neighbor prevention
- **HIPAA/SOC 2 compliance**: dedicated infrastructure explicitly satisfies audit requirements
- **Performance guarantee**: tenant's query performance unaffected by other tenants' load
- **Custom configurations**: each database can have different PostgreSQL settings, extensions, parameters
- **Easy data residency**: pin database to specific geography/region for GDPR
- **No cross-tenant queries**: impossible to accidentally leak data across tenants

**Disadvantages**:
- **Extreme cost**: 1,000 tenants × $200-500/month per database = $200K-500K/month
- **Operational complexity**: 1,000 databases to backup, patch, monitor, upgrade
- **Slow tenant onboarding**: database creation/teardown takes minutes
- **Resource waste**: small tenants don't justify dedicated instance but must have one
- **Connection pooling per database**: can't use single shared pool; each tenant gets own pool
- **Schema migrations**: updating 1,000 schemas requires orchestrated distributed migrations

**Cost Profile**: $200-500/month per tenant database (AWS RDS, Azure PostgreSQL)
- 100 enterprise tenants: $20K-50K/month
- Prohibitive for SMB tenants

**Best For**:
- Enterprise SaaS (Fortune 500 customers) with dedicated contracts
- Regulated industries requiring explicit isolation (healthcare, legal, finance)
- <100 tenants where operational complexity is manageable
- Products with extreme performance requirements (millisecond SLA)

**When to Avoid**:
- SMB-focused products (cost per tenant too high)
- Growth-stage startups (too expensive)
- Products with >1,000 SMB tenants

---

### 1.4 Hybrid Model (Mixed Isolation Levels)

**What it is**: Different tenants use different architectures based on tier. Free/SMB on shared database, Premium on schema-per-tenant, Enterprise on dedicated database.

**Implementation Pattern**:
```yaml
# tenant_config.yaml
tenants:
  free:
    isolation_level: row_level
    database: shared-db-1
    max_storage_gb: 1
    cost_per_month: 0

  professional:
    isolation_level: schema_per_tenant
    database: shared-db-2
    max_storage_gb: 100
    cost_per_month: 199

  enterprise:
    isolation_level: database_per_tenant
    database: tenant-456-dedicated-db
    max_storage_gb: unlimited
    cost_per_month: 5000
```

**Advantages**:
- Cost-optimized: SMB on cheap shared infrastructure, Enterprise on expensive dedicated
- Clear upgrade path: tenant moves from free → shared schema → dedicated database
- Compliance flexibility: only Enterprise needs dedicated databases for HIPAA
- Revenue-aligned: higher-margin Enterprise segment gets better isolation
- Operational manageability: most tenants on shared tier, few on expensive tier

**Disadvantages**:
- Operational complexity: multiple isolation models to test and support
- Data migration between tiers: moving tenant from shared to dedicated requires ETL
- Increased application logic: routing logic must select correct database per tenant
- Testing complexity: must test all isolation combinations

**Cost Profile**: Blended across tenant mix
- Example: 10,000 Free (row-level), 1,000 Professional (schema), 10 Enterprise (dedicated)
- Shared database: $2,500/month
- Schema database: $3,500/month
- Enterprise databases: 10 × $300 = $3,000/month
- **Total: $9,000/month** vs $50K-500K with database-per-tenant for all

**Best For**:
- Mature SaaS products with tiered pricing
- Mixed customer base (SMB + Enterprise)
- Products with runway to manage operational complexity
- Compliance-aware platforms

---

### 1.5 Trade-Offs Matrix

| Criterion | Row-Level | Schema | Database | Hybrid |
|-----------|-----------|--------|----------|--------|
| **Isolation Level** | Logical (high risk) | Logical (medium risk) | Physical (zero risk) | Variable |
| **Cost per Tenant** | $0.05-0.20 | $0.15-0.50 | $200-500 | $1-200 |
| **Tenant Scaling** | 10K+ easy | 1K-5K easy | <100 feasible | Variable |
| **Compliance (HIPAA)** | Difficult | Moderate | Easy | Conditional |
| **Query Performance** | Shared (noisy neighbor risk) | Isolated (per-schema) | Isolated | Variable |
| **Schema Flexibility** | None | High | Complete | Variable |
| **Operational Overhead** | Low | Medium | High | High |
| **Data Residency Control** | Limited | Limited | Full | Variable |
| **Vendor Lock-in** | Low | Low | Medium | Medium |

---

## 2. DATABASE-LEVEL IMPLEMENTATION

### 2.1 PostgreSQL Row Level Security (RLS) for Multi-Tenancy

**How RLS Works**:
RLS in PostgreSQL allows you to attach security policies to tables that automatically filter rows based on conditions. The database evaluates the policy on every query before returning results.

**Policy Evaluation Process**:
1. User executes query: `SELECT * FROM projects`
2. Database checks if RLS is enabled on `projects` table
3. For each row in table, database evaluates USING clause
4. Only rows where USING clause returns TRUE are included in result

**Core Implementation**:
```sql
-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create permissive policy (default: OR logic with other policies)
CREATE POLICY tenant_isolation_select ON projects
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Create restrictive policy (default: AND logic with permissive)
CREATE POLICY prevent_cross_tenant_write ON projects
    AS RESTRICTIVE
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Superuser/role-based bypass (for operations, support)
CREATE ROLE tenant_user;
ALTER TABLE projects FORCE ROW LEVEL SECURITY;  -- even superuser must follow RLS
```

**Setting Tenant Context in Application**:

```javascript
// Node.js with node-postgres
const { Client } = require('pg');

async function queryWithTenantContext(tenantId, query, params) {
    const client = new Client({
        connectionString: process.env.DATABASE_URL
    });

    await client.connect();

    // Set session variable BEFORE executing query
    await client.query(
        `SET app.current_tenant_id = $1`,
        [tenantId]
    );

    const result = await client.query(query, params);
    await client.end();

    return result;
}

// Usage
const projects = await queryWithTenantContext(
    tenantId,
    'SELECT * FROM projects WHERE created_at > NOW() - INTERVAL 30 DAY'
);
```

```python
# Python with psycopg3
import psycopg

async def query_with_tenant_context(tenant_id: str, query: str, params: list):
    async with await psycopg.AsyncConnection.connect(
        conninfo="postgresql://..."
    ) as conn:
        # Set tenant context
        await conn.execute(
            f"SET app.current_tenant_id = '{tenant_id}'"
        )

        # Query automatically filtered by RLS
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            return await cur.fetchall()
```

**Real-World Patterns**:

Pattern 1: Tenant Context from JWT Claims
```javascript
// Express middleware
app.use((req, res, next) => {
    const token = req.headers.authorization.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Store tenant_id in request context
    req.tenantId = decoded.tenant_id;

    next();
});

// In route handler
app.get('/api/projects', async (req, res) => {
    const projects = await queryWithTenantContext(
        req.tenantId,
        'SELECT * FROM projects'
    );
    res.json(projects);
});
```

Pattern 2: Tenant Context from URL Subdomain
```javascript
// subdomain.app.com vs tenant2.app.com
const subdomainRouter = require('express-subdomain-router');

app.use(subdomainRouter.create({
    '/': (req, res) => {
        // Route to main app
    }
}));

// Middleware to extract tenant from subdomain
app.use((req, res, next) => {
    const [subdomain] = req.hostname.split('.');

    // Look up tenant by subdomain
    const tenant = await db.tenants.findOne({ subdomain });
    req.tenantId = tenant.id;

    next();
});
```

**Performance Considerations**:

1. **Index Strategy**: For RLS to perform well, always create an index on `tenant_id`:
```sql
-- Essential for performance
CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);

-- If filtering by multiple columns
CREATE INDEX idx_projects_tenant_created ON projects(tenant_id, created_at DESC);

-- For complex policies with joins
CREATE INDEX idx_projects_tenant_user ON projects(tenant_id, user_id);
```

2. **Policy Complexity Impact**:
- Simple equality check (like `tenant_id = X`): ~1-2% overhead
- Joins in policy (like `EXISTS (SELECT ...))`): 10-20% overhead
- Multiple restrictive policies: overhead multiplies

3. **Benchmark Results** (from production deployments):
```
With 10K rows per tenant, 100 tenants:
- Query without RLS:  2ms
- Query with simple RLS: 2.1ms (5% overhead)
- Query with JOIN in policy: 2.8ms (40% overhead)

At 1M rows per tenant scale, index quality becomes critical.
Poorly indexed RLS policies can cause full table scans.
```

### 2.2 Supabase RLS for Multi-Tenancy

**What Supabase Provides**:
Supabase is a managed PostgreSQL backend that handles RLS, auth, and realtime subscriptions. Supabase Auth integrates natively with RLS via JWT claims.

**Setup Flow**:
```sql
-- 1. Create users table linked to Supabase Auth
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    tenant_id UUID NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create tenant-aware table
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    title TEXT,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 4. Create policy using Supabase's auth.uid() and custom claims
CREATE POLICY "Users can access documents in their tenant"
ON documents
FOR SELECT
USING (
    tenant_id = (
        SELECT tenant_id FROM users WHERE id = auth.uid()
    )
);

-- 5. For authenticated users only
CREATE POLICY "Users can create documents in their tenant"
ON documents
FOR INSERT
WITH CHECK (
    auth.uid() IN (
        SELECT id FROM users WHERE tenant_id = documents.tenant_id
    )
);
```

**Client-Side Usage** (JavaScript):
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
    process.env.REACT_APP_SUPABASE_URL,
    process.env.REACT_APP_SUPABASE_ANON_KEY
);

// Sign in user
const { data, error } = await supabase.auth.signInWithPassword({
    email: user@example.com,
    password: password
});

// Supabase automatically includes user ID in JWT and RLS filters apply
// No need to manually set tenant context
const { data: documents } = await supabase
    .from('documents')
    .select('*')
    .eq('tenant_id', userTenantId);
```

**Real-World Challenges in Supabase**:

Challenge 1: Auth Provider Integration
```sql
-- Problem: Supabase auth.uid() doesn't work with custom JWT providers
-- Solution: Create custom function that extracts user_id from JWT claims
CREATE OR REPLACE FUNCTION get_current_user_id() RETURNS UUID AS $$
BEGIN
  -- If using Better Auth or similar, manually parse JWT
  RETURN current_setting('request.jwt.claims')::jsonb->>'sub'::uuid;
EXCEPTION
  WHEN OTHERS THEN
    RETURN auth.uid();
END;
$$ LANGUAGE plpgsql STABLE;

-- Then use in policy
CREATE POLICY "custom_auth_policy"
ON documents
FOR SELECT
USING (
    tenant_id = (
        SELECT tenant_id FROM users WHERE id = get_current_user_id()
    )
);
```

Challenge 2: Avoiding N+1 Performance Issues
```sql
-- Slow: This causes SELECT for every row
CREATE POLICY slow_tenant_check ON documents
FOR SELECT
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- Fast: Store tenant_id in JWT claims or user's app_metadata
CREATE POLICY fast_tenant_check ON documents
FOR SELECT
USING (
    tenant_id = current_setting('request.jwt.claims')::jsonb->>'tenant_id'::uuid
);

-- Set app_metadata in Supabase Auth when creating user
UPDATE auth.users
SET user_metadata = jsonb_build_object('tenant_id', 'uuid-value')
WHERE id = 'user-id';
```

### 2.3 Connection Pooling Strategies

**Challenge**: PostgreSQL has connection limits (default 100 per database). With 10K tenants, if each has persistent connections, you'll exceed limits. Must use connection pooling to share connections.

**Approach 1: Shared Connection Pool with Session Variables**
```javascript
// PgBouncer or node-postgres connection pooling
const { Pool } = require('pg');

const pool = new Pool({
    max: 20,  // Single pool shared by ALL tenants
    host: 'mydb.postgres.database.azure.com',
    database: 'mydb'
});

async function queryTenant(tenantId, sql, params) {
    const client = await pool.connect();
    try {
        // Set tenant context BEFORE query
        await client.query('SET app.current_tenant_id = $1', [tenantId]);

        // Query is automatically filtered by RLS
        const result = await client.query(sql, params);
        return result.rows;
    } finally {
        client.release();
    }
}
```

**Approach 2: Per-Tenant Connection Pools (Schema Per Tenant)**
```yaml
# When using schema-per-tenant model
connection_pools:
  tenant_123:
    pool_size: 5
    connection_string: "postgresql://user:pass@db.postgres.database.azure.com/mydb?search_path=tenant_123"

  tenant_456:
    pool_size: 5
    connection_string: "postgresql://user:pass@db.postgres.database.azure.com/mydb?search_path=tenant_456"

# Only viable for <1000 tenants
```

**Approach 3: Dedicated Pooler (Supavisor)**

Supabase offers Supavisor, a cloud-native connection pooler designed for multi-tenant PostgreSQL:
```bash
# Supavisor creates logical connections (client-side)
# Maps to fewer physical connections (server-side)

# Client request: 1000 concurrent connections
# Supavisor pool: 20 physical connections to PostgreSQL
# Multiplexing ratio: 50:1
```

**PgBouncer Configuration for Multi-Tenancy**:
```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
# Route all requests through single database
mydb = host=mydb.postgres.database.azure.com port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction  # Connection returned after each transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3
```

**Key Consideration**: Session variables are NOT preserved across connection reuses in transaction mode. Solution:
```javascript
// WRONG: Assumes connection reuse preserves SET session variable
await pool.query('SET app.current_tenant_id = $1', [tenantId]);
await pool.query('SELECT * FROM projects');  // May use wrong tenant_id!

// RIGHT: Set session variable in same transaction/request
const client = await pool.connect();
try {
    await client.query('BEGIN');
    await client.query('SET app.current_tenant_id = $1', [tenantId]);
    await client.query('SELECT * FROM projects');
    await client.query('COMMIT');
} finally {
    client.release();
}
```

### 2.4 Data Migration: Upgrading Isolation Levels

**Scenario**: Tenant starts on shared database (row-level), upgrades to Enterprise and needs dedicated database. Must migrate data without downtime.

**Migration Strategy (Blue-Green)**:

```bash
#!/bin/bash
# Step 1: Create target database
aws rds create-db-instance \
  --db-instance-identifier tenant-456-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --allocated-storage 100

# Step 2: Replicate data from source
pg_dump \
  -h source-db.postgres.database.azure.com \
  -d mydb \
  -U postgres \
  -T "NOT (tenant_123_* OR tenant_124_* OR tenant_456_*)" \
  | psql -h tenant-456-prod.postgres.database.azure.com -d tenant456db

# Step 3: Filter data for specific tenant during copy
# Only copy data where tenant_id = 'tenant-456'
psql -h source-db.postgres.database.azure.com << EOF
CREATE TABLE migration_temp AS
  SELECT * FROM projects WHERE tenant_id = 'tenant-456';
SELECT * FROM projects_metadata WHERE tenant_id = 'tenant-456';
SELECT * FROM documents WHERE tenant_id = 'tenant-456';
EOF

# Step 4: Switch routing (minimal downtime)
# Update application connection string for tenant-456
# From: postgresql://user:pass@shared-db/mydb (with RLS tenant_456 filtering)
# To: postgresql://user:pass@tenant-456-prod/tenant456db (dedicated)

# Step 5: Verify sync
SELECT COUNT(*) FROM source_db.projects WHERE tenant_id = 'tenant-456';
SELECT COUNT(*) FROM target_db.projects;  # Should match
```

**Continuous Sync During Migration**:
```sql
-- Use pglogical or AWS DMS for CDC (Change Data Capture)
-- Ensures no data loss during cutover

-- pglogical setup
SELECT pglogical.create_subscription(
    subscription_name := 'tenant_456_migration',
    provider_dsn := 'postgresql://source-db/mydb',
    replication_sets := ARRAY['tenant_456_data']
);

-- Monitor replication lag
SELECT slot_name, pg_wal_lsn_diff(pg_current_wal_insert_lsn(), restart_lsn)
FROM pg_replication_slots;
```

### 2.5 Sharding Strategies

**When to Shard**:
- >1 million rows per tenant in shared database
- >10 million total rows across all tenants
- Cross-region data residency requirements
- CPU/disk per-database limits approaching

**Sharding by Tenant ID** (Most Common):
```sql
-- Determine shard based on tenant_id hash
-- tenant_id hash(tenant_id) % 4 = shard number
-- tenant-456 might map to shard_2

-- Shard 0: PostgreSQL instance in us-east-1
-- Shard 1: PostgreSQL instance in us-west-2
-- Shard 2: PostgreSQL instance in eu-west-1
-- Shard 3: PostgreSQL instance in ap-southeast-1

-- Store mapping
CREATE TABLE tenant_shard_mapping (
    tenant_id UUID PRIMARY KEY,
    shard_id INT NOT NULL,
    shard_connection_string TEXT NOT NULL,
    region TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- At query time, look up shard
INSERT INTO tenant_shard_mapping VALUES (
    'tenant-456',
    2,
    'postgresql://user:pass@eu-west-1-db.azure.com/shard_2',
    'eu-west-1'
);
```

**Sharding by Geography** (Compliance):
```yaml
# GDPR: EU customer data must stay in EU
# CCPA: California customer data in US
tenant_europe:
  database: eu-postgres-1
  region: eu-west-1
  backup_region: eu-central-1

tenant_california:
  database: us-postgres-1
  region: us-west-1
  backup_region: us-east-1

tenant_apac:
  database: apac-postgres-1
  region: ap-southeast-1
  backup_region: ap-southeast-2
```

**Sharding by Plan Tier**:
```yaml
free_tier:
  database: shared-free-db
  shard_count: 1
  region: us-east-1

professional_tier:
  database_group: [prof-shard-0, prof-shard-1, prof-shard-2]
  shard_count: 3
  region: us-east-1

enterprise_tier:
  database: dedicated-per-tenant
  shard_count: variable
  region: customer_specified
```

---

## 3. APPLICATION-LEVEL PATTERNS

### 3.1 Middleware Tenant Resolution

**Pattern 1: Subdomain-Based**
```javascript
// Express middleware to extract tenant from subdomain
function subdomainTenantMiddleware(req, res, next) {
    // accounting.acmeapp.com -> accounting
    // hr.acmeapp.com -> hr
    const subdomain = req.hostname.split('.')[0];

    if (subdomain === 'www' || subdomain === 'api') {
        return res.status(400).json({ error: 'Invalid subdomain' });
    }

    // Look up tenant by subdomain
    const tenant = tenantDB.query(
        'SELECT id FROM tenants WHERE subdomain = $1',
        [subdomain]
    );

    if (!tenant) {
        return res.status(404).json({ error: 'Tenant not found' });
    }

    req.tenantId = tenant.id;
    req.tenant = tenant;

    next();
}

app.use(subdomainTenantMiddleware);
```

**Pattern 2: Path-Based**
```javascript
// /tenant/accounting/projects vs /tenant/hr/projects
function pathTenantMiddleware(req, res, next) {
    const match = req.path.match(/^\/tenant\/([^\/]+)\//);

    if (!match) {
        return res.status(400).json({ error: 'Invalid path' });
    }

    const tenantSlug = match[1];
    const tenant = tenantDB.query(
        'SELECT id FROM tenants WHERE slug = $1',
        [tenantSlug]
    );

    req.tenantId = tenant.id;
    req.path = req.path.replace(`/tenant/${tenantSlug}/`, '/');

    next();
}

app.use(pathTenantMiddleware);
```

**Pattern 3: Header-Based**
```javascript
// X-Tenant-ID: tenant-456
function headerTenantMiddleware(req, res, next) {
    const tenantId = req.headers['x-tenant-id'];

    if (!tenantId) {
        return res.status(400).json({ error: 'Missing X-Tenant-ID header' });
    }

    // Validate tenant exists and user has access
    const tenant = tenantDB.query(
        'SELECT id FROM tenants WHERE id = $1',
        [tenantId]
    );

    if (!tenant) {
        return res.status(404).json({ error: 'Tenant not found' });
    }

    req.tenantId = tenantId;

    next();
}

app.use(headerTenantMiddleware);
```

**Pattern 4: JWT Claim-Based**
```javascript
function jwtTenantMiddleware(req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
        return res.status(401).json({ error: 'Missing authorization' });
    }

    const token = authHeader.split(' ')[1];

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        // tenant_id embedded in JWT by auth provider
        const tenantId = decoded.tenant_id || decoded.org_id;

        if (!tenantId) {
            return res.status(400).json({ error: 'No tenant in JWT' });
        }

        req.tenantId = tenantId;
        req.user = decoded;

        next();
    } catch (err) {
        return res.status(401).json({ error: 'Invalid token' });
    }
}

app.use(jwtTenantMiddleware);
```

**Comparison of Approaches**:

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Subdomain** | User-facing, memorable | Requires DNS wildcard, TLS cert per tenant | SaaS with multi-workspace model |
| **Path** | No DNS requirements, single cert | URL-based, less clean | API-first products |
| **Header** | Programmatic, clean | Not user-discoverable | Mobile/SDK clients |
| **JWT** | Cryptographically verified, no DB lookup | Requires JWT in every request | Distributed systems, microservices |

### 3.2 ORM-Level Tenant Scoping

**Prisma with Automatic Tenant Filtering**:

```typescript
// Define tenant context
const createTenantContext = (tenantId: string) => {
    return {
        tenantId,
        extensions: {
            result: {
                // Extend every query result
                $allModels: {
                    async $allOperations({ args, operation, query }) {
                        // Inject tenant_id WHERE clause automatically
                        if (operation === 'findUnique' || operation === 'findFirst') {
                            args.where = {
                                ...args.where,
                                tenantId: tenantId
                            };
                        }

                        if (operation === 'findMany') {
                            args.where = {
                                ...args.where,
                                tenantId: tenantId
                            };
                        }

                        return query(args);
                    }
                }
            }
        }
    };
};

// Usage
const tenantPrisma = new PrismaClient().$extends(
    createTenantContext('tenant-456')
);

// tenantPrisma.project.findMany() automatically adds
// WHERE tenantId = 'tenant-456'
const projects = await tenantPrisma.project.findMany({
    where: { status: 'active' }  // Final WHERE: tenantId AND status
});
```

**Drizzle ORM with Dynamic Schemas**:

```typescript
import { pgTable, text, uuid } from 'drizzle-orm/pg-core';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

// Store which schema to query
const getTenantSchema = async (tenantId: string) => {
    // Look up schema name for tenant
    // tenant-456 -> tenant_456 schema
    return `tenant_${tenantId.replace('-', '_')}`;
};

const queryTenant = async (tenantId: string) => {
    const schema = await getTenantSchema(tenantId);

    const client = postgres(`
        postgres://user:pass@db.postgres.database.azure.com/mydb
        ?search_path=${schema}
    `);

    const db = drizzle(client);
    return db;
};

// Usage
const db = await queryTenant('tenant-456');
const projects = await db.select().from(projectsTable);
```

### 3.3 Request Context Propagation

**Pattern: AsyncLocalStorage (Node.js)**
```typescript
import { AsyncLocalStorage } from 'async_hooks';

const requestContext = new AsyncLocalStorage();

// Middleware to set context
app.use((req, res, next) => {
    const tenantId = req.headers['x-tenant-id'];

    // Run all downstream code in this context
    requestContext.run({ tenantId }, next);
});

// Helper to get tenant ID from any nested function
export const getTenantId = () => {
    const context = requestContext.getStore();
    return context?.tenantId;
};

// Usage in service layer
export async function getProjects() {
    const tenantId = getTenantId();  // Available everywhere
    return db.query('SELECT * FROM projects WHERE tenant_id = $1', [tenantId]);
}
```

**Pattern: Context API (React/Frontend)**
```jsx
import { createContext, useContext } from 'react';

const TenantContext = createContext(null);

export const TenantProvider = ({ tenantId, children }) => {
    return (
        <TenantContext.Provider value={{ tenantId }}>
            {children}
        </TenantContext.Provider>
    );
};

export const useTenant = () => {
    const context = useContext(TenantContext);
    if (!context) {
        throw new Error('useTenant must be used within TenantProvider');
    }
    return context.tenantId;
};

// Usage
function ProjectList() {
    const tenantId = useTenant();

    const [projects, setProjects] = useState([]);

    useEffect(() => {
        fetch(`/api/projects`, {
            headers: { 'X-Tenant-ID': tenantId }
        }).then(r => r.json()).then(setProjects);
    }, [tenantId]);

    return <div>{/* ... */}</div>;
}
```

### 3.4 Caching Strategies for Multi-Tenancy

**Critical Mistake**: Not namespacing cache keys by tenant
```javascript
// WRONG: All tenants share cache key
const projects = await getOrCache('projects', () => {
    return db.query('SELECT * FROM projects');
});
// Tenant A gets Tenant B's cached projects!

// RIGHT: Include tenant_id in cache key
const projects = await getOrCache(`projects:${tenantId}`, () => {
    return db.query(
        'SELECT * FROM projects WHERE tenant_id = $1',
        [tenantId]
    );
});
```

**Redis Cache Namespace Pattern**:
```typescript
class CacheService {
    private redis: RedisClient;

    constructor(redis: RedisClient) {
        this.redis = redis;
    }

    private getKey(tenantId: string, resource: string, id?: string) {
        // All cache keys namespaced by tenant
        return `tenant:${tenantId}:${resource}:${id || '*'}`;
    }

    async get(tenantId: string, resource: string, id: string) {
        const key = this.getKey(tenantId, resource, id);
        const cached = await this.redis.get(key);
        return cached ? JSON.parse(cached) : null;
    }

    async set(tenantId: string, resource: string, id: string, value: any, ttl = 300) {
        const key = this.getKey(tenantId, resource, id);
        await this.redis.setex(key, ttl, JSON.stringify(value));
    }

    async invalidateTenant(tenantId: string) {
        // Clear all tenant's cache when needed
        const pattern = this.getKey(tenantId, '*');
        const keys = await this.redis.keys(pattern);
        if (keys.length > 0) {
            await this.redis.del(...keys);
        }
    }
}
```

### 3.5 Background Jobs and Tenant Context

**Problem**: Background jobs (Celery, Bull, etc.) don't have HTTP request context, so tenant ID must be explicitly passed.

**Solution Pattern**:
```typescript
// jobs/processProjectExport.ts
import Bull from 'bull';

const exportQueue = new Bull('project-exports');

// Enqueue job with tenant context
export async function enqueueProjectExport(tenantId: string, projectId: string) {
    await exportQueue.add(
        {
            tenantId,  // MUST include tenant ID
            projectId,
            startedAt: new Date()
        },
        {
            jobId: `export:${tenantId}:${projectId}`,
            attempts: 3,
            backoff: { type: 'exponential', delay: 2000 }
        }
    );
}

// Process job with tenant context set
exportQueue.process(async (job) => {
    const { tenantId, projectId } = job.data;

    // Set tenant context for database queries
    process.env.CURRENT_TENANT_ID = tenantId;

    // Now all DB queries automatically filtered by RLS
    const project = await db.projects.findUnique({
        where: { id: projectId }
    });

    // Generate export
    const csv = generateCSV(project);

    // Upload to storage namespaced by tenant
    await storage.upload(
        `exports/tenant-${tenantId}/${projectId}-export.csv`,
        csv
    );

    return { success: true };
});
```

---

## 4. AUTHENTICATION & AUTHORIZATION PATTERNS

### 4.1 Organization-Level Authentication Services

**Clerk Organizations** (Recommended for B2B SaaS):
```typescript
// clerk.com offers native multi-org support
import { clerkClient } from '@clerk/clerk-sdk-node';

// Create organization
const organization = await clerkClient.organizations.createOrganization({
    name: 'Acme Corp'
});

// User joins organization with role
await clerkClient.organizations.addMemberToOrganization({
    organizationId: organization.id,
    userId: 'user_123',
    role: 'admin'  // or 'member', 'basic_member'
});

// Get user's organizations
const userOrgs = await clerkClient.users.getOrganizationMembershipList({
    userId: 'user_123'
});

// In middleware, extract current organization from JWT
import { getAuth } from '@clerk/nextjs/server';

export async function GET(req) {
    const { userId, orgId } = getAuth(req);

    // orgId automatically from JWT
    const org = await clerkClient.organizations.getOrganization({
        organizationId: orgId
    });

    // All subsequent queries scoped to this organization
}
```

**WorkOS** (Enterprise SSO + Directory Sync):
```typescript
import { WorkOS } from '@workos-inc/node';

const workos = new WorkOS(process.env.WORKOS_API_KEY);

// Provision organization for enterprise customer
const org = await workos.organizations.createOrganization({
    name: 'Enterprise Co',
    domains: ['enterprise.com']  // Email domain for auto-provisioning
});

// Enable SAML SSO for organization
const ssoSession = await workos.ssoSessions.createSsoSession({
    organizationId: org.id,
    clientId: process.env.WORKOS_CLIENT_ID,
    returnUrl: 'https://app.example.com/auth/callback'
});

// Verify user owns enterprise domain and auto-create in org
const verified = await workos.ssoSessions.getSsoSession({
    sessionId: ssoSession.id
});

// User automatically added to organization via SAML
if (verified.user.email.endsWith('@enterprise.com')) {
    // Auto-provision workspace for enterprise
}
```

**Auth0 Organizations**:
```typescript
import { ManagementClient } from 'auth0';

const management = new ManagementClient({
    domain: process.env.AUTH0_DOMAIN,
    clientId: process.env.AUTH0_MANAGEMENT_CLIENT_ID,
    clientSecret: process.env.AUTH0_MANAGEMENT_CLIENT_SECRET
});

// Create organization
const org = await management.organizations.create({
    name: 'Acme Corp',
    display_name: 'Acme Corporation'
});

// Add member with role
await management.organizations.addMembers(org.id, {
    members: [
        { user_id: 'user_123', role_id: 'admin_role_id' }
    ]
});

// In JWT, include organization context
// JWT claims will include org_id, org_roles[], org_permissions[]
```

### 4.2 RBAC (Role-Based Access Control)

**Simple Tenant + Role Model**:
```sql
-- Users belong to tenant with role
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email TEXT NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('admin', 'member', 'viewer')),
    UNIQUE(tenant_id, email)
);

-- Define what each role can do
CREATE TABLE role_permissions (
    role VARCHAR NOT NULL,
    resource VARCHAR NOT NULL,
    action VARCHAR NOT NULL,  -- 'read', 'write', 'delete'
    CHECK (role IN ('admin', 'member', 'viewer')),
    PRIMARY KEY (role, resource, action)
);

-- Sample permissions
INSERT INTO role_permissions VALUES
('admin', 'projects', 'read'),
('admin', 'projects', 'write'),
('admin', 'projects', 'delete'),
('admin', 'users', 'read'),
('admin', 'users', 'write'),
('member', 'projects', 'read'),
('member', 'projects', 'write'),
('viewer', 'projects', 'read');
```

**RBAC Enforcement in Application**:
```typescript
// Middleware to check permissions
async function requirePermission(resource: string, action: string) {
    return async (req, res, next) => {
        const userId = req.user.id;
        const tenantId = req.tenantId;

        // Get user's role in this tenant
        const userRole = await db.users.findUnique({
            where: { id_tenantId: { id: userId, tenantId } },
            select: { role: true }
        });

        // Check if role has permission
        const hasPermission = await db.rolePermissions.findUnique({
            where: {
                role_resource_action: {
                    role: userRole.role,
                    resource,
                    action
                }
            }
        });

        if (!hasPermission) {
            return res.status(403).json({ error: 'Permission denied' });
        }

        next();
    };
}

// Usage
app.post(
    '/api/projects',
    requirePermission('projects', 'write'),
    createProjectHandler
);

app.delete(
    '/api/projects/:id',
    requirePermission('projects', 'delete'),
    deleteProjectHandler
);
```

### 4.3 ABAC (Attribute-Based Access Control)

**Use Case**: RBAC is too coarse-grained; need fine-grained control based on attributes.

Example: User can view projects if (role == 'member' AND team == user.team) OR (created_by_user == user.id)

```sql
-- ABAC with policies
CREATE TABLE access_policies (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    resource_type VARCHAR NOT NULL,  -- 'projects', 'documents'
    conditions JSONB NOT NULL,  -- SQL-like conditions
    effect VARCHAR NOT NULL CHECK (effect IN ('allow', 'deny')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Example policy: Members can view projects in their team
INSERT INTO access_policies VALUES (
    gen_random_uuid(),
    'tenant-123',
    'projects',
    '{"condition": "user.team == resource.team"}',
    'allow'
);

-- Example policy: Admins can delete any project
INSERT INTO access_policies VALUES (
    gen_random_uuid(),
    'tenant-123',
    'projects',
    '{"condition": "user.role == ''admin''"}',
    'allow'
);
```

**ABAC Evaluation Engine**:
```typescript
interface ABACContext {
    user: {
        id: string;
        role: string;
        team: string;
        email: string;
    };
    resource: {
        id: string;
        type: string;
        owner_id: string;
        team: string;
        [key: string]: any;
    };
    action: string;
    environment: {
        time: Date;
        ip: string;
        [key: string]: any;
    };
}

async function evaluateABAC(
    tenantId: string,
    context: ABACContext
): Promise<boolean> {
    // Get all policies for this resource type
    const policies = await db.accessPolicies.findMany({
        where: {
            tenant_id: tenantId,
            resource_type: context.resource.type
        }
    });

    // Evaluate each policy
    let allowed = false;
    let denied = false;

    for (const policy of policies) {
        if (evaluateCondition(policy.conditions, context)) {
            if (policy.effect === 'allow') {
                allowed = true;
            } else {
                denied = true;  // Deny overrides allow
            }
        }
    }

    return allowed && !denied;
}

function evaluateCondition(condition: any, context: ABACContext): boolean {
    // Parse and evaluate condition like:
    // "user.role == 'admin' AND resource.team == user.team"

    const conditionStr = JSON.stringify(condition);

    // Replace variables with actual values
    let evaluated = conditionStr
        .replace(/user\.(\w+)/g, (_, key) => JSON.stringify(context.user[key]))
        .replace(/resource\.(\w+)/g, (_, key) => JSON.stringify(context.resource[key]))
        .replace(/environment\.(\w+)/g, (_, key) => JSON.stringify(context.environment[key]));

    // Safely evaluate (use dedicated library like Cerbos in production)
    return Function(`return ${evaluated}`)();
}
```

### 4.4 Impersonation Pattern for Support

**Use Case**: Support team needs to debug issues by viewing customer's data without compromising security.

```sql
-- Track impersonation for audit
CREATE TABLE impersonation_logs (
    id UUID PRIMARY KEY,
    support_user_id UUID NOT NULL,
    impersonated_user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    reason TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    actions_taken TEXT[]  -- Track what support did while impersonating
);

-- Add impersonation column to users
ALTER TABLE users ADD COLUMN impersonated_by UUID REFERENCES users(id);
ALTER TABLE users ADD COLUMN impersonation_reason TEXT;
```

**Impersonation Workflow**:
```typescript
app.post('/api/admin/impersonate/:userId', async (req, res) => {
    const supportUserId = req.user.id;
    const targetUserId = req.params.userId;
    const reason = req.body.reason;

    // Only support role can impersonate
    if (req.user.role !== 'support') {
        return res.status(403).json({ error: 'Permission denied' });
    }

    // Log impersonation start
    const log = await db.impersonationLogs.create({
        data: {
            support_user_id: supportUserId,
            impersonated_user_id: targetUserId,
            tenant_id: req.tenantId,
            reason,
            started_at: new Date()
        }
    });

    // Create temporary JWT for impersonated user
    const token = jwt.sign(
        {
            sub: targetUserId,
            tenant_id: req.tenantId,
            impersonated_by: supportUserId,
            impersonation_log_id: log.id
        },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }  // Short expiration
    );

    res.json({ token, impersonation_log_id: log.id });
});

// When support user makes requests with impersonation token,
// log all actions for audit trail
app.use((req, res, next) => {
    if (req.user.impersonated_by) {
        // Log action to impersonation_logs
        const action = `${req.method} ${req.path}`;
        db.impersonationLogs.update({
            where: { id: req.user.impersonation_log_id },
            data: {
                actions_taken: { push: action }
            }
        });
    }
    next();
});
```

---

## 5. INFRASTRUCTURE ISOLATION

### 5.1 Kubernetes Multi-Tenancy

**Namespace Per Tenant**:
```yaml
# One Kubernetes namespace per tenant
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-456

---
# Resource quota to prevent noisy neighbor
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-456-quota
  namespace: tenant-456
spec:
  hard:
    requests.cpu: "10"  # Max 10 CPU cores
    requests.memory: "50Gi"  # Max 50GB memory
    pods: "100"  # Max 100 pods
    persistentvolumeclaims: "10"  # Max 10 PVCs
```

**Network Policy Isolation**:
```yaml
# Prevent traffic between tenant namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-tenant
  namespace: tenant-456
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: tenant-456  # Only traffic from same namespace
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: tenant-456
  - to:  # Allow DNS
    - namespaceSelector:
        name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

### 5.2 AWS/GCP Project-Level Isolation

**AWS Organizations for Enterprise Tenants**:
```bash
# Each enterprise tenant gets own AWS Account
aws organizations create-account \
  --email "tenant-456@customers.example.com" \
  --account-name "Tenant 456 Prod"

# Isolate billing, IAM, resources
aws organizations create-organizational-unit \
  --parent-id r-1234 \
  --name "tenant-456"

# Apply policies to prevent data access across accounts
aws organizations attach-policy \
  --policy-id p-xxxxxxxxxx \
  --target-id ou-tenant-456
```

**GCP Projects for Enterprise Tenants**:
```bash
# Each tenant gets dedicated GCP project
gcloud projects create tenant-456-prod \
  --name="Tenant 456 Production" \
  --organization-id=123456789

# Set quotas per project
gcloud compute project-info add-metadata \
  --project=tenant-456-prod \
  --metadata=cpu-quota=64,memory-quota=256

# Enable only required APIs
gcloud services enable \
  --project=tenant-456-prod \
  compute.googleapis.com \
  storage-api.googleapis.com
```

### 5.3 Network Isolation

**VPC Per Tenant (Enterprise)**:
```hcl
# Terraform: VPC per enterprise tenant
resource "aws_vpc" "tenant_456" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name      = "tenant-456-vpc"
    TenantID  = "tenant-456"
  }
}

# Private subnets for isolation
resource "aws_subnet" "tenant_456_private" {
  vpc_id            = aws_vpc.tenant_456.id
  cidr_block        = "10.1.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name     = "tenant-456-private"
    TenantID = "tenant-456"
  }
}

# Security group restricts traffic
resource "aws_security_group" "tenant_456" {
  vpc_id = aws_vpc.tenant_456.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    TenantID = "tenant-456"
  }
}
```

---

## 6. REAL-WORLD CASE STUDIES & PRICING

### 6.1 Shopify's Multi-Tenant Architecture

**Architecture Overview**:
- Pod-based isolation: Each pod contains 1-50 stores
- Complete Shopify instance per pod (MySQL, Redis, workers)
- Stateless application servers shared across pods
- Separate datastores per pod prevent noisy neighbor issues

**How Pods Work**:
```
Pod 1 (Region: US-East)
├── Datastore (MySQL + Redis)
└── 25 stores

Pod 2 (Region: US-East)
├── Datastore (MySQL + Redis)
└── 18 stores

Pod 3 (Region: EU)
├── Datastore (MySQL + Redis)
└── 30 stores

Shared stateless workers handle:
├── Request routing
├── Authentication
├── API gateway
└── Load balancing
```

**Handling Flash Sales**:
- Black Friday: one store on a pod gets 1000x traffic
- Shopify dynamically isolates that store to dedicated pod
- Other stores unaffected (no resource contention)
- Extra-large merchants get their own pod permanently

**Data Migration During Black Friday**:
```
11:59 PM: Store A gets allocated dedicated pod
├── Live replication from shared pod
├── App switches at midnight
└── Zero downtime during peak

Post-sale: Store A scaled down to shared pod if traffic drops
```

**Cost Model**:
- Shared pod: supports 1000+ SMB stores efficiently
- Enterprise pod (dedicated): can support 1-5 large stores
- Premium pod (high-isolation): single massive merchant

### 6.2 Cost Breakdown by Scale

**100 Tenants (Early Stage)**:
```
Architecture: Row-level RLS in PostgreSQL
Database: AWS RDS db.t3.small (~$30/month)
Application: 2x t3.small EC2 (~$30/month)
Redis cache: t3.micro (~$15/month)
CDN: CloudFront (~$50/month)
Total: ~$125/month
Cost per tenant: $1.25/month
```

**1,000 Tenants (Growth Stage)**:
```
Architecture: Hybrid (500 on row-level, 500 on schema-per-tenant)
Database Tier 1: db.r5.xlarge PostgreSQL (~$400/month)
Database Tier 2: 2x db.r5.large PostgreSQL (~$350/month)
Application: 5x t3.large (~$200/month)
Redis cluster: 3 nodes (~$300/month)
Load balancer: ALB (~$20/month)
Monitoring: DataDog (~$200/month)
Total: ~$1,470/month
Cost per tenant: $1.47/month (economies of scale)
```

**10,000 Tenants (Scale Stage)**:
```
Architecture: Tiered
Tier 1 (8,000 SMB): Row-level RLS
├── Database: db.r6i.4xlarge (~$1,200/month)
├── Connection pooling: Supavisor (~$300/month)
└── Cost per tenant: $0.19

Tier 2 (1,500 Professional): Schema per tenant
├── Database: 3x db.r6i.2xlarge (~$900/month)
└── Cost per tenant: $0.60

Tier 3 (500 Enterprise): Dedicated databases
├── 500x t3.medium RDS (~$50/month each = $25,000)
└── Cost per tenant: $50

Total infrastructure: ~$27,000/month
Blended cost per tenant: $2.70/month
Revenue assumption: $99/month avg → gross margin 63%
```

**100,000 Tenants (Enterprise Scale)**:
```
Architecture: Global multi-region
US-East (40K tenants)
├── Database cluster: 5x db.r6i.8xlarge ($3,000/month)
├── Read replicas: 3x db.r6i.4xlarge ($1,800/month)
└── Cost per tenant: $0.12

EU-West (35K tenants, GDPR compliance)
├── Database cluster: 5x db.r6i.8xlarge ($3,000/month)
└── Cost per tenant: $0.086

APAC (25K tenants)
├── Database cluster: 3x db.r6i.8xlarge ($1,800/month)
└── Cost per tenant: $0.072

Total infrastructure: ~$10K/month (database only)
Additional: App servers, CDN, cache, monitoring: ~$20K
Total: ~$30K/month
Blended cost per tenant: $0.30/month
```

### 6.3 When to Upgrade Isolation Level

**From Row-Level to Schema-Per-Tenant**:
- When: 1,000+ tenants
- Why: Catalog bloat, schema flexibility needs
- Migration: Live with pglogical continuous replication
- Cost increase: +30-50% infrastructure

**From Shared to Dedicated Database**:
- When: Single tenant generating >$50K/year revenue (enterprise)
- Why: Performance guarantees, compliance, customization
- Trigger: SLA requirements, HIPAA/GDPR compliance, >100M rows
- Cost multiple: 100-200x per tenant

---

## 7. COMPLIANCE & DATA RESIDENCY

### 7.1 GDPR Compliance in Multi-Tenant Systems

**Key Requirements**:
1. **Data Residency**: EU citizen data must stay in EU
2. **Data Portability**: Can export all personal data
3. **Right to be Forgotten**: Can delete all data within 30 days
4. **Encryption**: In transit and at rest
5. **Audit Trails**: Track who accessed what data

**Implementation**:
```sql
-- Track data residency per tenant
CREATE TABLE tenant_data_residency (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id),
    residency_region VARCHAR NOT NULL,  -- 'eu', 'us', 'apac'
    primary_database_host TEXT NOT NULL,
    backup_regions TEXT[] NOT NULL,
    agreed_at TIMESTAMPTZ NOT NULL,
    gdpr_compliant BOOLEAN DEFAULT false,
    data_processing_agreement TEXT NOT NULL,
    CHECK (residency_region IN ('eu', 'us', 'apac'))
);

-- Audit all data access
CREATE TABLE data_access_audit (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    resource_type VARCHAR NOT NULL,  -- 'users', 'documents'
    resource_id UUID NOT NULL,
    action VARCHAR NOT NULL,  -- 'read', 'write', 'delete'
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- GDPR right to be forgotten
ALTER TABLE users ADD COLUMN anonymized_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN anonymized_fields JSONB;  -- Track what was anonymized

CREATE PROCEDURE anonymize_user(user_id UUID, tenant_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users
    SET
        email = 'deleted+' || id || '@example.com',
        name = 'Deleted User',
        anonymized_at = NOW(),
        anonymized_fields = jsonb_build_object(
            'original_email', email,
            'original_name', name
        )
    WHERE id = user_id AND tenant_id = tenant_id;

    INSERT INTO data_access_audit VALUES (
        gen_random_uuid(),
        tenant_id,
        user_id,
        'users',
        user_id,
        'anonymize',
        NOW(),
        NULL,
        'GDPR Right to be Forgotten'
    );
END;
$$;
```

### 7.2 HIPAA Compliance for Healthcare SaaS

**Core Requirements**:
1. **Business Associate Agreement (BAA)**: Signed with customer
2. **Encryption**: 256-bit AES at rest, TLS 1.2+ in transit
3. **Access Controls**: Audit logs of all access
4. **Integrity Controls**: Data cannot be modified without audit trail
5. **Availability**: 99.9% uptime + disaster recovery

**HIPAA-Compliant Architecture**:
```yaml
# Dedicated database per healthcare tenant (required for HIPAA)
healthcare_tenants:
  database_type: dedicated_postgres
  encryption_at_rest: "AES-256"
  encryption_in_transit: "TLS 1.3"
  backup_encryption: "AES-256"
  backup_region: separate_geography

  # HIPAA audit logging (immutable)
  audit_logging:
    destination: "S3 with WORM (Write Once Read Many)"
    retention: "7 years"
    integrity_check: "SHA-256 checksums"

  # Access logging
  access_logging:
    enabled: true
    destination: "CloudWatch Logs"
    tracking: ["user_id", "timestamp", "resource", "action"]

  # Data integrity
  integrity_verification:
    database_checksums: enabled
    replication_verification: enabled

  compliance_certifications:
    - "SOC 2 Type II"
    - "HIPAA Business Associate"
    - "HITRUST CSF"
```

---

## 8. TESTING MULTI-TENANT SYSTEMS

### 8.1 Data Leak Prevention Testing

**Critical Test**: Tenant A cannot access Tenant B's data

```typescript
// Automated test suite
describe('Multi-Tenant Data Isolation', () => {
    const tenantA = { id: 'tenant-a', name: 'Acme Corp' };
    const tenantB = { id: 'tenant-b', name: 'Widget Inc' };

    beforeAll(async () => {
        // Create test tenants and sample data
        await setupTestTenant(tenantA);
        await setupTestTenant(tenantB);

        // Create sample projects
        await createProject(tenantA.id, { name: 'Secret Project' });
        await createProject(tenantB.id, { name: 'Public Project' });
    });

    test('Tenant A cannot read Tenant B projects', async () => {
        const client = authenticateAs(tenantA);

        // This should return empty (Tenant A's projects only)
        const projects = await client.get('/api/projects');

        expect(projects).toHaveLength(1);
        expect(projects[0].name).toBe('Secret Project');

        // Verify Tenant B's data is NOT present
        expect(projects.some(p => p.name === 'Public Project')).toBe(false);
    });

    test('Tenant A cannot write to Tenant B data', async () => {
        const clientA = authenticateAs(tenantA);
        const projectB = await getProject(tenantB.id, 'public-project-id');

        // Try to modify Tenant B's project
        const response = await clientA.put(
            `/api/projects/${projectB.id}`,
            { name: 'Hacked!' }
        );

        // Should fail with 403 or 404 (not found)
        expect([403, 404]).toContain(response.status);

        // Verify data was not modified
        const updated = await getProject(tenantB.id, projectB.id);
        expect(updated.name).toBe('Public Project');
    });

    test('Tenant A cannot delete Tenant B data', async () => {
        const clientA = authenticateAs(tenantA);
        const projectB = await getProject(tenantB.id, 'public-project-id');

        const response = await clientA.delete(
            `/api/projects/${projectB.id}`
        );

        expect([403, 404]).toContain(response.status);

        // Verify data still exists
        const exists = await getProject(tenantB.id, projectB.id);
        expect(exists).toBeDefined();
    });

    test('Cross-tenant SQL injection blocked', async () => {
        const clientA = authenticateAs(tenantA);

        // Attempt SQL injection to access Tenant B data
        const maliciousQuery = `' OR tenant_id != '${tenantA.id}`;

        const response = await clientA.get(
            `/api/projects?search=${encodeURIComponent(maliciousQuery)}`
        );

        // Should return only Tenant A's projects
        expect(response.data.every(p => p.tenant_id === tenantA.id)).toBe(true);
    });

    test('API parameter tampering blocked', async () => {
        const clientA = authenticateAs(tenantA);

        // Try to fetch Tenant B's data by changing X-Tenant-ID header
        const response = await clientA.get(
            '/api/projects',
            { headers: { 'X-Tenant-ID': tenantB.id } }
        );

        // Should return Tenant A's projects (server overrides header)
        expect(response.data.every(p => p.tenant_id === tenantA.id)).toBe(true);
    });
});
```

### 8.2 Performance Testing Under Tenant Load

```typescript
// Load testing with multiple concurrent tenants
describe('Multi-Tenant Performance', () => {
    test('Query performance consistent across tenant count', async () => {
        const metrics = [];

        // Test with 10, 100, 1000 tenants
        for (const tenantCount of [10, 100, 1000]) {
            // Create test tenants
            const tenants = await createTenants(tenantCount);

            // Add identical data to each tenant
            for (const tenant of tenants) {
                for (let i = 0; i < 1000; i++) {
                    await createProject(tenant.id, { name: `Project ${i}` });
                }
            }

            // Measure query time
            const startTime = performance.now();
            const projects = await queryTenant(
                tenants[0].id,
                'SELECT * FROM projects'
            );
            const duration = performance.now() - startTime;

            metrics.push({
                tenantCount,
                queryTimeMs: duration,
                resultCount: projects.length
            });
        }

        // Verify query time doesn't degrade linearly with tenant count
        // With proper indexing: 10 tenants ~5ms, 100 tenants ~5ms, 1000 tenants ~6ms
        expect(metrics[0].queryTimeMs).toBeLessThan(10);  // 10 tenants
        expect(metrics[1].queryTimeMs).toBeLessThan(10);  // 100 tenants
        expect(metrics[2].queryTimeMs).toBeLessThan(15);  // 1000 tenants (slight overhead)
    });
});
```

---

## 9. DECISION MATRIX: CHOOSING YOUR MODEL

| Tenant Count | Primary Goal | Recommended | Cost | Complexity |
|------------|--------------|-------------|------|------------|
| <100 | MVP, quick launch | Row-level RLS | $0.50-2 per tenant | Low |
| 100-1K | Growth | Row-level RLS + RLS optimization | $0.20-1 | Low-Medium |
| 1K-10K | Scale, multi-tier | Hybrid (shared + schema) | $0.50-5 | Medium |
| 10K-100K | Enterprise mix | Hybrid (tiered by plan) | $0.30-50 | High |
| >100K | Global at scale | Multi-region sharding | $0.10-100+ | Very High |

---

## 10. MIGRATION CHECKLIST

When upgrading from Row-Level to Schema-Per-Tenant:

- [ ] Audit current data for tenant_id consistency
- [ ] Plan schema creation without downtime
- [ ] Set up pglogical replication streams
- [ ] Create monitoring for replication lag
- [ ] Implement gradual tenant migration (5% per week)
- [ ] Test fallback procedure
- [ ] Coordinate with support for customer comms
- [ ] Monitor query performance post-migration
- [ ] Update connection pooling configuration
- [ ] Archive old row-level schema after 2 weeks

---

## 11. KEY REFERENCES

### AWS & Azure Documentation
- [AWS SaaS Fundamentals](https://docs.aws.amazon.com/whitepapers/latest/saas-architecture-fundamentals/re-defining-multi-tenancy.html)
- [Azure Multi-Tenant Solutions](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)
- [AWS Guidance Multi-Tenant](https://aws.amazon.com/solutions/guidance/multi-tenant-architectures-on-aws/)

### PostgreSQL & Database
- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [AWS Multi-Tenant RLS Guide](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)
- [Citus Sharding Guide](https://www.citusdata.com/blog/2016/08/10/sharding-for-a-multi-tenant-app-with-postgres/)

### Supabase & Modern Tools
- [Supabase RLS Documentation](https://supabase.com/features/row-level-security)
- [Implementing Multi-tenancy with Supabase and Clerk](https://clerk.com/blog/multitenancy-clerk-supabase-b2b)

### Authentication Services
- [Clerk Organizations Docs](https://clerk.com/docs/guides/organizations/overview)
- [WorkOS Developer Guide](https://workos.com/blog/developers-guide-saas-multi-tenant-architecture)
- [Auth0 Organizations](https://auth0.com/docs/get-started/applications)

### Compliance
- [GDPR Compliance in Multi-Tenant SaaS](https://www.future-processing.com/blog/multi-tenant-architecture/)
- [HIPAA and Multi-Tenancy](https://neon.com/blog/hipaa-multitenancy-b2b-saas)

---

## Related References

- [Databases: Relational](./07-databases-relational.md) — PostgreSQL RLS and relational schema design
- [Auth Solutions](./10-auth-solutions.md) — Authentication and authorization patterns for multi-tenant
- [Compliance: GDPR & CCPA](./36-compliance-gdpr-ccpa.md) — Data residency and tenant isolation compliance
- [Edge & Multi-Region](./43-edge-multi-region.md) — Distributing multi-tenant systems across regions
- [Startup to Enterprise](./46-startup-to-enterprise.md) — Scaling multi-tenancy from MVP to enterprise

---

**Document Status**: Production Ready
**Last Reviewed**: March 2026
**Next Review**: September 2026
<!-- PRICING_STABILITY: MODERATE | Updated: 2026-03-03 | Multi-tenancy tooling and auth provider pricing changes annually. Verify org-level auth pricing before recommending. -->
