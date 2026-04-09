# Conductor Research: Scaffolding & Project Generation Tools

> Researched: 2026-04-09
> Purpose: Evaluate existing tools to inform relAIn-it's Conductor design

---

## The Landscape (2026)

The scaffolding space has split into three tiers:

1. **Full Project Generators** — Create entire project structures from templates
2. **Micro-Generators** — Create individual files/components within existing projects
3. **TUI Builders** — Tools for building interactive terminal experiences (used BY generators)

relAIn-it's Conductor needs aspects of all three.

---

## Tier 1: Full Project Generators

### Copier ⭐ (Recommended for study)
- **What:** Python-based project scaffolding with template lifecycle management
- **Key differentiator:** `copier update` — pull template changes into existing projects
- **Config:** YAML-based (`copier.yml`)
- **Why it matters for us:** Copier solves the "Day 2 problem" — keeping generated projects in sync with upstream template improvements. relAIn-it's Conductor could learn from this: when the template evolves, existing projects should be able to pull updates.
- **Limitation:** Python-only toolchain, not native to our Rust/Node stack
- **Link:** https://copier.readthedocs.io

### Cookiecutter
- **What:** Mature, widely-adopted, language-agnostic project generator
- **Config:** JSON-based (`cookiecutter.json`)
- **Massive template ecosystem** — hundreds of community templates
- **Limitation:** One-shot generation only. Once scaffolded, the link to the template is broken. No updates.
- **Link:** https://cookiecutter.readthedocs.io

### create-tauri-app (Official)
- **What:** Tauri's own interactive scaffolding tool
- **Run:** `npm create tauri-app@latest`
- **Prompts:** Project name → Frontend language → Package manager → UI template
- **Templates:** React, Vue, Svelte, Solid, Angular, Vanilla, Yew, Leptos
- **Why it matters:** This is literally what we'd use for Flash mode's Tauri+React preset. We should study its output structure as the reference implementation.
- **Limitation:** Only generates initial structure, no lifecycle/update capability
- **Link:** https://tauri.app/start/create-project/

### Verdict: Full Generators
Copier's update/lifecycle model is closest to what relAIn-it needs. But we're not adopting Copier itself — we're learning from its patterns and building our own within the Conductor.

---

## Tier 2: Micro-Generators

### Plop.js ⭐ (Relevant for component-level scaffolding)
- **What:** Minimalist micro-generator framework
- **Architecture:** Config-first — single `plopfile.js` defines all generators
- **Workflow:** CLI prompts → Handlebars templates → file generation
- **Strengths:**
  - Very fast to set up
  - Pure JavaScript, full programmatic control
  - Good for: "generate a new React component", "add a new Tauri command"
- **Limitation:** Can get unwieldy for large projects, centralized config file
- **Link:** https://plopjs.com

### Hygen
- **What:** File-system-first code generator
- **Architecture:** Folder structure = generator namespace (`_templates/component/new/`)
- **Strengths:**
  - Scales better than Plop for large codebases/monorepos
  - Context-aware (detects where you are in the project)
  - Fast startup
- **Limitation:** Steeper learning curve, folder convention is rigid
- **Link:** https://www.hygen.io

### Verdict: Micro-Generators
Plop's simplicity is appealing for relAIn-it's internal use (e.g., quickly generating new observer modules or nudge types). Hygen's file-system-first approach is interesting but adds complexity we don't need yet.

---

## Tier 3: TUI Builders (for building the Conductor's interactive UI)

### Gum (Charmbracelet) ⭐⭐ (Strong candidate)
- **What:** Shell script helper for building interactive terminal UIs
- **Language:** Go (standalone binary, no runtime deps)
- **Features:**
  - `gum input` — text input with placeholder
  - `gum choose` — select from list
  - `gum confirm` — yes/no
  - `gum spin` — loading spinner with command execution
  - `gum filter` — fuzzy search/filter
  - `gum style` — styled text output
  - `gum write` — multi-line text editor
- **Why it matters:** Gum is the perfect building block for the Conductor's interactive prompts. It's language-agnostic (just shell commands), gorgeous out of the box, and can be called from any script (Python, Node, Rust, PowerShell).
- **Link:** https://github.com/charmbracelet/gum

### @inquirer/prompts (Node.js)
- **What:** Modern, modular CLI prompt library (successor to inquirer.js)
- **Features:** Input, select, confirm, checkbox, password, editor
- **Why it matters:** If we build the Conductor in Node.js, this is the prompt library
- **Limitation:** Requires Node.js runtime
- **Link:** https://www.npmjs.com/package/@inquirer/prompts

### Verdict: TUI Builders
Gum is the standout — it's beautiful, fast, standalone binary, no runtime dependencies. If we build the Conductor as a shell/PowerShell orchestrator that calls Gum for prompts, we get a gorgeous interactive experience with zero dependency overhead.

---

## Synthesis: What This Means for relAIn-it's Conductor

### Recommended Architecture

```
Conductor
├── Entry: PowerShell/Shell script (or Rust CLI)
├── Prompts: Gum (interactive TUI) or @inquirer/prompts (if Node)
├── Templates: File-system-based (like Hygen's `_templates/` pattern)
├── Generator: Custom — reads template, applies answers, writes files
├── Lifecycle: Copier-inspired update capability (relAIn-it can re-run on existing projects)
└── Micro-gen: Plop-like internal generators for component-level scaffolding
```

### Key Design Decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Runtime** | Python or standalone (Gum-based shell) | Avoid adding Node/Rust deps just for the Conductor |
| **Interactive prompts** | Gum | Gorgeous, zero-dep, works from any language |
| **Template storage** | `research/conductor/templates/` subfolder | Hygen-inspired, filesystem-first |
| **Update capability** | Copier-inspired | Conductor should be re-runnable on existing projects |
| **Micro-generation** | Plop-inspired patterns | For later: "give me a new observer module" |

### Open Questions

1. **Should the Conductor be a standalone tool or embedded in relAIn-it's Rust binary?**
   - Standalone = can be used before relAIn-it itself is built
   - Embedded = tighter integration, one binary

2. **Gum availability** — is it installed? Should we bundle it?
   - `winget install charmbracelet.gum` or `go install github.com/charmbracelet/gum@latest`

3. **Template format** — Handlebars (like Plop), Jinja2 (like Copier/Cookiecutter), or simple string replacement?

---

## References

- Copier: https://copier.readthedocs.io
- Cookiecutter: https://cookiecutter.readthedocs.io
- Plop: https://plopjs.com
- Hygen: https://www.hygen.io
- Gum: https://github.com/charmbracelet/gum
- @inquirer/prompts: https://www.npmjs.com/package/@inquirer/prompts
- create-tauri-app: https://tauri.app/start/create-project/
