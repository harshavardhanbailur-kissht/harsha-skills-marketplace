# Comprehensive Research: File Dependency Analysis in Polyglot Repositories

## Executive Summary

Dependency analysis in polyglot repositories requires understanding how multiple languages and ecosystems track dependencies differently. Modern tools like Madge, dependency-cruiser, and Go's built-in tools provide language-specific insights, while cross-language coordination requires shared abstractions like OpenAPI, Protobuf, and JSON Schema. This research covers the state-of-the-art in dependency graph construction, circular dependency detection, and topological ordering algorithms that enable intelligent conflict resolution during merges.

---

## Part 1: TypeScript/JavaScript Dependency Analysis

### 1.1 Madge: Building Dependency Graphs from Imports

[Madge](https://github.com/pahen/madge) is a mature tool for creating visual dependency graphs and detecting circular dependencies in JavaScript and TypeScript projects. It supports CommonJS, AMD, and ES6 module formats.

#### How Madge Works

Madge operates by:

1. **Parsing Module Imports**: Uses AST (Abstract Syntax Tree) parsing to extract import/require statements from source files
2. **Module Resolution**: Leverages the `filing-cabinet` library to resolve module paths according to Node.js resolution rules and TypeScript configuration
3. **Graph Construction**: Builds a directed graph where nodes are modules and edges represent import relationships
4. **Graph Analysis**: Performs algorithms on the graph to detect cycles, orphaned modules, and dead code

#### Key Features

- **Circular Dependency Detection**: Identifies cycles by depth-first search traversal
- **Orphan Detection**: Finds modules never imported by other code
- **Multiple Output Formats**: JSON, DOT (GraphViz), plain text, and HTML visualization
- **TypeScript Support**: Requires `tsconfig.json` configuration to resolve TypeScript paths and aliases

#### Usage Example

```bash
# Detect circular dependencies
npx madge --circular src/main.ts --ts-config tsconfig.json

# Find orphaned modules
npx madge --orphans src/main.ts --ts-config tsconfig.json

# Generate JSON graph
npx madge --json src/main.ts > graph.json
```

#### Limitations

- Performance degrades on very large projects (newer tool Skott offers 7x performance improvement)
- Requires accurate `tsconfig.json` for TypeScript path resolution
- Does not understand semantic meaning of re-exports or conditional imports

### 1.2 Dependency-Cruiser: Rules-Based Dependency Checking

[dependency-cruiser](https://github.com/sverweij/dependency-cruiser) is a more sophisticated tool that validates dependencies against user-defined rules, enabling architectural constraints to be enforced programmatically.

#### Three Types of Rules

**Forbidden Rules**: Prohibit specific dependency patterns
- Applied when a dependency violates a rule, triggering an error
- Example: "views should not import from controllers"

**Allowed Rules**: Whitelist permitted dependency patterns
- Only dependencies matching at least one allowed rule are valid
- Example: "utilities may only import from other utilities"

**Required Rules**: Mandate that certain modules have specific dependencies
- Example: "every controller must depend on the base controller"

#### Configuration Pattern

```javascript
// .dependency-cruiser.js
module.exports = {
  rules: [
    {
      name: "no-view-to-controller",
      severity: "error",
      from: { path: "src/views" },
      to: { path: "src/controllers" }
    },
    {
      name: "no-circular",
      severity: "error",
      type: "cycle"
    }
  ]
};
```

#### Advantages Over Madge

- Enforces architectural constraints beyond cycle detection
- Supports path-based rules, file patterns, and dependency types
- Integration with CI/CD pipelines for automated enforcement
- Prevents "spaghetti code" patterns at the root

### 1.3 TypeScript Import Chains: Import → Re-export → Barrel File → Consumer

TypeScript dependency chains can become complex when barrel files and re-exports are involved:

#### Import Chain Structure

```
consumer.ts
  └─ imports from → index.ts (barrel file)
      └─ re-exports from → module-a.ts
      └─ re-exports from → module-b.ts
          └─ imports from → utility.ts
              └─ imports from → types.ts
```

#### The Barrel File Problem

Barrel files aggregate exports to create clean public APIs:

```typescript
// src/components/index.ts (barrel)
export * from './Button.tsx';
export * from './Input.tsx';
export * from './Modal.tsx';
```

However, importing from barrels creates deep dependency chains because:
- The barrel must be re-parsed for every import
- All re-exported modules must be type-checked transitively
- TypeScript's module resolution crawls the entire dependency tree

#### Real-World Impact

Atlassian's engineering team reported that [removing barrel files reduced build times by 75%](https://www.atlassian.com/blog/atlassian-engineering/faster-builds-when-removing-barrel-files). The issue stems from how TypeScript and bundlers process re-exports:

- Type-checker must read and parse every intermediate file
- Module bundlers lose tree-shaking opportunities with `export *` patterns
- Circular dependencies become harder to detect when hidden behind barrel re-exports

#### Recommended Pattern

Prefer explicit imports over barrel re-exports:

```typescript
// AVOID
import { Button, Input } from './components';

// PREFER
import Button from './components/Button';
import Input from './components/Input';
```

### 1.4 Circular Dependency Detection in TypeScript

Multiple specialized tools detect circular dependencies in TypeScript:

#### Tools and Approaches

1. **Madge**: Graph-based detection using DFS traversal
2. **DPDM** ([acrazing/dpdm](https://github.com/acrazing/dpdm)): Static analyzer for JavaScript and TypeScript
3. **DPDM-Fast** ([GrinZero/dpdm-fast](https://github.com/GrinZero/dpdm-fast)): Rust-based DPDM with 10x performance improvement
4. **ESLint + eslint-plugin-import**: Runtime rule `no-cycle` checks imports as code is parsed
5. **VSCode Extension**: Circular Dependencies Finder for real-time inline detection

#### Detection Algorithm

Circular dependency detection uses Depth-First Search (DFS):

1. Start from each module node
2. Recursively traverse outgoing edges (imports)
3. Track visited modules in current path
4. If revisiting a module in the current path, a cycle is detected
5. Report all cycles found

#### CI/CD Integration

Circular dependency detection is commonly integrated into GitHub Actions:

```yaml
- name: Check for circular dependencies
  run: npx madge --circular src/

- name: Build fails if cycles found
  if: failure()
```

---

## Part 2: Go Dependency Analysis

### 2.1 `go mod graph`: Module-Level Dependencies

The `go mod graph` command displays the module dependency graph at the module level, showing direct and transitive module dependencies in a format suitable for visualization and analysis.

#### Output Format

```
github.com/example/myapp github.com/lib/a@v1.0.0
github.com/lib/a@v1.0.0 github.com/lib/b@v2.0.0
github.com/lib/b@v2.0.0 github.com/lib/c@v1.5.0
```

Each line represents an edge from module A to module B, where A directly requires B.

#### Key Characteristics

- **Version-Aware**: Shows exact versions of module dependencies
- **Direct Dependencies Only**: Shows what each module explicitly requires
- **DAG Structure**: Go modules form a Directed Acyclic Graph by design
- **Minimal Version Selection**: Go selects the semantically highest version that satisfies all requirements

#### Usage for Dependency Analysis

```bash
# View full module graph
go mod graph

# Find all modules that depend on a specific module
go mod graph | grep "github.com/lib/config"

# Visualize with graphviz
go mod graph | dot -Tsvg > graph.svg
```

### 2.2 Package-Level Dependency Analysis: `go list -m all`

While `go mod graph` shows module-level dependencies, `go list -m all` provides a different perspective focused on which packages are actually used.

#### Command Behavior

```bash
# List all modules with versions
go list -m all

# Output format
github.com/example/myapp
github.com/lib/a v1.0.0
github.com/lib/b v2.0.0 // indirect
github.com/lib/c v1.5.0 // indirect
```

#### Understanding Direct vs. Indirect Dependencies

**Direct Dependencies**:
- Explicitly imported by packages in the main module
- Listed without `// indirect` comment
- Must be specified in `go.mod`

**Indirect Dependencies**:
- Transitively required by direct dependencies
- Marked with `// indirect` comment
- Added automatically by Go 1.17+ when needed for reproducibility
- Do not need explicit management in `go.mod` unless requiring different version than selected

#### Practical Analysis

```bash
# Find which packages import a specific module
go list -m -json all | jq '.[] | select(.Path | contains("config"))'

# Check for outdated dependencies
go list -u -m -json all

# Identify unused indirect dependencies
go mod graph | awk '{print $1}' | sort -u > used.txt
```

### 2.3 Internal Package Dependencies

Go enforces strict architectural boundaries through the `internal` keyword, introduced in Go 1.4.

#### Rules for Internal Packages

- Any package under an `internal/` directory can **only** be imported by packages within the same source tree
- Packages outside the source tree attempting to import from `internal/` will receive a compile error
- Enables "unexported" package-level functionality without polluting the public API

#### Example Structure

```
github.com/example/mylib/
├── internal/
│   └── utils/      # Can only be imported by packages in mylib
│       └── helpers.go
├── public/
│   └── api.go      # Can import from internal/utils
└── go.mod
```

When external code imports `github.com/example/mylib/public`, it cannot access `github.com/example/mylib/internal/utils`, enforcing clean API boundaries.

#### DAG Implications

Internal packages enforce layering:
- Public API layer depends on internal implementation layer
- No circular dependencies possible because external consumers cannot import internal packages
- Creates clear separation of concerns and maintainability

### 2.4 Go's Strict DAG: Why Import Cycles Cannot Exist

Go's build system fundamentally prevents cyclic imports at compile time.

#### Why This Matters

1. **Guaranteed Build Performance**: No cycles means the Go build system can be highly parallelizable
2. **Simpler Reasoning**: Developers know import relationships form a directed acyclic graph
3. **Prevents Class Initialization Ordering Bugs**: Unlike languages that struggle with circular dependencies

#### How Go Enforces This

```go
package a

import "example.com/b"  // Package b

// If b also imports a:
// package b
// import "example.com/a"
// → Compile error: import cycle not allowed
```

The Go compiler detects cycles during the build phase and immediately rejects the code. This forces developers to design modules with clean separation of concerns.

#### Breaking Cycles in Go

Common refactoring patterns to break cycles:

1. **Extract Common Types**: Create a third package for shared types
   ```
   a → types ← b
   ```

2. **Use Interfaces**: Invert dependencies through interfaces
   ```
   a → interface ← b (implements interface)
   ```

3. **Apply Dependency Injection**: Remove direct imports by passing dependencies
   ```
   a → factory(b) instead of a directly importing b
   ```

---

## Part 3: CSS and Tailwind Dependency Chains

### 3.1 CSS @import Chains

CSS files can form dependency chains through `@import` directives, creating similar graph structures to programming language imports.

#### @import Rules and Order

- `@import` statements must appear before all other rules (except `@charset` and empty `@layer`)
- Multiple `@import` chains can quickly become difficult to manage
- Build tools must resolve imports recursively to produce a single CSS output

#### Example Chain

```css
/* main.css */
@import './variables.css';
@import './theme.css';
@import './components.css';

/* variables.css */
@import './color-palette.css';

/* theme.css */
@import './variables.css';  /* Potential duplicate or ordering issue */
```

### 3.2 Tailwind CSS → PostCSS → Vite Dependency Chain

Modern frontend builds create complex dependency chains across configuration files.

#### Tailwind CSS v4 Built-in Import Handling

With Tailwind CSS v4, the framework handles `@import` directives natively, eliminating the need for `postcss-import` plugin in many cases. This simplifies the dependency chain.

#### Configuration Dependency Chain

```
vite.config.js
  └─ references build system
      └─ uses postcss.config.js
          └─ loads Tailwind plugin
              └─ processes tailwind.config.js
                  └─ defines theme configuration
                      └─ affects CSS variable generation
                          └─ imported by src/styles/main.css
                              └─ imported by src/index.ts
```

#### Configuration Layer Dependencies

1. **vite.config.js**: Build tool configuration (top level)
2. **postcss.config.js**: CSS transformer configuration
3. **tailwind.config.js**: Tailwind theme and variant configuration
4. **src/styles/main.css**: Entry CSS file with @tailwind directives
5. **Application source**: imports the CSS entry point

#### PostCSS @import Ordering Requirements

When manually managing @import chains:

```css
/* postcss.config.js needs postcss-import first */
module.exports = {
  plugins: [
    require('postcss-import'),  // MUST be first
    require('tailwindcss'),
    require('autoprefixer'),
  ]
}
```

Without `postcss-import` as the first plugin, subsequent `@import` statements won't be resolved correctly.

#### Separate Files Pattern

To avoid import ordering issues, separate files are created for each Tailwind layer:

```css
/* src/styles/index.css */
@import './base.css';      /* @tailwind base */
@import './components.css'; /* @tailwind components */
@import './utilities.css';  /* @tailwind utilities */
```

This pattern ensures correct cascading order and makes the dependency tree explicit and maintainable.

### 3.3 CSS Variable Inheritance Chains

CSS variables create transitive dependencies through inheritance:

```css
/* variables.css */
:root {
  --color-primary: #3b82f6;
  --color-secondary: var(--color-primary);  /* Depends on --color-primary */
}

/* theme.css */
:root {
  --button-bg: var(--color-primary);  /* Transitively depends on variables.css */
}
```

Unlike programming language imports, CSS variable chains are resolved at runtime by the browser, but source files still need correct ordering to be understandable and maintainable.

---

## Part 4: Cross-Language Dependencies in Polyglot Repositories

### 4.1 TypeScript Frontend ↔ Go Backend API Contract

Polyglot repositories require explicit contracts to coordinate between different language ecosystems.

#### API Contract as the Boundary

The HTTP API contract serves as the central dependency point:

```
TypeScript Frontend
  └─ depends on API contract
      └─ defined by OpenAPI spec or type definitions
          └─ implemented by Go Backend
              └─ depends on data models
                  └─ validated against contract
```

#### Coordination Without Shared Language

In the absence of shared type definitions:

1. **API Contract First**: Design the REST/gRPC API before implementation
2. **Specification File**: OpenAPI YAML/JSON or Protobuf definitions serve as source of truth
3. **Code Generation**: Both frontend and backend generate types from contract
4. **Bi-directional Validation**: Each side validates against contract independently

#### Example OpenAPI Contract

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
      required:
        - id
        - name
        - email
```

Both Go and TypeScript can generate type definitions from this single source:

```go
// Generated from OpenAPI spec
type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}
```

```typescript
// Generated from OpenAPI spec
interface User {
  id: string;
  name: string;
  email: string;
}
```

### 4.2 Shared Type Definitions: Protobuf, OpenAPI, JSON Schema

Multiple standards enable type sharing across language boundaries.

#### Protocol Buffers (Protobuf)

[Buf](https://buf.build/docs/bsr/module/dependency-management/) provides dependency management for Protobuf modules across polyglot projects.

**Strengths**:
- Binary format ensures version compatibility
- Generated code is available in Go, Python, Java, TypeScript, etc.
- Module system supports versioned dependencies
- gRPC integration enables strongly-typed RPC calls

**Dependency Structure**:
```proto
// api/v1/user.proto
syntax = "proto3";
package api.v1;

message User {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

Generated code depends on this single `.proto` source file.

#### OpenAPI Specification

[OpenAPI 3.0+](https://www.linkedin.com/pulse/modern-way-managing-apis-using-protobuf-openapi-alexsandro-souza/) defines REST API contracts in YAML or JSON.

**Tools for Code Generation**:
- OpenAPI Generator: Generates client libraries and server stubs in 20+ languages
- [openapi2proto](https://github.com/nytimes/openapi2proto): Converts OpenAPI specs to Protobuf schemas

**Dependency Chain**:
```
openapi.yaml (API contract)
  ├─ generates Go server types
  ├─ generates TypeScript client types
  └─ generates documentation
```

#### JSON Schema

Lightweight alternative to OpenAPI for validating JSON data structures.

**Use Cases**:
- Configuration file validation
- REST API payload validation
- Shared validation rules across languages

**Example**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "name": {"type": "string"}
  }
}
```

### 4.3 Configuration Files Affecting Multiple Languages

Configuration files often have implicit dependencies across multiple parts of the system.

#### Example Configuration Chain

```
.env (environment variables)
  ├─ referenced by Go application (via viper/envconfig)
  ├─ referenced by TypeScript frontend (via dotenv)
  └─ drives build configuration

docker-compose.yml (service configuration)
  ├─ depends on Dockerfile
  │   └─ depends on both Go and TypeScript builds
  └─ defines network topology for backend/frontend

.eslintrc.js / .prettierrc (code style)
  ├─ enforced by TypeScript linter
  └─ may conflict with Go's gofmt standards

tsconfig.json (TypeScript compilation)
  ├─ defines path aliases
  ├─ must align with bundler configuration
  └─ affects import resolution in circular dependency tools
```

### 4.4 Docker Build Dependencies

Multi-stage Docker builds create explicit dependency graphs between build stages.

#### Build Stage Dependencies

```dockerfile
# Stage 1: Build Go backend
FROM golang:1.22 AS go-builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o backend ./cmd

# Stage 2: Build TypeScript frontend
FROM node:20 AS ts-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 3: Runtime image
FROM ubuntu:22.04
COPY --from=go-builder /app/backend .
COPY --from=ts-builder /app/dist ./public
CMD ["./backend"]
```

#### Dependency Graph

```
runtime image
  ├─ depends on go-builder stage
  │   └─ depends on golang:1.22 base image
  └─ depends on ts-builder stage
      └─ depends on node:20 base image
```

Docker tracks these dependencies and parallelizes stage building where possible. COPY --from creates explicit dependencies that must be satisfied before proceeding.

---

## Part 5: Building Dependency Graphs for Conflict Resolution

### 5.1 Determining Resolution Order: Which Files MUST Be Resolved First?

Not all files in a merge conflict have equal importance. Some files must be resolved before others to maintain consistency.

#### Priority Hierarchy

**Priority 1 (Resolve First): Foundation Files**
- Type definitions (`.d.ts`, `types.ts`)
- Interface definitions
- Shared schemas (Protobuf, OpenAPI, JSON Schema)
- Package managers metadata (`package.json`, `go.mod`)
- Build configuration (`tsconfig.json`, Dockerfile)

These files define contracts that other code depends on. Resolving them first ensures downstream conflicts can be validated.

**Priority 2: Configuration Files**
- Environment configuration (`.env`, config files)
- Build system configuration (postcss.config.js, vite.config.js)
- Linting/formatting rules (.eslintrc, .prettierrc)

Configuration changes can affect how other files compile or run, so they should be resolved early.

**Priority 3: Shared Utility Code**
- Utility functions and helpers
- Constants and enumerations
- Base classes and abstract types
- Common middleware

Many other modules depend on utilities, so resolving them early prevents cascading conflicts.

**Priority 4: Business Logic Implementation**
- Controllers, handlers, services
- Component implementations
- Business logic functions

These depend on utilities and interfaces but are rarely dependencies for other code.

**Priority 5 (Resolve Last): Consumer Code**
- Tests and test fixtures
- Client code
- Integration code
- Documentation

Tests depend on nearly everything else, so resolve them last. Consumer code can be validated against resolved dependencies.

### 5.2 The DAG: From Config → Types → Implementation → Tests

A well-designed project follows this dependency ordering:

```
Configuration Layer
  ↓
Type Definition Layer
  ↓
Utility/Shared Code Layer
  ↓
Business Logic Implementation Layer
  ↓
Consumer/Test Layer
```

#### Concrete Example

```
Resolve Order:
1. package.json / go.mod
2. tsconfig.json, tailwind.config.js, go.mod
3. src/types/index.ts, src/types/api.ts
4. src/utils/string.ts, src/utils/date.ts
5. src/services/UserService.ts, handlers/userHandler.ts
6. src/components/UserProfile.tsx
7. src/components/__tests__/UserProfile.test.tsx
```

Each layer can be resolved once its dependencies are satisfied.

---

## Part 6: Kahn's Algorithm for Topological Sorting

### 6.1 Algorithm Description

[Kahn's algorithm](https://www.geeksforgeeks.org/dsa/topological-sorting-indegree-based-solution/) is a graph algorithm for producing a topological ordering of a DAG—a linear ordering where every node appears before all nodes it points to.

#### Algorithm Steps

1. **Calculate In-Degrees**: For each node, count how many incoming edges it has
   - In-degree = number of nodes that depend on this node
   - A node with in-degree 0 has no dependencies

2. **Initialize Queue**: Enqueue all nodes with in-degree 0
   - These nodes can be processed first (no prerequisites)

3. **Process Queue**:
   - Dequeue a node with in-degree 0
   - Add it to the result ordering
   - For each neighbor (node this one points to):
     - Decrease its in-degree by 1
     - If in-degree becomes 0, enqueue it

4. **Repeat**: Continue until queue is empty

#### Pseudo-Code

```
function kahnsAlgorithm(graph):
    inDegree = calculateInDegrees(graph)
    queue = Queue()

    // Step 1: Enqueue all nodes with in-degree 0
    for each node in graph:
        if inDegree[node] == 0:
            queue.enqueue(node)

    ordering = []

    // Step 2: Process nodes level by level
    while queue is not empty:
        node = queue.dequeue()
        ordering.append(node)

        // Reduce in-degree of neighbors
        for each neighbor of node:
            inDegree[neighbor] -= 1
            if inDegree[neighbor] == 0:
                queue.enqueue(neighbor)

    // Step 3: Check for cycles
    if length(ordering) != length(graph):
        return ERROR: "Graph contains a cycle"

    return ordering
```

#### Time and Space Complexity

- **Time**: O(V + E) where V = vertices (files), E = edges (dependencies)
- **Space**: O(V) for the queue and in-degree tracking
- Very efficient even for large graphs

### 6.2 Building the Adjacency List from Import Statements

To use Kahn's algorithm on source files, first build a graph from imports.

#### For TypeScript/JavaScript

```typescript
// Parse imports using AST
import * as fs from 'fs';
import * as parser from '@babel/parser';

interface DepGraph {
  [file: string]: string[];  // file → list of files it imports
}

function buildGraph(sourceDir: string): DepGraph {
    const graph: DepGraph = {};
    const files = getAllFiles(sourceDir);

    for (const file of files) {
        graph[file] = [];
        const content = fs.readFileSync(file, 'utf-8');
        const ast = parser.parse(content, {sourceType: 'module'});

        // Extract all import statements
        traverseAST(ast, (node) => {
            if (node.type === 'ImportDeclaration') {
                const importedModule = resolveModulePath(node.source.value, file);
                graph[file].push(importedModule);
            }
        });
    }

    return graph;
}
```

#### For Go

```bash
# Build graph from go list output
go list -json -all ./... | jq -r '.Imports[]' > dependencies.txt
```

Or programmatically:

```go
package main

import (
    "go/parser"
    "go/token"
)

func buildGraph(dir string) map[string][]string {
    graph := make(map[string][]string)
    fset := token.NewFileSet()

    packages, _ := parser.ParseDir(fset, dir, nil, parser.ImportsOnly)

    for pkgName, pkg := range packages {
        graph[pkgName] = []string{}
        for _, file := range pkg.Files {
            for _, imp := range file.Imports {
                graph[pkgName] = append(graph[pkgName], imp.Path.Value)
            }
        }
    }

    return graph
}
```

### 6.3 Handling Cycles in Dependency Graphs

While DAGs should not contain cycles, they sometimes do in practice due to architectural issues.

#### Cycle Detection

Before applying Kahn's algorithm, detect cycles:

```typescript
function detectCycles(graph: DepGraph): string[][] {
    const cycles: string[][] = [];
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    function dfs(node: string, path: string[]) {
        visited.add(node);
        recursionStack.add(node);
        path.push(node);

        for (const neighbor of graph[node] || []) {
            if (recursionStack.has(neighbor)) {
                // Cycle detected
                const cycleStart = path.indexOf(neighbor);
                cycles.push(path.slice(cycleStart));
            } else if (!visited.has(neighbor)) {
                dfs(neighbor, [...path]);
            }
        }

        recursionStack.delete(node);
    }

    for (const node of Object.keys(graph)) {
        if (!visited.has(node)) {
            dfs(node, []);
        }
    }

    return cycles;
}
```

#### Breaking Cycles

Common strategies to eliminate cycles:

1. **Extract Shared Types**: Move common types to a separate module
   ```typescript
   // Before: A → B → A
   // After:  A → Types ← B
   ```

2. **Use Dependency Injection**: Pass dependencies instead of importing
   ```typescript
   // Before: moduleA imports moduleB directly
   // After:  moduleA receives moduleB as constructor argument
   ```

3. **Apply Facade Pattern**: Hide circular dependencies behind a simplified interface

### 6.4 Batching: Files at the Same Level Can Be Resolved in Parallel

A key insight from topological sorting is that nodes at the same level can be processed simultaneously.

#### Kahn's Algorithm Naturally Produces Levels

```typescript
function kahnsAlgorithmWithLevels(graph: DepGraph): string[][] {
    const inDegree = calculateInDegrees(graph);
    const queue = Object.keys(graph).filter(node => inDegree[node] === 0);
    const levels: string[][] = [];

    while (queue.length > 0) {
        const currentLevel = [...queue];  // All nodes at this level
        levels.push(currentLevel);

        const nextQueue = [];

        for (const node of currentLevel) {
            for (const neighbor of graph[node] || []) {
                inDegree[neighbor]--;
                if (inDegree[neighbor] === 0) {
                    nextQueue.push(neighbor);
                }
            }
        }

        queue = nextQueue;
    }

    return levels;
}
```

#### Practical Application

In merge conflict resolution:

```
Level 1: [package.json, go.mod, tsconfig.json]
  ↓ (all can be resolved in parallel)
Level 2: [types.ts, interfaces.ts, config.ts]
  ↓ (all can be resolved in parallel)
Level 3: [utils.ts, helpers.ts]
  ↓ (all can be resolved in parallel)
Level 4: [UserService.ts, ProductService.ts]
  ↓ (all can be resolved in parallel)
Level 5: [components/User.tsx, components/Product.tsx]
  ↓
Level 6: [tests/User.test.tsx, tests/Product.test.tsx]
```

Files at the same level have no dependency relationships with each other, enabling parallel resolution.

---

## Part 7: Practical Heuristics for Dependency Ordering

### 7.1 Package Managers First: `package.json` / `go.mod`

**Always resolve package manager metadata first.**

These files define which external dependencies are available. All other resolutions depend on knowing which modules are present.

**Why**:
- Defines the entire module graph
- Changes to dependencies affect build configuration
- Version constraints affect compatibility checks

**Resolution Strategy**:
```
1. Merge package.json / go.mod
2. Run dependency installation/validation (npm install, go mod tidy)
3. Verify lock file consistency
4. Only then resolve other files
```

### 7.2 Type Definitions Before Implementations

**Core Rule**: All type definitions must be resolved before any implementation code.

This ensures that type-checking, imports, and circular dependency detection can be done correctly on implementation code.

**Examples**:
- `src/types/index.ts` before `src/services/UserService.ts`
- `internal/models/user.go` before `internal/handlers/user_handler.go`
- `.d.ts` declaration files before corresponding `.js` implementations

**Why This Order**:
- Type checker needs type definitions available before checking implementations
- Circular dependency detection requires knowing all exported types
- Build tools can properly resolve type imports

### 7.3 Utilities and Shared Code Before Consumers

**Rule**: Dependency direction should flow downward: utilities are used by higher-level code, not vice versa.

**Priority Order**:
1. Constants and enumerations
2. Type utilities and type guards
3. String/date/math utilities
4. Base classes and abstract types
5. Middleware and decorators
6. Service layer
7. Component/controller layer
8. Integration and consumer code

**Example**:
```
1. src/utils/string.ts
2. src/utils/validation.ts
3. src/services/UserService.ts (depends on utils)
4. src/handlers/UserHandler.ts (depends on services)
5. src/routes.ts (depends on handlers)
6. tests/ (depends on everything)
```

### 7.4 Tests and Spec Files Always Last

**Rule**: Never resolve test files until all production code is resolved.

Tests depend on production code, not the reverse. Resolving tests prematurely can mask issues in production code.

**Test Resolution Strategy**:
1. All source files resolved first
2. Test files validated against resolved source
3. New test assertions validated against type definitions
4. Integration tests resolved last (they depend on all other tests and source)

### 7.5 Configuration Files: Position by Impact Scope

**Local Scope** (single file or directory):
- Resolve early (before the code using them)
- Example: `.eslintrc` affecting `src/components/`

**Project Scope** (entire project):
- Resolve after package managers but before most source code
- Example: `tsconfig.json`, `jest.config.js`

**System Scope** (build process):
- Resolve first (after package.json)
- Example: `Dockerfile`, `vite.config.js`, `postcss.config.js`

**Resolution Order**:
```
1. package.json / go.mod
2. Dockerfile, vite.config.js, webpack.config.js (system scope)
3. tsconfig.json, jest.config.js, .babelrc (project scope)
4. Source types
5. Source implementation
6. .eslintrc in affected directories (local scope)
7. Tests
```

### 7.6 Environment and Configuration Variables

**.env files** have subtle ordering implications:

- Build-time configuration affects which code is compiled
- Runtime configuration affects execution
- Different environments (.env.development, .env.production) may have incompatible keys

**Strategy**:
```
1. Resolve .env.example (defines schema)
2. Resolve .env files (if conflicting, check against example)
3. Verify all required keys are present
4. Only then resolve code that reads from .env
```

---

## Part 8: Practical Implementation Examples

### 8.1 Building a Conflict Resolution Analyzer

This example shows a practical tool that analyzes merge conflicts using Kahn's algorithm:

```typescript
import fs from 'fs';
import path from 'path';

interface ConflictFile {
  path: string;
  priority: number;
  dependencies: string[];
}

interface AnalysisResult {
  resolutionOrder: ConflictFile[];
  parallelBatches: ConflictFile[][];
  circularDependencies: string[][];
}

function analyzeConflictedFiles(files: string[]): AnalysisResult {
  // Step 1: Build dependency graph
  const graph = buildDependencyGraph(files);

  // Step 2: Assign base priorities
  const priorities = assignBasePriorities(files);

  // Step 3: Detect cycles
  const cycles = detectCycles(graph);
  if (cycles.length > 0) {
    console.warn('⚠️ Circular dependencies detected:', cycles);
  }

  // Step 4: Apply Kahn's algorithm
  const parallelBatches = kahnsAlgorithmWithLevels(graph);

  // Step 5: Flatten to ordered list
  const resolutionOrder = flattenWithPriorities(
    parallelBatches,
    priorities
  );

  return {
    resolutionOrder,
    parallelBatches,
    circularDependencies: cycles
  };
}

function assignBasePriorities(files: string[]): Map<string, number> {
  const priorities = new Map<string, number>();

  for (const file of files) {
    if (file.includes('package.json') || file.includes('go.mod')) {
      priorities.set(file, 100);  // Highest priority
    } else if (file.endsWith('.d.ts') || file.includes('types/')) {
      priorities.set(file, 80);
    } else if (file.includes('config.') || file.includes('.env')) {
      priorities.set(file, 70);
    } else if (file.includes('utils/') || file.includes('helpers/')) {
      priorities.set(file, 50);
    } else if (file.includes('.test.') || file.includes('.spec.')) {
      priorities.set(file, 10);   // Lowest priority
    } else {
      priorities.set(file, 30);   // Default: implementation
    }
  }

  return priorities;
}

function flattenWithPriorities(
  batches: string[][],
  priorities: Map<string, number>
): ConflictFile[] {
  const result: ConflictFile[] = [];

  for (const batch of batches) {
    // Within same priority level, sort by priority
    const sorted = batch.sort((a, b) => {
      return (priorities.get(b) || 0) - (priorities.get(a) || 0);
    });

    for (const file of sorted) {
      result.push({
        path: file,
        priority: priorities.get(file) || 0,
        dependencies: [] // Would populate from graph
      });
    }
  }

  return result;
}
```

---

## Summary: Key Takeaways

1. **Language-Specific Tools Matter**: Madge, dependency-cruiser, and Go's built-in tools provide irreplaceable insights into each ecosystem's dependency structure.

2. **Barrel Files Are Expensive**: Re-export patterns create deep dependency chains that slow builds and complicate dependency analysis—prefer explicit imports.

3. **Shared Contracts Enable Polyglot Repos**: OpenAPI, Protobuf, and JSON Schema serve as lingua francas for cross-language coordination.

4. **Kahn's Algorithm Scales**: Topological sorting produces both linear resolution order and parallel processing batches—critical for merge conflict resolution.

5. **Priority is Predictable**: Foundation files (types, config, package managers) always resolve first; consumer code (tests) always last.

6. **Cycles Must Be Eliminated**: Go enforces this by design, but TypeScript/JavaScript require explicit tools and architectural discipline.

7. **Configuration Order Matters**: System-scope configs resolve before project-scope, which resolve before file-specific configurations.

8. **Parallelization Opportunities Exist**: Nodes at the same topological level have no dependency relationships and can be processed simultaneously, enabling faster merge resolution.

---

## References and Further Reading

- [madge - GitHub](https://github.com/pahen/madge)
- [dependency-cruiser - GitHub](https://github.com/sverweij/dependency-cruiser)
- [Go Modules Documentation](https://go.dev/doc/modules)
- [Tailwind CSS Installation Guide](https://tailwindcss.com/docs)
- [Buf - Protocol Buffer Management](https://buf.build/)
- [Kahn's Algorithm - GeeksforGeeks](https://www.geeksforgeeks.org/dsa/topological-sorting-indegree-based-solution/)
- [Atlassian Engineering: 75% Faster Builds by Removing Barrel Files](https://www.atlassian.com/blog/atlassian-engineering/faster-builds-when-removing-barrel-files)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Go Internal Packages - DEV Community](https://dev.to/stefanalfbo/internal-packages-in-go-2h9)
- [TypeScript Circular Dependencies](https://javascript.plainenglish.io/detect-prevent-and-fix-circular-dependencies-in-javascript-and-typescript-7d9819d37ce2)
