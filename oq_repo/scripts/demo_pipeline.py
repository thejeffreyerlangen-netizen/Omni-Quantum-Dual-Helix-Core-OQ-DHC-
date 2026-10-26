#!/usr/bin/env python3
"""One-shot demo: catalog sensors → field telemetry → optional PNG."""
from __future__ import annotations
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.facade import OQDHCFacade

def main():
    fac = OQDHCFacade(dimension=48, artifact_dir="artifacts_out")
    report = []
    for name in ["IMX742_Medical", "IMX711_XRay", "LYTIA_L910"]:
        fusion, fields = fac.ingest_cmos(name, seed=1, steps=2)
        fr = fac.render_frame(write_png=True, resolution=128)
        report.append({
            "sensor": name,
            "fusion": fusion.to_dict(),
            "field": fields.to_dict(),
            "render": fr.to_dict(),
        })
        fac.reset()
    os.makedirs("artifacts_out", exist_ok=True)
    out = "artifacts_out/demo_report.json"
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({"ok": True, "report": out, "n": len(report)}, indent=2))

if __name__ == "__main__":
    main()
