#!/usr/bin/env python3
"""
Filter bugs against ignore rules.

Reads the bug manifest and ignore rules, marks matching bugs as 'ignored',
and outputs the filtered list.

Usage:
    python filter_bugs.py [--manifest PATH] [--rules PATH] [--dry-run]

Example:
    python filter_bugs.py
    python filter_bugs.py --dry-run  # Preview without modifying manifest
    python filter_bugs.py --manifest ./project/.debug-session/bug-manifest.yaml
"""

import argparse
import fnmatch
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import yaml
except ImportError:
    print("❌ Error: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


def load_yaml(path: Path) -> Optional[Dict]:
    """Load a YAML file."""
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text())
    except Exception as e:
        print(f"❌ Error loading {path}: {e}", file=sys.stderr)
        return None


def save_yaml(data: Dict, path: Path) -> bool:
    """Save data to YAML file."""
    # Check write permissions explicitly (chmod doesn't block root)
    parent_dir = path.parent if path.parent != Path() else Path('.')
    if not os.access(parent_dir, os.W_OK):
        return False

    try:
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        return True
    except Exception as e:
        print(f"❌ Error saving {path}: {e}", file=sys.stderr)
        return False


def is_rule_expired(rule: Dict) -> bool:
    """Check if a rule has expired."""
    expires = rule.get("expires")
    if not expires:
        return False
    
    try:
        expire_date = datetime.fromisoformat(str(expires).replace('Z', '+00:00'))
        return datetime.now().astimezone() > expire_date
    except (ValueError, TypeError):
        # Try parsing as date only
        try:
            expire_date = datetime.strptime(str(expires), "%Y-%m-%d")
            return datetime.now() > expire_date
        except (ValueError, TypeError):
            return False


def rule_matches_bug(rule: Dict, bug: Dict, file_content: Optional[str] = None) -> bool:
    """
    Check if an ignore rule matches a bug.
    
    Matching criteria (any match triggers ignore):
    1. Pattern match on file content at bug line
    2. File glob match on bug location
    3. Category match (rule applies to bug's category)
    """
    # Skip expired rules
    if is_rule_expired(rule):
        return False
    
    bug_file = bug.get("location", {}).get("file", "")
    bug_line = bug.get("location", {}).get("line", 0)
    bug_category = bug.get("category", "")
    
    # Check category restriction first
    rule_categories = rule.get("categories", [])
    if rule_categories and bug_category not in rule_categories:
        return False
    
    # Check file glob
    file_glob = rule.get("file_glob")
    if file_glob:
        if fnmatch.fnmatch(bug_file, file_glob):
            return True
    
    # Check pattern (regex or literal)
    pattern = rule.get("pattern")
    if pattern and file_content:
        try:
            lines = file_content.split('\n')
            if 0 < bug_line <= len(lines):
                line_content = lines[bug_line - 1]
                # Try regex first, fall back to literal
                try:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        return True
                except re.error:
                    if pattern.lower() in line_content.lower():
                        return True
        except (IndexError, TypeError, AttributeError):
            pass

    return False


def filter_bugs(manifest_path: Path, rules_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Apply ignore rules to bugs in manifest.
    
    Returns:
        Dict with counts: {'matched': N, 'expired_rules': N, 'already_ignored': N}
    """
    stats = {'matched': 0, 'expired_rules': 0, 'already_ignored': 0, 'pending': 0}
    
    # Load manifest
    manifest = load_yaml(manifest_path)
    if not manifest:
        print(f"❌ Manifest not found: {manifest_path}", file=sys.stderr)
        return stats
    
    # Load rules
    rules_data = load_yaml(rules_path)
    rules = rules_data.get("rules", []) if rules_data else []
    
    if not rules:
        print("ℹ️  No ignore rules defined", file=sys.stderr)
        return stats
    
    # Count expired rules
    for rule in rules:
        if is_rule_expired(rule):
            stats['expired_rules'] += 1
            print(f"⚠️  Expired rule: {rule.get('id', 'unknown')}", file=sys.stderr)
    
    # Cache file contents for pattern matching
    file_cache: Dict[str, str] = {}
    
    # Process each bug
    bugs = manifest.get("bugs", [])
    for bug in bugs:
        # Skip already processed
        if bug.get("status") == "ignored":
            stats['already_ignored'] += 1
            continue
        
        if bug.get("status") in ["fixed", "verified"]:
            continue
        
        # Get file content for pattern matching
        bug_file = bug.get("location", {}).get("file", "")
        if bug_file and bug_file not in file_cache:
            try:
                file_cache[bug_file] = Path(bug_file).read_text(encoding='utf-8', errors='ignore')
            except (OSError, IOError):
                file_cache[bug_file] = ""
        
        file_content = file_cache.get(bug_file, "")
        
        # Check each rule
        for rule in rules:
            if is_rule_expired(rule):
                continue
                
            if rule_matches_bug(rule, bug, file_content):
                if not dry_run:
                    bug["status"] = "ignored"
                    bug["ignore_rule"] = rule.get("id", "unknown")
                    bug["ignored_at"] = datetime.now().isoformat()
                stats['matched'] += 1
                print(f"🚫 Ignored: {bug['id']} - {bug.get('description', '')} (rule: {rule.get('id')})")
                break
        else:
            if bug.get("status") == "pending":
                stats['pending'] += 1
    
    # Update manifest stats
    if not dry_run and stats['matched'] > 0:
        manifest_stats = manifest.get("stats", {})
        manifest_stats["ignored"] = manifest_stats.get("ignored", 0) + stats['matched']
        manifest_stats["pending"] = manifest_stats.get("pending", 0) - stats['matched']
        manifest["stats"] = manifest_stats
        
        if save_yaml(manifest, manifest_path):
            print(f"\n✅ Updated manifest: {stats['matched']} bugs ignored")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Filter bugs against ignore rules"
    )
    parser.add_argument("--manifest", "-m", default=".debug-session/bug-manifest.yaml",
                       help="Path to bug manifest")
    parser.add_argument("--rules", "-r", default=".debug-session/ignore-rules.yaml",
                       help="Path to ignore rules")
    parser.add_argument("--dry-run", "-n", action="store_true",
                       help="Preview matches without modifying manifest")
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    rules_path = Path(args.rules)
    
    if args.dry_run:
        print("🔍 Dry run - no changes will be made\n")
    
    stats = filter_bugs(manifest_path, rules_path, args.dry_run)
    
    print(f"\n📊 Summary:")
    print(f"   Matched & ignored: {stats['matched']}")
    print(f"   Already ignored: {stats['already_ignored']}")
    print(f"   Remaining pending: {stats['pending']}")
    if stats['expired_rules'] > 0:
        print(f"   ⚠️  Expired rules: {stats['expired_rules']}")


if __name__ == "__main__":
    main()
