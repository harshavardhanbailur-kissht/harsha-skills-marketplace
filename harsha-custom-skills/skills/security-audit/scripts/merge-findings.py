#!/usr/bin/env python3
"""
Merge and deduplicate security audit findings from multiple domains.

Usage:
  python3 merge-findings.py findings1.json findings2.json ...
  cat all-findings.json | python3 merge-findings.py

Output: Deduplicated findings JSON with merged metadata and risk score.
"""

import json
import sys
from typing import Dict, List, Any
from collections import defaultdict


SEVERITY_RANK = {
    'critical': 0,
    'high': 1,
    'medium': 2,
    'low': 3,
    'info': 4
}

SEVERITY_SCORES = {
    'critical': 25,
    'high': 10,
    'medium': 3,
    'low': 1,
    'info': 0
}


def normalize_location(location: str) -> str:
    """Normalize file location for comparison."""
    # Remove leading ./ or /
    loc = location.lstrip('./')
    # Split into file:line
    if ':' in loc:
        parts = loc.rsplit(':', 1)
        filepath = parts[0]
        line = parts[1] if parts[1].isdigit() else '0'
        return f"{filepath}:{line}"
    return loc


def deduplicate(findings: List[Dict]) -> List[Dict]:
    """
    Deduplicate findings by file:line.

    When multiple findings have the same location:
    - Keep the one with highest severity
    - Merge CWE/OWASP references from all
    - Combine evidence if different
    - Track domains that found the issue
    """
    by_location: Dict[str, List[Dict]] = defaultdict(list)

    for finding in findings:
        location = normalize_location(finding.get('location', 'unknown'))
        by_location[location].append(finding)

    merged = []
    for location, group in by_location.items():
        if len(group) == 1:
            # Single finding - keep as is
            result = group[0].copy()
            result['duplicate_count'] = 1
            result['domains'] = [result.get('domain', 'unknown')]
            merged.append(result)
            continue

        # Multiple findings at same location - merge them
        # Sort by severity (highest first)
        group.sort(key=lambda x: SEVERITY_RANK.get(
            x.get('severity', 'info').lower(), 4
        ))

        # Start with the highest severity finding
        best = group[0].copy()

        # Collect all CWE, OWASP, and domain references
        all_cwes = set()
        all_owasp = set()
        all_domains = set()
        all_evidence = []

        for finding in group:
            cwe = finding.get('cwe', '')
            if cwe:
                all_cwes.add(cwe)

            owasp = finding.get('owasp', '')
            if owasp:
                all_owasp.add(owasp)

            domain = finding.get('domain', '')
            if domain:
                all_domains.add(domain)

            evidence = finding.get('evidence', '')
            if evidence and evidence not in all_evidence:
                all_evidence.append(evidence)

        # Merge references
        if len(all_cwes) > 1:
            best['cwe'] = ', '.join(sorted(all_cwes))

        if len(all_owasp) > 1:
            best['owasp'] = ', '.join(sorted(all_owasp))

        best['domains'] = list(sorted(all_domains))
        best['duplicate_count'] = len(group)

        # Combine evidence if multiple different pieces
        if len(all_evidence) > 1:
            best['evidence'] = '\n---\n'.join(all_evidence[:3])  # Limit to 3

        # Note in checklist if merged from multiple domains
        if len(all_domains) > 1:
            existing_notes = best.get('checklist_notes', '')
            merge_note = f"Merged from {len(group)} findings across domains: {', '.join(all_domains)}"
            best['checklist_notes'] = f"{existing_notes}\n{merge_note}".strip()

        merged.append(best)

    return merged


def assign_ids(findings: List[Dict]) -> List[Dict]:
    """
    Assign sequential IDs to findings, sorted by severity.

    Critical findings get lower IDs, making them appear first.
    """
    # Sort by severity, then by location for deterministic ordering
    findings.sort(key=lambda x: (
        SEVERITY_RANK.get(x.get('severity', 'info').lower(), 4),
        x.get('location', '')
    ))

    for i, finding in enumerate(findings, 1):
        finding['id'] = f'FINDING-{i:03d}'

    return findings


def calculate_risk_score(findings: List[Dict]) -> int:
    """
    Calculate overall risk score (0-100).

    Formula: Critical*25 + High*10 + Medium*3 + Low*1, capped at 100
    """
    score = 0
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        score += SEVERITY_SCORES.get(severity, 0)
    return min(100, score)


def get_risk_level(score: int) -> str:
    """Convert risk score to human-readable level."""
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
    counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'info': 0
    }
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity in counts:
            counts[severity] += 1
    return counts


def count_by_domain(findings: List[Dict]) -> Dict[str, int]:
    """Count findings by security domain."""
    counts: Dict[str, int] = {}
    for finding in findings:
        domain = finding.get('domain', 'other')
        counts[domain] = counts.get(domain, 0) + 1
    return counts


def validate_finding(finding: Dict) -> List[str]:
    """Validate a finding has required fields."""
    required = [
        'title', 'severity', 'cwe', 'owasp', 'domain',
        'location', 'evidence', 'impact', 'fix', 'verification'
    ]
    missing = [field for field in required if not finding.get(field)]
    return missing


def merge_findings(all_findings: List[Dict], project: str = "Unknown") -> Dict[str, Any]:
    """
    Main merge function.

    Takes a list of findings, deduplicates, assigns IDs,
    calculates risk score, and returns complete audit result.
    """
    # Filter out empty or invalid findings
    valid_findings = []
    warnings = []

    for i, finding in enumerate(all_findings):
        if not isinstance(finding, dict):
            warnings.append(f"Item {i}: Not a valid finding object")
            continue

        missing = validate_finding(finding)
        if missing:
            warnings.append(f"Item {i}: Missing fields: {missing}")

        valid_findings.append(finding)

    # Deduplicate and assign IDs
    merged = deduplicate(valid_findings)
    merged = assign_ids(merged)

    # Calculate stats
    risk_score = calculate_risk_score(merged)
    summary = count_by_severity(merged)
    by_domain = count_by_domain(merged)

    result = {
        'project': project,
        'audit_date': __import__('datetime').datetime.now().strftime('%Y-%m-%d'),
        'risk_score': risk_score,
        'risk_level': get_risk_level(risk_score),
        'total_before_dedup': len(all_findings),
        'total_after_dedup': len(merged),
        'duplicates_removed': len(all_findings) - len(merged),
        'summary': summary,
        'by_domain': by_domain,
        'findings': merged
    }

    if warnings:
        result['warnings'] = warnings

    return result


def main():
    """Entry point."""
    all_findings: List[Dict] = []
    project = "Unknown Project"

    if len(sys.argv) > 1:
        # Read from file arguments
        for filepath in sys.argv[1:]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Handle different input formats
                if isinstance(data, list):
                    all_findings.extend(data)
                elif isinstance(data, dict):
                    if 'findings' in data:
                        all_findings.extend(data['findings'])
                    if 'project' in data:
                        project = data['project']
                    else:
                        # Single finding object
                        all_findings.append(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {filepath}: {e}", file=sys.stderr)
                continue
    else:
        # Read from stdin
        try:
            data = json.load(sys.stdin)
            if isinstance(data, list):
                all_findings = data
            elif isinstance(data, dict):
                if 'findings' in data:
                    all_findings = data['findings']
                if 'project' in data:
                    project = data['project']
                else:
                    all_findings = [data]
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    if not all_findings:
        # Return empty result
        result = {
            'project': project,
            'audit_date': __import__('datetime').datetime.now().strftime('%Y-%m-%d'),
            'risk_score': 0,
            'risk_level': 'Low Risk',
            'total_before_dedup': 0,
            'total_after_dedup': 0,
            'duplicates_removed': 0,
            'summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            },
            'by_domain': {},
            'findings': []
        }
        print(json.dumps(result, indent=2))
        return

    result = merge_findings(all_findings, project)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
