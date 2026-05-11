# Search Observability, Monitoring, and Analytics: A Comprehensive Reference

## Table of Contents
1. [Search Metrics Taxonomy](#search-metrics-taxonomy)
2. [Query Analytics](#query-analytics)
3. [Click Analytics](#click-analytics)
4. [Relevance Monitoring](#relevance-monitoring)
5. [Infrastructure Monitoring](#infrastructure-monitoring)
6. [Dashboards and Alerting](#dashboards-and-alerting)
7. [Search Logging](#search-logging)
8. [Debugging Search Issues](#debugging-search-issues)
9. [Search Quality Programs](#search-quality-programs)
10. [Tools and Platforms](#tools-and-platforms)

---

## Search Metrics Taxonomy

Understanding search metrics is foundational to building observable search systems. Search metrics fall into several categories: performance metrics, quality metrics, and operational metrics.

### Latency Metrics: P50, P95, P99

Latency percentiles represent the distribution of response times across all requests, providing critical insights into user experience and system performance.

**P50 (Median):** The 50th percentile representing the middle value in the distribution. Half of all requests complete faster than P50, and half take longer. This metric represents the "typical" request experience but can be misleading as it doesn't reveal tail behavior.

**P95:** The 95th percentile where 95% of requests complete within this time. Only 5% of requests experience latency equal to or worse than P95. This metric captures the experience of the vast majority of users.

**P99:** The 99th percentile where 99% of requests complete within this time. This metric captures the tail latency—the slowest 1% of requests. P99 is critical for identifying when the system degrades for small portions of the user population.

Why percentiles matter: Most distributed systems exhibit a "hockey stick" curve when latency is plotted across percentiles. Performance remains relatively flat through P95, then shoots up sharply at P99 and beyond. This tail behavior is often caused by:
- Garbage collection pauses in the JVM
- Disk I/O operations
- Network contention
- Resource contention under peak load
- Query complexity outliers

**Best Practices for Latency Monitoring:**
- Track all three metrics (P50, P95, P99) continuously
- Set SLOs around P95 or P99 rather than average latency
- Monitor latency percentiles over time windows (1-minute, 5-minute, 1-hour windows)
- Alert when P99 degrades, not P50
- Use time-series databases (Prometheus, Datadog) to aggregate percentiles

### Throughput Metrics: QPS and RPS

Queries Per Second (QPS) and Requests Per Second (RPS) measure how many requests your system handles within a unit time.

**QPS Definition:** The total number of search queries processed by the system in one second, including all query types (search, autocomplete, filtering, etc.).

**Capacity Planning:** Understanding your QPS capacity is essential for:
- Determining when to scale horizontally
- Identifying bottleneck resources
- Predicting future infrastructure needs
- Sizing caches and connection pools

**Metrics to Track:**
- Peak QPS (highest load during peak hours)
- Average QPS (baseline load)
- QPS per shard or per cluster node
- QPS per query type or endpoint

### Error Rates

Error rates quantify the proportion of requests that fail or return degraded responses.

**Categories of Errors:**
- **4xx errors:** Client errors (malformed queries, invalid parameters, unauthorized access)
- **5xx errors:** Server errors (service unavailable, timeout, backend failures)
- **Timeout errors:** Queries that exceed maximum execution time
- **Partial errors:** Queries that partially succeed (e.g., some shards respond, others timeout)

**Error Rate Calculations:**
- Error Rate % = (Failed Requests / Total Requests) × 100
- Error Budget = (1 - Target SLO) × Time Period
  - Example: For a 99.9% SLO over 1 month (2,592,000 seconds), error budget = 2,592 seconds

**Monitoring Practices:**
- Track error rates by type, endpoint, and shard
- Set alerts for sudden spikes in error rates (e.g., >0.1%)
- Investigate correlations between error spikes and other system changes
- Maintain error budget dashboards to track remaining allowance

### Zero-Result Rate (ZRR)

Zero-result rate measures the proportion of search queries that return no results—a critical indicator of search effectiveness and data quality.

**Significance:**
- High ZRR indicates:
  - User intent not matching indexed content
  - Spelling mismatches or language barriers
  - Content gaps in the data
  - Poor query expansion or synonym handling
  - Overly strict filtering parameters

**Measurement:**
- ZRR % = (Queries with 0 Results / Total Queries) × 100
- Track ZRR trends over time (daily, weekly, monthly)
- Segment ZRR by:
  - Query type or category
  - User segment
  - Time period (peak vs. off-peak)
  - Geographic region

**Improvement Strategies:**
- Analyze zero-result queries to identify content gaps
- Implement query expansion and fuzzy matching
- Add synonyms and related terms to improve coverage
- Use zero-result queries as demand signals for new products or content
- Implement fallback strategies (e.g., show similar results, suggest corrections)

### Click-Through Rate (CTR)

Click-through rate measures what percentage of search results receive clicks from users.

**Definitions:**
- **SERP CTR:** Clicks on any result divided by total impressions
- **Position CTR:** Clicks at a specific position divided by impressions at that position
- **Result CTR:** Clicks on a specific result across all positions

**Position Bias in CTR:**
- Top-ranked results receive disproportionately more clicks due to position bias
- Position 1 typically has 10-100x higher CTR than position 10
- CTR cannot be used directly as a relevance signal without accounting for position bias
- This is why click models (cascade, position-based) are necessary

**Using CTR Data:**
- Identify which queries have suspiciously low CTR (possible relevance issues)
- Monitor CTR by result position to understand user satisfaction
- Track CTR trends to detect degradation in search quality
- Use CTR as a signal for automatic ranking adjustments (with care)

### Abandonment Rate

Abandonment rate measures the percentage of search sessions where users perform no clicks on any result.

**Causes:**
- Highly relevant results visible above the fold
- User found an answer in the query suggestion
- Results were clearly irrelevant (user abandons without clicking)
- User was exploring but found information via other means
- Search quality issues (user frustrated and leaves)

**Interpretation:**
- Some abandonment is healthy (user satisfied with top result)
- Sudden increases in abandonment can indicate quality degradation
- Correlate abandonment with other metrics to understand root causes
- Segment by query type, query length, and user segment for deeper insights

### Mean Reciprocal Rank (MRR)

Mean Reciprocal Rank measures where the first relevant result appears in the ranking.

**Calculation:**
- For each query, find the rank of the first relevant result
- Reciprocal Rank = 1 / (Rank of First Relevant Result)
- MRR = Average of all reciprocal ranks

**Example:**
- Query 1: First relevant result at position 2 → Reciprocal Rank = 0.5
- Query 2: First relevant result at position 1 → Reciprocal Rank = 1.0
- Query 3: First relevant result at position 5 → Reciprocal Rank = 0.2
- MRR = (0.5 + 1.0 + 0.2) / 3 = 0.57

**Use Cases:**
- Ideal for scenarios with a single "correct" answer (e.g., factual queries)
- Works well for information retrieval evaluation
- MRR focuses on finding the right answer quickly, not ranking all relevant results

---

## Query Analytics

Query analytics provides insights into user search behavior, revealing patterns that inform content strategy, algorithm improvements, and demand signals.

### Top Queries Analysis

Top queries are the most frequently searched terms—typically the top 1,000 queries represent a significant portion of overall search volume.

**Characteristics:**
- Often capture high-volume, broad intent queries
- Provide baseline understanding of user needs
- Enable direct optimization (landing pages, merchandising, content)
- Privacy-safe (aggregated above certain thresholds)

**Analysis Frameworks:**
1. **Intent Classification:** Categorize top queries by type (navigational, informational, transactional, local)
2. **Success Metrics:** Cross-reference CTR, abandonment, dwell time by query
3. **Content Alignment:** Ensure index contains content matching top query intent
4. **Merchandising Opportunities:** Identify queries suitable for promoted results, ads, or special sections

**Common Tools:**
- Google Search Console (for web search)
- Amazon Kendra Analytics
- Native platform dashboards (Shopify, WooCommerce, etc.)
- Custom analytics using logs and query parsing

### Long-Tail Distribution

The long-tail represents the vast majority of unique queries—many queries searched only once or a few times—but collectively represent significant search volume.

**Characteristics:**
- 80-90% of queries are unique or low-frequency
- Difficult to optimize individually due to low volume
- Represent emerging trends and niche interests
- Contain valuable intent signals for model training

**Handling Long-Tail Queries:**
- Use query expansion and semantic matching to broaden results
- Leverage synonyms and related term mapping
- Implement fuzzy matching for typos and variations
- Use machine learning to understand intent despite variations
- Create fallback ranking strategies for rare queries

**Demand Signals from Long-Tail:**
- Zero-result long-tail queries reveal content gaps
- Sudden spikes in rare query searches indicate emerging trends
- Long-tail queries often have higher conversion intent than top queries
- Product teams should monitor long-tail for feature requests and new opportunities

### Query Categorization

Organizing queries into categories enables segmented analysis and targeted optimization.

**Categorization Schemes:**
1. **Intent-Based:** Navigational, informational, transactional, local
2. **Domain-Based:** By product category, content type, or business vertical
3. **Linguistic-Based:** Query length, presence of operators, language
4. **Temporal-Based:** Seasonal, trending, evergreen
5. **Funnel-Based:** Top-of-funnel awareness, mid-funnel consideration, bottom-funnel purchase

**Benefits:**
- Identify which categories have poor performance
- Apply targeted ranking algorithms per category
- Allocate resources to optimize high-impact categories
- Detect category-specific quality issues

### Trending Queries

Trending queries are searches experiencing rapid growth compared to baseline.

**Detection Methods:**
- Compare week-over-week or month-over-month growth
- Use statistical anomaly detection (e.g., Z-score, isolation forests)
- Monitor for unusual spikes in volume
- Track emerging terms gaining popularity

**Operational Value:**
- Alert content and merchandising teams to create timely content
- Identify new product opportunities
- Inform ad bidding strategies
- Detect negative trends (e.g., complaint-related queries)

**Example Trends:**
- Seasonal products gaining traction as season approaches
- Breaking news driving related searches
- Viral content or events creating search spikes
- New features or products discovering initial demand

### Failed Queries Analysis

Failed queries are searches returning zero results or results matching user intent poorly.

**Identification:**
- Queries with ZRR = 1 (absolutely zero results)
- Queries with very low CTR relative to query frequency
- Queries with high abandonment rate
- Queries in search logs but not in result logs

**Analysis Process:**
1. **Categorize Failure Mode:**
   - No matching content (content gap)
   - Matching content exists but not indexed
   - Indexed content but poor ranking
   - Query too specific (over-specification)

2. **Prioritize for Fixing:**
   - High-volume queries affecting many users
   - Queries with high commercial value
   - Queries indicating product gaps
   - Queries with easy fixes (e.g., synonym addition)

3. **Implement Solutions:**
   - Add synonyms or query expansion rules
   - Create or index missing content
   - Adjust ranking weights for better matches
   - Implement partial matching as fallback
   - Deploy spelling corrections

---

## Click Analytics

Click data provides online signals about user satisfaction and content relevance, but requires sophisticated modeling to account for position bias and examine bias.

### Click Models Framework

Click models are probabilistic frameworks that explain observed click patterns and separate relevance signals from position bias.

**The Position Bias Problem:**
Users are more likely to click on top-ranked results regardless of actual relevance. A click on result #1 may indicate either high relevance or just position bias. Click models infer the underlying relevance by accounting for this bias.

### Cascade Model (CM)

The Cascade Model assumes sequential examination behavior: users scan results from top to bottom and stop at the first result they click.

**Assumptions:**
1. Users examine results sequentially from top to bottom
2. All top-ranked results are examined
3. Results below an unexamined result are also unexamined (cascade assumption)
4. A click indicates relevance, and the user stops examining after a click

**Mathematical Framework:**
- P(click at position k) = P(examined at k) × P(relevant | examined at k)
- P(examined at 1) = 1 (top result always examined)
- P(examined at k) = P(examined at k-1) × P(not relevant | examined at k-1)

**Strengths:**
- Simple and interpretable
- Works well for queries where users find a satisfying result early
- Minimal computation overhead

**Limitations:**
- Doesn't account for users examining multiple results before clicking
- Assumes stops after first click (not true for exploratory searches)
- Position bias is conflated with relevance

### Position-Based Model (PBM)

The Position-Based Model decouples position bias from relevance by modeling examination probability as dependent only on position, not on previous results.

**Assumptions:**
1. Examination probability depends only on position (P_exam(k))
2. Click probability depends on relevance and examination (P_click(k) = P_exam(k) × P_rel)
3. Different items at the same position have the same examination probability

**Advantages:**
- More flexible than cascade model
- Position bias is explicitly modeled and can be quantified
- Can handle cases where users examine multiple results without clicking

**Limitations:**
- Assumes position bias is uniform across all queries
- Doesn't account for differences in query-result relevance
- May overestimate position effect

### Dynamic Bayesian Network (DBN) Model

The DBN extends cascade and position-based models to incorporate temporal sequences and complex dependencies.

**Key Features:**
- Models sequential clicking behavior
- Incorporates both position bias and result relevance
- Can include temporal aspects (time between clicks)
- Captures examination probability based on previous interactions

**Application:** DBN models are particularly useful for complex search sessions where users review multiple results over time before making decisions.

### Click-Through Rate by Position

CTR varies dramatically by position, making position-specific analysis essential.

**Typical CTR Distribution:**
- Position 1: 10-30% CTR
- Position 2: 5-15% CTR
- Position 3: 3-10% CTR
- Position 4: 2-5% CTR
- Position 5+: <2% CTR
- Below fold: <1% CTR

**Position Effects:**
- Each additional position typically reduces CTR by 30-50%
- Visibility on viewport (above/below fold) has dramatic impact
- Moving from position 10 to position 1 can increase CTR by 10-100x

**Using Position-Specific CTR:**
- Monitor CTR trends by position to detect quality changes
- Identify when top results fail to deliver expected CTR
- Calculate position-adjusted relevance scores
- A/B test ranking changes using position-specific impact

### Dwell Time Analysis

Dwell time measures how long a user spends on a clicked search result before returning to search results.

**Measurement:**
- Dwell Time = Time on Page - Time on SERP
- Typically requires click instrumentation (click time, return time)
- Should account for multiple visits to same result

**Interpretation:**
- **Long Dwell (>2 minutes):** User likely satisfied and engaged with content
- **Medium Dwell (30 seconds - 2 minutes):** User reading content, possibly satisfied
- **Short Dwell (<30 seconds):** User either found answer quickly or left unsatisfied
- **Zero Dwell:** User immediately returns (likely unsatisfied)

**Satisfaction Correlation:**
Research shows strong correlation between dwell time and user satisfaction:
- Queries with average dwell time >90 seconds correlate with high satisfaction
- Short dwell times correlate with quality issues or user dissatisfaction
- Dwell time is a more reliable signal than clicks alone

**Using Dwell Time:**
- Segment queries and results by dwell time patterns
- Compare dwell time before/after ranking changes (A/B testing)
- Identify queries with consistently short dwell times for optimization
- Use as secondary signal with clicks to infer relevance

**Dwell Time Challenges:**
- Requires client-side instrumentation
- Privacy concerns with user-level tracking
- Can be skewed by content length (longer articles naturally have longer dwell)
- Context switching (user may switch tabs, reducing dwell measurement)

### SERP Click Maps

SERP click maps are heatmaps showing where and how frequently users click across the search results page.

**Benefits:**
- Visual representation of user engagement patterns
- Identifies dead zones (rarely clicked regions)
- Shows whether users scroll below the fold
- Reveals format effectiveness (organic vs. featured vs. ads)

**Typical Click Patterns:**
- Heavy concentration at top-left (reading direction bias)
- Organic results receive more clicks than ads in most verticals
- Featured snippets often attract clicks despite position
- Long-tail traffic scrolls deeper and explores more results

**Optimization Insights:**
- Ensure high-quality results in top positions (primary click zone)
- Test featured result formats to improve engagement
- Use below-fold space strategically for less essential content
- Monitor click maps to detect UX changes (viewport size, page layout)

---

## Relevance Monitoring

Relevance is the core metric for search quality—whether results match user intent. Both offline and online metrics are essential for comprehensive evaluation.

### Offline Metrics

Offline metrics evaluate search quality using historical judgment data without requiring live user interaction.

#### NDCG (Normalized Discounted Cumulative Gain)

NDCG measures ranking quality by considering both the relevance of items and their positions, with lower positions receiving logarithmic discount.

**Calculation:**
- DCG = Σ(relevance_i / log2(position_i + 1))
- IDCG = Best possible DCG (perfect ranking)
- NDCG = DCG / IDCG (normalized to 0-1 range)

**Example:**
Suppose relevance judgments are 1=not relevant, 2=somewhat relevant, 3=highly relevant

Query Result Set:
1. Result A (relevance 3)
2. Result B (relevance 2)
3. Result C (relevance 3)
4. Result D (relevance 0)

DCG = 3/log2(2) + 2/log2(3) + 3/log2(4) + 0/log2(5)
    = 3/1 + 2/1.58 + 3/2 + 0
    = 3 + 1.26 + 1.5
    = 5.76

Ideal ranking would be:
1. Result A or C (relevance 3)
2. Result C or A (relevance 3)
3. Result B (relevance 2)
4. Result D (relevance 0)

IDCG = 3/1 + 3/1.58 + 2/2 = 3 + 1.90 + 1 = 5.90

NDCG = 5.76 / 5.90 = 0.976 (97.6%)

**Interpretation:**
- NDCG@5: Only first 5 results count (mobile-friendly metric)
- NDCG@10: Standard metric for full SERP evaluation
- NDCG ranges from 0 (worst) to 1 (perfect)
- 0.7+ is typically considered good relevance

**Strengths:**
- Accounts for graded relevance (not just binary)
- Position-aware (penalizes bad rankings)
- Normalized for comparison across queries

**Limitations:**
- Requires labeled judgment data
- Offline only—doesn't measure real user satisfaction
- Judgments may not reflect true user intent
- Labor-intensive to create judgment sets

#### MAP (Mean Average Precision)

MAP measures the precision of relevant items at different cutoff points, averaging precision across all queries.

**Calculation:**
- For each query and position k:
  - Precision@k = (Relevant items in top k) / k
  - AP = Σ(Precision@k) / (Number of relevant items)
- MAP = Average of AP across all queries

**Example:**
Query: "machine learning algorithms"
Relevant items: 3 total

Results:
1. Relevant ✓ - Precision@1 = 1/1 = 1.0
2. Not relevant ✗ - Precision@2 = 1/2 = 0.5
3. Relevant ✓ - Precision@3 = 2/3 = 0.667
4. Relevant ✓ - Precision@4 = 3/4 = 0.75
5. Not relevant ✗ - Precision@5 = 3/5 = 0.6

AP = (1.0 + 0.667 + 0.75) / 3 = 0.806

**Best For:**
- When you want to know how many relevant results are in top K
- Emphasizes getting all relevant items ranked high
- Works better when number of relevant items varies by query

**Limitations:**
- Doesn't penalize as heavily for bad placements as NDCG
- Assumes binary relevance (relevant/not relevant)
- Ignores positions without relevant items

#### MRR (Mean Reciprocal Rank)

MRR focuses on finding the first relevant result as quickly as possible.

**Calculation:**
- Reciprocal Rank = 1 / (position of first relevant result)
- MRR = Average reciprocal ranks across all queries

**Example:**
- Query 1: First relevant at position 1 → RR = 1.0
- Query 2: First relevant at position 3 → RR = 0.333
- Query 3: First relevant at position 2 → RR = 0.5
- MRR = (1.0 + 0.333 + 0.5) / 3 = 0.61

**Best For:**
- Fact queries where one correct answer exists (Wikipedia, Wolfram Alpha)
- Scenarios where finding the right answer quickly is paramount
- Evaluating precision at top-1

**Limitations:**
- Ignores all results after the first relevant one
- Unsuitable when multiple equally valid results exist
- Doesn't capture ranking quality of multiple relevant items

### Online Metrics

Online metrics measure real user interactions with search results, providing ground truth about satisfaction.

#### Click-Through Rate (CTR)

CTR is the proportion of impressions that receive clicks—a direct user satisfaction signal.

**Challenges:**
- Position bias: top results get more clicks regardless of quality
- Examine bias: user may not scroll to see all results
- Intent mismatch: user may click despite relevance mismatch

**Solutions:**
- Use click models to infer relevance from clicks
- Combine with dwell time for stronger signal
- Compare CTR changes within experiments, not absolute values

#### User Dwell Time

As discussed in click analytics, dwell time (time spent on result) correlates with satisfaction.

**Advantages:**
- Less biased by position than clicks
- Objective measurement of engagement
- Captures both clicking behavior and time investment

**Disadvantages:**
- Privacy implications of tracking time on external sites
- Variable by content type (long articles naturally have longer dwell)
- Requires client instrumentation

#### Query Return Rate

Query return rate (how often user returns to search for the same query) is a strong negative signal.

**Interpretation:**
- High return rate: User unsatisfied with initial results
- Low return rate: User satisfied or found answer in first session

**Measurement:**
- Track sessions where same query appears multiple times
- Calculate return rate = (Sessions with query return) / (Total sessions with query)

**Advantages:**
- Strong signal of dissatisfaction
- Naturally accounts for position bias
- Objective and easy to measure

#### Pagination Depth

How deep users scroll or paginate through results indicates satisfaction.

**Patterns:**
- Users stopping at result 3-5: Likely found satisfactory answer
- Users scrolling to page 5+: Unsatisfied with initial results
- Users examining many results: Complex information needs

### Relevance Regression Detection

Relevance regression is when search quality declines—critical to detect early.

**Detection Approaches:**

1. **Statistical Process Control:**
   - Calculate control limits (mean ± 2-3 standard deviations)
   - Alert when metrics fall outside control limits
   - Detect trends in metrics over time

2. **Time-Series Analysis:**
   - Model expected metric values based on history
   - Compare actual vs. predicted values
   - Flag significant deviations

3. **Change-Point Detection:**
   - Identify when metric distribution shifts
   - Correlate with system changes (deployments, updates)
   - Automate root cause analysis

4. **Cohort Analysis:**
   - Compare metrics across user segments
   - Segment by device, location, user type
   - Identify if regression is widespread or localized

**Common Regression Causes:**
- Algorithm changes (ranking, indexing, query processing)
- Index corruptions or data quality issues
- Infrastructure issues (latency, availability)
- Spam or low-quality content infiltration
- External changes (competitor changes, market shifts)

### A/B Testing for Search

A/B testing validates ranking changes improve real user experience.

**Test Design:**
1. **Hypothesis:** "Ranking change X will improve relevance metric Y by Z%"
2. **Control Group:** Existing ranking algorithm
3. **Treatment Group:** New ranking algorithm
4. **Metrics:** Primary (relevance), secondary (CTR, dwell, return rate)
5. **Duration:** Minimum 1-2 weeks to account for day-of-week effects

**Statistical Rigor:**
- Power analysis to determine required sample size
- Minimum difference to detect (MDE)
- Confidence level (typically 95%)
- Account for multiple comparisons correction

**Common Pitfalls:**
- Insufficient sample size (underpowered tests)
- Peeking at results during experiment (stopping early)
- Metric selection bias (cherry-picking metrics)
- Ignoring holdout groups for validation

---

## Infrastructure Monitoring

Search infrastructure monitoring ensures the underlying systems supporting search operate optimally.

### Elasticsearch Cluster Health

Elasticsearch cluster health is the foundation for reliable search.

**Health Status Indicators:**

**Green Status:**
- All primary and replica shards are allocated
- Complete cluster redundancy
- Optimal state for production

**Yellow Status:**
- All primary shards allocated but some replicas unallocated
- Reduced redundancy but searches still work
- Indicates node failures or capacity constraints
- Action required: investigate missing replicas

**Red Status:**
- Some primary shards unallocated
- Data loss possible, searches may fail
- Emergency: immediate investigation required

**Cluster Health API:**
```
GET /_cluster/health
```

Returns: active_shards, active_primary_shards, unassigned_shards, delayed_unassigned_shards, status

### Shard Allocation and Management

Shards are the fundamental unit of parallelism in Elasticsearch.

**Allocation Strategies:**
- **Balanced:** Distributes shards evenly across nodes
- **Awareness:** Allocates based on node attributes (rack, zone, tier)
- **Filtering:** Includes/excludes nodes based on attributes
- **Rebalancing:** Moves shards to optimize distribution

**Monitoring Shards:**
- Unassigned shards: Use _cluster/allocation/explain API to diagnose
- Shard imbalance: Monitor bytes/documents per shard
- Shard movement frequency: High churn indicates instability
- Hot shards: Some shards receive disproportionate query load

**Best Practices:**
- Keep shard count reasonable (typically 1-3 per node)
- Balance shard sizes to prevent hot spots
- Use shard awareness for multi-zone deployments
- Monitor and understand replica placement

### JVM Metrics

Java Virtual Machine (JVM) health directly impacts Elasticsearch performance.

**Critical JVM Metrics:**

**Heap Memory:**
- Current usage: Should stay <75% under normal load
- GC pause duration: Should be <1 second
- Full GC frequency: More than monthly indicates issue
- Young generation GC: Frequent but fast (<100ms)
- Old generation GC: Should be rare

**Garbage Collection:**
- Young generation: Efficient but frequent (seconds)
- Old generation: Slow but rare (minutes or less)
- Full GC: Very slow and should be infrequent
- GC pauses: Stop-the-world pauses impact query latency

**Memory Pressure:**
- JVM memory pressure increases when heap exceeds 75%
- Elasticsearch throttles operations when pressure exceeds 85%
- Increases bulk rejection and query queueing

**Monitoring JVM:**
- Track heap usage trends over time
- Alert on consistent >80% heap usage
- Monitor GC pause duration and frequency
- Use -XX:+PrintGCDetails for detailed GC logging

### Disk I/O Monitoring

Disk performance is a primary bottleneck in search operations.

**Key Metrics:**
- **Latency:** Disk read/write response time (should be <10ms)
- **Throughput:** Bytes read/written per second
- **Utilization:** Percentage of disk resources in use
- **Queue Depth:** Pending I/O operations
- **IOPS:** Input/output operations per second

**Elasticsearch-Specific I/O:**
- Index writes: Continuous during ingestion
- Segment merging: Background I/O, increases disk load
- Garbage collection: I/O may pause during GC
- Caching: OS page cache affects I/O patterns

**Optimization:**
- Use SSD storage (much better than HDD for random I/O)
- Monitor disk usage and clean up old indices
- Tune merge policies to reduce merge I/O
- Consider tiered storage (hot/warm/cold)

### Query Queue Depth

Query queue depth indicates how many queries are waiting for processing.

**Monitoring:**
- Search queue depth: Pending search requests
- Bulk queue depth: Pending indexing operations
- Index queue depth: Background indexing tasks

**Interpretation:**
- Growing queue: Queries arriving faster than processing
- Sustained queue: System overloaded or degraded
- Sudden spike: Possible slow query causing backlog

**Response:**
- Investigate slow queries in queue
- Check JVM memory and GC pauses
- Verify disk I/O is not bottleneck
- Consider query timeout to prevent cascading failures

### Circuit Breakers

Circuit breakers prevent out-of-memory errors and uncontrolled resource consumption.

**Types:**
1. **Field Data Circuit Breaker:** Limits fielddata caching
2. **JVM Heap Circuit Breaker:** Reserves heap space for operations
3. **Request Circuit Breaker:** Limits memory per request
4. **In-flight Request Circuit Breaker:** Limits concurrent requests

**Triggering:**
- Requests rejected with circuit_breaker_exception
- Prevents OOM but degrades user experience
- Indicates insufficient resources

**Tuning:**
- Monitor circuit breaker trip frequency
- Increase limits if trips are legitimate
- Optimize queries if trips are excessive
- Use separate JVM heaps for different thread pools

### Thread Pool Saturation

Thread pools execute queries and indexing operations.

**Thread Pools:**
- **Search:** Parallel query execution
- **Write (Bulk):** Document indexing
- **Index:** Background indexing tasks
- **Merge:** Segment merging

**Saturation Indicators:**
- Queue size growing
- Rejection count increasing
- Request latency increasing with queue depth

**Monitoring:**
- Active threads: Currently executing tasks
- Queue size: Pending tasks
- Rejections: Tasks rejected due to queue overflow
- Completion time: Task execution duration

---

## Dashboards and Alerting

Dashboards provide visibility into search health, while alerting enables proactive response to issues.

### Building Search Quality Dashboards

Effective search dashboards surface the most critical metrics while remaining uncluttered.

**Dashboard Components:**

**1. Operational Health (top-level overview)**
- Cluster health status
- Query error rate (%)
- P95 latency (ms)
- QPS (current and trend)
- Alert count (triggered alerts)

**2. Search Quality**
- Zero-result rate (% and trend)
- Click-through rate by position
- Top 10 queries (by volume)
- Failed queries count
- Search quality score (composite metric)

**3. Performance Metrics**
- Latency percentiles (P50, P95, P99)
- Throughput (QPS, documents/sec)
- Error rates by type (timeout, 5xx, etc.)
- Slow query trending

**4. Infrastructure Health**
- Cluster status (green/yellow/red)
- Shard allocation status
- JVM heap usage %
- Disk usage %
- Query queue depth

**5. Resource Utilization**
- CPU usage per node
- Memory usage
- Network I/O
- Disk I/O latency

### Tools: Grafana and Kibana

**Grafana:**
- Multi-source dashboarding (Prometheus, Elasticsearch, InfluxDB, etc.)
- Rich visualization library
- Advanced alerting capabilities
- Query language flexibility
- Good for infrastructure-wide monitoring

**Kibana:**
- Native Elasticsearch integration
- Full-text search on dashboards
- Canvas for custom visualizations
- Integrated log analysis
- Better for Elasticsearch-specific monitoring

**Comparison:**
- Grafana: Better for multi-source, time-series data
- Kibana: Better for Elasticsearch cluster and application logs
- Many deployments use both: Grafana for infra, Kibana for ES-specific

### Key Charts for Search Monitoring

**1. Time Series Charts:**
- Latency percentiles (P50, P95, P99) over time
- Error rate trends
- Zero-result rate trends
- Throughput (QPS) variation

**2. Heatmaps:**
- Latency distribution (time on X, latency on Y, intensity = frequency)
- Error rate patterns across time/shard/node
- Traffic patterns by hour

**3. Scatter Plots:**
- Latency vs. QPS (identify saturation point)
- Query complexity vs. latency
- Result set size vs. latency

**4. Bar Charts:**
- Top 10 queries by volume
- Error count by type
- Latency by query type
- Performance by node

**5. Gauge Metrics:**
- Current cluster health status
- JVM heap usage %
- Disk usage %
- Active shard count

### Alerting Thresholds

Thresholds determine when alerts trigger, requiring careful calibration.

**Calibration Process:**
1. Establish baseline (normal operating range)
2. Define tolerance (acceptable variance)
3. Set thresholds 1-2 standard deviations above baseline
4. Implement gradually (tune over weeks)
5. Monitor alert fatigue (too many false positives)

**Recommended Thresholds:**

| Metric | Warning | Critical |
|--------|---------|----------|
| P95 Latency | 200ms | 500ms |
| P99 Latency | 500ms | 1000ms |
| Error Rate | 0.1% | 1% |
| Zero-Result Rate | 10% | 20% |
| JVM Heap | 75% | 85% |
| Disk Usage | 80% | 90% |
| Query Queue | 100 | 500 |

### SLO Definition

Service Level Objectives define acceptable performance standards.

**Example SLO:**
"99% of search queries complete within 200ms P95 latency"

**Components:**
1. **Service:** What is being measured (search service)
2. **Metric:** P95 latency
3. **Target:** 99%
4. **Threshold:** 200ms
5. **Measurement window:** Monthly

**Error Budget:**
- With 99% SLO over 1 month: 43,200 seconds error budget
- Can tolerate ~7 minutes of violations
- Remaining budget = (1 - actual uptime) × time period

**Using Error Budget:**
- Deploy risky changes if budget remains
- Freeze deployments if budget exhausted
- Balance speed of innovation with reliability

---

## Search Logging

Comprehensive logging enables debugging, analysis, and audit trail maintenance.

### What to Log

**Query Logging:**
- Query text/ID
- Query timestamp
- Query type (search, autocomplete, filter)
- Query parameters (from, size, filters)
- User ID (hashed for privacy)
- Session ID
- Client information (device, app version)

**Result Logging:**
- Query ID (link to query log)
- Result count (total hits)
- Result IDs/scores (top N results)
- Relevance scores
- Query execution time
- Index/shard touched

**Click Logging:**
- Query ID
- Result ID
- Click position
- Click timestamp
- Click-to-return time (dwell time)
- Session ID

**Error Logging:**
- Error type (timeout, circuit breaker, etc.)
- Error message and stack trace
- Query that caused error
- System state (load, memory, etc.)
- Timestamp

**Performance Logging:**
- Query latency
- Query execution phases
- JVM metrics at query time
- Network latency
- Disk I/O latency

### Structured Logging

Structured logging stores log entries as machine-readable data (JSON) instead of text.

**Benefits:**
- Searchable and queryable
- Easy to aggregate and analyze
- Efficient parsing
- Enables automated alerting

**Format:**
```json
{
  "timestamp": "2025-02-15T10:30:45.123Z",
  "log_level": "INFO",
  "service": "search-api",
  "query_id": "q_abc123",
  "user_id": "u_xyz789",
  "query_text": "machine learning books",
  "query_latency_ms": 145,
  "result_count": 1234,
  "error": null,
  "tags": ["search", "success"]
}
```

**Structured Logging Tools:**
- ELK Stack (Elasticsearch-Logstash-Kibana)
- Datadog
- Splunk
- Google Cloud Logging
- AWS CloudWatch Logs

### Privacy-Safe Logging

Search queries may contain sensitive information requiring protection.

**Privacy Techniques:**

1. **Query Hashing:**
   - Hash query text to enable duplicate detection without storing text
   - Use salted hash for reproducibility

2. **PII Removal:**
   - Redact personal information (emails, SSNs, credit cards)
   - Use regex or NLP to identify patterns
   - Replace with placeholders: "[EMAIL]", "[PHONE]"

3. **Selective Logging:**
   - Only log aggregated statistics
   - Sample logs (1 in 1000) for detailed analysis
   - Log only non-sensitive metadata

4. **Data Retention:**
   - Set retention policies (e.g., 30 days)
   - Comply with GDPR, CCPA regulations
   - Enable user opt-out mechanisms

5. **Access Control:**
   - Restrict log access to authorized personnel
   - Audit log access
   - Encrypt logs in transit and at rest

### Log Aggregation: ELK and Datadog

**ELK Stack:**
- Elasticsearch: Storage and search
- Logstash: Parse, transform, aggregate logs
- Kibana: Visualization and exploration

**Advantages:**
- Open-source (self-hosted)
- Cost-effective at scale
- Full control over data
- Elasticsearch integration

**Disadvantages:**
- Operational overhead
- Requires infrastructure
- Manual scaling and tuning

**Datadog:**
- SaaS log aggregation
- Built-in integrations
- AI-powered anomaly detection
- Agent-based collection

**Advantages:**
- No operational overhead
- Advanced analytics
- Cloud-native
- 360-degree observability

**Disadvantages:**
- SaaS costs
- Data retention limits
- Vendor lock-in

---

## Debugging Search Issues

When search quality degrades, systematic debugging identifies root causes.

### Elasticsearch Explain API

The Explain API shows how a specific document matches a query.

**Usage:**
```
GET /my_index/_explain/doc_id
{
  "query": {
    "match": {
      "title": "machine learning"
    }
  }
}
```

**Output Includes:**
- `matched`: Whether document matches query
- `explanation`: Scoring breakdown
  - Query clause contribution
  - Field boost factors
  - TF-IDF components
  - Match weight

**Interpretation:**
- Identifies which query clauses matched
- Shows relative contribution of each field
- Reveals boost effects (positive or negative)
- Compares actual vs. expected scoring

**Example Analysis:**
If expected result ranks lower than actual:
1. Use Explain API on both documents
2. Compare score components
3. Check field boosts
4. Identify scoring differences
5. Adjust weights/boosts if needed

### Query Profiling

Query profiling breaks down query execution into phases.

**Enabling Profiling:**
```
GET /my_index/_search
{
  "profile": true,
  "query": { ... }
}
```

**Output Phases:**
1. **Query Phase:** Distributed scoring of matching documents
2. **Fetch Phase:** Retrieving actual document contents
3. **Expand Phase:** Expanding collapsed results
4. **Collapse Phase:** Grouping/collapsing results

**Metrics per Phase:**
- Time (milliseconds)
- Breakdown by component
- Score calculation details

**Optimization Insights:**
- If query phase slow: Optimize scoring, add filters
- If fetch phase slow: Check document size, add source filtering
- If collapse slow: Reduce collapse field cardinality

### Slow Query Logs

Slow query logs capture queries exceeding latency thresholds.

**Configuration:**
```
PUT /_settings
{
  "index.search.slowlog.threshold.query.warn": "1s",
  "index.search.slowlog.threshold.query.info": "500ms",
  "index.search.slowlog.threshold.query.debug": "100ms"
}
```

**Log Contents:**
- Query text
- Execution time
- Took milliseconds
- Shard information
- Source IP

**Analysis Process:**
1. Identify slow query patterns
2. Check frequency (one-off vs. chronic)
3. Compare execution time breakdown
4. Review query parameters
5. Check index statistics

### Score Explanation

Understanding why a document received a particular score enables optimization.

**Scoring Components:**

**Term Frequency (TF):**
- How often term appears in document
- More occurrences = higher relevance

**Inverse Document Frequency (IDF):**
- How rare the term is across all documents
- Rarer terms = higher relevance
- Common terms (the, and, etc.) have low IDF

**Field Boosts:**
- Title match: +10x boost
- Category match: +5x boost
- Body match: 1x baseline

**Query Boosts:**
- Explicit boost parameters
- Function scores
- Decay functions

**Example Score Breakdown:**
Query: "machine learning book"
Document: "Introduction to Machine Learning"

```
Score = 15.23
├── "machine" (TF=1, IDF=8.5, boost=1) = 8.5
├── "learning" (TF=1, IDF=6.8, boost=1) = 6.8
├── "book" (TF=0, IDF=5.2, boost=1) = 0
└── Coordination bonus = 0.03
```

### "Why Does This Rank Here?" Debugging

When a result has unexpected rank, systematic investigation identifies issues.

**Investigation Steps:**

1. **Verify Relevance:**
   - Is the document actually relevant to the query?
   - Would you expect it to rank here?
   - Is query intent matched?

2. **Check Scoring:**
   - Use Explain API to compare with nearby results
   - Check field matches and boosts
   - Verify filter impact

3. **Examine Index:**
   - Verify document is indexed correctly
   - Check field values and analysis
   - Confirm no unexpected boosts

4. **Review Query:**
   - Check query parameters (from, size)
   - Verify filters applied
   - Check boost functions

5. **Compare Ranking:**
   - Explain API for top 5 results
   - Compare scores and contributions
   - Identify scoring anomalies

6. **Root Cause Analysis:**
   - Algorithm issue: Fix ranking model
   - Data issue: Fix indexed content
   - Query issue: Improve query processing
   - Configuration: Adjust boosts/weights

---

## Search Quality Programs

Building sustainable search quality requires systematic processes and team structures.

### Building a Search Quality Team

**Team Composition:**

1. **Search Relevance Engineer:**
   - Owns search ranking algorithm
   - A/B tests ranking changes
   - Implements improvements
   - Technical: Python, ML, data analysis

2. **Search Analytics Engineer:**
   - Builds dashboards and monitoring
   - Analyzes query/click logs
   - Identifies quality issues
   - Technical: SQL, data visualization, statistics

3. **Search Quality Analyst:**
   - Creates judgment lists
   - Evaluates search quality
   - Documents best practices
   - Non-technical: Domain expertise, communication

4. **Search Product Manager:**
   - Sets search goals and strategy
   - Prioritizes improvements
   - Communicates with stakeholders
   - Leadership: Vision, roadmap, strategy

### Judgment Collection

Judgment lists enable offline evaluation and algorithm optimization.

**Judgment Workflow:**

1. **Query Selection:**
   - Sample queries proportionally to search volume
   - Include top queries, long-tail, trending, failed
   - Represent diverse intents and query types

2. **Result Evaluation:**
   - Present judges with query and results
   - Provide clear evaluation guidelines
   - Collect ratings (binary or graded)

3. **Inter-rater Agreement:**
   - Multiple judges per query (e.g., 3)
   - Calculate agreement (Cohen's kappa)
   - Resolve disagreements through discussion
   - Refine guidelines if agreement low

4. **Scale:**
   - Start small: 100-200 queries
   - Grow systematically: 1000+ queries
   - Maintain continuously: Add new queries quarterly

**Judgment Guidelines:**
- Define relevance clearly (match, helpful, actionable)
- Provide examples (relevant, not relevant, borderline)
- Specify evaluation criteria per query type
- Document rationale for edge cases

**Tools:**
- Quepid: Open-source judgment collection
- Rated: Commercial judgment service
- Custom systems: Build internal interfaces

### Search Quality Meetings

Regular meetings sustain focus on quality improvement.

**Weekly Metrics Review:**
- Review key metrics (ZRR, CTR, NDCG)
- Identify trends and anomalies
- Discuss failures and impact
- Duration: 30 minutes

**Bi-weekly Ranking Review:**
- Evaluate current A/B tests
- Plan new ranking experiments
- Review slow queries
- Discuss optimization opportunities
- Duration: 1 hour

**Monthly Quality Review:**
- Comprehensive metric review
- Judgment list evaluation
- Customer feedback analysis
- OKR progress
- Strategic planning
- Duration: 2 hours

**Quarterly Planning:**
- Set quality goals
- Prioritize projects
- Plan judgment collection
- Resource allocation
- Duration: 1-2 hours

### Continuous Improvement Loops

Search quality improves through systematic iteration.

**The OODA Loop (Observe, Orient, Decide, Act):**

1. **Observe:** Collect metrics and data
   - Query analytics
   - Click analytics
   - Quality metrics
   - User feedback

2. **Orient:** Analyze and understand
   - Root cause analysis
   - Hypothesis formation
   - Opportunity identification
   - Prioritization

3. **Decide:** Plan improvements
   - Hypothesis testing plan
   - Resource allocation
   - Timeline
   - Success metrics

4. **Act:** Implement improvements
   - Develop ranking changes
   - Test offline (judgment evaluation)
   - Test online (A/B test)
   - Deploy if successful

5. **Iterate:** Repeat cycle
   - Continuous improvement
   - Faster cycles as processes mature
   - Building institutional knowledge

**Velocity Factors:**
- **Cycle time:** How long experiments take (1-4 weeks typical)
- **Throughput:** Number of experiments in flight
- **Learning rate:** How quickly team improves from failures

---

## Tools and Platforms

Purpose-built tools accelerate search quality work.

### Quepid

Quepid is an open-source relevance testing platform for search quality evaluation.

**Capabilities:**
- Query and judgment management
- NDCG, MAP, MRR calculation
- Snapshot comparison (before/after)
- Multi-search engine support
- API-driven testing

**Integration:**
- Elasticsearch
- OpenSearch
- Solr
- Algolia
- Vectara
- Custom APIs

**Workflow:**
1. Create test case (queries + judgments)
2. Execute query against search engine
3. View results and scores
4. Make ranking changes
5. Compare metrics improvements

**Advantages:**
- Open-source and free
- Lightweight and easy to deploy
- Strong community support
- Fast iteration cycles

### Splainer

Splainer provides visualization and debugging of Elasticsearch/Solr queries.

**Features:**
- Visual query builder
- Score explanation display
- Result preview
- Query performance metrics
- Integration with Quepid

**Use Cases:**
- Understanding why results rank as they do
- Debugging failing queries
- Exploring field analysis
- Score comparison across queries

**Workflow:**
1. Enter query text
2. View matching documents
3. See score breakdown per document
4. Understand field contributions
5. Iterate on query/boosts

### Rated

Rated is a commercial search evaluation platform providing crowdsourced judgments.

**Services:**
- Judgment collection at scale
- Search quality audits
- Ranking evaluation
- Report generation

**Advantages:**
- Professional evaluators
- Managed quality control
- Reduces internal labor
- Industry benchmarks

**Use Cases:**
- Building large judgment sets (1000+ queries)
- Periodic audits
- Competitive benchmarking
- Domain-specific evaluation

### Algolia Analytics

Algolia provides built-in search analytics for Algolia-hosted search.

**Metrics:**
- Top searches
- Zero-result queries
- Popular filters
- Click-through by position
- Search success rate

**Features:**
- Dashboard visualization
- Query recommendations
- Trending analysis
- A/B testing

### SearchPilot

SearchPilot is a search A/B testing platform for ecommerce sites.

**Capabilities:**
- Experiment management
- Revenue impact calculation
- Statistical significance testing
- Multivariate testing
- Result analysis

**Integration:**
- Shopify
- BigCommerce
- Custom platforms

---

## Conclusion

Search observability requires coordinated efforts across metrics, logging, dashboards, and team processes. The most effective organizations combine:

1. **Comprehensive Metrics:** Understanding all dimensions of search quality
2. **Operational Visibility:** Real-time dashboards and alerting
3. **Offline Evaluation:** Judgment-based testing before production
4. **Online Validation:** A/B testing with real users
5. **Systematic Processes:** Regular reviews and continuous improvement
6. **Effective Tools:** Purpose-built platforms for relevance testing and analysis
7. **Skilled Teams:** Dedicated focus on search quality

By implementing these practices, organizations build search systems that reliably deliver relevant results and continuously improve user satisfaction.

---

## Sources

- [Performance Metrics - Sentry](https://docs.sentry.io/product/insights/overview/metrics/)
- [P50 vs P95 vs P99 Latency Explained - OneUptime](https://oneuptime.com/blog/post/2025-09-15-p50-vs-p95-vs-p99-latency-percentiles/view)
- [Mastering Latency Metrics - Medium](https://medium.com/javarevisited/mastering-latency-metrics-p90-p95-p99-d5427faea879)
- [What Is P99 Latency - Aerospike](https://aerospike.com/blog/what-is-p99-latency/)
- [Gaining insights with search analytics - Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/search-analytics.html)
- [How to Identify & Fix Zero-Result Searches - Wizzy](https://wizzy.ai/blog/zero-result-searches-solution/)
- [The Generalized Cascade Click Model - ResearchGate](https://www.researchgate.net/publication/356455648_The_Generalized_Cascade_Click_Model_A_Unified_Framework_for_Estimating_Click_Models)
- [Click Models for Web Search - Academic Paper](https://clickmodels.weebly.com/uploads/5/2/2/5/52257029/mc2015-clickmodels.pdf)
- [Modeling dwell time to predict click-level satisfaction - ACM](https://dl.acm.org/doi/10.1145/2556195.2556220)
- [Evaluation Metrics for Search and Recommendation Systems - Weaviate](https://weaviate.io/blog/retrieval-evaluation-metrics)
- [Evaluating recommendation systems - Shaped](https://www.shaped.ai/blog/evaluating-recommendation-systems-map-mmr-ndcg)
- [Normalized Discounted Cumulative Gain explained - Evidently AI](https://www.evidentlyai.com/ranking-metrics/ndcg-metric)
- [Demystifying NDCG - Medium](https://medium.com/data-science/demystifying-ndcg-bee3be58cfe0)
- [Offline Evaluation Metrics in Information Retrieval - GeeksforGeeks](https://www.geeksforgeeks.org/machine-learning/offline-evaluation-metrics-in-information-retrieval/)
- [How to Monitor Elasticsearch Cluster Health - OneUptime](https://oneuptime.com/blog/post/2026-01-27-elasticsearch-cluster-health/view)
- [Essential Health Checks to Keep Elasticsearch Healthy - DZone](https://dzone.com/articles/keep-your-search-cluster-fit-essential-health-chec)
- [Top 10 Elasticsearch Metrics to Monitor Performance - Sematext](https://sematext.com/blog/top-10-elasticsearch-metrics-to-watch/)
- [Create SLOs - Grafana Cloud Documentation](https://grafana.com/docs/grafana-cloud/alerting-and-irm/slo/create/)
- [Kibana vs Grafana - Middleware](https://middleware.io/blog/kibana-vs-grafana/)
- [Log Aggregation: ELK Stack, Loki, and Structured Logging - Calmops](https://calmops.com/devops/log-aggregation-elk-loki/)
- [Datadog vs Logstash - StackShare](https://stackshare.io/stackups/datadog-vs-logstash)
- [Improve Elasticsearch Query Performance with Profiling - Coralogix](https://coralogix.com/blog/improve-elasticsearch-query-performance-with-profiling-and-slow-logs/)
- [Slow query and index logging - Elastic Docs](https://www.elastic.co/docs/deploy-manage/monitor/logging-configuration/slow-logs)
- [Advanced tuning: finding and fixing slow Elasticsearch queries - Elastic Blog](https://www.elastic.co/blog/advanced-tuning-finding-and-fixing-slow-elasticsearch-queries)
- [Search quality evaluation with judgement lists - Elasticsearch Labs](https://www.elastic.co/search-labs/blog/judgment-lists)
- [Measuring and improving search quality metrics - OpenSearch](https://opensearch.org/blog/measuring-and-improving-search-quality-metrics/)
- [Quepid - Relevancy Tuning Platform](https://www.quepidapp.com/)
- [GitHub - Quepid](https://github.com/o19s/quepid)
- [GitHub - Splainer Search](https://github.com/o19s/splainer-search)
