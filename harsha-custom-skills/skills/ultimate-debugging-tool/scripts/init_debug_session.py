#!/usr/bin/env python3
"""
Initialize a Gas Debugger session for a project.

Creates .debug-session/ directory with:
- bug-manifest.yaml (empty template)
- ignore-rules.yaml (default rules)
- session.yaml (session metadata)

Usage:
    python init_debug_session.py <project_path> [--goal "description"]

Example:
    python init_debug_session.py ./my-project --goal "Fix auth vulnerabilities"
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
import uuid

DEFAULT_IGNORE_RULES = """# Gas Debugger Ignore Rules
# Add patterns here to skip known false positives

rules:
  # Example: Testing credentials (uncomment and modify as needed)
  # - id: "v0-testing-creds"
  #   pattern: "password.*=.*['\"]1111['\"]"
  #   reason: "V0 testing credential"
  #   expires: "2025-03-01"
  #   categories: ["security"]
  
  # Example: Test fixtures
  # - id: "test-fixtures"
  #   file_glob: "tests/**"
  #   categories: ["security"]
  #   reason: "Test fixtures don't require production security"
  
  # Example: TODO markers
  # - id: "todo-markers"
  #   pattern: "TODO:|FIXME:"
  #   reason: "Intentional technical debt markers"
  #   categories: ["quality"]
"""

MANIFEST_TEMPLATE = """# Gas Debugger Bug Manifest
# Auto-generated - do not edit status fields manually during active session

session:
  id: "{session_id}"
  started: "{timestamp}"
  original_goal: "{goal}"
  project_path: "{project_path}"
  
stats:
  total_found: 0
  pending: 0
  fixing: 0
  fixed: 0
  verified: 0
  ignored: 0
  
bugs: []
"""

SESSION_TEMPLATE = """# Gas Debugger Session Metadata
session:
  id: "{session_id}"
  started: "{timestamp}"
  project_path: "{project_path}"
  goal: "{goal}"
  
state:
  current_phase: "initialized"  # initialized | scanning | fixing | verifying | complete
  last_bug_id: null
  scan_categories_completed: []
  
history:
  - timestamp: "{timestamp}"
    action: "session_initialized"
    details: "Created new debug session"
"""


def init_session(project_path: str, goal: str = "Debug and fix code issues") -> bool:
    """
    Initialize a new debug session.
    
    Args:
        project_path: Path to the project to debug
        goal: Description of the debugging goal
        
    Returns:
        True if successful, False otherwise
    """
    project = Path(project_path).resolve()
    
    if not project.exists():
        print(f"❌ Error: Project path does not exist: {project}")
        return False
    
    # Create .debug-session directory
    debug_dir = project / ".debug-session"
    
    if debug_dir.exists():
        print(f"⚠️  Warning: .debug-session already exists at {debug_dir}")
        response = input("   Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("   Aborted.")
            return False
    
    debug_dir.mkdir(exist_ok=True)
    
    # Generate session ID and timestamp
    session_id = f"sess-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    timestamp = datetime.now().isoformat()
    
    # Create bug manifest
    manifest_path = debug_dir / "bug-manifest.yaml"

    # Check write permissions explicitly (chmod doesn't block root)
    if not os.access(debug_dir, os.W_OK):
        print(f"❌ No write permission for {debug_dir}")
        return False

    manifest_content = MANIFEST_TEMPLATE.format(
        session_id=session_id,
        timestamp=timestamp,
        goal=goal,
        project_path=str(project)
    )
    try:
        manifest_path.write_text(manifest_content)
        print(f"✅ Created bug-manifest.yaml")
    except OSError as e:
        print(f"❌ Failed to write bug-manifest.yaml: {e}")
        return False

    # Create ignore rules
    ignore_path = debug_dir / "ignore-rules.yaml"
    try:
        ignore_path.write_text(DEFAULT_IGNORE_RULES)
        print(f"✅ Created ignore-rules.yaml")
    except OSError as e:
        print(f"❌ Failed to write ignore-rules.yaml: {e}")
        return False

    # Create session metadata
    session_path = debug_dir / "session.yaml"
    session_content = SESSION_TEMPLATE.format(
        session_id=session_id,
        timestamp=timestamp,
        project_path=str(project),
        goal=goal
    )
    try:
        session_path.write_text(session_content)
        print(f"✅ Created session.yaml")
    except OSError as e:
        print(f"❌ Failed to write session.yaml: {e}")
        return False

    # Create directories for scan results
    try:
        (debug_dir / "scans").mkdir(exist_ok=True)
        (debug_dir / "fixes").mkdir(exist_ok=True)
        (debug_dir / "verifications").mkdir(exist_ok=True)
        print(f"✅ Created scan/fix/verification directories")
    except OSError as e:
        print(f"❌ Failed to create subdirectories: {e}")
        return False
    
    print(f"\n🚀 Debug session initialized!")
    print(f"   Session ID: {session_id}")
    print(f"   Project: {project}")
    print(f"   Goal: {goal}")
    print(f"\nNext steps:")
    print(f"  1. Edit ignore-rules.yaml to add known false positives")
    print(f"  2. Run: scan_bugs.py {project} --category all")
    print(f"  3. Review bug-manifest.yaml and fix bugs one at a time")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a Gas Debugger session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./my-project
  %(prog)s ./my-project --goal "Fix security vulnerabilities"
  %(prog)s /path/to/code --goal "Pre-release audit"
        """
    )
    parser.add_argument("project_path", help="Path to the project to debug")
    parser.add_argument("--goal", "-g", default="Debug and fix code issues",
                       help="Description of the debugging goal")
    
    args = parser.parse_args()
    
    success = init_session(args.project_path, args.goal)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
