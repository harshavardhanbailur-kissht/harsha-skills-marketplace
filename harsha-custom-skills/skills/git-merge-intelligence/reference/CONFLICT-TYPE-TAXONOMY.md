# Conflict Type Taxonomy

Classification system for merge conflicts. Load during Phase 2 (Triage).

---

## Conflict Types

### 1. ADDITIVE

**Definition**: Both branches add new, non-overlapping code to the same region.

**Detection**:
- Base version is a subset of both ours and theirs
- No common deletions between the branches
- New code blocks are structurally independent

**Examples**:
- Both branches add different import statements
- Both branches add different functions to the same file
- Both branches add different fields to the same interface

**Default Strategy**: `KEEP_BOTH`

**Risk Level**: LOW — Typically safe to merge both additions.

**Watch For**:
- Duplicate function names or variable names
- Import collisions (two packages with same default export name)
- Enum members with same numeric value

```
Detection heuristic:
  ours_additions = ours_lines - base_lines
  theirs_additions = theirs_lines - base_lines
  ours_deletions = base_lines - ours_lines
  
  IF ours_additions AND theirs_additions AND NOT ours_deletions:
    → ADDITIVE
```

---

### 2. MODIFY_SAME

**Definition**: Both branches modify the same lines of code differently.

**Detection**:
- All three versions (base, ours, theirs) differ
- Overlapping line modifications exist
- Git conflict markers span the modified region

**Examples**:
- Both branches change a function's implementation
- Both branches modify the same configuration value
- Both branches update the same API endpoint handler

**Default Strategy**: `MANUAL_MERGE`

**Risk Level**: MEDIUM to HIGH — Requires understanding intent of both changes.

**Watch For**:
- Semantic conflicts hidden within textual conflicts
- Type narrowing vs widening conflicts
- Side-effect ordering changes

```
Detection heuristic:
  overlap_modifications = (ours_changes ∩ theirs_changes)
  
  IF overlap_modifications AND base ≠ ours AND base ≠ theirs AND ours ≠ theirs:
    → MODIFY_SAME
```

---

### 3. DELETE_MODIFY

**Definition**: One branch deletes code that the other branch modified.

**Detection**:
- One version (ours or theirs) is missing lines present in base
- The other version modifies those same lines
- Git reports as modify/delete conflict

**Examples**:
- Branch A deletes a deprecated function; Branch B adds error handling to it
- Branch A removes a component; Branch B adds props to it
- Branch A removes a config section; Branch B modifies values in it

**Default Strategy**: `DEEP_THINK`

**Risk Level**: HIGH — Deletion intent must be understood. Was the code:
- Moved to another file? (check renames)
- Replaced by a different implementation?
- Truly deprecated and safe to remove?

**Watch For**:
- Code moved, not deleted (check other files in the same branch)
- Feature flags that disable code (soft delete vs hard delete)
- Deprecation vs removal

```
Detection:
  IF base_has_content AND (ours_missing OR theirs_missing):
    → DELETE_MODIFY
```

---

### 4. RENAME_MODIFY

**Definition**: One branch renames a file while the other modifies its content.

**Detection**:
- Git detects rename via similarity threshold
- `git diff --name-status` shows `R` (rename) for one branch
- Content changes exist in the renamed file

**Examples**:
- Branch A renames `utils.ts` to `helpers.ts`; Branch B adds a function to `utils.ts`
- Branch A moves `src/api/users.go` to `internal/api/users.go`; Branch B changes the handler

**Default Strategy**: `DEEP_THINK`

**Risk Level**: HIGH — Must resolve both the path and content simultaneously.

**Resolution Approach**:
1. Accept the rename (new path)
2. Apply content modifications to the renamed file
3. Update all import/require paths that reference the old name

```
Detection:
  IF git_status shows 'R' AND content_differs:
    → RENAME_MODIFY
```

---

### 5. SEMANTIC

**Definition**: Code compiles after merge but has semantic incompatibilities.

**Detection**:
- No textual conflict (Git merges cleanly OR textual conflict masks semantic issue)
- Type contracts violated across module boundaries
- Function behavior changed in incompatible ways

**Examples**:
- Branch A changes `calculateTotal()` return type from `number` to `{amount: number, tax: number}`; Branch B calls `calculateTotal() + fee` (was valid, now type error)
- Branch A removes a side effect from function X; Branch B adds code depending on that side effect
- Branch A changes enum value assignments; Branch B adds switch cases using old values

**Default Strategy**: `DEEP_THINK`

**Risk Level**: CRITICAL — These are the hardest conflicts to detect and the most dangerous.

**Detection Methods**:
- Run `tsc --noEmit` after textual resolution
- Check function signature changes against call sites
- Verify interface satisfaction after struct/type merging
- Compare side-effect chains (function call ordering)

```
Detection:
  IF textual_merge_succeeds BUT (
    type_check_fails OR
    interface_unsatisfied OR
    call_signature_mismatch
  ):
    → SEMANTIC
```

---

### 6. CONFIG

**Definition**: Configuration file conflict (JSON, YAML, TOML, dotfiles).

**Detection**:
- File extension is `.json`, `.yaml`, `.yml`, `.toml`, `.cfg`, `.ini`
- OR file is a known config file (`tsconfig.json`, `docker-compose.yml`, etc.)
- NOT a lockfile

**Examples**:
- Both branches modify `tsconfig.json` compiler options
- Both branches add different services to `docker-compose.yml`
- Both branches change CI pipeline steps

**Default Strategy**: `MANUAL_MERGE` (deep merge where possible)

**Risk Level**: MEDIUM — Config errors can break builds silently.

**Resolution Approach**:
- JSON/YAML: Parse both versions, deep merge, validate schema
- Docker: Merge services, volumes, networks
- CI: Keep all unique steps, merge shared steps

```
Detection:
  IF extension IN [json, yaml, yml, toml, cfg, ini] AND NOT lockfile:
    → CONFIG
```

---

### 7. LOCKFILE

**Definition**: Package manager lock file or checksum file.

**Detection**:
- File is one of: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `poetry.lock`, `Cargo.lock`, `Gemfile.lock`, `composer.lock`

**Default Strategy**: `REGENERATE` — Never merge manually.

**Risk Level**: LOW (when regenerated) / CRITICAL (when merged manually)

**Resolution**: 
1. Accept our version of the manifest file (`package.json`, `go.mod`, etc.)
2. Delete the lockfile
3. Regenerate: `npm install` / `go mod tidy` / `poetry lock` / `cargo generate-lockfile`

**HARD RULE**: Never attempt to manually resolve lockfile conflicts. The hash/checksum data is computed, not authored.

```
Detection:
  IF filename IN known_lockfile_names:
    → LOCKFILE
```

---

### 8. AUTH_SECURITY

**Definition**: Conflict in authentication, authorization, cryptography, or security-critical code.

**Detection**:
- File path contains: `auth`, `security`, `permission`, `rbac`, `acl`, `crypto`, `jwt`, `oauth`, `session`, `token`
- OR file handles: password hashing, API key validation, CORS policy, CSP headers, rate limiting
- AND language is executable (not docs/markdown)

**Default Strategy**: `DEEP_THINK` — Always invoke multi-expert analysis.

**Risk Level**: CRITICAL — Security bugs in merge resolution can create vulnerabilities.

**Resolution Approach**:
1. NEVER auto-resolve auth code
2. Present both versions to Deep Thinker with full context
3. Invoke Security Expert on the panel
4. If confidence < 70%, present to human with explicit security questions
5. Document the security implications of the chosen resolution

**Watch For**:
- JWT algorithm changes (HS256 → RS256)
- Token expiration changes
- Password hashing algorithm changes (bcrypt rounds)
- CORS origin allowlist changes
- Rate limit threshold changes
- Role/permission enum changes

```
Detection:
  IF path_contains_security_keywords AND language IS executable:
    → AUTH_SECURITY
```

---

## Conflict Type Priority Order

When a file matches multiple types, use the highest-priority classification:

```
AUTH_SECURITY  (highest — security always wins)
    ↓
SEMANTIC       (compile-but-broken)
    ↓
LOCKFILE       (special handling required)
    ↓
DELETE_MODIFY   (high risk)
    ↓
RENAME_MODIFY   (path + content resolution)
    ↓
MODIFY_SAME    (standard conflict)
    ↓
CONFIG         (config file handling)
    ↓
ADDITIVE       (lowest risk)
```

---

## Complexity Matrix

| Type × Size | < 50 lines | 50-200 lines | 200+ lines |
|-------------|-----------|-------------|-----------|
| ADDITIVE | TRIVIAL | MODERATE | MODERATE |
| MODIFY_SAME | MODERATE | MODERATE | COMPLEX |
| DELETE_MODIFY | COMPLEX | COMPLEX | COMPLEX |
| RENAME_MODIFY | COMPLEX | COMPLEX | COMPLEX |
| SEMANTIC | CRITICAL | CRITICAL | CRITICAL |
| CONFIG | MODERATE | MODERATE | COMPLEX |
| LOCKFILE | CRITICAL | CRITICAL | CRITICAL |
| AUTH_SECURITY | CRITICAL | CRITICAL | CRITICAL |

---

## References
- semantic-conflict-patterns.md (Sections 1-8: Full Taxonomy)
- git-conflict-anatomy.md (Sections 3-5: Conflict Types)
- ai-merge-resolution-research.md (Sections 2-4: Classification Methods)
