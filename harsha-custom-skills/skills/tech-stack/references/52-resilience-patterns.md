# Resilience Patterns Reference Guide

<!-- PRICING_STABILITY: Production-grade resilience patterns for distributed systems -->

## Executive Summary

Resilience patterns enable systems to handle failures gracefully, maintain partial functionality during degradation, and recover automatically from transient errors. This guide covers circuit breakers (Closed→Open→Half-Open state machine), retry strategies with exponential backoff + jitter, bulkhead isolation techniques, chaos engineering practices, and observability frameworks. Includes real outage case studies (Cloudflare Nov 2025: 28% app impact, AWS Oct 2025: 70+ services affected), implementation libraries for Node.js/Go/Python/Java, health check patterns (liveness/readiness/startup probes), and SLI/SLO/SLA definitions with Google SRE error budget models for sustainable incident response.

---

## 1. Circuit Breaker Pattern

The Circuit Breaker is a critical pattern for preventing cascading failures in distributed systems. It monitors for failures and stops sending requests to failing services.

### Pattern Overview

```
Request Flow: Client → [Breaker] → Service

States:
┌─────────────┐       failure_threshold     ┌──────────┐
│   CLOSED    │ ─────────────────────────→ │   OPEN   │
│  (OK)       │ ←─────────────────────────  │ (FAILING)│
└─────────────┘      success / timeout      └──────────┘
      ↑                                           │
      │         half_open_attempts=success       │
      └───────────────────────────────────────────┘
              HALF-OPEN (testing recovery)
```

### Implementation Libraries by Language

| Language | Library | Async Support | Custom Hooks | Active Dev |
|----------|---------|---------------|--------------|-----------|
| Node.js | opossum | ✓ (Promise) | ✓ (event emitters) | Active |
| Go | gobreaker | ✗ (sync patterns) | ✓ (custom func) | Active |
| Python | PyBreaker | ✓ (asyncio) | ✓ (listeners) | Active |
| Java | Resilience4j | ✓ (CompletableFuture) | ✓ (EventConsumer) | Active |
| Rust | failure-rs | ✓ (async/await) | ⚠ (minimal) | Maintenance |

### State Transitions in Detail

#### CLOSED State
- Normal operation: all requests pass through
- Count failures per window (e.g., 10 failures in 60 seconds)
- On threshold breach → transition to OPEN
- Success/normal operation resets failure counter

#### OPEN State
- Requests fail immediately (fast-fail)
- No calls reach the backend service
- Prevents overload on struggling service
- Timer starts (e.g., 30 seconds)
- After timeout → transition to HALF-OPEN

#### HALF-OPEN State
- Limited test traffic allowed through (e.g., 3 requests)
- If test request succeeds → back to CLOSED
- If test request fails → back to OPEN (and restart timer)
- Allows recovery verification before returning to normal

### Configuration Parameters

```
circuit_breaker_config = {
  # Failure threshold before opening
  failure_threshold: 5,              # failures
  failure_window: 60,                # seconds

  # OR use error rate threshold
  error_rate_threshold: 0.5,         # 50% errors

  # Recovery behavior
  timeout: 30,                       # seconds in OPEN state
  half_open_max_requests: 3,         # test requests allowed

  # Granularity
  metrics_window: 10,                # seconds (rolling window)

  # Optional: per-error-type behavior
  exclude_errors: [404, 401],        # don't count these as failures
  retry_timeout_multiplier: 2.0,     # exponential backoff for retry
}
```

### Node.js Implementation (Opossum)

```javascript
const CircuitBreaker = require('opossum');

// Basic setup
const breaker = new CircuitBreaker(async (url) => {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}, {
  timeout: 3000,                    // request timeout
  errorThresholdPercentage: 50,     // fail after 50% errors
  resetTimeout: 30000,              // wait 30s before half-open
  rollingCountTimeout: 10000,       // 10s rolling window
  rollingCountBuckets: 10,          // 10 buckets
  name: 'user-service'
});

// Listen to state changes
breaker.on('open', () => console.log('Circuit opened!'));
breaker.on('halfOpen', () => console.log('Testing recovery...'));
breaker.on('close', () => console.log('Circuit closed, normal operation'));

// Use the breaker
try {
  const data = await breaker.fire('https://api.example.com/users/123');
  console.log('Success:', data);
} catch (error) {
  if (error.code === 'EBREAKER') {
    console.log('Circuit is OPEN - service unavailable, use fallback');
    // Serve from cache, return default response, etc.
  } else {
    console.log('Request failed:', error.message);
  }
}

// Advanced: Custom fallback
const breaker2 = new CircuitBreaker(makeRequest, {
  timeout: 3000,
  resetTimeout: 30000
});

breaker2.fallback(() => ({
  status: 'degraded',
  data: getCachedUserData()
}));

// Monitoring state
setInterval(() => {
  const stats = breaker.stats;
  console.log(`
    Requests: ${stats.fires}
    Successes: ${stats.successes}
    Failures: ${stats.failures}
    Timeouts: ${stats.timeouts}
    Error Rate: ${(stats.failures / stats.fires * 100).toFixed(2)}%
  `);
}, 5000);
```

### Go Implementation (gobreaker)

```go
package main

import (
  "github.com/grpc-ecosystem/go-grpc-middleware/retry"
  "github.com/sony/gobreaker"
  "net/http"
)

// Basic circuit breaker
cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
  Name:        "UserService",
  MaxRequests: 3,                    // half-open max requests
  Interval:    time.Second * 10,     // rolling window
  Timeout:     time.Second * 30,     // open state duration
  ReadyToTrip: func(counts gobreaker.Counts) bool {
    failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
    return counts.Requests >= 3 && failureRatio >= 0.6
  },
  OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
    log.Printf("Circuit breaker %s: %v -> %v", name, from, to)
  },
})

// Execute request through breaker
result, err := cb.Execute(func() (interface{}, error) {
  resp, err := http.Get("https://api.example.com/users")
  if err != nil {
    return nil, err
  }
  defer resp.Body.Close()

  if resp.StatusCode >= 500 {
    return nil, fmt.Errorf("server error: %d", resp.StatusCode)
  }

  var data interface{}
  json.NewDecoder(resp.Body).Decode(&data)
  return data, nil
})

if err != nil {
  if err == gobreaker.ErrOpenState {
    log.Println("Circuit is OPEN, returning cached response")
    return getCachedData()
  }
  return err
}
```

### Python Implementation (PyBreaker)

```python
from pybreaker import CircuitBreaker
import requests
import logging

# Create breaker
breaker = CircuitBreaker(
    fail_max=5,                      # failures before open
    reset_timeout=30,                # seconds in open state
    listeners=[                      # state change listeners
        lambda cb, *args: logging.info(f"Circuit {cb.name} opened"),
    ]
)

@breaker
def fetch_user(user_id):
    """Fetch user, protected by circuit breaker"""
    response = requests.get(f'https://api.example.com/users/{user_id}')
    response.raise_for_status()
    return response.json()

# With fallback
@breaker.copy()
def fetch_user_with_cache(user_id):
    try:
        return fetch_user(user_id)
    except Exception as e:
        if breaker.opened:
            logging.warning(f"Circuit open, using cached user {user_id}")
            return get_cached_user(user_id)
        raise

# Async support (Python 3.8+)
from pybreaker import CircuitBreaker as AsyncCircuitBreaker

async_breaker = AsyncCircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    listeners=[]
)

async def fetch_user_async(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.example.com/users/{user_id}') as resp:
            return await resp.json()

# Use async breaker
try:
    user = await async_breaker(fetch_user_async, user_id=123)
except Exception as e:
    if async_breaker.opened:
        user = await get_cached_user_async(123)
```

### Java Implementation (Resilience4j)

```java
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.core.registry.EntryAddedEvent;

// Configuration
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50.0f)           // 50% failure rate
    .slowCallRateThreshold(50.0f)          // 50% slow calls
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .permittedNumberOfCallsInHalfOpenState(3)
    .automaticTransitionFromOpenToHalfOpenEnabled(true)
    .recordExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(BusinessException.class)
    .build();

// Create breaker
CircuitBreaker breaker = CircuitBreaker.of("userService", config);

// Add listeners
breaker.getEventPublisher()
    .onStateTransition(event -> logger.info("State transition: {}", event))
    .onSuccess(event -> logger.debug("Call succeeded"))
    .onError(event -> logger.warn("Call failed"));

// Use breaker with functional composition
Supplier<String> supplier = CircuitBreaker.decorateSupplier(
    breaker,
    () -> fetchUser(123)
);

try {
    String result = supplier.get();
} catch (CallNotPermittedException e) {
    logger.error("Circuit is OPEN, using fallback");
    return getUserFromCache(123);
}

// Async support (CompletableFuture)
CompletionStage<String> future = CircuitBreaker.decorateCompletionStage(
    breaker,
    () -> fetchUserAsync(123)
);

future.exceptionally(throwable -> {
    if (throwable instanceof CallNotPermittedException) {
        return getUserFromCacheSync(123);
    }
    throw new RuntimeException(throwable);
});
```

### Metrics to Monitor

| Metric | Threshold Alert | Why It Matters |
|--------|-----------------|----------------|
| Error Rate | > 5% for 2 min | Early indicator of problems |
| Circuit State | OPEN → email on-call | Service degradation |
| P99 Latency | > 5s for 1 min | User experience impact |
| Half-Open Failures | > 2 consecutive | Breaker thrashing |
| False Positives | Breaker open, service healthy | Needs tuning |

---

## 2. Retry Strategies

Retries are crucial for handling transient failures, but must be implemented carefully to avoid making things worse.

### Exponential Backoff with Jitter

```
Attempt 1: T+0ms (immediate)
Attempt 2: T+100ms + jitter (0-50ms)
Attempt 3: T+200ms + jitter (0-100ms)
Attempt 4: T+400ms + jitter (0-200ms)
Attempt 5: T+800ms + jitter (0-400ms)
Attempt 6: T+1600ms + jitter (0-800ms)

Formula: delay = base_delay * (2 ^ attempt) + random(0, base_delay * (2 ^ attempt))
```

Without jitter, all clients retry simultaneously → thundering herd → system overload.

With jitter, retries spread out → reduces peak load.

### Google SRE Retry Budget Model

Google recommends limiting retry traffic to 20% of total budget, plus 10 free retries/second:

```
Total QPS: 10,000 requests/sec
Retry budget allocation: 20% of successful requests
Free retries: 10 retries/sec minimum

If 99% success rate normally:
- 100 failed requests/sec
- Budget available: (10,000 * 0.99 * 0.20) = 1,980 retries/sec
- Actual budget: max(100 + 1,980, 10) = 2,080 retries/sec

But if failure rate spikes:
- 1,000 failed requests/sec
- Budget: (10,000 * 0.90 * 0.20) = 1,800 retries/sec
- Actual budget: max(1,000 + 1,800, 10) = 2,800 retries/sec
- At this point, stop retrying to prevent overload
```

### Node.js Example: Exponential Backoff with Jitter

```javascript
async function retryWithBackoff(fn, options = {}) {
  const {
    maxRetries = 5,
    baseDelay = 100,        // milliseconds
    maxDelay = 8000,        // milliseconds
    jitterFactor = 0.1      // 10% jitter
  } = options;

  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry on 4xx client errors or specific business logic errors
      if (error.statusCode >= 400 && error.statusCode < 500) {
        throw error;
      }

      // Don't retry on last attempt
      if (attempt === maxRetries) {
        break;
      }

      // Calculate delay with exponential backoff
      const exponentialDelay = baseDelay * Math.pow(2, attempt);
      const delay = Math.min(exponentialDelay, maxDelay);

      // Add jitter: 0 to (jitterFactor * delay)
      const jitter = Math.random() * delay * jitterFactor;
      const totalDelay = delay + jitter;

      console.log(
        `Retry attempt ${attempt + 1}/${maxRetries} ` +
        `after ${totalDelay.toFixed(0)}ms, reason: ${error.message}`
      );

      await new Promise(resolve => setTimeout(resolve, totalDelay));
    }
  }

  throw lastError;
}

// Usage
const user = await retryWithBackoff(
  () => fetch('https://api.example.com/users/123').then(r => r.json()),
  { maxRetries: 4, baseDelay: 100, maxDelay: 5000 }
);
```

### Idempotency Keys for Safe Retries

Idempotency keys ensure that retrying a request doesn't cause duplicate side effects.

```javascript
// Client-side: generate unique key per request
import crypto from 'crypto';

async function makePayment(userId, amount) {
  const idempotencyKey = crypto.randomUUID();
  const headers = {
    'Idempotency-Key': idempotencyKey,
    'Content-Type': 'application/json'
  };

  // Retry this request; server will deduplicate based on key
  return retryWithBackoff(() =>
    fetch('https://api.example.com/payments', {
      method: 'POST',
      headers,
      body: JSON.stringify({ userId, amount })
    }).then(r => r.json())
  );
}

// Server-side: deduplicate based on key
const idempotencyCache = new Map(); // In production: use Redis

app.post('/payments', (req, res) => {
  const { 'idempotency-key': key } = req.headers;

  if (!key) {
    return res.status(400).json({ error: 'Idempotency-Key required' });
  }

  // Check if we've already processed this request
  if (idempotencyCache.has(key)) {
    const cachedResponse = idempotencyCache.get(key);
    return res.status(200).json(cachedResponse);
  }

  // Process payment
  try {
    const result = processPayment(req.body);
    idempotencyCache.set(key, result);
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### When NOT to Retry

| Condition | Reason |
|-----------|--------|
| 4xx client errors (except 429, 408) | Request is malformed, retrying won't help |
| Business logic failures | Not transient, e.g., "insufficient funds" |
| 429 Too Many Requests | Already indicating system overload |
| Saga/distributed transaction step failed | Risk of inconsistency |
| Request without Idempotency-Key | Risk of duplicates |
| Already exceeded retry budget | Prevent cascading failures |

### Retry Strategies Comparison

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Fixed Delay** (1s, 1s, 1s) | Simple | Thundering herd, slow recovery | Internal APIs only |
| **Linear Backoff** (1s, 2s, 3s) | Predictable | Still has herd problem | Non-critical, low QPS |
| **Exponential Backoff** | Spreads load | Can be too aggressive | Most external APIs |
| **Exponential + Jitter** | Optimal load spreading | Slightly higher latency | Production systems |
| **Decorrelated Jitter** | Better distribution | More complex | High-QPS systems |

---

## 3. Bulkhead Isolation

Bulkheads prevent one failing component from bringing down the entire system by isolating resources.

### Thread Pool Isolation

```javascript
// Node.js with piscina worker pools
import Piscina from 'piscina';
import path from 'path';

// Separate worker pool for CPU-intensive tasks (reporting)
const reportingPool = new Piscina({
  filename: path.resolve('workers/reporting-worker.js'),
  maxThreads: 4,
  minThreads: 1,
  maxQueue: 100,
  name: 'reporting'
});

// Separate worker pool for I/O operations (file uploads)
const uploadPool = new Piscina({
  filename: path.resolve('workers/upload-worker.js'),
  maxThreads: 8,
  minThreads: 2,
  maxQueue: 500,
  name: 'uploads'
});

// Main application thread stays responsive
app.get('/dashboard', (req, res) => {
  res.json({ status: 'ok' });  // Always fast
});

app.post('/generate-report', async (req, res) => {
  try {
    // Runs in separate thread; main thread not blocked
    const report = await reportingPool.run({ userId: req.user.id });
    res.json(report);
  } catch (error) {
    if (error.message.includes('queue is full')) {
      res.status(503).json({ error: 'Report generation overloaded' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

app.post('/upload', async (req, res) => {
  try {
    const result = await uploadPool.run({ file: req.file });
    res.json(result);
  } catch (error) {
    if (error.message.includes('queue is full')) {
      res.status(503).json({ error: 'Upload service overloaded' });
    }
  }
});
```

### Java Example: Thread Pool Bulkheads

```java
import io.github.resilience4j.bulkhead.Bulkhead;
import io.github.resilience4j.bulkhead.BulkheadConfig;
import io.github.resilience4j.bulkhead.BulkheadRegistry;

// Separate bulkhead for user service
BulkheadConfig userBulkheadConfig = BulkheadConfig.custom()
    .maxConcurrentCalls(20)        // max 20 concurrent calls
    .maxWaitDuration(Duration.ofSeconds(10))
    .build();

Bulkhead userBulkhead = Bulkhead.of("userService", userBulkheadConfig);

// Separate bulkhead for reporting
BulkheadConfig reportingBulkheadConfig = BulkheadConfig.custom()
    .maxConcurrentCalls(5)         // CPU-intensive, lower limit
    .maxWaitDuration(Duration.ofSeconds(5))
    .build();

Bulkhead reportingBulkhead = Bulkhead.of("reporting", reportingBulkheadConfig);

// Usage
public String getUser(String userId) {
    return Bulkhead.decorateSupplier(userBulkhead, () ->
        userService.fetchUser(userId)
    ).get();
}

public String generateReport(String reportId) {
    return Bulkhead.decorateSupplier(reportingBulkhead, () ->
        reportingService.generate(reportId)
    ).get();
}
```

### Connection Pool Isolation

```javascript
// PostgreSQL: separate pools for critical vs non-critical operations
import pg from 'pg';

// High-priority pool: user authentication, payment processing
const criticalPool = new pg.Pool({
  user: 'app_user',
  password: process.env.DB_PASSWORD,
  host: 'db.example.com',
  port: 5432,
  database: 'app_db',
  max: 20,           // max 20 connections
  min: 5,            // keep 5 idle connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Standard pool: API requests, user operations
const standardPool = new pg.Pool({
  user: 'app_user',
  password: process.env.DB_PASSWORD,
  host: 'db.example.com',
  port: 5432,
  database: 'app_db',
  max: 30,
  min: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Background pool: analytics, batch jobs (low priority)
const backgroundPool = new pg.Pool({
  user: 'app_user',
  password: process.env.DB_PASSWORD,
  host: 'db.example.com',
  port: 5432,
  database: 'app_db',
  max: 10,
  min: 2,
  idleTimeoutMillis: 60000,
  connectionTimeoutMillis: 5000,
});

// Usage
async function processPayment(userId, amount) {
  const client = await criticalPool.connect();
  try {
    await client.query('BEGIN');
    await client.query('UPDATE users SET balance = balance - $1 WHERE id = $2',
      [amount, userId]);
    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

async function generateAnalytics() {
  // Low priority, uses background pool
  const result = await backgroundPool.query(
    'SELECT COUNT(*) as count FROM events WHERE created_at > NOW() - INTERVAL 1 day'
  );
  return result.rows[0];
}
```

### Kubernetes Resource Limits as Bulkheads

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  template:
    spec:
      containers:
      - name: api
        image: api:v1
        resources:
          requests:
            cpu: 500m          # guaranteed allocation
            memory: 512Mi
          limits:
            cpu: 2000m         # max allowed
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 2

---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"       # total CPU for team
    requests.memory: "100Gi"  # total memory for team
    pods: "200"               # max pods
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values:
      - high-priority
      - normal

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-isolation
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

---

## 4. Chaos Engineering

Chaos engineering deliberately injects failures to find weaknesses before they cause real outages.

### Tools Overview

| Tool | Deployment | Target | Cost | Learning Curve |
|------|-----------|--------|------|-----------------|
| Chaos Monkey | AWS only | EC2 instances | Free (Netflix OSS) | Low |
| Gremlin | SaaS or on-prem | VMs, Kubernetes, containers | $1,200+/month | Medium |
| LitmusChaos | Kubernetes | Pods, network, storage | Free (CNCF) | High |
| Pumba | Docker | Containers | Free (OSS) | Low |
| ChaosIQ | Cloud managed | Multi-cloud | $2,000+/month | Medium |

### Chaos Monkey: Random EC2 Termination

```bash
# Netflix's chaos monkey - terminates random EC2 instances in production

# Configuration
{
  "InstanceTerminationConfig": {
    "group_name": "prod-api-asg",
    "enabled": true,
    "termination_probability": 0.2,    # 20% chance per instance daily
    "time_window": "9:00-17:00",       # business hours only
    "whitelist": ["prod-api-critical"] # never terminate these
  }
}

# Deployment: run as Lambda function or EC2 instance
# Logs to CloudWatch when instances are terminated
```

### Gremlin: Orchestrated Chaos Experiments

```python
# Gremlin API integration
import requests
import json

def create_latency_attack():
    """Create a latency injection attack"""
    attack = {
        "target": {
            "type": "Kubernetes",
            "filters": {
                "labels": {
                    "app": "api",
                    "stage": "production"
                }
            }
        },
        "command": {
            "type": "latency",
            "latency": 500,           # 500ms latency
            "jitter": 100,            # +/- 100ms variation
            "percent": 50             # affect 50% of traffic
        },
        "scheduling": {
            "duration": 300,          # 5 minutes
            "runStrategy": "scheduled",
            "scheduledTime": "2026-03-02T14:00:00Z"
        }
    }

    response = requests.post(
        'https://api.gremlin.com/v1/attacks',
        headers={'Authorization': f'Key {GREMLIN_API_KEY}'},
        json=attack
    )

    return response.json()

def create_packet_loss_attack():
    """Simulate 5% packet loss"""
    attack = {
        "target": {
            "type": "Kubernetes",
            "filters": {
                "labels": {"app": "database"}
            }
        },
        "command": {
            "type": "packet_loss",
            "percent": 5              # 5% packet loss
        },
        "scheduling": {
            "duration": 120           # 2 minutes
        }
    }

    response = requests.post(
        'https://api.gremlin.com/v1/attacks',
        headers={'Authorization': f'Key {GREMLIN_API_KEY}'},
        json=attack
    )

    return response.json()

def create_cpu_attack():
    """Spike CPU to 90%"""
    attack = {
        "target": {
            "type": "Kubernetes",
            "filters": {
                "labels": {"app": "worker"}
            }
        },
        "command": {
            "type": "cpu",
            "cores": 2,               # use 2 CPU cores
            "percent": 90             # at 90% utilization
        },
        "scheduling": {
            "duration": 180           # 3 minutes
        }
    }

    response = requests.post(
        'https://api.gremlin.com/v1/attacks',
        headers={'Authorization': f'Key {GREMLIN_API_KEY}'},
        json=attack
    )

    return response.json()
```

### LitmusChaos: Kubernetes-Native Chaos

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosExperiment
metadata:
  name: pod-kill-chaos
  namespace: chaos-testing
spec:
  definition:
    apiversion: batch/v1
    kind: Job
    spec:
      template:
        metadata:
          labels:
            app: pod-kill-chaos
        spec:
          serviceAccountName: litmus-admin
          containers:
          - name: pod-kill-chaos
            image: litmuschaos/go-runner:latest
            env:
            - name: TARGET_NAMESPACE
              value: production
            - name: TARGET_LABEL
              value: app=api
            - name: KILL_COUNT
              value: "2"              # kill 2 pods
            - name: CHAOS_DURATION
              value: "60"             # seconds
            - name: CHAOS_INTERVAL
              value: "30"             # interval between kills
          restartPolicy: Never

---
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: api-chaos-test
  namespace: production
spec:
  engineState: active
  appinfo:
    appns: production
    applabel: "app=api"
    appkind: Deployment
  chaosServiceAccount: litmus-admin
  experiments:
  - name: pod-kill-chaos
    spec:
      components:
        env:
        - name: TOTAL_CHAOS_DURATION
          value: "120"               # 2 minute experiment
        - name: CHAOS_INTERVAL
          value: "30"
      probe:
        - name: api-availability
          type: httpProbe
          httpProbe/inputs:
            url: http://api-service/health
            insecureSkipVerify: false
            responseTimeout: 2000
            retry: 5
          mode: Continuous
          runProperties:
            probeTimeout: 5000
            interval: 1000
          expectedResult: |
            statusCode: 200
  resultName: api-chaos-result
  jobCleanUpPolicy: delete

---
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosExperiment
metadata:
  name: network-latency-chaos
spec:
  definition:
    apiversion: batch/v1
    kind: Job
    spec:
      template:
        metadata:
          labels:
            app: network-chaos
        spec:
          containers:
          - name: network-chaos
            image: litmuschaos/go-runner:latest
            env:
            - name: TARGET_CONTAINER
              value: api
            - name: NETWORK_LATENCY
              value: "250"            # 250ms latency
            - name: JITTER
              value: "50"             # +/- 50ms
            - name: TC_IMAGE
              value: gaiaadm/iproute2 # traffic control image
```

### Game Days: Running Chaos Experiments

A game day is a scheduled chaos engineering exercise where teams practice responding to failures.

```markdown
## Game Day: April 15, 2026

### Participants
- API Team: 4 engineers
- Database Team: 3 engineers
- Incident Commander: 1 (from SRE team)
- Observer: 1 (from Product)

### Schedule
2:00 PM - Briefing: "We're simulating database failure"
2:05 PM - Incident starts (database pods killed)
2:35 PM - Debrief starts (30 min duration)
3:00 PM - Post-mortem discussion

### Chaos Scenario
At 2:05 PM, kill 3 out of 5 database replicas simultaneously.
Expected system behavior:
- Connection pooling handles failover
- Read replicas in different zone take over
- API latency increases by 200-500ms
- No 5xx errors (should return cached data)

### Acceptance Criteria
✓ PagerDuty alert fires within 30 seconds
✓ On-call engineer acknowledges within 5 minutes
✓ System continues serving at least 95% of requests
✓ Database failover completes within 2 minutes
✓ Team communicates status every 2 minutes

### Observation Points
- How quickly did team identify root cause?
- Were runbooks followed or improvised?
- Did monitoring alert on the right metrics?
- Was communication clear to stakeholders?
- How much manual intervention was needed?

### Post-Incident Review
Document:
1. What went well
2. What didn't go well
3. Action items (preferably < 5)
4. Timeline of events
5. Lessons learned
```

### Progressive Chaos: Start Small, Increase Scope

```
Week 1: Single dependency failures
├─ Kill one database connection
├─ Introduce 100ms latency to cache
└─ Drop 1% of API requests

Week 2: Service-level failures
├─ Kill entire microservice (returns 503)
├─ Introduce 1 second latency to payment service
└─ Simulate cache stampede (all keys expire simultaneously)

Week 3: Zone/cluster failures
├─ Simulate entire availability zone going down
├─ Network partition between services
└─ Disk pressure (75% full)

Week 4: Coordinated failures (multiple simultaneous)
├─ Database failure + cache failure
├─ Two microservices down + high latency on third
└─ Network congestion + CPU spike
```

---

## 5. Real Outage Post-Mortems: Case Studies

### Case Study 1: Cloudflare November 2025 Incident

**Impact**: 28% of Cloudflare customers affected for 25 minutes

**Root Cause**: Bot Management configuration change doubled the size of generated JavaScript file, from 200KB → 400KB.

```
Timeline:
12:00 PM - Configuration deployment to Bot Management
12:02 PM - First metrics anomaly detected (increased bandwidth)
12:05 PM - Monitoring alert fires (P99 latency > 5s)
12:07 PM - Incident commander engaged
12:15 PM - Root cause identified: JS file size doubled
12:25 PM - Configuration rolled back
12:27 PM - Service recovered, all customers normal
12:40 PM - Post-mortem started

Impact Metrics:
- 28% of customer zones affected
- Page load time increased 3-4 seconds
- 15% of requests returned with 502 Bad Gateway
- 25 minutes of degraded service
```

**Architectural Fix**:

```javascript
// Before: No size validation
const generateBotManagementJS = (config) => {
  return generateCode(config);  // Could be any size
};

// After: Strict size budgets
const JAVASCRIPT_SIZE_BUDGET = {
  bot_management: 250 * 1024,    // 250KB max
  analytics: 100 * 1024,
  cdn_control: 50 * 1024
};

const generateBotManagementJS = (config) => {
  const code = generateCode(config);
  const size = Buffer.byteLength(code, 'utf8');

  if (size > JAVASCRIPT_SIZE_BUDGET.bot_management) {
    throw new Error(
      `Bot Management JS exceeds size budget: ` +
      `${size} > ${JAVASCRIPT_SIZE_BUDGET.bot_management}`
    );
  }

  return code;
};

// Deployment validation
async function validateDeployment(config) {
  const jsSize = Buffer.byteLength(generateBotManagementJS(config));
  const budgetChange = jsSize - PREVIOUS_SIZE;

  if (budgetChange > 0.1 * JAVASCRIPT_SIZE_BUDGET.bot_management) {
    throw new Error(
      `Size increase exceeds 10% threshold: ${budgetChange} bytes`
    );
  }

  return true;
}
```

**Lessons Learned**:
1. Configuration changes need size budget validation
2. Rolling deployments should check edge metrics (bandwidth, latency)
3. Need canary deployment: test with 1% traffic before 100%
4. Alert on size changes to static assets

### Case Study 2: AWS DynamoDB October 2025 Incident

**Impact**: 70+ services affected, intermittent unavailability for 15 minutes

**Root Cause**: DNS race condition in DynamoDB control plane. During scaling operation, DNS resolver encountered inconsistent responses, causing some clients to connect to wrong endpoint.

```
Timeline:
02:00 AM - DynamoDB scaling operation started
02:03 AM - DNS cache inconsistency begins
02:05 AM - Services start seeing connection timeouts
02:08 AM - 70+ AWS services report elevated error rates
02:10 AM - AWS incident status page updated
02:15 AM - DNS records reconciled
02:18 AM - All services recovered
02:45 AM - Post-mortem initiated

Affected Services:
- Lambda (unable to invoke)
- RDS (connection pooling failures)
- ElastiCache (metadata operations)
- CloudWatch (metrics ingestion)
```

**Architectural Fix**:

```go
// Before: Simple DNS resolution
func connectToDynamoDB(endpoint string) (*Connection, error) {
  return DialTCP(endpoint, 8000)
}

// After: Connection pooling with health checks
type DynamoDBConnector struct {
  endpoint string
  pool *ConnectionPool
  resolver *DNSResolver
  healthCheck *HealthChecker
}

func (c *DynamoDBConnector) Init() error {
  // Verify DNS resolution multiple times
  for i := 0; i < 3; i++ {
    addr, err := c.resolver.Resolve(c.endpoint)
    if err != nil {
      return err
    }
    if i > 0 && addr != c.lastResolvedAddr {
      return fmt.Errorf("DNS inconsistency detected")
    }
    c.lastResolvedAddr = addr
    time.Sleep(100 * time.Millisecond)
  }

  // Connection pooling with TTL
  c.pool = NewConnectionPool(10, 30*time.Second)
  c.healthCheck = NewHealthChecker(5 * time.Second)

  return nil
}

func (c *DynamoDBConnector) GetConnection() (*Connection, error) {
  // Periodically refresh DNS
  if time.Since(c.lastDNSRefresh) > 5*time.Minute {
    if err := c.refreshDNS(); err != nil {
      return nil, err
    }
  }

  conn := c.pool.Get()
  if !c.healthCheck.IsHealthy(conn) {
    conn = nil
  }

  if conn == nil {
    addr, err := c.resolver.Resolve(c.endpoint)
    if err != nil {
      return nil, err
    }
    conn, err = DialTCP(addr, 8000)
  }

  return conn, nil
}
```

**Lessons Learned**:
1. DNS resolution can have consistency issues during scaling
2. Connection pooling must include TTL and health checks
3. DNS results should be verified before use
4. Services should implement fallback endpoints
5. Test DNS failures in chaos engineering

---

## 6. Health Check Patterns

### Liveness vs Readiness vs Startup Probes

| Probe Type | Purpose | When It Fires | Recovery Action |
|-----------|---------|---------------|-----------------|
| **Liveness** | "Is process alive?" | Every 10s (example) | Restart container |
| **Readiness** | "Can accept requests?" | Every 5s (example) | Remove from load balancer |
| **Startup** | "Has process initialized?" | Every 10s for 30s max | Restart if not ready |

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
spec:
  containers:
  - name: api
    image: api:v1
    ports:
    - containerPort: 8080

    # Startup Probe: ensure app has initialized
    startupProbe:
      httpGet:
        path: /startup
        port: 8080
      failureThreshold: 30        # 30 * 10s = 300s max startup time
      periodSeconds: 10
      timeoutSeconds: 2

    # Liveness Probe: crash if truly hung
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 60     # wait for startup
      periodSeconds: 10           # check every 10s
      timeoutSeconds: 2
      failureThreshold: 3         # restart after 3 failures

    # Readiness Probe: temporary unavailability
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5            # frequent checks
      timeoutSeconds: 1
      successThreshold: 1
      failureThreshold: 2         # remove from LB after 2 failures
```

### Deep Health Checks

```javascript
// Simple health check: just responds
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Deep health check: verifies dependencies
app.get('/health/deep', async (req, res) => {
  const checks = await Promise.allSettled([
    db.query('SELECT 1'),           // database connectivity
    cache.get('health:check'),      // cache connectivity
    externalAPI.health(),           // external service
    fs.promises.access(storageDir)  // file system
  ]);

  const status = checks.every(c => c.status === 'fulfilled')
    ? 'healthy'
    : 'degraded';

  res.status(status === 'healthy' ? 200 : 503).json({
    status,
    checks: {
      database: checks[0].status === 'fulfilled' ? 'ok' : 'failed',
      cache: checks[1].status === 'fulfilled' ? 'ok' : 'failed',
      externalAPI: checks[2].status === 'fulfilled' ? 'ok' : 'failed',
      storage: checks[3].status === 'fulfilled' ? 'ok' : 'failed'
    }
  });
});

// Readiness: accepts traffic?
app.get('/ready', async (req, res) => {
  // Only report ready if database is accessible
  try {
    await db.query('SELECT 1');
    res.json({ ready: true });
  } catch {
    res.status(503).json({ ready: false, reason: 'database unreachable' });
  }
});

// Startup: fully initialized?
let initialized = false;
const startup = async () => {
  try {
    await loadConfiguration();
    await connectToDatabase();
    await warmUpCaches();
    initialized = true;
  } catch (error) {
    console.error('Startup failed:', error);
    initialized = false;
  }
};

app.get('/startup', (req, res) => {
  res.status(initialized ? 200 : 503)
    .json({ initialized });
});

startup();
```

### Graceful Degradation

```javascript
// When database is down, serve from cache with warnings
app.get('/users/:id', async (req, res) => {
  try {
    // Try database first
    const user = await db.query(
      'SELECT * FROM users WHERE id = $1',
      [req.params.id]
    );
    res.json({
      data: user,
      source: 'primary',
      cacheAge: 0
    });
  } catch (dbError) {
    // Database failed, try cache
    try {
      const cachedUser = await cache.get(`user:${req.params.id}`);
      if (cachedUser) {
        res.status(206).json({  // 206 Partial Content
          data: cachedUser,
          source: 'cache',
          cacheAge: await cache.ttl(`user:${req.params.id}`),
          warning: 'stale data'
        });
        return;
      }
    } catch (cacheError) {
      console.error('Cache error:', cacheError);
    }

    // Both failed, return error with fallback
    res.status(503).json({
      error: 'Service temporarily unavailable',
      fallback: {
        data: {
          id: req.params.id,
          name: 'Unknown User',
          status: 'degraded_mode'
        },
        source: 'fallback'
      }
    });
  }
});
```

---

## 7. Observability for Resilience

Observability enables understanding system behavior and identifying resilience issues.

### SLI, SLO, SLA Definitions and Examples

```
┌─────────────────────────────────────────────────────┐
│ SLA (Service Level Agreement)                       │
│ Contract with customers (includes penalties)        │
│ "99.9% availability or 10% refund"                 │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ SLO (Service Level Objective)                       │
│ Engineering goal (internal target)                  │
│ "99.95% availability" (stricter than SLA)          │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ SLI (Service Level Indicator)                       │
│ Actual measurement (metric we track)                │
│ "Successfully served requests / Total requests"    │
└─────────────────────────────────────────────────────┘
```

### Example SLIs and SLOs

```
API Service SLOs:

1. Availability (uptime)
   SLI: (successful_requests / total_requests) * 100
   SLO: >= 99.9% (52.6 minutes downtime/month allowed)
   Alerting: < 99.5% error rate for 5 minutes

2. Latency (response time)
   SLI: P99 request latency
   SLO: <= 500ms for 99% of requests
   Alerting: > 800ms for 2 minutes

3. Freshness (data age)
   SLI: Time since data was last updated / target freshness
   SLO: Cache hit rate >= 95%
   Alerting: < 90% cache hit for 5 minutes

4. Correctness (accuracy)
   SLI: Queries returning correct results / total queries
   SLO: >= 99.99% correctness
   Alerting: Any detected data corruption

Monthly Error Budget for 99.9% SLO:
- Month length: 43,200 minutes
- Error budget: (1 - 0.999) * 43,200 = 43.2 minutes
- Usage tracking: Real downtime < 43.2 minutes = SLO met
```

### Error Budget Implementation

```javascript
// Google SRE Error Budget Model
class ErrorBudgetTracker {
  constructor(sloTarget = 0.999, windowMinutes = 30 * 24 * 60) {
    this.sloTarget = sloTarget;           // 99.9%
    this.windowMinutes = windowMinutes;   // 30 days
    this.budgetMinutes = (1 - sloTarget) * windowMinutes;  // 43.2 min
    this.consumedMinutes = 0;
  }

  recordDowntime(minutes) {
    this.consumedMinutes += minutes;
  }

  getRemainingBudget() {
    return this.budgetMinutes - this.consumedMinutes;
  }

  getConsumptionPercent() {
    return (this.consumedMinutes / this.budgetMinutes) * 100;
  }

  canDeployRiskyChange() {
    // Only deploy if we have buffer for incidents
    const consumed = this.getConsumptionPercent();
    return consumed < 50;  // conservative: must have 50%+ budget left
  }

  getDeploymentPolicy() {
    const remaining = this.getRemainingBudget();

    if (remaining > 30) {
      return {
        policy: 'aggressive',
        deployments_per_day: 10,
        requires_review: false,
        risk_tolerance: 'high'
      };
    } else if (remaining > 10) {
      return {
        policy: 'moderate',
        deployments_per_day: 3,
        requires_review: true,
        risk_tolerance: 'medium'
      };
    } else {
      return {
        policy: 'conservative',
        deployments_per_day: 0,
        requires_review: 'security_team',
        risk_tolerance: 'low'
      };
    }
  }
}

// Usage
const budget = new ErrorBudgetTracker(0.999);

// During month
budget.recordDowntime(5);   // 5 minutes of downtime
budget.recordDowntime(3);   // 3 more minutes
console.log(`Budget consumed: ${budget.getConsumptionPercent().toFixed(1)}%`);
console.log(`Remaining: ${budget.getRemainingBudget().toFixed(1)} minutes`);

// Deployment decision
if (budget.canDeployRiskyChange()) {
  console.log('OK to deploy risky feature flags');
} else {
  console.log('Only deploy critical bugfixes');
}

// Policy adjusts based on budget
const policy = budget.getDeploymentPolicy();
console.log(`Current policy: ${policy.policy}`);
```

### Symptom-Based vs Cause-Based Alerting

```javascript
// BAD: Cause-based alerting (alerts on symptoms)
app.get('/metrics/alerts', (req, res) => {
  // These alerts don't help: they're symptoms, not causes
  const causeBasedAlerts = [
    {
      name: 'High CPU',
      condition: 'cpu > 80%',
      problem: 'Could be caused by: slow queries, memory leak, DDoS, etc'
    },
    {
      name: 'High Memory',
      condition: 'memory > 85%',
      problem: 'Could be caused by: memory leak, large dataset, cache misconfiguration, etc'
    },
    {
      name: 'High Disk I/O',
      condition: 'disk_io > 1000 ops/sec',
      problem: 'Could be caused by: hot data, poor indexing, compaction, etc'
    }
  ];

  res.json(causeBasedAlerts);
});

// GOOD: Symptom-based alerting (alerts on user impact)
const symptomBasedAlerts = [
  {
    name: 'API P99 Latency High',
    condition: 'histogram_quantile(0.99, api_request_duration) > 500ms',
    duration: '5m',
    action: 'Check database performance, cache hit rate, network latency',
    slo_impact: 'violates latency SLO'
  },
  {
    name: 'Error Rate Spike',
    condition: 'rate(http_requests_total{status=~"5.."}[5m]) > 0.01',
    duration: '2m',
    action: 'Check service logs, dependency health, rate limits',
    slo_impact: 'violates availability SLO'
  },
  {
    name: 'Cache Hit Rate Drop',
    condition: 'cache_hit_ratio < 0.90',
    duration: '10m',
    action: 'Check cache capacity, eviction policy, data freshness',
    slo_impact: 'violates freshness SLO'
  },
  {
    name: 'Queue Depth Growing',
    condition: 'queue_depth > 1000 AND queue_depth increasing',
    duration: '5m',
    action: 'Check worker pool health, consumer lag, data processing speed',
    slo_impact: 'potential future availability issue'
  }
];
```

---

## 8. Implementation Checklist

Use this checklist when implementing resilience patterns:

### Circuit Breaker Checklist
- [ ] Identify critical service dependencies
- [ ] Set failure threshold (e.g., 5 failures in 60s)
- [ ] Implement fallback/cache behavior
- [ ] Monitor circuit state transitions
- [ ] Test half-open recovery
- [ ] Tune timeout values per service
- [ ] Alert on state changes
- [ ] Document manual override procedure

### Retry Checklist
- [ ] Use exponential backoff with jitter
- [ ] Implement idempotency keys
- [ ] Exclude non-retryable errors (4xx)
- [ ] Set max retry count
- [ ] Monitor retry rates
- [ ] Implement retry budgets
- [ ] Test retry behavior under load
- [ ] Document when NOT to retry

### Bulkhead Checklist
- [ ] Identify resource pools (connections, threads)
- [ ] Set max pool size based on capacity
- [ ] Implement queue with reasonable limits
- [ ] Add monitoring for pool saturation
- [ ] Test graceful degradation
- [ ] Document queue full behavior
- [ ] Set appropriate timeouts
- [ ] Test connection pool exhaustion

### Health Check Checklist
- [ ] Implement /health endpoint (liveness)
- [ ] Implement /ready endpoint (readiness)
- [ ] Implement /startup endpoint (startup)
- [ ] Include deep health checks (database, cache)
- [ ] Set appropriate probe intervals
- [ ] Document probe expectations
- [ ] Test probe behavior under failure
- [ ] Monitor probe success rates

### Chaos Engineering Checklist
- [ ] Start with low-impact experiments
- [ ] Schedule game days monthly
- [ ] Document expected system behavior
- [ ] Establish clear incident commander
- [ ] Record all findings
- [ ] Create action items
- [ ] Test fixes in staging
- [ ] Track metrics during chaos

### Observability Checklist
- [ ] Define SLIs for critical paths
- [ ] Set SLOs stricter than SLAs
- [ ] Implement error budget tracking
- [ ] Create symptom-based alerts
- [ ] Monitor all resilience patterns
- [ ] Track MTTR and MTBF
- [ ] Review metrics monthly
- [ ] Adjust SLOs as needed

---

## 9. Quick Reference: Pattern Selection Matrix

```
Failure Type          Pattern              Config Priority
─────────────────────────────────────────────────────────
Transient errors      Retry                100ms base, 5s max
Service unavailable   Circuit Breaker      5 failures/60s, 30s timeout
Resource exhaustion   Bulkhead             pool size, queue limit
Cascading failures    Combination          all three
Unknown reliability   Chaos Engineering    start with single pod
Not meeting SLO       Observability        SLI/SLO/budget model
Difficult recovery    Health Checks        deep checks, graceful degrade
```

---

## Related References
- [Observability & Distributed Tracing](./55-observability-tracing.md) — Monitoring resilience metrics
- [Monitoring & Logging Solutions](./22-monitoring-logging.md) — Failure detection and alerting
- [Background Jobs & Event-Driven Architecture](./50-background-jobs-events.md) — Async resilience patterns
- [Edge Computing & Multi-Region Architecture](./43-edge-multi-region.md) — Geographic resilience
- [Performance Benchmarks](./47-performance-benchmarks.md) — Performance under load testing

---

**Last Updated**: March 2026
**Status**: Production-Grade
**Version**: 3.2
