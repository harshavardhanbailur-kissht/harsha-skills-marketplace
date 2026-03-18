# API Reference Template

**API Version**: {{VERSION}} | **Last Updated**: {{DATE}} | **Stability**: {{STABLE | BETA | EXPERIMENTAL}}

---

## Overview

{{2-3 sentence description of API purpose and scope}}

**Base URL**: `{{BASE_URL}}`

**Authentication**: {{AUTH_METHOD}} — see [Authentication](#authentication)

---

## Authentication

### Method: {{AUTH_TYPE}}

{{Description of auth method — OAuth2, API Key, mTLS, etc.}}

**Example**:
```bash
curl -H "Authorization: Bearer {{TOKEN}}" \
  https://api.example.com/v1/users
```

**Token Refresh** (if applicable):
```bash
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token={{REFRESH_TOKEN}}
```

---

## Endpoints

---

### {{HTTP_METHOD}} {{ENDPOINT}}

**Confidence**: {{HIGH | MEDIUM | LOW}} ⚠️

**Description**: {{Brief description of what this endpoint does}}

**Use Case**: {{When would you call this endpoint?}}

#### Parameters

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `{{param}}` | {{type}} | Yes/No | {{description}} |

**Query Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `{{param}}` | {{type}} | Yes/No | {{default}} | {{description}} |

**Request Body** (if applicable):
```json
{
  "{{field}}": "{{type}}, e.g., string",
  "{{field}}": {{type}},
  "{{nested}}": {
    "{{field}}": "{{type}}"
  }
}
```

#### Response

**Status Code**: {{200 | 201 | 400 | 401 | 403 | 404 | 500}}

```json
{
  "{{field}}": "{{type}} — {{description}}",
  "{{field}}": {{type}},
  "{{meta}}": {
    "{{field}}": "{{type}}"
  }
}
```

**Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

#### Errors

| Code | Error Message | Description | Solution |
|------|---|---|---|
| `400` | `invalid_param` | {{Error description}} | {{How to fix}} |
| `401` | `unauthorized` | {{Error description}} | {{How to fix}} |
| `403` | `forbidden` | {{Error description}} | {{How to fix}} |
| `404` | `not_found` | {{Error description}} | {{How to fix}} |
| `429` | `rate_limit_exceeded` | {{Error description}} | {{How to fix}} |
| `500` | `server_error` | {{Error description}} | {{How to fix}} |

**Error Response Format**:
```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field": "Description of what went wrong with this field"
    }
  }
}
```

#### Examples

**Request**:
```bash
curl -X {{METHOD}} "https://api.example.com/v1/{{endpoint}}" \
  -H "Authorization: Bearer token_xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "{{field}}": "{{value}}"
  }'
```

**Response** (Success):
```json
{
  "id": "resource_123",
  "{{field}}": "{{value}}",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Response** (Error):
```json
{
  "error": {
    "code": "invalid_param",
    "message": "Missing required field: name"
  }
}
```

#### Rate Limiting

- **Limit**: {{LIMIT}} requests per {{WINDOW}}
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Behavior**: Returns `429 Too Many Requests` when exceeded

#### Pagination (if applicable)

```json
{
  "data": [{{items}}],
  "meta": {
    "total": 150,
    "page": 1,
    "page_size": 50,
    "has_next": true,
    "has_prev": false
  }
}
```

**Query Parameters**:
- `page` (int, default: 1) — Page number
- `page_size` (int, default: 50, max: 200) — Items per page

---

### {{HTTP_METHOD}} {{ENDPOINT}}

**Confidence**: {{HIGH | MEDIUM | LOW}} ⚠️

**Description**: {{Brief description}}

#### Parameters

{{Document parameters same as above}}

#### Response

{{Document response same as above}}

#### Examples

{{Provide request/response examples}}

---

## Webhooks

### Event: {{EVENT_NAME}}

**Description**: {{When is this event triggered?}}

**Delivery**:
- **Endpoint**: Customer configures on dashboard
- **Method**: `POST`
- **Headers**: `X-Webhook-Signature: HMAC-SHA256(body, secret)`

**Payload**:
```json
{
  "event_type": "{{event_name}}",
  "event_id": "evt_123",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "{{field}}": "{{value}}"
  }
}
```

**Signature Verification** (Node.js example):
```javascript
const crypto = require('crypto');
const signature = crypto
  .createHmac('sha256', webhook_secret)
  .update(JSON.stringify(body))
  .digest('hex');

if (signature !== request.headers['x-webhook-signature']) {
  throw new Error('Signature verification failed');
}
```

**Retry Policy**:
- Attempts: 3
- Backoff: Exponential (1s, 10s, 100s)
- Status Codes: Retry on 5xx, 408, 429

---

## Rate Limiting & Throttling

**Rate Limits**:
- Standard: {{LIMIT}} req/min per API key
- High Volume: {{LIMIT}} req/min (contact sales)

**Throttling**:
- Burst: {{BURST_LIMIT}} requests allowed
- Backpressure: Returns `429` when exceeded

**How to Handle 429**:
```javascript
async function callAPIWithRetry(endpoint, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(endpoint);
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        const delay = parseInt(retryAfter) * 1000;
        await sleep(delay);
        continue;
      }
      return response;
    } catch (error) {
      console.error(`Attempt ${attempt + 1} failed:`, error);
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Filtering & Sorting

### Filtering

| Field | Operator | Example |
|---|---|---|
| `name` | `$eq`, `$contains` | `?name[$contains]=john` |
| `status` | `$eq`, `$in` | `?status[$in]=active,pending` |
| `created_at` | `$gte`, `$lte`, `$eq` | `?created_at[$gte]=2024-01-01` |

### Sorting

```
?sort=name (ascending)
?sort=-name (descending)
?sort=created_at,-name (multiple fields)
```

---

## Response Codes & Status

| Code | Meaning | Retry? | Description |
|------|---------|--------|-------------|
| `200` | OK | No | Request succeeded |
| `201` | Created | No | Resource created successfully |
| `204` | No Content | No | Success, no response body |
| `400` | Bad Request | No | Invalid parameters; client error |
| `401` | Unauthorized | No | Missing or invalid auth token |
| `403` | Forbidden | No | Authenticated but not authorized |
| `404` | Not Found | No | Resource does not exist |
| `409` | Conflict | No | Resource state conflict (e.g., duplicate) |
| `429` | Too Many Requests | Yes | Rate limit exceeded; wait and retry |
| `500` | Server Error | Yes | Unexpected server error |
| `502` | Bad Gateway | Yes | Gateway error; retry after delay |
| `503` | Service Unavailable | Yes | Temporarily unavailable; retry later |

---

## Changelogs & Versioning

### API Versions

| Version | Release Date | Status | Sunset Date |
|---------|---|---|---|
| `v2` (current) | 2024-01-15 | Stable | {{DATE}} |
| `v1` | 2023-01-15 | Deprecated | 2024-06-15 |

### Recent Changes

**v2.1.0** (2024-01-15):
- Added `{{field}}` to `{{endpoint}}` response
- Deprecated `{{old_field}}`; use `{{new_field}}` instead
- Fixed: {{bug fix description}}

**v2.0.0** (2024-01-01):
- Breaking: Removed `{{field}}`; migrate to `{{replacement}}`
- New: Added support for {{feature}}

---

## SDK & Libraries

| Language | Library | Install |
|---|---|---|
| Python | `{{package_name}}` | `pip install {{package_name}}` |
| JavaScript | `{{package_name}}` | `npm install {{package_name}}` |
| Go | `github.com/{{user}}/{{repo}}` | `go get github.com/{{user}}/{{repo}}` |

**Python Example**:
```python
from {{package}} import Client

client = Client(api_key="{{token}}")
users = client.users.list(page=1)
```

**JavaScript Example**:
```javascript
const { APIClient } = require('{{package}}');
const client = new APIClient({ apiKey: '{{token}}' });
const users = await client.users.list({ page: 1 });
```

---

## Testing & Sandbox

**Sandbox Environment**: {{SANDBOX_URL}}

**Test Credentials**:
```
API Key: sk_test_{{TEST_KEY}}
```

**Test Resources**:
- Use `test_*` prefixes for IDs in sandbox
- Example: `acct_test_123456`

---

## Support & Feedback

- **Documentation**: {{DOCS_URL}}
- **Status Page**: {{STATUS_PAGE_URL}}
- **Support Email**: {{EMAIL}}
- **Slack Community**: {{SLACK_URL}}

**Report a Bug**: Open an issue on {{GITHUB_REPO}} or email {{EMAIL}}

---

## Appendix: Data Types

| Type | Format | Example |
|------|--------|---------|
| `string` | UTF-8 text | `"John Doe"` |
| `integer` | Signed 64-bit | `42` |
| `float` | IEEE 754 | `3.14` |
| `boolean` | `true` / `false` | `true` |
| `datetime` | ISO 8601 | `"2024-01-15T10:30:00Z"` |
| `array` | JSON array | `[1, 2, 3]` |
| `object` | JSON object | `{"key": "value"}` |
| `null` | JSON null | `null` |

---

**Version**: {{VERSION}} | **Generated**: {{DATE}}
