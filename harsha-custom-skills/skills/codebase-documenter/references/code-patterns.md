# Code Patterns Reference

## Architectural Pattern Detection Framework

### MVC (Model-View-Controller)
**Detection markers:**
- Separate directories/packages: `models/`, `views/`, `controllers/`
- Controller classes handling HTTP routing
- Models with data persistence logic
- Views with template files (.jsx, .erb, .html.j2)
- Command: grep for "class.*Controller\|@route\|@app.get"

**Implementation patterns by language:**
- **Python**: Django/Flask with `models.py`, `views.py`, `urls.py`
- **JavaScript**: Express with `routes/`, `controllers/`, `models/`
- **Rails**: Convention-based `app/models`, `app/controllers`, `app/views`

**Confidence scoring:**
- Explicit directory structure: +40 points
- Routing annotations: +20 points
- Dependency flow (Model ← View ← Controller): +25 points
- Tests confirming MVC responsibility separation: +15 points
- Score > 80 = High confidence

**Why this might be wrong:** MVC assumes unidirectional data flow that rarely holds in complex systems. View layer often needs to query multiple models directly (data access abstraction failure). Controllers become fat orchestrators instead of thin routers.

**Better alternative:** Consider hexagonal architecture where "View" is just an adapter, or MVVM where data binding replaces controller logic.

---

### Microservices Pattern
**Detection markers:**
- Multiple independent deployable units in separate repos/directories
- Inter-service communication: HTTP (REST/gRPC), message queues, events
- Separate databases per service
- API gateway or service mesh references
- Independent build/deployment configs (docker-compose, k8s manifests)

**Service boundary identification:**
- Language/framework changes between modules (polyglot indicator)
- Separate dependency trees (package.json, requirements.txt, go.mod)
- Cross-service calls via environment variables or service discovery

**Confidence scoring:**
- Separate git repos: +35 points
- Docker/K8s per service: +25 points
- Async communication (queues/events): +20 points
- Service-to-service API contracts: +15 points
- Deployment isolation: +5 points
- Score > 70 = High confidence

**Keyword patterns:**
```
service.*client|grpc.*stub|http.*request|queue.*consumer|event.*listener
```

**Why this might be wrong:** Microservices introduces distributed system complexity (eventual consistency, partial failures, cascading latency). Justified only with 10+ services and autonomous teams. Many codebases are "distributed monoliths" with tight coupling despite physical separation.

**Better alternative:** Modular monolith with clear package boundaries, deploy together until you have operational evidence justifying separation.

---

### Event-Driven Architecture
**Detection markers:**
- Message brokers: Kafka, RabbitMQ, AWS SNS/SQS, Google Pub/Sub, NATS
- Event publisher patterns: `.publish()`, `.emit()`, `.send_event()`
- Event listener patterns: `.subscribe()`, `.on()`, `@event_handler`, `@consumer`
- Event schema/contract files (Avro, Protobuf, JSON Schema)
- Domain event types as dedicated classes/interfaces

**Event flow analysis:**
1. Find all `.publish(` or `.emit(` calls
2. Trace consumer registration
3. Identify event ordering guarantees (exactly-once vs at-least-once)
4. Detect saga patterns (multi-step event chains)

**Confidence scoring:**
- Message broker integration: +30 points
- Event schema definitions: +25 points
- Multiple consumers per event: +20 points
- Async execution patterns: +15 points
- Score > 60 = High confidence

**Why this might be wrong:** Event-driven systems are notoriously difficult to debug and trace. Event ordering assumptions often break. Dead-letter queues hint at undocumented failure modes. May introduce unnecessary latency compared to synchronous RPCs.

**Better alternative:** Hybrid approach: synchronous for critical paths (checkout), asynchronous for analytics/notifications.

---

### CQRS (Command Query Responsibility Segregation)
**Detection markers:**
- Separate command and query paths/handlers
- Write model differs from read model
- Command handlers validate/persist changes
- Query handlers read from denormalized views
- Event sourcing alongside CQRS (audit trail of all commands)
- Separate databases: write DB, read replicas or materialized views

**Implementation patterns:**
```python
# Python example
class CreateOrderCommand: ...
class OrderCommandHandler:
    def handle(self, cmd: CreateOrderCommand) -> OrderId: ...
class GetOrderQuery: ...
class OrderQueryHandler:
    def handle(self, query: GetOrderQuery) -> OrderDTO: ...
```

**Confidence scoring:**
- Explicit Command/Query handler separation: +35 points
- Separate read/write data stores: +25 points
- Eventual consistency handling: +20 points
- Command result types differ from Query return types: +15 points
- Score > 75 = High confidence

**Why this might be wrong:** CQRS introduces significant complexity with eventual consistency bugs. Read model synchronization failures cause stale data incidents. Justified only for high-read, complex-write domains. Premature CQRS is common overengineering.

**Better alternative:** Transactional consistency with smart indexing. CQRS only if operational metrics show divergence is acceptable.

---

### Saga Pattern (Distributed Transactions)
**Detection markers:**
- Multi-step workflows across services
- Compensation logic (rollback handlers)
- State machine tracking transaction status (Pending → Processing → Completed/Failed)
- Orchestrator or choreography patterns:
  - **Orchestrator**: Central service coordinates steps
  - **Choreography**: Services emit events triggering next step

**Detection queries:**
```
grep -r "compensate\|rollback\|saga\|transaction.*step\|orchestrat"
```

**Saga types:**
1. **Orchestration-based**: Controller service makes decisions
2. **Choreography-based**: Services react to events

**Confidence scoring:**
- Explicit saga pattern code/comments: +40 points
- Compensation handlers present: +25 points
- Transaction state machine: +20 points
- Cross-service coordination: +15 points
- Score > 80 = High confidence

**Why this might be wrong:** Sagas are notoriously hard to reason about. Compensating transactions may not truly restore state (idempotency failures). Saga failure recovery is complex. Event ordering issues cause inconsistency.

**Better alternative:** Redesign to eliminate distributed transactions. Keep related data together (domain-driven boundaries).

---

### Two-Phase Commit (2PC)
**Detection markers:**
- Explicit "prepare" phase before "commit"
- Transaction coordinator pattern
- Database-level 2PC calls
- XA transactions or equivalent
- Voting mechanism for transaction readiness

**Why this is problematic:** 2PC blocks resources during prepare phase. Single resource failure blocks entire transaction. Poor performance under network partitions.

**Better alternative:** Saga pattern with compensations, or redesign to avoid distributed transactions.

---

### Hexagonal Architecture (Ports & Adapters)
**Detection markers:**
- Core domain isolated from infrastructure
- Ports: interfaces defining domain→external contracts
- Adapters: implementations of ports for specific technologies
- Dependency inversion: domain doesn't depend on adapters
- Clear input/output boundaries

**Directory structure:**
```
src/
  domain/          # Core business logic (language-agnostic)
  ports/           # Interfaces (Repository, MessageBus, Logger)
  adapters/        # Implementations (PostgresRepository, KafkaMessageBus)
  applications/    # Use cases binding domain + adapters
```

**Confidence scoring:**
- Domain logic isolated in separate layer: +35 points
- Port interfaces defined: +25 points
- Multiple adapter implementations per port: +20 points
- Dependency inversion (domain points inward): +15 points
- Test ports used for testing: +5 points
- Score > 80 = High confidence

**Why this might be wrong:** Creates abstraction overhead. Simple projects don't benefit from multiple adapters. May encourage premature generalization.

**Better alternative:** Simpler onion architecture or layered for small codebases.

---

### Clean Architecture
**Detection markers:**
- Layer separation: Entities → Use Cases → Interface Adapters → Frameworks
- Entities: Core business objects
- Use Cases: Business rules orchestration
- Interface Adapters: Translate between use cases and external systems
- Frameworks: UI, databases, web frameworks
- Dependency rule: Dependencies point inward only

**Confidence scoring:**
- Clear layer separation: +30 points
- Dependency inversion compliance: +25 points
- Entity independence from frameworks: +20 points
- Use case orchestration patterns: +15 points
- Score > 70 = High confidence

**Why this might be wrong:** Dogmatic layering can add excessive indirection. Layer count (5+ layers) causes tunnel vision—easy to miss cross-layer concerns.

**Better alternative:** Pragmatic hexagonal with 3 layers: domain, port, adapter.

---

## Anti-Pattern Detection

### God Objects
**Detection indicators:**
- Class with 1000+ lines of code
- 50+ public methods
- Handles multiple unrelated responsibilities
- Used by many different clients for different purposes

**Analysis approach:**
```bash
# Find large classes
find . -name "*.py" -exec wc -l {} + | sort -rn | head -20
grep -r "class\|def " | awk -F: '{file=$1; count++} END {print file, count}' | sort -k2 -rn
```

**Why it's problematic:** Testing any feature requires testing entire god object. Changes to unrelated features impact all users. Change propagation is unpredictable.

**Remediation:** Extract cohesive responsibilities into separate classes. Use single responsibility principle to identify extraction points.

---

### Circular Dependencies
**Detection approach:**
1. Build dependency graph (imports/requires)
2. Find cycles: A → B → C → A
3. Identify cycle participants

**Language-specific tools:**
- **Python**: `pydeps` graphviz output, manual import trace
- **JavaScript**: `madge` or `eslint-plugin-import` cycle detection
- **Go**: `goda` for cycle analysis
- **Java**: CheckStyle or manual Maven dependency tree

**Impact scoring:**
- Bidirectional imports: -20 points architectural purity
- Tight coupling indicated: Risk level High
- Testing difficulty: Need to stub/mock more extensively

**Remediation:** Extract shared abstractions, or find the "lower" layer and make it depend up.

---

### Deep Coupling
**Detection markers:**
- Client code accessing nested properties: `obj.sub.deep.value`
- Multiple levels of inheritance (3+ generations)
- Classes depending on implementation details instead of abstractions
- Service layer directly accessing database layer (skipping repository pattern)

**Measurement:**
- Depth: Count property access levels
- Breadth: Count total dependencies per class
- Brittleness: Calculate ratio of test changes per code change

**Why it's problematic:** Changes to intermediate layers break multiple levels. Tests must construct entire object trees.

**Remediation:** Extract intermediate abstractions. Hide implementation details behind interfaces.

---

### Missing Abstraction
**Detection markers:**
- Same conditional logic repeated in multiple methods
- Multiple clients checking `.type` field or `isinstance(obj, Type)`
- Duplicate parameter passing through multiple function levels
- Copy-pasted similar but slightly different code

**Example:**
```python
# Missing abstraction: clients check concrete type
if isinstance(payment, CreditCard):
    process_credit_card(payment)
elif isinstance(payment, PayPal):
    process_paypal(payment)

# Should be:
payment.process()  # Polymorphic
```

**Remediation:** Extract interface/base class. Move conditional logic into polymorphic dispatch.

---

## Language-Specific Idiom Detection

### Python Idioms
- Decorator usage: `@property`, `@classmethod`, `@contextmanager`
- Context managers: `with` statements for resource management
- Generator patterns: `yield` for lazy evaluation
- Dataclass/NamedTuple usage indicating immutability intent
- Type hints presence (Python 3.5+) indicating intent for static analysis

### JavaScript/TypeScript Idioms
- Async/await vs Promise chains vs callbacks (modernness indicator)
- Type definitions (TypeScript) vs JSDoc comments
- Module patterns: CommonJS vs ES6 modules
- Dependency injection vs global state
- React hooks vs class components (version intent)

### Go Idioms
- Error handling: `if err != nil` pervasiveness
- Interface-based design (no inheritance)
- Goroutine/channel patterns for concurrency
- Package organization by feature vs by layer

### Rust Idioms
- Ownership model enforcement (borrow checker)
- Result<T, E> vs Option<T> for error handling
- Trait-based polymorphism
- Unsafe blocks and justification

### Java Idioms
- Dependency injection frameworks (Spring, Guice)
- Stream API usage (Java 8+)
- Sealed classes vs inheritance (Java 17+)
- Record types for data carriers (Java 14+)

---

## Design Pattern Recognition with Confidence Scoring

### Singleton Pattern
**Markers:**
- Static instance holder: `public static final MyClass INSTANCE`
- Private constructor preventing instantiation
- Thread-safe initialization (double-checked locking or eager)

**Confidence calculation:**
- Private constructor: +30 points
- Static instance: +30 points
- Thread-safe initialization: +20 points
- Accessor method: +20 points
- Score > 70 = Detected singleton

**Why it's problematic:** Singletons hide dependencies. Difficult to test (global state). Breaks dependency injection patterns.

**Better alternative:** Dependency injection of single instance.

---

### Factory Pattern
**Markers:**
- Method returning object: `createFoo()`, `FooFactory.make()`
- Parameter-driven type selection
- Encapsulates instantiation logic
- Often used with abstract classes/interfaces

**Confidence scoring:**
- Factory method/class exists: +30 points
- Returns interface/abstract type: +25 points
- Constructor is private/hidden: +20 points
- Parameter determines concrete type: +25 points
- Score > 70 = Detected factory

**Practical use:** Verify factory reduces client coupling to concrete classes.

---

### Strategy Pattern
**Markers:**
- Strategy interface/abstract class defining behavior
- Multiple implementations of strategy
- Context class accepting strategy as dependency
- Runtime strategy selection

**Confidence scoring:**
- Common interface among implementations: +35 points
- Context uses strategy polymorphically: +30 points
- Multiple concrete strategies: +20 points
- No conditional logic in context: +15 points
- Score > 80 = High confidence

---

### Observer Pattern
**Markers:**
- Subject maintaining list of observers
- Observers registering with subject
- Subject notifying observers on state change
- Event/listener terminology

**Confidence scoring:**
- Explicit observer list: +30 points
- Subscribe/notify methods: +30 points
- Multiple observer implementations: +20 points
- Decoupled communication: +20 points
- Score > 80 = High confidence

---

### Template Method Pattern
**Markers:**
- Abstract base class defining algorithm steps
- Protected abstract methods for customization points
- Concrete subclasses implementing customization points
- Algorithm flow stays in base class

**Confidence scoring:**
- Abstract class with defined sequence: +35 points
- Protected abstract methods: +30 points
- Concrete implementations: +20 points
- Test verifies overall flow: +15 points
- Score > 80 = Detected

**Why it's problematic:** Inheritance-based (less flexible than composition). Difficult to combine multiple customizations.

**Better alternative:** Strategy pattern with composition.

---

### Decorator Pattern
**Markers:**
- Wrapper class implementing same interface as wrapped object
- Delegates to wrapped object
- Adds behavior before/after delegation
- Supports wrapping with multiple decorators

**Confidence scoring:**
- Same interface as wrapped type: +40 points
- Delegation to wrapped object: +30 points
- Added behavior present: +20 points
- Multiple decorator layers possible: +10 points
- Score > 70 = Detected decorator

---

### Adapter Pattern
**Markers:**
- Converts one interface to another
- Wraps incompatible object
- Client expects one interface, adapter provides translation
- Often named with "Adapter" suffix

**Confidence scoring:**
- Interface mismatch evident: +35 points
- Wrapper/bridge pattern: +30 points
- Method translation present: +25 points
- External library integration: +10 points
- Score > 80 = Likely adapter

---

### Repository Pattern
**Markers:**
- Abstracts data access with common interface
- Methods like `findById()`, `save()`, `delete()`, `findAll()`
- Isolation of domain model from persistence technology
- Framework-agnostic interface definition

**Confidence scoring:**
- Repository interface/abstract class: +35 points
- Multiple implementations (SQL, NoSQL, in-memory): +25 points
- Standard CRUD methods: +20 points
- Domain model isolation: +20 points
- Score > 80 = High confidence

**Verification:** Check if tests use in-memory implementation, indicating proper abstraction.

---

### Dependency Injection Pattern
**Markers:**
- Constructor injection: dependencies passed to `__init__` or constructor
- Method injection: setter methods for dependencies
- Container managing lifecycle
- No `new` keywords in client code creating dependencies

**Confidence scoring:**
- Constructor parameters accept abstractions: +35 points
- No direct instantiation of dependencies: +25 points
- DI container/framework present: +20 points
- Tests use mock implementations: +20 points
- Score > 80 = High confidence

**Framework detection:**
- Python: FastAPI Depends, Pydantic, manual DI
- JavaScript: NestJS, TypeDI, manual DI
- Java: Spring, Guice, Dagger
- Go: Wire, manual DI (idiomatic)

---

## Contrarian Pattern Analysis Framework

**For each detected pattern, answer:**

1. **What problem does this solve?**
   - Example: "MVC separates concerns between data, display, and control flow"

2. **What assumption does it make?**
   - Example: "MVC assumes unidirectional data dependency: Model → Controller ← View"

3. **When does that assumption break?**
   - Example: "View layer often needs to query multiple models simultaneously, creating direct Model-View dependencies"

4. **What hidden costs does it impose?**
   - Example: "Controller logic becomes fat; multiple models create orchestration complexity"

5. **What would be better?**
   - Example: "Query object pattern where View requests pre-computed DTOs, or hexagonal architecture isolating domain from all delivery mechanisms"

6. **Evidence in this codebase:**
   - Point to specific files violating the pattern's assumptions
   - Identify pain points in tests or commits
   - Note missed opportunities for simplification

This contrarian framework prevents cargo-cult pattern adoption and surfaces real architectural problems.
