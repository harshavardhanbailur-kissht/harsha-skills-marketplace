---
name: LAP Intelligence Hub v2
description: Real-time Jira knowledge base with intelligent search, incremental sync, and theme detection for 1,839+ LAP project tickets
---

## Goal

Create and maintain a searchable, real-time intelligence hub for the LAP Jira project (Cloud ID: 76a6058f-c3ec-4764-8c15-e7d4a3e8aae2). The hub must:
- Index 1,839+ tickets across 46 epics and 13 themes (KYC, Payment, TopUp, Login, etc.)
- Enable sub-100ms search via Cmd+K with BM25F-inspired field-weighted relevance
- Maintain data freshness via incremental sync using 5-minute overlap windows
- Provide real-time analytics, theme detection, and quality insights
- Support seamless session handoff via CURRENT_OPERATION.json checkpoints

## Critical Constraints (Must Be True)

### Data Integrity
- **Chunked Architecture**: Store max 100 tickets per JSON file (< 500KB each)
- **Nested Fields**: Extract `fields.issuetype.name`, `fields.status.name`, `fields.assignee.displayName`, `fields.parent.key`
- **Completion Status**: Only tickets with status "Done" OR "LIVE" count toward completion metrics
- **Incremental Sync Window**: Always use 5-minute overlap (sync from `updated >= YYYY-MM-DD` minus 5 min)
- **JQL Pagination**: Primary method is `project = LAP AND key > LAP-{N} ORDER BY key ASC (maxResults: 100)`, secondary is `updated >= "YYYY-MM-DD"`

### Search & UX
- **Primary Interaction**: Cmd+K triggers search (not menu navigation)
- **Fuse.js Config**: key weight 3.0, summary 2.0, description 1.0, threshold 0.3, distance 100
- **Web Worker Hint**: Offload search to worker if 2K+ tickets detected
- **Dark Theme Palette**: Background #0a0e27 with semantic colors (error: #ef4444, success: #22c55e, warning: #f59e0b)

### Session Continuity
- **Checkpoint Mechanism**: Reference CURRENT_OPERATION.json for state handoff between sessions
- **Metadata Preservation**: Never discard sync timestamps, last cursor position, or theme mappings
- **Error Recovery**: Log all JQL queries with timestamps for audit/replay capability

## Quick Start

### 1. Full Data Sync
```bash
python extract_all_tickets.py --project LAP --cloud-id 76a6058f-c3ec-4764-8c15-e7d4a3e8aae2
```
Fetches all 1,839+ tickets, chunks into 100-ticket files, validates against schema.

### 2. Incremental Sync (5-min Overlap)
```bash
python generate_hub.py --incremental --overlap-minutes 5
```
Syncs only tickets updated in last 24h (respecting 5-min overlap), merges with existing data.

### 3. Search & Generate Hub
```bash
python generate_hub.py --analyze-themes --export-html
```
Detects 13 themes, generates index, exports searchable HTML with Charts.js analytics.

## Core Workflows

### Sync Workflow
1. Check CURRENT_OPERATION.json for last sync timestamp and cursor
2. Run incremental JQL with 5-min overlap window
3. Validate chunk size (max 100 tickets, < 500KB per file)
4. Update CURRENT_OPERATION.json with new cursor and timestamp
5. Log sync delta (added/modified/deleted counts)

### Search Workflow
1. User presses Cmd+K in UI
2. Query routed to Fuse.js with field weights (key: 3.0, summary: 2.0, description: 1.0)
3. If 2K+ tickets, spawn Web Worker for search execution
4. Return top 20 results within 100ms distance threshold
5. Render with snippet highlighting (bold matched terms)

### Theme Detection Workflow
1. Parse ticket summary/description against theme keyword rules
2. Apply BM25F-inspired scoring: summary matches count 2x, description 1x
3. Assign confidence levels (high > 0.8, medium 0.5-0.8, low < 0.5)
4. Map tickets to 13 themes: KYC, Payment, TopUp, Login, Settlement, API, Dashboard, Reporting, Admin, Webhook, Notification, Compliance, Infrastructure
5. Generate theme-based analytics (completion rate, velocity, open issues per theme)

### Generate Hub Workflow
1. Load chunked JSON files and merge into single in-memory index
2. Run theme detection across all tickets
3. Calculate metrics: total, completed (Done + LIVE), by-epic, by-theme
4. Build Fuse.js search index with optimized config
5. Render HTML with:
   - Search bar (Cmd+K focus)
   - Theme cards with completion % (Charts.js pie)
   - Epic breakdown (Charts.js bar)
   - Completion timeline (Charts.js line)
   - Quality metrics (missing assignees, stale tickets > 30 days)

### Add Theme Workflow
1. Define new theme name and keyword rules (summary/description patterns)
2. Update theme-detection-rules.md with scoring weights
3. Re-run theme detection across all tickets
4. Validate theme boundaries (no overlap with existing themes)
5. Commit theme update to CURRENT_OPERATION.json metadata

### Quality Check Workflow
1. Validate all chunks (file size < 500KB, count <= 100)
2. Verify nested field extraction (issuetype, status, assignee, parent)
3. Detect anomalies: missing summary, unresolved status, stale (> 60 days without update)
4. Generate quality report: completeness %, data freshness, orphaned tickets
5. Flag for manual review if any metric drops below threshold

## Session Handoff

**CURRENT_OPERATION.json** checkpoint structure:
```json
{
  "last_sync_timestamp": "2026-02-27T10:30:00Z",
  "last_cursor_key": "LAP-1839",
  "sync_method": "incremental",
  "overlap_minutes": 5,
  "total_tickets": 1839,
  "chunks_created": 19,
  "themes_detected": 13,
  "last_quality_check": "2026-02-27T09:15:00Z",
  "error_log": []
}
```

Before starting: Check CURRENT_OPERATION.json for `last_sync_timestamp` and `last_cursor_key`. Resume from that point.
After completion: Update all fields, commit checkpoint, log any errors.

## Architecture Overview

**Data Flow**:
1. **Extract**: JQL → Jira API → Validate Schema → Chunk (100 tickets/file)
2. **Transform**: Parse nested fields → Theme detect (BM25F scoring) → Generate stats
3. **Index**: Build Fuse.js index → Optimize field weights → Web Worker support
4. **Render**: HTML template → Charts.js visualizations → Dark theme styling
5. **Store**: JSON chunks + index + CURRENT_OPERATION.json checkpoint

**Files**:
- `tickets/`: 19 JSON files (LAP-1-100.json, LAP-101-200.json, etc.)
- `hub.json`: Merged index with metadata and theme mappings
- `hub.html`: Searchable UI with Charts.js analytics and dark theme
- `CURRENT_OPERATION.json`: Session checkpoint (sync state, cursors, metrics)

## Reference Files
- **jira-sync-guide.md**: JQL pagination, field extraction, cloud ID details
- **knowledge-base-schema.md**: JSON chunk schema, nested field mapping, validation rules
- **theme-detection-rules.md**: 13 theme keywords, BM25F scoring (2x summary, 1x description)
- **search-engine-config.md**: Fuse.js config (weights, threshold, distance), Web Worker hints
- **hub-generation-guide.md**: HTML template, Charts.js integration, dark theme palette
- **troubleshooting.md**: Common issues, JQL errors, sync recovery, Web Worker debugging
- **data-quality-checklist.md**: Validation rules, anomaly detection, completeness metrics

## Scripts

| Script | Purpose |
|--------|---------|
| `extract_all_tickets.py` | Full dump: fetch all LAP tickets via JQL, chunk to 100/file, validate |
| `generate_hub.py` | Transform: merge chunks, detect themes (BM25F), build Fuse.js index, render HTML |
| `verify_data.py` | QA: validate chunk schema, nested fields, completeness, detect stale tickets |
| `analyze_tickets.py` | Analytics: compute metrics by epic/theme, identify anomalies, export CSV |
| `export_knowledge.py` | Export hub as markdown/PDF for offline knowledge base |

## Key Stats

- **Total Tickets**: 1,839
- **Epics**: 46
- **Themes**: 13 (KYC, Payment, TopUp, Login, Settlement, API, Dashboard, Reporting, Admin, Webhook, Notification, Compliance, Infrastructure)
- **Chunks**: 19 files (100 tickets max per file)
- **Completion Rate**: Tickets with status "Done" or "LIVE"
- **Sync Window**: 5-minute overlap for incremental updates
- **Search Latency Target**: < 100ms (Cmd+K to first result)
- **Theme Confidence**: High (> 0.8), Medium (0.5-0.8), Low (< 0.5)
