#!/usr/bin/env python3
"""
Build self-contained HTML web guide from release notes data.
Generates a single HTML file with role-based tabs, search, and filtering.

Usage:
    python build_web_guide.py --input release-data.json --output release-notes.html
    python build_web_guide.py --input tickets.csv --project LAP --output release-notes.html
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from html import escape

# Import the generator if available
try:
    from generate_release_notes import load_csv, load_json, classify_ticket, group_tickets, GENERATORS
except ImportError:
    # Running standalone — minimal classification
    pass


def build_html(guides, tickets, groups, metadata):
    """Build self-contained HTML with all guides embedded"""

    ticket_json = json.dumps(tickets, default=str)
    guide_sections = ""

    tab_names = {
        "pm": "Product Manager",
        "qa": "QA Engineer",
        "dev": "Developer",
        "training": "Training",
        "ba": "Business Analyst",
        "ops": "Operations",
        "leadership": "Leadership",
    }

    # Build tab buttons
    tab_buttons = ""
    for key in guides:
        name = tab_names.get(key, key.title())
        active = "active" if key == list(guides.keys())[0] else ""
        tab_buttons += f'<button class="tab-btn {active}" data-tab="{key}">{name}</button>\n'

    # Build tab content
    tab_contents = ""
    for key, content in guides.items():
        active = "active" if key == list(guides.keys())[0] else ""
        # Convert markdown to basic HTML
        html_content = markdown_to_html(content)
        tab_contents += f'<div class="tab-content {active}" id="tab-{key}">{html_content}</div>\n'

    # Stats
    total = len(tickets)
    bugs = sum(1 for t in tickets if t.get("issue_type") == "Bug")
    stories = sum(1 for t in tickets if t.get("issue_type") == "Story")
    critical = sum(1 for t in tickets if t.get("status_badge") == "Critical Fix")
    categories = list(groups.keys()) if groups else []

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Release Notes: {escape(metadata.get('project', 'Project'))} — {escape(metadata.get('date', ''))}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 24px 32px; }}
.header h1 {{ font-size: 24px; font-weight: 600; }}
.header .meta {{ font-size: 14px; opacity: 0.8; margin-top: 8px; }}
.stats {{ display: flex; gap: 24px; margin-top: 16px; flex-wrap: wrap; }}
.stat {{ background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px 20px; }}
.stat .num {{ font-size: 28px; font-weight: 700; }}
.stat .label {{ font-size: 12px; opacity: 0.7; text-transform: uppercase; }}
.controls {{ background: white; border-bottom: 1px solid #e0e0e0; padding: 12px 32px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; position: sticky; top: 0; z-index: 100; }}
.search {{ flex: 1; min-width: 200px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }}
.filter-btn {{ padding: 6px 14px; border: 1px solid #ddd; border-radius: 20px; background: white; cursor: pointer; font-size: 13px; transition: all 0.2s; }}
.filter-btn:hover, .filter-btn.active {{ background: #1a1a2e; color: white; border-color: #1a1a2e; }}
.tabs {{ background: white; padding: 0 32px; border-bottom: 2px solid #e0e0e0; display: flex; gap: 0; overflow-x: auto; }}
.tab-btn {{ padding: 14px 24px; border: none; background: none; cursor: pointer; font-size: 14px; font-weight: 500; color: #666; border-bottom: 3px solid transparent; transition: all 0.2s; white-space: nowrap; }}
.tab-btn:hover {{ color: #333; }}
.tab-btn.active {{ color: #1a1a2e; border-bottom-color: #1a1a2e; }}
.content {{ max-width: 900px; margin: 24px auto; padding: 0 32px; }}
.tab-content {{ display: none; background: white; border-radius: 12px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.tab-content.active {{ display: block; }}
.tab-content h1 {{ font-size: 22px; margin-bottom: 16px; color: #1a1a2e; }}
.tab-content h2 {{ font-size: 18px; margin: 24px 0 12px; color: #333; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
.tab-content h3 {{ font-size: 15px; margin: 16px 0 8px; color: #555; }}
.tab-content p {{ line-height: 1.6; margin-bottom: 12px; }}
.tab-content ul {{ margin: 8px 0 16px 24px; }}
.tab-content li {{ margin-bottom: 6px; line-height: 1.5; }}
.tab-content table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }}
.tab-content th {{ background: #f8f9fa; padding: 10px 12px; text-align: left; border: 1px solid #e0e0e0; font-weight: 600; }}
.tab-content td {{ padding: 8px 12px; border: 1px solid #e0e0e0; }}
.tab-content tr:nth-child(even) {{ background: #fafafa; }}
.tab-content a {{ color: #2563eb; text-decoration: none; }}
.tab-content a:hover {{ text-decoration: underline; }}
.badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
.badge-critical {{ background: #EA4335; color: white; }}
.badge-live {{ background: #34A853; color: white; }}
.badge-enhancement {{ background: #FBBC04; color: #333; }}
.footer {{ text-align: center; padding: 24px; color: #999; font-size: 12px; }}
.highlight {{ background: #fff3cd; padding: 2px 4px; border-radius: 2px; }}
input[type="checkbox"] {{ margin-right: 8px; }}
@media (max-width: 768px) {{
  .header {{ padding: 16px; }}
  .stats {{ gap: 12px; }}
  .stat {{ padding: 8px 14px; }}
  .stat .num {{ font-size: 20px; }}
  .controls {{ padding: 8px 16px; }}
  .tabs {{ padding: 0 16px; }}
  .content {{ padding: 0 16px; }}
  .tab-content {{ padding: 20px; }}
}}
@media print {{
  .controls, .tabs, .footer {{ display: none; }}
  .tab-content {{ display: block !important; page-break-after: always; box-shadow: none; }}
  .header {{ background: white; color: black; }}
}}
</style>
</head>
<body>
<div class="header">
  <h1>Release Notes: {escape(metadata.get('project', 'Project'))} {escape(metadata.get('version', ''))}</h1>
  <div class="meta">Release Date: {escape(metadata.get('date', datetime.now().strftime('%Y-%m-%d')))} | Generated by Kissht Release Notes Mastery</div>
  <div class="stats">
    <div class="stat"><div class="num">{total}</div><div class="label">Total Tickets</div></div>
    <div class="stat"><div class="num">{bugs}</div><div class="label">Bugs Fixed</div></div>
    <div class="stat"><div class="num">{stories}</div><div class="label">Features</div></div>
    <div class="stat"><div class="num">{critical}</div><div class="label">Critical Fixes</div></div>
    <div class="stat"><div class="num">{len(categories)}</div><div class="label">Categories</div></div>
  </div>
</div>

<div class="controls">
  <input type="text" class="search" placeholder="Search across all guides..." id="searchInput">
  <button class="filter-btn" onclick="window.print()">Print</button>
</div>

<div class="tabs">
  {tab_buttons}
</div>

<div class="content">
  {tab_contents}
</div>

<div class="footer">
  Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Kissht Release Notes Mastery Skill
</div>

<script>
// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  }});
}});

// Search
document.getElementById('searchInput').addEventListener('input', function(e) {{
  const query = e.target.value.toLowerCase();
  if (!query) {{
    document.querySelectorAll('.highlight').forEach(el => {{
      el.outerHTML = el.textContent;
    }});
    return;
  }}
  // Simple search highlight — find text in active tab
  const active = document.querySelector('.tab-content.active');
  if (active) {{
    // Reset first
    active.querySelectorAll('.highlight').forEach(el => {{
      el.outerHTML = el.textContent;
    }});
  }}
}});

// Keyboard navigation
document.addEventListener('keydown', (e) => {{
  const tabs = document.querySelectorAll('.tab-btn');
  const activeIdx = [...tabs].findIndex(t => t.classList.contains('active'));
  if (e.key === 'ArrowRight' && activeIdx < tabs.length - 1) {{
    tabs[activeIdx + 1].click();
  }} else if (e.key === 'ArrowLeft' && activeIdx > 0) {{
    tabs[activeIdx - 1].click();
  }}
}});
</script>
</body>
</html>"""

    return html


def markdown_to_html(md_text):
    """Convert basic markdown to HTML (no external dependencies)"""
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_list = False
    in_checklist = False

    for line in lines:
        stripped = line.strip()

        # Headers
        if stripped.startswith('# '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append(f'<h1>{escape(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append(f'<h2>{escape(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append(f'<h3>{escape(stripped[4:])}</h3>')
        # Table
        elif stripped.startswith('|'):
            if not in_table:
                if in_list: html_lines.append('</ul>'); in_list = False
                html_lines.append('<table>')
                in_table = True
            if stripped.replace('|', '').replace('-', '').replace(' ', '') == '':
                continue  # Skip separator row
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            tag = 'th' if not any('<td>' in l for l in html_lines[-5:] if '<t' in l) else 'td'
            row = '<tr>' + ''.join(f'<{tag}>{escape(c)}</{tag}>' for c in cells) + '</tr>'
            html_lines.append(row)
        # Checklist
        elif stripped.startswith('- [ ]') or stripped.startswith('- [x]'):
            if in_table: html_lines.append('</table>'); in_table = False
            if not in_checklist:
                html_lines.append('<ul style="list-style:none;padding-left:8px;">')
                in_checklist = True
            checked = 'checked' if '[x]' in stripped else ''
            text = stripped.replace('- [ ]', '').replace('- [x]', '').strip()
            html_lines.append(f'<li><input type="checkbox" {checked} disabled>{escape(text)}</li>')
        # Unordered list
        elif stripped.startswith('- '):
            if in_table: html_lines.append('</table>'); in_table = False
            if in_checklist: html_lines.append('</ul>'); in_checklist = False
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            # Handle bold markers
            text = stripped[2:]
            text = bold_and_links(text)
            html_lines.append(f'<li>{text}</li>')
        # Numbered list
        elif stripped and stripped[0].isdigit() and '. ' in stripped[:4]:
            if in_table: html_lines.append('</table>'); in_table = False
            text = stripped.split('. ', 1)[1] if '. ' in stripped else stripped
            text = bold_and_links(text)
            html_lines.append(f'<li>{text}</li>')
        # Horizontal rule
        elif stripped == '---':
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append('<hr>')
        # Empty line
        elif not stripped:
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_checklist: html_lines.append('</ul>'); in_checklist = False
            if in_table: html_lines.append('</table>'); in_table = False
        # Regular text
        else:
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_table: html_lines.append('</table>'); in_table = False
            text = bold_and_links(escape(stripped))
            html_lines.append(f'<p>{text}</p>')

    if in_list: html_lines.append('</ul>')
    if in_table: html_lines.append('</table>')
    if in_checklist: html_lines.append('</ul>')

    return '\n'.join(html_lines)


def bold_and_links(text):
    """Convert **bold** and [text](url) in text"""
    import re
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text


def main():
    parser = argparse.ArgumentParser(description="Build HTML release notes web guide")
    parser.add_argument("--input", required=True, help="Path to release-data.json or tickets.csv")
    parser.add_argument("--output", default="release-notes.html", help="Output HTML file")
    parser.add_argument("--project", default="LAP", help="Project name")
    parser.add_argument("--date", default=None, help="Release date")
    parser.add_argument("--version", default="", help="Version/sprint name")

    args = parser.parse_args()

    metadata = {
        "project": args.project,
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "version": args.version,
    }

    if args.input.endswith(".json"):
        with open(args.input) as f:
            data = json.load(f)
        guides = data.get("guides", {})
        tickets = data.get("tickets", [])
        groups = data.get("groups", {})
        if "metadata" in data:
            metadata.update(data["metadata"])
    elif args.input.endswith(".csv"):
        # Need to generate guides from CSV
        try:
            from generate_release_notes import load_csv, classify_ticket, group_tickets, GENERATORS
        except ImportError:
            print("Error: generate_release_notes.py must be in the same directory for CSV input")
            sys.exit(1)

        raw_tickets = load_csv(args.input)
        tickets = [classify_ticket(t) for t in raw_tickets]
        groups = group_tickets(tickets)
        guides = {}
        for stakeholder, gen_func in GENERATORS.items():
            guides[stakeholder] = gen_func(tickets, groups, metadata)
    else:
        print(f"Unsupported input format: {args.input}")
        sys.exit(1)

    # Build HTML
    html = build_html(guides, tickets, groups, metadata)

    with open(args.output, 'w') as f:
        f.write(html)

    print(f"Web guide saved to: {args.output}")
    size_kb = os.path.getsize(args.output) / 1024
    print(f"File size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
