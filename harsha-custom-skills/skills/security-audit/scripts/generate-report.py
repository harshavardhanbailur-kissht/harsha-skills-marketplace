#!/usr/bin/env python3
"""
Security Audit Report Generator
Takes JSON findings from security audit and generates a formatted markdown report.
Uses only Python stdlib - no external dependencies required.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


def calculate_risk_score(findings: List[Dict]) -> int:
    """Calculate overall risk score (0-100) based on findings."""
    score = 0
    for finding in findings:
        severity = finding.get('severity', '').lower()
        if severity == 'critical':
            score += 25
        elif severity == 'high':
            score += 10
        elif severity == 'medium':
            score += 3
        elif severity == 'low':
            score += 1
    return min(100, score)


def get_risk_level(score: int) -> str:
    """Convert risk score to risk level description."""
    if score <= 20:
        return "Low Risk"
    elif score <= 50:
        return "Moderate Risk"
    elif score <= 80:
        return "High Risk"
    else:
        return "Critical Risk"


def count_by_severity(findings: List[Dict]) -> Dict[str, int]:
    """Count findings by severity level."""
    counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity in counts:
            counts[severity] += 1
    return counts


def count_by_domain(findings: List[Dict]) -> Dict[str, int]:
    """Count findings by security domain."""
    counts = {}
    for finding in findings:
        domain = finding.get('domain', 'other')
        counts[domain] = counts.get(domain, 0) + 1
    return counts


def generate_executive_summary(project: str, findings: List[Dict], risk_score: int) -> str:
    """Generate executive summary section."""
    counts = count_by_severity(findings)
    risk_level = get_risk_level(risk_score)

    # Get top 5 critical/high issues
    critical_high = [f for f in findings if f.get('severity', '').lower() in ('critical', 'high')]
    top_issues = critical_high[:5]

    summary = f"""## Executive Summary

**Project:** {project}
**Audit Date:** {datetime.now().strftime('%Y-%m-%d')}
**Risk Score:** {risk_score}/100 ({risk_level})

### Finding Summary

| Severity | Count |
|----------|-------|
| Critical | {counts['critical']} |
| High | {counts['high']} |
| Medium | {counts['medium']} |
| Low | {counts['low']} |
| Info | {counts['info']} |
| **Total** | **{len(findings)}** |

### Risk Assessment

"""

    if risk_score <= 20:
        summary += "The codebase has a **low security risk** profile. Routine maintenance and monitoring recommended.\n\n"
    elif risk_score <= 50:
        summary += "The codebase has a **moderate security risk** profile. Prioritize addressing high and critical severity issues.\n\n"
    elif risk_score <= 80:
        summary += "The codebase has a **high security risk** profile. Immediate attention needed for critical findings.\n\n"
    else:
        summary += "⚠️ The codebase has a **critical security risk** profile. **Stop deployment** and address critical issues immediately.\n\n"

    if top_issues:
        summary += "### Top Issues Requiring Immediate Attention\n\n"
        for i, issue in enumerate(top_issues, 1):
            summary += f"{i}. **{issue.get('title', 'Untitled')}** ({issue.get('severity', 'N/A')}) - {issue.get('location', 'Unknown')}\n"
        summary += "\n"

    return summary


def generate_findings_table(findings: List[Dict]) -> str:
    """Generate findings summary table."""
    if not findings:
        return "No findings to report.\n"

    table = """## Findings Overview

| ID | Severity | Domain | Title | CWE | Location | Status |
|----|----------|--------|-------|-----|----------|--------|
"""

    for finding in findings:
        finding_id = finding.get('id', 'N/A')
        severity = finding.get('severity', 'N/A')
        domain = finding.get('domain', 'N/A')
        title = finding.get('title', 'Untitled')[:40]
        cwe = finding.get('cwe', 'N/A')
        location = finding.get('location', 'N/A')[:30]
        status = finding.get('checklist_status', 'pending')
        status_emoji = '✅' if status == 'all_pass' else '⚠️'

        table += f"| {finding_id} | {severity} | {domain} | {title} | {cwe} | {location} | {status_emoji} |\n"

    return table + "\n"


def generate_detailed_findings(findings: List[Dict]) -> str:
    """Generate detailed findings section."""
    if not findings:
        return ""

    output = "## Detailed Findings\n\n"

    # Group by severity
    severity_order = ['critical', 'high', 'medium', 'low', 'info']

    for severity in severity_order:
        severity_findings = [f for f in findings if f.get('severity', '').lower() == severity]

        if not severity_findings:
            continue

        output += f"### {severity.title()} Severity\n\n"

        for finding in severity_findings:
            output += f"#### {finding.get('id', 'N/A')}: {finding.get('title', 'Untitled')}\n\n"
            output += f"- **Severity:** {finding.get('severity', 'N/A')}\n"
            output += f"- **CVSS:** {finding.get('cvss', 'N/A')}\n"
            output += f"- **CWE:** {finding.get('cwe', 'N/A')}\n"
            output += f"- **OWASP:** {finding.get('owasp', 'N/A')}\n"
            output += f"- **Domain:** {finding.get('domain', 'N/A')}\n"
            output += f"- **Location:** `{finding.get('location', 'N/A')}`\n\n"

            if finding.get('evidence'):
                output += f"**Evidence:**\n```\n{finding['evidence']}\n```\n\n"

            if finding.get('impact'):
                output += f"**Impact:** {finding['impact']}\n\n"

            if finding.get('fix'):
                output += f"**Recommended Fix:**\n```diff\n{finding['fix']}\n```\n\n"

            if finding.get('verification'):
                output += f"**Verification:** {finding['verification']}\n\n"

            checklist_status = finding.get('checklist_status', 'pending')
            if checklist_status == 'all_pass':
                output += "**Non-Invasive Checklist:** ✅ All 10 points pass - Ready to apply\n\n"
            else:
                notes = finding.get('checklist_notes', 'Requires manual review')
                output += f"**Non-Invasive Checklist:** ⚠️ {notes}\n\n"

            output += "---\n\n"

    return output


def generate_implementation_roadmap(findings: List[Dict]) -> str:
    """Generate implementation roadmap section."""
    output = """## Implementation Roadmap

### Phase 1: Immediate (0-48 hours)
*Configuration and dependency fixes - lowest risk changes*

"""

    # Phase 1: Config/deps
    phase1 = [f for f in findings
              if f.get('severity', '').lower() in ('critical', 'high')
              and f.get('domain', '') in ('config-headers', 'dependency', 'secrets')]

    if phase1:
        for f in phase1[:5]:
            output += f"- [ ] {f.get('id', 'N/A')}: {f.get('title', 'Untitled')}\n"
    else:
        output += "- No items in this phase\n"

    output += """
### Phase 2: Short-term (1-2 weeks)
*Validation wrappers and sanitization - moderate complexity*

"""

    # Phase 2: Validation/sanitization
    phase2 = [f for f in findings
              if f.get('severity', '').lower() in ('critical', 'high', 'medium')
              and f.get('domain', '') in ('injection', 'xss-csrf', 'input-output', 'error-handling')]

    if phase2:
        for f in phase2[:5]:
            output += f"- [ ] {f.get('id', 'N/A')}: {f.get('title', 'Untitled')}\n"
    else:
        output += "- No items in this phase\n"

    output += """
### Phase 3: Medium-term (2-4 weeks)
*Authentication, access control, and business logic - requires more testing*

"""

    # Phase 3: Auth/access/business
    phase3 = [f for f in findings
              if f.get('domain', '') in ('auth-session', 'access-control', 'business-logic', 'concurrency')]

    if phase3:
        for f in phase3[:5]:
            output += f"- [ ] {f.get('id', 'N/A')}: {f.get('title', 'Untitled')}\n"
    else:
        output += "- No items in this phase\n"

    return output + "\n"


def generate_verification_plan(findings: List[Dict]) -> str:
    """Generate verification plan section."""
    return """## Verification Plan

### For Each Fix

1. **Pre-fix baseline capture**
   - Save current API responses
   - Run existing test suite
   - Document expected behavior

2. **Apply fix**
   - Implement recommended change
   - Verify minimal diff

3. **Post-fix verification**
   - Run test suite (all tests pass)
   - Compare API responses (unchanged)
   - Verify fix resolves issue
   - Check no performance regression

4. **Regression testing**
   - Full integration test
   - Security-specific test added

### Overall Verification

```bash
# Run after all fixes applied
npm test  # or pytest, go test, etc.

# Check security headers
curl -sI https://your-app.com | grep -E "X-Frame|X-Content|Strict-Transport"

# Verify no regressions
diff baseline_responses.json postfix_responses.json
```

"""


def generate_report(data: Dict) -> str:
    """Generate complete security audit report."""
    project = data.get('project', 'Unknown Project')
    findings = data.get('findings', [])

    risk_score = data.get('risk_score') or calculate_risk_score(findings)

    report = f"""# Security Audit Report

---

"""

    report += generate_executive_summary(project, findings, risk_score)
    report += generate_findings_table(findings)
    report += generate_detailed_findings(findings)
    report += generate_implementation_roadmap(findings)
    report += generate_verification_plan(findings)

    report += """---

*Report generated by Security Audit Skill*
*🤖 Generated with [Claude Code](https://claude.com/claude-code)*
"""

    return report


def generate_sarif(data: Dict) -> str:
    """
    Generate SARIF v2.1.0 output for integration with:
    - GitHub Code Scanning
    - VS Code SARIF Viewer
    - Azure DevOps
    - Other SARIF-compatible tools
    """
    findings = data.get('findings', [])

    rules = []
    results = []
    seen_rules = set()

    for finding in findings:
        # Create rule ID from CWE
        cwe = finding.get('cwe', 'UNKNOWN')
        rule_id = cwe.replace('CWE-', 'SEC') if cwe.startswith('CWE-') else f"SEC-{cwe}"

        # Add rule definition if not seen
        if rule_id not in seen_rules:
            seen_rules.add(rule_id)
            cwe_number = cwe.replace('CWE-', '') if cwe.startswith('CWE-') else ''

            rules.append({
                "id": rule_id,
                "name": finding.get('title', 'Security Finding'),
                "shortDescription": {
                    "text": finding.get('title', '')
                },
                "fullDescription": {
                    "text": finding.get('impact', finding.get('title', ''))
                },
                "helpUri": f"https://cwe.mitre.org/data/definitions/{cwe_number}.html" if cwe_number.isdigit() else "",
                "properties": {
                    "tags": ["security", finding.get('owasp', ''), finding.get('domain', '')]
                },
                "defaultConfiguration": {
                    "level": "warning"
                }
            })

        # Parse location
        location = finding.get('location', ':1')
        parts = location.rsplit(':', 1)
        filepath = parts[0] if parts else location
        try:
            line = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        except (ValueError, IndexError):
            line = 1

        # Map severity to SARIF level
        severity_map = {
            'critical': 'error',
            'high': 'error',
            'medium': 'warning',
            'low': 'note',
            'info': 'note'
        }
        level = severity_map.get(finding.get('severity', '').lower(), 'warning')

        # Create result
        result = {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": finding.get('impact', finding.get('title', ''))
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": filepath,
                        "uriBaseId": "%SRCROOT%"
                    },
                    "region": {
                        "startLine": line
                    }
                }
            }]
        }

        # Add fix suggestion if available
        fix = finding.get('fix', '')
        if fix:
            result["fixes"] = [{
                "description": {
                    "text": "Apply recommended fix"
                },
                "artifactChanges": [{
                    "artifactLocation": {
                        "uri": filepath
                    },
                    "replacements": [{
                        "deletedRegion": {
                            "startLine": line
                        },
                        "insertedContent": {
                            "text": fix
                        }
                    }]
                }]
            }]

        # Add properties
        result["properties"] = {
            "severity": finding.get('severity', ''),
            "cvss": finding.get('cvss', ''),
            "domain": finding.get('domain', ''),
            "checklist_status": finding.get('checklist_status', ''),
            "owasp": finding.get('owasp', ''),
            "cwe": finding.get('cwe', '')
        }

        results.append(result)

    # Construct SARIF document
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "security-audit-skill",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/anthropics/claude-code",
                    "rules": rules
                }
            },
            "results": results,
            "invocations": [{
                "executionSuccessful": True,
                "endTimeUtc": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }]
        }]
    }

    return json.dumps(sarif, indent=2)


def print_usage():
    """Print usage information."""
    usage = """
Security Audit Report Generator

Usage:
  python3 generate-report.py [input.json] [output.md] [--format FORMAT]
  cat findings.json | python3 generate-report.py [--format FORMAT]

Options:
  --format FORMAT   Output format: markdown (default) or sarif
  --help, -h        Show this help message

Examples:
  python3 generate-report.py findings.json                    # Output markdown to stdout
  python3 generate-report.py findings.json report.md          # Output markdown to file
  python3 generate-report.py findings.json --format sarif     # Output SARIF to stdout
  python3 generate-report.py findings.json report.sarif --format sarif
  cat findings.json | python3 generate-report.py --format sarif > report.sarif
"""
    print(usage, file=sys.stderr)


def main():
    """Entry point."""
    # Parse arguments
    args = sys.argv[1:]
    input_file = None
    output_file = None
    output_format = 'markdown'

    # Handle --help
    if '-h' in args or '--help' in args:
        print_usage()
        sys.exit(0)

    # Extract --format argument
    if '--format' in args:
        idx = args.index('--format')
        if idx + 1 < len(args):
            output_format = args[idx + 1].lower()
            args = args[:idx] + args[idx + 2:]
        else:
            print("Error: --format requires an argument (markdown or sarif)", file=sys.stderr)
            sys.exit(1)

    # Remaining positional arguments
    if len(args) >= 1:
        input_file = args[0]
    if len(args) >= 2:
        output_file = args[1]

    # Validate format
    if output_format not in ('markdown', 'sarif', 'md'):
        print(f"Error: Unknown format '{output_format}'. Use 'markdown' or 'sarif'.", file=sys.stderr)
        sys.exit(1)

    # Read input
    if input_file:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading {input_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    # Generate output
    if output_format == 'sarif':
        output = generate_sarif(data)
    else:
        output = generate_report(data)

    # Write output
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report written to {output_file}", file=sys.stderr)
        except IOError as e:
            print(f"Error writing {output_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == '__main__':
    main()
