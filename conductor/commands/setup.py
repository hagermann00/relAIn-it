"""
conductor:setup — Scaffolds the project and ensures foundation.

Modes:
  - AUDIT: Check what exists, report gaps, offer to fill them
  - FLASH: Generate all missing files with sensible defaults (no questions)
  - CONDUCTOR: Interactive walkthrough with questions and choices

First run is always AUDIT → then offers FLASH or CONDUCTOR.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime


# === TEMPLATE: Tauri + Vite + React + TypeScript + Tailwind ===

TEMPLATES = {
    "package.json": lambda name: json.dumps({
        "name": name,
        "private": True,
        "version": "0.1.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc && vite build",
            "preview": "vite preview",
            "tauri": "tauri"
        },
        "dependencies": {
            "@tauri-apps/api": "^2.0.0",
            "react": "^18.3.1",
            "react-dom": "^18.3.1"
        },
        "devDependencies": {
            "@tauri-apps/cli": "^2.0.0",
            "@types/react": "^18.3.0",
            "@types/react-dom": "^18.3.0",
            "@vitejs/plugin-react": "^4.3.0",
            "autoprefixer": "^10.4.19",
            "postcss": "^8.4.38",
            "tailwindcss": "^3.4.4",
            "tailwindcss-animate": "^1.0.7",
            "typescript": "^5.5.0",
            "vite": "^5.3.0"
        }
    }, indent=2),

    "index.html": lambda name: f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",

    "vite.config.ts": lambda name: """import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
});
""",

    "tsconfig.json": lambda name: json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": True,
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
            "strict": True,
            "noUnusedLocals": False,
            "noUnusedParameters": False,
            "noFallthroughCasesInSwitch": True
        },
        "include": ["src"],
        "references": [{"path": "./tsconfig.node.json"}]
    }, indent=2),

    "tsconfig.node.json": lambda name: json.dumps({
        "compilerOptions": {
            "composite": True,
            "skipLibCheck": True,
            "module": "ESNext",
            "moduleResolution": "bundler",
            "allowSyntheticDefaultImports": True
        },
        "include": ["vite.config.ts"]
    }, indent=2),

    "postcss.config.js": lambda name: """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
""",

    "src/main.tsx": lambda name: """import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",

    "src-tauri/build.rs": lambda name: """fn main() {
    tauri_build::build()
}
""",
}


def _find_ui_root(project_root: str) -> str:
    """Locate the ui-rail directory."""
    for c in ["ui-rail", "ui", "frontend", "app"]:
        path = os.path.join(project_root, c)
        if os.path.isdir(path):
            return path
    return project_root


def _audit(ui_root: str) -> list:
    """Returns list of (rel_path, description) for missing files."""
    missing = []
    for rel_path in TEMPLATES:
        full = os.path.join(ui_root, rel_path)
        if not os.path.isfile(full):
            missing.append(rel_path)
    return missing


def _flash(ui_root: str, project_name: str, missing: list):
    """Generate all missing files with defaults. No questions."""
    created = []
    for rel_path in missing:
        full = os.path.join(ui_root, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)

        content = TEMPLATES[rel_path](project_name)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(rel_path)
        print(f"    ✅ Created: {rel_path}")

    return created


def _detect_project_name(ui_root: str, project_root: str) -> str:
    """Try to detect project name from existing files."""
    pkg = os.path.join(ui_root, "package.json")
    if os.path.isfile(pkg):
        try:
            with open(pkg) as f:
                data = json.load(f)
                return data.get("name", "")
        except Exception:
            pass

    tauri_conf = os.path.join(ui_root, "src-tauri", "tauri.conf.json")
    if os.path.isfile(tauri_conf):
        try:
            with open(tauri_conf) as f:
                data = json.load(f)
                return data.get("productName", "")
        except Exception:
            pass

    return os.path.basename(project_root)


def _prompt(message: str, default: str = "") -> str:
    """Simple interactive prompt."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"    ? {message}{suffix}: ").strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _npm_install(ui_root: str):
    """Run npm install if node_modules is missing."""
    nm = os.path.join(ui_root, "node_modules")
    if not os.path.isdir(nm):
        print()
        print("  ── INSTALLING DEPENDENCIES ──")
        print("    Running npm install...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=ui_root,
            capture_output=True,
            text=True,
            timeout=120,
            shell=True,
        )
        if result.returncode == 0:
            print("    ✅ npm install complete")
        else:
            print(f"    ❌ npm install failed:\n{result.stderr[:500]}")
    else:
        print("    ✅ node_modules already present")


def _log_action(project_root: str, action: str, details: dict):
    """Log conductor action to .relain-it/conductor.log"""
    log_dir = os.path.join(project_root, ".relain-it")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "conductor.log")

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        **details,
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run(project_root: str):
    """Execute conductor:setup"""

    ui_root = _find_ui_root(project_root)
    project_name = _detect_project_name(ui_root, project_root)

    print("  ┌─────────────────────────────────────────┐")
    print("  │        conductor:setup                   │")
    print("  └─────────────────────────────────────────┘")
    print()
    print(f"  Project: {project_name}")
    print(f"  UI Root: {ui_root}")
    print()

    # Phase 1: Audit
    print("  ── AUDIT ──")
    missing = _audit(ui_root)

    if not missing:
        print("    ✅ All foundation files present. Nothing to scaffold.")
        _npm_install(ui_root)
        _log_action(project_root, "setup:audit", {"result": "complete", "missing": 0})
        print()
        print("  ✅ Setup verified. Foundation is solid.")
        return

    print(f"    Found {len(missing)} missing file(s):")
    for path in missing:
        print(f"      → {path}")
    print()

    # Phase 2: Choose mode
    print("  How do you want to proceed?")
    print("    [F] Flash — Generate all missing files with defaults (no questions)")
    print("    [C] Conductor — Interactive walkthrough with choices")
    print("    [S] Skip — Don't generate anything, just report")
    print()

    mode = _prompt("Mode", "F").upper()

    if mode == "S":
        print("    Skipped. No files generated.")
        _log_action(project_root, "setup:skip", {"missing": missing})
        return

    if mode == "C":
        # Conductor mode: ask questions
        print()
        print("  ── CONDUCTOR MODE ──")
        project_name = _prompt("Project name", project_name)
        # Future: more questions here (stack, preferences, etc.)
        print()

    # Phase 3: Generate
    print("  ── GENERATING ──")
    created = _flash(ui_root, project_name, missing)
    print()

    # Phase 4: Dependencies
    _npm_install(ui_root)

    # Phase 5: Log
    _log_action(project_root, f"setup:{'conductor' if mode == 'C' else 'flash'}", {
        "project_name": project_name,
        "created": created,
        "mode": mode,
    })

    print()
    print(f"  ✅ Setup complete. {len(created)} file(s) created.")
    print("     Run `conductor:status` to verify.")
