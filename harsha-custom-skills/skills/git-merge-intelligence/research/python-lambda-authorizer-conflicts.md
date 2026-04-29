# Python Lambda Authorizer Conflict Patterns: Comprehensive Research

**Date**: April 2026
**Focus**: Conflict resolution patterns for Python Lambda authorizers in AWS API Gateway
**Scope**: Architecture, security implications, and merge strategies

---

## 1. Lambda Authorizer Architecture

### 1.1 How Lambda Authorizers Work in API Gateway

Lambda authorizers (custom authorizers) are AWS Lambda functions that implement custom authorization logic for API Gateway endpoints. When a client makes a request to an API Gateway API, the authorization flow works as follows:

1. **Request Interception**: API Gateway intercepts the incoming request
2. **Authorization Check**: API Gateway checks if the method request is configured with a Lambda authorizer
3. **Authorizer Invocation**: If configured, API Gateway invokes the Lambda authorizer function, passing request context
4. **Token/Parameter Validation**: The Lambda function validates the caller's identity (either from bearer token or request parameters)
5. **Policy Generation**: The authorizer returns an IAM policy that specifies whether the caller has access
6. **Policy Caching**: API Gateway caches the returned policy for up to 1 hour (by default)
7. **Request Processing**: Based on the policy, the request either proceeds to the backend or is rejected

The authorizer also returns a principal identifier (caller's ID) and optionally a context object containing additional information to pass to the backend integration.

**Reference**: [AWS API Gateway Lambda Authorizers Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)

### 1.2 Token-Based vs Request-Based Authorizers

#### Token-Based Authorizers
- **Input**: Receives a bearer token (JWT, OAuth token, or custom format) from a fixed location (typically Authorization header)
- **Cache Key**: The token value itself becomes the cache key automatically
- **Use Case**: When identity information is encapsulated in a token (OAuth 2.0, OpenID Connect)
- **Validation**: Extract and validate the token, verify signature, check claims
- **Example Flow**:
  ```
  Client → Authorization: Bearer eyJhbGc... → API Gateway → Lambda Authorizer
  ```

#### Request-Based Authorizers
- **Input**: Receives the entire request object including headers, query parameters, stage variables, and API Gateway context
- **Cache Key**: Must be explicitly specified (typically Authorization header, apiKey query parameter, or context variables)
- **Use Case**: When authorization depends on multiple request attributes (headers, IP, query params, path)
- **Validation**: Inspect multiple request properties before making authorization decision
- **Example Flow**:
  ```
  Client → Headers + Query + Context → API Gateway → Lambda Authorizer
  ```

**Key Difference**: Token-based is simpler for stateless token validation; request-based is more flexible for complex authorization logic.

**Reference**: [AWS API Gateway Lambda Authorizer Input Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-input.html)

### 1.3 Authorization Flow and Component Breakdown

#### Complete Authorization Flow

```
1. CLIENT REQUEST
   ├─ Bearer Token OR
   └─ Request Parameters + Headers

2. API GATEWAY
   ├─ Check if method has Lambda authorizer configured
   ├─ Look for cached policy (cache key-based lookup)
   └─ If not cached, invoke Lambda

3. LAMBDA AUTHORIZER FUNCTION
   ├─ Extract token or request context
   ├─ Validate token/credentials
   │  ├─ Signature verification
   │  ├─ Claims validation
   │  ├─ Expiration check
   │  └─ Custom business logic
   ├─ Generate IAM Policy
   │  ├─ Principal ID
   │  ├─ Effect (Allow/Deny)
   │  ├─ Resource ARN patterns
   │  └─ Context object (optional)
   └─ Return AuthorizerResponse

4. API GATEWAY CACHING
   ├─ Cache policy for up to 1 hour
   ├─ Cache key: token or explicit cache key parameters
   └─ Subsequent requests use cached policy (critical security concern)

5. REQUEST EVALUATION
   ├─ Apply cached/returned IAM policy
   ├─ If Allow: Forward to backend integration
   └─ If Deny: Return 403 Forbidden

6. CONTEXT PASSING
   └─ authorizer context object → backend integration
      (accessible in Lambda proxy events or as headers)
```

#### Key Components

**Principal Identifier**:
- The unique identifier of the caller (user ID, email, service name)
- Must be returned in all authorizer responses
- Used in CloudTrail logging and context

**IAM Policy Document**:
- Standard AWS IAM policy format
- Specifies allowed/denied API Gateway methods and resources
- Wildcards supported for resource patterns (e.g., `arn:aws:execute-api:region:account:api-id/stage/GET/*`)

**Context Object**:
- Optional dictionary of key-value pairs (strings only in API Gateway)
- Passed to backend integration
- Useful for passing user metadata (role, department, subscription tier)

**Reference**: [AWS Lambda Authorizer Response Format](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)

---

## 2. Python Lambda Authorizer Conflict Patterns

This section covers the most common merge conflict scenarios in Python Lambda authorizer code.

### 2.1 Google-Auth Library Usage and OIDC Token Validation Conflicts

#### Pattern: Version Conflicts in google-auth

**Scenario**: Different branches update google-auth to different versions, or one branch adds google-auth while another adds a dependency with conflicting cryptography requirements.

**Common Conflict**:
```
requirements.txt (Branch A):
  google-auth==2.30.0
  cryptography==41.0.0

requirements.txt (Branch B):
  google-auth==2.25.0
  pyopenssl==23.2.0  # Conflicts with enterprise_cert extras
```

**Risk**: Incorrect resolution can lead to version incompatibility, failing token validation, or runtime import errors.

**Security Consideration**: The google-auth library's behavior may differ between versions, affecting token validation rigor.

**Resolution Strategy**:
- Always merge toward the NEWER version of google-auth
- Verify that chosen version supports all features used in the codebase
- Test that `id_token.verify_oauth2_token()` functions correctly with the selected version
- **Conflict Rule**: Avoid combining `pyopenssl` and `enterprise_cert` extras simultaneously

**Reference**: [google-auth PyPI Package](https://pypi.org/project/google-auth/)

#### Pattern: Token Validation Logic Conflicts

**Scenario**: Both branches modify OIDC token validation code, each adding different checks or refactoring validation flow.

**Example Conflict**:
```python
# Branch A: Stricter audience validation
def validate_token(token):
    info = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience=EXPECTED_AUDIENCE,  # Added explicit audience check
        clock_skew_in_seconds=5
    )
    return info

# Branch B: Added issuer validation
def validate_token(token):
    info = id_token.verify_oauth2_token(token, requests.Request())
    if info['iss'] != EXPECTED_ISSUER:  # Manual issuer check
        raise ValueError("Invalid issuer")
    return info
```

**Conflict Resolution**: Merge both validation checks. The resolution should include:
- Audience verification (client_id)
- Issuer verification (iss claim)
- Expiration validation (exp claim - done by library)
- Custom clock skew tolerance if needed

**Correct Merged Version**:
```python
def validate_token(token):
    try:
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=EXPECTED_AUDIENCE,
            clock_skew_in_seconds=5
        )
        if info['iss'] != EXPECTED_ISSUER:
            raise ValueError(f"Invalid issuer: {info['iss']}")
        return info
    except ValueError as e:
        raise AuthenticationError(f"Token validation failed: {str(e)}")
```

### 2.2 Allowed Domains/Emails List Conflicts

#### Pattern: Multiple Branches Adding/Modifying Allowlist

**Scenario**: One branch adds a new allowed domain, another adds allowed email addresses, creating a merge conflict in configuration.

**Example**:
```python
# Branch A: New domain whitelist
ALLOWED_DOMAINS = [
    "company.com",
    "partner1.com",  # Added
]

# Branch B: Email-based allowlist
ALLOWED_EMAILS = [
    "admin@company.com",
    "special_user@external.com",  # Added
]
```

**Merge Conflict Manifestation**:
- Both branches modifying same configuration variable
- Conflict markers in list initialization
- Potential accidental removal of entries when resolving

**Security Risk**:
- **Too Permissive**: Merging incorrectly to include unauthorized domains
- **Too Restrictive**: Accidentally excluding valid entries, blocking legitimate users
- **Logic Error**: Removing domain checks while keeping email checks (or vice versa) creates inconsistent security posture

**Resolution Strategy**:
1. Always merge toward MORE RESTRICTIVE (security-first principle)
2. If conflicting:
   - Keep ALL entries from both branches
   - Add comments with merge dates
   - Consider consolidating to centralized config (environment variables)
3. Validate that merged allowlist is intentional and complete

**Example Correct Resolution**:
```python
# Merged: All entries from both branches
ALLOWED_DOMAINS = [
    "company.com",
    "partner1.com",      # From Branch A
]

ALLOWED_EMAILS = [
    "admin@company.com",
    "special_user@external.com",  # From Branch B
]

# Use most restrictive: domain AND email checks
def is_authorized(token_info):
    domain = extract_domain(token_info['email'])
    return (
        domain in ALLOWED_DOMAINS and
        token_info['email'] in ALLOWED_EMAILS
    )
```

### 2.3 Token Validation Logic Refactoring Conflicts

#### Pattern: Simultaneous Refactoring + New Feature Addition

**Scenario**: Branch A refactors the validation logic into helper functions while Branch B adds new claim validation.

**Example Conflict**:
```python
# Branch A: Refactored
def extract_and_validate_token(event):
    token = _extract_token(event)
    return _validate_and_decode(token)

def _extract_token(event):
    # Implementation

def _validate_and_decode(token):
    # Implementation

# Branch B: New logic added
def extract_and_validate_token(event):
    token = extract_token_from_header(event)
    validate_token_format(token)
    info = validate_token(token)
    validate_custom_claims(info)  # NEW
    return info
```

**Merge Challenge**: Code structure changed in Branch A while functionality added in Branch B. Simple text merge is insufficient.

**Resolution Strategy**:
1. Adopt the more modular structure (Branch A's refactoring is better)
2. Incorporate new validation checks (Branch B's custom claims validation)
3. Ensure validation order is correct and atomic

**Correct Merged Version**:
```python
def extract_and_validate_token(event):
    """Extract, validate format, and decode token with all checks."""
    token = _extract_token(event)
    _validate_token_format(token)  # From B
    info = _validate_and_decode(token)  # From A
    _validate_custom_claims(info)  # From B
    return info

def _extract_token(event):
    """Extract token from Authorization header."""
    # Implementation

def _validate_token_format(token):
    """Validate token is JWT format."""
    # From Branch B

def _validate_and_decode(token):
    """Validate signature, expiration, audience, issuer."""
    # Implementation with all checks

def _validate_custom_claims(info):
    """Validate application-specific claims."""
    # From Branch B
```

### 2.4 IAM Policy Generation Conflicts

#### Pattern: Different Policy Resource Patterns

**Scenario**: One branch adds support for new API methods, another refactors resource pattern matching.

**Example**:
```python
# Branch A: New endpoints
def get_policy(principal_id, effect):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": [
                    "arn:aws:execute-api:*:*:*/*/GET/users",
                    "arn:aws:execute-api:*:*:*/*/GET/users/*",
                    "arn:aws:execute-api:*:*:*/*/POST/orders",  # NEW
                ]
            }]
        }
    }

# Branch B: Dynamic resource generation
def get_policy(principal_id, effect):
    methods = ["GET", "POST", "DELETE"]
    resources = [
        f"arn:aws:execute-api:*:*:*/*/{method}/*"
        for method in methods
    ]
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resources
            }]
        }
    }
```

**Security Risk**:
- **Too Permissive**: Merging to grant access to unintended endpoints
- **Pattern Override**: Dynamic patterns may accidentally allow wildcard access (`*/*/*/*`)
- **Logic Error**: Merging incompatible approaches creates inconsistent policy evaluation

**Resolution Strategy**:
1. Adopt the more specific (Branch A) unless there's clear reason for dynamic generation
2. If using dynamic patterns, ensure:
   - Whitelist of allowed methods is explicit and minimal
   - Resource patterns are as specific as possible (avoid wildcards)
   - Deny-by-default approach (only Allow what's necessary)
3. Validate merged policy against expected endpoints

**Correct Merged Approach**:
```python
def get_policy(principal_id, effect, role=None):
    """Generate IAM policy based on role."""
    # Define resources by role (security-first)
    resources_by_role = {
        "admin": [
            "arn:aws:execute-api:*:*:*/*/GET/users",
            "arn:aws:execute-api:*:*:*/*/GET/users/*",
            "arn:aws:execute-api:*:*:*/*/POST/orders",
            "arn:aws:execute-api:*:*:*/*/DELETE/orders/*",
        ],
        "user": [
            "arn:aws:execute-api:*:*:*/*/GET/users",
            "arn:aws:execute-api:*:*:*/*/POST/orders",
        ],
        "guest": [
            "arn:aws:execute-api:*:*:*/*/GET/users",
        ]
    }

    resources = resources_by_role.get(role, [])

    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resources
            }]
        }
    }
```

### 2.5 Error Handling and Logging Conflicts

#### Pattern: Different Exception Handling Strategies

**Scenario**: One branch adds detailed error logging for debugging, another adds structured error responses for security.

**Example**:
```python
# Branch A: Detailed logging
def lambda_handler(event, context):
    try:
        token = extract_token(event)
        info = validate_token(token)
        return build_policy(info['sub'], 'Allow')
    except Exception as e:
        print(f"Auth failed: {str(e)}")  # SECURITY RISK: May leak info
        return build_policy('unauthorized', 'Deny')

# Branch B: Structured responses
def lambda_handler(event, context):
    try:
        token = extract_token(event)
        info = validate_token(token)
        return build_policy(info['sub'], 'Allow')
    except TokenValidationError as e:
        logger.error("Token validation failed", extra={"error_type": "validation"})
        return build_policy('unauthorized', 'Deny')
    except Exception as e:
        logger.error("Unexpected error", extra={"error_type": "unexpected"})
        return build_policy('unauthorized', 'Deny')
```

**Security Risk**:
- Overly detailed error messages leak information about auth system
- Different exception handling creates inconsistent responses
- Logging sensitive data (tokens, user info) in production

**Resolution Strategy**:
1. Use structured logging with error categorization (Branch B approach)
2. Never log token contents, only error classification
3. Return generic Deny response to client regardless of error type
4. Use CloudWatch for secure detailed logging with proper retention

**Correct Merged Version**:
```python
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        token = extract_token(event)
        info = validate_token(token)
        logger.info("Auth successful", extra={"principal": info['sub']})
        return build_policy(info['sub'], 'Allow')
    except TokenValidationError:
        logger.warning("Token validation failed", extra={"error_type": "validation"})
        return build_policy('unauthorized', 'Deny')
    except TokenExtractionError:
        logger.warning("Token extraction failed", extra={"error_type": "extraction"})
        return build_policy('unauthorized', 'Deny')
    except Exception as e:
        logger.error("Unexpected error in authorizer", extra={
            "error_type": "unexpected",
            "error_class": type(e).__name__
        })
        return build_policy('unauthorized', 'Deny')

def extract_token(event):
    """Extract token from Authorization header."""
    auth_header = event.get('authorizationToken', '')
    if not auth_header.startswith('Bearer '):
        raise TokenExtractionError("Invalid authorization header format")
    return auth_header[7:]

def validate_token(token):
    """Validate token and return decoded claims."""
    try:
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=EXPECTED_AUDIENCE
        )
        return info
    except ValueError as e:
        raise TokenValidationError(f"Token validation failed") from e

class TokenValidationError(Exception):
    pass

class TokenExtractionError(Exception):
    pass
```

---

## 3. Security Implications of Incorrect Resolution

Understanding the security consequences of incorrect merge resolution is critical, as Lambda authorizers are a "critical path" component of API security.

### 3.1 Too Permissive Resolution

**Definition**: Merging in a way that grants access to more users or resources than intended.

**Symptoms**:
- Wildcard patterns not restricted (`*/*/*/*`)
- Missing validation checks from either branch
- Overly broad domain/email allowlists
- Accidentally removed deny logic

**Example Scenario**:
```python
# Incorrect merge result:
def get_policy(principal_id, effect):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": "Allow",  # WRONG: Always Allow, ignoring effect param
                "Resource": "arn:aws:execute-api:*:*:*/*/*"  # WRONG: Too broad
            }]
        }
    }
```

**Impact**:
- Unauthorized access to API endpoints
- Data breach: Users accessing resources beyond their role
- Privilege escalation: Non-admin accessing admin endpoints
- Compliance violation: Audit trails show access was granted

**Real-World Example**:
- Merging allowed_domains from multiple branches without realizing one includes a competitor's domain
- Accidentally removing issuer verification check while adding audience check
- Merging wildcard resources instead of specific endpoint patterns

### 3.2 Too Restrictive Resolution

**Definition**: Merging in a way that blocks legitimate users or functionality.

**Symptoms**:
- Missing allowlist entries from one or both branches
- Over-strict validation that rejects valid tokens
- Removed support for legitimate authentication methods
- Incompatible version conflicts blocking library import

**Example Scenario**:
```python
# Incorrect merge result - only kept Branch A's domains:
ALLOWED_DOMAINS = [
    "company.com",
    # Missing "partner1.com" from Branch B!
]

# Users from partner1.com now cannot authenticate
```

**Impact**:
- Service outage for legitimate users
- Support burden: Debugging "why can't I access the API?"
- Revenue loss: Users can't use the service
- Business partner issues: External users locked out

**Real-World Example**:
- New API client onboarded in one branch, accidentally removed during merge
- Token validation made stricter, rejecting tokens with valid but non-standard claims
- Requirements.txt conflict not properly resolved, google-auth fails to import

### 3.3 Logic Error / Authentication Bypass

**Definition**: Merging creates unintended logic flow that bypasses security checks.

**Symptoms**:
- Validation conditions combined with AND/OR incorrectly
- Early return before all checks complete
- Inverted boolean logic
- Try/catch blocks swallowing exceptions

**Example Scenario**:
```python
# Incorrect merge result - logic error:
def is_authorized(token_info):
    # Branch A check
    if token_info.get('email_verified') != True:
        return False

    # Branch B check
    if token_info.get('email').endswith('@company.com'):
        return True

    # WRONG: Returns True regardless of email_verified if domain matches!
    return False

# Attack: Attacker uses unverified email from any domain with 'company.com' substring
```

**Another Example - Exception Handling**:
```python
# Incorrect merge result:
def lambda_handler(event, context):
    try:
        token = extract_token(event)
        info = validate_token(token)  # Might raise ValueError
        return build_policy(info['sub'], 'Allow')
    except:  # WRONG: Catches all exceptions
        return build_policy('user', 'Allow')  # WRONG: Defaults to Allow!

# Attack: Invalid token causes exception, exception handler grants access
```

**Impact**:
- Complete authentication bypass
- Any user can access any endpoint
- Attacker gains unrestricted API access
- Critical security vulnerability

### 3.4 Why Authorizer Code is "Critical Path"

Lambda authorizers are critical path components because:

1. **First Line of Defense**: Every API request goes through the authorizer first
2. **Single Point of Failure**: One bug affects all API users
3. **Security Gateway**: Authorization decisions determine who can access what
4. **No "Slightly Wrong"**: Security decisions are binary (Allow/Deny) with no middle ground
5. **Hard to Debug in Production**: Authorizer failures can't be easily debugged with CloudWatch alone

**Merge Conflict Treatment**:
- Lambda authorizer conflicts should be treated with highest priority
- NEVER commit an authorizer merge without testing locally first
- ALWAYS run security validation tests after resolution
- Code review should verify all validation checks are present
- Test both Allow and Deny scenarios

---

## 4. OIDC Token Validation Patterns

OIDC (OpenID Connect) token validation is the core responsibility of Python Lambda authorizers using Google authentication.

### 4.1 google-auth `id_token.verify_oauth2_token()` Usage

#### Function Signature and Parameters

```python
from google.oauth2 import id_token
import google.auth.transport.requests

# Basic usage
claims = id_token.verify_oauth2_token(
    id_token_str,              # The JWT token string
    request,                   # google.auth.transport.requests.Request()
    audience=CLIENT_ID,        # Your OAuth 2.0 Client ID
    clock_skew_in_seconds=None # Optional: Allow clock skew for time differences
)
```

#### What `verify_oauth2_token()` Validates Automatically

The function validates:
1. **Signature**: Verifies the JWT signature using Google's public keys (fetched from JWKS endpoint)
2. **Expiration (exp)**: Checks that the token hasn't expired
3. **Issued At (iat)**: Validates the token was recently issued
4. **Audience (aud)**: Verifies the token's audience matches the provided CLIENT_ID
5. **Google's Public Keys**: Automatically fetches and caches from Google's JWKS endpoint

#### What You Must Validate Manually

1. **Issuer (iss)**: Verify token was issued by expected Google OAuth endpoint
2. **Email Verification (email_verified)**: Confirm email claim if using email-based authorization
3. **Hd Claim (Hosted Domain)**: For Google Workspace, verify hd claim matches organization
4. **Custom Claims**: Application-specific claims (roles, permissions, etc.)

#### Common Implementation Pattern

```python
def validate_id_token(token_str):
    """Validate Google ID token and return claims."""
    try:
        # id_token.verify_oauth2_token validates signature, exp, aud
        claims = id_token.verify_oauth2_token(
            token_str,
            google.auth.transport.requests.Request(),
            audience=os.environ['GOOGLE_CLIENT_ID'],
            clock_skew_in_seconds=10  # Allow 10-second clock skew
        )

        # Manual validations
        if claims['iss'] not in [
            'https://accounts.google.com',
            'https://accounts.google.com/'
        ]:
            raise ValueError(f"Invalid issuer: {claims['iss']}")

        # If using email-based authorization
        if not claims.get('email_verified'):
            raise ValueError("Email not verified")

        # For Google Workspace organizations
        if 'hd' in claims:  # hd = hosted domain
            if claims['hd'] != 'company.com':
                raise ValueError(f"Invalid domain: {claims['hd']}")

        return claims

    except ValueError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise AuthenticationError(f"Invalid token")
```

**Reference**: [google.oauth2.id_token module documentation](https://googleapis.dev/python/google-auth/latest/reference/google.oauth2.id_token.html)

### 4.2 Token Claims Validation

#### Standard OIDC Claims

```python
# After successful id_token.verify_oauth2_token(), claims include:

claims = {
    'iss': 'https://accounts.google.com',           # Issuer
    'sub': '118364335991896786099',                 # Subject (unique user ID)
    'aud': 'CLIENT_ID.apps.googleusercontent.com',  # Audience
    'iat': 1234567890,                              # Issued at (timestamp)
    'exp': 1234571490,                              # Expiration (timestamp)
    'email': 'user@gmail.com',                      # User email
    'email_verified': True,                         # Email verified by provider
    'name': 'John Doe',                             # User full name
    'given_name': 'John',                           # First name
    'family_name': 'Doe',                           # Last name
    'picture': 'https://lh3.googleusercontent.com/...',  # Profile picture URL
    'locale': 'en',                                 # User locale
    # For Google Workspace:
    'hd': 'company.com',                           # Hosted domain
    'azp': 'CLIENT_ID.apps.googleusercontent.com'  # Authorized party (who it was issued to)
}
```

#### Custom Claim Validation Patterns

```python
def validate_claims(claims):
    """Validate application-specific claim requirements."""

    # Email domain validation (more specific than hd)
    email = claims.get('email', '')
    if not email.endswith('@company.com'):
        raise ValueError(f"Invalid email domain: {email}")

    # Email allowlist validation
    ALLOWED_EMAILS = {
        'admin@company.com',
        'service-account@company.com',
    }
    if email not in ALLOWED_EMAILS:
        raise ValueError(f"Email not in allowlist: {email}")

    # Role/group claims (if using custom claims in token)
    # Note: Google doesn't add custom claims to ID tokens by default
    # You would need to use Google Claims mappings or Access tokens instead
    roles = claims.get('roles', [])
    if 'authorized_user' not in roles:
        raise ValueError("User not in authorized_user role")

    return True
```

### 4.3 Audience Verification

#### Why Audience Verification is Critical

The audience (aud) claim is crucial because it identifies the intended recipient of the token. Without verifying it:
- Your application accepts ANY valid token issued by Google
- An attacker could use a token issued for a different app to impersonate a user on your app
- This is a critical authentication bypass vulnerability

#### Correct Audience Verification

```python
import os

EXPECTED_AUDIENCE = os.environ['GOOGLE_CLIENT_ID']  # e.g., 'CLIENT_ID.apps.googleusercontent.com'

def verify_audience(token_str):
    """Verify token audience matches expected client ID."""
    claims = id_token.verify_oauth2_token(
        token_str,
        google.auth.transport.requests.Request(),
        audience=EXPECTED_AUDIENCE  # REQUIRED: Explicitly specify
    )
    # If audience doesn't match, verify_oauth2_token raises ValueError
    return claims

# WRONG - Don't do this:
def verify_audience_wrong(token_str):
    claims = id_token.verify_oauth2_token(
        token_str,
        google.auth.transport.requests.Request()
        # audience=None  # WRONG: No audience check!
    )
    return claims
```

#### Audience Mismatch Scenarios

```python
# Scenario 1: Token issued for different app
# Token aud: 'OTHER_APP_ID.apps.googleusercontent.com'
# Expected: 'MY_APP_ID.apps.googleusercontent.com'
# Result: ValueError raised (CORRECT)

# Scenario 2: Token issued for same app (correct)
# Token aud: 'MY_APP_ID.apps.googleusercontent.com'
# Expected: 'MY_APP_ID.apps.googleusercontent.com'
# Result: Claims returned (CORRECT)

# Scenario 3: Missing audience in token
# Token aud: None
# Expected: 'MY_APP_ID.apps.googleusercontent.com'
# Result: ValueError raised (CORRECT)
```

### 4.4 Issuer Verification

#### Why Issuer Verification Matters

The issuer (iss) claim identifies who issued the token. Google has two valid issuer endpoints:
- `https://accounts.google.com`
- `https://accounts.google.com/` (with trailing slash)

Verifying the issuer prevents accepting tokens from unauthorized OAuth providers.

#### Correct Issuer Verification

```python
VALID_ISSUERS = {
    'https://accounts.google.com',
    'https://accounts.google.com/',
}

def verify_issuer(claims):
    """Verify token was issued by Google."""
    issuer = claims.get('iss')
    if issuer not in VALID_ISSUERS:
        raise ValueError(f"Invalid issuer: {issuer}")
    return True

def validate_and_return_claims(token_str):
    """Complete token validation with all checks."""
    # This validates signature, exp, aud
    claims = id_token.verify_oauth2_token(
        token_str,
        google.auth.transport.requests.Request(),
        audience=os.environ['GOOGLE_CLIENT_ID'],
        clock_skew_in_seconds=10
    )

    # Manual issuer validation
    verify_issuer(claims)

    # Email verification validation
    if not claims.get('email_verified'):
        raise ValueError("Email not verified by provider")

    # Domain validation (for Google Workspace)
    if 'hd' in claims and claims['hd'] != 'company.com':
        raise ValueError(f"Invalid domain: {claims['hd']}")

    return claims
```

#### Issuer Format Considerations

```python
# Be strict about issuer format
# GOOD - Accept only known good formats
GOOD_ISSUERS = {'https://accounts.google.com', 'https://accounts.google.com/'}

# BAD - Too permissive
BAD_ISSUERS = ['accounts.google.com', '*google.com', 'google.com']

# Avoid substring matching or startswith:
# WRONG: if issuer.startswith('accounts.google'):
# CORRECT: if issuer in VALID_ISSUERS
```

---

## 5. Common Conflict Scenarios

This section documents real-world conflict patterns that occur frequently in Python Lambda authorizer code.

### 5.1 Both Branches Add New Allowed Domains

#### Scenario Description

Two teams work on different features:
- Team A: Adds new business partner (partner1.com)
- Team B: Adds new customer integration (partner2.com)

Both modify the allowed domains configuration, creating a merge conflict.

#### How Conflict Manifests

```
CONFLICT in authorizer.py:
<<<<<<< HEAD
ALLOWED_DOMAINS = [
    'company.com',
    'partner1.com',  # Team A added
]
||||||| merged-common-ancestor
ALLOWED_DOMAINS = [
    'company.com',
]
=======
ALLOWED_DOMAINS = [
    'company.com',
    'partner2.com',  # Team B added
]
>>>>>>> feature/partner2-integration
```

#### Incorrect Resolution (Too Restrictive)

```python
# Taking only HEAD's changes
ALLOWED_DOMAINS = [
    'company.com',
    'partner1.com',
]
# Result: partner2.com users can't authenticate
```

#### Correct Resolution

```python
# Merge both domain additions
ALLOWED_DOMAINS = [
    'company.com',
    'partner1.com',      # From Team A
    'partner2.com',      # From Team B
]
```

#### Validation After Merge

```python
# Test that both partners' users can authenticate
import pytest

def test_partner1_domain_allowed():
    token_info = {'email': 'user@partner1.com', 'email_verified': True}
    assert is_authorized(token_info)

def test_partner2_domain_allowed():
    token_info = {'email': 'user@partner2.com', 'email_verified': True}
    assert is_authorized(token_info)

def test_unauthorized_domain_rejected():
    token_info = {'email': 'user@attacker.com', 'email_verified': True}
    assert not is_authorized(token_info)
```

### 5.2 One Branch Refactors Auth Logic While Other Adds New Checks

#### Scenario Description

- Team A: Refactors token validation into reusable helper functions
- Team B: Adds new claim validation (role-based access control)

Both changes are valuable but conflict in code structure.

#### How Conflict Manifests

```
CONFLICT: Structure of validation logic differs significantly
Branch A: Modular helper functions
Branch B: Additional validation checks
```

#### Branch A: Refactored Structure

```python
def extract_token(event):
    auth_header = event.get('authorizationToken', '')
    return auth_header[7:]  # Remove 'Bearer '

def validate_token(token):
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience=CLIENT_ID
    )

def lambda_handler(event, context):
    token = extract_token(event)
    claims = validate_token(token)
    return build_policy(claims['sub'], 'Allow')
```

#### Branch B: New Validation

```python
def lambda_handler(event, context):
    token = event['authorizationToken'][7:]
    claims = id_token.verify_oauth2_token(token, requests.Request(), audience=CLIENT_ID)

    # NEW: Role validation
    if 'roles' not in claims or 'api_user' not in claims['roles']:
        return build_policy('user', 'Deny')

    # NEW: Email domain check
    email = claims.get('email', '')
    if not email.endswith('@company.com'):
        return build_policy('user', 'Deny')

    return build_policy(claims['sub'], 'Allow')
```

#### Correct Merge

```python
def extract_token(event):
    """Extract token from Authorization header."""
    auth_header = event.get('authorizationToken', '')
    if not auth_header.startswith('Bearer '):
        raise ValueError("Invalid authorization header")
    return auth_header[7:]

def validate_token(token):
    """Validate token signature and claims."""
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience=CLIENT_ID
    )

def validate_authorization(claims):
    """Validate authorization-specific claims."""
    # From Branch B
    if 'roles' not in claims or 'api_user' not in claims['roles']:
        raise AuthorizationError("User not in api_user role")

    email = claims.get('email', '')
    if not email.endswith('@company.com'):
        raise AuthorizationError("Email domain not authorized")

    return True

def lambda_handler(event, context):
    """Main authorizer handler."""
    try:
        token = extract_token(event)
        claims = validate_token(token)
        validate_authorization(claims)
        return build_policy(claims['sub'], 'Allow')
    except (ValueError, AuthorizationError) as e:
        logger.warning(f"Authorization failed: {type(e).__name__}")
        return build_policy('unauthorized', 'Deny')
```

### 5.3 Environment Variable Changes for Auth Configuration

#### Scenario Description

- Team A: Refactors to read issuer from environment variable
- Team B: Adds new audience validation with its own env var

Conflict in how configuration is loaded and used.

#### Branch A: Configurable Issuer

```python
import os

def get_issuer():
    return os.environ.get('OIDC_ISSUER', 'https://accounts.google.com')

def validate_issuer(claims):
    expected_issuer = get_issuer()
    if claims['iss'] != expected_issuer:
        raise ValueError(f"Invalid issuer")
    return True
```

#### Branch B: Multiple Config Variables

```python
import os

def validate_token(token):
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience=os.environ['OAUTH2_AUDIENCE'],  # NEW
        clock_skew_in_seconds=int(os.environ.get('TOKEN_CLOCK_SKEW', '10'))  # NEW
    )
```

#### Correct Merge with Consolidated Config

```python
import os
from dataclasses import dataclass

@dataclass
class AuthConfig:
    """OIDC authentication configuration."""
    audience: str
    issuer: str
    clock_skew: int
    allowed_domains: list

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            audience=os.environ['OAUTH2_AUDIENCE'],
            issuer=os.environ.get('OIDC_ISSUER', 'https://accounts.google.com'),
            clock_skew=int(os.environ.get('TOKEN_CLOCK_SKEW', '10')),
            allowed_domains=os.environ.get('ALLOWED_DOMAINS', 'company.com').split(',')
        )

# Load once at module level
CONFIG = AuthConfig.from_env()

def validate_token(token):
    """Validate token with consolidated config."""
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience=CONFIG.audience,
        clock_skew_in_seconds=CONFIG.clock_skew
    )

def validate_issuer(claims):
    """Validate issuer from config."""
    if claims['iss'] != CONFIG.issuer:
        raise ValueError(f"Invalid issuer")

def validate_domain(claims):
    """Validate email domain from config."""
    email = claims.get('email', '')
    domain = email.split('@')[1] if '@' in email else ''
    if domain not in CONFIG.allowed_domains:
        raise ValueError(f"Domain not allowed: {domain}")
```

### 5.4 Dependency Version Changes (google-auth Library)

#### Scenario Description

- Team A: Upgrades google-auth from 2.20.0 to 2.30.0 for security fix
- Team B: Keeps google-auth at 2.25.0, adds pyopenssl for TLS support

Conflicting versions in requirements.txt.

#### How Conflict Manifests

```
CONFLICT in requirements.txt:
<<<<<<< HEAD
google-auth==2.30.0
pyopenssl==23.2.0
cryptography==41.0.0
||||||| merged-common-ancestor
google-auth==2.20.0
cryptography==40.0.0
=======
google-auth==2.25.0
pyopenssl==23.2.0
cryptography==40.0.0
>>>>>>> feature/tls-support
```

#### Why This Matters

Different google-auth versions may have:
- Different behavior in `id_token.verify_oauth2_token()`
- Updated cryptography dependencies
- Security fixes or regressions
- API changes for clock skew handling or other parameters

#### Correct Resolution (Security-First)

```
# Always merge toward NEWER security-fixed version
google-auth==2.30.0

# Verify cryptography compatibility
# Note: pyopenssl and enterprise_cert extras conflict
# Use only what's necessary
cryptography==41.0.0
```

#### Resolution Strategy for Version Conflicts

```
1. Identify the most recent STABLE version mentioned (2.30.0)
2. Check if it has security patches
3. Verify that newer version supports all features from both branches
4. Test locally with merged version before committing

# Correct merged requirements.txt
google-auth==2.30.0  # Use newer security-fixed version
requests==2.31.0
```

#### Testing Merged Dependencies

```bash
# Create test environment with merged requirements
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# Run minimal test
python -c "
from google.oauth2 import id_token
import google.auth.transport.requests
print('Import successful')
print(f'google-auth version: {id_token.__name__}')
"

# Run actual authorizer test
python -m pytest tests/test_authorizer.py -v
```

---

## 6. Resolution Strategies

Systematic approach to resolving Lambda authorizer merge conflicts safely and securely.

### 6.1 Security-First Principle: Always Merge Toward More Restrictive

#### Core Strategy

When resolving authorizer conflicts, the guiding principle is **deny by default, allow by explicit configuration**.

```python
# WRONG: Default to Allow
def is_authorized(user):
    if user.has_paid_subscription():
        return True  # If they have subscription, allow
    return True  # DEFAULT ALLOW - if we're unsure, allow anyway

# CORRECT: Default to Deny
def is_authorized(user):
    # Check all conditions
    if not user.email_verified:
        return False
    if user.email.split('@')[1] not in ALLOWED_DOMAINS:
        return False
    if 'api_user' not in user.roles:
        return False

    return True  # Only Allow if ALL checks pass
```

#### Conflict Resolution Decision Tree

```
Is there a conflict in allowed domains/emails?
├─ YES: Include ALL entries from both branches
│       (More restrictive: more validation required)
└─ NO: Continue

Is there a conflict in validation logic?
├─ YES: Keep ALL checks from both branches
│       (More restrictive: more validation checks)
└─ NO: Continue

Is there a conflict in IAM policy resources?
├─ YES: Keep MORE SPECIFIC resources
│       (More restrictive: fewer allowed endpoints)
└─ NO: Continue

Is there a conflict in error handling?
├─ YES: Use approach that defaults to Deny
│       (More restrictive: fail securely)
└─ NO: Continue

Is there a version conflict?
├─ YES: Use NEWER stable version with security fixes
│       (More restrictive: more security checks)
└─ NO: MERGE COMPLETE
```

#### Examples of Security-First Decisions

```python
# Conflict in email validation
# Branch A: check email_verified
# Branch B: check email domain
# Resolution: Do BOTH (AND logic, more restrictive)
if not claims.get('email_verified') or \
   not claims.get('email', '').endswith('@company.com'):
    return False

# Conflict in resource patterns
# Branch A: arn:aws:execute-api:*:*:*/*/GET/users/*
# Branch B: arn:aws:execute-api:*:*:*/*/*
# Resolution: Use Branch A (more specific, less permissive)

# Conflict in exception handling
# Branch A: Catch specific exceptions, Deny
# Branch B: Catch all exceptions, Allow
# Resolution: Use Branch A (fail securely)
```

### 6.2 Validation: Testing Authorizer Locally

#### Local Testing Setup with SAM CLI

```bash
# Prerequisites
pip install aws-sam-cli

# Create SAM template for local testing (template.yaml)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2.0

Globals:
  Function:
    Timeout: 30
    MemorySize: 128

Resources:
  AuthorizerFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: authorizer.lambda_handler
      Runtime: python3.11
      Environment:
        Variables:
          GOOGLE_CLIENT_ID: !Ref GoogleClientIdParameter
          ALLOWED_DOMAINS: 'company.com,partner.com'

  TestApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: test
      Auth:
        Authorizers:
          AuthorizerFunction:
            FunctionArn: !GetAtt AuthorizerFunction.Arn

Parameters:
  GoogleClientIdParameter:
    Type: String
    Default: 'your-client-id.apps.googleusercontent.com'

# Run local API Gateway with authorizer
sam local start-api --parameter-overrides GoogleClientIdParameter=your-client-id.apps.googleusercontent.com
```

**Reference**: [AWS SAM CLI local testing for Lambda authorizers](https://aws.amazon.com/about-aws/whats-new/2023/04/aws-sam-cli-local-testing-support-api-gateway-lambda-authorizers/)

#### Unit Testing Authorizer Locally

```python
import pytest
import os
from unittest.mock import patch, MagicMock
from authorizer import lambda_handler, validate_token, validate_authorization

# Mock environment variables
@pytest.fixture
def auth_env():
    with patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test-client-id.apps.googleusercontent.com',
        'ALLOWED_DOMAINS': 'company.com,partner.com'
    }):
        yield

class TestTokenValidation:
    """Test token validation logic."""

    @patch('authorizer.id_token.verify_oauth2_token')
    def test_valid_token_with_allowed_domain(self, mock_verify):
        """Test that valid token with allowed domain is accepted."""
        mock_verify.return_value = {
            'sub': 'user123',
            'email': 'user@company.com',
            'email_verified': True,
            'iss': 'https://accounts.google.com',
        }

        claims = validate_token('valid-token')
        assert claims['sub'] == 'user123'
        assert claims['email'] == 'user@company.com'

    @patch('authorizer.id_token.verify_oauth2_token')
    def test_expired_token_raises_error(self, mock_verify):
        """Test that expired token raises ValueError."""
        mock_verify.side_effect = ValueError("Token expired")

        with pytest.raises(ValueError):
            validate_token('expired-token')

    @patch('authorizer.id_token.verify_oauth2_token')
    def test_invalid_audience_raises_error(self, mock_verify):
        """Test that mismatched audience raises error."""
        mock_verify.side_effect = ValueError("Audience mismatch")

        with pytest.raises(ValueError):
            validate_token('wrong-audience-token')

class TestAuthorization:
    """Test authorization logic."""

    def test_allowed_domain_authorized(self):
        """Test user from allowed domain is authorized."""
        claims = {
            'email': 'user@company.com',
            'email_verified': True,
            'roles': ['api_user'],
            'iss': 'https://accounts.google.com',
        }
        assert validate_authorization(claims)

    def test_unverified_email_denied(self):
        """Test unverified email is denied."""
        claims = {
            'email': 'user@company.com',
            'email_verified': False,  # NOT verified
            'roles': ['api_user'],
        }
        with pytest.raises(ValueError):
            validate_authorization(claims)

    def test_unauthorized_domain_denied(self):
        """Test unauthorized domain is denied."""
        claims = {
            'email': 'user@attacker.com',
            'email_verified': True,
            'roles': ['api_user'],
        }
        with pytest.raises(ValueError):
            validate_authorization(claims)

    def test_missing_role_denied(self):
        """Test missing api_user role is denied."""
        claims = {
            'email': 'user@company.com',
            'email_verified': True,
            'roles': ['other_role'],  # Missing 'api_user'
        }
        with pytest.raises(ValueError):
            validate_authorization(claims)

class TestLambdaHandler:
    """Test complete handler flow."""

    @patch('authorizer.validate_token')
    @patch('authorizer.validate_authorization')
    @patch('authorizer.build_policy')
    def test_authorized_request(self, mock_policy, mock_auth, mock_token):
        """Test handler grants Allow for valid request."""
        mock_token.return_value = {
            'sub': 'user123',
            'email': 'user@company.com',
            'email_verified': True,
            'roles': ['api_user'],
        }
        mock_auth.return_value = True
        mock_policy.return_value = {'principalId': 'user123', 'policyDocument': {}}

        response = lambda_handler({
            'authorizationToken': 'Bearer valid-token'
        }, {})

        assert response['principalId'] == 'user123'
        mock_policy.assert_called_once_with('user123', 'Allow')

    @patch('authorizer.validate_token')
    def test_invalid_token_denied(self, mock_token):
        """Test handler denies invalid token."""
        mock_token.side_effect = ValueError("Invalid token")

        response = lambda_handler({
            'authorizationToken': 'Bearer invalid-token'
        }, {})

        assert response['policyDocument']['Statement'][0]['Effect'] == 'Deny'

# Run tests
# pytest tests/test_authorizer.py -v --tb=short
```

#### Integration Testing

```python
# tests/test_authorizer_integration.py
import json
import os
import requests
from datetime import datetime, timedelta
import jwt

class TestAuthorizerIntegration:
    """Integration tests against local API Gateway."""

    @classmethod
    def setup_class(cls):
        """Setup: Start local SAM API."""
        # Assumes: sam local start-api running on localhost:3000
        cls.api_url = 'http://localhost:3000'
        cls.secret = 'test-secret'

    def create_test_token(self, claims, secret=None, expiry_hours=1):
        """Create a test JWT token."""
        secret = secret or self.secret
        payload = {
            'iss': 'https://accounts.google.com',
            'sub': 'test-user',
            'aud': os.environ['GOOGLE_CLIENT_ID'],
            'iat': datetime.utcnow().timestamp(),
            'exp': (datetime.utcnow() + timedelta(hours=expiry_hours)).timestamp(),
            **claims
        }
        return jwt.encode(payload, secret, algorithm='HS256')

    def test_valid_request_allowed(self):
        """Test valid request is allowed."""
        token = self.create_test_token({
            'email': 'user@company.com',
            'email_verified': True,
            'roles': ['api_user']
        })

        response = requests.get(
            f'{self.api_url}/users',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200

    def test_invalid_domain_denied(self):
        """Test request from invalid domain is denied."""
        token = self.create_test_token({
            'email': 'user@attacker.com',
            'email_verified': True,
            'roles': ['api_user']
        })

        response = requests.get(
            f'{self.api_url}/users',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 403

    def test_expired_token_denied(self):
        """Test expired token is denied."""
        token = self.create_test_token(
            {'email': 'user@company.com'},
            expiry_hours=-1  # Already expired
        )

        response = requests.get(
            f'{self.api_url}/users',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 401

    def test_missing_token_denied(self):
        """Test request without token is denied."""
        response = requests.get(f'{self.api_url}/users')
        assert response.status_code == 401
```

### 6.3 Post-Merge Verification Checklist

After resolving a Lambda authorizer merge conflict, verify:

#### Security Checks

- [ ] All allowed domains from both branches are included
- [ ] All allowed emails from both branches are included
- [ ] All validation checks from both branches are present
- [ ] Email verification is enforced (if required)
- [ ] Token issuer is verified
- [ ] Token audience matches expected client ID
- [ ] IAM policy resources are as specific as possible (no broad wildcards)
- [ ] Default policy effect is Deny (not Allow)
- [ ] Exception handling never grants Access on error
- [ ] Sensitive data not logged (tokens, passwords, full error messages)

#### Functionality Checks

- [ ] Requirements.txt dependencies resolve without conflicts
- [ ] google-auth imports successfully
- [ ] id_token.verify_oauth2_token() works with merged config
- [ ] All custom validation functions execute
- [ ] Token with all valid claims passes authorization
- [ ] Token with any invalid claim is denied
- [ ] Expired tokens are denied
- [ ] Tokens with wrong audience are denied
- [ ] Tokens from wrong issuer are denied

#### Code Quality Checks

- [ ] No merge conflict markers remain
- [ ] Code formatting is consistent
- [ ] All imports are present
- [ ] No circular imports
- [ ] Lambda function timeout is appropriate (>5 seconds, <30 seconds)
- [ ] Memory allocation is appropriate (>128MB)

#### Testing Checks

- [ ] Unit tests pass locally
- [ ] Integration tests pass with local SAM CLI
- [ ] Test coverage includes both Allow and Deny paths
- [ ] Security-critical paths have specific test cases
- [ ] CloudWatch logs show expected entries for test runs

---

## 7. Python-Specific Merge Considerations

Python-specific factors that affect Lambda authorizer merge resolution.

### 7.1 requirements.txt / Pipfile Conflicts

#### requirements.txt Conflict Resolution

```
# Pattern 1: Both branches pin different versions
<<<<<<< HEAD
google-auth==2.30.0
requests==2.31.0
=======
google-auth==2.25.0
requests==2.28.0
>>>>>>> feature/auth-update

# Resolution: Use NEWER versions that include security fixes
google-auth==2.30.0
requests==2.31.0
```

#### Pipfile Lock Issues

```
# If using Pipenv with Pipfile.lock:
# 1. Resolve text conflicts in Pipfile
# 2. Regenerate Pipfile.lock:
#
pipenv lock --python 3.11 --requirements > requirements.txt

# Verify transitive dependencies
pipenv graph | grep google-auth
```

#### Common Version Conflict Scenarios

```python
# Scenario 1: Security update in one branch
# Branch A: google-auth==2.30.0  (has security fix)
# Branch B: google-auth==2.25.0  (unpatched)
# Resolution: google-auth==2.30.0

# Scenario 2: Extra dependencies differ
# Branch A: google-auth[pyopenssl]==2.30.0
# Branch B: google-auth==2.30.0
# Resolution: Use version without extras if not needed
# If TLS support needed: google-auth[pyopenssl]==2.30.0

# Scenario 3: Transitive dependency conflict
# Branch A: google-auth==2.30.0  → cryptography==41.0.0
# Branch B: pyopenssl==23.2.0    → cryptography==40.0.0
# Resolution: Explicitly pin cryptography==41.0.0
google-auth==2.30.0
cryptography==41.0.0
```

#### Verification Commands

```bash
# Check resolved dependencies
pip install -r requirements.txt --dry-run

# Test imports
python -c "
from google.oauth2 import id_token
from google.auth.transport import requests
print('All imports successful')
"

# Check for version conflicts
pip check  # Reports conflicting dependencies
```

### 7.2 Lambda Layer Conflicts

#### What are Lambda Layers?

Lambda layers allow you to package libraries, custom code, or other content to use with your Lambda functions. Layers help manage shared dependencies and reduce deployment package size.

#### Layer Structure

```
lambda_layer.zip
├── python/
│   ├── lib/
│   │   └── python3.11/
│   │       └── site-packages/
│   │           ├── google/
│   │           │   ├── oauth2/
│   │           │   └── auth/
│   │           └── requests/
│   └── requirements.txt
└── Pipfile
```

#### Merge Conflict in Layers

```
Scenario: Both branches add dependencies to shared layer
Branch A: Adds google-auth to layer
Branch B: Adds cryptography to layer

Conflict: Which dependencies are in layer vs. function deployment package?

Risk: If google-auth in layer and cryptography in function package,
      version mismatch causes import failure
```

#### Resolution Strategy for Layer Conflicts

```python
# Best Practice: Keep all auth dependencies in ONE place

# Option 1: All in Lambda Layer (Recommended)
# layer/requirements.txt:
google-auth==2.30.0
requests==2.31.0
cryptography==41.0.0

# Function deployment package: Empty (or only application code)

# Option 2: All in Function Deployment Package
# function/requirements.txt:
google-auth==2.30.0
requests==2.31.0
cryptography==41.0.0

# Lambda layers: None (except AWS SDK, preinstalled)

# WRONG: Split dependencies
# Layer has: google-auth, requests
# Function has: cryptography
# Risk: Version mismatch, import errors
```

#### Layer Precedence Rules

When resolving layer conflicts, remember:
- **Functions layers have precedence over runtime-included libraries**
- If you deploy your own version of a library, it overrides the runtime version
- **Boto3 dependency conflict**: If you include Boto3 in layer/function, you must also include all its dependencies

```python
# Dangerous pattern - splits dependencies
# Layer 1: google-auth==2.30.0
# Layer 2: cryptography==40.0.0  (too old, incompatible!)
# Result: Runtime error or auth failure

# Safe pattern - explicit pinning
# Layer: Consolidates all versions
# requirements.txt:
google-auth==2.30.0  # includes cryptography as dependency
requests==2.31.0
# Generates transitive dependency: cryptography==41.0.0 (compatible)
```

**Reference**: [AWS Lambda Layers for Python](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html)

### 7.3 Python Import Order and Module-Level Conflicts

#### Import Order Matters for Environment Variables

```python
# WRONG: Environment variables loaded at import time
import os
CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']  # Fails if not set during import

# CORRECT: Load at function invocation time
def lambda_handler(event, context):
    client_id = os.environ['GOOGLE_CLIENT_ID']  # Loads when function runs
    ...
```

#### Merge Conflict in Import Statements

```
CONFLICT:
<<<<<<< HEAD
from google.oauth2 import id_token
import google.auth.transport.requests as requests
=======
from google.oauth2 import id_token
from google.auth.transport.requests import Request
>>>>>>> feature/refactor-imports
```

**Resolution**:
```python
# Correct approach combines both styles appropriately
from google.oauth2 import id_token
import google.auth.transport.requests
from google.auth.transport.requests import Request

# Use Request class for instantiation
request_instance = Request()

# Or use the module directly
requests = google.auth.transport.requests
```

#### Circular Import Prevention

```python
# authorizer.py
# ✓ GOOD: Import at module level
from google.oauth2 import id_token

# ✓ GOOD: Import inside function if needed
def validate_token(token):
    import requests  # Local import when needed
    ...

# ✗ BAD: Circular import
# authorizer.py imports from utils.py
# utils.py imports from authorizer.py
# Result: ImportError or None attributes
```

#### Common Module-Level Merge Conflict

```python
# Conflict pattern: Different import styles after refactor
# Branch A: Clean imports at top
# Branch B: Dynamic imports in functions

# RESOLUTION: Standardize on top-level imports for deterministic behavior
# Top of authorizer.py
import os
import logging
from google.oauth2 import id_token
import google.auth.transport.requests
import requests

logger = logging.getLogger()

# Module-level configuration (loaded when function is initialized)
CONFIG = {
    'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
    'allowed_domains': os.environ.get('ALLOWED_DOMAINS', '').split(','),
    'clock_skew': int(os.environ.get('TOKEN_CLOCK_SKEW', '10')),
}

def lambda_handler(event, context):
    # Use CONFIG loaded at module init time
    ...
```

---

## 8. Summary and Key Takeaways

### Critical Principles

1. **Security-First Merging**: Always merge toward MORE RESTRICTIVE authorization rules
2. **Fail Securely**: Default to Deny when uncertain; never default to Allow
3. **Complete Validation**: Merge ALL checks from both branches (AND logic, not OR)
4. **Explicit Configuration**: Use environment variables; avoid hardcoded defaults
5. **Comprehensive Testing**: Test both Allow and Deny paths locally before deployment

### Pre-Merge Checklist

- [ ] Both branches' allowed domains/emails are documented
- [ ] Both branches' validation checks are understood
- [ ] Dependency version conflicts are identified
- [ ] Security implications of each approach are clear

### Post-Merge Verification

- [ ] No merge conflict markers remain
- [ ] All imports resolve
- [ ] Unit tests pass
- [ ] Integration tests pass with SAM CLI
- [ ] Security checks verified (domain, email, token validation)
- [ ] IAM policy resources are specific
- [ ] Default effect is Deny, not Allow

### When in Doubt

1. **Merge toward More Restrictive**: If unsure which check to keep, keep both
2. **Test Locally**: Use SAM CLI for local testing before deploying
3. **Code Review**: Have security-focused review for auth code
4. **Fail Safely**: Default to Deny; log carefully without exposing secrets

---

## References and Documentation

- [AWS API Gateway Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [google.oauth2.id_token module documentation](https://googleapis.dev/python/google-auth/latest/reference/google.oauth2.id_token.html)
- [Verify Google ID tokens](https://developers.google.com/identity/gsi/web/guides/verify-google-id-token)
- [OIDC Token Validation Best Practices](https://curity.io/resources/learn/validating-an-id-token/)
- [AWS SAM CLI Local Testing for Lambda Authorizers](https://aws.amazon.com/about-aws/whats-new/2023/04/aws-sam-cli-local-testing-support-api-gateway-lambda-authorizers/)
- [AWS Lambda Python Layers](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html)
- [google-auth PyPI Package](https://pypi.org/project/google-auth/)
- [Security Best Practices in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/security-best-practices.html)

---

**Document Version**: 1.0
**Last Updated**: April 2026
**Classification**: Technical Research
**Audience**: Software Engineers, DevOps, Security Teams
