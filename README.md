# relAIn-it

**The Third-Brain Watcher Layer for the iiWii Ecosystem**

relAIn-it is a quiet, read-only observer that watches your workspace in real time, detects tangents, isolates them, and delivers the right intervention at the right moment — all while staying in the background.

## What It Does

- **Watches** your workspace: open files, git state, keystrokes, context
- **Detects** tangents and automatically isolates them (tags, side branches, folders)
- **Nudges** at natural breakpoints: "Looks clean — commit?" / "Tangent isolated. Back?"
- **Enforces** momentum when you've declared intent ("You said you're building X. This isn't X.")
- **Preserves** everything via silent background backups and ghost commits
- **Traces** the origin of ideas and flags implicit decisions
- **Bootstraps** new projects via Flash scaffolding or guided Conductor mode

## Core Philosophy

| Principle | Meaning |
|-----------|---------|
| **Chinese Wall** | Can read everything, never contributes unless explicitly asked |
| **Sovereignty** | You stay in control — it highlights, you decide |
| **No Modes** | Adapts to whatever style you're in (jam, build, refactor, etc.) |
| **Minimal Interruption** | Most work is invisible until you need it |

## The Four Intervention Types

1. 🏇 **Riding Crop** — Aggressive momentum enforcement when you're drifting from declared intent
2. 🛑 **Hold-the-Horses** — Structural gates that prevent building on sand (missing foundation, untrusted code)
3. 💬 **Gentle Nudge** — Periodic reminders at natural breakpoints
4. 👻 **Silent Action** — Invisible background work (backups, tagging, isolation)

## Architecture

- **Frontend**: Tauri 2 + Vite + React + TypeScript + Tailwind CSS
- **Backend**: Rust (Tauri core) — sysinfo, TTS/STT, file watching, git integration
- **Data**: Own `.relain-it/` git repo with bidirectional action logging + SQLite observation DB
- **Shared Context**: Append-only context file bridging relAIn-it observations to the iiWii ecosystem

## Project Structure

```
relAIn-it/
├── ui-rail/                    # The Stealth Rail — Tauri desktop app
│   ├── src/                    # React frontend
│   │   ├── App.tsx             # Main rail UI (20px → 100px → 400px expand)
│   │   ├── FloatingPlayer.tsx  # TTS floating player window
│   │   ├── main.tsx            # React entry point
│   │   └── index.css           # Styles + Tailwind
│   ├── src-tauri/              # Rust backend
│   │   ├── src/main.rs         # Core: telemetry, TTS, hotkeys, window mgmt
│   │   ├── Cargo.toml          # Rust dependencies
│   │   ├── build.rs            # Tauri build script
│   │   └── tauri.conf.json     # Window & app config
│   ├── package.json            # Frontend deps
│   ├── vite.config.ts          # Vite build config
│   ├── tailwind.config.js      # Tailwind config
│   └── index.html              # Vite entry point
├── .gitignore
├── README.md                   # ← You are here
├── CURRENT_STATE.md            # What's done, what's next
└── ARCHITECTURE.md             # Deep technical spec
```

## Current Status

See [CURRENT_STATE.md](./CURRENT_STATE.md) for detailed progress tracking.

**TL;DR**: Foundation scaffolding complete. Project compiles (frontend). Rust backend has API-compat fixes applied. Next: build the Conductor bootstrap system and use it to prove the workspace setup flow.

## Development

```bash
cd ui-rail
npm install
npx tauri dev
```

## License

Private — iiWii Sovereign Infrastructure.
