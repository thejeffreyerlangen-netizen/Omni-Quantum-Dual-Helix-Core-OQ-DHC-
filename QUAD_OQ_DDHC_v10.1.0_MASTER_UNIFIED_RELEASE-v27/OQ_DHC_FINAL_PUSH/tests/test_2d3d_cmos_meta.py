#!/usr/bin/env python3
"""Tests: Dimension 2/3 (API), 2D-Feld-Injektion, CMOS-Metadaten-Vollständigkeit."""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "oq_repo")))

from src.core_engine import OmniQuantumDualHelixCoreMaster
from src.cmos_fusion import CMOSFusionEngine

P = F = 0


def chk(name: str, ok: bool, detail: str = "") -> None:
    global P, F
    if ok:
        P += 1
        print(f"  [PASS] {name}" + (f" — {detail}" if detail else ""))
    else:
        F += 1
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    print("=" * 72)
    print(" TEST 2D/3D + CMOS METADATA")
    print("=" * 72)

    # --- 2D/3D as invalid engine dimensions ---
    print("\n--- Dimension 2 / 3 (must reject) ---")
    for d in (2, 3):
        try:
            OmniQuantumDualHelixCoreMaster(dimension=d)
            chk(f"dim_{d}_rejected", False, "expected ValueError")
        except ValueError as e:
            chk(f"dim_{d}_rejected", ">= 4" in str(e), str(e))

    # --- 2D array inject into valid 48-D core (ravel) ---
    print("\n--- 2D field inject (ravel into 48-D) ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=48)
    field_2d = np.sin(np.linspace(0, 2 * np.pi, 48)).reshape(6, 8)
    c.inject_state(field_2d)
    r = c.execute_evolution_cycle(dt=0.01)
    chk("inject_2d_shape", c.state_psi.shape == (48,), str(c.state_psi.shape))
    chk("inject_2d_finite", np.all(np.isfinite(c.state_psi)), "state finite")
    chk("inject_2d_swat", r["swat_status"] == "CONNECTED", r["swat_status"])

    # --- 3D tensor ravel ---
    print("\n--- 3D field inject ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=48)
    field_3d = np.arange(48, dtype=np.float64).reshape(3, 4, 4)
    c.inject_state(field_3d)
    r = c.execute_evolution_cycle(dt=0.01)
    chk("inject_3d_shape", c.state_psi.shape == (48,), str(c.state_psi.shape))
    chk("inject_3d_swat", r["swat_status"] == "CONNECTED", r["swat_status"])

    # --- Helix 4x12 is internal 2D lattice ---
    print("\n--- Internal 4×12 helix lattice ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=48)
    c.state_psi = np.sin(np.linspace(0, 4 * np.pi, 48))
    c.execute_evolution_cycle(dt=0.01)
    helix = c.coupling._reshape_helix()
    chk("helix_shape_4x12", helix.shape == (4, 12), str(helix.shape))
    chk("helix_finite", np.all(np.isfinite(helix)), "ok")

    # --- CMOS metadata completeness ---
    print("\n--- CMOS metadata ---")
    required = {
        "sensor", "pixel_count", "sample_count", "max_voltage",
        "field_determinant", "swat_status", "pins_p", "pins_n", "status",
    }
    eng = CMOSFusionEngine()
    for sensor in eng.list_sensors():
        d = eng.execute_fusion(sensor, seed=1).to_dict()
        missing = required - set(d.keys())
        chk(f"{sensor}_keys", not missing, f"missing={missing}")
        chk(f"{sensor}_det_near_1", abs(float(d["field_determinant"]) - 1.0) < 1e-9,
            str(d["field_determinant"]))
        chk(f"{sensor}_pixel_count", int(d["pixel_count"]) == int(
            __import__("src.cmos_fusion", fromlist=["SENSOR_CATALOG"]).SENSOR_CATALOG[sensor].res_h
            * __import__("src.cmos_fusion", fromlist=["SENSOR_CATALOG"]).SENSOR_CATALOG[sensor].res_v
        ), str(d["pixel_count"]))

    print("\n" + "=" * 72)
    print(f" RESULT: {P} passed, {F} failed")
    print("=" * 72)
    return 0 if F == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
