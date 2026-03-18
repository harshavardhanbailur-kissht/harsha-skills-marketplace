# Jira Automation & API Integration

## Table of Contents
1. [Architecture Overview](#architecture)
2. [Method 1: Google Apps Script Webhook](#gas-webhook)
3. [Method 2: Python Jira Poller](#python-poller)
4. [Method 3: Jira Automation Rules](#jira-rules)
5. [Method 4: Scheduled Claude Task](#scheduled-task)
6. [Batch Generation Pipeline](#batch-pipeline)
7. [Distribution Channels](#distribution)
8. [API Reference](#api-reference)

---

## Architecture

Three automation tiers, from simplest to most sophisticated:

```
TIER 1 (Existing — already set up for Kissht):
Jira ticket → Done status
    → Jira Automation Rule → Webhook → Google Apps Script
    → Append to Google Sheet "LAP Release Notes Tracker"
    → Columns A-N populated (ticket, dates, contributors, cycle time)
    → Apps Script populates O-T (category, journey, title, status, audience, context)

TIER 2 (Enhanced — adds AI generation):
Google Sheet accumulates tickets
    → On sprint close / weekly schedule
    → Python script reads sheet / Jira API
    → AI generates stakeholder-specific guides
    → Outputs: HTML web app + Markdown files + Word docs

TIER 3 (Full automation — event-driven):
Jira ticket → Done
    → Webhook → Cloud Function / Apps Script
    → AI classification + enrichment
    → Auto-generate all stakeholder guides
    → Push to Slack / email / Confluence
    → Web dashboard auto-updates
```

## Method 1: Google Apps Script Webhook

This is already set up for the Kissht LAP project. The existing script handles:

**Webhook Receiver (doPost)**:
- Receives POST from Jira automation when ticket → Done
- Fetches full issue data via Jira REST API
- Extracts contributors (commenters, worklog, past assignees)
- Calculates cycle time
- Appends to Google Sheet

**Historical Backfill (backfillAll/backfillBatch)**:
- JQL: `project = LAP AND status = Done ORDER BY resolutiondate DESC`
- Paginated processing (50 tickets per batch)
- Duplicate detection via column A ticket key check
- Rate limiting: 500ms between API calls

**Scheduled Polling (pollRecent)**:
- Hourly trigger via Google Apps Script time-based trigger
- JQL: `project = LAP AND status changed to Done AFTER -2h`
- Safety net for missed webhooks

**Release Note Enrichment (populateReleaseNotes)**:
- Maps ticket keys to predefined categories via TICKET_MAPPING
- Populates columns O-T: Category, Journey, Title, Status, Audience, Context
- Creates separate "Release Announcements" sheet with formatted content

**Configuration needed**:
```javascript
const CONFIG = {
  JIRA_DOMAIN: "kissht.atlassian.net",
  JIRA_EMAIL: "your-email@kissht.com",
  JIRA_API_TOKEN: "your-api-token",
  PROJECT_KEY: "LAP",  // or "UP" for Ring
  SHEET_NAME: "Release Notes"
};
```

### Extending for Auto-Generation

To add AI-powered guide generation to the existing Apps Script:

```javascript
// Add to Apps Script after ticket is processed:
function triggerGuideGeneration(ticketCount) {
  // When accumulated tickets exceed threshold, trigger generation
  if (ticketCount >= 10 || isSprintEnd()) {
    // Option A: Call a Cloud Function that runs the Python generator
    const url = "YOUR_CLOUD_FUNCTION_URL/generate-guides";
    UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({
        project: CONFIG.PROJECT_KEY,
        sheetId: SpreadsheetApp.getActiveSpreadsheet().getId()
      })
    });

    // Option B: Send Slack notification to trigger manual generation
    notifySlack("Sprint closing: " + ticketCount + " tickets ready for release notes generation");
  }
}
```

## Method 2: Python Jira Poller

For environments where you want more control over the generation pipeline:

```python
# jira_poller.py — Core polling logic
import requests
from datetime import datetime, timedelta

class JiraPoller:
    def __init__(self, domain, email, api_token, project_key):
        self.base_url = f"https://{domain}"
        self.auth = (email, api_token)
        self.project_key = project_key

    def get_done_tickets(self, since_hours=24):
        """Fetch tickets moved to Done in the last N hours"""
        jql = (
            f'project = {self.project_key} '
            f'AND status changed to Done AFTER -{since_hours}h '
            f'ORDER BY updated DESC'
        )
        return self._search(jql)

    def get_sprint_tickets(self, sprint_name):
        """Fetch all Done tickets in a specific sprint"""
        jql = (
            f'project = {self.project_key} '
            f'AND sprint = "{sprint_name}" '
            f'AND status = Done '
            f'ORDER BY resolutiondate DESC'
        )
        return self._search(jql)

    def get_release_tickets(self, fix_version):
        """Fetch all tickets in a fix version"""
        jql = (
            f'project = {self.project_key} '
            f'AND fixVersion = "{fix_version}" '
            f'AND status = Done'
        )
        return self._search(jql)

    def _search(self, jql, max_results=100):
        """Execute JQL search with pagination"""
        all_issues = []
        start_at = 0
        while True:
            resp = requests.get(
                f"{self.base_url}/rest/api/3/search",
                auth=self.auth,
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": "summary,issuetype,priority,status,"
                              "assignee,reporter,created,resolutiondate,"
                              "fixVersions,sprint,labels,components",
                    "expand": "changelog"
                }
            )
            data = resp.json()
            all_issues.extend(data.get("issues", []))
            if start_at + len(data["issues"]) >= data["total"]:
                break
            start_at += len(data["issues"])
        return all_issues

    def enrich_ticket(self, issue):
        """Extract all relevant data from a Jira issue"""
        fields = issue["fields"]
        key = issue["key"]

        # Get contributors
        commenters = self._get_commenters(key)
        worklog_authors = self._get_worklog_authors(key)
        past_assignees = self._get_past_assignees(issue)
        completed_date = self._get_completed_date(issue)

        return {
            "key": key,
            "link": f"{self.base_url}/browse/{key}",
            "summary": fields.get("summary", ""),
            "issue_type": fields.get("issuetype", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "status": fields.get("status", {}).get("name", ""),
            "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
            "reporter": (fields.get("reporter") or {}).get("displayName", ""),
            "created": fields.get("created", ""),
            "completed": completed_date,
            "commenters": commenters,
            "worklog_authors": worklog_authors,
            "past_assignees": past_assignees,
            "cycle_time_days": self._calc_cycle_time(fields.get("created"), completed_date),
            "labels": [l for l in fields.get("labels", [])],
            "components": [c["name"] for c in fields.get("components", [])],
        }
```

### Integration with Release Note Generation

```python
# Pipeline: Poll → Enrich → Classify → Generate
def generate_release_notes(poller, stakeholders, output_format="html"):
    # 1. Get tickets
    tickets = poller.get_done_tickets(since_hours=168)  # Last 7 days

    # 2. Enrich each ticket
    enriched = [poller.enrich_ticket(t) for t in tickets]

    # 3. Classify (AI-powered)
    classified = classify_tickets(enriched)  # Uses domain knowledge

    # 4. Group into announcements
    announcements = group_into_announcements(classified)

    # 5. Generate stakeholder guides
    guides = {}
    for stakeholder in stakeholders:
        guides[stakeholder] = generate_guide(announcements, stakeholder)

    # 6. Output
    if output_format == "html":
        return build_web_guide(guides)
    elif output_format == "markdown":
        return {s: write_markdown(g) for s, g in guides.items()}
    elif output_format == "docx":
        return {s: write_docx(g) for s, g in guides.items()}
```

## Method 3: Jira Automation Rules

Configure in Jira directly at `kissht.atlassian.net/jira/settings/automation`:

**Rule 1: Ticket → Done → Webhook**
```
TRIGGER: When status changes TO "Done"
CONDITION: Project = LAP (or UP)
ACTION: Send web request
  URL: [Google Apps Script Web App URL]
  Method: POST
  Body: {"issueKey": "{{issue.key}}", "summary": "{{issue.summary}}"}
```

**Rule 2: Sprint Close → Notify**
```
TRIGGER: When sprint is completed
CONDITION: Project = LAP
ACTION: Send Slack message
  Channel: #releases
  Message: "Sprint {{sprint.name}} completed with {{sprint.completedIssues.size}} tickets.
            Run release notes generation."
```

**Rule 3: Fix Version Released → Generate**
```
TRIGGER: When version is released
CONDITION: Project = LAP
ACTION: Send web request to generation endpoint
  Body: {"fixVersion": "{{version.name}}", "project": "{{project.key}}"}
```

## Method 4: Scheduled Claude Task

Use the `schedule` skill to create a periodic generation task:

```
Task: kissht-release-notes-weekly
Schedule: "0 9 * * 1" (Every Monday 9 AM)
Prompt: |
  Generate weekly release notes for the Kissht LAP project.

  1. Read the CSV file at ~/Downloads/LAP Release Notes Tracker - Release Notes.csv
  2. Filter to tickets completed in the last 7 days
  3. Use the kissht-release-notes-mastery skill to generate stakeholder guides
  4. Output as HTML web app to ~/Downloads/release-notes-[date].html
  5. Generate individual markdown files for PM, QA, Dev, Training, BA, Ops
```

For one-time generation (e.g., sprint close):
```
Task: sprint-release-notes
Schedule: fireAt: "2026-03-14T17:00:00+05:30" (Friday 5 PM IST)
```

## Batch Generation Pipeline

For sprint-end batch processing:

```
Step 1: Accumulate (Ongoing — Tier 1)
    Jira webhooks → Google Sheet → Rows accumulate

Step 2: Enrich (Sprint close)
    Run Apps Script populateReleaseNotes()
    → Columns O-T populated with categories, journeys, audiences

Step 3: Export (Sprint close)
    Download CSV from Google Sheet
    OR use Python poller to fetch fresh data from Jira API

Step 4: Generate (Sprint close)
    Feed data to AI generation pipeline
    → Classify tickets
    → Group into announcements
    → Generate per-stakeholder guides

Step 5: Review (Sprint close + 1 day)
    PM reviews and approves content
    Training team flags SOP updates needed

Step 6: Distribute (Sprint close + 1-2 days)
    Push to Slack channels
    Email to stakeholder distribution lists
    Update web dashboard
    Upload to Confluence/Notion
```

## Distribution Channels

### Slack Integration
```javascript
function notifySlack(channel, guideUrl, summary) {
  const webhookUrl = "YOUR_SLACK_WEBHOOK";
  const payload = {
    channel: channel,
    blocks: [
      {
        type: "header",
        text: { type: "plain_text", text: "Release Notes Ready" }
      },
      {
        type: "section",
        text: { type: "mrkdwn", text: summary }
      },
      {
        type: "actions",
        elements: [{
          type: "button",
          text: { type: "plain_text", text: "View Release Notes" },
          url: guideUrl
        }]
      }
    ]
  };
  // Send to Slack
}
```

### Channel Routing
| Stakeholder | Slack Channel | Email DL |
|------------|--------------|----------|
| PM | #product-releases | pm-team@kissht.com |
| QA | #qa-releases | qa-team@kissht.com |
| Dev | #dev-releases | dev-team@kissht.com |
| Training | #training-updates | training@kissht.com |
| BA | #ba-releases | ba-team@kissht.com |
| Ops | #ops-releases | ops-team@kissht.com |
| Leadership | #leadership-updates | leadership@kissht.com |

## API Reference

### Jira REST API v3 (Cloud)

**Search**: `GET /rest/api/3/search?jql={jql}&fields={fields}&expand=changelog`

**Issue**: `GET /rest/api/3/issue/{issueKey}?fields=summary,status,...&expand=changelog`

**Comments**: `GET /rest/api/3/issue/{issueKey}/comment`

**Worklog**: `GET /rest/api/3/issue/{issueKey}/worklog`

**Sprint**: `GET /rest/agile/1.0/sprint/{sprintId}`

**Auth**: Basic auth with email + API token (base64 encoded)

**Rate limits**: ~100 requests/minute per user on Jira Cloud

### Google Sheets API (for reading data)
```python
# Using gspread library
import gspread
gc = gspread.service_account(filename='credentials.json')
sheet = gc.open("LAP Release Notes Tracker").worksheet("Release Notes")
records = sheet.get_all_records()
```

---

## Jira API v3 Rate Limiting (2025-2026 Changes)

**CRITICAL UPDATE**: Atlassian is transitioning Jira Cloud to a new points-based rate limiting system:

### Legacy Rate Limits (still active for most instances)
- **Per-user limit**: ~100 requests/minute
- **Concurrent requests**: ~10 simultaneous requests per user
- **Pagination**: Max 100 results per page (search), 50 recommended

### New Points-Based Rate Limits (rolling out 2025-2026)
- Each API endpoint costs a different number of "points"
- Points replenish over time windows
- Complex queries (JQL with `expand=changelog`) cost more points
- Rate limit headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

**Adaptation strategies for the poller scripts**:
```python
# Resilient API call with rate limit handling
import time

def resilient_jira_call(url, auth, params, max_retries=3):
    for attempt in range(max_retries):
        resp = requests.get(url, auth=auth, params=params)

        if resp.status_code == 200:
            return resp.json()

        if resp.status_code == 429:  # Rate limited
            retry_after = int(resp.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        if resp.status_code >= 500:  # Server error
            time.sleep(2 ** attempt)  # Exponential backoff
            continue

        # Client error — don't retry
        resp.raise_for_status()

    raise Exception(f"Failed after {max_retries} retries")
```

### OAuth 2.0 Migration Path

Jira Cloud is deprecating basic auth for some use cases. For production automation:

```python
# OAuth 2.0 (3LO) — for user-context operations
# 1. Register app at developer.atlassian.com
# 2. Get access token via OAuth flow
# 3. Use Bearer token instead of basic auth

class JiraOAuthPoller:
    def __init__(self, domain, access_token, project_key):
        self.base_url = f"https://{domain}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        self.project_key = project_key

    def _request(self, endpoint, params=None):
        return resilient_jira_call(
            f"{self.base_url}{endpoint}",
            auth=None,  # Using header auth
            params=params,
            headers=self.headers
        )
```

---

## Enhanced Automation Architecture

### Event-Driven Pipeline (Tier 3 Full Architecture)

```
                    ┌─────────────────┐
                    │    JIRA CLOUD    │
                    │                 │
                    │  Ticket → Done  │
                    └────────┬────────┘
                             │ Webhook POST
                    ┌────────┴────────┐
                    │  EVENT ROUTER   │
                    │  (Apps Script   │
                    │   or Cloud Fn)  │
                    └──┬──────────┬───┘
                       │          │
           ┌───────────┴──┐  ┌───┴───────────┐
           │ ACCUMULATOR  │  │  THRESHOLD     │
           │ Google Sheet  │  │  CHECKER       │
           │ Row appended  │  │  (N tickets?   │
           └──────────────┘  │   Sprint end?) │
                             └───┬────────────┘
                                 │ trigger
                    ┌────────────┴────────────┐
                    │   GENERATION ENGINE     │
                    │  1. Load ticket batch   │
                    │  2. Classify + enrich   │
                    │  3. Apply COSTAR lens   │
                    │  4. Render templates    │
                    │  5. Confidence tag      │
                    │  6. Verify accuracy     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   DISTRIBUTION ENGINE   │
                    │                         │
                    │  ┌──────┐ ┌──────┐     │
                    │  │Slack │ │Email │     │
                    │  │#chan  │ │  DL  │     │
                    │  └──────┘ └──────┘     │
                    │  ┌──────┐ ┌──────┐     │
                    │  │Conflu│ │ HTML │     │
                    │  │ence  │ │ File │     │
                    │  └──────┘ └──────┘     │
                    └─────────────────────────┘
```

### Webhook Payload Processing

When receiving a Jira webhook for ticket status change, extract these critical fields:

```javascript
// Webhook payload from Jira (simplified)
{
  "webhookEvent": "jira:issue_updated",
  "issue": {
    "key": "LAP-2050",
    "fields": {
      "summary": "...",
      "issuetype": { "name": "Bug" },
      "priority": { "name": "High" },
      "status": { "name": "Done" },
      "assignee": { "displayName": "..." },
      "reporter": { "displayName": "..." },
      "fixVersions": [{ "name": "Sprint 24" }],
      "labels": ["regression", "saral-sync"],
      "components": [{ "name": "Document Management" }]
    }
  },
  "changelog": {
    "items": [{
      "field": "status",
      "fromString": "In Review",
      "toString": "Done"
    }]
  }
}
```

### Batch vs Real-Time Generation Tradeoffs

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **Real-time** (per ticket) | Urgent fixes, hotfix releases | Immediate visibility | Noisy, many small updates |
| **Daily batch** | Active sprints | Balance of timeliness + coherence | May miss urgent items |
| **Sprint-close batch** | Standard sprints | Best grouping, coherent narrative | Delayed visibility |
| **Version release** | Planned releases | Cleanest output, full context | Only works with fix versions |
| **On-demand** | Ad-hoc requests | Full control, customizable | Manual trigger required |

Recommendation: Use **sprint-close batch** as default, with **real-time alerts** for Critical Fix tickets only.

### Jira Automation Rule — Advanced Triggers

```yaml
# Rule: Auto-classify and accumulate critical tickets in real-time
name: "Release Notes — Critical Fix Alert"
trigger:
  type: issue_transitioned
  to_status: Done
  conditions:
    - field: priority
      value: [Highest, High]
    - field: project
      value: LAP
actions:
  - type: send_web_request
    url: "YOUR_WEBHOOK_URL"
    method: POST
    body: |
      {
        "key": "{{issue.key}}",
        "summary": "{{issue.summary}}",
        "priority": "{{issue.priority.name}}",
        "assignee": "{{issue.assignee.displayName}}",
        "classification": "critical_fix",
        "immediate_notify": true
      }
  - type: send_slack_message
    channel: "#ops-releases"
    message: "⚠️ Critical fix deployed: {{issue.key}} — {{issue.summary}}"
```

---

## MCP Server Integration

For deeper Jira integration, build an MCP server using the `mcp-builder` skill:

```python
# Conceptual MCP server for Jira → Release Notes
# Uses FastMCP framework

from fastmcp import FastMCP

mcp = FastMCP("jira-release-notes")

@mcp.tool()
def get_sprint_tickets(project: str, sprint: str) -> dict:
    """Fetch all Done tickets in a sprint"""
    poller = JiraPoller(domain, email, token, project)
    issues = poller.get_sprint_tickets(sprint)
    return {"tickets": [poller.enrich_ticket(i) for i in issues]}

@mcp.tool()
def generate_stakeholder_guide(tickets: list, stakeholder: str) -> str:
    """Generate a guide for a specific stakeholder"""
    classified = [classify_ticket(t) for t in tickets]
    groups = group_tickets(classified)
    return GENERATORS[stakeholder](classified, groups, metadata)

@mcp.tool()
def build_release_web_app(tickets: list, stakeholders: list) -> str:
    """Generate self-contained HTML web app"""
    guides = {}
    for s in stakeholders:
        guides[s] = generate_stakeholder_guide(tickets, s)
    return build_html(guides, tickets, groups, metadata)
```

This enables natural language interaction:
- "Get all tickets from Sprint 24 and generate QA and PM guides"
- "Build a release web app for the last 7 days of LAP tickets"
- "What critical fixes were deployed this week?"

---

## Google Apps Script V8 Runtime & Best Practices

### Runtime & Execution Limits

| Limit | Value | Impact on Release Notes Pipeline |
|-------|-------|--------------------------------|
| Execution time | 6 minutes per run | Use trigger chaining for large backlogs |
| URL fetches | 20,000/day | Budget: ~100 tickets/day at 5 API calls each |
| Triggers | 20 per user per script | Reserve 3 for release notes (hourly poll, sprint close, manual) |
| Properties store | 500KB total, 9KB per key | Store last-processed timestamp, not full ticket data |
| Concurrent executions | 30/user | Unlikely to hit for release notes |

### Trigger Chaining for Large Backlogs

When backfilling >100 tickets, a single 6-minute execution won't suffice. Use trigger chaining:

```javascript
function backfillBatch() {
  const props = PropertiesService.getScriptProperties();
  const startAt = parseInt(props.getProperty('BACKFILL_OFFSET') || '0');
  const BATCH_SIZE = 50;
  const startTime = Date.now();
  const MAX_RUNTIME_MS = 5 * 60 * 1000; // 5 min safety margin

  const tickets = fetchJiraTickets(startAt, BATCH_SIZE);

  tickets.forEach((ticket, i) => {
    if (Date.now() - startTime > MAX_RUNTIME_MS) {
      // Save progress and schedule continuation
      props.setProperty('BACKFILL_OFFSET', String(startAt + i));
      ScriptApp.newTrigger('backfillBatch')
        .timeBased()
        .after(10 * 1000) // 10 second delay
        .create();
      return;
    }
    processTicket(ticket);
  });

  if (tickets.length < BATCH_SIZE) {
    // Backfill complete
    props.deleteProperty('BACKFILL_OFFSET');
    cleanupTriggers('backfillBatch');
  } else {
    props.setProperty('BACKFILL_OFFSET', String(startAt + BATCH_SIZE));
    ScriptApp.newTrigger('backfillBatch')
      .timeBased()
      .after(10 * 1000)
      .create();
  }
}

function cleanupTriggers(functionName) {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === functionName)
    .forEach(t => ScriptApp.deleteTrigger(t));
}
```

### Exponential Backoff for Jira API

```javascript
function fetchWithBackoff(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = UrlFetchApp.fetch(url, {
        ...options,
        muteHttpExceptions: true
      });
      const code = response.getResponseCode();

      if (code === 200) return JSON.parse(response.getContentText());
      if (code === 429) {
        // Rate limited — respect Retry-After header
        const retryAfter = parseInt(
          response.getHeaders()['Retry-After'] || '60'
        );
        Utilities.sleep(retryAfter * 1000);
        continue;
      }
      if (code >= 500) {
        Utilities.sleep(Math.pow(2, attempt) * 1000);
        continue;
      }
      throw new Error(`HTTP ${code}: ${response.getContentText()}`);
    } catch (e) {
      if (attempt === maxRetries - 1) throw e;
      Utilities.sleep(Math.pow(2, attempt) * 1000);
    }
  }
}
```

---

## State-Driven Pipeline Architecture

Adapted from the Project Orchestrator skill pattern — transforms the release notes pipeline from a fragile linear process into a resilient, resumable, checkpoint-driven workflow.

### Pipeline State Model

```yaml
# .release-notes/state.yaml — persisted between runs
pipeline:
  phase: "classify"  # accumulate | classify | generate | review | distribute
  phase_progress: 0.45
  started_at: "2026-03-07T09:00:00+05:30"
  last_checkpoint: "2026-03-07T09:30:00+05:30"

release:
  project: "LAP"
  sprint: "Sprint 24"
  date_range: "2026-02-24 to 2026-03-07"
  total_tickets: 45
  processed_tickets: 20

tasks:
  - id: "FETCH-001"
    name: "Fetch Done tickets from Jira"
    status: "completed"  # pending | in_progress | completed | failed | blocked
    outputs: ["data/raw_tickets.json"]

  - id: "CLASSIFY-001"
    name: "Classify tickets by category + journey"
    status: "in_progress"
    depends: ["FETCH-001"]
    progress: 0.45
    outputs: ["data/classified_tickets.json"]

  - id: "GENERATE-PM"
    name: "Generate PM stakeholder guide"
    status: "pending"
    depends: ["CLASSIFY-001"]
    assigned_template: "templates/pm-guide.md"

  - id: "GENERATE-QA"
    name: "Generate QA stakeholder guide"
    status: "pending"
    depends: ["CLASSIFY-001"]
    assigned_template: "templates/qa-guide.md"

  # ... more generation tasks per stakeholder

  - id: "REVIEW-001"
    name: "Self-review all guides"
    status: "pending"
    depends: ["GENERATE-PM", "GENERATE-QA", "GENERATE-DEV",
              "GENERATE-TRAINING", "GENERATE-BA", "GENERATE-OPS",
              "GENERATE-LEADERSHIP"]

  - id: "DISTRIBUTE-001"
    name: "Push to distribution channels"
    status: "pending"
    depends: ["REVIEW-001"]

checkpoints:
  - id: "CP-001"
    timestamp: "2026-03-07T09:15:00+05:30"
    phase: "accumulate"
    data_file: "checkpoints/cp001_raw.json"
```

### Checkpoint & Recovery

At each pipeline phase, create a checkpoint that enables:
- **Resume after failure**: If classification crashes, restart from last checkpoint
- **Rollback**: If generated guides are wrong, revert to classification checkpoint
- **Audit trail**: Every state transition logged for compliance

### Human Escalation Protocol

When the pipeline encounters ambiguity (e.g., ticket classification unclear):

```markdown
# HUMAN_INPUT_NEEDED.md

## What Happened
3 tickets don't clearly fit any category during classification.

## Ambiguous Tickets
1. LAP-2050: "Update dependencies for auth module" — Infrastructure? Security?
2. LAP-2055: "Fix typo in error message" — General Fixes? Training impact?
3. LAP-2060: "Refactor fee calculation module" — Transaction? Technical Debt?

## Options
A. Create "Infrastructure/Maintenance" category
B. Place in "General Fixes"
C. Classify by impact (LAP-2050→Security, LAP-2055→General, LAP-2060→Transaction)

## Recommendation
Option C — classify by business impact, not change type

## How to Resume
Respond with chosen option. Pipeline will resume from classification checkpoint.
```

---

## Forge Platform Migration Awareness

Atlassian is migrating app development to the Forge platform. For future-proofing:

### What's Changing
- **Connect apps** (current): Server-hosted, use REST API directly
- **Forge apps** (future): Hosted on Atlassian infrastructure, sandboxed runtime
- **Impact**: Webhooks and REST API remain stable; Forge adds new event-driven patterns

### Forge Event Triggers (Alternative to Webhooks)
```javascript
// Forge: Event-driven trigger for ticket status change
// (Not yet required — REST API + webhooks still fully supported)
import Resolver from '@forge/resolver';
import { events } from '@forge/events';

const resolver = new Resolver();

resolver.define('issue-transition', async ({ payload }) => {
  const { issue, changelog } = payload;
  const statusChange = changelog.items.find(i => i.field === 'status');

  if (statusChange?.toString === 'Done') {
    await accumulateTicket(issue);
    await checkGenerationThreshold();
  }
});

export const handler = resolver.getDefinitions();
```

### Migration Timeline
- **2025-2026**: Both Connect and Forge fully supported
- **2027+**: Connect apps may face restrictions
- **Recommendation**: Build on REST API + webhooks now; plan Forge migration when stable

---

## Advanced Jira JQL Patterns for Release Notes

### Useful JQL Queries

```sql
-- All tickets resolved in current sprint
project = LAP AND sprint in openSprints()
AND status = Done ORDER BY resolutiondate DESC

-- Tickets by a specific assignee in date range
project = LAP AND status = Done
AND assignee = "developer.name"
AND resolved >= "2026-03-01" AND resolved <= "2026-03-07"
ORDER BY priority DESC

-- Critical fixes only (for real-time alerts)
project = LAP AND status changed to Done
AND priority in (Highest, High) AND issuetype = Bug
AND resolved >= startOfDay()

-- Tickets with specific labels (for category filtering)
project = LAP AND status = Done AND labels in (saral-sync, bureau-fix)
AND sprint = "Sprint 24"

-- Tickets without fix version (orphan detection)
project = LAP AND status = Done AND fixVersion is EMPTY
AND resolved >= startOfWeek()

-- Release version tracking
project = LAP AND fixVersion = "v2.5.0" AND status = Done
ORDER BY issuetype ASC, priority DESC
```

### JQL for Sprint Velocity Metrics

```sql
-- Bug:Feature ratio for current sprint
-- (Run two queries and compute ratio)
-- Bugs:
project = LAP AND sprint in openSprints() AND issuetype = Bug AND status = Done

-- Stories:
project = LAP AND sprint in openSprints() AND issuetype = Story AND status = Done

-- Average cycle time proxy (resolved - created)
project = LAP AND sprint in openSprints() AND status = Done
AND created >= startOfMonth()
ORDER BY resolved ASC
```
