#!/usr/bin/env python3
"""
Generate a complete KiCad BGA-144 footprint (12×12, 0.8 mm pitch)
for the OQ-DHC package.

Usage:
  python gen_bga144_footprint.py [--out PATH] [--pitch 0.8] [--pad 0.4]

Default output:
  ../oq_dhc_devboard/footprints/BGA-144_12x12_0.8mm.kicad_mod
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

ROWS = "ABCDEFGHIJKL"  # 12 rows
N = 12


def generate(pitch: float = 0.8, pad_size: float = 0.4) -> str:
    half = (N - 1) / 2.0
    court = half * pitch + 0.8
    fab = half * pitch + 0.0

    lines: list[str] = [
        '(footprint "BGA-144_12x12_0.8mm"',
        '  (version 20221018)',
        '  (generator "gen_bga144_footprint.py")',
        '  (layer "F.Cu")',
        '  (descr "BGA-144 12x12 0.8mm pitch – full OQ-DHC package")',
        '  (tags "bga 144 oq-dhc 0.8mm")',
        '  (attr smd)',
        '  (fp_text reference "REF**" (at 0 -7.5) (layer "F.SilkS")',
        '    (effects (font (size 1 1) (thickness 0.15))))',
        '  (fp_text value "BGA-144_12x12_0.8mm" (at 0 7.5) (layer "F.Fab")',
        '    (effects (font (size 1 1) (thickness 0.15))))',
        f'  (fp_rect (start -{court:.3f} -{court:.3f}) (end {court:.3f} {court:.3f})',
        '    (stroke (width 0.1) (type default)) (fill none) (layer "F.CrtYd"))',
        f'  (fp_rect (start -{fab:.3f} -{fab:.3f}) (end {fab:.3f} {fab:.3f})',
        '    (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))',
        # Pin-1 (A1) marker on silkscreen
        f'  (fp_circle (center {-half*pitch:.3f} {-half*pitch - 0.6:.3f}) '
        f'(end {-half*pitch:.3f} {-half*pitch - 0.35:.3f})',
        '    (stroke (width 0.1) (type default)) (fill none) (layer "F.SilkS"))',
    ]

    for ri, row in enumerate(ROWS):
        y = -half * pitch + ri * pitch
        for ci in range(1, N + 1):
            x = -half * pitch + (ci - 1) * pitch
            pad = f"{row}{ci}"
            lines.append(
                f'  (pad "{pad}" smd circle (at {x:.4f} {y:.4f}) '
                f'(size {pad_size} {pad_size}) (layers "F.Cu" "F.Paste" "F.Mask"))'
            )

    lines.append(")")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate OQ-DHC BGA-144 KiCad footprint")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "oq_dhc_devboard"
        / "footprints"
        / "BGA-144_12x12_0.8mm.kicad_mod",
    )
    ap.add_argument("--pitch", type=float, default=0.8)
    ap.add_argument("--pad", type=float, default=0.4)
    args = ap.parse_args()

    text = generate(pitch=args.pitch, pad_size=args.pad)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    pad_count = text.count('(pad "')
    print(f"Wrote {args.out}  ({pad_count} pads, pitch={args.pitch} mm)")


if __name__ == "__main__":
    main()
