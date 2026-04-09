"""
conductor:revert — Reverts previous conductor actions.

Uses the conductor action log to identify and reverse previous operations.
"""

import os
import json


def run(project_root: str):
    """Execute conductor:revert"""

    print("  ┌─────────────────────────────────────────┐")
    print("  │        conductor:revert                  │")
    print("  └─────────────────────────────────────────┘")
    print()

    log_file = os.path.join(project_root, ".relain-it", "conductor.log")
    if not os.path.isfile(log_file):
        print("  No conductor log found. Nothing to revert.")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        entries = [json.loads(l.strip()) for l in f.readlines() if l.strip()]

    if not entries:
        print("  Conductor log is empty. Nothing to revert.")
        return

    # Show last 5 revertable actions
    revertable = [e for e in entries if e.get("action", "").startswith("setup:")]
    if not revertable:
        print("  No revertable actions found.")
        return

    print("  Recent revertable actions:")
    for i, entry in enumerate(revertable[-5:]):
        ts = entry.get("timestamp", "?")[:19]
        action = entry.get("action", "?")
        created = entry.get("created", [])
        print(f"    [{i+1}] [{ts}] {action} — {len(created)} file(s)")

    print()
    print("  ⚠️  Revert will DELETE generated files.")
    try:
        choice = input("    ? Revert which action? (number, or 'n' to cancel): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n    Cancelled.")
        return

    if choice.lower() in ("n", "no", ""):
        print("    Cancelled.")
        return

    try:
        idx = int(choice) - 1
        target = revertable[-5:][idx]
    except (ValueError, IndexError):
        print("    Invalid selection.")
        return

    created_files = target.get("created", [])
    if not created_files:
        print("    No files to revert for this action.")
        return

    ui_root = None
    for c in ["ui-rail", "ui", "frontend", "app"]:
        path = os.path.join(project_root, c)
        if os.path.isdir(path):
            ui_root = path
            break
    if not ui_root:
        ui_root = project_root

    deleted = []
    for rel_path in created_files:
        full = os.path.join(ui_root, rel_path)
        if os.path.isfile(full):
            os.remove(full)
            deleted.append(rel_path)
            print(f"    🗑️  Deleted: {rel_path}")
        else:
            print(f"    ⏭️  Already gone: {rel_path}")

    # Log the revert
    revert_entry = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "action": "revert",
        "reverted_action": target.get("action"),
        "deleted_files": deleted,
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(revert_entry) + "\n")

    print(f"\n  ✅ Reverted. {len(deleted)} file(s) removed.")
