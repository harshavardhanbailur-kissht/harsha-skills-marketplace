# Geospatial Search Encyclopedia - Quick Reference Index

## Document Overview
- **Total Words:** 7,105
- **Lines:** 1,838
- **File Size:** 60KB
- **Last Updated:** March 2026
- **Version:** 1.0

## Coverage Summary

### 1. Geospatial Indexing Data Structures (Comprehensive)

#### Covered:
- **R-tree and Variants** (R*-tree, R+-tree)
  - Mathematical foundation, complexity analysis
  - Production usage: PostGIS, Oracle, MySQL
  - Pros/cons for various workloads

- **Quadtree**
  - Recursive subdivision algorithm
  - Performance: O(log₄ N) vs O(log₂ N) for KD-tree
  - Use cases: Gaming, non-uniform data, zoom-based maps

- **KD-tree (K-Dimensional Tree)**
  - Binary tree space partitioning
  - O(log N) search, excellent for kNN
  - Curse of dimensionality (D > 20 problematic)

- **Geohash**
  - Z-order curve, string-based encoding
  - 11 precision levels detailed
  - Boundary artifacts and solutions

- **S2 Geometry (Google)**
  - Hilbert curve on sphere
  - Level 0-30 hierarchy (1cm at level 30)
  - Advantages over geohash
  - Production: Google Maps, Earth, Search

- **H3 (Uber's Hexagonal Grid)**
  - Hexagonal hierarchy (7-way subdivision)
  - O(1) operations for all common queries
  - 6 constant neighbors
  - Production: Surge pricing, delivery radius, routing

### 2. Proximity and Radius Search

#### Distance Formulas:
- **Haversine Formula**
  - Mathematical definition and implementation
  - Accuracy: ~0.5% error
  - Use when: Real-time, millions of queries/sec

- **Vincenty Formula**
  - Accounts for Earth's ellipsoid shape
  - Accuracy: 0.5 meters vs 10km for Haversine
  - Use when: High-precision geodetic calculations

#### Algorithms:
- **Two-stage Radius Search**
  - Bounding box pre-filter (O(log N))
  - Precise distance filtering (O(K))
  - 10-100x speedup vs naive approach

- **k-Nearest Neighbors (kNN)**
  - Basic expansion algorithm
  - kMkNN: 3-40x faster than KD-tree
  - HNSW: Approximate, sub-millisecond queries

### 3. Geospatial Databases

#### PostGIS (PostgreSQL)
- Complex operations: unions, buffers, intersections
- GIST, BRIN, SP-GIST indexes
- Best for: Polygons, complex geometries
- Benchmark: 161 queries/sec for bounding box

#### MongoDB 2dsphere
- Native spherical geometry
- GeoJSON Point format
- 100x speedup vs non-indexed
- Benchmark: 5-50ms per query

#### Elasticsearch
- geo_point: Simple distance queries
- geo_shape: Complex geometries
- Benchmark: 574 queries/sec (1.74s for 1000)
- Best for: Full-text + spatial integration

#### Redis Geo
- In-memory sorted sets
- Microsecond latency
- Simple operations only
- Use: Real-time tracking, caching

#### DynamoDB Geo
- Composite key with geohash
- Managed service, billions of items
- Limited geospatial operations

### 4. Implementation Patterns

#### Geofencing:
- **Circle:** Simple distance check
- **Polygon:** Ray casting algorithm, O(P) complexity
- **Isochrone:** Travel-time based, API integration
- Entry/exit detection with state tracking

#### Point-in-Polygon:
- Two-stage optimization (bbox + precise)
- Ray casting algorithm pseudocode
- O(P) for P vertices

#### Route-Based Search:
- Nearby along path algorithm
- Point-to-segment distance calculation
- Delivery route optimization use case

### 5. Production Architecture

#### Case Studies:
1. **Uber's H3 Surge Pricing**
   - H3 encoding, demand/supply aggregation
   - 6 neighbors simplicity

2. **Uber Eats Delivery**
   - Isochrone service areas
   - 30-minute delivery radius
   - Redis caching with 6-hour TTL

3. **Airbnb Map Search**
   - Geohash aggregation per zoom level
   - Viewport bounding box queries
   - CDN caching

4. **Google Maps Places**
   - S2 spatial + full-text indexing
   - Multi-index combination
   - Distance + rating + recency ranking

5. **Mapbox Search**
   - Address search with spatial relevance
   - Popularity signals integration
   - Open now filtering

### 6. Decision Trees and When to Use What

#### Decision Matrix:
| Metric | R-tree | Quadtree | Geohash | S2 | H3 | KD-tree |
|---|---|---|---|---|---|---|
| Points (<1M) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Points (1M-100M) | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Polygons | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Real-time Updates | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

#### Database Choice:
- **Real estate:** PostGIS (polygons)
- **Food delivery:** MongoDB (simple points)
- **Surge pricing:** H3 + Redis (aggregation)
- **Location search:** Elasticsearch (full-text + spatial)
- **GIS analysis:** PostGIS (complex operations)

### 7. Performance Benchmarks

#### Point Query Performance:
| Data Size | Operation | Best Time |
|---|---|---|
| 1K | Proximity | <1ms |
| 100K | Proximity | 3-5ms |
| 1M | Proximity | 10-15ms (S2) |
| 100M | Proximity | 60-100ms (H3) |
| 1B | Proximity | 100-200ms (H3) |

#### Index Build Time:
- 100K points: 30-50ms (Geohash fastest)
- 1M points: 500ms-1s
- 100M points: 1-2 minutes

#### Real-World Benchmarks:
- Elasticsearch: 574 queries/sec (bounding box)
- PostGIS: 161 queries/sec (bounding box)
- MongoDB: 5-50ms per query
- Redis Geo: Microseconds

### 8. Emerging Technologies

#### Spatio-Temporal Search:
- Combining location + time dimension
- GeoMesa: Z-order curve implementation
- Use: Fleet tracking, environmental monitoring

#### 3D Geospatial:
- Octree (quadtree for 3D)
- 3D R-tree
- Applications: Drones, mining, UAM

#### Indoor Positioning:
- WiFi fingerprinting (1-5m accuracy)
- BLE beacons (1-10m accuracy)
- Ultra-Wideband (10-30cm accuracy)
- Dead reckoning with sensor fusion

---

## References

Document includes 40+ authoritative sources covering:
- Academic papers (ACM, IEEE, PMC)
- Production systems (Uber, Google, Elasticsearch)
- Official documentation (PostGIS, MongoDB, Redis)
- Technical blogs and Medium articles
- Open-source projects (S2, H3, Sedona)

## Key Takeaways

1. **No one-size-fits-all solution** - choose based on workload
2. **Trade-offs are real** - accuracy vs speed, simplicity vs features
3. **Scale matters** - different structures for 1K vs 1B points
4. **Hybrid approaches work** - combine multiple indexes
5. **Production systems are pragmatic** - not always textbook implementations

## File Metadata
- Created: March 1, 2026
- Total Lines: 1,838
- Total Words: 7,105
- File Size: 60KB
- Format: Markdown
