# Bitbucket API Guide

Reference for querying PR metadata, commits, comments, and file changes during merge intelligence operations.

**Source**: research/bitbucket-api-complete-reference.md

## Authentication Setup

Set these environment variables before making API calls:

```bash
# Required env vars
export BB_WORKSPACE="your-workspace"
export BB_REPO="your-repo-slug"
export BB_PR_ID="123"
export BB_API_TOKEN="your-api-token"  # Repository Access Token or App Password
```

## Runnable curl Commands

All commands use consistent placeholders for easy scripting.

### Get PR Metadata

Returns title, description, source branch, destination branch.

```bash
curl -s -u "username:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID" \
  | jq '{title: .title, description: .description, source: .source.branch.name, destination: .destination.branch.name}'
```

### Get PR Commits

Lists all commits in the PR.

```bash
curl -s -u "username:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/commits" \
  | jq '.values[] | {hash: .hash, message: .message}'
```

### Get PR Comments (Review Feedback)

Returns all comments and inline feedback.

```bash
curl -s -u "username:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments" \
  | jq '.values[] | {user: .user.display_name, content: .content.raw, inline: .inline}'
```

### Get Diffstat (Changed Files)

Returns list of modified files with line counts.

```bash
curl -s -u "username:$BB_API_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/diffstat" \
  | jq '.values[] | {path: .new.path, status: .status, lines_added: .lines_added, lines_removed: .lines_removed}'
```

## Rate Limiting

- **Unauthenticated**: 60 requests/minute
- **Authenticated**: 1000 requests/hour
- **429 response**: Rate limited — implement exponential backoff (start at 1s, cap at 60s)
- **Caching**: Cache responses for the duration of the merge session to avoid redundant calls

## Pagination Pattern

API responses with multiple items use cursor-based pagination:

```bash
NEXT_URL="https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments?pagelen=100"
while [ "$NEXT_URL" != "null" ]; do
  RESPONSE=$(curl -s -u "username:$BB_API_TOKEN" "$NEXT_URL")
  echo "$RESPONSE" | jq '.values[]'
  NEXT_URL=$(echo "$RESPONSE" | jq -r '.next // "null"')
done
```

Use `pagelen=100` to reduce API calls.

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 401 | Unauthorized | Check credentials and API token scope |
| 404 | Not found | Verify workspace, repo slug, and PR ID are correct |
| 429 | Rate limited | Wait, then retry with exponential backoff |

## Graceful Degradation

If any API call fails:
1. Log the error with HTTP status and response body
2. Continue merge operation using **git-log-only mode** (CLI commands instead of API)
3. Notify user that some PR metadata (comments, review feedback) is unavailable

Example fallback: use `git log --all --graph` to understand commit history without API.
