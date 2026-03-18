#!/usr/bin/env python3
"""
Jira Poller for Kissht Release Notes
Polls Jira for completed tickets and feeds them to the release notes generator.

Usage:
    python jira_poller.py --domain kissht.atlassian.net --email user@kissht.com --token YOUR_TOKEN --project LAP --since 168
    python jira_poller.py --domain kissht.atlassian.net --email user@kissht.com --token YOUR_TOKEN --project LAP --sprint "Sprint 23"
    python jira_poller.py --config jira_config.json --since 24

Configuration file (jira_config.json):
{
    "domain": "kissht.atlassian.net",
    "email": "user@kissht.com",
    "api_token": "YOUR_API_TOKEN",
    "project_key": "LAP"
}
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("Install requests: pip install requests --break-system-packages")
    sys.exit(1)


class JiraPoller:
    """Polls Jira Cloud for completed tickets"""

    def __init__(self, domain, email, api_token, project_key):
        self.base_url = f"https://{domain}"
        self.auth = (email, api_token)
        self.project_key = project_key

    def test_connection(self):
        """Verify credentials work"""
        resp = requests.get(
            f"{self.base_url}/rest/api/3/myself",
            auth=self.auth
        )
        if resp.status_code == 200:
            user = resp.json()
            print(f"Connected as: {user['displayName']} ({user.get('emailAddress', 'N/A')})")
            return True
        else:
            print(f"Connection failed: {resp.status_code} — {resp.text[:200]}")
            return False

    def get_done_tickets(self, since_hours=168):
        """Fetch tickets moved to Done in the last N hours"""
        jql = (
            f'project = {self.project_key} '
            f'AND status changed to Done AFTER -{since_hours}h '
            f'ORDER BY updated DESC'
        )
        return self._search(jql)

    def get_sprint_tickets(self, sprint_name):
        """Fetch all Done tickets in a specific sprint"""
        jql = (
            f'project = {self.project_key} '
            f'AND sprint = "{sprint_name}" '
            f'AND status = Done '
            f'ORDER BY resolutiondate DESC'
        )
        return self._search(jql)

    def get_version_tickets(self, fix_version):
        """Fetch all tickets in a fix version"""
        jql = (
            f'project = {self.project_key} '
            f'AND fixVersion = "{fix_version}" '
            f'AND status = Done'
        )
        return self._search(jql)

    def get_all_done(self):
        """Fetch ALL Done tickets (use with caution)"""
        jql = (
            f'project = {self.project_key} '
            f'AND status = Done '
            f'ORDER BY resolutiondate DESC'
        )
        return self._search(jql)

    def _search(self, jql, fields=None):
        """Execute JQL search with pagination"""
        if fields is None:
            fields = (
                "summary,issuetype,priority,status,assignee,reporter,"
                "created,resolutiondate,fixVersions,labels,components"
            )

        all_issues = []
        start_at = 0
        max_results = 50

        while True:
            resp = requests.get(
                f"{self.base_url}/rest/api/3/search",
                auth=self.auth,
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": fields,
                    "expand": "changelog"
                }
            )

            if resp.status_code != 200:
                print(f"Search failed: {resp.status_code} — {resp.text[:200]}")
                break

            data = resp.json()
            issues = data.get("issues", [])
            all_issues.extend(issues)

            total = data.get("total", 0)
            print(f"  Fetched {len(all_issues)}/{total} issues...")

            if start_at + len(issues) >= total:
                break
            start_at += len(issues)
            time.sleep(0.5)  # Rate limiting

        return all_issues

    def enrich_ticket(self, issue):
        """Extract structured data from a Jira issue"""
        fields = issue["fields"]
        key = issue["key"]

        # Get completed date from changelog
        completed_date = self._get_completed_date(issue)

        # Get contributors
        commenters = self._get_commenters(key)
        worklog_authors = self._get_worklog_authors(key)
        past_assignees = self._get_past_assignees(issue)

        # Calculate cycle time
        created = fields.get("created", "")
        cycle_time = self._calc_cycle_time(created, completed_date)

        return {
            "key": key,
            "link": f"{self.base_url}/browse/{key}",
            "summary": fields.get("summary", ""),
            "issue_type": (fields.get("issuetype") or {}).get("name", ""),
            "priority": (fields.get("priority") or {}).get("name", ""),
            "status": (fields.get("status") or {}).get("name", ""),
            "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
            "reporter": (fields.get("reporter") or {}).get("displayName", ""),
            "created": created,
            "completed": completed_date,
            "commenters": ", ".join(commenters),
            "worklog": ", ".join(worklog_authors),
            "past_assignees": ", ".join(past_assignees),
            "cycle_time": str(cycle_time) if cycle_time else "",
            "labels": [l for l in fields.get("labels", [])],
            "components": [c["name"] for c in fields.get("components", [])],
        }

    def _get_completed_date(self, issue):
        """Extract the date when ticket was moved to Done"""
        changelog = issue.get("changelog", {})
        completed = ""
        for history in changelog.get("histories", []):
            for item in history.get("items", []):
                if item.get("field") == "status" and (item.get("toString") or "").lower() == "done":
                    completed = history.get("created", "")
        # Fallback to resolution date
        if not completed:
            completed = issue["fields"].get("resolutiondate", "")
        return completed

    def _get_commenters(self, key):
        """Get unique commenter names"""
        resp = requests.get(
            f"{self.base_url}/rest/api/3/issue/{key}/comment",
            auth=self.auth
        )
        if resp.status_code != 200:
            return []
        comments = resp.json().get("comments", [])
        names = set()
        for c in comments:
            author = c.get("author", {})
            if author.get("displayName"):
                names.add(author["displayName"])
        return sorted(names)

    def _get_worklog_authors(self, key):
        """Get unique worklog author names"""
        resp = requests.get(
            f"{self.base_url}/rest/api/3/issue/{key}/worklog",
            auth=self.auth
        )
        if resp.status_code != 200:
            return []
        worklogs = resp.json().get("worklogs", [])
        names = set()
        for w in worklogs:
            author = w.get("author", {})
            if author.get("displayName"):
                names.add(author["displayName"])
        return sorted(names)

    def _get_past_assignees(self, issue):
        """Extract past assignees from changelog"""
        changelog = issue.get("changelog", {})
        names = set()
        for history in changelog.get("histories", []):
            for item in history.get("items", []):
                if item.get("field") == "assignee":
                    if item.get("fromString"):
                        names.add(item["fromString"])
                    if item.get("toString"):
                        names.add(item["toString"])
        return sorted(names)

    def _calc_cycle_time(self, created, completed):
        """Calculate cycle time in days"""
        if not created or not completed:
            return None
        try:
            c = datetime.fromisoformat(created.replace("Z", "+00:00"))
            d = datetime.fromisoformat(completed.replace("Z", "+00:00"))
            diff = (d - c).total_seconds() / 86400
            return round(diff, 1)
        except Exception:
            return None


def main():
    parser = argparse.ArgumentParser(description="Poll Jira for completed tickets")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--domain", help="Jira domain (e.g., kissht.atlassian.net)")
    parser.add_argument("--email", help="Jira email")
    parser.add_argument("--token", help="Jira API token")
    parser.add_argument("--project", default="LAP", help="Project key")
    parser.add_argument("--since", type=int, default=168, help="Hours to look back (default: 168 = 7 days)")
    parser.add_argument("--sprint", help="Sprint name to fetch")
    parser.add_argument("--version", help="Fix version to fetch")
    parser.add_argument("--output", default="tickets.json", help="Output file path")
    parser.add_argument("--enrich", action="store_true", help="Fetch full contributor data (slower)")
    parser.add_argument("--csv", action="store_true", help="Output as CSV instead of JSON")

    args = parser.parse_args()

    # Load config
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        domain = config.get("domain", args.domain)
        email = config.get("email", args.email)
        token = config.get("api_token", args.token)
        project = config.get("project_key", args.project)
    else:
        domain = args.domain
        email = args.email
        token = args.token
        project = args.project

    if not all([domain, email, token]):
        print("Error: domain, email, and token are required (via args or config file)")
        sys.exit(1)

    # Initialize poller
    poller = JiraPoller(domain, email, token, project)

    # Test connection
    if not poller.test_connection():
        sys.exit(1)

    # Fetch tickets
    if args.sprint:
        print(f"Fetching sprint '{args.sprint}' tickets...")
        issues = poller.get_sprint_tickets(args.sprint)
    elif args.version:
        print(f"Fetching version '{args.version}' tickets...")
        issues = poller.get_version_tickets(args.version)
    else:
        print(f"Fetching tickets completed in last {args.since} hours...")
        issues = poller.get_done_tickets(args.since)

    print(f"Found {len(issues)} tickets")

    # Enrich if requested
    if args.enrich:
        print("Enriching tickets with contributor data...")
        tickets = []
        for i, issue in enumerate(issues):
            tickets.append(poller.enrich_ticket(issue))
            if (i + 1) % 10 == 0:
                print(f"  Enriched {i + 1}/{len(issues)}")
            time.sleep(0.3)
    else:
        # Basic extraction without extra API calls
        tickets = []
        for issue in issues:
            fields = issue["fields"]
            tickets.append({
                "key": issue["key"],
                "link": f"{poller.base_url}/browse/{issue['key']}",
                "summary": fields.get("summary", ""),
                "issue_type": (fields.get("issuetype") or {}).get("name", ""),
                "priority": (fields.get("priority") or {}).get("name", ""),
                "status": (fields.get("status") or {}).get("name", ""),
                "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
                "reporter": (fields.get("reporter") or {}).get("displayName", ""),
                "created": fields.get("created", ""),
                "completed": fields.get("resolutiondate", ""),
                "cycle_time": "",
            })

    # Save output
    if args.csv:
        import csv
        output_path = args.output.replace('.json', '.csv') if args.output.endswith('.json') else args.output
        with open(output_path, 'w', newline='') as f:
            if tickets:
                writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
                writer.writeheader()
                writer.writerows(tickets)
        print(f"Saved {len(tickets)} tickets to {output_path}")
    else:
        with open(args.output, 'w') as f:
            json.dump({"tickets": tickets, "count": len(tickets), "fetched_at": datetime.now().isoformat()}, f, indent=2)
        print(f"Saved {len(tickets)} tickets to {args.output}")


if __name__ == "__main__":
    main()
