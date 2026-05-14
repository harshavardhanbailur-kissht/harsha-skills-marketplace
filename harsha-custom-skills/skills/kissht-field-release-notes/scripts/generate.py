#!/usr/bin/env python3
"""
generate.py — Scaffolding skeleton for kissht-field-release-notes skill.

Takes one or more LAP Jira ticket keys and emits a DRAFT release note pre-populated
with the title placeholder from templates/release-note-template.md (Pattern A only).

Usage:
    python generate.py LAP-2180 LAP-2181 LAP-2222 --feature-name "DigiLocker Journey Revamp" --out drafts/digilocker.md
    python generate.py LAP-2154 --feature-name "LSQ Renach Handling" --pattern branching_outcome --out drafts/renach.md

IMPORTANT — THIS IS A SKELETON:
  - fetch_ticket() is a stub that raises NotImplementedError.
    Wire up the Atlassian MCP (getJiraIssue) before using in production.
  - populate_template() only fills the title; all other placeholders remain.
    The LLM step (Claude running the skill) does the real population.
  - verify() supports both patterns: workflow_change and branching_outcome.
    Pass --pattern to select. Defaults to workflow_change.
  - The skill itself runs end-to-end through Claude. This script is here
    for users who want to scaffold a draft locally before iterating.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = SKILL_ROOT / "templates" / "release-note-template.md"
GLOSSARY_PATH = SKILL_ROOT / "references" / "lap-glossary.md"
STAGES_KB_PATH = SKILL_ROOT / "knowledge-base" / "lap-stages.md"


def fetch_ticket(key: str) -> dict[str, Any]:
    """Fetch a Jira ticket. Stub — replace with the real MCP call when wiring up."""
    # In production, this is replaced by:
    #   getJiraIssue(cloudId="76a6058f-...", issueIdOrKey=key,
    #                fields=[...], responseContentFormat="markdown")
    raise NotImplementedError(
        "fetch_ticket is a stub. The skill itself runs the Atlassian MCP "
        "call directly. Wire this up only if running the pipeline locally."
    )


def decompose(ticket: dict[str, Any]) -> dict[str, Any]:
    """
    Map Jira fields to release-note beats.
    See references/jira-to-release-note.md for the full mapping table.
    """
    fields = ticket.get("fields", {})
    return {
        "key": ticket.get("key"),
        "summary": fields.get("summary", ""),
        "description": fields.get("description", ""),
        "status": fields.get("status", {}).get("name"),
        "issuetype": fields.get("issuetype", {}).get("name"),
        "reporter": fields.get("reporter", {}).get("displayName"),
        "assignee": fields.get("assignee", {}).get("displayName"),
        "parent_summary": (fields.get("parent") or {})
            .get("fields", {})
            .get("summary"),
    }


def reconcile(decomposed: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge multi-ticket bundles into a single release-note input."""
    if not decomposed:
        raise ValueError("No tickets to reconcile")
    if len(decomposed) == 1:
        return decomposed[0]

    # Multi-ticket bundle: pick the latest-resolved as authoritative for the
    # flow, but consolidate rules and contacts across all tickets.
    primary = decomposed[0]
    return {
        "key": ", ".join(d["key"] for d in decomposed),
        "summary": primary["summary"],
        "descriptions": [d["description"] for d in decomposed],
        "reporters": list({d["reporter"] for d in decomposed if d.get("reporter")}),
        "assignees": list({d["assignee"] for d in decomposed if d.get("assignee")}),
        "tickets": decomposed,
    }


def populate_template(reconciled: dict[str, Any], feature_name: str) -> str:
    """Populate the release-note template. Returns markdown string."""
    template = TEMPLATE_PATH.read_text()
    # The template uses <…> placeholders. In production, the LLM step
    # populates these by reading the reconciled input + glossary.
    # Here we just stamp the title and leave placeholders.
    return template.replace("<Feature Name>", feature_name)


def verify(draft: str, pattern: str = "workflow_change") -> list[str]:
    """
    Run the §7 Phase 7 verification gate from SKILL.md. Returns list of failures.

    Args:
        draft:   The markdown draft text.
        pattern: "workflow_change" (Pattern A — Relook) or
                 "branching_outcome" (Pattern B — Renach).
                 Defaults to "workflow_change".
    """
    failures: list[str] = []

    # ── Universal checks (both patterns) ──────────────────────────────────────
    if not draft.strip().startswith("# Release Note:"):
        failures.append("Title must start with '# Release Note: '.")

    if "## For any issues or clarifications" not in draft:
        failures.append("Contacts block ('## For any issues or clarifications') missing.")

    word_count = len(draft.split())
    if word_count > 900:
        failures.append(
            f"Length: {word_count} words. Target ≤ 600 for single-feature notes; "
            "anything > 900 should be split."
        )

    # ── Pattern A — Workflow Change ────────────────────────────────────────────
    if pattern == "workflow_change":
        if "## The new flow" not in draft:
            failures.append("Workflow Change: '## The new flow' heading missing.")
        if "→" not in draft:
            failures.append("Workflow Change: Flow arrow diagram (→) missing.")
        if "Stages in the system" not in draft:
            failures.append("Workflow Change: 'Stages in the system' list missing.")
        if "## Key rules" not in draft:
            failures.append("Workflow Change: '## Key rules' heading missing.")
        if "## What this means for you" not in draft:
            failures.append("Workflow Change: '## What this means for you' heading missing.")

    # ── Pattern B — Branching Outcome ─────────────────────────────────────────
    elif pattern == "branching_outcome":
        # Negative checks: Pattern B must NOT contain Pattern-A constructs.
        if "## The new flow" in draft:
            failures.append(
                "Branching Outcome: '## The new flow' found — this heading belongs to "
                "Workflow Change only. Replace with '## What this is about'."
            )
        if "Stages in the system" in draft:
            failures.append(
                "Branching Outcome: 'Stages in the system' list found — this belongs to "
                "Workflow Change only. The stage is unchanged in Branching Outcome; "
                "embed the locator inside '## What you do' instead."
            )
        # Positive checks: Pattern B required headings.
        if "## What this is about" not in draft:
            failures.append("Branching Outcome: '## What this is about' heading missing.")
        if "## What you do" not in draft:
            failures.append("Branching Outcome: '## What you do' heading missing.")
        if "## What happens next" not in draft:
            failures.append("Branching Outcome: '## What happens next' heading missing.")

    else:
        failures.append(
            f"Unknown pattern '{pattern}'. Use 'workflow_change' or 'branching_outcome'."
        )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Kissht field release note.")
    parser.add_argument("tickets", nargs="+", help="LAP Jira ticket keys (e.g. LAP-2180 LAP-2181)")
    parser.add_argument("--feature-name", required=True, help="Colloquial feature name for the title")
    parser.add_argument(
        "--pattern",
        choices=["workflow_change", "branching_outcome"],
        default="workflow_change",
        help="Release note pattern: workflow_change (Relook/Pattern A) or branching_outcome (Renach/Pattern B). Default: workflow_change",
    )
    parser.add_argument("--out", type=Path, default=Path("draft.md"), help="Output path for draft")
    args = parser.parse_args()

    print(f"[generate] Fetching {len(args.tickets)} ticket(s)…", file=sys.stderr)
    decomposed = []
    for key in args.tickets:
        try:
            ticket = fetch_ticket(key)
        except NotImplementedError as exc:
            print(f"[generate] {exc}", file=sys.stderr)
            print(
                "[generate] Stub mode — emitting an unfilled template draft.",
                file=sys.stderr,
            )
            draft = populate_template({}, args.feature_name)
            args.out.write_text(draft)
            print(f"[generate] Draft template written to {args.out}", file=sys.stderr)
            return 0
        decomposed.append(decompose(ticket))

    reconciled = reconcile(decomposed)
    draft = populate_template(reconciled, args.feature_name)

    print(f"[generate] Running verification gate (pattern: {args.pattern})…", file=sys.stderr)
    failures = verify(draft, pattern=args.pattern)
    if failures:
        print("[generate] VERIFICATION FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print("[generate] Draft written anyway for inspection.", file=sys.stderr)
    else:
        print("[generate] All gates passed.", file=sys.stderr)

    args.out.write_text(draft)
    print(f"[generate] Draft written to {args.out}", file=sys.stderr)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
