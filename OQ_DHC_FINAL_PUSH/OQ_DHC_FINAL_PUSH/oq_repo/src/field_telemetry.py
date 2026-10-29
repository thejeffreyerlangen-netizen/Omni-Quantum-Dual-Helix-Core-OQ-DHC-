"""GTR / field parameter export – shared contract for Python, C-SDK, CSR."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict
import hashlib
import numpy as np

from .protocol import CoreSnapshot


@dataclass
class FieldParams:
    """Readable field parameters after a fusion/render/core step."""
    determinant: float
    residual: float
    torsion_proxy: float
    base_frequency_hz: float
    swat_status: str
    system_status: str
    cycle: int
    frame_seal: str
    psi_energy: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_field_params(snap: CoreSnapshot, torsion: float = 0.0) -> FieldParams:
    psi = np.asarray(snap.state_psi, dtype=np.float64)
    energy = float(np.dot(psi, psi)) if psi.size else 0.0
    # unit-circle style determinant proxy from residual phase
    phase = snap.residual * 0.01
    det = float(np.cos(phase) ** 2 + np.sin(phase) ** 2)
    seal_src = f"{snap.cycle}|{snap.residual:.8e}|{energy:.8e}|{snap.swat_status}"
    seal = hashlib.sha256(seal_src.encode()).hexdigest()[:16]
    return FieldParams(
        determinant=det,
        residual=float(snap.residual),
        torsion_proxy=float(torsion),
        base_frequency_hz=float(snap.base_frequency),
        swat_status=snap.swat_status,
        system_status=snap.system_status,
        cycle=int(snap.cycle),
        frame_seal=seal,
        psi_energy=energy,
    )
