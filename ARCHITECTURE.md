# relAIn-it: Architecture

## System Overview

```
┌──────────────────────────────────────────────────────┐
│                    relAIn-it                         │
│                                                      │
│  ┌─────────────┐    ┌──────────────┐                │
│  │  UI Rail    │◄──►│  Rust Core   │                │
│  │  (React)    │    │  (Tauri 2)   │                │
│  │             │    │              │                │
│  │ • Stealth   │    │ • Watcher    │                │
│  │   Rail      │    │ • Telemetry  │                │
│  │ • Nudge     │    │ • TTS/STT   │                │
│  │   Display   │    │ • Hotkeys    │                │
│  │ • Dashboard │    │ • Git Obs.   │                │
│  └─────────────┘    └──────┬───────┘                │
│                            │                         │
│                     ┌──────▼───────┐                │
│                     │  Data Layer  │                │
│                     │              │                │
│                     │ • SQLite DB  │                │
│                     │ • Own Git    │                │
│                     │ • Shared Ctx │                │
│                     └──────────────┘                │
└──────────────────────────────────────────────────────┘
```

## Chinese Wall Principle

relAIn-it operates on a strict read/write separation:

### READ (Unlimited)
- All workspace files
- Git history and state
- System telemetry (CPU, RAM)
- Clipboard content (for read-aloud)
- User's declared goals and session context

### WRITE (Strictly Limited)
1. **Own `.relain-it/` directory** — observation DB, action logs, own git
2. **Append-only shared context file** — bridge to iiWii ecosystem memory
3. **Ghost commits** — to relAIn-it's own branches, never touching user's work
4. **Scaffold files** — ONLY when user explicitly triggers Flash/Conductor/etc.
5. **UI state** — nudge displays, rail state, floating player

Everything else is observation-only.

## Intervention System

### Trigger Logic

```
Observation Stream
     │
     ▼
┌─ Heuristic Engine ─────────────────────────────────┐
│                                                      │
│  Time in unrelated files > threshold                │
│  + Declared goal exists                             │
│  + No commit in N minutes                           │
│  + File activity pattern diverges from goal          │
│                                                      │
│  ──► Classify: Riding Crop / Gate / Nudge / Silent  │
│                                                      │
│  ──► Check: Cooldown timer (don't spam)             │
│  ──► Check: User dismissed similar nudge recently?  │
│  ──► Check: Natural breakpoint? (file save, pause)  │
│                                                      │
│  ──► Deliver or suppress                            │
└──────────────────────────────────────────────────────┘
```

### Escalation Path
```
Silent (always on)
  → Nudge (at natural breakpoints)
    → Gate (when foundation is missing)
      → Riding Crop (when declared intent is being ignored)
```

## Data Model

### Bidirectional Git Log (`.relain-it/git/`)

**Inward commits** (tagged `[IN]`):
- Observations, detected events, context snapshots
- What the user did, when, in what files

**Outward commits** (tagged `[OUT]`):
- What relAIn-it did in response
- Nudges delivered, gates triggered, scaffolds created
- User's response to each action

### SQLite Schema (`.relain-it/relain.db`)

```sql
-- What relAIn-it sees
CREATE TABLE observations (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL, -- file_open, file_edit, git_commit, etc.
    file_path TEXT,
    git_branch TEXT,
    context_hash TEXT,        -- hash of surrounding context for dedup
    declared_goal TEXT
);

-- What relAIn-it does
CREATE TABLE actions (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL, -- nudge, gate, riding_crop, silent, scaffold
    trigger_observation_id INTEGER REFERENCES observations(id),
    message TEXT,
    user_response TEXT,        -- accepted, dismissed, ignored
    metadata TEXT              -- JSON blob for action-specific data
);

-- Tangent tracking
CREATE TABLE tangents (
    id INTEGER PRIMARY KEY,
    detected_at TEXT NOT NULL,
    session_id TEXT NOT NULL,
    files TEXT NOT NULL,        -- JSON array of involved files
    isolation_branch TEXT,
    status TEXT DEFAULT 'active', -- active, parked, merged, abandoned
    origin_trace TEXT           -- where the tangent started
);

-- Learned preferences
CREATE TABLE preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    learned_from TEXT,         -- which observations led to this preference
    confidence REAL DEFAULT 0.5,
    updated_at TEXT
);
```

### Shared Context File (`shared_context.jsonl`)

Append-only JSONL. One of relAIn-it's few write permissions to the main system.

```jsonl
{"ts":"2026-04-09T07:45:00Z","type":"preference","key":"stack.default","value":"tauri+vite+react","confidence":0.8}
{"ts":"2026-04-09T07:50:00Z","type":"convention","key":"folder.structure","value":"ui-rail/src pattern","source":"observed"}
{"ts":"2026-04-09T08:00:00Z","type":"behavioral","key":"tangent.frequency","value":"high","note":"user explores before committing"}
```

## Workspace Bootstrap System

### Available Modes (Extensible Registry)

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Flash** | Auto or manual | Instant generic boilerplate, best defaults |
| **Conductor** | Manual or offered | Guided walkthrough with smart questions |
| **Playground** | Manual | Quick scratch space, disposable |
| **Custom** | Learned | User-defined or evolved presets |

### Conductor Flow

```
1. "What are we building?" → free text or category select
2. Detect stack from answer → offer defaults
3. "Preferences?" → optional, skippable (learns over time)
4. Generate scaffold → all boilerplate files
5. Verify build → npm install + compile check
6. Commit → "foundation: conductor-scaffolded [project-type]"
```

## Tech Stack

### Frontend (ui-rail/src/)
- React 18 + TypeScript
- Tailwind CSS 3 + tailwindcss-animate
- Vite 5 (dev server + build)
- `@tauri-apps/api` for Rust ↔ JS bridge

### Backend (ui-rail/src-tauri/)
- Rust (edition 2021)
- Tauri 2.x (window management, IPC, security)
- sysinfo (CPU/RAM telemetry)
- tts (text-to-speech)
- enigo (keyboard simulation for clipboard capture)
- arboard (clipboard access)
- global-hotkey (system-wide hotkey registration)
- window-vibrancy (Windows 11 Mica/Acrylic effects)

### Future Additions
- notify (file system watching) — Phase 1
- git2 (git state observation) — Phase 1
- rusqlite (observation database) — Phase 1
- vosk (speech-to-text) — Phase 4
