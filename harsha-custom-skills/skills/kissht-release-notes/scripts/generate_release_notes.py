#!/usr/bin/env python3
"""
Kissht Release Notes Generator
Transforms ticket data (CSV or JSON) into stakeholder-specific release documentation.

Usage:
    python generate_release_notes.py --input tickets.csv --output ./output --stakeholders pm,qa,dev,training,ba,ops
    python generate_release_notes.py --input tickets.json --output ./output --format html
    python generate_release_notes.py --input tickets.csv --output ./output --format all
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path


# ============================================================================
# DOMAIN KNOWLEDGE: Feature Categories & Journey Stages
# ============================================================================

CATEGORY_KEYWORDS = {
    "Document Management": ["document", "doc", "upload", "replace", "cleanup", "saral doc", "los doc", "activity", "document manager"],
    "KYC & Identity": ["kyc", "aadhaar", "selfie", "liveness", "address proof", "identity", "osv", "verification"],
    "Sales PD & Property": ["sales pd", "property", "home", "pd visit", "check-in", "check-out", "field visit"],
    "Credit & Bureau": ["bureau", "cibil", "credit", "waiver", "cam", "cpa", "brc", "score"],
    "Transaction & Sanction": ["sanction", "disbursal", "disbursement", "transaction", "ipa", "ncm", "tranche", "fee"],
    "LOS Panel & Operations": ["los panel", "smart view", "form", "dropdown", "ui", "usability"],
    "Multi-Applicant & Top-Up": ["co-applicant", "top-up", "topup", "co-app", "concurrent", "mortgage"],
    "Data Consistency": ["mapping", "format", "field", "data", "standardize", "query mapping"],
    "BRE & Eligibility": ["bre", "eligibility", "rule engine", "business rule", "program"],
    "Integration": ["saral", "lsq", "mavis", "integration", "sync", "api"],
}

JOURNEY_STAGES = [
    "Lead Created",
    "Applicant Valid → Applicant Onboarded",
    "Applicant Onboarded → CPA Verified",
    "BRE Approved → CPA Verified",
    "Sales PD Complete",
    "IPA Pending → Disbursed",
    "Final Sanction Approval Pending",
    "Disbursed",
    "Various",
]

STATUS_CLASSIFICATION = {
    "Highest": "Critical Fix",
    "High": "Live Now",
    "Medium": "Enhancement",
    "Low": "Enhancement",
    "Lowest": "Enhancement",
}

AUDIENCE_MAPPING = {
    "Document Management": ["Sales RM", "CPA", "Branch Ops"],
    "KYC & Identity": ["Sales RM", "CPA"],
    "Sales PD & Property": ["Sales RM", "BCM"],
    "Credit & Bureau": ["BCM", "CPA"],
    "Transaction & Sanction": ["BCM", "Central Ops", "Finance"],
    "LOS Panel & Operations": ["All Users"],
    "Multi-Applicant & Top-Up": ["Sales RM", "Central Ops"],
    "Data Consistency": ["All Users"],
    "BRE & Eligibility": ["BCM", "CPA"],
    "Integration": ["Dev", "Ops"],
    "General Fixes": ["All Users"],
}

# Weighted keyword scoring (from content-generation.md NLP Classification)
KEYWORD_WEIGHTS = {
    "Document Management": {
        "high": ["document upload", "doc sync", "saral", "document replace", "document cleanup"],
        "medium": ["attachment", "file", "upload"]
    },
    "KYC & Identity": {
        "high": ["kyc", "aadhaar", "selfie", "liveness", "pan card", "ekyc", "identity verification"],
        "medium": ["verification", "identity", "photo"]
    },
    "Credit & Bureau": {
        "high": ["bureau", "cibil", "waiver", "bre", "cam report", "credit score", "bureau pull"],
        "medium": ["score", "credit", "eligibility", "threshold"]
    },
    "Transaction & Sanction": {
        "high": ["sanction", "disbursal", "disbursement", "tranche", "fee", "transaction status", "ncm"],
        "medium": ["loan", "amount", "payment", "emi"]
    },
    "Sales PD & Property": {
        "high": ["pd visit", "property", "home visit", "valuation", "personal discussion", "site visit"],
        "medium": ["field", "visit"]
    },
    "LOS Panel & Operations": {
        "high": ["los panel", "smart view", "form", "dropdown", "ui fix", "dashboard"],
        "medium": ["display", "button", "screen", "view"]
    },
    "Multi-Applicant & Top-Up": {
        "high": ["co-applicant", "income contributor", "top-up", "ic applicant", "concurrent"],
        "medium": ["applicant", "co-app"]
    },
    "Data Consistency": {
        "high": ["field mapping", "dropdown values", "data mismatch", "sync", "standardize"],
        "medium": ["mapping", "format", "value"]
    },
    "BRE & Eligibility": {
        "high": ["bre rule", "eligibility", "program", "business rule", "whitelist", "mavis"],
        "medium": ["rule", "eligible", "qualify"]
    },
    "Integration": {
        "high": ["saral los", "lsq lap", "api", "integration", "webhook", "account aggregator"],
        "medium": ["connect", "interface", "endpoint"]
    },
}

# Hinglish / Indian English normalization (common in Kissht tickets)
HINGLISH_MAPPINGS = {
    "updation": "update", "updations": "updates",
    "rectification": "fix", "rectify": "fix",
    "bifurcation": "split", "prepone": "advance",
    "intimation": "notification",
    "disbursment": "disbursement",
}

# RBI compliance trigger keywords
COMPLIANCE_KEYWORDS = [
    "kfs", "key fact statement", "consent", "data localization",
    "audit trail", "cooling off", "grievance", "lsp disclosure",
    "rbi", "regulatory", "compliance", "account aggregator",
    "digital consent", "e-sign", "otp verification",
    "interest rate", "penal charges", "foreclosure",
]


# ============================================================================
# DATA LOADING
# ============================================================================

def load_csv(filepath):
    """Load tickets from CSV (Google Sheets export format)"""
    tickets = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticket = {
                "key": row.get("Ticket Key", "").strip(),
                "link": row.get("Ticket Link", "").strip(),
                "summary": row.get("Summary", "").strip(),
                "created": row.get("Created Date", "").strip(),
                "completed": row.get("Completed Date", "").strip(),
                "status": row.get("Status", "").strip(),
                "assignee": row.get("Assignee", "").strip(),
                "reporter": row.get("Reporter", "").strip(),
                "commenters": row.get("Contributors (Commenters)", "").strip(),
                "worklog": row.get("Contributors (Worklog)", "").strip(),
                "past_assignees": row.get("Contributors (Past Assignees)", "").strip(),
                "issue_type": row.get("Issue Type", "").strip(),
                "priority": row.get("Priority", "").strip(),
                "cycle_time": row.get("Cycle Time (Days)", "").strip(),
            }
            if ticket["key"]:
                tickets.append(ticket)
    return tickets


def load_json(filepath):
    """Load tickets from JSON format"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("tickets", data.get("issues", []))


# ============================================================================
# CLASSIFICATION ENGINE
# ============================================================================

def classify_ticket(ticket):
    """Classify a ticket by category, journey stage, status, audience, and confidence.

    Uses weighted keyword scoring (HIGH=3, MEDIUM=2) with Hinglish normalization.
    Returns classification with confidence level (VERIFIED/HIGH/MEDIUM/LOW).
    Also detects RBI compliance triggers.
    """
    summary = ticket["summary"]
    summary_lower = summary.lower()

    # Hinglish normalization
    for hinglish, english in HINGLISH_MAPPINGS.items():
        summary_lower = summary_lower.replace(hinglish, english)

    # --- Weighted Category Classification ---
    category = "General Fixes"
    max_score = 0
    all_scores = {}

    for cat, weights in KEYWORD_WEIGHTS.items():
        score = 0
        for kw in weights.get("high", []):
            if kw in summary_lower:
                score += 3
        for kw in weights.get("medium", []):
            if kw in summary_lower:
                score += 2
        all_scores[cat] = score
        if score > max_score:
            max_score = score
            category = cat

    # Fallback to simple keyword match if weighted scoring fails
    if max_score == 0:
        for cat, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in summary_lower)
            if score > max_score:
                max_score = score
                category = cat

    # --- Confidence Level ---
    if max_score >= 6:
        confidence = "VERIFIED"
        confidence_tag = "[✓]"
    elif max_score >= 3:
        confidence = "HIGH"
        confidence_tag = "[H]"
    elif max_score >= 2:
        confidence = "MEDIUM"
        confidence_tag = "[M]"
    else:
        confidence = "LOW"
        confidence_tag = "[L]"
        category = "General Fixes"

    # --- Status Classification (enhanced) ---
    priority = ticket.get("priority", "Medium")
    issue_type = ticket.get("issue_type", "")
    status_badge = STATUS_CLASSIFICATION.get(priority, "Enhancement")

    # Override: High priority bugs are always Critical Fix
    if priority in ["Highest", "High"] and issue_type == "Bug":
        status_badge = "Critical Fix"
    # Override: Blocker/crash keywords → Critical Fix
    if any(w in summary_lower for w in ["blocker", "crash", "production", "urgent", "hotfix", "data loss"]):
        status_badge = "Critical Fix"

    # --- Audience ---
    audience = AUDIENCE_MAPPING.get(category, ["All Users"])

    # --- Journey Stage ---
    journey = "Various"
    if any(kw in summary_lower for kw in ["kyc", "aadhaar", "selfie", "onboard", "liveness"]):
        journey = "Applicant Valid → Applicant Onboarded"
    elif any(kw in summary_lower for kw in ["document", "cpa", "verification", "doc sync"]):
        journey = "Applicant Onboarded → CPA Verified"
    elif any(kw in summary_lower for kw in ["bureau", "cibil", "credit", "cam", "bre", "waiver"]):
        journey = "BRE Approved → CPA Verified"
    elif any(kw in summary_lower for kw in ["sales pd", "property", "home", "pd visit", "valuation"]):
        journey = "Sales PD Complete"
    elif any(kw in summary_lower for kw in ["sanction", "disbursal", "ipa", "ncm", "tranche", "fee"]):
        journey = "IPA Pending → Disbursed"
    elif any(kw in summary_lower for kw in ["lead", "saral", "lsq"]):
        journey = "Lead Created"

    # --- RBI Compliance Detection ---
    compliance_flag = any(kw in summary_lower for kw in COMPLIANCE_KEYWORDS)

    # --- Sentiment-based framing ---
    neg_words = ["fix", "bug", "error", "fail", "crash", "missing", "incorrect", "wrong", "broken", "block"]
    pos_words = ["add", "new", "enhance", "improve", "feature", "enable", "support", "implement", "introduce"]
    neg_count = sum(1 for w in neg_words if w in summary_lower)
    pos_count = sum(1 for w in pos_words if w in summary_lower)
    framing = "fix" if (issue_type == "Bug" or neg_count > pos_count) else (
        "feature" if pos_count > neg_count else "enhancement"
    )

    ticket["category"] = category
    ticket["journey"] = journey
    ticket["status_badge"] = status_badge
    ticket["audience"] = audience
    ticket["confidence"] = confidence
    ticket["confidence_tag"] = confidence_tag
    ticket["confidence_score"] = max_score
    ticket["compliance_flag"] = compliance_flag
    ticket["framing"] = framing

    return ticket


def group_tickets(tickets):
    """Group tickets into release announcements by category"""
    groups = defaultdict(list)
    for t in tickets:
        groups[t["category"]].append(t)
    return dict(groups)


# ============================================================================
# GUIDE GENERATORS
# ============================================================================

def generate_pm_guide(tickets, groups, metadata):
    """Generate Product Manager release notes"""
    lines = []
    lines.append(f"# Release Notes: {metadata['project']} — Product Manager View")
    lines.append(f"**Release Date**: {metadata['date']}")
    lines.append(f"**Tickets Shipped**: {len(tickets)}")
    lines.append("")

    # Executive summary
    bug_count = sum(1 for t in tickets if t.get("issue_type") == "Bug")
    story_count = sum(1 for t in tickets if t.get("issue_type") == "Story")
    critical_count = sum(1 for t in tickets if t.get("status_badge") == "Critical Fix")

    lines.append("## Executive Summary")
    lines.append(f"This release ships {len(tickets)} updates ({bug_count} bug fixes, "
                 f"{story_count} features). {critical_count} critical production fixes were resolved. "
                 f"Key areas of improvement include {', '.join(list(groups.keys())[:3])}.")
    lines.append("")

    # Per-group highlights
    lines.append("## Release Highlights")
    lines.append("")
    for category, group_tickets_list in groups.items():
        statuses = set(t["status_badge"] for t in group_tickets_list)
        top_status = "Critical Fix" if "Critical Fix" in statuses else "Live Now"
        audiences = set()
        for t in group_tickets_list:
            audiences.update(t.get("audience", []))

        lines.append(f"### {top_status}: {category}")
        lines.append(f"**Tickets**: {len(group_tickets_list)} ({', '.join(t['key'] for t in group_tickets_list[:5])}{'...' if len(group_tickets_list) > 5 else ''})")
        lines.append(f"**Affected Roles**: {', '.join(sorted(audiences))}")
        lines.append("")

        lines.append("**Key Changes**:")
        for t in group_tickets_list[:5]:
            lines.append(f"- {t['summary']}")
        lines.append("")

    # Metrics
    cycle_times = [float(t["cycle_time"]) for t in tickets if t.get("cycle_time")]
    avg_cycle = sum(cycle_times) / len(cycle_times) if cycle_times else 0

    lines.append("## Delivery Metrics")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Shipped | {len(tickets)} |")
    lines.append(f"| Bug:Feature Ratio | {bug_count}:{story_count} |")
    lines.append(f"| Critical Fixes | {critical_count} |")
    lines.append(f"| Avg Cycle Time | {avg_cycle:.1f} days |")
    lines.append("")

    return "\n".join(lines)


def generate_qa_guide(tickets, groups, metadata):
    """Generate QA impact assessment"""
    lines = []
    lines.append(f"# QA Impact Assessment: {metadata['project']}")
    lines.append(f"**Release Date**: {metadata['date']}")
    critical_count = sum(1 for t in tickets if t.get("status_badge") == "Critical Fix")
    risk = "HIGH" if critical_count > 2 else ("MEDIUM" if critical_count > 0 else "LOW")
    lines.append(f"**Overall Risk Level**: {risk}")
    lines.append("")

    lines.append("## Test Impact Summary")
    lines.append("| Module | Changes | Risk | Priority |")
    lines.append("|--------|---------|------|----------|")
    for category, group_tickets_list in groups.items():
        has_critical = any(t["status_badge"] == "Critical Fix" for t in group_tickets_list)
        risk_level = "HIGH" if has_critical else "MEDIUM"
        priority = "P1" if has_critical else "P2"
        lines.append(f"| {category} | {len(group_tickets_list)} | {risk_level} | {priority} |")
    lines.append("")

    # Detailed per-group
    for category, group_tickets_list in groups.items():
        lines.append(f"## {category}")
        lines.append("")
        for t in group_tickets_list:
            lines.append(f"### [{t['key']}]({t.get('link', '')}) — {t['summary']}")
            lines.append(f"- **Type**: {t.get('issue_type', 'Unknown')}")
            lines.append(f"- **Priority**: {t.get('priority', 'Medium')}")
            lines.append(f"- **Journey**: {t.get('journey', 'Various')}")
            lines.append(f"- **Regression Risk**: Test {t.get('journey', 'related')} flows")
            lines.append("")

    lines.append("## Regression Checklist")
    for t in tickets:
        if t.get("status_badge") == "Critical Fix":
            lines.append(f"- [ ] **{t['key']}**: {t['summary']} (CRITICAL)")
    for t in tickets:
        if t.get("status_badge") != "Critical Fix":
            lines.append(f"- [ ] {t['key']}: {t['summary']}")
    lines.append("")

    return "\n".join(lines)


def generate_dev_guide(tickets, groups, metadata):
    """Generate developer changelog"""
    lines = []
    lines.append(f"# Developer Changelog: {metadata['project']}")
    lines.append(f"**Release Date**: {metadata['date']}")
    lines.append("")

    for category, group_tickets_list in groups.items():
        lines.append(f"## {category}")
        lines.append("")
        for t in group_tickets_list:
            lines.append(f"### {t['key']}: {t['summary']}")
            lines.append(f"- **Type**: {t.get('issue_type', 'Unknown')}")
            lines.append(f"- **Assignee**: {t.get('assignee', 'Unknown')}")
            contributors = []
            if t.get("commenters"):
                contributors.append(t["commenters"])
            if t.get("past_assignees"):
                contributors.append(t["past_assignees"])
            if contributors:
                lines.append(f"- **Contributors**: {', '.join(contributors)}")
            lines.append(f"- **Cycle Time**: {t.get('cycle_time', 'N/A')} days")
            if t.get("link"):
                lines.append(f"- **Jira**: [{t['key']}]({t['link']})")
            lines.append("")

    # Contributor summary
    assignee_counts = defaultdict(int)
    for t in tickets:
        if t.get("assignee"):
            assignee_counts[t["assignee"]] += 1

    lines.append("## Contributor Summary")
    lines.append("| Developer | Tickets |")
    lines.append("|-----------|---------|")
    for dev, count in sorted(assignee_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {dev} | {count} |")
    lines.append("")

    return "\n".join(lines)


def generate_training_guide(tickets, groups, metadata):
    """Generate training & SOP guide"""
    lines = []
    lines.append(f"# Training & SOP Guide: {metadata['project']}")
    lines.append(f"**Effective Date**: {metadata['date']}")
    critical_count = sum(1 for t in tickets if t.get("status_badge") == "Critical Fix")
    priority = "MANDATORY" if critical_count > 0 else "RECOMMENDED"
    lines.append(f"**Training Priority**: {priority}")
    lines.append("")

    # Group by audience
    audience_changes = defaultdict(list)
    for t in tickets:
        for role in t.get("audience", ["All Users"]):
            audience_changes[role].append(t)

    lines.append("## Changes by Team Role")
    lines.append("")
    for role, role_tickets in sorted(audience_changes.items()):
        lines.append(f"### For {role}")
        lines.append("")
        for t in role_tickets:
            is_critical = t.get("status_badge") == "Critical Fix"
            tag = " **(MANDATORY)**" if is_critical else ""
            lines.append(f"- {t['summary']}{tag}")
            lines.append(f"  - Category: {t.get('category', 'General')}")
            lines.append(f"  - Journey: {t.get('journey', 'Various')}")
        lines.append("")

    lines.append("## SOP Update Checklist")
    lines.append("| Category | Change | Priority |")
    lines.append("|----------|--------|----------|")
    for category, group_tickets_list in groups.items():
        has_critical = any(t["status_badge"] == "Critical Fix" for t in group_tickets_list)
        lines.append(f"| {category} | {len(group_tickets_list)} changes | {'P1' if has_critical else 'P2'} |")
    lines.append("")

    return "\n".join(lines)


def generate_ba_guide(tickets, groups, metadata):
    """Generate BA impact analysis"""
    lines = []
    lines.append(f"# Business Analyst Impact Analysis: {metadata['project']}")
    lines.append(f"**Release Date**: {metadata['date']}")
    lines.append("")

    # Journey impact matrix
    journey_groups = defaultdict(list)
    for t in tickets:
        journey_groups[t.get("journey", "Various")].append(t)

    lines.append("## Journey Stage Impact Matrix")
    lines.append("| Journey Stage | Changes | Impact | Tickets |")
    lines.append("|--------------|---------|--------|---------|")
    for journey, j_tickets in journey_groups.items():
        has_critical = any(t["status_badge"] == "Critical Fix" for t in j_tickets)
        impact = "HIGH" if has_critical else "MEDIUM"
        keys = ", ".join(t["key"] for t in j_tickets[:3])
        lines.append(f"| {journey} | {len(j_tickets)} | {impact} | {keys} |")
    lines.append("")

    # Detailed per journey
    for journey, j_tickets in journey_groups.items():
        lines.append(f"## {journey}")
        lines.append("")
        for t in j_tickets:
            lines.append(f"### {t['key']}: {t['summary']}")
            lines.append(f"- **Category**: {t.get('category', 'General')}")
            lines.append(f"- **Impact**: {t.get('status_badge', 'Enhancement')}")
            lines.append(f"- **Audience**: {', '.join(t.get('audience', ['All']))}")
            lines.append("")

    return "\n".join(lines)


def generate_ops_guide(tickets, groups, metadata):
    """Generate operations runbook"""
    lines = []
    lines.append(f"# Operations Runbook: {metadata['project']}")
    lines.append(f"**Release Date**: {metadata['date']}")
    critical_count = sum(1 for t in tickets if t.get("status_badge") == "Critical Fix")
    risk = "CRITICAL" if critical_count > 2 else "STANDARD"
    lines.append(f"**Risk Level**: {risk}")
    lines.append("")

    lines.append("## Deployment Summary")
    lines.append(f"| Item | Detail |")
    lines.append(f"|------|--------|")
    lines.append(f"| Total Tickets | {len(tickets)} |")
    lines.append(f"| Critical Fixes | {critical_count} |")
    lines.append(f"| Modules Affected | {', '.join(groups.keys())} |")
    lines.append("")

    # Critical items
    critical_tickets = [t for t in tickets if t.get("status_badge") == "Critical Fix"]
    if critical_tickets:
        lines.append("## Critical Changes (Monitor Closely)")
        for t in critical_tickets:
            lines.append(f"### {t['key']}: {t['summary']}")
            lines.append(f"- **Priority**: {t.get('priority', 'High')}")
            lines.append(f"- **Assignee**: {t.get('assignee', 'Unknown')} (escalation contact)")
            lines.append(f"- **Category**: {t.get('category', 'General')}")
            lines.append("")

    lines.append("## Post-Deployment Verification")
    for category in groups.keys():
        lines.append(f"- [ ] {category}: Verify changes functional")
    lines.append("")

    lines.append("## Escalation Contacts")
    assignees = set(t.get("assignee", "") for t in tickets if t.get("assignee"))
    lines.append("| Developer | Area |")
    lines.append("|-----------|------|")
    for a in sorted(assignees):
        areas = set(t["category"] for t in tickets if t.get("assignee") == a)
        lines.append(f"| {a} | {', '.join(areas)} |")
    lines.append("")

    return "\n".join(lines)


def generate_leadership_summary(tickets, groups, metadata):
    """Generate executive summary"""
    bug_count = sum(1 for t in tickets if t.get("issue_type") == "Bug")
    story_count = sum(1 for t in tickets if t.get("issue_type") == "Story")
    critical_count = sum(1 for t in tickets if t.get("status_badge") == "Critical Fix")
    cycle_times = [float(t["cycle_time"]) for t in tickets if t.get("cycle_time")]
    avg_cycle = sum(cycle_times) / len(cycle_times) if cycle_times else 0

    lines = []
    lines.append(f"# Executive Summary: {metadata['project']}")
    lines.append(f"**Date**: {metadata['date']}")
    lines.append("")

    lines.append(f"This release ships {len(tickets)} updates ({bug_count} fixes, "
                 f"{story_count} features) across {len(groups)} areas. "
                 f"{critical_count} critical production issues were resolved. "
                 f"Average delivery cycle time was {avg_cycle:.1f} days.")
    lines.append("")

    lines.append("## Key Numbers")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Features Shipped | {story_count} |")
    lines.append(f"| Bugs Fixed | {bug_count} |")
    lines.append(f"| Critical Fixes | {critical_count} |")
    lines.append(f"| Avg Cycle Time | {avg_cycle:.1f} days |")
    lines.append("")

    # Top wins
    lines.append("## Top Wins")
    for i, (category, group_tickets_list) in enumerate(list(groups.items())[:3], 1):
        lines.append(f"{i}. **{category}**: {len(group_tickets_list)} improvements shipped")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

GENERATORS = {
    "pm": generate_pm_guide,
    "qa": generate_qa_guide,
    "dev": generate_dev_guide,
    "training": generate_training_guide,
    "ba": generate_ba_guide,
    "ops": generate_ops_guide,
    "leadership": generate_leadership_summary,
}


def generate_all(tickets, stakeholders, metadata, output_dir, output_format="markdown"):
    """Generate all requested stakeholder guides"""
    # Classify all tickets
    classified = [classify_ticket(t) for t in tickets]

    # Group into categories
    groups = group_tickets(classified)

    # Generate guides
    guides = {}
    for stakeholder in stakeholders:
        if stakeholder in GENERATORS:
            guides[stakeholder] = GENERATORS[stakeholder](classified, groups, metadata)
            print(f"  Generated {stakeholder} guide ({len(guides[stakeholder])} chars)")

    # Output
    os.makedirs(output_dir, exist_ok=True)

    if output_format in ("markdown", "all"):
        for stakeholder, content in guides.items():
            filepath = os.path.join(output_dir, f"release-notes-{stakeholder}.md")
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"  Saved: {filepath}")

    if output_format in ("json", "all"):
        json_path = os.path.join(output_dir, "release-data.json")
        with open(json_path, 'w') as f:
            json.dump({
                "metadata": metadata,
                "tickets": classified,
                "groups": {k: [t["key"] for t in v] for k, v in groups.items()},
                "guides": guides,
            }, f, indent=2, default=str)
        print(f"  Saved: {json_path}")

    return guides, classified, groups


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate stakeholder-specific release notes")
    parser.add_argument("--input", required=True, help="Path to CSV or JSON ticket data")
    parser.add_argument("--output", default="./release-notes-output", help="Output directory")
    parser.add_argument("--stakeholders", default="pm,qa,dev,training,ba,ops,leadership",
                        help="Comma-separated list of stakeholders")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json", "all"],
                        help="Output format")
    parser.add_argument("--project", default="LAP", help="Project name")
    parser.add_argument("--date", default=None, help="Release date (defaults to today)")

    args = parser.parse_args()

    # Load data
    input_path = args.input
    if input_path.endswith(".csv"):
        tickets = load_csv(input_path)
    elif input_path.endswith(".json"):
        tickets = load_json(input_path)
    else:
        print(f"Unsupported format: {input_path}")
        sys.exit(1)

    print(f"Loaded {len(tickets)} tickets from {input_path}")

    # Metadata
    metadata = {
        "project": args.project,
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
    }

    # Generate
    stakeholders = [s.strip() for s in args.stakeholders.split(",")]
    print(f"Generating guides for: {', '.join(stakeholders)}")

    guides, classified, groups = generate_all(
        tickets, stakeholders, metadata, args.output, args.format
    )

    print(f"\nDone! {len(guides)} guides generated in {args.output}")


if __name__ == "__main__":
    main()
