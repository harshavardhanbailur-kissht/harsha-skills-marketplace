# Research 09: Prompt Injection Defense in Multi-Agent Systems

## Source Validation
- **Primary**: OWASP LLM Top 10 2025 (LLM01: Prompt Injection — #1 vulnerability)
- **Academic**: Gosmar et al. 2025 (Multi-Agent Defense Pipeline), Cross-Multimodal Provenance Framework
- **Framework**: Minimizer-Sanitizer Defense (firewall approach)
- **Industry**: 73% of production AI deployments have prompt injection vulnerabilities
- **Scrutiny Level**: Maximum (OWASP + peer-reviewed + production evidence)

## Key Findings

### 1. Why Multi-Agent Systems Amplify Injection Risk
In single-agent systems, injection targets one model. In multi-agent systems:
- Agent A's output becomes Agent B's input — injection can propagate
- Coordinator agent passes data between workers — acts as amplifier
- Tool outputs (file contents, API responses) are untrusted data sources
- Each agent boundary is a potential injection surface

**Critical for our skill**: Our executor passes dependency outputs from completed
tasks into downstream task prompts. A compromised task output could inject
instructions into all dependent tasks.

### 2. Multi-Agent Defense Pipeline Architecture
Gosmar et al. propose a layered defense using specialized agents:
- **Front-End Generator**: Produces initial response
- **Guard/Sanitizer Agent**: Sanitizes outputs before passing downstream
- **Policy Enforcer Agent**: Ensures compliance with security policies

Key metrics introduced:
- Injection Success Rate (ISR): % of injections that succeed
- Policy Override Frequency (POF): How often policies are bypassed
- Prompt Sanitization Rate (PSR): % of injections caught by sanitizer
- Compliance Consistency Score (CCS): Stability of policy enforcement

### 3. Zero-Trust Inter-Agent Communication
The Cross-Multimodal Provenance-Aware Framework proposes:
- **Provenance ledger**: Tracks data origin and trust levels across agents
- **Input sanitization**: Every prompt sanitized BEFORE reaching any agent
- **Output validation**: Every output validated BEFORE passing to next agent
- **Trust scoring**: Each data element tagged with origin trust level

### 4. Minimizer-Sanitizer Defense (Firewall Pattern)
- **Minimizer**: Strips information not required for the task (reduces attack surface)
- **Sanitizer**: Removes suspected injection content from tool/dependency outputs
- Operates as limited-privilege LLM between agents
- **Limitation**: Can be bypassed via obfuscation or alternative modalities (Braille encoding)
- "Outperforms all existing methods on all benchmarks" despite known bypasses

### 5. OWASP Top 10 LLM 2025 — Relevant Entries
- **LLM01 Prompt Injection**: #1 vulnerability, appears in 73% of deployments
- **LLM05 Improper Output Handling**: LLM output executed in downstream systems
  without validation → SQL injection, XSS, command injection
- **Defense**: Treat ALL LLM responses as untrusted user input

### 6. Defense-in-Depth Strategy for Our Skill
Layer 1: **Input Sanitization** (before task prompt assembly)
  - Strip control characters, encoded instructions, markdown injection
  - Validate dependency outputs against expected schema/format

Layer 2: **Output Boundary Enforcement** (after each task completes)
  - Verify output matches Interface Contract (expected format/content)
  - Flag outputs containing instruction-like patterns

Layer 3: **Provenance Tracking** (across the pipeline)
  - Tag each data element with source task ID
  - Audit trail of what data flowed where

Layer 4: **Sandboxed Execution** (for code outputs)
  - Never execute generated code in the orchestrator's context
  - Use subprocess with timeout and resource limits

## Applied Improvements
1. Add output sanitization step between executor layers
2. Add Interface Contract validation (schema check, not just format)
3. Add provenance metadata to task outputs
4. Document security model in SKILL.md
5. Add sanitization utility to scripts/
