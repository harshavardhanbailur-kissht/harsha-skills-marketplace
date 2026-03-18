# AI-Native Architecture Patterns (2025-2026)

## Executive Summary

The AI stack has matured significantly. Rather than rebuilding applications as AI-first, most organizations should strategically ADD AI features to existing architectures. The core AI stack consists of five layers:

1. **Model Provider** (OpenAI, Anthropic, Google, open-source)
2. **Gateway/Routing Layer** (semantic caching, model selection, failover)
3. **Orchestration** (agents, workflows, chains)
4. **Vector Database** (RAG retrieval, embeddings storage)
5. **Observability** (cost tracking, latency, quality monitoring)

**Key takeaway**: Cost optimization through semantic caching, model routing, and prompt caching can reduce AI infrastructure costs by 60-80%. Vector databases are essential for RAG systems; pgvector handles most use cases at enterprise scale (<10M vectors).

---

## The AI Stack Layers

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  Application Layer (Chat, Search, Classification)   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  Orchestration Layer (LangChain, LlamaIndex, CrewAI)│
│  - Agent loops                                       │
│  - Workflow scheduling                               │
│  - Tool/function calling                             │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  Gateway/Routing Layer (liteLLM, Helicone, Portkey) │
│  - Semantic caching (40-60% hit rates)               │
│  - Model routing (cost optimization)                 │
│  - Failover & retry logic                            │
│  - Rate limiting & quota management                  │
└────────────────────┬────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐  ┌───────▼──────┐  ┌──────▼──────┐
│  Model │  │  Vector DB   │  │ Observability
│Provider│  │   (Embeddings)   │ (Langfuse)
└────────┘  └──────────────┘  └──────────────┘
```

### Layer Details

#### 1. Model Provider Layer
- Handles direct API calls to LLMs
- Abstractions: OpenAI SDK, Anthropic SDK, Ollama (local), vLLM (self-hosted)
- Responsibility: tokenization, rate limiting, cost tracking
- Critical decision: API vs. self-hosted (see decision matrix below)

#### 2. Gateway/Routing Layer
- **Semantic Caching**: Cache responses based on semantic similarity, not exact string matching
- **Model Routing**: Send simple tasks to smaller/cheaper models (Claude Haiku 4.5 vs Opus 4.6)
- **Failover**: If OpenAI is down, route to Anthropic or Google
- **Request transformation**: Standardize prompts, add system context, log usage

**Popular tools**: liteLLM (open-source), Helicone (managed), Portkey (multi-provider)

#### 3. Orchestration Layer
- Implements agent loops, chains, and workflows
- Handles tool calling and function execution
- Manages context windows and token budgets
- Examples: multi-step reasoning, autonomous agents

#### 4. Vector Database Layer
- Stores embeddings for semantic search
- Essential for RAG (Retrieval-Augmented Generation)
- Typical operations: insert, search, update, delete embeddings
- Trade-off: managed service (Pinecone) vs. self-hosted (pgvector, Qdrant)

#### 5. Observability Layer
- Cost tracking per request, user, feature
- Latency monitoring (model, gateway, DB latencies)
- Quality metrics (user feedback, LLM-as-judge evaluation)
- Alert system for cost anomalies and errors

---

## LLM Provider Comparison

| Provider | Cost ($/1M tokens) | Input/Output | Best For | Strengths | Weakness |
|----------|-------------------|--------------|----------|-----------|----------|
| **OpenAI GPT-5** | $5/$15 | 128K ctx | Complex reasoning, coding, multimodal | Most capable, broad ecosystem | Expensive for high volume |
| **OpenAI GPT-4o** | $2.50/$10 | 128K ctx | Balanced capability, multimodal | Good cost/capability ratio | Less powerful than GPT-5 |
| **OpenAI GPT-4o mini** | $0.15/$0.60 | 128K ctx | Fast responses, cost-sensitive | Excellent cost efficiency | Limited reasoning depth |
| **Anthropic Claude Opus 4.6 4.6** | $5/$25 | 200K ctx | Long documents, nuanced analysis, coding | Longest context, highest quality | Higher cost, slower |
| **Anthropic Claude Sonnet 4.6** | $3/$15 | 200K ctx | Balanced reasoning + speed | Best quality/cost ratio | Moderate cost |
| **Anthropic Claude Haiku 4.5** | $1/$5 | 200K ctx | Budget-conscious, routing, classification | Fastest Anthropic model | Limited deep reasoning |
| **Google Gemini 2.0 Flash** | $0.10/$0.40 | 1M ctx | Long-context RAG, multimodal | Huge context window, fast | Less consistent on complex tasks |
| **Meta Llama 4** | $0 (self-host) | 128K ctx | Privacy-critical, high volume, fine-tuning | Open weights, no API costs, fine-tunable | Ops overhead, lower ceiling |
| **DeepSeek V3** | $0.27/$1.10 | 128K ctx | Cost-sensitive reasoning, coding | 140x cheaper than o1 for reasoning | China-based, compliance concerns |
| **Mistral Large 2** | $2/$6 | 128K ctx | EU compliance, multilingual | EU-hosted, good quality | Smaller ecosystem |
| **Qwen 3.5** | $0 (self-host) | 128K ctx | Multilingual, Asian language support | Strong open-source, multilingual | Newer, less battle-tested |

<!-- PRICING_STABILITY: HIGH_VOLATILITY | Updated: 2026-03-02 | AI model pricing changes monthly. ALWAYS verify current pricing at provider websites before recommending. Models listed: GPT-5 (Aug 2025), Claude 4.x series (2025), Gemini 2.0 (2025), Llama 4 (Apr 2025), DeepSeek V3 (2025), Qwen 3.5 (Feb 2026) -->

**Recommendation**: Use a **gateway pattern** with multiple providers:
- Use Haiku 4.5/GPT-4o mini for routing and classification ($0.15-$1/M input tokens)
- Use Claude Opus 4.6/GPT-5 for complex reasoning ($5/M input tokens)
- Use Gemini 2.0 Flash for long-context RAG ($0.10/M input, 1M context window)
- Use DeepSeek V3 for cost-sensitive reasoning tasks (140x cheaper than o1)
- Use Llama 4/Qwen 3.5 self-hosted for privacy-critical or high-volume pipelines
- Self-host only if >100K daily requests or privacy-critical

---

## AI Gateway Patterns

### Pattern 1: Semantic Caching
```javascript
// Pseudo-code: Semantic caching with embedding similarity
async function query(userMessage) {
  const embedding = await embedModel.embed(userMessage);
  const cachedResult = await vectorDB.searchSimilar(embedding, threshold=0.95);

  if (cachedResult) {
    return cachedResult.response; // 40-60% cache hit rate
  }

  const llmResponse = await llm.complete(userMessage);
  await vectorDB.store(embedding, llmResponse, cost=llmResponse.cost);
  return llmResponse;
}
```

**Benefits**:
- 40-60% cache hit rates on real workloads
- 90% cost reduction on cache hits
- Transparent to application code

**Tools**: Helicone (managed), liteLLM (open-source), Prompt Caching (Claude, native)

### Pattern 2: Model Routing
```javascript
// Route based on complexity
async function route(prompt) {
  const complexity = estimateComplexity(prompt);

  if (complexity < 3) {
    return llm.complete(prompt, model='claude-3.5-haiku'); // $0.80/1M
  } else if (complexity < 7) {
    return llm.complete(prompt, model='claude-3-sonnet'); // $3/1M
  } else {
    return llm.complete(prompt, model='claude-3-opus'); // $15/1M
  }
}
```

**Cost savings**: 15-50x reduction on simple tasks by routing to smaller models

### Pattern 3: Failover Strategy
```javascript
async function queryWithFailover(prompt) {
  try {
    return await openai.complete(prompt); // Primary
  } catch (error) {
    if (error.statusCode === 429 || error.statusCode === 500) {
      console.log('OpenAI unavailable, using Anthropic');
      return await anthropic.complete(prompt); // Fallback
    }
  }
}
```

**Recommended tools**:
- **liteLLM**: Open-source, minimal overhead, community-maintained
- **Helicone**: Managed service, semantic caching built-in, $0.30/1K requests
- **Portkey**: Enterprise features, guardrails, analytics dashboard

---

## Agent Framework Comparison

| Framework | Best For | Strengths | Learning Curve | Maturity |
|-----------|----------|-----------|-----------------|----------|
| **LangChain** | Complex chains, multi-step | Largest ecosystem, 50+ integrations | Medium | Production-ready |
| **LlamaIndex** | RAG, document indexing | Purpose-built for RAG, great docs | Low | Production-ready |
| **CrewAI** | Multi-agent teams | Simple syntax, role-based agents | Low | Early (v0.x) |
| **Vercel AI SDK** | Web apps, streaming | React integration, edge computing | Low | Growing |
| **AutoGen (Microsoft)** | Research, complex scenarios | Flexible, conversation-based | High | Evolving |
| **Anthropic Prompt Caching** | High-volume, long contexts | Native to Claude API, 90% discount | Low | New (2025) |

**Recommendation by use case**:
- **RAG system**: LlamaIndex (specialized) or LangChain (flexibility)
- **Chat app**: Vercel AI SDK (web) or LangChain (flexible)
- **Autonomous agents**: CrewAI (simple) or AutoGen (research)
- **Simple API calls**: None needed (direct SDK)

---

## Vector Database Comparison

| Database | Pricing Model | Best For | Strengths | Tradeoffs |
|----------|---------------|----------|-----------|-----------|
| **Pinecone** | $0.40/1K vectors/mo + query costs | Managed RAG, fast scaling | No ops, serverless, fast | Expensive at scale, vendor lock-in |
| **Weaviate** | Self-hosted free, cloud $75+/mo | Enterprise RAG, generative search | Open-source, GraphQL API | Complex deployment |
| **Qdrant** | Self-hosted free, cloud $240+/mo | High-performance vector search | Rust-based, very fast | Smaller ecosystem |
| **pgvector** | PostgreSQL extension (free) | Existing Postgres deployments | Already own DB, free | Limited vector-specific features |
| **Chroma** | Open-source free | Lightweight embedding storage | Simple, fast setup | Limited scaling features |
| **Milvus** | Self-hosted free | Large-scale embeddings (>50M) | Highly scalable, performance | Kubernetes required |

### Decision Matrix for Vector DB
```
IF <100K vectors AND using PostgreSQL
  → pgvector (free, integrated)

IF <1M vectors AND want managed service
  → Pinecone (simple, but pricier)

IF <1M vectors AND cost-conscious
  → Qdrant or Weaviate (self-hosted or cloud)

IF >10M vectors
  → Milvus (self-hosted) or specialized at-scale vendor

IF prototype/MVP
  → Chroma or in-memory vector store
```

**Cost example** (1M vectors, 100K monthly queries):
- Pinecone: ~$400-600/month
- pgvector (self-hosted): ~$20-50/month (server cost)
- Qdrant cloud: ~$240/month + query costs

---

## RAG Architecture Patterns

### Pattern 1: Basic RAG Workflow
```
User Query
    │
    ├─→ Embed Query (small embedding model)
    │
    ├─→ Vector Search (retrieve top-k docs)
    │
    ├─→ Rank/Filter Results
    │
    ├─→ Build Context (chunk + combine results)
    │
    └─→ LLM (with context in system message)
           │
           └─→ Response to User
```

**Key decisions**:
- Embedding model: small & fast (all-MiniLM-L6-v2, text-embedding-3-small)
- Chunk size: 256-1024 tokens (balance retrieval precision vs. context window)
- Top-k: typically 3-5 docs for single-query RAG
- Re-ranking: use a cross-encoder for better relevance (10-20% improvement)

### Pattern 2: Hybrid RAG (Vector + Keyword)
```
User Query
    │
    ├─→ Vector Search (semantic)
    │
    ├─→ BM25/Keyword Search (exact match)
    │
    ├─→ Combine & De-duplicate Results
    │
    └─→ LLM Context Building
```

**When to use**: Documents with specific terminology, IDs, or exact phrases users search for

### Pattern 3: GraphRAG
```
Documents
    │
    ├─→ Extract Entities (LLM)
    │
    ├─→ Build Knowledge Graph
    │
    ├─→ Store as Graph DB
    │
    ├─→ Multi-hop Traversal for Query
    │
    └─→ LLM Reasoning over Paths
```

**Benefits**:
- Better for multi-hop reasoning ("What are the implications of X on Y?")
- Reduces hallucination by explicit relationship tracking
- More interpretable results

**Tradeoff**: Requires more infrastructure (graph DB), slower inference

### Pattern 4: Multi-Stage Retrieval
```
User Query
    │
    ├─→ Stage 1: Dense Retrieval (vector search, 50 docs)
    │
    ├─→ Stage 2: Lexical Search on Stage 1 Results (20 docs)
    │
    ├─→ Stage 3: LLM Relevance Ranking (top 3 docs)
    │
    └─→ Final Context for LLM
```

**Benefits**:
- Higher quality results than single-stage
- Catches edge cases (exact keyword matches)
- Computational efficiency (filter early stages)

---

## Cost Optimization Strategies

### Strategy 1: Semantic Caching
**Impact**: 40-60% cost reduction for typical workloads

```javascript
// Cache responses semantically
const cache = new SemanticCache(vectorDB);

async function respond(query) {
  const cached = await cache.get(query, similarity=0.95);
  if (cached) {
    return cached.response; // Instant, zero cost
  }

  const response = await llm.complete(query);
  await cache.set(query, response);
  return response;
}
```

**How it works**: Embed the query, search similar embeddings in cache, return cached response if >95% similar

### Strategy 2: Prompt Compression
**Impact**: 6-95% token savings depending on technique

**Techniques**:
1. **Summarization**: Compress documents before passing to LLM
2. **Token pruning**: Remove stop words, low-information tokens
3. **Abstraction**: Convert examples to structured templates
4. **Selective context**: Only pass relevant docs (hybrid RAG)

**Tools**: `llmlingua`, manual summarization, extract-then-generate patterns

**Example savings**:
- 1000-token document → 100-token summary (90% savings)
- But: slight quality loss, must validate

### Strategy 3: Model Routing
**Impact**: 15-50x cost reduction on easy queries

**Logic**:
```
Simple task (classify sentiment, extract entity)
  → Use Haiku/mini ($0.80/1M)

Medium task (summarize, answer from context)
  → Use Sonnet ($3/1M)

Complex task (reasoning, creative generation)
  → Use Opus ($15/1M)
```

**Cost breakdown example** (1M daily requests):
- All Opus: $15,000/day
- With routing (50% Haiku, 30% Sonnet, 20% Opus): $1,200/day (92% savings)

### Strategy 4: Prompt Caching
**Impact**: 90% cost reduction on repeated context (Claude native), 50% on some OpenAI models

**Native caching** (Claude):
```
Request 1: 10K tokens context + 100 token query = ~$0.30
Request 2-10: Reuse cached context = ~$0.03 each

Cost: $0.30 + (9 × $0.03) = $0.57 vs. $3.00 without cache
```

**When to use**:
- RAG with consistent knowledge base (Wikipedia, company docs)
- Long system prompts (tone, guidelines)
- Multi-turn conversations

### Strategy 5: Batch Processing
**Impact**: 50% cost reduction for non-latency-critical work

**Example**: Process 1000 customer reviews overnight vs. real-time
- Real-time: $3,000 (expensive models, low latency)
- Batch: $1,500 (cheaper models, async processing)

---

## Self-Hosting vs. API Decision

### Decision Matrix

| Factor | Self-Host (Ollama/vLLM) | API (OpenAI/Anthropic) |
|--------|------------------------|------------------------|
| **Cost/month** | $20-200 (GPU) | $500-5,000+ (at scale) |
| **Setup time** | 2-4 hours | 15 minutes |
| **Model quality** | 85-95% (Llama 4, Qwen 3.5) | 95%+ (Opus 4.6, GPT-5) |
| **Latency** | 100-500ms | 500-2,000ms |
| **Privacy** | ✅ Data stays local | ✗ Third-party processing |
| **Reliability** | Self-managed ⚠️ | 99.99% SLA |
| **Ops overhead** | GPU management, scaling | None |
| **Best for** | Privacy, high volume | Production quality, simplicity |

### Cost Breakeven Analysis

**When is self-hosting cheaper?**

```
Self-host cost: GPU_cost/month + ops_labor
API cost: (token_count * price_per_token) / 30 days

Breakeven = GPU_cost / (token_savings_per_day * 30)
```

**Example**:
- GPU server: $500/month (rented)
- Daily requests: 100K
- Avg tokens: 500 per request = 50M tokens/day
- API cost at $0.003/1K: 50M × $0.000003 = $150/day = $4,500/month
- Breakeven: Self-host saves $4,000/month

**Recommendation**:
- <10K daily requests: Use API (simplicity wins)
- 10K-100K daily requests: Evaluate self-hosting
- >100K daily requests: Self-hosting is likely cheaper
- Privacy-critical: Self-host regardless of cost

---

## Adding AI to Existing Apps: Step-by-Step Pattern

### Phase 1: Assessment
1. Identify high-impact use cases (support automation, content generation, search)
2. Estimate token volume (queries/day × avg tokens)
3. Calculate ROI (time saved × hourly rate vs. AI cost)
4. Choose: Enhance existing app or build new AI service

### Phase 2: Foundation
1. Set up cost tracking early (via gateway or middleware)
2. Implement request logging (for optimization later)
3. Choose gateway (liteLLM for open-source, Helicone for managed)
4. Set up monitoring for latency and errors

### Phase 3: MVP Feature
1. Pick one narrow use case (e.g., "AI chat in support")
2. Implement with direct API call (no orchestration yet)
3. Add caching for common questions
4. Monitor cost, latency, quality for 2 weeks

### Phase 4: Scale & Optimize
1. Implement semantic caching (if >1K daily requests)
2. Add model routing (if cost is concern)
3. Evaluate RAG need (if many context-based queries)
4. Add vector DB only when retrieval is bottleneck

### Phase 5: Production Hardening
1. Implement retry logic and fallback providers
2. Set rate limits per user/API key
3. Build observability dashboard
4. Alert on cost anomalies (>20% daily variance)

### Code Example: Adding AI Chat to Existing App

```python
# Step 1: Direct API call (MVP)
from anthropic import Anthropic

async def chat_endpoint(message: str):
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-haiku",
        messages=[{"role": "user", "content": message}],
        max_tokens=500,
    )
    return response.content[0].text

# Step 2: Add caching (after 1K requests/day)
from functools import lru_cache

@lru_cache(maxsize=1000)
async def chat_cached(message: str):
    return await chat_endpoint(message)

# Step 3: Add semantic caching (after 5K requests/day)
async def chat_semantic_cached(message: str):
    embedding = embed_model.embed(message)
    cached = await semantic_cache.get(embedding, threshold=0.95)
    if cached:
        return cached

    response = await chat_endpoint(message)
    await semantic_cache.set(embedding, response)
    return response

# Step 4: Add cost tracking
async def chat_with_tracking(message: str, user_id: str):
    response = await chat_semantic_cached(message)

    # Track cost
    cost = calculate_cost(response.usage)
    db.save_usage(user_id, cost, tokens=response.usage.total_tokens)

    return response
```

---

## AI Observability Tools

| Tool | Pricing | Best For | Features |
|------|---------|----------|----------|
| **Langfuse** | Free tier, $25/mo | Complete LLM monitoring | Cost tracking, latency, quality, traces |
| **Helicone** | Free tier, $29/mo | Gateway + observability | Semantic caching, analytics, low overhead |
| **Braintrust** | Free, $30/mo | Human feedback & evaluation | LLM-as-judge, prompt monitoring |
| **LangSmith** | Free tier, $39/mo | LangChain integration | Tracing, debugging, cost analysis |
| **OpenObserve** | Open-source | High-volume logging | Cost-effective at scale, self-hosted |

### Key Metrics to Monitor

1. **Cost per feature**
   - Track cost by feature, user, org
   - Alert if daily cost >20% above average

2. **Latency percentiles**
   - P50, P95, P99 (not just average)
   - Identify outliers (long-running queries)

3. **Quality metrics**
   - User feedback (thumbs up/down)
   - LLM-as-judge evaluation (relevance, accuracy)
   - Compare models on same queries

4. **Token efficiency**
   - Avg tokens per request (optimization opportunity)
   - Cache hit rate (semantic caching effectiveness)

5. **Error tracking**
   - Rate limit hits
   - Timeout frequency
   - Provider outages

---

## Common AI Architecture Mistakes

### Mistake 1: No Cost Controls
**Problem**: Unbounded token spending, surprise $10K bills

**Solution**:
- Implement per-request cost limits
- Set daily/monthly budgets by feature
- Route expensive queries to cheaper models
- Alert on 20% daily cost variance

### Mistake 2: Using Expensive Models for Simple Tasks
**Problem**: Paying $15/1M tokens to classify sentiment

**Solution**:
- Implement model routing
- Reserve expensive models for complex reasoning
- Use Haiku for 95% of queries (cost: $0.80/1M)

### Mistake 3: No Rate Limiting on AI Endpoints
**Problem**: User accidentally calls AI endpoint in loop, costs spike

**Solution**:
- Implement per-user rate limits (e.g., 10 requests/minute)
- Implement per-API-key quotas (monthly limit)
- Add exponential backoff on retry

### Mistake 4: Tight Coupling to Single Provider
**Problem**: OpenAI goes down, entire feature is broken

**Solution**:
- Use gateway pattern (liteLLM, Helicone)
- Configure failover to secondary provider
- Test failover regularly

### Mistake 5: Synchronous AI Calls Blocking Requests
**Problem**: User waits 5 seconds for LLM response, request times out

**Solution**:
- Make AI calls async (background job queue)
- Return immediately with "processing" message
- Update UI when response is ready (WebSocket, polling)
- Use streaming for interactive features

### Mistake 6: No Semantic Caching
**Problem**: Processing identical queries twice, paying 2x cost

**Solution**:
- Implement semantic caching at gateway layer
- Set similarity threshold (0.95 = nearly identical)
- Expected: 40-60% cache hit rates

### Mistake 7: RAG Without Relevance Ranking
**Problem**: Passing irrelevant documents to LLM, poor quality results

**Solution**:
- Implement multi-stage retrieval (vector + lexical + re-rank)
- Use cross-encoder for ranking (10-20% quality improvement)
- Monitor retrieval hit rates

### Mistake 8: No Observability
**Problem**: Can't explain why costs are rising or quality degraded

**Solution**:
- Log every request (model, tokens, cost, quality)
- Build dashboards (cost over time, latency, errors)
- Set up alerts for anomalies

---

## Decision Logic Flowchart

```
STARTING POINT: "I want to add AI to my app"

1. WHAT FEATURE?
   ├─ Chat/Q&A?
   │  └─ Need RAG? YES → Go to RAG Setup
   │              NO → Use Direct API Call + Semantic Caching
   │
   ├─ Classification/Extraction?
   │  └─ Use Haiku model, implement model routing
   │
   ├─ Content generation?
   │  └─ Use Opus, implement prompt caching
   │
   └─ Image/Multimodal?
      └─ Use vision-capable model (GPT-4V, Claude 3 Opus)

2. SCALE ESTIMATE (requests/day)
   ├─ <100: Skip optimization, use API directly
   ├─ 100-1K: Add basic request logging
   ├─ 1K-10K: Implement semantic caching
   ├─ 10K-100K: Add model routing
   └─ >100K: Consider self-hosting or RAG optimization

3. COST CONCERN?
   ├─ Budget <$100/mo?
   │  └─ Use cheap models (Haiku, mini) + aggressive caching
   │
   ├─ Budget <$1K/mo?
   │  └─ Use routing + semantic caching + prompt caching
   │
   └─ Budget >$1K/mo?
      └─ Can optimize aggressively OR consider self-hosting

4. RAG SETUP (if needed)
   ├─ Vector DB choice:
   │  ├─ <100K vectors? → pgvector or Chroma
   │  ├─ <1M vectors? → Pinecone or Qdrant
   │  └─ >1M vectors? → Milvus or specialized vendor
   │
   ├─ Retrieval pattern:
   │  ├─ Simple search? → Basic RAG (vector only)
   │  ├─ Mixed keyword+semantic? → Hybrid RAG
   │  └─ Complex reasoning? → GraphRAG
   │
   └─ Orchestration:
      ├─ Simple chains? → LangChain
      ├─ RAG-heavy? → LlamaIndex
      └─ Agents? → CrewAI or AutoGen

5. PROVIDER SELECTION
   ├─ Privacy-critical?
   │  └─ Self-host (Ollama, vLLM)
   │
   ├─ Need best quality?
   │  └─ Use Claude Opus 4.6 3.5 or GPT-4
   │
   ├─ Cost-sensitive?
   │  └─ Use routing + cheap models
   │
   └─ Long contexts (>50K tokens)?
      └─ Use Claude Opus 4.6 (200K) or Gemini 2.0 (1M)

6. MONITORING SETUP
   ├─ Log every request
   ├─ Track cost, latency, quality
   ├─ Set alerts for anomalies
   └─ Review weekly for optimization
```

---

## Cost Calculation Template

Use this template to estimate AI feature costs:

```
Inputs:
- Daily requests: X
- Avg input tokens/request: Y
- Avg output tokens/request: Z
- Model: M
- Cache hit rate: H%

Calculation:
1. Input token cost:
   = (X * Y * (1 - H%)) * (input_price_per_1M_tokens / 1_000_000)

2. Output token cost:
   = (X * Z) * (output_price_per_1M_tokens / 1_000_000)

3. Total daily cost:
   = Input cost + Output cost

4. Monthly cost:
   = Total daily cost * 30

Example (Claude Haiku 4.5):
- 10,000 requests/day
- 500 input tokens, 200 output tokens avg
- 50% cache hit rate

Input: 10K * 500 * 0.5 * ($0.80 / 1M) = $2/day
Output: 10K * 200 * ($4 / 1M) = $8/day
Total: $10/day = $300/month

With prompt caching (90% discount on cached):
Input: 10K * 500 * ($0.08 / 1M) = $0.40/day
Output: 10K * 200 * ($4 / 1M) = $8/day (per-request output still costs)
Total: $8.40/day = $252/month
```

---

## Pricing Stability Note

**PRICING_STABILITY: low | last_verified: 2026-03 | check_interval: 3_months**

AI pricing changes rapidly:
- Model pricing typically decreases 5-10% every 3-6 months
- New models are released frequently (better quality at same price)
- Caching discounts improve with provider competition
- Self-hosting costs depend on GPU market (volatile)

**Recommendations**:
1. Re-evaluate provider pricing quarterly
2. Test new models on your workload
3. Monitor for new caching/optimization features
4. Keep alternative providers benchmarked
5. Build cost tracking from day one (easier to optimize later)

---

## Related References
- [AI/ML Integration Tech Stack Research](./27-ai-ml-integration-tech-stack.md) — Comprehensive AI/ML tool evaluation and selection
- [Data Pipelines, ETL/ELT, and Data Engineering Patterns](./60-data-pipelines-etl-elt.md) — Data infrastructure for training and processing
- [GDPR & CCPA/CPRA Compliance Architecture Guide](./43-compliance-governance.md) — Privacy considerations for AI systems
- [Performance Benchmarks 2025-2026: Data-Driven Technology Selection](./47-performance-benchmarks-2025-2026.md) — Latency and throughput metrics for AI services
- [MASTER COST REFERENCE MATRIX](./32-master-cost-reference-matrix.md) — AI model pricing and infrastructure costs

---

## References & Further Reading

- **OpenAI Pricing**: https://openai.com/pricing
- **Anthropic Pricing**: https://www.anthropic.com/pricing
- **LangChain Docs**: https://python.langchain.com/
- **LlamaIndex Docs**: https://docs.llamaindex.ai/
- **Vector DB Comparison**: https://www.anyscale.com/blog/vector-databases/
- **RAG Best Practices**: https://arxiv.org/abs/2312.10997
- **AI Cost Optimization**: https://www.helicone.ai/blog/cost-optimization

---

**Last updated**: March 2026
**Maintenance**: Review quarterly for pricing changes and new patterns
**Audience**: Full-stack developers, platform engineers, ML engineers
