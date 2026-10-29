#!/usr/bin/env python3
"""Architectural integration tests: facade → core → render → SWAT gate → artifact."""
from __future__ import annotations

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from src.facade import OQDHCFacade
from src.protocol import RenderStatus, SwatStatus


def main() -> int:
    out = Path(__file__).resolve().parent.parent / "artifacts_out"
    fac = OQDHCFacade(dimension=48, artifact_dir=out)
    fac.load_state(np.sin(np.linspace(0, 4 * np.pi, 48)))
    fac.step(5)

    snap = fac.snapshot()
    assert snap.swat_status == SwatStatus.CONNECTED.value, snap
    assert snap.dimension == 48

    fr = fac.render_frame(write_png=True, resolution=128)
    assert fr.status == RenderStatus.SUCCESS.value, fr
    assert fr.artifact_path and Path(fr.artifact_path).is_file(), fr.artifact_path
    assert fr.width == 128 and fr.height == 128
    print(f"[PASS] render artifact: {fr.artifact_path} id={fr.frame_id}")

    # Force lockdown path via direct state (architectural gate test)
    fac.core.swat_status = SwatStatus.PHYSICALLY_DISCONNECTED.value
    fr2 = fac.render_frame(write_png=False)
    assert fr2.status == RenderStatus.REJECTED_LOCKDOWN.value, fr2
    print("[PASS] SWAT gates render")

    fac.reset()
    fac.load_state(np.sin(np.linspace(0, 2 * np.pi, 48)) * 0.5)
    fac.step(2)
    assert fac.snapshot().swat_status == SwatStatus.CONNECTED.value
    print("[PASS] reset restores CONNECTED")

    profiles = fac.twin.list_profiles()
    assert len(profiles) >= 1
    twin = fac.run_twin(profiles[0])
    assert "e_chain_frame_seal" in twin
    print(f"[PASS] twin profile {profiles[0]}")

    print("ALL INTEGRATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
