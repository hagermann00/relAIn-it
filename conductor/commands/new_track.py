"""
conductor:newTrack — Plans a new track with tasks.

A "track" is a unit of work: a named goal with a list of tasks.
Tracks are stored as JSON files in .relain-it/tracks/.
"""

import os
import json
from datetime import datetime


def _prompt(message: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"    ? {message}{suffix}: ").strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def run(project_root: str):
    """Execute conductor:newTrack"""

    print("  ┌─────────────────────────────────────────┐")
    print("  │        conductor:newTrack                │")
    print("  └─────────────────────────────────────────┘")
    print()

    # Collect track info
    track_name = _prompt("Track name (short description)")
    if not track_name:
        print("    ✗ Track name required. Aborting.")
        return

    track_goal = _prompt("Goal (what does completion look like?)")

    # Collect tasks
    print()
    print("  Enter tasks (one per line, empty line to finish):")
    tasks = []
    while True:
        try:
            task = input(f"    [{len(tasks)+1}] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not task:
            break
        tasks.append({"description": task, "done": False})

    if not tasks:
        print("    ✗ No tasks entered. Aborting.")
        return

    # Generate track ID
    track_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + track_name.lower().replace(" ", "_")[:30]

    track = {
        "id": track_id,
        "name": track_name,
        "goal": track_goal,
        "status": "active",
        "created": datetime.now().isoformat(),
        "tasks": tasks,
    }

    # Save
    tracks_dir = os.path.join(project_root, ".relain-it", "tracks")
    os.makedirs(tracks_dir, exist_ok=True)
    track_file = os.path.join(tracks_dir, f"{track_id}.json")

    with open(track_file, "w", encoding="utf-8") as f:
        json.dump(track, f, indent=2)

    print()
    print(f"  ✅ Track created: {track_name}")
    print(f"     {len(tasks)} task(s)")
    print(f"     File: {track_file}")
    print()
    print("  Run `conductor:implement` to begin execution.")

    # Log
    log_dir = os.path.join(project_root, ".relain-it")
    log_file = os.path.join(log_dir, "conductor.log")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "newTrack",
        "track_id": track_id,
        "track_name": track_name,
        "task_count": len(tasks),
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
