"""
conductor:status — Displays the current project state, gaps, and health.

Scans the project root for:
- Expected files and their presence/absence
- Git state (branch, dirty files, remote sync)
- Build readiness (can npm install? can cargo check?)
- Foundation completeness score
"""

import os
import subprocess
import json
from pathlib import Path


# Foundation files that MUST exist for a Tauri+Vite+React project
FOUNDATION_FILES = {
    "package.json": "Frontend project identity and dependencies",
    "index.html": "Vite entry point — Tauri serves this",
    "vite.config.ts": "Vite build tool configuration",
    "tsconfig.json": "TypeScript compilation config",
    "tsconfig.node.json": "Node-side TypeScript config",
    "postcss.config.js": "PostCSS/Tailwind processing",
    "tailwind.config.js": "Tailwind CSS configuration",
    "src/main.tsx": "React entry point",
    "src/App.tsx": "Main React component",
    "src/index.css": "Base stylesheet with Tailwind directives",
    "src-tauri/Cargo.toml": "Rust dependencies",
    "src-tauri/build.rs": "Tauri build script",
    "src-tauri/tauri.conf.json": "Tauri window and app config",
    "src-tauri/src/main.rs": "Rust backend entry point",
    "src-tauri/icons/icon.ico": "App icon (Windows)",
}

PROJECT_DOCS = {
    "README.md": "Project overview",
    "CURRENT_STATE.md": "Progress tracking",
    "ARCHITECTURE.md": "Technical architecture",
    ".gitignore": "Git ignore rules",
}


def _check_git(project_root: str) -> dict:
    """Check git state."""
    result = {"initialized": False, "branch": None, "dirty": False, "remote": None, "ahead": 0, "behind": 0}

    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_root, capture_output=True, text=True, timeout=5
        )
        if branch.returncode == 0:
            result["initialized"] = True
            result["branch"] = branch.stdout.strip()

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root, capture_output=True, text=True, timeout=5
        )
        if status.returncode == 0:
            result["dirty"] = len(status.stdout.strip()) > 0
            result["dirty_count"] = len([l for l in status.stdout.strip().split("\n") if l])

        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_root, capture_output=True, text=True, timeout=5
        )
        if remote.returncode == 0:
            result["remote"] = remote.stdout.strip()

    except Exception:
        pass

    return result


def _check_node_modules(ui_root: str) -> dict:
    """Check if node_modules exists and has expected packages."""
    nm_path = os.path.join(ui_root, "node_modules")
    result = {"installed": os.path.isdir(nm_path), "package_count": 0}

    if result["installed"]:
        result["package_count"] = len([
            d for d in os.listdir(nm_path)
            if os.path.isdir(os.path.join(nm_path, d)) and not d.startswith(".")
        ])

    return result


def _check_cargo_target(tauri_root: str) -> dict:
    """Check Rust build state."""
    target = os.path.join(tauri_root, "target")
    return {
        "target_exists": os.path.isdir(target),
        "cargo_lock_exists": os.path.isfile(os.path.join(tauri_root, "Cargo.lock")),
    }


def _find_ui_root(project_root: str) -> str:
    """Locate the ui-rail directory."""
    candidates = ["ui-rail", "ui", "frontend", "app"]
    for c in candidates:
        path = os.path.join(project_root, c)
        if os.path.isdir(path):
            return path
    return project_root


def run(project_root: str):
    """Execute conductor:status"""

    ui_root = _find_ui_root(project_root)
    tauri_root = os.path.join(ui_root, "src-tauri")

    print("  ┌─────────────────────────────────────────┐")
    print("  │        conductor:status                  │")
    print("  └─────────────────────────────────────────┘")
    print()

    # 1. Foundation Files
    print("  ── FOUNDATION FILES ──")
    found = 0
    total = len(FOUNDATION_FILES)
    missing = []

    for rel_path, description in FOUNDATION_FILES.items():
        full_path = os.path.join(ui_root, rel_path)
        exists = os.path.isfile(full_path)
        icon = "✅" if exists else "❌"
        print(f"    {icon} {rel_path}")
        if exists:
            found += 1
        else:
            missing.append((rel_path, description))

    score = (found / total) * 100
    print()
    print(f"  Foundation Score: {found}/{total} ({score:.0f}%)")
    if missing:
        print()
        print("  ⚠️  Missing files:")
        for path, desc in missing:
            print(f"      → {path}: {desc}")
    print()

    # 2. Project Docs
    print("  ── PROJECT DOCS ──")
    for rel_path, description in PROJECT_DOCS.items():
        full_path = os.path.join(project_root, rel_path)
        exists = os.path.isfile(full_path)
        icon = "✅" if exists else "❌"
        print(f"    {icon} {rel_path} — {description}")
    print()

    # 3. Git State
    print("  ── GIT STATE ──")
    git = _check_git(project_root)
    if git["initialized"]:
        print(f"    Branch: {git['branch']}")
        print(f"    Remote: {git['remote'] or 'none'}")
        dirty_icon = "⚠️  DIRTY" if git["dirty"] else "✅ Clean"
        print(f"    Status: {dirty_icon}" + (f" ({git.get('dirty_count', 0)} files)" if git["dirty"] else ""))
    else:
        print("    ❌ Git not initialized")
    print()

    # 4. Dependencies
    print("  ── DEPENDENCIES ──")
    node = _check_node_modules(ui_root)
    if node["installed"]:
        print(f"    ✅ node_modules: {node['package_count']} packages")
    else:
        print("    ❌ node_modules: NOT INSTALLED (run npm install)")

    cargo = _check_cargo_target(tauri_root)
    cargo_icon = "✅" if cargo["cargo_lock_exists"] else "❌"
    print(f"    {cargo_icon} Cargo.lock: {'exists' if cargo['cargo_lock_exists'] else 'missing'}")
    print()

    # 5. Overall Verdict
    print("  ── VERDICT ──")
    if score == 100 and node["installed"] and not git["dirty"]:
        print("    🟢 READY — Foundation complete, deps installed, git clean")
    elif score == 100 and node["installed"]:
        print("    🟡 BUILDABLE — Foundation complete but git is dirty")
    elif score >= 80:
        print(f"    🟡 MOSTLY THERE — {len(missing)} file(s) missing")
    else:
        print(f"    🔴 NOT READY — {len(missing)} foundation file(s) missing")

    print()
