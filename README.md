# `responsive-rust-gui` — Antigravity Agent Skill

An open-source **Google Antigravity Agent Skill** designed to guide, audit, and refactor standalone responsive user interfaces in Rust using **`egui/eframe`** and **`iced`**.

It equips AI coding assistants (such as Antigravity, Cursor, and Claude) with architectural directives to enforce DPI scaling pipelines, logical point normalization, modular tokenization, and static analysis verification.

---

## Overview

Building responsive GUIs in Rust across diverse hardware—from small 5-inch handhelds (e.g., Steam Deck) to 4K Ultrawide monitors—often leads AI agents into common pitfalls: hardcoding physical pixel thresholds, mixing DPI scaling with layout topology, or executing synchronous I/O inside render loops.

The `responsive-rust-gui` skill transforms your AI agent into an opinionated, pragmatic UI architect that enforces clean separation of concerns and maintainable, modular Rust code.

---

## Directory Package Architecture

Built according to the **Google Antigravity Skill Specification** (Level 1–4 progressive disclosure pattern):

```text
responsive-rust-gui/
├── SKILL.md                         # Core skill definition (YAML Frontmatter & Directives)
├── references/                      # Deep technical specs (Level 2: Asset Utilization)
│   └── dpi_pipeline_spec.md         # DPI resolution equations, EDID/DRM fallback & scale hierarchy
├── examples/                        # Golden pair for few-shot learning (Level 3: Few-Shot)
│   ├── input_legacy_ui.rs           # Legacy code exhibiting anti-patterns
│   └── output_responsive_ui.rs      # Canonical refactored code (LayoutConfig, DesignTokens, LayoutTier)
└── scripts/                         # Deterministic static analysis (Level 4: Procedural Logic)
    └── validate_layout.py           # Python validator catching magic numbers and sync render I/O
```

---

## Core Architectural Invariants

1. **User Style Precedence (`USER_STYLE_OVERRIDE`)**: The user's global coding conventions always take absolute precedence over generic library defaults.
2. **Layer Separation**:
   - **Metric Layer**: Adjusts rasterization multiplier $S$ ($P_{\text{physical}} = P_{\text{logical}} \times S$).
   - **Structural Layer**: Operates exclusively on normalized logical points ($W_{\text{pt}} = W_{\text{px}} / S$).
3. **Pragmatic Debate (`DEBATE_POLICY`)**: The agent alerts the user upon detecting architectural risks. If the user acknowledges the risk and insists on their approach, the agent yields immediately with inline code documentation.
4. **Zero Magic Numbers (`CODE_STYLE_POLICY`)**: Eliminates literal scalar dimensions inside `update`/`view` methods in favor of `DesignTokens` and `LayoutConfig`.
5. **Wireframe Validation (`WORKFLOW_POLICY`)**: Encourages rapid layout validation using placeholder components before attaching complex domain state.

---

## Quick Start & Installation

### Option 1: Workspace / Project Scope (Recommended)

Clone or copy the skill directory into your project's `.agents/skills/` folder:

```bash
mkdir -p .agents/skills/
cp -r responsive-rust-gui .agents/skills/
```

### Option 2: Global Scope

To make the skill available across all local projects in **Antigravity** or **Antigravity CLI (`agy`)**:

```bash
# Antigravity CLI / Global Agent Skills
mkdir -p ~/.gemini/antigravity-cli/skills/
cp -r responsive-rust-gui ~/.gemini/antigravity-cli/skills/
```

### Option 3: Via `npx skills` Package Manager

```bash
npx skills add github.com/Never-Answers/responsive-rust-gui
```

---

## Usage with Antigravity CLI (`agy`)

Once installed, the agent will automatically trigger the skill when responsive Rust GUI tasks are requested, or you can invoke it directly:

```bash
agy --skill responsive-rust-gui "Audit and refactor src/ui/dashboard.rs"
```

### Running the Static Validator

You can run the included static analysis script manually or within your CI/CD pipeline:

```bash
# Scan a single Rust UI file
python3 scripts/validate_layout.py src/ui/dashboard.rs

# Scan an entire directory of Rust source files
python3 scripts/validate_layout.py src/ui/
```

---

## Before & After Refactoring Example

### Before (Legacy Anti-Patterns)

```rust
// Hardcoded dimensions and physical pixel checks inside update loop
if ctx.screen_rect().width() > 1920.0 {
    ui.set_width(350.0);
    let edid = std::fs::read_to_string("/sys/class/drm/card0/edid").unwrap(); // Sync I/O in render!
}
```

### After (Canonical Refactored Code)

```rust
// Normalized logical tier resolution & modular tokens
let width_pt = ctx.screen_rect().width();
let tier = LayoutTier::resolve(width_pt, &self.config);

ui.set_width(self.config.tokens.sidebar_width_pt);
```

---

## License

Distributed under the **WTFPL** License.
