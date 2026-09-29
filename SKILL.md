---
name: responsive-rust-gui
description: Audits, guides, and refactors responsive Rust GUIs in egui/eframe and iced. Enforces metric vs structural layer separation, zero magic numbers, modular layout tokens, and user style override precedence. Use when designing, reviewing, or refactoring Rust desktop or embedded interfaces.
---

# Skill: `responsive-rust-gui`

A skill for guiding, auditing, and enhancing the creation and refactoring of responsive GUIs in Rust using `egui/eframe` and `iced` within the Antigravity ecosystem.

---

## 0. Supreme Directive: Precedence of User Global Style (`USER_STYLE_OVERRIDE`)

> **ABSOLUTE GOLDEN RULE**: The user's global code style directives and conventions take **total and unrestricted precedence** over any Rust standard, framework convention (`egui`/`iced`), or technical rule contained within this skill.

* **Inviolability of Style**: In the event of any conflict between the user's preferred style (naming conventions, error handling patterns, formatting, macro usage, folder architecture, or coding habits) and the generic recommendations of this skill, the agent **must strictly adopt the user's style** without contestation.
* **Harmonious Integration**: The responsiveness, DPI, and layout rules contained in this skill must be expressed using the user's coding style as the baseline syntax.

---

## 1. Interaction & Operational Policies

### 1.1 Pragmatic Firmness & Respectful Debate (`DEBATE_POLICY`)
The agent acts as a rigorous architectural guardian while remaining pragmatic and flexible:

1. **First Pass (Architectural Alert)**:
   Upon identifying a user proposal that violates a responsiveness invariant (e.g., checking raw physical pixel width, executing I/O inside the render loop, coupling competing GUI runtimes), the agent **must pause generating final code** and present a clear, technical alert:
   * **Risk Diagnosis**: Explain the root cause and impact (e.g., UI distortion on 4K/HiDPI screens, FPS drops).
   * **Recommended Alternative**: Present the canonical solution aligned with invariants.
2. **Second Pass (Immediate Compliance)**:
   If the user acknowledges the risks or chooses to proceed with their original design (e.g., fixed industrial kiosk constraints), the agent **must yield immediately**. The agent implements the exact requested route with a concise inline code comment documenting the exception.

### 1.2 Zero "Magic Numbers" & Modular Design (`CODE_STYLE_POLICY`)
To prevent maintenance debt, the agent enforces modularization by default:

* **Zero Loose Scalars**: Literal numerical values (widths, heights, margins, font sizes, corner radii, or breakpoints) must never appear directly inside drawing/render methods (`update` in `egui` or `view` in `iced`).
* **Named Constants & Modular Configs**: All visual parameters and topological boundaries must be declared via named constants with explicit unit suffixes (e.g., `pub const BREAKPOINT_COMPACT_PT: f32 = 768.0;`) or encapsulated in reusable structs like `DesignTokens` and `LayoutConfig`.

### 1.3 Placeholder & Wireframe Validation (`WORKFLOW_POLICY`)
Before wiring complex domain logic:

* **Topological Prototyping First**: Propose building lightweight wireframes using placeholder elements (colored panels, stubbed buttons, layout labels).
* **Resize & Scale Testing**: Verify layout adaptation against window resize events and scale factor changes in logical points before binding domain state.

---

## 2. Architectural Invariants & Layer Separation

```
+-----------------------------------------------------------------------+
|                            PHYSICAL LAYER                             |
|          Native Resolutions (px) & Real Display Dimensions (mm)        |
+-----------------------------------------------------------------------+
                                   |
                                   v  [Scale Factor (S) via ScaleResolver]
+-----------------------------------------------------------------------+
|                            METRIC LAYER                               |
|        Logical Coordinates & Density-Independent Points (pt)          |
+-----------------------------------------------------------------------+
                                   |
                                   v  [Topology: Flexbox / Grid / Tiers]
+-----------------------------------------------------------------------+
|                           STRUCTURAL LAYER                            |
|       Node Hierarchy, Panels, Design Tokens & Layout Tiers            |
+-----------------------------------------------------------------------+
```

1. **Metric Layer vs. Structural Layer**:
   * The **Metric Layer** handles scale factor rasterization ($P_{\text{physical}} = P_{\text{logical}} \times S$). It ensures physical readability without altering the component tree.
   * The **Structural Layer** operates strictly on **logical points** ($P_{\text{logical}}$). It manages aspect ratios, columns, panel visibility, and layout flow.
2. **Mandatory Logical Normalization**:
   * All layout decisions (breakpoints, `LayoutTier`) must evaluate normalized logical dimensions ($W_{\text{pt}} = W_{\text{px}} / S$).
3. **Hardware & OS I/O Isolation**:
   * Hardware scans (EDID/DRM in `/sys/class/drm`) or window manager scale queries must execute exclusively during startup (`ScaleResolver`), emitting an immutable or reactive metric for the vision layer. Reference `references/dpi_pipeline_spec.md` for full hardware fallback equations.
4. **Framework Selection Matrix**:
   * **`egui` + `egui_taffy`**: For immediate mode tools, internal panels, and operational dashboards (using `egui_taffy` to prevent flexbox layout jitter).
   * **`iced` (TEA)**: For retained/reactive applications using Elm Architecture, structuring layouts via `Row`, `Column`, `Space`, and `Length::FillPortion`.

---

## 3. Interception Matrix & Technical Alerts

| User Proposal / Choice | Invariant Violated | Agent Alert & Debate Response |
| :--- | :--- | :--- |
| **Checking physical pixels (`width_px > 1920`) for breakpoints** | Confusing pixel density (DPI) with layout topology. | Alert that on a 4K display ($S=2.0$), a 1920px physical window is logically only 960pt (compact). Propose logical point normalization. |
| **Executing `/sys/class/drm` or disk I/O inside `update`/`view`** | Synchronous I/O in the per-frame render loop. | Warn about frame drops and high latency. Recommend moving scale resolution to application startup. |
| **Coupling Slint or multiple runtimes inside `iced`** | Runtime bloat and conflicting event loops. | Question necessity and demonstrate native `iced` reactive flexbox (`Row`/`Column`/`FillPortion`). |
| **Small touch targets ($\le 24\text{ pt}$) on handheld profiles** | Ergonomic mismatch with primary input modality. | Warn about touch precision and suggest `DesignTokens::for_handheld_touch()` ($\ge 44\text{–}48\text{ pt}$). |

---

## 4. Modular Templates & Canonical Patterns

### 4.1 Design Tokenization & Modular Configuration

```rust
#[derive(Debug, Clone, Copy)]
pub struct DesignTokens {
    pub min_touch_target_pt: f32,
    pub spacing_unit_pt: f32,
    pub font_heading_pt: f32,
    pub font_body_pt: f32,
    pub corner_radius_pt: f32,
}

impl DesignTokens {
    pub fn for_handheld_touch() -> Self {
        Self {
            min_touch_target_pt: 48.0,
            spacing_unit_pt: 16.0,
            font_heading_pt: 24.0,
            font_body_pt: 16.0,
            corner_radius_pt: 8.0,
        }
    }

    pub fn for_desktop_mouse() -> Self {
        Self {
            min_touch_target_pt: 28.0,
            spacing_unit_pt: 8.0,
            font_heading_pt: 20.0,
            font_body_pt: 14.0,
            corner_radius_pt: 4.0,
        }
    }
}

pub struct LayoutConfig {
    pub compact_threshold_pt: f32,
    pub medium_threshold_pt: f32,
    pub tokens: DesignTokens,
}

impl Default for LayoutConfig {
    fn default() -> Self {
        Self {
            compact_threshold_pt: 768.0,
            medium_threshold_pt: 1440.0,
            tokens: DesignTokens::for_desktop_mouse(),
        }
    }
}
```

### 4.2 Logical Breakpoint Classification (`LayoutTier`)

```rust
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum LayoutTier {
    Compact,   // Handhelds & portrait screens (< 768 pt)
    Medium,    // Laptops & mid-sized displays (768 - 1440 pt)
    Expanded,  // Desktop 1080p, 4K, & Ultrawide (> 1440 pt)
}

impl LayoutTier {
    pub fn resolve(width_pt: f32, config: &LayoutConfig) -> Self {
        if width_pt < config.compact_threshold_pt {
            Self::Compact
        } else if width_pt < config.medium_threshold_pt {
            Self::Medium
        } else {
            Self::Expanded
        }
    }
}
```

---

## 5. Assets, Scripts & References

This skill includes bundled assets for progressive disclosure:

* **Hardware & DPI Specifications**: Refer to `references/dpi_pipeline_spec.md` for exact PPI equations, EDID parsing logic, and multimonitor dynamic scaling protocols.
* **Golden Examples (Few-Shot)**:
  * `examples/input_legacy_ui.rs` — Legacy anti-pattern code with magic numbers and physical pixel checks.
  * `examples/output_responsive_ui.rs` — Canonical refactored version with modular structs and logical point normalization.
* **Static Analysis Script**:
  * Execute `python scripts/validate_layout.py <path_to_rust_file>` to run a deterministic check for magic numbers and render-loop I/O before delivering code.

---

## 6. Output Verification & Delivery Checklist

Before delivering code to the user, verify:

1. **User Style Precedence**: Does the code strictly follow the user's global style rules?
2. **Zero Magic Numbers**: Are all visual dimensions encapsulated in constants or configuration structs?
3. **Logical Point Normalization**: Are all breakpoint checks performed on logical coordinates ($W_{\text{pt}}$)?
4. **Respected Overrides**: If the user rejected an architectural recommendation, was their choice implemented immediately with inline documentation?
