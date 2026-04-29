# Knowledge Graph Builder

**Purpose**: Map relationships between knowledge entries and visualize the knowledge base structure.
**Usage**: Implement in Phase 3.5 of the Deep Research Synthesizer pipeline.
**Output**: Queryable graph structure, D3.js visualizations, and graph metrics.
**Last Updated**: 2026-02-09

---

## Table of Contents

1. Relationship Types
2. Relationship Detection Algorithm
3. Graph Data Structure
4. D3.js Force-Directed Graph Specifications
5. Cluster Detection
6. Graph Metrics
7. Graph Export & Visualization
8. Query Patterns

---

## Relationship Types

Knowledge entries connect through six types of relationships. Each type serves different discovery patterns.

### Semantic (Same Concept, Different Angle)

**Definition**: Two entries discuss the same underlying concept from different perspectives.

**Examples**:
- "Water Usage in Cotton Production" (environmental impact) ↔ "Water Recycling in Factories" (solutions)
- "AI Diagnostic Accuracy" (clinical performance) ↔ "AI Bias in Diagnosis" (equity concerns)
- "Blockchain for Transparency" (technology) ↔ "Certification Standards" (governance)

**Detection signals**:
- Title or content overlap (shared keywords like "sustainable", "AI", "water")
- Entries that would benefit readers equally
- Different stakeholder perspectives (company vs. worker vs. environment)

**Strength**: 0.7-0.9 (moderate to strong; not hierarchical)

**UI Behavior**: Hover one entry, highlight related entries. Reader can explore different angles.

---

### Hierarchical (Parent-Child / Taxonomy)

**Definition**: One entry is a generalization or specialization of another.

**Examples**:
- "Machine Learning" → "Neural Networks" → "Transformers"
- "Sustainable Fashion" → "Supply Chain" → "Ethical Labor"
- "Renewable Energy" → "Solar Power" → "Photovoltaic Efficiency"

**Detection signals**:
- Explicit taxonomy (category/subcategory relationship)
- Entry titles form X → subset of X pattern
- One entry is prerequisite knowledge for another
- Table of contents structure

**Strength**: 0.8-1.0 (strong; hierarchical links are explicit)

**UI Behavior**: Show as collapsible tree. Can expand "Renewable Energy" to show children, collapse to show parent only.

---

### Causal (Causes / Enables / Blocks)

**Definition**: One condition causes, enables, or blocks another.

**Examples**:
- "Water Scarcity" → CAUSES → "Higher Textile Production Costs"
- "Blockchain Technology" → ENABLES → "Supply Chain Transparency"
- "Regulatory Requirements" → BLOCKS → "Cheap Fast Fashion Production"
- "Consumer Demand for Sustainability" → DRIVES → "Corporate Sustainability Investments"

**Detection signals**:
- Language: "leads to", "causes", "enables", "prevents", "drives", "because"
- Logical dependencies (can't understand effect without cause)
- Mechanism or chain-of-causation description

**Strength**: 0.6-0.9 (depends on directness of causal link)

**UI Behavior**: Show with arrows pointing direction. "Click for mechanism" to see explanation.

---

### Temporal (Before / After)

**Definition**: One event or development precedes another.

**Examples**:
- "Industrial Revolution" → PRECEDES → "Mass Production Era"
- "COVID-19 Pandemic (2020)" → PRECEDES → "Supply Chain Disruptions (2021-2023)"
- "First Sustainable Fashion Certification (2001)" → LEADS TO → "Mainstream Adoption (2020s)"

**Detection signals**:
- Chronological ordering (2020 event before 2025 event)
- Language: "before", "after", "then", "following", "during", "meanwhile"
- Historical progression patterns
- Phase or era description

**Strength**: 0.7-1.0 (historical links are usually clear)

**UI Behavior**: Show as timeline or chronological sequence. Can filter by time period.

---

### Comparative (Alternative / Competing)

**Definition**: Two approaches or solutions are alternatives or in competition.

**Examples**:
- "Organic Cotton" vs. "Synthetic Fibers"
- "Blockchain Tracking" vs. "Traditional Certification"
- "Worker-Owned Fashion Brands" vs. "Corporate Sustainability Programs"
- "Carbon Tax Policy" vs. "Voluntary Carbon Markets"

**Detection signals**:
- Language: "versus", "compared to", "alternative", "instead of", "unlike"
- Similar scope/purpose but different approach
- Entries that answer "which is better?" question
- Pros/cons comparison structure

**Strength**: 0.6-0.8 (comparison strength depends on how directly opposed)

**UI Behavior**: Show as side-by-side comparison. Toggle between entries to see relative strengths.

---

### Dependency (Requires Understanding Of)

**Definition**: One concept requires understanding another concept first.

**Examples**:
- "Circular Economy" REQUIRES → "Material Science Basics"
- "Supply Chain Optimization" REQUIRES → "Network Theory"
- "AI Healthcare" REQUIRES → "Understanding of Regulatory Landscape"
- "Quantum Computing Applications" REQUIRES → "Quantum Physics Fundamentals"

**Detection signals**:
- Pedagogical order (teach A before B)
- Language: "requires understanding", "depends on", "prerequisite", "builds on"
- Technical complexity escalation
- "To understand X, first learn Y" structure

**Strength**: 0.7-0.9 (prerequisites are fairly absolute)

**UI Behavior**: Show as suggested reading order. "This entry builds on: [prerequisite]"

---

## Relationship Detection Algorithm

Relationships can be detected through four methods, listed from most reliable to least:

### Method 1: Explicit (User-Provided)

**Most reliable**: Relationships manually tagged by researchers during Phase 3.

**Entry format**:
```json
{
  "id": "entry-42",
  "title": "Water Usage in Cotton",
  "related": [
    {"target_id": "entry-51", "type": "semantic", "strength": 0.85},
    {"target_id": "entry-63", "type": "causal", "strength": 0.7},
    {"target_id": "entry-28", "type": "hierarchical", "strength": 0.9}
  ]
}
```

**Advantages**: Accurate, researcher-curated, includes strength scores
**Disadvantages**: Requires manual work
**Effort**: 2-3 minutes per entry during Phase 3 data extraction

---

### Method 2: Tag Overlap (Automated)

**Moderately reliable**: Entries sharing multiple tags are likely related.

**Algorithm**:
```
For each entry A:
  For each entry B (where B ≠ A):
    shared_tags = intersection(A.tags, B.tags)
    if len(shared_tags) >= 2:
      strength = len(shared_tags) / max(len(A.tags), len(B.tags))
      type = "semantic"  # tag overlap suggests semantic relation
      create_edge(A, B, type, strength)
```

**Example**:
- Entry A tags: ["water", "textile", "sustainability", "environment"]
- Entry B tags: ["water", "pollution", "recycling", "manufacturing"]
- Shared: ["water"] = 1 tag
- Result: No edge (threshold is 2+)

```
- Entry C tags: ["water", "textile", "dyeing", "pollution"]
- Entry D tags: ["water", "textile", "waste", "sustainability"]
- Shared: ["water", "textile"] = 2 tags
- Result: Edge created, strength = 2/4 = 0.5
```

**Advantages**: Fully automated, fast
**Disadvantages**: Misses relationships without tag overlap, creates false positives
**Filtering**: Apply minimum strength threshold (0.4+) to reduce noise

---

### Method 3: Category Siblings (Taxonomy-Based)

**Moderately reliable**: Entries in same category/subcategory are likely related.

**Algorithm**:
```
For each entry A:
  category = A.category + ":" + A.subcategory
  For each entry B (same category):
    if A.id ≠ B.id:
      # Siblings in same taxonomy
      strength = 0.5  # base strength for same category
      # Boost if tags also overlap
      if tag_overlap(A, B) >= 1:
        strength += 0.2
      type = "semantic"
      create_edge(A, B, type, strength)
```

**Example**:
```
Category: "Sustainable Fashion / Environmental Impact"
├─ Entry X: "Water Usage in Cotton"
├─ Entry Y: "Dyeing Wastewater Pollution"
└─ Entry Z: "Textile Waste in Landfills"

Relationships:
X ↔ Y: strength 0.7 (same category, shared tag "water")
X ↔ Z: strength 0.5 (same category, no tag overlap)
Y ↔ Z: strength 0.5 (same category, no tag overlap)
```

**Advantages**: Leverages existing taxonomy, reduces false positives from tag-only method
**Disadvantages**: Requires clean taxonomy structure
**Best for**: Knowledge bases with clear hierarchical organization

---

### Method 4: Content Similarity (TF-IDF)

**Least reliable but catches distant relationships**: Entries with similar content are related.

**Algorithm**:
```
1. Vectorize entry content using TF-IDF
   - Tokenize titles + summaries
   - Remove stopwords
   - Compute term frequencies
2. For each pair (A, B):
   - Compute cosine similarity between vectors
   - If similarity > 0.3:
     strength = similarity  # 0.3-1.0
     type = "semantic"
     create_edge(A, B, type, strength)
```

**Example**:
```
Entry A: "Cotton Production and Water"
Entry B: "Sustainable Textiles Overview"

TF-IDF vectors:
A: {cotton: 0.4, water: 0.3, production: 0.2, textile: 0.1}
B: {textile: 0.3, sustainable: 0.2, cotton: 0.2, production: 0.15}

Cosine similarity: 0.45 (above 0.3 threshold)
Result: Edge created, type = "semantic", strength = 0.45
```

**Advantages**: Catches distant relationships, fully automated
**Disadvantages**: Computationally expensive, prone to false positives
**Optimization**: Only run if other methods insufficient; apply strict threshold (>0.4)

---

### Method 5 (Optional): Citation Chains

**Highest fidelity but rare**: Entry A references Entry B's source.

**Algorithm**:
```
For each entry A with sources list S_A:
  For each entry B with sources list S_B:
    For each source s_A in S_A:
      For each source s_B in S_B:
        if s_A.url == s_B.url:  # same source cited
          type = determine_type(A, B, shared_source)
          strength = 0.8
          create_edge(A, B, type, strength)
```

**Example**:
```
Entry A "Cotton Water Usage"
- Sources: [WWF report URL, UN report URL]

Entry B "Environmental Impact of Textiles"
- Sources: [WWF report URL, McKinsey report URL]

Shared source: WWF report
Result: Edge created, type = likely "hierarchical" or "semantic"
```

**Advantages**: Very accurate (entries discussing same sources are likely connected)
**Disadvantages**: Only works if sources are fully documented; rare
**Use**: Boost strength of edges found by other methods

---

## Graph Data Structure

### JSON Schema

```json
{
  "metadata": {
    "created": "2026-02-09",
    "topic": "Sustainable Fashion Supply Chains",
    "entry_count": 47,
    "relationship_count": 128,
    "graph_density": 0.34,
    "clustering_coefficient": 0.52
  },

  "nodes": [
    {
      "id": "entry-1",
      "title": "Cotton Water Consumption",
      "category": "Environmental Impact",
      "subcategory": "Water",
      "summary": "Cotton production consumes 2,700 liters per shirt...",
      "authority_tier": "Tier 1",
      "confidence": "HIGH",
      "tags": ["water", "cotton", "agriculture", "sustainability"],
      "word_count": 850,
      "source_url": "https://waterfootprint.org/...",
      "created_date": "2026-02-01",
      "last_verified": "2026-02-09",
      "connections": 7,
      "in_degree": 4,
      "out_degree": 3
    },
    {
      "id": "entry-2",
      "title": "Dyeing Wastewater Pollution",
      "category": "Environmental Impact",
      "subcategory": "Water",
      "summary": "Textile dyeing produces 10-20% of industrial water pollution...",
      "authority_tier": "Tier 1",
      "confidence": "HIGH",
      "tags": ["water", "pollution", "dyeing", "manufacturing"],
      "word_count": 920,
      "source_url": "https://unep.org/...",
      "created_date": "2026-02-02",
      "last_verified": "2026-02-09",
      "connections": 6,
      "in_degree": 3,
      "out_degree": 3
    }
  ],

  "edges": [
    {
      "id": "edge-1",
      "source": "entry-1",
      "target": "entry-2",
      "type": "semantic",
      "strength": 0.85,
      "direction": "undirected",
      "explanation": "Both discuss water impact in textile production"
    },
    {
      "id": "edge-2",
      "source": "entry-1",
      "target": "entry-5",
      "type": "hierarchical",
      "strength": 0.9,
      "direction": "directed",
      "explanation": "Cotton is a specific case of textile water usage"
    },
    {
      "id": "edge-3",
      "source": "entry-3",
      "target": "entry-1",
      "type": "causal",
      "strength": 0.7,
      "direction": "directed",
      "explanation": "Water scarcity increases cotton production costs"
    }
  ],

  "clusters": [
    {
      "id": "cluster-1",
      "name": "Environmental Impact",
      "color": "#E74C3C",
      "nodes": ["entry-1", "entry-2", "entry-4", "entry-7"],
      "internal_edges": 8,
      "external_edges": 3,
      "density": 0.71,
      "centroid": "entry-1"
    },
    {
      "id": "cluster-2",
      "name": "Supply Chain Governance",
      "color": "#3498DB",
      "nodes": ["entry-10", "entry-12", "entry-15"],
      "internal_edges": 2,
      "external_edges": 5,
      "density": 0.33,
      "centroid": "entry-12"
    }
  ]
}
```

### Node Properties

| Property | Type | Example | Purpose |
|----------|------|---------|---------|
| id | string | "entry-42" | Unique identifier |
| title | string | "Cotton Water Usage" | Display in graph |
| category | string | "Environmental Impact" | Color/cluster assignment |
| subcategory | string | "Water" | Sub-group organization |
| summary | string | "Cotton produces..." | Tooltip content |
| authority_tier | enum | "Tier 1" | Node styling (Tier 1 = larger/prominent) |
| confidence | enum | "HIGH"/"MEDIUM"/"LOW" | Visual indicator (color shade) |
| tags | array | ["water", "cotton"] | For search/filter |
| word_count | number | 850 | Node size factor |
| connections | number | 7 | Degree (used for node radius) |
| in_degree | number | 4 | Directed: incoming edges |
| out_degree | number | 3 | Directed: outgoing edges |

### Edge Properties

| Property | Type | Example | Purpose |
|----------|------|---------|---------|
| id | string | "edge-127" | Unique identifier |
| source | string | "entry-1" | From node |
| target | string | "entry-2" | To node |
| type | enum | "semantic" | Color/style encoding |
| strength | number | 0.85 | Thickness/opacity |
| direction | enum | "directed"/"undirected" | Arrow styling |
| explanation | string | "Both discuss water" | Tooltip text |

---

## D3.js Force-Directed Graph Specifications

### HTML/SVG Container

```html
<div id="knowledge-graph-container"></div>

<style>
  #knowledge-graph-container {
    width: 100%;
    height: 100vh;
    border: 1px solid #ddd;
    background: #f9f9f9;
  }

  .node {
    stroke: #fff;
    stroke-width: 2px;
    cursor: pointer;
  }

  .node:hover {
    stroke: #333;
    stroke-width: 3px;
  }

  .link {
    stroke: #999;
    stroke-opacity: 0.6;
  }

  .link.semantic { stroke: #3498DB; }
  .link.hierarchical { stroke: #2ECC71; }
  .link.causal { stroke: #F39C12; }
  .link.temporal { stroke: #9B59B6; }
  .link.comparative { stroke: #E67E22; }
  .link.dependency { stroke: #C0392B; }

  .node-label {
    font-size: 12px;
    pointer-events: none;
    user-select: none;
  }

  .tooltip {
    position: absolute;
    background: white;
    border: 1px solid #999;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 12px;
    max-width: 300px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    z-index: 1000;
  }
</style>
```

### D3.js Force Simulation

```javascript
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

// Load graph data
const graphData = await fetch("/knowledge-graph.json").then(r => r.json());

// Container setup
const container = document.getElementById("knowledge-graph-container");
const width = container.clientWidth;
const height = container.clientHeight;

// SVG setup
const svg = d3.select(container)
  .append("svg")
  .attr("width", width)
  .attr("height", height);

// Force simulation
const simulation = d3.forceSimulation(graphData.nodes)
  .force("link", d3.forceLink(graphData.edges)
    .id(d => d.id)
    .distance(d => 100)  // link distance
    .strength(d => d.strength * 0.5)  // stronger links pull harder
  )
  .force("charge", d3.forceManyBody()
    .strength(-300)  // repulsion strength
    .distanceMin(50)
    .distanceMax(500)
  )
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide()
    .radius(d => Math.log(d.connections + 1) * 10 + 5)
    .iterations(2)
  );

// Link rendering
const link = svg.selectAll(".link")
  .data(graphData.edges)
  .enter()
  .append("line")
  .attr("class", d => `link ${d.type}`)
  .attr("stroke-width", d => d.strength * 3)
  .attr("marker-end", d => d.direction === "directed" ? "url(#arrowhead)" : "");

// Arrow marker for directed edges
svg.append("defs").append("marker")
  .attr("id", "arrowhead")
  .attr("markerWidth", 10)
  .attr("markerHeight", 10)
  .attr("refX", 9)
  .attr("refY", 3)
  .attr("orient", "auto")
  .append("polygon")
  .attr("points", "0 0, 10 3, 0 6")
  .attr("fill", "#999");

// Node rendering
const node = svg.selectAll(".node")
  .data(graphData.nodes)
  .enter()
  .append("circle")
  .attr("class", "node")
  .attr("r", d => Math.log(d.connections + 1) * 10)
  .attr("fill", d => {
    // Color by category
    const categoryColors = {
      "Environmental Impact": "#E74C3C",
      "Supply Chain": "#3498DB",
      "Economics": "#2ECC71",
      "Governance": "#F39C12",
      "Equity": "#9B59B6"
    };
    return categoryColors[d.category] || "#95A5A6";
  })
  .style("opacity", d => {
    // Opacity by confidence
    if (d.confidence === "HIGH") return 1.0;
    if (d.confidence === "MEDIUM") return 0.8;
    if (d.confidence === "LOW") return 0.6;
    return 0.4;
  })
  .call(d3.drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded)
  );

// Node labels (shown on hover)
node.append("title")
  .text(d => d.title);

// Tooltip
const tooltip = d3.select("body")
  .append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);

node.on("mouseover", function(event, d) {
  // Highlight connected nodes
  link.style("stroke-opacity", l =>
    l.source === d || l.target === d ? 0.9 : 0.1
  );
  node.style("opacity", n =>
    n === d || graphData.edges.some(e =>
      (e.source === d && e.target === n) ||
      (e.source === n && e.target === d)
    ) ? 1.0 : 0.1
  );

  // Show tooltip
  tooltip.transition().duration(200).style("opacity", 0.9);
  tooltip.html(`
    <strong>${d.title}</strong><br/>
    Category: ${d.category}<br/>
    Confidence: ${d.confidence}<br/>
    Authority: ${d.authority_tier}<br/>
    Connections: ${d.connections}
  `)
    .style("left", (event.pageX + 10) + "px")
    .style("top", (event.pageY - 28) + "px");
})
.on("mouseout", function() {
  link.style("stroke-opacity", 0.6);
  node.style("opacity", d =>
    d.confidence === "HIGH" ? 1.0 :
    d.confidence === "MEDIUM" ? 0.8 : 0.6
  );
  tooltip.transition().duration(200).style("opacity", 0);
});

// Update positions on simulation tick
simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
});

// Drag handlers
function dragStarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragEnded(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

// Zoom and pan
const zoom = d3.zoom()
  .scaleExtent([0.1, 4])
  .on("zoom", (event) => {
    svg.selectAll("g, line, circle").attr("transform", event.transform);
  });

svg.call(zoom);
```

### Force Configuration Guide

| Force | Parameter | Value | Purpose |
|-------|-----------|-------|---------|
| Link | distance | 100 | Preferred edge length (pixels) |
| Link | strength | 0.5 × edge.strength | How hard edges pull |
| ManyBody | strength | -300 | Repulsion (negative) |
| ManyBody | distanceMin | 50 | Repulsion applies above this |
| Collision | radius | log(deg + 1) × 10 + 5 | Prevent node overlap |
| Center | - | (width/2, height/2) | Gravity toward center |

**Tuning**: If graph is too scattered, increase link.strength or decrease charge. If too clustered, increase charge (more negative).

### Zoom & Pan

```javascript
// Zoom extent
const zoom = d3.zoom()
  .scaleExtent([0.1, 4])  // 10% to 400% zoom
  .on("zoom", (event) => {
    svg.attr("transform", event.transform);
  });

svg.call(zoom);

// Reset zoom button
d3.select("#reset-zoom").on("click", () => {
  svg.transition()
    .duration(750)
    .call(zoom.transform, d3.zoomIdentity.translate(width/2, height/2));
});
```

---

## Cluster Detection

### Modularity-Based Community Detection

**Goal**: Find natural groupings of related entries (clusters).

**Algorithm** (Louvain method, simplified):

```javascript
// Initialize: each node is own cluster
let clusters = {};
graphData.nodes.forEach(n => { clusters[n.id] = n.id; });

let improved = true;
while (improved) {
  improved = false;

  // For each node
  for (let node of graphData.nodes) {
    let bestCluster = clusters[node.id];
    let bestModularity = calculateModularity(clusters);

    // Try moving to each neighbor's cluster
    for (let neighbor of node.neighbors) {
      let newClusters = {...clusters};
      newClusters[node.id] = clusters[neighbor.id];
      let newModularity = calculateModularity(newClusters);

      if (newModularity > bestModularity) {
        bestCluster = clusters[neighbor.id];
        bestModularity = newModularity;
        improved = true;
      }
    }

    clusters[node.id] = bestCluster;
  }
}
```

**Practical Implementation** (JavaScript library):
```javascript
// Using sigma.js or similar
import { louvain } from "graph-clustering";

const clusters = louvain(graphData);
// Returns: {clusterA: [node1, node3, node5], clusterB: [node2, node4]}

// Assign colors to clusters
const clusterColors = {};
let colorIndex = 0;
const colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"];

for (let clusterName in clusters) {
  clusterColors[clusterName] = colors[colorIndex % colors.length];
  colorIndex++;
}

// Apply to nodes
graphData.nodes.forEach(node => {
  node.cluster = findClusterForNode(node.id, clusters);
  node.clusterColor = clusterColors[node.cluster];
});
```

### Cluster Visualization

**Convex Hulls** (show cluster boundaries):
```javascript
// For each cluster, compute convex hull of member nodes
const convexHulls = svg.selectAll(".cluster-hull")
  .data(clustersArray)
  .enter()
  .append("path")
  .attr("class", "cluster-hull")
  .attr("d", d => {
    const points = d.nodes.map(id => {
      const node = graphData.nodes.find(n => n.id === id);
      return [node.x, node.y];
    });
    return d3.polygonHull(points);
  })
  .attr("fill", d => clusterColors[d.name])
  .attr("opacity", 0.1)
  .attr("stroke", d => clusterColors[d.name])
  .attr("stroke-width", 2);
```

---

## Graph Metrics

### Centrality Metrics

**Degree Centrality**: How many connections does each node have?
```
formula: degree(node) = number of edges connected to node
range: 0 to N-1 (where N = number of nodes)
interpretation: High = hub/important entry
example: "Supply Chain" entry with 15 connections is a hub
```

**Betweenness Centrality**: How often is this node on shortest paths between other nodes?
```
formula: Complex (see networkx library), roughly:
  betweenness(node) = Σ (paths through node) / (all shortest paths)
range: 0 to 1 (normalized)
interpretation: High = bridge between communities
example: "Regulatory Framework" bridges "Environmental" and "Governance" clusters
```

**Closeness Centrality**: How close is this node to all others?
```
formula: closeness(node) = 1 / (average shortest path distance)
range: 0 to 1
interpretation: High = central to the graph structure
example: Generic "Sustainability" entry close to all others
```

### Graph-Level Metrics

**Graph Density**: How connected is the overall graph?
```
formula: density = (actual edges) / (possible edges)
         = edges / (nodes * (nodes - 1) / 2)
range: 0 to 1
interpretation:
  - 0 = no connections
  - 0.1-0.3 = sparse, topic-specific connections (good)
  - 0.3-0.5 = moderate (acceptable)
  - >0.5 = dense, everything connected (dilutes signal)
target for knowledge base: 0.15-0.35
```

**Average Clustering Coefficient**: Do neighbors tend to be connected?
```
formula: For each node, count edges between its neighbors, divide by possible edges.
         Average across all nodes.
range: 0 to 1
interpretation:
  - 0 = no clustering (tree-like)
  - 1 = complete clustering (cliques)
  - 0.3-0.6 = natural clustering (good)
usage: High = entries naturally cluster by topic
```

**Diameter**: Longest shortest path between any two nodes.
```
formula: max(shortest path length between all pairs)
interpretation:
  - Small (<5) = good navigation (max 5 hops to reach any entry)
  - Large (>10) = fragmented, hard to navigate
target: <6 hops
```

**Connected Components**: How many isolated subgraphs exist?
```
formula: Count of separate connected components
interpretation:
  - 1 = single connected graph (ideal)
  - >1 = isolated clusters (may indicate gaps in research)
target: 1 (or <3 if unavoidable)
```

---

## Graph Export & Visualization

### JSON Export (for D3.js)

**File format**: `/knowledge-graphs/sustainable-fashion-graph.json`

```json
{
  "metadata": {
    "created": "2026-02-09T14:32:00Z",
    "topic": "Sustainable Fashion Supply Chains",
    "version": "2.1",
    "statistics": {
      "nodes": 47,
      "edges": 128,
      "density": 0.34,
      "diameter": 5,
      "components": 1
    }
  },
  "nodes": [...],
  "edges": [...],
  "clusters": [...]
}
```

### SVG Export (Static Visualization)

```javascript
// Render graph to SVG, save as static image
const svgString = new XMLSerializer().serializeToString(svg.node());
const blob = new Blob([svgString], { type: "image/svg+xml" });
const url = URL.createObjectURL(blob);

const link = document.createElement("a");
link.href = url;
link.download = "knowledge-graph.svg";
link.click();
```

### DOT Format Export (Graphviz)

```
digraph KnowledgeGraph {
  rankdir=LR;
  node [shape=circle, style=filled];

  // Nodes
  "entry-1" [label="Cotton Water", fillcolor="#E74C3C"];
  "entry-2" [label="Dyeing Wastewater", fillcolor="#E74C3C"];

  // Edges
  "entry-1" -> "entry-2" [label="semantic", color="blue", penwidth=2.5];
  "entry-1" -> "entry-5" [label="hierarchical", color="green", penwidth=2.7];
}
```

Save as `.dot` file, render with Graphviz:
```bash
dot -Tpng knowledge-graph.dot -o knowledge-graph.png
```

### HTML Interactive Export

Bundle D3.js visualization as standalone HTML:
```html
<!DOCTYPE html>
<html>
<head>
  <title>Knowledge Graph: Sustainable Fashion</title>
  <script src="https://cdn.jsdelivr.net/npm/d3@7/+esm"></script>
  <style>/* ... D3 styles ... */</style>
</head>
<body>
  <div id="graph"></div>
  <script>
    // Inline D3.js rendering code
    // Load graphData from embedded JSON
    const graphData = {...};
    // ... render graph ...
  </script>
</body>
</html>
```

### Bibliography/References Export

Generate CSV of all sources cited in knowledge graph:

```csv
source_id,title,author,year,url,cited_in_entries,authority_tier
s1,Cotton Water Footprint,Smithson J,2024,https://...,entry-1;entry-3,Tier 1
s2,UNEP Textile Report,UN UNEP,2023,https://...,entry-2;entry-4,Tier 1
```

---

## Query Patterns

### Common Search Queries on Knowledge Graph

**Pattern 1: "What is related to X?"**
```javascript
function findRelated(entryId) {
  const node = graphData.nodes.find(n => n.id === entryId);
  const edges = graphData.edges.filter(e =>
    e.source === entryId || e.target === entryId
  );
  return edges.map(e =>
    e.source === entryId ? e.target : e.source
  );
}

// Usage
findRelated("entry-1")
// Returns: ["entry-2", "entry-5", "entry-7", ...]
```

**Pattern 2: "What's a prerequisite for X?"**
```javascript
function findPrerequisites(entryId) {
  const incomingEdges = graphData.edges.filter(e =>
    e.target === entryId && e.type === "dependency"
  );
  return incomingEdges.map(e => e.source);
}

// Usage
findPrerequisites("entry-quantum-computing")
// Returns: ["entry-physics-basics", "entry-math-fundamentals"]
```

**Pattern 3: "What does X cause?"**
```javascript
function findEffects(entryId) {
  const outgoingEdges = graphData.edges.filter(e =>
    e.source === entryId && e.type === "causal"
  );
  return outgoingEdges.map(e => e.target);
}

// Usage
findEffects("entry-water-scarcity")
// Returns: ["entry-cost-increase", "entry-substitutes"]
```

**Pattern 4: "Compare X and Y"**
```javascript
function findComparison(entryId1, entryId2) {
  return graphData.edges.find(e =>
    e.type === "comparative" &&
    ((e.source === entryId1 && e.target === entryId2) ||
     (e.source === entryId2 && e.target === entryId1))
  );
}
```

**Pattern 5: "Timeline of events"**
```javascript
function buildTimeline() {
  const temporalEdges = graphData.edges.filter(e => e.type === "temporal");
  const sortedEvents = [];

  // Build DAG and topological sort
  // ... implementation ...

  return sortedEvents;
}
```

**Pattern 6: "Cluster analysis"**
```javascript
function analyzeCluster(clusterName) {
  const cluster = graphData.clusters.find(c => c.name === clusterName);
  return {
    name: cluster.name,
    size: cluster.nodes.length,
    internal_density: cluster.density,
    external_connections: cluster.external_edges,
    hub_entry: cluster.centroid
  };
}
```

---

## Learning Mode: Dependency-Ordered Output

When learning mode is active (see SKILL.md Phase 3.5 Enhancement), the knowledge graph transforms from a flat exploration tool into a **progressive learning guide**. This section defines how dependency edges power content ordering, tier assignment, and PM-specific framing.

### Topological Sort on Dependency Edges

Perform a topological sort on all edges where `type === "dependency"` to determine prerequisite ordering. This produces a linear sequence where no concept appears before its prerequisites.

**Algorithm**:
```javascript
function topologicalSortDependencies(graphData) {
  // Filter to dependency edges only
  const depEdges = graphData.edges.filter(e => e.type === 'dependency');

  // Build adjacency list and in-degree map
  const inDegree = {};
  const adjList = {};
  graphData.nodes.forEach(n => {
    inDegree[n.id] = 0;
    adjList[n.id] = [];
  });

  depEdges.forEach(e => {
    // e.source REQUIRES e.target (target is prerequisite)
    // So directed edge: target → source (learn target first)
    adjList[e.target] = adjList[e.target] || [];
    adjList[e.target].push(e.source);
    inDegree[e.source] = (inDegree[e.source] || 0) + 1;
  });

  // Kahn's algorithm
  const queue = [];
  const sorted = [];

  for (const nodeId in inDegree) {
    if (inDegree[nodeId] === 0) queue.push(nodeId);
  }

  while (queue.length > 0) {
    const current = queue.shift();
    sorted.push(current);

    for (const neighbor of (adjList[current] || [])) {
      inDegree[neighbor]--;
      if (inDegree[neighbor] === 0) queue.push(neighbor);
    }
  }

  // Handle cycles (nodes not in sorted = cycle members, append at end)
  const sortedSet = new Set(sorted);
  graphData.nodes.forEach(n => {
    if (!sortedSet.has(n.id)) sorted.push(n.id);
  });

  return sorted;
}
```

**Edge direction convention**: A dependency edge `{ source: "circular-economy", target: "material-science-basics", type: "dependency" }` means "circular-economy REQUIRES material-science-basics." In the topological sort, `material-science-basics` appears first.

### Three Learning Tiers

After topological sort, assign each node a learning tier based on its **in-degree on dependency edges only** (how many prerequisites it has):

| Tier | In-Degree (dependency) | Description | Framing Style |
|------|----------------------|-------------|---------------|
| **Foundation** | 0 | No prerequisites. Entry points to the topic. | Accessible language, real-world analogies, concrete examples. "Imagine you're..." or "Think of it like..." |
| **Intermediate** | 1-2 | Builds on 1-2 foundation concepts. | Reference prerequisites explicitly: "Building on [Foundation Concept], we can now explore..." Include bridging context. |
| **Advanced** | 3+ | Requires understanding of multiple prior concepts. | Technical precision, edge cases, trade-offs, nuance. Assume reader has absorbed earlier sections. |

**Tier assignment algorithm**:
```javascript
function assignLearningTiers(graphData) {
  const depEdges = graphData.edges.filter(e => e.type === 'dependency');

  // Count dependency in-degree per node
  const depInDegree = {};
  graphData.nodes.forEach(n => { depInDegree[n.id] = 0; });
  depEdges.forEach(e => {
    depInDegree[e.source] = (depInDegree[e.source] || 0) + 1;
  });

  // Assign tiers
  graphData.nodes.forEach(n => {
    const deg = depInDegree[n.id] || 0;
    if (deg === 0) {
      n.learning_tier = 'foundation';
      n.tier_label = 'Foundation';
      n.tier_color = '#059669'; // green
    } else if (deg <= 2) {
      n.learning_tier = 'intermediate';
      n.tier_label = 'Intermediate';
      n.tier_color = '#d97706'; // amber
    } else {
      n.learning_tier = 'advanced';
      n.tier_label = 'Advanced';
      n.tier_color = '#dc2626'; // red
    }
    n.dependency_in_degree = deg;
  });

  return graphData;
}
```

### PM Context Framing

When the research topic is PM-related, apply an additional framing layer to each entry. PM-topic detection uses keyword matching against the user's original query and entry content.

**PM Detection Keywords**: `product management`, `sprint`, `OKR`, `roadmap`, `discovery`, `prioritization`, `stakeholder`, `user story`, `A/B test`, `funnel`, `retention`, `JTBD`, `jobs to be done`, `backlog`, `MVP`, `product-led growth`, `PLG`, `north star metric`, `feature flag`, `release`, `agile`, `scrum`, `kanban`, `user research`, `persona`, `product-market fit`, `PMF`, `churn`, `activation`, `onboarding`, `NPS`, `CSAT`, `RICE`, `ICE`, `MoSCoW`, `PRD`, `product requirements`

**PM Framing Additions** (added to each entry when PM mode is active):

For **Foundation** tier entries:
```markdown
### How This Applies in PM Work
[1-2 paragraphs explaining the concept in the context of day-to-day product management]

### When to Use This
- [Specific PM situations where this concept applies]

### When NOT to Use This
- [Common misapplications or anti-patterns in PM context]

### Real-World PM Scenario
[A concrete example: "You're a PM at a B2B SaaS company. Your team just shipped..."]
```

For **Intermediate** tier entries:
```markdown
### PM Practice Connection
[How this builds on foundation concepts in PM context. Reference specific prerequisite entries.]

### Related PM Frameworks
- [Framework 1]: [How it connects to this concept]
- [Framework 2]: [How it connects]

### Practical Application
[Step-by-step how a PM would apply this in their workflow]
```

For **Advanced** tier entries:
```markdown
### Expert PM Perspective
[Nuanced trade-offs, edge cases, and advanced application patterns]

### Common Pitfalls
[What experienced PMs get wrong with this concept]

### Combining with Other Frameworks
[How to synthesize this with other advanced concepts]
```

### Navigation Ordering in Webapp

When learning mode is active, the webapp sidebar and navigation follow dependency order instead of alphabetical:

1. **Sidebar sections**: Group entries by learning tier, with Foundation at top, Advanced at bottom
2. **Within each tier**: Order by topological sort position (concepts with fewer dependencies first)
3. **Visual indicators**: Show tier badge next to each entry title
4. **Progress tracking**: Optional checkmarks for entries the user has read

**Sidebar rendering (pseudocode)**:
```javascript
function renderLearningSidebar(graphData, sortedOrder) {
  const tiers = {
    foundation: { label: 'Foundation', icon: '🟢', entries: [] },
    intermediate: { label: 'Intermediate', icon: '🟡', entries: [] },
    advanced: { label: 'Advanced', icon: '🔴', entries: [] }
  };

  // Group by tier, maintaining topological order
  sortedOrder.forEach(nodeId => {
    const node = graphData.nodes.find(n => n.id === nodeId);
    if (node && tiers[node.learning_tier]) {
      tiers[node.learning_tier].entries.push(node);
    }
  });

  // Render each tier section
  for (const [tierKey, tier] of Object.entries(tiers)) {
    renderTierHeader(tier.icon, tier.label, tier.entries.length);
    tier.entries.forEach(entry => {
      renderSidebarEntry(entry, { showTierBadge: true, showPrerequisites: true });
    });
  }
}
```

### Learning Path View

A new "Learning Path" view (toggle alongside "Explore Mode" / knowledge graph) that presents entries as a linear progression:

```
┌─────────────────────────────────────────────────┐
│  LEARNING PATH                                   │
│                                                   │
│  🟢 FOUNDATION                                   │
│  ┌──────────────────────────────────────┐        │
│  │ 1. What is Product Discovery?        │───┐    │
│  └──────────────────────────────────────┘   │    │
│  ┌──────────────────────────────────────┐   │    │
│  │ 2. Understanding User Needs          │───┤    │
│  └──────────────────────────────────────┘   │    │
│                                              │    │
│  🟡 INTERMEDIATE                             │    │
│  ┌──────────────────────────────────────┐   │    │
│  │ 3. Opportunity Solution Trees    ←───┘───┤    │
│  │    Builds on: #1, #2                 │   │    │
│  └──────────────────────────────────────┘   │    │
│  ┌──────────────────────────────────────┐   │    │
│  │ 4. Assumption Mapping            ←───┘   │    │
│  │    Builds on: #1                     │───┤    │
│  └──────────────────────────────────────┘   │    │
│                                              │    │
│  🔴 ADVANCED                                 │    │
│  ┌──────────────────────────────────────┐   │    │
│  │ 5. Continuous Discovery Habits   ←───┘   │    │
│  │    Builds on: #1, #3, #4             │   │    │
│  └──────────────────────────────────────┘   │    │
└─────────────────────────────────────────────────┘
```

**Features**:
- Connecting arrows show which prerequisites feed into each entry
- "Builds on" labels reference specific earlier entries
- Entries expand inline when clicked (no page navigation needed)
- Progress indicator shows completion percentage

### Learning Mode Graph Visualization Enhancements

When learning mode is active, the D3.js knowledge graph gets additional visual cues:

1. **Node border color** = learning tier color (green/amber/red)
2. **Dependency edges highlighted** = thicker, solid lines with arrows showing "learn this first" direction
3. **Non-dependency edges dimmed** = lighter opacity to emphasize the learning path
4. **Suggested starting node** = pulsing animation on the foundation node with highest centrality
5. **"Next to learn" indicator** = when hovering a node, highlight which nodes become "unlocked" (their prerequisites are met)

---

## Implementation Checklist

Before publishing knowledge graph:

- [ ] All nodes have required fields (id, title, category, connections)
- [ ] All edges have type and strength (0-1.0)
- [ ] Graph density between 0.15-0.35
- [ ] Orphan count <10% of nodes
- [ ] Clustering coefficient 0.3-0.6
- [ ] Diameter <6
- [ ] D3.js graph renders in <2 seconds
- [ ] Graph mobile-responsive (tested on phone/tablet)
- [ ] SVG export works without errors
- [ ] DOT export for Graphviz valid
- [ ] Search queries working (test 5+ patterns)
- [ ] Cluster detection matches researcher intention
- [ ] Tooltips show relevant information
- [ ] Zoom/pan controls responsive
- [ ] Bibliography export complete

---

**Version**: 2.0
**Last Updated**: 2026-02-09
**Status**: Production
