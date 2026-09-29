// Anti-pattern Example: Unresponsive Rust GUI with Magic Numbers and Physical Pixel Checks
// DO NOT USE THIS PATTERN - Included for skill comparison purposes.

use eframe::egui;

pub struct LegacyDashboardApp {
    pub scale: f32,
}

impl eframe::App for LegacyDashboardApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // ANTI-PATTERN 1: Synchronous I/O in the per-frame render loop!
        let _edid_data = std::fs::read_to_string("/sys/class/drm/card0-DP-1/edid").ok();

        // ANTI-PATTERN 2: Checking physical pixels directly instead of normalized logical points!
        // On a 4K display (3840px) at S=2.0, this treats a 1920px window as "Ultrawide" when it is logically only 960pt.
        if ctx.screen_rect().width() > 1920.0 {
            egui::CentralPanel::default().show(ctx, |ui| {
                ui.horizontal(|ui| {
                    // ANTI-PATTERN 3: Loose "magic numbers" soltos no código!
                    ui.set_width(350.0); // Hardcoded sidebar width
                    ui.label("Sidebar");

                    ui.add_space(12.0); // Hardcoded margin
                    ui.add_sized([400.0, 48.0], egui::Button::new("Action")); // Hardcoded button size
                });
            });
        } else {
            egui::CentralPanel::default().show(ctx, |ui| {
                ui.vertical(|ui| {
                    ui.label("Compact");
                    ui.add_sized([200.0, 30.0], egui::Button::new("Action"));
                });
            });
        }
    }
}
