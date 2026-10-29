#!/usr/bin/env python3
"""End-to-end: CMOS → core → field params → render gate → SWAT."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.facade import OQDHCFacade
from src.protocol import SwatStatus, RenderStatus
from src.cmos_fusion import CMOSFusionEngine, V_CRITICAL_PEAK
import numpy as np

def main() -> int:
    fac = OQDHCFacade(dimension=48, artifact_dir="artifacts_out")
    eng = CMOSFusionEngine()

    for name in eng.list_sensors():
        fusion, fields = fac.ingest_cmos(name, seed=11, steps=2)
        print(f"[{name}] fusion={fusion.status} seal={fields.frame_seal} det={fields.determinant:.6f}")
        assert fields.determinant > 0.99
        fr = fac.render_frame(write_png=True, resolution=64)
        assert fr.status == RenderStatus.SUCCESS.value
        print(f"  render={fr.status} artifact={fr.artifact_path}")

    # Overvoltage path via fusion engine then core
    hot = np.array([0.5, V_CRITICAL_PEAK + 1.0])
    r = eng.execute_fusion("LYTIA_L910", analog_voltages=hot)
    assert r.swat_status == SwatStatus.PHYSICALLY_DISCONNECTED.value
    fac.core.swat_status = r.swat_status
    fr2 = fac.render_frame(write_png=False)
    assert fr2.status == RenderStatus.REJECTED_LOCKDOWN.value
    print("[PASS] e2e SWAT blocks render after CMOS overvoltage")

    fac.reset()
    fp = fac.get_field_params()
    assert fp.swat_status == SwatStatus.CONNECTED.value
    print(f"[PASS] field_params after reset cycle={fp.cycle} energy={fp.psi_energy:.4f}")
    print("ALL E2E TESTS PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
