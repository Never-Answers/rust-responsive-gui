#!/usr/bin/env python3
"""
Static Layout Validator for Rust GUIs (`validate_layout.py`)
Rigorously audits Rust UI code (egui, eframe, iced) for responsiveness anti-patterns:
1. Hardcoded physical pixel checks in breakpoints (> 1080, > 1440, > 1920)
2. Synchronous I/O operations or hardware checks inside render loops or UI helper functions
3. Hardcoded magic numbers in layout calls (set_width, add_sized, Length::Fixed, padding, etc.)

Supports single files or recursive directory scanning (e.g. `python3 validate_layout.py src/`).
"""

import os
import sys
import re
from pathlib import Path


def extract_function_bodies(content):
    """
    Extracts function names and their full body text using a brace-matching parser.
    Handles nested blocks (if, match, closures) correctly without early truncation.
    """
    functions = []
    # Match function signatures
    fn_header_pattern = re.compile(
        r"(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*(?:<.*?>)?\s*\((.*?)\)(?:\s*->\s*[^{]+)?\s*\{",
        re.DOTALL,
    )

    for match in fn_header_pattern.finditer(content):
        fn_name = match.group(1)
        start_idx = match.end() - 1  # Index of opening brace '{'

        # Count braces to find matching closing brace
        brace_count = 0
        end_idx = start_idx
        in_string = False
        escape = False

        for i in range(start_idx, len(content)):
            char = content[i]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break

        body = content[start_idx + 1 : end_idx]
        functions.append((fn_name, body))

    return functions


def validate_rust_file(file_path):
    errors = []
    warnings = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"ERROR: Could not read file {file_path}: {e}"], []

    # Filter out pure test files if necessary, or process all .rs
    functions = extract_function_bodies(content)

    # UI render loop function names or helpers
    ui_fn_patterns = re.compile(
        r"^(update|view|render|draw|build|ui|show|view_.*|render_.*|draw_.*)$"
    )

    # 1. Synchronous I/O / Hardware check in UI functions
    for fn_name, body in functions:
        if ui_fn_patterns.match(fn_name):
            io_patterns = [
                (r"std::fs::", "std::fs file operations"),
                (r"read_to_string", "file read_to_string"),
                (r"File::open", "File::open call"),
                (r"/sys/class/drm", "DRM/sysfs hardware access"),
                (r"/dev/", "device file access"),
                (r"reqwest::", "blocking network call"),
                (r"ureq::", "blocking network call"),
                (r"Command::new", "external process execution"),
            ]
            for pattern, desc in io_patterns:
                if re.search(pattern, body):
                    errors.append(
                        f"Line check in `{fn_name}` ({file_path.name}): Detected {desc} inside UI render function `{fn_name}`. "
                        "Move synchronous I/O or hardware checks to application startup (`ScaleResolver`)."
                    )

    # 2. Hardcoded large physical pixel breakpoints
    breakpoint_patterns = [
        (
            r"screen_rect\(\)\.width\(\)\s*>\s*(1080|1440|1920|2560|3840)",
            "Direct physical pixel comparison",
        ),
        (
            r"width_px\s*>\s*(1080|1440|1920|2560|3840)",
            "Direct physical pixel variable check",
        ),
        (
            r"window\.inner_size\(\)\.width\s*>\s*(1080|1440|1920|2560|3840)",
            "Raw physical window width comparison",
        ),
    ]
    for pattern, desc in breakpoint_patterns:
        matches = re.finditer(pattern, content)
        for m in matches:
            warnings.append(
                f"In {file_path.name}: {desc} (`{m.group(0)}`). "
                "Ensure width is normalized by scale factor S into logical points before evaluating breakpoints."
            )

    # 3. Magic Numbers in layout dimensions (egui & iced)
    layout_magic_patterns = [
        # egui
        (
            r"(set_width|set_height|set_min_width|set_max_width|add_sized|add_space)\s*\(\s*\[?\s*([0-9]{2,4}\.[0-9]+|[0-9]{2,4})\s*[,\]\)]",
            "egui layout call",
        ),
        # iced
        (
            r"Length::Fixed\s*\(\s*([0-9]{2,4}\.[0-9]+|[0-9]{2,4})\s*\)",
            "iced Length::Fixed call",
        ),
        (
            r"\.(padding|spacing|width|height)\s*\(\s*([0-9]{2,4}\.[0-9]+|[0-9]{2,4})\s*\)",
            "iced/egui layout modifier",
        ),
    ]

    for pattern, desc in layout_magic_patterns:
        for match in re.finditer(pattern, content):
            # Extract number
            groups = match.groups()
            num_val = groups[-1]
            # Ignore standard small zeros/ones if needed, but flag magic layout scalars > 1.0
            try:
                val_float = float(num_val)
                if val_float > 0.0:
                    warnings.append(
                        f"In {file_path.name}: Hardcoded magic number `{num_val}` in {desc} (`{match.group(0)}`). "
                        "Extract scalar values into `DesignTokens` or `LayoutConfig` to maintain code modularity."
                    )
            except ValueError:
                pass

    return errors, warnings


def run_validation(target_path):
    target = Path(target_path)
    all_errors = []
    all_warnings = []
    files_scanned = 0

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.rs"))
    else:
        print(f"Error: Target path '{target_path}' does not exist.")
        return 1

    for file_path in files:
        # Skip target/ directory or generated files
        if "target/" in str(file_path):
            continue
        files_scanned += 1
        errors, warnings = validate_rust_file(file_path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    print("=== Antigravity Responsive Rust GUI Static Analysis ===")
    print(f"Target Path: {target_path}")
    print(f"Files Scanned: {files_scanned}\n")

    if all_errors:
        print("-> FAILURES DETECTED:")
        for err in all_errors:
            print(f"  - {err}")

    if all_warnings:
        print("\n-> WARNINGS:")
        for warn in all_warnings:
            print(f"  - {warn}")

    if not all_errors and not all_warnings:
        print(
            "-> PASSED: No anti-patterns detected across scanned files. Code adheres to modular responsive rules."
        )
        return 0
    elif all_errors:
        return 1
    else:
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_layout.py <path_to_rust_file_or_directory>")
        sys.exit(1)

    sys.exit(run_validation(sys.argv[1]))
