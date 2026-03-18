# Cross-Domain Vulnerability Detection Patterns

Individual domain auditors analyze in isolation. This reference defines vulnerability chains that span multiple domains and the correlation patterns the coordinator uses to detect them in post-synthesis.

## Why This Matters

Research indicates 30-50% of critical vulnerabilities span multiple security domains. A single-domain auditor sees only its piece. The coordinator's post-synthesis phase catches what individual auditors miss.

## Top 10 Vulnerability Chains

### Chain 1: Auth Bypass + SQL Injection (CVSS 9.8)
- **Pattern:** User input flows through SQL query that returns auth result
- **Detection:** auth-session auditor finds weak auth AND injection auditor finds SQLi in same module
- **Correlation type:** Source-Sink Misalignment
- **Example:** Login query uses `SELECT * FROM users WHERE name='${input}'` — bypasses auth AND extracts data

### Chain 2: IDOR + Business Logic Bypass (CVSS 9.5)
- **Pattern:** Can read others' objects AND no ownership check in business workflow
- **Detection:** access-control finds IDOR AND business-logic finds missing ownership validation
- **Correlation type:** Assumption Violation
- **Example:** User can view another user's order AND change its status without being the owner

### Chain 3: CORS Misconfiguration + IDOR (CVSS 9.2)
- **Pattern:** Wildcard CORS allows cross-origin requests to IDOR-vulnerable endpoints
- **Detection:** config-headers finds `Access-Control-Allow-Origin: *` AND access-control finds IDOR
- **Correlation type:** Boundary Crossing
- **Example:** Any website can make authenticated requests to fetch other users' data

### Chain 4: XXE + SSRF (CVSS 9.1)
- **Pattern:** XML external entities can trigger server-side requests
- **Detection:** input-output finds XXE AND api-endpoint flags SSRF risk
- **Correlation type:** Compound Sink Reachability
- **Example:** XML upload with external entity pointing to internal metadata API

### Chain 5: Race Condition + Privilege Escalation (CVSS 9.0)
- **Pattern:** TOCTOU gap in permission check allows role modification mid-request
- **Detection:** concurrency auditor finds race condition AND access-control finds privilege escalation vector
- **Correlation type:** Prerequisite Met
- **Example:** Check role → (race window) → role updated → action executes with new role

### Chain 6: Weak Crypto + Information Disclosure (CVSS 8.9)
- **Pattern:** Weak algorithm used to protect data that is also exposed through another channel
- **Detection:** crypto-data finds weak hash AND logging/error auditor finds data exposure
- **Correlation type:** Disclosure + Exploitation
- **Example:** MD5-hashed passwords AND error response includes password hash

### Chain 7: Config Disclosure + Environment Injection (CVSS 8.8)
- **Pattern:** .env file exposed AND application uses env vars in system commands
- **Detection:** secrets auditor finds exposed config AND injection auditor finds env-based command execution
- **Correlation type:** Gate Bypass + Dangerous Operation
- **Example:** `.env` readable via path traversal AND `DB_HOST` used in connection string without validation

### Chain 8: Broken Auth + Session Fixation (CVSS 8.7)
- **Pattern:** Predictable session tokens AND writable session IDs
- **Detection:** auth-session finds weak token generation AND auth-session finds session fixation
- **Correlation type:** Multiple Layer Bypass
- **Example:** Sequential session IDs AND no regeneration on login

### Chain 9: Path Traversal + Secrets Access (CVSS 8.6)
- **Pattern:** Directory traversal to read key files
- **Detection:** input-output finds path traversal AND secrets auditor identifies sensitive file locations
- **Correlation type:** Compound Sink
- **Example:** `../../.env` readable via file download endpoint

### Chain 10: API Key Disclosure + Rate Limit Bypass (CVSS 8.5)
- **Pattern:** Hardcoded API key AND no per-key rate limiting
- **Detection:** secrets auditor finds hardcoded key AND api-endpoint finds missing rate limits
- **Correlation type:** Prerequisite Met
- **Example:** Exposed API key allows unlimited requests, no per-key throttling

## Five Correlation Patterns for Coordinator

The coordinator runs these 5 patterns against ALL findings after merge:

### Pattern A: Source-Sink Misalignment
- **Check:** Does a tainted data source (flagged by one auditor) reach a dangerous sink (flagged by another)?
- **Method:** Match `location` file paths — if source file and sink file are in the same data flow, flag chain
- **Trigger:** Injection + Auth, Injection + Database, Input-Output + Any

### Pattern B: Assumption Violation
- **Check:** Does Auditor A's finding assume a condition that Auditor B proved false?
- **Method:** Look for pairs where one finding is "missing validation" and another is "bypass possible"
- **Trigger:** Access-Control + Business-Logic, Auth + Any

### Pattern C: Prerequisite Met
- **Check:** Does Exploit A require condition B, and did Auditor C confirm B exists?
- **Method:** For each finding with a precondition, search other findings that satisfy it
- **Trigger:** Race-Condition + Privilege, Secrets + Injection, Config + Any

### Pattern D: Compound Sink Reachability
- **Check:** Does single tainted data reach multiple dangerous sinks across domains?
- **Method:** Track input parameters across findings — same `req.params.id` in multiple findings = chain
- **Trigger:** Any finding pair sharing the same input variable

### Pattern E: Boundary Crossing
- **Check:** Does data cross a trust boundary without validation?
- **Method:** Check if CORS/config finding enables cross-origin access to vulnerable endpoint
- **Trigger:** Config-Headers + Access-Control, Config-Headers + IDOR, Config-Headers + API

## Severity Amplification

When a chain is detected, amplify severity:

```
Chain severity = max(individual severities in chain)
  + 2.0 if security gate bypassed
  + 1.5 if information disclosure enables further exploitation
  + 1.0 per additional defense layer bypassed
  + 0.5 per prerequisite satisfied by another finding
Cap at 10.0
```

## Coordinator Integration

Add to Phase 3 (Synthesis) after deduplication:

1. Load all merged findings
2. For each of the 5 correlation patterns, scan finding pairs
3. For each detected chain, create a new CHAIN finding:
   - ID: `CHAIN-001`, `CHAIN-002`, etc.
   - Title: `[Chain Type]: [Description]`
   - Severity: Amplified per rules above
   - Component findings: List the individual finding IDs that form the chain
   - Impact: Combined impact statement
   - Fix priority: Fix the WEAKEST link in the chain first

4. Add chain findings to the report under a dedicated "Cross-Domain Chains" section
