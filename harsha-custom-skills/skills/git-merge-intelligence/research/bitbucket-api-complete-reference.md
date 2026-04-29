# Bitbucket Cloud REST API v2.0 Complete Reference
## For Merge Conflict Resolution Context

**API Base URL:** `https://api.bitbucket.org/2.0/`

**Last Updated:** April 2026

**Documentation:** [Official Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/)

---

## Table of Contents

1. [Authentication Methods](#authentication-methods)
2. [Pull Request Metadata](#pull-request-metadata)
3. [PR Diff and Diffstat](#pr-diff-and-diffstat)
4. [PR Activity](#pr-activity)
5. [PR Commits](#pr-commits)
6. [PR Comments](#pr-comments)
7. [Finding Related PRs](#finding-related-prs)
8. [Rate Limiting](#rate-limiting)
9. [Pagination](#pagination)
10. [Practical curl + jq Recipes](#practical-curl--jq-recipes)
11. [Error Handling](#error-handling)
12. [Bitbucket Server vs Cloud API Differences](#bitbucket-server-vs-cloud-api-differences)

---

## Authentication Methods

### 1. App Passwords (Deprecated as of June 9, 2026)

**Status:** App passwords are being deprecated. Bitbucket Cloud will no longer allow the creation of new app passwords, and existing app passwords will stop working entirely on **June 9, 2026**.

**Implementation:**
```bash
# Using app password with Basic Auth
curl --request GET \
  --user "$BB_USERNAME:$BB_APP_PASSWORD" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID"
```

**Variables:**
- `$BB_USERNAME`: Your Bitbucket username
- `$BB_APP_PASSWORD`: App password (not your account password)

### 2. OAuth 2.0 (Recommended)

**Grant Flows Supported:**
- Authorization Code Flow (for user delegation)
- Client Credentials Flow (for service-to-service)
- Implicit Flow (for browser-based apps)
- JWT Bearer Token Exchange (custom Bitbucket flow)

**Implementation:**
```bash
# Using OAuth access token
curl --request GET \
  --header "Authorization: Bearer $BB_ACCESS_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID"
```

**Variables:**
- `$BB_ACCESS_TOKEN`: OAuth 2.0 access token (expires in 1 hour)

**Getting an Access Token:**
```bash
# Refresh token flow (if you have a refresh token)
curl --request POST \
  --url 'https://bitbucket.org/site/oauth2/access_token' \
  --user "$BB_CLIENT_ID:$BB_CLIENT_SECRET" \
  --data "grant_type=refresh_token&refresh_token=$BB_REFRESH_TOKEN"
```

### 3. API Tokens (New Standard as of June 9, 2026)

**Status:** Recommended replacement for app passwords.

**Implementation:**
```bash
# Using API token with Basic Auth
curl --request GET \
  --user "$BB_EMAIL:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID"
```

**Variables:**
- `$BB_EMAIL`: Your Atlassian account email address
- `$BB_API_TOKEN`: API token (long-term credential)

**Token Scopes:**
- `repository:read`: Read repository data, pull requests, commits
- `repository:write`: Write repository data (create/update PRs)
- `pullrequest:read`: Read pull request details
- `pullrequest:write`: Create/update pull requests

**Choosing Authentication:**
| Method | Status | Use Case |
|--------|--------|----------|
| App Password | Deprecated (ends 6/9/2026) | Legacy integrations only |
| OAuth 2.0 | Active | Web apps, user delegation |
| API Token | Recommended | Scripts, CI/CD, automation |

---

## Pull Request Metadata

### Endpoint: Get PR Details

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Pull request ID |
| `title` | string | PR title |
| `description` | string | Full PR description (markdown) |
| `state` | string | PR state: `OPEN`, `MERGED`, `DECLINED`, `SUPERSEDED` |
| `source` | object | Source branch details |
| `source.branch.name` | string | Source branch name |
| `source.repository` | object | Source repository information |
| `destination` | object | Destination branch details |
| `destination.branch.name` | string | Destination/target branch name |
| `destination.commit.hash` | string | Commit hash at destination |
| `author` | object | PR author information |
| `author.display_name` | string | Author's display name |
| `author.username` | string | Author's username (deprecated, use account_id) |
| `author.account_id` | string | Author's account ID |
| `created_on` | string | ISO 8601 creation timestamp |
| `updated_on` | string | ISO 8601 last update timestamp |
| `merge_commit` | object | Merge commit info (if merged) |
| `merge_commit.hash` | string | Hash of merge commit |
| `close_source_branch` | boolean | Whether source branch is deleted after merge |
| `draft` | boolean | Whether PR is a draft |
| `reason` | string | Reason if declined (e.g., "DUPLICATE") |
| `reason_long` | string | Long-form reason text |
| `reviewers` | array | List of assigned reviewers |
| `reviewers[].account_id` | string | Reviewer's account ID |
| `reviewers[].display_name` | string | Reviewer's display name |
| `links` | object | Links to related resources |
| `links.self` | object | Self reference |
| `links.comments` | object | Comments endpoint |
| `links.activity` | object | Activity endpoint |
| `links.diff` | object | Diff endpoint |
| `links.diffstat` | object | Diffstat endpoint |
| `links.approve` | object | Approve endpoint |
| `links.merge` | object | Merge endpoint |
| `links.html` | object | HTML link to PR in UI |

### Example Request

```bash
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID"
```

### Example Response

```json
{
  "id": 123,
  "title": "Add merge conflict detection",
  "description": "Implements automatic detection and context analysis for merge conflicts in pull requests.",
  "state": "OPEN",
  "source": {
    "branch": {
      "name": "feature/conflict-detection"
    },
    "repository": {
      "type": "repository",
      "full_name": "workspace/repo"
    }
  },
  "destination": {
    "branch": {
      "name": "main"
    },
    "commit": {
      "hash": "abc123def456"
    }
  },
  "author": {
    "display_name": "Jane Developer",
    "account_id": "507f1f77bcf86cd799439011"
  },
  "created_on": "2026-04-01T10:15:00.000000+00:00",
  "updated_on": "2026-04-07T14:22:30.000000+00:00",
  "close_source_branch": true,
  "draft": false,
  "reviewers": [
    {
      "display_name": "John Reviewer",
      "account_id": "507f1f77bcf86cd799439012"
    }
  ],
  "links": {
    "self": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123" },
    "comments": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123/comments" },
    "activity": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123/activity" },
    "diff": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123/diff" },
    "diffstat": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123/diffstat" },
    "approve": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123/approve" },
    "merge": { "href": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123/merge" },
    "html": { "href": "https://bitbucket.org/workspace/repo/pull-requests/123" }
  }
}
```

---

## PR Diff and Diffstat

### Endpoint 1: Get PR Diff

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diff
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `context` | integer | Lines of context around changes (default: 3) |

**Response:**
Returns unified diff format showing all changes in the PR.

### Endpoint 2: Get PR Diffstat

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diffstat
```

**Response Fields (paginated array):**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Change status: `added`, `modified`, `removed` |
| `lines_removed` | integer | Number of lines deleted |
| `lines_added` | integer | Number of lines added |
| `type` | string | `file` for file changes |
| `new` | object | New file information |
| `new.path` | string | Path in new version |
| `old` | object | Old file information (if file was modified/deleted) |
| `old.path` | string | Path in old version |

**Example Request:**

```bash
# Get diff
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/diff"

# Get diffstat (more efficient for file list)
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/diffstat"
```

**Example Diffstat Response:**

```json
{
  "pagelen": 30,
  "values": [
    {
      "type": "file",
      "status": "modified",
      "lines_removed": 5,
      "lines_added": 12,
      "new": {
        "path": "src/merge/conflict.py"
      },
      "old": {
        "path": "src/merge/conflict.py"
      }
    },
    {
      "type": "file",
      "status": "added",
      "lines_removed": 0,
      "lines_added": 45,
      "new": {
        "path": "src/merge/detector.py"
      },
      "old": null
    }
  ],
  "page": 1,
  "size": 2
}
```

---

## PR Activity

### Endpoint: Get PR Activity Log

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/activity
```

**Response Fields (paginated array):**

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Activity type: `pull_request`, `approval`, `comment`, `update` |
| `pull_request` | object | PR reference |
| `comment` | object | Comment details (for comment activities) |
| `comment.id` | integer | Comment ID |
| `comment.created_on` | string | ISO 8601 timestamp |
| `comment.updated_on` | string | ISO 8601 timestamp |
| `comment.user` | object | Comment author |
| `comment.user.display_name` | string | Author display name |
| `comment.user.account_id` | string | Author account ID |
| `comment.content.raw` | string | Comment text (markdown) |
| `comment.inline` | object | Inline comment location (if present) |
| `comment.inline.path` | string | File path for inline comment |
| `comment.inline.from` | integer | Starting line (old version) |
| `comment.inline.to` | integer | Ending line (new version) |
| `approval` | object | Approval details (for approval activities) |
| `approval.user` | object | Approver information |
| `approval.user.display_name` | string | Approver display name |
| `approval.user.account_id` | string | Approver account ID |
| `approval.pullrequest` | object | Reference to PR approved |
| `reason` | string | Reason for action (e.g., "APPROVED", "CHANGES_REQUESTED") |
| `created_on` | string | ISO 8601 timestamp of activity |

**Activity Types:**
- `pull_request`: PR was created, updated, or state changed
- `approval`: Reviewer approved or removed approval
- `comment`: Comment was added or updated
- `update`: PR fields were updated (title, description, etc.)

**Example Request:**

```bash
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/activity"
```

**Example Activity Response:**

```json
{
  "pagelen": 30,
  "values": [
    {
      "type": "pull_request",
      "pull_request": {
        "id": 123,
        "title": "Add merge conflict detection"
      },
      "created_on": "2026-04-01T10:15:00.000000+00:00"
    },
    {
      "type": "comment",
      "comment": {
        "id": 456,
        "content": {
          "raw": "This approach looks good. Can you add unit tests?"
        },
        "user": {
          "display_name": "John Reviewer",
          "account_id": "507f1f77bcf86cd799439012"
        },
        "created_on": "2026-04-02T13:22:15.000000+00:00",
        "inline": {
          "path": "src/merge/conflict.py",
          "to": 45
        }
      }
    },
    {
      "type": "approval",
      "approval": {
        "pullrequest": { "id": 123 },
        "user": {
          "display_name": "John Reviewer",
          "account_id": "507f1f77bcf86cd799439012"
        }
      },
      "created_on": "2026-04-03T15:30:00.000000+00:00"
    }
  ],
  "page": 1,
  "pagelen": 30,
  "size": 3
}
```

---

## PR Commits

### Endpoint: Get PR Commits

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/commits
```

**Response Fields (paginated array):**

| Field | Type | Description |
|-------|------|-------------|
| `hash` | string | Commit SHA-1 hash |
| `date` | string | ISO 8601 commit timestamp |
| `message` | string | Commit message |
| `author` | object | Commit author |
| `author.raw` | string | Full author line (name + email) |
| `author.user` | object | Bitbucket user (if registered) |
| `author.user.display_name` | string | Display name |
| `author.user.account_id` | string | Account ID |
| `parents` | array | Parent commit hashes |
| `parents[].hash` | string | Parent commit hash |
| `links` | object | Links to related resources |

**Example Request:**

```bash
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/commits?pagelen=50"
```

**Example Commits Response:**

```json
{
  "pagelen": 50,
  "values": [
    {
      "hash": "abc123def456789",
      "date": "2026-04-01T10:10:00.000000+00:00",
      "message": "Implement conflict detection algorithm\n\nAdds new ConflictDetector class that analyzes\nmerge conflict markers and provides context.",
      "author": {
        "raw": "Jane Developer <jane@example.com>",
        "user": {
          "display_name": "Jane Developer",
          "account_id": "507f1f77bcf86cd799439011"
        }
      },
      "parents": [
        { "hash": "prev123hash" }
      ]
    },
    {
      "hash": "xyz789abc123",
      "date": "2026-04-01T11:20:00.000000+00:00",
      "message": "Add unit tests for conflict detection",
      "author": {
        "raw": "Jane Developer <jane@example.com>"
      },
      "parents": [
        { "hash": "abc123def456789" }
      ]
    }
  ],
  "page": 1,
  "size": 2
}
```

---

## PR Comments

### Endpoint: Get PR Comments

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pagelen` | integer | Results per page (max: 100, default: 30) |
| `page` | integer | Page number (starts at 1) |
| `sort` | string | Sort order: `-created_on` (newest first) or `created_on` (oldest first) |

**Response Fields (paginated array):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Comment ID |
| `created_on` | string | ISO 8601 creation timestamp |
| `updated_on` | string | ISO 8601 last update timestamp |
| `content` | object | Comment content |
| `content.raw` | string | Comment text (markdown) |
| `content.markup` | string | Markup type (usually `markdown`) |
| `content.html` | string | Rendered HTML (if available) |
| `user` | object | Comment author |
| `user.display_name` | string | Author display name |
| `user.account_id` | string | Author account ID |
| `user.username` | string | Author username (deprecated) |
| `inline` | object | Inline comment location (null if general comment) |
| `inline.path` | string | File path for inline comment |
| `inline.from` | integer | Starting line in old version |
| `inline.to` | integer | Ending line in new version |
| `type` | string | Always `pullrequest_comment` |
| `pullrequest` | object | PR reference |
| `links` | object | Links to related resources |

### Creating a Comment

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments
```

**Request Body (General Comment):**

```json
{
  "content": {
    "raw": "This looks good, but consider adding error handling."
  }
}
```

**Request Body (Inline Comment):**

```json
{
  "content": {
    "raw": "This function should validate input parameters."
  },
  "inline": {
    "path": "src/merge/conflict.py",
    "to": 42
  }
}
```

**Example Requests:**

```bash
# Get all comments for a PR
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments"

# Create a general comment
curl --request POST \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "content": {
      "raw": "This implementation is solid."
    }
  }' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments"

# Create an inline comment
curl --request POST \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
    "content": {
      "raw": "Consider adding type hints here."
    },
    "inline": {
      "path": "src/merge/conflict.py",
      "to": 25
    }
  }' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments"
```

**Example Comments Response:**

```json
{
  "pagelen": 30,
  "values": [
    {
      "id": 456,
      "created_on": "2026-04-02T13:22:15.000000+00:00",
      "updated_on": "2026-04-02T13:22:15.000000+00:00",
      "content": {
        "raw": "This approach looks good. Can you add unit tests?"
      },
      "user": {
        "display_name": "John Reviewer",
        "account_id": "507f1f77bcf86cd799439012"
      },
      "inline": {
        "path": "src/merge/conflict.py",
        "to": 45
      },
      "type": "pullrequest_comment"
    },
    {
      "id": 457,
      "created_on": "2026-04-03T09:15:00.000000+00:00",
      "updated_on": "2026-04-03T09:15:00.000000+00:00",
      "content": {
        "raw": "All tests added and passing."
      },
      "user": {
        "display_name": "Jane Developer",
        "account_id": "507f1f77bcf86cd799439011"
      },
      "inline": null,
      "type": "pullrequest_comment"
    }
  ],
  "page": 1,
  "pagelen": 30,
  "size": 2
}
```

---

## Finding Related PRs

### Finding PRs on the Same Destination Branch

```
GET /2.0/repositories/{workspace}/{repo}/pullrequests?q=destination.branch.name+%3D+"<branch_name>"&state=OPEN
```

**Query Syntax:**
- `destination.branch.name = "main"`: PRs targeting main branch
- `source.branch.name = "feature/x"`: PRs from feature/x branch
- `state = "OPEN"`: Only open PRs
- `state = "MERGED"`: Only merged PRs

**Example Requests:**

```bash
# Find all open PRs targeting main branch
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?q=destination.branch.name%20=%20%22main%22%20and%20state=%22OPEN%22"

# Find PRs with specific source and destination branches
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?q=source.branch.name=%22feature/x%22%20and%20destination.branch.name=%22develop%22"

# Find all merged PRs between two branches
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?q=source.branch.name=%22release/1.0%22%20and%20destination.branch.name=%22main%22%20and%20state=%22MERGED%22"
```

**Available Query Fields:**
- `destination.branch.name`: Target branch name
- `source.branch.name`: Source branch name
- `state`: PR state (OPEN, MERGED, DECLINED, SUPERSEDED)
- `author.display_name`: PR author
- `created_on`: Creation date for range queries
- `updated_on`: Last update date for range queries

---

## Rate Limiting

### Rate Limit Basics

Bitbucket Cloud enforces rate limits on API requests to prevent abuse and maintain service stability.

**Limit Measurements:**
- **Unauthenticated requests:** Measured per IP address
- **Authenticated requests:** Measured per user ID
- **Token-based requests:** Measured per access token

### Standard Rate Limits

| User Type | Requests per Hour | Notes |
|-----------|------------------|-------|
| Unauthenticated | 60 | Per IP address |
| Authenticated | 3,600 | Per user ID |
| With paid seats | 3,600 + (10 × paid users) | Capped at 10,000/hour |

### Monitoring Rate Limits

**Response Headers:**

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Total requests allowed in the window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |
| `X-RateLimit-NearLimit` | `true` when remaining < 20% of limit |

**Example:**

```bash
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  --include \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests" \
  | grep "X-RateLimit"
```

### Handling 429 Responses

When you receive a 429 (Too Many Requests) response:

```json
{
  "type": "error",
  "error": {
    "message": "Rate limit exceeded"
  }
}
```

**Strategies:**

1. **Exponential Backoff:**
   ```bash
   for attempt in {1..5}; do
     response=$(curl --request GET \
       --user "$BB_USERNAME:$BB_API_TOKEN" \
       --write-out "\n%{http_code}" \
       "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID")

     http_code=$(echo "$response" | tail -n1)

     if [ "$http_code" = "429" ]; then
       sleep $((2 ** attempt))
       continue
     fi
     break
   done
   ```

2. **Check Before Making Requests:**
   ```bash
   # Check remaining requests
   remaining=$(curl --request GET \
     --user "$BB_USERNAME:$BB_API_TOKEN" \
     --include \
     --silent \
     "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests" \
     | grep "X-RateLimit-Remaining" | cut -d' ' -f2)

   if [ "$remaining" -lt 50 ]; then
     echo "Approaching rate limit. Waiting..."
     sleep 3600
   fi
   ```

3. **Use Multiple Authentication Methods:**
   - Distribute requests across multiple user accounts
   - Use service accounts with additional paid seats
   - Implement request queuing with staggered timing

4. **Optimize Requests:**
   - Use `pagelen=100` to fetch more data per request
   - Use the `fields` parameter to request only needed fields
   - Cache responses appropriately

---

## Pagination

### Pagination Structure

Bitbucket Cloud returns paginated results in collections with the following structure:

```json
{
  "pagelen": 30,
  "values": [...],
  "page": 1,
  "size": 75,
  "next": "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests?page=2&pagelen=30"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `pagelen` | integer | Number of results per page (requested) |
| `page` | integer | Current page number (starts at 1) |
| `size` | integer | Total number of results |
| `values` | array | Results on current page |
| `next` | string | URL for next page (omitted on last page) |
| `previous` | string | URL for previous page (omitted on first page) |

### Pagination Parameters

```
GET /endpoint?page=1&pagelen=50
```

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | N/A | Page number (1-indexed) |
| `pagelen` | integer | 30 | 100 | Results per page |

### Pagination Best Practices

**Do NOT construct page URLs manually.** Always use the `next` field returned in responses:

```bash
# Initial request
url="https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?pagelen=100"

while [ -n "$url" ]; do
  response=$(curl --request GET \
    --user "$BB_USERNAME:$BB_API_TOKEN" \
    --header 'Accept: application/json' \
    "$url")

  echo "$response" | jq '.values[]'

  # Get next page URL from response
  url=$(echo "$response" | jq -r '.next // empty')
done
```

### Efficient Pagination Example

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

# Fetch all comments for a PR with pagination
fetch_all_pr_comments() {
  local url="https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments?pagelen=100"
  local all_comments="[]"

  while [ -n "$url" ]; do
    response=$(curl -s --request GET \
      --user "$BB_USERNAME:$BB_API_TOKEN" \
      --header 'Accept: application/json' \
      "$url")

    # Merge comment values
    all_comments=$(echo "$all_comments" "$response" | \
      jq -s '.[0] + (.[1].values // [])')

    # Get next URL
    url=$(echo "$response" | jq -r '.next // empty')
  done

  echo "$all_comments"
}

fetch_all_pr_comments
```

---

## Practical curl + jq Recipes

### Recipe 1: Extract PR Title and Description

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID" | \
  jq '{
    id: .id,
    title: .title,
    description: .description,
    author: .author.display_name,
    state: .state
  }'
```

**Output:**
```json
{
  "id": 123,
  "title": "Add merge conflict detection",
  "description": "Implements automatic detection...",
  "author": "Jane Developer",
  "state": "OPEN"
}
```

### Recipe 2: List All Changed Files with Stats

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/diffstat?pagelen=100" | \
  jq '.values[] | {
    status: .status,
    path: (.new.path // .old.path),
    added: .lines_added,
    removed: .lines_removed
  }'
```

**Output:**
```json
{
  "status": "modified",
  "path": "src/merge/conflict.py",
  "added": 12,
  "removed": 5
}
{
  "status": "added",
  "path": "src/merge/detector.py",
  "added": 45,
  "removed": 0
}
```

### Recipe 3: Extract All Commit Messages

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

# Fetch all commits with pagination
fetch_all_commits() {
  local url="https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/commits?pagelen=100"

  while [ -n "$url" ]; do
    response=$(curl -s --request GET \
      --user "$BB_USERNAME:$BB_API_TOKEN" \
      --header 'Accept: application/json' \
      "$url")

    echo "$response" | jq '.values[] | {
      hash: .hash[0:8],
      message: .message,
      author: .author.user.display_name // .author.raw,
      date: .date
    }'

    url=$(echo "$response" | jq -r '.next // empty')
  done
}

fetch_all_commits
```

**Output:**
```json
{
  "hash": "abc123de",
  "message": "Implement conflict detection algorithm",
  "author": "Jane Developer",
  "date": "2026-04-01T10:10:00.000000+00:00"
}
```

### Recipe 4: Extract Review Comments (Inline + General)

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

# Fetch all comments with pagination
fetch_all_comments() {
  local url="https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments?pagelen=100&sort=-created_on"

  while [ -n "$url" ]; do
    response=$(curl -s --request GET \
      --user "$BB_USERNAME:$BB_API_TOKEN" \
      --header 'Accept: application/json' \
      "$url")

    echo "$response" | jq '.values[] | {
      id: .id,
      type: (if .inline then "inline" else "general" end),
      file: .inline.path // "general",
      line: .inline.to // "N/A",
      author: .user.display_name,
      comment: .content.raw,
      created: .created_on
    }'

    url=$(echo "$response" | jq -r '.next // empty')
  done
}

fetch_all_comments
```

**Output:**
```json
{
  "id": 456,
  "type": "inline",
  "file": "src/merge/conflict.py",
  "line": 45,
  "author": "John Reviewer",
  "comment": "This approach looks good.",
  "created": "2026-04-02T13:22:15.000000+00:00"
}
```

### Recipe 5: Check PR Approval Status

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

# Get approval status from activity
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/activity" | \
  jq '.values[] | select(.type == "approval") | {
    approver: .approval.user.display_name,
    action: (if .approval then "approved" else "removed" end),
    date: .created_on
  }'
```

**Output:**
```json
{
  "approver": "John Reviewer",
  "action": "approved",
  "date": "2026-04-03T15:30:00.000000+00:00"
}
```

### Recipe 6: Find Merge Conflicts Using Diff

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

# Extract conflict markers from diff
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  --header 'Accept: application/json' \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/diff" | \
  grep -E "^(\+{7}|={7}|-{7})" | \
  head -20
```

**Note:** Returns lines with conflict markers if present.

### Recipe 7: Get PR Overview for Merge Conflict Analysis

```bash
#!/bin/bash

BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"

# Combined fetch for merge conflict context
{
  echo "=== PR METADATA ==="
  curl -s --request GET \
    --user "$BB_USERNAME:$BB_API_TOKEN" \
    --header 'Accept: application/json' \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID" | \
    jq '{
      title: .title,
      source: .source.branch.name,
      destination: .destination.branch.name,
      state: .state,
      author: .author.display_name
    }'

  echo ""
  echo "=== CHANGED FILES ==="
  curl -s --request GET \
    --user "$BB_USERNAME:$BB_API_TOKEN" \
    --header 'Accept: application/json' \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/diffstat" | \
    jq '.values | length' && \
    echo "files changed"

  echo ""
  echo "=== RECENT COMMENTS ==="
  curl -s --request GET \
    --user "$BB_USERNAME:$BB_API_TOKEN" \
    --header 'Accept: application/json' \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments?pagelen=5&sort=-created_on" | \
    jq '.values | length' && \
    echo "recent comments"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Causes | Resolution |
|------|---------|--------|-----------|
| **200** | OK | Request succeeded | No action needed |
| **201** | Created | Resource created | No action needed |
| **204** | No Content | Success, no response body | No action needed |
| **400** | Bad Request | Invalid parameters or malformed JSON | Check request syntax; validate parameters |
| **401** | Unauthorized | Invalid/missing authentication | Verify credentials; check token expiry; update API token after 6/9/2026 |
| **403** | Forbidden | Authenticated but no permission | Check repository access; verify token scopes |
| **404** | Not Found | Resource doesn't exist | Verify workspace, repo, and PR ID exist |
| **429** | Too Many Requests | Rate limit exceeded | Implement backoff; check remaining quota; use pagination |
| **500** | Server Error | Bitbucket service error | Retry after delay; check status page |
| **503** | Service Unavailable | Bitbucket maintenance | Retry after delay; check status page |

### Error Response Format

```json
{
  "type": "error",
  "error": {
    "message": "Detailed error message",
    "detail": "Additional context if available"
  }
}
```

### Common Error Scenarios

**401: Invalid Credentials**

```bash
# Problem: Using wrong authentication method
curl --request GET \
  --user "user@example.com:old-app-password" \
  "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests"

# Error Response:
# {
#   "type": "error",
#   "error": {
#     "message": "Unauthorized"
#   }
# }

# Solution: Use API token instead (after 6/9/2026)
curl --request GET \
  --user "user@example.com:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests"
```

**403: Insufficient Permissions**

```bash
# Problem: Token doesn't have required scope
curl --request GET \
  --user "user@example.com:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/workspace/private-repo/pullrequests"

# Error Response:
# {
#   "type": "error",
#   "error": {
#     "message": "You do not have permission"
#   }
# }

# Solution: Create token with appropriate scope (repository:read)
```

**404: Not Found**

```bash
# Problem: PR ID doesn't exist
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/99999"

# Error Response:
# {
#   "type": "error",
#   "error": {
#     "message": "Not found"
#   }
# }

# Solution: Verify PR exists
curl --request GET \
  --user "$BB_USERNAME:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests"
```

**429: Rate Limited**

```bash
# Problem: Too many requests
# HTTP 429 Too Many Requests
# Headers: X-RateLimit-Remaining: 0

# Solution: Implement backoff and retry
for attempt in {1..5}; do
  http_code=$(curl -w "%{http_code}" -o /dev/null -s \
    --user "$BB_USERNAME:$BB_API_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests")

  if [ "$http_code" = "429" ]; then
    sleep $((2 ** attempt))
    continue
  else
    break
  fi
done
```

### Error Handling Best Practices

```bash
#!/bin/bash

# Comprehensive error handling example
BB_USERNAME="user@example.com"
BB_API_TOKEN="token"
BB_WORKSPACE="workspace"
BB_REPO="repo"
BB_PR_ID="123"

make_api_request() {
  local method=$1
  local endpoint=$2
  local data=$3

  local response=$(curl -s -w "\n%{http_code}" \
    --request "$method" \
    --user "$BB_USERNAME:$BB_API_TOKEN" \
    --header 'Accept: application/json' \
    --header 'Content-Type: application/json' \
    ${data:+--data "$data"} \
    "$endpoint")

  local body=$(echo "$response" | head -n -1)
  local http_code=$(echo "$response" | tail -n 1)

  case $http_code in
    200|201|204)
      echo "$body"
      return 0
      ;;
    401)
      echo "ERROR: Authentication failed. Check credentials." >&2
      return 1
      ;;
    403)
      echo "ERROR: Insufficient permissions." >&2
      return 1
      ;;
    404)
      echo "ERROR: Resource not found." >&2
      return 1
      ;;
    429)
      echo "ERROR: Rate limited. Waiting..." >&2
      sleep 60
      # Retry once
      make_api_request "$method" "$endpoint" "$data"
      ;;
    *)
      echo "ERROR: HTTP $http_code" >&2
      echo "$body" >&2
      return 1
      ;;
  esac
}

# Usage
make_api_request "GET" \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID"
```

---

## Bitbucket Server vs Cloud API Differences

### API Architecture

| Aspect | Cloud (v2.0) | Server (v1.0) |
|--------|--------------|---------------|
| **Base URL** | `https://api.bitbucket.org/2.0/` | `https://<instance>/rest/api/1.0/` |
| **Version** | 2.0 (modern REST) | 1.0 (legacy) |
| **Authentication** | OAuth 2.0, App Passwords, API Tokens | Basic Auth, Personal Access Tokens |
| **Deployment** | Atlassian Cloud (SaaS) | On-premise or Data Center |

### Endpoint Differences

**Cloud:**
```
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/activity
GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments
```

**Server:**
```
GET /1.0/projects/{project}/repos/{repo}/pull-requests/{id}
GET /1.0/projects/{project}/repos/{repo}/pull-requests/{id}/activities
GET /1.0/projects/{project}/repos/{repo}/pull-requests/{id}/comments
```

### Key API Differences

| Feature | Cloud | Server |
|---------|-------|--------|
| **Rate Limiting** | Yes, enforced hourly | No rate limiting (configurable) |
| **Privacy** | Returns account_id, not username | Returns usernames |
| **Links in Responses** | Included (HATEOAS) | Less structured |
| **Merge Conflict Detection** | No direct endpoint | Limited support |
| **Webhooks** | Supported | Supported |
| **OAuth 2.0** | Full support | Limited support |
| **Pagination** | `page`, `pagelen` | `start`, `limit` |
| **Workspace Concept** | Yes (replaces projects) | Projects instead |

### Authentication Differences

**Cloud Authentication:**
```bash
# OAuth 2.0
Authorization: Bearer $ACCESS_TOKEN

# API Token (new standard)
--user "email@example.com:$API_TOKEN"

# App Password (deprecated)
--user "username:$APP_PASSWORD"
```

**Server Authentication:**
```bash
# Personal Access Token
Authorization: Bearer $PERSONAL_ACCESS_TOKEN

# Basic Auth (legacy)
--user "username:password"
```

### Migration Considerations

When migrating from Server to Cloud:

1. **Authentication:** Update to use OAuth 2.0 or API Tokens
2. **Endpoints:** Update paths (workspace/repo instead of project/repo)
3. **Field Names:** Some fields differ (e.g., usernames become account IDs)
4. **Rate Limits:** Implement rate limit handling
5. **API Links:** Cloud includes HATEOAS links; use them instead of constructing URLs manually

### Example: Getting PR Details

**Server (v1.0):**
```bash
curl --request GET \
  --user "username:password" \
  "https://bitbucket.example.com/rest/api/1.0/projects/PROJ/repos/repo/pull-requests/123"
```

**Cloud (v2.0):**
```bash
curl --request GET \
  --user "email@example.com:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/workspace/repo/pullrequests/123"
```

---

## References and Resources

### Official Atlassian Documentation

- [Bitbucket Cloud REST API v2.0](https://developer.atlassian.com/cloud/bitbucket/rest/)
- [Bitbucket Cloud REST API - Pull Requests](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/)
- [Using App Passwords](https://support.atlassian.com/bitbucket-cloud/docs/using-app-passwords/)
- [OAuth 2.0 on Bitbucket Cloud](https://support.atlassian.com/bitbucket-cloud/docs/use-oauth-on-bitbucket-cloud/)
- [API Request Limits](https://support.atlassian.com/bitbucket-cloud/docs/api-request-limits/)
- [Rate Limit Troubleshooting](https://support.atlassian.com/bitbucket-cloud/kb/bitbucket-cloud-rate-limit-troubleshooting/)

### Community Resources

- [Bitbucket API Guide - Zuplo](https://zuplo.com/learning-center/bitbucket-api)
- [Python Atlassian API Library](https://github.com/atlassian-api/atlassian-python-api)
- [How to Get Pull Request Data with REST API](https://stiltsoft.com/blog/how-to-get-pull-request-data-with-rest-api-in-bitbucket-cloud/)

### Key Findings Summary

1. **Authentication is transitioning:** App passwords deprecated June 9, 2026; API Tokens are the new standard
2. **Rate limits are per-token:** Plan accordingly for high-volume operations
3. **Always use paginated endpoints:** Don't construct URLs manually; use the `next` field
4. **Inline comments are supported:** For merge conflict analysis, extract via the `inline` object in comments/activity
5. **Diff and diffstat differ:** Use diffstat for file lists; use diff for full diffs
6. **HATEOAS links provided:** Every PR response includes links to activity, comments, diff, diffstat, etc.
7. **Workspace model in Cloud:** Different from Server's project-based model
8. **Rate limit headers included:** Monitor X-RateLimit-* headers for proactive management

---

**Document Version:** 1.0
**Last Updated:** April 7, 2026
**Status:** Complete and verified against Bitbucket Cloud API v2.0
