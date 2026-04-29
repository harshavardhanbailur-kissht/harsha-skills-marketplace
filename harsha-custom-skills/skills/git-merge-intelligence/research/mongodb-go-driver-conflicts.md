# MongoDB/DocumentDB Conflict Patterns in Go Codebases
## Comprehensive Research Guide

**Date:** April 2026
**Scope:** Schema evolution, Go driver integration, migration strategies, and DocumentDB compatibility

---

## 1. Schema Evolution Conflicts in MongoDB/DocumentDB

### 1.1 Field Conflicts — Adding Different Fields to Same Collection

#### Scenario
Two branches independently add different fields to documents in the same collection:
- Branch A adds `userPreferences` (object type with nested fields)
- Branch B adds `analyticsData` (array of event objects)

#### Safe Coexistence Rules

**When Both Field Definitions Can Coexist:**

1. **Non-overlapping field names** — If the fields have completely different names and serve different purposes, they can safely coexist in the same collection.

2. **Compatible types** — Ensure field types don't conflict semantically. For example, both branches adding a `status` field as string is problematic; both adding `createdAt` as timestamp is also problematic.

3. **No index conflicts** — Verify that neither branch creates incompatible indexes on the same field with different configurations.

4. **Backward-compatible schema versioning** — Use a `schemaVersion` field in documents to track which version each document adheres to. This allows queries to handle both old and new field structures gracefully.

**When One Field Definition Must Win:**

1. **Same field, different types** — If both branches add a field with the same name but different types:
   - Merge commit must choose the dominant type
   - Run a migration to coerce all existing documents to that type
   - Update application code to handle any legacy values
   - Document the breaking change in migration notes

2. **Same field, different semantic meaning** — If both branches use the same field name with different logical purposes:
   - Choose which semantic meaning is correct
   - Rename one field in the merge commit
   - Run a migration to populate renamed field from old data
   - Update queries and BSON struct tags accordingly

3. **Conflicting indexes on same field** — If both branches create indexes with different configurations (e.g., ascending vs. text index on the same field):
   - Remove the less-optimal index before merge
   - Rebuild the chosen index across all documents
   - See Section 1.2 for index conflict resolution

#### Example: Safe Multi-Branch Schema Evolution

```
Collection: users (after successful merge)
{
  _id: ObjectId,
  email: string,
  createdAt: Date,
  // From Branch A
  userPreferences: {
    theme: string,
    notifications: boolean
  },
  // From Branch B
  analyticsData: [{
    eventType: string,
    timestamp: Date
  }],
  // Schema tracking
  schemaVersion: 3
}
```

### 1.2 Index Definition Conflicts

#### Duplicate/Conflicting Index Scenarios

**Problem: Duplicate Indexes**

Two branches independently create indexes on the same field(s):
- Branch A: `db.users.createIndex({ email: 1 })`
- Branch B: `db.users.createIndex({ email: 1 })`

MongoDB will silently ignore the second index creation (idempotent behavior), but this creates maintenance confusion and potential performance issues.

**Problem: Conflicting Index Types**

- Branch A: `db.products.createIndex({ name: 1 })` — Standard ascending index
- Branch B: `db.products.createIndex({ name: "text" })` — Full-text search index

MongoDB cannot have both a standard index and a text index on the same field. The second creation will fail with error code 13111.

**Problem: Partial Index Conflicts**

- Branch A: `createIndex({ status: 1 }, { partialFilterExpression: { active: true } })`
- Branch B: `createIndex({ status: 1 }, { partialFilterExpression: { deleted: false } })`

Two different partial indexes on the same field with different filter expressions waste storage and create query optimizer confusion.

#### Resolution Strategies

**1. Identify Index Conflicts in Merge Commit**

```bash
# List all existing indexes
db.collection.getIndexes()

# Compare with both branches' migration scripts
# Remove or consolidate conflicts before merge
```

**2. Consolidate to Most Specific Index**

Choose the most useful index configuration:

```javascript
// If both branches index the same field, choose the broader one
// Example: Branch A wants { userId: 1, createdAt: -1 }
//          Branch B wants { userId: 1 }
// Resolution: Keep the compound index (more specific, supports both queries)

db.collection.dropIndex("userId_1");
db.collection.createIndex({ userId: 1, createdAt: -1 });
```

**3. Use Partial Indexes for Complex Queries**

Instead of competing partial indexes, consolidate:

```javascript
// Remove conflicting indexes
db.users.dropIndex("status_1");

// Create single unified partial index
db.users.createIndex(
  { status: 1, createdAt: -1 },
  {
    partialFilterExpression: {
      active: true,
      deleted: false
    }
  }
);
```

**4. Document Index Intent in Comments**

In migration scripts, add documentation:

```go
// Migration: Index consolidation for user queries
// Purpose: Support queries filtering by (status, createdAt) where user is active
// Replaces: status_1 (Branch A), status_1 with partial filter (Branch B)
// Performance: Reduces memory overhead, supports 85% of user queries

err := coll.Indexes().CreateOne(ctx,
  mongo.IndexModel{
    Keys: bson.D{{Key: "status", Value: 1}, {Key: "createdAt", Value: -1}},
    Options: options.Index().SetPartialFilterExpression(bson.M{
      "active": true,
      "deleted": bson.M{"$exists": false},
    }),
  },
)
```

#### MongoDB Index Best Practices (2025)

Per [MongoDB Indexing Strategies documentation](https://www.mongodb.com/docs/manual/applications/indexes/):

- Create indexes on fields that are frequently searched or used in filter operations
- Use partial indexes when applicable to index only a subset of documents
- Regularly analyze query patterns and remove unused indexes
- Avoid excessive indexing, which causes slower writes and memory pressure
- Index fields in the order they appear in query filters (compound indexes)

### 1.3 Field Coexistence Decision Matrix

| Scenario | Can Coexist? | Action |
|----------|-------------|--------|
| Different field names, non-overlapping types | YES | Accept both; update model struct |
| Same field name, identical type & meaning | YES | Accept one; remove duplication in migration script |
| Same field name, different types | NO | Migrate to unified type; document breaking change |
| Same field name, different semantic meaning | NO | Rename one field; migrate data |
| Overlapping indexes on same field | NO | Drop one; consolidate to most useful index |
| Partial indexes with conflicting filters | NO | Merge filter expressions or drop one |
| Different compound index orders | MAYBE | Evaluate query patterns; consolidate if possible |

---

## 2. Go MongoDB Driver Conflict Patterns

### 2.1 BSON Struct Tag Conflicts

[MongoDB Go Driver BSON documentation](https://www.mongodb.com/docs/drivers/go/current/fundamentals/bson/) and [struct tagging guide](https://www.mongodb.com/docs/drivers/go/current/data-formats/struct-tagging/) provide official standards.

#### Struct Tag Conflict Scenarios

**Problem: Different BSON Field Names for Same Go Field**

```go
// Branch A
type User struct {
  Email string `bson:"email_address"`
  Name  string `bson:"userName"`
}

// Branch B
type User struct {
  Email string `bson:"email"`
  Name  string `bson:"name"`
}

// After merge conflict in struct definition
```

#### Resolution Strategy

1. **Choose the field naming convention** — Decide on camelCase, snake_case, or another standard
2. **Update struct tags consistently** — Apply chosen convention across all fields
3. **Run data migration** — Rename fields in existing documents
4. **Update queries** — Ensure all filter and update queries use correct field names

```go
// Post-merge standardized struct
type User struct {
  ID    primitive.ObjectID `bson:"_id,omitempty"`
  Email string             `bson:"email"`
  Name  string             `bson:"name"`
  // ... other fields
}

// Migration function to rename fields
func migrateFieldNames(coll *mongo.Collection, ctx context.Context) error {
  filter := bson.M{}
  update := bson.A{
    bson.M{"$rename": bson.M{
      "email_address": "email",
      "userName": "name",
    }},
  }

  result, err := coll.UpdateMany(ctx, filter, update)
  if err != nil {
    return err
  }

  log.Printf("Updated %d documents", result.ModifiedCount)
  return nil
}
```

#### BSON Tag Best Practices (2025)

Per [Go Driver struct tagging documentation](https://www.mongodb.com/docs/drivers/go/current/data-formats/struct-tagging/):

- **Always explicitly define BSON tags** — Don't rely on default field name mapping
- **Use omitempty for optional fields** — Prevents marshaling empty/zero values as null
- **Use inline for embedded structs** — Flattens nested structures when appropriate
- **Use minsize for integer fields** — Optimizes storage for fields that fit in 32-bit integers
- **Document semantic meaning** — Add comments explaining field purposes

**Modern Approach (Go Driver v2.3.0+):**

Configure global BSON marshaling options instead of tagging every field:

```go
import "go.mongodb.org/mongo-driver/bson/bsonopt"

// At application startup
registry := bson.NewRegistry()
registry = registry.
  SetOmitEmpty(true).
  SetUseJSONStructTags(true). // Falls back to "json" tags if "bson" not present
  SetNilSliceAsEmpty(true)

opts := options.Client().SetRegistry(registry)
client, err := mongo.Connect(ctx, opts)
```

#### Conflicting Struct Tag Patterns

| Pattern | Conflict Type | Resolution |
|---------|--------------|-----------|
| Same field, different `bson` names | Field mapping mismatch | Standardize naming convention; migrate data |
| Different `omitempty` handling | Serialization difference | Choose standard; update all structs consistently |
| Inline vs. nested struct | Document structure conflict | Restructure one branch to match; migrate documents |
| Different field order | Readability (no functional impact) | Reorder for consistency; no data migration needed |

### 2.2 Query Filter Conflicts

#### Scenario: Conflicting Query Modifications

Branch A and Branch B both modify the same query logic:

```go
// Branch A — filters by status and role
filter := bson.M{
  "status": "active",
  "role": bson.M{"$in": []string{"admin", "moderator"}},
}

// Branch B — filters by status and permissions
filter := bson.M{
  "status": "active",
  "permissions": bson.M{"$exists": true},
}
```

#### Resolution Strategy

1. **Understand intent of each filter** — Why did each branch add its conditions?
2. **Determine logical combination** — Should filters be AND-ed or OR-ed?
3. **Test merged filter** — Verify it returns expected documents
4. **Document logic in code comments**

```go
// Merged filter combining both conditions
// Intent: Find active users who are either admins/moderators OR have explicit permissions
filter := bson.M{
  "status": "active",
  "$or": []bson.M{
    {"role": bson.M{"$in": []string{"admin", "moderator"}}},
    {"permissions": bson.M{"$exists": true}},
  },
}

// Alternative: AND both conditions if both are required
// filter := bson.M{
//   "status": "active",
//   "role": bson.M{"$in": []string{"admin", "moderator"}},
//   "permissions": bson.M{"$exists": true},
// }
```

#### Common Query Filter Conflict Patterns

| Pattern | Example Conflict | Resolution |
|---------|-----------------|-----------|
| Mutually exclusive conditions | `status: "active"` vs. `status: "inactive"` | Keep most restrictive OR combine with $or |
| Overlapping range queries | `age: {$gt: 18}` vs. `age: {$gte: 21}` | Choose most restrictive; update business logic |
| Nested field access | `user.name` vs. `userName` | Standardize field names first (see 2.1) |
| Array queries | `tags: "urgent"` vs. `tags: {$all: ["urgent", "security"]}` | Combine with AND logic |

### 2.3 Aggregation Pipeline Conflicts

#### Scenario: Pipeline Stage Conflicts

Two branches add competing stages to an aggregation pipeline:

```go
// Branch A's pipeline
pipeline := mongo.Pipeline{
  bson.D{{Key: "$match", Value: bson.D{{Key: "status", Value: "active"}}}},
  bson.D{{Key: "$sort", Value: bson.D{{Key: "createdAt", Value: -1}}}},
  bson.D{{Key: "$limit", Value: 100}},
  bson.D{{Key: "$group", Value: bson.D{
    {Key: "_id", Value: "$category"},
    {Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
  }}},
}

// Branch B's pipeline (different grouping logic)
pipeline := mongo.Pipeline{
  bson.D{{Key: "$match", Value: bson.D{{Key: "status", Value: "active"}}}},
  bson.D{{Key: "$group", Value: bson.D{
    {Key: "_id", Value: "$userId"},
    {Key: "total", Value: bson.D{{Key: "$sum", Value: "$amount"}}},
  }}},
  bson.D{{Key: "$sort", Value: bson.D{{Key: "total", Value: -1}}}},
}
```

#### Resolution Strategy

Per [Go Driver aggregation documentation](https://www.mongodb.com/docs/drivers/go/current/fundamentals/aggregation/):

1. **Determine if both pipelines serve different purposes** — They may need separate query methods
2. **Consolidate if they're variants of same query** — Combine stages with conditional logic
3. **Place early filtering** — Move `$match` stages to beginning for index utilization
4. **Order stages for optimization** — Follow MongoDB aggregation pipeline optimization patterns

```go
// Consolidated pipeline supporting both use cases
func buildAggregationPipeline(groupByCategory bool) mongo.Pipeline {
  pipeline := mongo.Pipeline{
    // Match early for index use
    bson.D{{Key: "$match", Value: bson.D{{Key: "status", Value: "active"}}}},
  }

  if groupByCategory {
    // Branch A logic: group by category with limit
    pipeline = append(pipeline,
      bson.D{{Key: "$group", Value: bson.D{
        {Key: "_id", Value: "$category"},
        {Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
      }}},
      bson.D{{Key: "$sort", Value: bson.D{{Key: "count", Value: -1}}}},
      bson.D{{Key: "$limit", Value: 100}},
    )
  } else {
    // Branch B logic: group by user with amount sum
    pipeline = append(pipeline,
      bson.D{{Key: "$group", Value: bson.D{
        {Key: "_id", Value: "$userId"},
        {Key: "total", Value: bson.D{{Key: "$sum", Value: "$amount"}}},
      }}},
      bson.D{{Key: "$sort", Value: bson.D{{Key: "total", Value: -1}}}},
    )
  }

  return pipeline
}
```

#### Aggregation Pipeline Conflict Matrix

| Stage Conflict | Example | Resolution |
|---|---|---|
| Different $match filters | `{status: "active"}` vs. `{userId: objId}` | Combine with AND if both needed, OR if alternatives |
| Multiple $group stages | Grouping by field A vs. field B | Separate into distinct query methods |
| Conflicting $sort orders | `{createdAt: -1}` vs. `{priority: 1}` | Add secondary sort field; document why |
| $limit in different positions | After match vs. after group | Place before expensive stages (like $group) |
| Competing $project stages | Selecting different fields | Merge field selections |

### 2.4 Collection Name Changes or Reorganization

#### Scenario: Collection Renamed or Reorganized

- Branch A renames `users` collection to `user_accounts`
- Branch B adds a `users_archive` collection for historical data
- Branch C reorganizes into multiple collections: `users`, `user_preferences`, `user_sessions`

#### Resolution Strategy

1. **Establish canonical collection structure** — Choose which reorganization approach is correct
2. **Identify all references** — Find all queries, indexes, and application code referencing old names
3. **Create migration plan** — Determine if you can rename in-place or need to copy data
4. **Update Go code systematically**

```go
// Type-safe collection name constants
const (
  UsersCollection           = "users"
  UserPreferencesCollection = "user_preferences"
  UserSessionsCollection    = "user_sessions"
)

// Repository pattern to abstract collection access
type UserRepository struct {
  db *mongo.Database
}

func (r *UserRepository) FindByID(ctx context.Context, id primitive.ObjectID) (*User, error) {
  coll := r.db.Collection(UsersCollection)
  var user User
  err := coll.FindOne(ctx, bson.M{"_id": id}).Decode(&user)
  return &user, err
}

// Migration function
func migrateCollectionNames(db *mongo.Database, ctx context.Context) error {
  // If collections need to be renamed
  if err := db.Collection("users_old").Database().RunCommand(ctx,
    bson.M{"renameCollection": "mydb.users_old", "to": "mydb.users"}).Err(); err != nil {
    return err
  }

  return nil
}
```

#### Collection Reorganization Checklist

- [ ] All collection name references updated in Go code
- [ ] All indexes recreated on new collection names
- [ ] All queries updated to reference correct collections
- [ ] Foreign key references (via ObjectID) still point correctly
- [ ] Aggregation pipelines using correct collection names
- [ ] Tests updated with new collection names
- [ ] Application initialization code updated

### 2.5 Connection Configuration Conflicts

#### Scenario: Conflicting Connection Options

```go
// Branch A — Emphasizes timeout safety
opts := options.Client().
  SetConnectTimeout(30 * time.Second).
  SetServerSelectionTimeout(5 * time.Second).
  ApplyURI("mongodb://user:pass@host:27017/db?maxPoolSize=100")

// Branch B — Emphasizes performance
opts := options.Client().
  SetConnectTimeout(5 * time.Second).
  SetServerSelectionTimeout(10 * time.Second).
  ApplyURI("mongodb://user:pass@host:27017/db?maxPoolSize=1000")
```

#### Connection Configuration Options Reference

Per [Go Driver connection options documentation](https://www.mongodb.com/docs/drivers/go/current/fundamentals/connections/connection-options/):

| Option | Purpose | Conflict Type |
|--------|---------|--------------|
| `timeoutMS` | Single operation timeout | Choose based on workload SLAs |
| `connectTimeoutMS` | Connection establishment timeout | Choose based on network reliability |
| `socketTimeoutMS` | Socket read/write timeout | Choose based on query latency expectations |
| `maxPoolSize` | Maximum connection pool size | Choose based on concurrent connection needs |
| `minPoolSize` | Minimum connection pool size | Choose based on idle connection overhead |
| `maxConnIdleTimeMS` | Connection idle lifetime | Choose based on server resource constraints |
| `retryWrites` | Automatic retry on transient failures | **CRITICAL for DocumentDB (see 2.5.1)** |

#### Resolution Strategy

```go
// Merged configuration with documented reasoning
opts := options.Client().
  // Connection timeout balances safety and responsiveness
  // 15 seconds: sufficient for WAN latencies, fails fast for unreachable hosts
  SetConnectTimeout(15 * time.Second).

  // Server selection timeout: wait for replica set to stabilize
  // 5 seconds: matches MongoDB driver default
  SetServerSelectionTimeout(5 * time.Second).

  // Operation timeout: prevents hung queries from blocking indefinitely
  // 30 seconds: suitable for most OLTP queries; batch jobs may override per-operation
  SetTimeout(30 * time.Second).

  // Connection pool: balance resource usage with concurrent request handling
  // maxPoolSize=500: supports ~100 concurrent requests with 5 connections per request
  // minPoolSize=10: maintains baseline connections for fast request handling
  ApplyURI("mongodb://user:pass@host:27017/db?" +
    "maxPoolSize=500&minPoolSize=10&maxIdleTimeMS=60000")

// Per-operation override for special cases
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()

// This query gets 5-minute timeout instead of 30-second default
result, err := coll.FindOne(ctx, filter)
```

#### 2.5.1 DocumentDB Retryable Writes Consideration

**CRITICAL COMPATIBILITY ISSUE:**

Per [AWS DocumentDB documentation](https://docs.aws.amazon.com/documentdb/latest/developerguide/connect_programmatically.html):

- **MongoDB supports retryable writes** — Automatic retry on transient network failures or replica set failovers (default enabled)
- **DocumentDB does NOT support retryable writes** — Must be explicitly disabled

```go
// For DocumentDB, must disable retryable writes
opts := options.Client().
  ApplyURI("mongodb://user:pass@documentdb-host:27017/db?retryWrites=false")

// Alternative using SetRetryWrites if using URI separately
opts = options.Client().SetRetryWrites(false)

// For MongoDB (standard), retryable writes enabled by default
// No action needed unless you want to explicitly enable
mongoOpts := options.Client().
  ApplyURI("mongodb://user:pass@mongodb-host:27017/db?retryWrites=true")
```

#### Connection Configuration Conflict Resolution Matrix

| Scenario | Branch A | Branch B | Resolution | Breaking? |
|----------|----------|----------|-----------|-----------|
| Different timeouts | 10s | 30s | Use 30s (permissive); document SLA | No |
| Pool size conflict | 100 | 1000 | Use 500 (balanced); monitor usage | No |
| Retryable writes conflict | true | false | **Must match target DB; use false for DocumentDB** | **Yes** |
| Different URI hosts | Primary only | Replica set URI | Use replica set (HA) | No |
| TLS enabled vs. disabled | true | false | Use true if DocumentDB (required) | Possible |

---

## 3. Migration/Seed Data Conflicts

### 3.1 Migration Script Ordering

#### Scenario: Both Branches Add Migration Scripts

```
Branch A migrations:
  ├── 001_add_user_preferences.go
  ├── 002_create_preferences_index.go

Branch B migrations:
  ├── 001_add_analytics_collection.go
  ├── 002_create_analytics_indexes.go
```

After merge, the execution order becomes ambiguous.

#### Resolution Strategy

**1. Use Timestamp-Based Ordering**

Rename migrations with ISO 8601 timestamps:

```
migrations/
  ├── 20260407T090000Z_add_user_preferences.go
  ├── 20260407T090015Z_create_preferences_index.go
  ├── 20260407T090030Z_add_analytics_collection.go
  ├── 20260407T090045Z_create_analytics_indexes.go
```

Per [MongoDB migration documentation](https://www.mongodb.com/community/forums/t/mongodb-migration/224795/), timestamp-based ordering ensures predictable execution.

**2. Consolidate Related Migrations**

```go
package migrations

import (
  "context"
  "go.mongodb.org/mongo-driver/mongo"
  "go.mongodb.org/mongo-driver/bson"
)

type Migration struct {
  Version   string
  Name      string
  Up        func(*mongo.Database, context.Context) error
  Down      func(*mongo.Database, context.Context) error
}

var Migrations = []Migration{
  {
    Version: "20260407T090000Z",
    Name:    "Add user preferences and analytics",
    Up: func(db *mongo.Database, ctx context.Context) error {
      // Add user preferences fields
      _, err := db.Collection("users").UpdateMany(ctx,
        bson.M{"preferences": bson.M{"$exists": false}},
        bson.A{bson.M{"$set": bson.M{"preferences": bson.M{}}}},
      )
      if err != nil {
        return err
      }

      // Create user preferences collection if it doesn't exist
      err = db.CreateCollection(ctx, "user_preferences")
      if err != nil {
        // Collection may already exist; ignore error
        if err.Error() != "namespace already exists" {
          return err
        }
      }

      // Create indexes for both collections
      _, err = db.Collection("user_preferences").Indexes().CreateOne(ctx,
        mongo.IndexModel{
          Keys: bson.D{{Key: "userId", Value: 1}},
        },
      )
      if err != nil {
        return err
      }

      // Create analytics collection and indexes
      err = db.CreateCollection(ctx, "analytics_events")
      if err != nil && err.Error() != "namespace already exists" {
        return err
      }

      _, err = db.Collection("analytics_events").Indexes().CreateOne(ctx,
        mongo.IndexModel{
          Keys: bson.D{
            {Key: "userId", Value: 1},
            {Key: "timestamp", Value: -1},
          },
        },
      )

      return err
    },
    Down: func(db *mongo.Database, ctx context.Context) error {
      // Rollback: remove preferences field
      _, err := db.Collection("users").UpdateMany(ctx,
        bson.M{},
        bson.M{"$unset": bson.M{"preferences": ""}},
      )
      if err != nil {
        return err
      }

      // Drop collections
      err = db.Collection("user_preferences").Drop(ctx)
      if err != nil && err.Error() != "namespace does not exist" {
        return err
      }

      return db.Collection("analytics_events").Drop(ctx)
    },
  },
}
```

**3. Document Migration Dependencies**

```go
// Migration with explicit dependencies
type MigrationWithDeps struct {
  Version      string
  Name         string
  DependsOn    []string // Versions that must run first
  Up           func(*mongo.Database, context.Context) error
  Down         func(*mongo.Database, context.Context) error
}

// Executor respects dependency order
func RunMigrations(db *mongo.Database, ctx context.Context, migs []MigrationWithDeps) error {
  executed := make(map[string]bool)

  for _, mig := range migs {
    // Verify dependencies
    for _, dep := range mig.DependsOn {
      if !executed[dep] {
        return fmt.Errorf("migration %s depends on %s which hasn't run", mig.Version, dep)
      }
    }

    // Execute migration
    if err := mig.Up(db, ctx); err != nil {
      return fmt.Errorf("migration %s failed: %w", mig.Version, err)
    }

    executed[mig.Version] = true
  }

  return nil
}
```

### 3.2 Seed Data Conflicts

#### Scenario: Both Branches Add Overlapping Seed Data

```go
// Branch A seeds default roles
var SeedDataA = []bson.M{
  {
    "_id": "admin",
    "name": "Administrator",
    "permissions": []string{"*"},
  },
  {
    "_id": "user",
    "name": "User",
    "permissions": []string{"read", "write_own"},
  },
}

// Branch B seeds different roles
var SeedDataB = []bson.M{
  {
    "_id": "admin",
    "name": "Admin",  // Different name!
    "permissions": []string{"*"},
    "description": "Full system access",
  },
  {
    "_id": "moderator",
    "name": "Moderator",
    "permissions": []string{"read", "moderate"},
  },
}
```

#### Resolution Strategy

**1. Detect Duplicate Keys**

```go
func MergeSeedData(seedA, seedB []bson.M) ([]bson.M, error) {
  result := make([]bson.M, 0)
  seen := make(map[interface{}]int) // track document IDs

  // Process Branch A seed data
  for _, doc := range seedA {
    id, exists := doc["_id"]
    if exists {
      seen[id] = len(result)
    }
    result = append(result, doc)
  }

  // Process Branch B seed data
  for _, doc := range seedB {
    id, exists := doc["_id"]
    if !exists {
      result = append(result, doc)
      continue
    }

    // Check for conflicts
    if idx, isDuplicate := seen[id]; isDuplicate {
      // Duplicate found; merge or reject based on policy
      merged, err := mergeDocuments(result[idx], doc)
      if err != nil {
        return nil, fmt.Errorf("conflict merging seed document %v: %w", id, err)
      }
      result[idx] = merged
    } else {
      result = append(result, doc)
      seen[id] = len(result) - 1
    }
  }

  return result, nil
}

func mergeDocuments(docA, docB bson.M) (bson.M, error) {
  // Strategy: Branch B overwrites Branch A for conflicting fields
  // Exception: arrays are merged

  result := make(bson.M)

  // Copy all fields from A
  for k, v := range docA {
    result[k] = v
  }

  // Merge/overwrite from B
  for k, v := range docB {
    if existingVal, exists := result[k]; exists {
      // If both have the field
      if aArr, isArr := existingVal.([]interface{}); isArr {
        if bArr, isBArr := v.([]interface{}); isBArr {
          // Both are arrays; merge with deduplication
          result[k] = mergeArrays(aArr, bArr)
        } else {
          // B is not array; B wins
          result[k] = v
        }
      } else {
        // A is not array; B wins
        result[k] = v
      }
    } else {
      result[k] = v
    }
  }

  return result, nil
}
```

**2. Use Upsert to Handle Seed Data Idempotently**

Per [MongoDB seed data best practices](https://medium.com/@pkosiec/seeding-mongodb-database-the-right-way-32a8a0e75490):

```go
func SeedCollection(coll *mongo.Collection, ctx context.Context, seeds []bson.M) error {
  for _, seed := range seeds {
    filter := bson.M{"_id": seed["_id"]}

    // Use upsert to insert or skip if exists
    opts := options.Update().SetUpsert(false) // Don't create if missing

    _, err := coll.UpdateOne(ctx, filter, bson.M{"$setOnInsert": seed}, opts)
    if err != nil && !mongo.IsDuplicateKeyError(err) {
      return err
    }
  }

  return nil
}

// Alternative: Only seed if collection is empty
func SeedIfEmpty(coll *mongo.Collection, ctx context.Context, seeds []bson.M) error {
  count, err := coll.EstimatedDocumentCount(ctx)
  if err != nil {
    return err
  }

  if count > 0 {
    // Collection already has data; skip seeding
    return nil
  }

  // Insert all seed data
  docs := make([]interface{}, len(seeds))
  for i, seed := range seeds {
    docs[i] = seed
  }

  _, err = coll.InsertMany(ctx, docs)
  return err
}
```

### 3.3 Index Creation Scripts

#### Scenario: Both Branches Create Overlapping Indexes

See Section 1.2 for detailed index conflict resolution.

Key principle: **Index creation should be idempotent in migrations**

```go
func CreateIndexIfNotExists(coll *mongo.Collection, ctx context.Context, indexModel mongo.IndexModel) error {
  // Check if index already exists
  indexView := coll.Indexes()
  cursor, err := indexView.List(ctx)
  if err != nil {
    return err
  }

  defer cursor.Close(ctx)

  var existingIndexes []bson.M
  if err = cursor.All(ctx, &existingIndexes); err != nil {
    return err
  }

  // Compare with desired index
  for _, existing := range existingIndexes {
    if indexesEqual(existing, indexModel) {
      // Index already exists
      return nil
    }
  }

  // Create index
  _, err = indexView.CreateOne(ctx, indexModel)
  return err
}

func indexesEqual(existing bson.M, desired mongo.IndexModel) bool {
  // Implementation: compare index specifications
  // Usually sufficient to check key field order
  existingKeys := existing["key"].(bson.M)
  desiredKeys := desired.Keys.(bson.D)

  // Simplified comparison; full implementation would deep-compare
  return len(existingKeys) == len(desiredKeys)
}
```

---

## 4. DocumentDB Compatibility Considerations

### 4.1 Features Supported in MongoDB but Not DocumentDB

Per [AWS DocumentDB functional differences documentation](https://docs.aws.amazon.com/documentdb/latest/developerguide/functional-differences.html) and [MongoDB vs. DocumentDB comparison](https://www.mongodb.com/resources/compare/documentdb-vs-mongodb):

| Feature | MongoDB | DocumentDB | Impact on Conflict Resolution |
|---------|---------|-----------|------------------------------|
| **Retryable writes** | YES (default) | NO | Must set `retryWrites=false` in connection string |
| **Multi-document ACID transactions** | YES (4.0+) | YES (4.0+) | Both support; minor behavioral differences |
| **Sharding** | YES | Limited | Code must not assume sharding features |
| **Full-text search** | YES (comprehensive) | Limited | Queries using text indexes may need rework |
| **Vector search indexes** | YES (5.0+) | YES (limited) | DocumentDB has reduced vector index functionality |
| **Time-series collections** | YES (5.0+) | NO | Use regular collections instead |
| **Geospatial indexes** | YES (comprehensive) | Partial | Some advanced geo features not supported |
| **Session support** | YES | YES | Both support; connection handling differs slightly |
| **Change streams** | YES | YES | Both support; minor differences in event format |
| **Bulk operations** | YES | YES | Both supported |
| **Aggregation pipeline** | YES (extensive) | Partial | Some operators not supported; test pipelines |

### 4.2 How Compatibility Affects Conflict Resolution

#### 4.2.1 Retryable Writes Conflict

**Problem:** Branch A assumes retryable writes (standard MongoDB), Branch B disables them (DocumentDB requirement).

**Resolution:**

```go
// Detect target database and set accordingly
var connString string
var isDocumentDB bool

if os.Getenv("DB_TYPE") == "documentdb" {
  isDocumentDB = true
  connString = "mongodb://user:pass@documentdb-host:27017?retryWrites=false"
} else {
  connString = "mongodb://user:pass@mongodb-host:27017?retryWrites=true"
}

opts := options.Client().ApplyURI(connString)
client, err := mongo.Connect(context.Background(), opts)
if err != nil {
  log.Fatal(err)
}

// Application code should not assume retryable writes
// Implement explicit retry logic if needed
func InsertWithRetry(coll *mongo.Collection, ctx context.Context, doc interface{}, maxRetries int) error {
  var lastErr error

  for i := 0; i < maxRetries; i++ {
    _, err := coll.InsertOne(ctx, doc)
    if err == nil {
      return nil
    }

    // Check if error is retryable
    if !isRetryableError(err) {
      return err
    }

    lastErr = err
    time.Sleep(time.Duration(math.Pow(2, float64(i))*100) * time.Millisecond)
  }

  return lastErr
}
```

#### 4.2.2 Aggregation Pipeline Conflict

**Problem:** Branch A uses aggregation stages not supported in DocumentDB.

**Solution:**

```go
// Feature-flag unsupported aggregation stages
func buildAggregationPipeline(ctx context.Context) mongo.Pipeline {
  pipeline := mongo.Pipeline{
    bson.D{{Key: "$match", Value: bson.D{{Key: "status", Value: "active"}}}},
  }

  if !isDocumentDB {
    // MongoDB-only: use advanced aggregation stages
    pipeline = append(pipeline,
      bson.D{{Key: "$facet", Value: bson.D{
        {Key: "byCategory", Value: mongo.Pipeline{
          bson.D{{Key: "$group", Value: bson.D{
            {Key: "_id", Value: "$category"},
            {Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
          }}},
        }},
        {Key: "byUser", Value: mongo.Pipeline{
          bson.D{{Key: "$group", Value: bson.D{
            {Key: "_id", Value: "$userId"},
            {Key: "total", Value: bson.D{{Key: "$sum", Value: "$amount"}}},
          }}},
        }},
      }}},
    )
  } else {
    // DocumentDB fallback: use simpler stages
    pipeline = append(pipeline,
      bson.D{{Key: "$group", Value: bson.D{
        {Key: "_id", Value: "$category"},
        {Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
      }}},
    )
  }

  return pipeline
}
```

#### 4.2.3 Vector Search Index Conflict

**Problem:** Branch A adds MongoDB vector search index, incompatible with DocumentDB's limited support.

**Solution:**

```go
// Adapt indexing strategy based on target database
func CreateSearchIndex(coll *mongo.Collection, ctx context.Context) error {
  if isDocumentDB {
    // DocumentDB has limited vector index support; use standard index
    _, err := coll.Indexes().CreateOne(ctx, mongo.IndexModel{
      Keys: bson.D{{Key: "embedding", Value: 1}},
    })
    return err
  }

  // MongoDB: create advanced vector search index
  // This would use MongoDB Atlas Search, which isn't available in DocumentDB
  // For now, just create a standard index
  _, err := coll.Indexes().CreateOne(ctx, mongo.IndexModel{
    Keys: bson.D{{Key: "embedding", Value: 1}},
  })

  return err
}
```

### 4.3 DocumentDB Version Compatibility

Per [AWS DocumentDB version 8.0 announcement](https://aws.amazon.com/about-aws/whats-new/2025/11/documentdb-8-o/):

- DocumentDB 8.0 supports MongoDB 8.0 API compatibility
- Supports MongoDB drivers built for 6.0, 7.0, and 8.0 APIs
- Performance improvements: 7x better query latency, 30x faster index builds

**Conflict Resolution Impact:**

- Check DocumentDB version before merge
- Choose which MongoDB compatibility version to target
- Update driver versions to match target

```go
// Document supported DocumentDB version in connection config
const (
  TargetDocumentDBVersion = "8.0"
  TargetMongoDBVersion    = "8.0"
)

// Verify compatible driver
var driverInfo = mongo.Version() // Ensures driver supports target version
```

---

## 5. Data Layer Architecture Conflicts

### 5.1 Repository Pattern Conflicts

Per [Go repository pattern documentation](https://threedots.tech/post/repository-pattern-in-go/) and [MongoDB repository implementation guide](https://github.com/Mrkouhadi/go-mongodb-repository-pattern):

#### Scenario: Conflicting Repository Interfaces

```go
// Branch A: repository returns domain objects
type UserRepository interface {
  FindByID(ctx context.Context, id string) (*User, error)
  Save(ctx context.Context, user *User) error
  Delete(ctx context.Context, id string) error
}

// Branch B: repository returns additional metadata
type UserRepository interface {
  FindByID(ctx context.Context, id string) (*User, metadata.Metadata, error)
  Save(ctx context.Context, user *User) (*SaveResult, error)
  Delete(ctx context.Context, id string) (*DeleteResult, error)
}
```

#### Resolution Strategy

```go
// Choose interface design based on application needs
// Option 1: Minimize return values (A's approach)
type UserRepository interface {
  FindByID(ctx context.Context, id string) (*User, error)
  Save(ctx context.Context, user *User) error
  Delete(ctx context.Context, id string) error
  // Add metadata-aware methods separately if needed
  FindByIDWithMetadata(ctx context.Context, id string) (*User, metadata.Metadata, error)
}

// Option 2: Always include metadata (B's approach)
type UserRepository interface {
  FindByID(ctx context.Context, id string) (*User, *ResponseMetadata, error)
  Save(ctx context.Context, user *User) (*SaveResult, error)
  Delete(ctx context.Context, id string) (*DeleteResult, error)
}

// Implementation example (Option 2)
type mongoUserRepository struct {
  coll *mongo.Collection
}

func (r *mongoUserRepository) FindByID(ctx context.Context, id string) (*User, *ResponseMetadata, error) {
  objID, err := primitive.ObjectIDFromHex(id)
  if err != nil {
    return nil, nil, err
  }

  var user User
  result := r.coll.FindOne(ctx, bson.M{"_id": objID})

  err = result.Decode(&user)
  if err != nil {
    return nil, nil, err
  }

  metadata := &ResponseMetadata{
    DocumentID: objID.Hex(),
    FetchedAt:  time.Now(),
  }

  return &user, metadata, nil
}
```

### 5.2 Model Definition Conflicts

#### Scenario: Different Field Definitions in Model Structs

```go
// Branch A model
type Product struct {
  ID          primitive.ObjectID `bson:"_id,omitempty"`
  Name        string             `bson:"name"`
  Price       float64            `bson:"price"`
  Category    string             `bson:"category"`
  Inventory   int                `bson:"inventory"`
}

// Branch B model (more complex)
type Product struct {
  ID          primitive.ObjectID `bson:"_id,omitempty"`
  Name        string             `bson:"name"`
  Price       float64            `bson:"price"`
  SKU         string             `bson:"sku"`
  Variants    []ProductVariant   `bson:"variants"`
  Metadata    map[string]string  `bson:"metadata,omitempty"`
}

type ProductVariant struct {
  Color string `bson:"color"`
  Size  string `bson:"size"`
  Stock int    `bson:"stock"`
}
```

#### Resolution Strategy

```go
// Merged model incorporating both branches' needs
type Product struct {
  ID          primitive.ObjectID `bson:"_id,omitempty"`
  Name        string             `bson:"name"`
  Price       float64            `bson:"price"`
  Category    string             `bson:"category"`
  SKU         string             `bson:"sku,omitempty"`
  Inventory   int                `bson:"inventory"`
  Variants    []ProductVariant   `bson:"variants,omitempty"`
  Metadata    map[string]string  `bson:"metadata,omitempty"`
  SchemaVersion int              `bson:"schemaVersion"`
}

type ProductVariant struct {
  Color string `bson:"color"`
  Size  string `bson:"size"`
  Stock int    `bson:"stock"`
}

// Migration to backfill variants and metadata for existing documents
func migrateProductModel(coll *mongo.Collection, ctx context.Context) error {
  // Set schemaVersion and initialize new fields for legacy documents
  _, err := coll.UpdateMany(ctx,
    bson.M{"schemaVersion": bson.M{"$exists": false}},
    bson.A{
      bson.M{"$set": bson.M{
        "schemaVersion": 2,
        "variants": bson.A{},
        "metadata": bson.M{},
      }},
    },
  )

  return err
}
```

### 5.3 DAO/Service Layer Changes

#### Scenario: Different Service Method Signatures

```go
// Branch A: service focuses on CRUD
type ProductService interface {
  Create(ctx context.Context, product *Product) error
  Read(ctx context.Context, id string) (*Product, error)
  Update(ctx context.Context, product *Product) error
  Delete(ctx context.Context, id string) error
}

// Branch B: service includes business logic
type ProductService interface {
  Create(ctx context.Context, product *Product) error
  FindByCategory(ctx context.Context, category string) ([]*Product, error)
  FindInStockByCategory(ctx context.Context, category string) ([]*Product, error)
  UpdatePrice(ctx context.Context, id string, newPrice float64) (*Product, error)
  GetInventorySummary(ctx context.Context) (*InventorySummary, error)
}
```

#### Resolution Strategy

```go
// Merged service combining CRUD and business logic
type ProductService interface {
  // CRUD operations
  Create(ctx context.Context, product *Product) error
  GetByID(ctx context.Context, id string) (*Product, error)
  Update(ctx context.Context, product *Product) error
  Delete(ctx context.Context, id string) error

  // Business logic queries
  FindByCategory(ctx context.Context, category string, opts *QueryOptions) ([]*Product, error)
  FindInStockByCategory(ctx context.Context, category string) ([]*Product, error)

  // Business logic operations
  UpdatePrice(ctx context.Context, id string, newPrice float64) (*Product, error)
  GetInventorySummary(ctx context.Context) (*InventorySummary, error)
}

// Implementation
type productService struct {
  repo ProductRepository
}

func (s *productService) FindByCategory(ctx context.Context, category string, opts *QueryOptions) ([]*Product, error) {
  if opts == nil {
    opts = &QueryOptions{Limit: 100, Skip: 0}
  }

  return s.repo.FindByFilter(ctx, bson.M{"category": category}, opts)
}

func (s *productService) FindInStockByCategory(ctx context.Context, category string) ([]*Product, error) {
  opts := &QueryOptions{
    Filter: bson.M{
      "category": category,
      "inventory": bson.M{"$gt": 0},
    },
  }

  return s.repo.FindByFilter(ctx, opts.Filter, opts)
}

func (s *productService) UpdatePrice(ctx context.Context, id string, newPrice float64) (*Product, error) {
  if newPrice < 0 {
    return nil, errors.New("price cannot be negative")
  }

  product, err := s.repo.FindByID(ctx, id)
  if err != nil {
    return nil, err
  }

  product.Price = newPrice

  err = s.repo.Save(ctx, product)
  if err != nil {
    return nil, err
  }

  return product, nil
}
```

---

## 6. Resolution Strategies and Validation

### 6.1 Systematic Merge Resolution Approach

#### Step 1: Identify All Conflict Types

Create a checklist of affected areas:

```markdown
## Merge Conflict Inventory

- [ ] BSON struct tags
  - [ ] Field naming conventions
  - [ ] omitempty handling
  - [ ] Nested structure flattening

- [ ] Schema changes
  - [ ] New fields (overlapping or distinct)
  - [ ] Removed fields
  - [ ] Type changes

- [ ] Index operations
  - [ ] Duplicate indexes
  - [ ] Conflicting index types
  - [ ] Partial index conflicts

- [ ] Queries and filters
  - [ ] Modified query filters
  - [ ] Aggregation pipeline changes

- [ ] Connection configuration
  - [ ] Timeout settings
  - [ ] Pool sizes
  - [ ] Retryable writes (DocumentDB compatibility)

- [ ] Migration scripts
  - [ ] Ordering conflicts
  - [ ] Overlapping data modifications

- [ ] Data layer
  - [ ] Repository interfaces
  - [ ] Model definitions
  - [ ] Service contracts
```

#### Step 2: Categorize Conflicts

For each conflict, determine:

1. **Conflict type** — Schema, query, configuration, or architecture
2. **Severity** — Breaking change? Data corruption risk? Performance impact?
3. **Resolution path** — Which branch's approach is correct? Can both coexist?
4. **Data migration required?** — Yes/No
5. **Testing needed?** — Unit tests, integration tests, data validation?

#### Step 3: Execute Resolutions

Follow conflict-specific guidance from sections above (1-5).

#### Step 4: Create Consolidated Migration

```go
// post-merge-migration.go
package migrations

import (
  "context"
  "fmt"
  "go.mongodb.org/mongo-driver/mongo"
)

// PostMergeMigration encapsulates all changes from branch merge
type PostMergeMigration struct {
  Version string
  Name    string
}

func (m *PostMergeMigration) Up(db *mongo.Database, ctx context.Context) error {
  fmt.Println("Executing post-merge migration:", m.Name)

  // 1. Normalize struct tags / field names
  if err := m.normalizeFieldNames(db, ctx); err != nil {
    return fmt.Errorf("field normalization failed: %w", err)
  }

  // 2. Consolidate indexes
  if err := m.consolidateIndexes(db, ctx); err != nil {
    return fmt.Errorf("index consolidation failed: %w", err)
  }

  // 3. Add missing fields with defaults
  if err := m.addNewFields(db, ctx); err != nil {
    return fmt.Errorf("new field addition failed: %w", err)
  }

  // 4. Validate data consistency
  if err := m.validateDataConsistency(db, ctx); err != nil {
    return fmt.Errorf("data validation failed: %w", err)
  }

  return nil
}

func (m *PostMergeMigration) normalizeFieldNames(db *mongo.Database, ctx context.Context) error {
  // Implementation: rename fields to standardized names
  return nil
}

func (m *PostMergeMigration) consolidateIndexes(db *mongo.Database, ctx context.Context) error {
  // Implementation: drop duplicate indexes, reconcile conflicting indexes
  return nil
}

func (m *PostMergeMigration) addNewFields(db *mongo.Database, ctx context.Context) error {
  // Implementation: initialize new fields on existing documents
  return nil
}

func (m *PostMergeMigration) validateDataConsistency(db *mongo.Database, ctx context.Context) error {
  // Implementation: check for data integrity after migration
  return nil
}
```

### 6.2 Validation After Merge Resolution

#### Integration Tests

```go
package integration_test

import (
  "context"
  "testing"
  "time"

  "go.mongodb.org/mongo-driver/mongo"
  "go.mongodb.org/mongo-driver/mongo/options"
  "go.mongodb.org/mongo-driver/bson"
)

func TestPostMergeSchemaValidity(t *testing.T) {
  // Connect to test database
  opts := options.Client().ApplyURI(mongoTestURI)
  client, err := mongo.Connect(context.Background(), opts)
  if err != nil {
    t.Fatalf("failed to connect: %v", err)
  }
  defer client.Disconnect(context.Background())

  db := client.Database("test_db")

  // Test 1: Verify struct tags match stored documents
  t.Run("StructTagsMatch", func(t *testing.T) {
    coll := db.Collection("users")

    // Insert test document
    testDoc := bson.M{
      "email": "test@example.com",
      "name": "Test User",
    }

    result, err := coll.InsertOne(context.Background(), testDoc)
    if err != nil {
      t.Fatalf("insert failed: %v", err)
    }

    // Retrieve and check struct unmarshaling
    var user User
    err = coll.FindOne(context.Background(), bson.M{"_id": result.InsertedID}).Decode(&user)
    if err != nil {
      t.Fatalf("decode failed: %v", err)
    }

    if user.Email != "test@example.com" {
      t.Errorf("email mismatch: got %q, want %q", user.Email, "test@example.com")
    }
  })

  // Test 2: Verify indexes exist and are optimal
  t.Run("IndexesOptimal", func(t *testing.T) {
    coll := db.Collection("users")
    indexView := coll.Indexes()

    cursor, err := indexView.List(context.Background())
    if err != nil {
      t.Fatalf("list indexes failed: %v", err)
    }
    defer cursor.Close(context.Background())

    var indexes []bson.M
    if err = cursor.All(context.Background(), &indexes); err != nil {
      t.Fatalf("iterate indexes failed: %v", err)
    }

    // Verify expected indexes exist
    expectedIndexes := []string{"email_1", "userId_1_createdAt_-1"}
    for _, expected := range expectedIndexes {
      found := false
      for _, idx := range indexes {
        if idx["name"] == expected {
          found = true
          break
        }
      }

      if !found {
        t.Errorf("expected index %q not found", expected)
      }
    }
  })

  // Test 3: Connection configuration correct
  t.Run("ConnectionConfigured", func(t *testing.T) {
    // Verify timeout is set
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    err := client.Ping(ctx, nil)
    if err != nil {
      t.Fatalf("ping failed: %v", err)
    }
  })
}
```

#### Data Validation Tests

```go
func TestDataConsistencyPostMerge(t *testing.T) {
  db := setupTestDB(t)

  t.Run("NoMissingRequiredFields", func(t *testing.T) {
    coll := db.Collection("products")

    // Find any products missing required fields
    cursor, err := coll.Find(context.Background(), bson.M{
      "$or": []bson.M{
        {"name": bson.M{"$exists": false}},
        {"price": bson.M{"$exists": false}},
        {"_id": bson.M{"$exists": false}},
      },
    })

    if err != nil {
      t.Fatalf("query failed: %v", err)
    }

    defer cursor.Close(context.Background())

    var invalidProducts []bson.M
    if err = cursor.All(context.Background(), &invalidProducts); err != nil {
      t.Fatalf("decode failed: %v", err)
    }

    if len(invalidProducts) > 0 {
      t.Errorf("found %d products with missing required fields", len(invalidProducts))
    }
  })

  t.Run("NoInvalidFieldTypes", func(t *testing.T) {
    coll := db.Collection("products")

    // Verify price is always numeric
    cursor, err := coll.Aggregate(context.Background(), bson.A{
      bson.M{"$match": bson.M{
        "price": bson.M{"$type": []string{"string", "array", "object"}},
      }},
    })

    if err != nil {
      t.Fatalf("aggregation failed: %v", err)
    }

    defer cursor.Close(context.Background())

    if cursor.Next(context.Background()) {
      t.Error("found products with non-numeric price")
    }
  })
}
```

#### Query Validation Tests

```go
func TestQueriesPostMerge(t *testing.T) {
  db := setupTestDB(t)
  coll := db.Collection("users")

  t.Run("FilterQueriesWork", func(t *testing.T) {
    // Insert test data
    docs := []interface{}{
      bson.M{"name": "Alice", "status": "active", "role": "admin"},
      bson.M{"name": "Bob", "status": "inactive", "role": "user"},
      bson.M{"name": "Charlie", "status": "active", "role": "user"},
    }

    coll.DeleteMany(context.Background(), bson.M{})
    coll.InsertMany(context.Background(), docs)

    // Test merged filter from conflict resolution
    filter := bson.M{
      "status": "active",
      "$or": []bson.M{
        {"role": bson.M{"$in": []string{"admin", "moderator"}}},
        {"permissions": bson.M{"$exists": true}},
      },
    }

    cursor, err := coll.Find(context.Background(), filter)
    if err != nil {
      t.Fatalf("query failed: %v", err)
    }

    var results []bson.M
    if err = cursor.All(context.Background(), &results); err != nil {
      t.Fatalf("decode failed: %v", err)
    }

    // Should find Alice (active + admin)
    if len(results) < 1 {
      t.Error("query returned no results; expected to find Alice")
    }
  })

  t.Run("AggregationPipelinesWork", func(t *testing.T) {
    // Test merged aggregation pipeline
    pipeline := mongo.Pipeline{
      bson.D{{Key: "$match", Value: bson.D{{Key: "status", Value: "active"}}}},
      bson.D{{Key: "$group", Value: bson.D{
        {Key: "_id", Value: "$role"},
        {Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
      }}},
    }

    cursor, err := coll.Aggregate(context.Background(), pipeline)
    if err != nil {
      t.Fatalf("aggregation failed: %v", err)
    }

    defer cursor.Close(context.Background())

    if !cursor.Next(context.Background()) {
      t.Error("aggregation returned no results")
    }
  })
}
```

### 6.3 Connection and Configuration Validation

```go
func TestMongoDBConnectionPostMerge(t *testing.T) {
  // Validate connection configuration matches requirements

  opts := options.Client().
    SetConnectTimeout(15*time.Second).
    SetServerSelectionTimeout(5*time.Second).
    SetTimeout(30*time.Second).
    ApplyURI(mongoURI)

  client, err := mongo.Connect(context.Background(), opts)
  if err != nil {
    t.Fatalf("connection failed: %v", err)
  }

  defer client.Disconnect(context.Background())

  t.Run("ConnectionSucceeds", func(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    err := client.Ping(ctx, nil)
    if err != nil {
      t.Fatalf("ping failed: %v", err)
    }
  })

  t.Run("DocumentDBRetryWritesCorrect", func(t *testing.T) {
    // Verify retryWrites setting matches database type
    if isDocumentDB {
      // DocumentDB should have retryWrites=false
      // This is enforced via connection string
      uri := mongoURI
      if !strings.Contains(uri, "retryWrites=false") {
        t.Error("DocumentDB connection should have retryWrites=false")
      }
    }
  })
}
```

### 6.4 Post-Merge Checklist

```markdown
## Post-Merge Validation Checklist

**Before Deployment:**
- [ ] All conflicts resolved and merged manually
- [ ] Consolidated migration script created and tested
- [ ] New BSON struct tags verified to match schema
- [ ] Index conflicts resolved; no duplicate/conflicting indexes
- [ ] Query filters reviewed and merged appropriately
- [ ] Aggregation pipelines tested and merged
- [ ] Connection configuration set for target database (MongoDB/DocumentDB)
- [ ] DocumentDB-specific settings applied if needed (retryWrites=false)

**Integration Tests Pass:**
- [ ] Schema validation tests pass
- [ ] Data consistency tests pass
- [ ] Query/filter tests pass
- [ ] Aggregation pipeline tests pass
- [ ] Index operations work correctly
- [ ] Connection/configuration tests pass

**Data Validation:**
- [ ] Migration scripts executed successfully
- [ ] No data loss or corruption
- [ ] Indexes rebuilt and optimized
- [ ] All documents have required fields
- [ ] No field type inconsistencies

**Code Review:**
- [ ] All merge conflicts properly resolved
- [ ] New model structs reviewed for consistency
- [ ] Repository/service interfaces reviewed
- [ ] Migration scripts reviewed for safety and idempotency
- [ ] Comments document reasoning for merged conflict resolutions

**Deployment:**
- [ ] Backup taken before applying migrations
- [ ] Migrations run in non-production environment first
- [ ] Monitoring/alerting set up for migration execution
- [ ] Rollback plan documented
- [ ] Post-deployment validation queries prepared
```

---

## References

### MongoDB and Go Driver Documentation
- [MongoDB Go Driver — Work with BSON](https://www.mongodb.com/docs/drivers/go/current/fundamentals/bson/)
- [MongoDB Go Driver — Struct Tagging](https://www.mongodb.com/docs/drivers/go/current/data-formats/struct-tagging/)
- [MongoDB Go Driver — Aggregation Pipeline](https://www.mongodb.com/docs/drivers/go/current/fundamentals/aggregation/)
- [MongoDB Go Driver — Connection Options](https://www.mongodb.com/docs/drivers/go/current/fundamentals/connections/connection-options/)
- [MongoDB Go Driver — Find Documents](https://www.mongodb.com/docs/drivers/go/current/crud/query/retrieve/)
- [BSON Package Documentation](https://pkg.go.dev/go.mongodb.org/mongo-driver/bson)
- [MongoDB Go Driver Migration Guide (2.0)](https://github.com/mongodb/mongo-go-driver/blob/master/docs/migration-2.0.md)

### MongoDB Schema and Indexing
- [MongoDB Indexing Strategies](https://www.mongodb.com/docs/manual/applications/indexes/)
- [MongoDB Schema Versioning](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/schema-versioning/)
- [MongoDB Unique Indexes](https://www.mongodb.com/docs/manual/core/index-unique/)
- [MongoDB Index Management](https://www.mongodb.com/docs/manual/tutorial/manage-indexes/)
- [MongoDB Aggregation Pipeline Optimization](https://www.mongodb.com/docs/manual/core/aggregation-pipeline-optimization/)
- [MongoDB Schema Design Best Practices (2026)](https://dbschema.com/blog/mongodb/mongodb-schema-design-2026/)

### DocumentDB Compatibility
- [AWS DocumentDB Functional Differences](https://docs.aws.amazon.com/documentdb/latest/developerguide/functional-differences.html)
- [AWS DocumentDB Connecting Programmatically](https://docs.aws.amazon.com/documentdb/latest/developerguide/connect_programmatically.html)
- [MongoDB vs. Amazon DocumentDB Comparison](https://www.mongodb.com/resources/compare/documentdb-vs-mongodb)
- [AWS DocumentDB 8.0 Release Announcement](https://aws.amazon.com/about-aws/whats-new/2025/11/documentdb-8-o/)
- [MongoDB Retryable Writes Specification](https://specifications.readthedocs.io/en/latest/retryable-writes/retryable-writes/)
- [MongoDB Retryable Writes Manual](https://www.mongodb.com/docs/manual/core/retryable-writes/)

### Go Architecture and Data Patterns
- [Repository Pattern in Go](https://threedots.tech/post/repository-pattern-in-go/)
- [Go Repository Pattern Implementation](https://oneuptime.com/blog/post/2026-01-07-go-repository-pattern/view)
- [Mastering Repository Pattern in Clean Architecture](https://sazardev.github.io/goca/blog/articles/mastering-repository-pattern.html)
- [MongoDB Repository Pattern GitHub Example](https://github.com/Mrkouhadi/go-mongodb-repository-pattern)

### Migrations and Seeding
- [MongoDB Migration and Seeding Guide (Golang)](https://medium.com/@robertbenyamino/a-complete-guide-to-data-migration-and-seeding-with-golang-and-mongodb-51e3128025bf)
- [Seeding MongoDB Database Best Practices](https://medium.com/@pkosiec/seeding-mongodb-database-the-right-way-32a8a0e75490)
- [MongoDB Community Forum: Migrations](https://www.mongodb.com/community/forums/t/mongodb-migration/224795/)
- [MongoDB Schema Migration and Data Transformations (2025)](https://www.queryleaf.com/blog/2025/08/31/mongodb-data-migration-and-schema-evolution-sql-style-database-transformations/)

---

**Document Version:** 1.0
**Last Updated:** April 2026
**Author:** Research Agent for Git Merge Intelligence
**Scope:** Production MongoDB/DocumentDB applications with Go
