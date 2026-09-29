# Technical Specification: DPI Resolution Pipeline & Hardware Isolation

This document contains the heavy mathematical specifications, hardware inspection protocols, and multimonitor dynamic scaling mechanisms for the `responsive-rust-gui` skill.

---

## 1. Metric Layer Scale Factor Equation

The primary projection from logical coordinates ($P_{\text{logical}}$) in points (`pt`) to physical screen pixels ($P_{\text{physical}}$) is defined as:

$$P_{\text{physical}} = P_{\text{logical}} \times S$$

Where $S \in \mathbb{R}^+$ is the scale factor multiplier (e.g., $1.0$, $1.25$, $1.5$, $2.0$, $2.5$).

---

## 2. Scale Resolver Precedence Hierarchy

To determine $S$, the system must evaluate sources of truth in strict order:

1. **User Override / CLI Flag**: `--force-scale-factor <float>` or explicit user configuration (`forced.max(0.5)`).
2. **Environment Variables**: `APP_SCALE_FACTOR`, `WINIT_HIDPI_FACTOR`, `GDK_SCALE`, `QT_SCALE_FACTOR`.
3. **OS Windowing Layer**: `Window::scale_factor()` from `winit` (Wayland, Win32, Cocoa, X11).
4. **Hardware Fallback (DRM/KMS/EDID)**:
   Physical monitor dimensions extracted from `/sys/class/drm/card*-*/edid` or `libudev`:

$$\text{PPI} = \frac{\sqrt{W_{\text{px}}^2 + H_{\text{px}}^2}}{\sqrt{\left(\frac{W_{\text{mm}}}{25.4}\right)^2 + \left(\frac{H_{\text{mm}}}{25.4}\right)^2}}$$

$$S_{\text{inferred}} = \max\left(1.0, \, \frac{\text{PPI}}{\text{PPI}_{\text{baseline}}}\right) \quad \text{where } \text{PPI}_{\text{baseline}} = 96.0$$

5. **Default Fallback**: $S = 1.0$.

---

## 3. Edge Cases & Handling Protocols

### Edge Case A: Corrupted EDID / Zero Physical Dimensions (`width_mm == 0 || height_mm == 0`)
* **Symptom**: Division by zero when converting millimeters to inches.
* **Protocol**: Detect `width_mm == 0` or `height_mm == 0`, emit a warning log (`log::warn!`), and gracefully fallback to $S = 1.0$ and $\text{PPI}_{\text{baseline}} = 96.0$.

### Edge Case B: Multi-Monitor Window Drag (DPI Transitions)
* **Symptom**: Moving a window from a 4K display ($S=2.0$) to a 1080p display ($S=1.0$) causes blurred rendering or improper scaling.
* **Protocol**: Subscribe to OS scale factor events (e.g., `WindowEvent::ScaleFactorChanged` in `winit`). On event receipt, update the `ScaleProfile` and immediately invalidate UI rasterization via `ctx.set_pixels_per_point(new_scale)` in `egui` or `scale_factor(&self)` in `iced`.

### Edge Case C: Fractional Scale Snap
* **Symptom**: Subpixel jitter or 1px border misalignment on fractional scale environments ($S = 1.25$ or $1.5$).
* **Protocol**: Perform pixel snapping on calculated bounds before final rasterization:

$$P_{\text{physical\_snapped}} = \text{round}(P_{\text{logical}} \times S)$$
