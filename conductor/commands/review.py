"""
conductor:review — Reviews completed tracks and work.

Scans for:
- Completed tracks in .relain-it/tracks/
- Git commit history since last review
- Conductor action log entries
"""

import os
import json
from pathlib import Path


def run(project_root: str):
    """Execute conductor:review"""

    print("  ┌─────────────────────────────────────────┐")
    print("  │        conductor:review                  │")
    print("  └─────────────────────────────────────────┘")
    print()

    # Check for conductor log
    log_file = os.path.join(project_root, ".relain-it", "conductor.log")
    if os.path.isfile(log_file):
        print("  ── CONDUCTOR ACTION LOG ──")
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print("    (empty)")
        else:
            for line in lines[-10:]:  # Last 10 entries
                try:
                    entry = json.loads(line.strip())
                    ts = entry.get("timestamp", "?")[:19]
                    action = entry.get("action", "?")
                    print(f"    [{ts}] {action}")

                    # Show details
                    for k, v in entry.items():
                        if k not in ("timestamp", "action"):
                            if isinstance(v, list) and len(v) > 3:
                                print(f"      {k}: [{len(v)} items]")
                            else:
                                print(f"      {k}: {v}")
                except json.JSONDecodeError:
                    print(f"    (malformed entry)")
            print()
            print(f"  Total entries: {len(lines)}")
    else:
        print("  No conductor log found. Run conductor:setup first.")

    # Check for tracks
    tracks_dir = os.path.join(project_root, ".relain-it", "tracks")
    if os.path.isdir(tracks_dir):
        print()
        print("  ── TRACKS ──")
        tracks = [f for f in os.listdir(tracks_dir) if f.endswith(".json")]
        if tracks:
            for track_file in sorted(tracks):
                track_path = os.path.join(tracks_dir, track_file)
                try:
                    with open(track_path, "r", encoding="utf-8") as f:
                        track = json.load(f)
                    status = track.get("status", "unknown")
                    name = track.get("name", track_file)
                    tasks_total = len(track.get("tasks", []))
                    tasks_done = sum(1 for t in track.get("tasks", []) if t.get("done"))
                    icon = "✅" if status == "complete" else "🔄" if status == "active" else "⏸️"
                    print(f"    {icon} {name}: {tasks_done}/{tasks_total} tasks ({status})")
                except Exception:
                    print(f"    ⚠️  {track_file}: could not parse")
        else:
            print("    No tracks yet. Run conductor:newTrack to create one.")
    else:
        print()
        print("  No tracks directory yet. Run conductor:newTrack to create one.")

    print()
