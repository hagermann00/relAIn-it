"""
conductor:implement — Executes tasks from an active track.

Walks through each task in the active track, marks them done,
and provides guidance for execution.
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
    """Execute conductor:implement"""

    print("  ┌─────────────────────────────────────────┐")
    print("  │        conductor:implement               │")
    print("  └─────────────────────────────────────────┘")
    print()

    tracks_dir = os.path.join(project_root, ".relain-it", "tracks")
    if not os.path.isdir(tracks_dir):
        print("  No tracks found. Run conductor:newTrack first.")
        return

    # Find active tracks
    active_tracks = []
    for f in sorted(os.listdir(tracks_dir)):
        if not f.endswith(".json"):
            continue
        track_path = os.path.join(tracks_dir, f)
        try:
            with open(track_path, "r", encoding="utf-8") as fp:
                track = json.load(fp)
            if track.get("status") == "active":
                active_tracks.append((f, track_path, track))
        except Exception:
            continue

    if not active_tracks:
        print("  No active tracks. Run conductor:newTrack to create one.")
        return

    # Show active tracks
    if len(active_tracks) == 1:
        _, track_path, track = active_tracks[0]
    else:
        print("  Active tracks:")
        for i, (fname, _, t) in enumerate(active_tracks):
            done = sum(1 for task in t.get("tasks", []) if task.get("done"))
            total = len(t.get("tasks", []))
            print(f"    [{i+1}] {t['name']} — {done}/{total} tasks")
        print()
        choice = _prompt("Which track?", "1")
        try:
            idx = int(choice) - 1
            _, track_path, track = active_tracks[idx]
        except (ValueError, IndexError):
            print("    Invalid selection.")
            return

    print(f"  Track: {track['name']}")
    if track.get("goal"):
        print(f"  Goal:  {track['goal']}")
    print()

    # Walk through tasks
    tasks = track.get("tasks", [])
    all_done = True

    for i, task in enumerate(tasks):
        if task.get("done"):
            print(f"    [✅] {i+1}. {task['description']}")
            continue

        all_done = False
        print(f"    [  ] {i+1}. {task['description']}")
        action = _prompt("Done? (y/skip/quit)", "skip")

        if action.lower() in ("y", "yes", "done"):
            task["done"] = True
            task["completed_at"] = datetime.now().isoformat()
            print(f"    [✅] Marked done.")
        elif action.lower() in ("q", "quit", "exit"):
            print("    Pausing implementation.")
            break
        else:
            print(f"    [  ] Skipped.")

    # Save updated track
    completed_count = sum(1 for t in tasks if t.get("done"))
    if completed_count == len(tasks):
        track["status"] = "complete"
        track["completed_at"] = datetime.now().isoformat()

    with open(track_path, "w", encoding="utf-8") as f:
        json.dump(track, f, indent=2)

    print()
    print(f"  Progress: {completed_count}/{len(tasks)} tasks complete")
    if track["status"] == "complete":
        print("  🎉 Track complete!")
    else:
        print("  Run `conductor:implement` again to continue.")

    # Log
    log_file = os.path.join(project_root, ".relain-it", "conductor.log")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "implement",
        "track_name": track["name"],
        "tasks_completed": completed_count,
        "tasks_total": len(tasks),
        "track_status": track["status"],
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
