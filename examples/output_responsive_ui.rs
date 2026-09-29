// Canonical Refactored Example: Responsive Rust GUI with Modular Layout & Logical Normalization

use eframe::egui;

/// Modular design tokens isolating raw scalars from rendering logic.
#[derive(Debug, Clone, Copy)]
pub struct DesignTokens {
    pub min_touch_target_pt: f32,
    pub sidebar_width_pt: f32,
    pub spacing_unit_pt: f32,
}

impl Default for DesignTokens {
    fn default() -> Self {
        Self {
            min_touch_target_pt: 48.0,
            sidebar_width_pt: 300.0,
            spacing_unit_pt: 12.0,
        }
    }
}

/// Modular layout configuration for topological tier thresholds.
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
            tokens: DesignTokens::default(),
        }
    }
}

/// Normalized layout tier classification based on logical points.
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum LayoutTier {
    Compact,
    Medium,
    Expanded,
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

pub struct ResponsiveDashboardApp {
    pub config: LayoutConfig,
    pub scale_factor: f32,
}

impl eframe::App for ResponsiveDashboardApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // 1. Enforce scale factor on the metric layer
        ctx.set_pixels_per_point(self.scale_factor);

        // 2. Evaluate screen width in normalized logical points
        let width_pt = ctx.screen_rect().width();
        let tier = LayoutTier::resolve(width_pt, &self.config);

        // 3. Render according to structural tier
        egui::CentralPanel::default().show(ctx, |ui| match tier {
            LayoutTier::Compact => self.render_compact(ui),
            LayoutTier::Medium | LayoutTier::Expanded => self.render_expanded(ui, tier),
        });
    }
}

impl ResponsiveDashboardApp {
    fn render_compact(&self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.heading("Compact / Handheld View");
            ui.add_space(self.config.tokens.spacing_unit_pt);
            ui.add_sized(
                [ui.available_width(), self.config.tokens.min_touch_target_pt],
                egui::Button::new("Primary Touch Action"),
            );
        });
    }

    fn render_expanded(&self, ui: &mut egui::Ui, tier: LayoutTier) {
        ui.horizontal(|ui| {
            ui.group(|ui| {
                ui.set_width(self.config.tokens.sidebar_width_pt);
                ui.label("Sidebar Navigation");
            });
            ui.add_space(self.config.tokens.spacing_unit_pt);
            ui.group(|ui| {
                ui.heading(format!("Dashboard View ({:?})", tier));
            });
        });
    }
}
