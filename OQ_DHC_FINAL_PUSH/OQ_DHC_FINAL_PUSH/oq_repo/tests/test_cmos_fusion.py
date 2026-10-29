#!/usr/bin/env python3
"""Sony-class CMOS envelope stress vectors → fusion engine + optional core inject."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from src.cmos_fusion import CMOSFusionEngine, SENSOR_CATALOG, V_CRITICAL_PEAK
from src.facade import OQDHCFacade
from src.protocol import SwatStatus


def main() -> int:
    eng = CMOSFusionEngine()
    assert set(eng.list_sensors()) == set(SENSOR_CATALOG.keys())

    for name in eng.list_sensors():
        r = eng.execute_fusion(name, seed=7)
        print(f"\n[FUSION] {name}")
        print(f"  pixels={r.pixel_count} samples={r.sample_count} Vmax={r.max_voltage:.3f}")
        print(f"  det={r.field_determinant:.12f} SWAT={r.swat_status}")
        print(f"  pins P={r.pins_p} N={r.pins_n} | {r.status}")
        assert r.field_determinant > 0.99
        assert r.swat_status == SwatStatus.CONNECTED.value
        assert r.status == "NOMINAL_FIELD_PROXY_ACTIVE"

    # Overvoltage → SWAT blank
    hot = np.array([1.0, 2.0, V_CRITICAL_PEAK + 0.5])
    r_hot = eng.execute_fusion("LYTIA_L910", analog_voltages=hot)
    assert r_hot.swat_status == SwatStatus.PHYSICALLY_DISCONNECTED.value
    assert r_hot.pins_p == "000000" and r_hot.pins_n == "000000"
    print("\n[PASS] overvoltage trips SWAT blank")

    # Inject downsampled voltages into digital core path
    fac = OQDHCFacade(dimension=48)
    samples = np.linspace(1.2, 2.5, 1024)
    fac.load_state(eng.voltages_to_psi(samples, 48))
    fac.step(3)
    assert fac.snapshot().swat_status == SwatStatus.CONNECTED.value
    print("[PASS] PSI inject from CMOS sample window")

    print("\n[✓ ALL CMOS FUSION TESTS PASSED]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
