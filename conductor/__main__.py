#!/usr/bin/env python3
"""
relAIn-it Conductor — The Project Orchestration CLI

Commands:
    conductor:status      Displays the current project state
    conductor:setup       Scaffolds the project and ensures foundation
    conductor:review      Reviews completed tracks/work
    conductor:revert      Reverts previous work
    conductor:newTrack    Plans a track, generates tasks
    conductor:implement   Executes the tasks defined in a track

Usage:
    python -m conductor status
    python -m conductor setup
    python -m conductor review
    python -m conductor revert
    python -m conductor newTrack
    python -m conductor implement
"""

import sys
import os
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add conductor package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commands.status import run as cmd_status
from commands.setup import run as cmd_setup
from commands.review import run as cmd_review
from commands.revert import run as cmd_revert
from commands.new_track import run as cmd_new_track
from commands.implement import run as cmd_implement

COMMANDS = {
    "status": cmd_status,
    "setup": cmd_setup,
    "review": cmd_review,
    "revert": cmd_revert,
    "newTrack": cmd_new_track,
    "newtrack": cmd_new_track,  # case-insensitive alias
    "implement": cmd_implement,
}

BANNER = """
╔══════════════════════════════════════════╗
║         relAIn-it  C O N D U C T O R    ║
║         ─────────────────────────────    ║
║         Project Orchestration Layer      ║
╚══════════════════════════════════════════╝
"""

HELP = """
  conductor:status      Show current project state, gaps, and health
  conductor:setup       Scaffold or validate project foundation
  conductor:review      Review completed tracks and work
  conductor:revert      Revert previous conductor actions
  conductor:newTrack    Plan a new track with tasks
  conductor:implement   Execute tasks from a track

  Usage: python -m conductor <command> [--project-root <path>]
"""


def main():
    print(BANNER)

    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h", "help"):
        print(HELP)
        sys.exit(0)

    command = sys.argv[1].replace("conductor:", "")

    if command not in COMMANDS:
        print(f"  ✗ Unknown command: '{command}'")
        print(f"    Available: {', '.join(k for k in COMMANDS if k != 'newtrack')}")
        sys.exit(1)

    # Determine project root
    project_root = None
    if "--project-root" in sys.argv:
        idx = sys.argv.index("--project-root")
        if idx + 1 < len(sys.argv):
            project_root = sys.argv[idx + 1]

    if not project_root:
        # Default: look for relAIn-it project root relative to conductor
        conductor_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(conductor_dir)

    print(f"  📍 Project root: {project_root}")
    print(f"  🎯 Command: conductor:{command}")
    print()

    COMMANDS[command](project_root)


if __name__ == "__main__":
    main()
