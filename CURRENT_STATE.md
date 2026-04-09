# relAIn-it: Current State

> Last updated: 2026-04-09

## What's Been Done

### Foundation Scaffolding ✅
- **package.json** — Vite + React 18 + TypeScript + Tailwind + Tauri API deps
- **index.html** — Vite entry point
- **vite.config.ts** — React plugin, port 1420 (Tauri devUrl)
- **tsconfig.json / tsconfig.node.json** — TypeScript compilation config
- **postcss.config.js** — Tailwind processing
- **src/main.tsx** — React entry point
- **src-tauri/build.rs** — Tauri build script (was missing, caused OUT_DIR error)
- **src-tauri/icons/icon.ico** — Placeholder icon (unblocks Tauri build)
- **tailwindcss-animate** — Installed (required by tailwind.config.js)
- **node_modules** — All deps installed via `npm install`

### Rust Backend Fixes ✅
- Added `use tauri::Emitter;` — required in Tauri 2.x for `.emit()` calls
- `global_cpu_usage()` → `global_cpu_info().cpu_usage()` — sysinfo 0.30+ API change
- `tauri-build` and `tauri` pinned to stable `"2"` (was `"2.0.0-rc"`)
- Removed `protocol-asset` feature (not declared in tauri.conf.json)
- Icon list trimmed to only `icon.ico` (only icon file that exists)

### React Frontend Fixes ✅
- Moved all `useState`/`useEffect` hooks before early return (Rules of Hooks violation)
- Fixed `toFixed()` string → number type mismatch in telemetry state

### Codebase Hygiene ✅
- **hndl-it quarantined** → `_ARCHIVE/QUARANTINE_UNTRUSTED/hndl-utils`
  - Assessed as vibe-code scaffolding with no working implementation
  - No code imported — concepts only noted for potential rewrite
  - Quarantine manifest written with forensic assessment

### Specification ✅
- Full architecture spec written covering:
  - Four intervention types (Riding Crop, Hold-the-Horses, Nudge, Silent)
  - Workspace bootstrap system (Flash / Conductor / Playground / Custom)
  - Bidirectional data model (own git + own DB + append-only shared context)
  - TTS + STT + highlight-read-aloud confirmed in scope

## What's Next

### Immediate: Conductor Bootstrap (Phase 0)
The standard for serious work is relAIn-it involvement. Before building more features, build the **Conductor** — a minimal interactive scaffold tool — and use it to initialize relAIn-it's own project. Eat our own cooking from day zero.

1. **Build Minimal Conductor** — Interactive prompt flow + scaffold generator
2. **Run Conductor on relAIn-it** — Let it generate/validate the foundation
3. **Verify full build** — `npm install` + `cargo tauri dev` end-to-end
4. **Commit as conductor-scaffolded foundation**

### Phase 1: The Watcher Core
- File system watcher (`notify` crate)
- Git state observer (`git2` crate)
- Session context tracker (SQLite via `rusqlite`)
- Observation event bus (Tauri events → frontend)
- Basic nudge scheduler

### Phase 2: The Bootstrap Gate
- Intent detection heuristics
- Flash / Conductor / Playground scaffold modes
- Preference learning system
- Hold-the-Horses intervention logic

### Phase 3: Tangent Detection & Isolation
- Context window analysis
- Auto-branching / auto-folder for tangents
- Origin tracing
- Ghost commits

### Phase 4: Voice & Read-Aloud
- TTS engine integration (nudges spoken aloud)
- STT for voice commands
- Highlight + read-aloud (global hotkey Ctrl+Alt+R)

## Known Issues

| Issue | Status | Notes |
|-------|--------|-------|
| Rust build needs full `cargo tauri build` verification | Pending | Frontend compiles; Rust needs icon + full build pass |
| Placeholder icon.ico is a gray square | Low priority | Replace with proper relAIn-it branding later |
| `window-vibrancy` Mica effect untested | Pending | Windows 11 specific, needs runtime test |
| `vosk` crate (STT) may have platform-specific build issues | Future | Phase 4 concern |
