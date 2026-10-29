"""
OQ-DHC CMOS interface & fusion test vectors (Layer 1).

Models the *digital boundary* of a sensor→core path:
  sensor profile + analog sample window → field proxy + SWAT gate check.

Does not implement physical ADC-less memristor coupling; that remains
Phase-2 / off-first-die. Digitized or emulated samples enter the same
CSR/PSI protocol as the rest of the stack.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import numpy as np

from .protocol import SwatStatus


@dataclass(frozen=True)
class SensorProfile:
    name: str
    res_h: int
    res_v: int
    fps: float
    v_min: float
    v_max: float
    notes: str = ""


# Real-world oriented envelopes (public Sony-class product points; used as stress vectors)
SENSOR_CATALOG: Dict[str, SensorProfile] = {
    "IMX742_Medical": SensorProfile(
        name="IMX742_Medical",
        res_h=720,
        res_v=720,
        fps=60.0,
        v_min=1.2,
        v_max=2.7,
        notes="compact medical / endoscope-class envelope",
    ),
    "IMX711_XRay": SensorProfile(
        name="IMX711_XRay",
        res_h=384,
        res_v=728,
        fps=26100.0,
        v_min=-1.2,
        v_max=2.7,
        notes="high-speed X-ray class envelope",
    ),
    "LYTIA_L910": SensorProfile(
        name="LYTIA_L910",
        res_h=8160,
        res_v=6120,
        fps=30.0,
        v_min=0.0,
        v_max=3.3,
        notes="high-DR mobile stacked-CMOS class envelope",
    ),
}

# BGA / IO safety rail used by digital SWAT proxy (volts)
V_CRITICAL_PEAK = 3.0
RESONANCE_ANCHOR_HZ = 98.112


@dataclass
class FusionResult:
    sensor: str
    pixel_count: int
    sample_count: int
    max_voltage: float
    field_determinant: float
    swat_status: str
    pins_p: str
    pins_n: str
    status: str
    bus_complexity: str = "O(1)_protocol_path"  # protocol path, not physical proof

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CMOSFusionEngine:
    """
    Maps sensor envelopes + voltage samples into GTR/SWAT-facing telemetry.
    Optional: downsample voltages into PSI-sized vector for core inject.
    """

    def __init__(self, resonance_hz: float = RESONANCE_ANCHOR_HZ):
        self.resonance_hz = resonance_hz
        self.swat_interlock_tripped = False

    def list_sensors(self) -> List[str]:
        return list(SENSOR_CATALOG.keys())

    def execute_fusion(
        self,
        sensor_name: str,
        analog_voltages: Optional[np.ndarray] = None,
        sample_n: int = 1024,
        seed: Optional[int] = None,
    ) -> FusionResult:
        if sensor_name not in SENSOR_CATALOG:
            raise KeyError(f"unknown sensor profile: {sensor_name}")
        spec = SENSOR_CATALOG[sensor_name]
        rng = np.random.default_rng(seed)

        if analog_voltages is None:
            # Nominal path: stay within digital SWAT rail; full v_max used in explicit overvoltage tests
            hi = min(spec.v_max, V_CRITICAL_PEAK - 1e-3)
            lo = min(spec.v_min, hi)
            analog_voltages = rng.uniform(lo, hi, size=sample_n)
        else:
            analog_voltages = np.asarray(analog_voltages, dtype=np.float64).ravel()

        total_elements = int(spec.res_h) * int(spec.res_v)
        time_delta = 1.0 / max(spec.fps, 1e-9)
        # symplectic-style unit circle identity (numerical check ≈ 1)
        field_determinant = float(
            np.cos(time_delta * self.resonance_hz) ** 2
            + np.sin(time_delta * self.resonance_hz) ** 2
        )

        max_peak = float(np.max(analog_voltages))
        if max_peak > V_CRITICAL_PEAK:
            self.swat_interlock_tripped = True
            swat = SwatStatus.PHYSICALLY_DISCONNECTED.value
            pins_p, pins_n = "000000", "000000"
            status = "CRITICAL_LOCKDOWN_PINS_BLANKED"
        else:
            swat = SwatStatus.CONNECTED.value
            ok = field_determinant > 0.99
            pins_p = "011110" if ok else "000000"
            pins_n = "100001" if ok else "000000"
            status = "NOMINAL_FIELD_PROXY_ACTIVE"

        return FusionResult(
            sensor=sensor_name,
            pixel_count=total_elements,
            sample_count=int(analog_voltages.size),
            max_voltage=max_peak,
            field_determinant=field_determinant,
            swat_status=swat,
            pins_p=pins_p,
            pins_n=pins_n,
            status=status,
        )

    def voltages_to_psi(self, voltages: np.ndarray, dimension: int = 48) -> np.ndarray:
        """Downsample / reshape sample window into PSI vector for core inject."""
        v = np.asarray(voltages, dtype=np.float64).ravel()
        if v.size == 0:
            return np.zeros(dimension, dtype=np.float64)
        idx = np.linspace(0, v.size - 1, dimension).astype(int)
        return v[idx].copy()


def run_all_catalog_scenarios(seed: int = 42) -> List[FusionResult]:
    eng = CMOSFusionEngine()
    return [eng.execute_fusion(name, seed=seed + i) for i, name in enumerate(eng.list_sensors())]
