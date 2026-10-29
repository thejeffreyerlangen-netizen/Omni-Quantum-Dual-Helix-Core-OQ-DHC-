"""
Omni Quantum Dual Helix Core (OQ-DHC) – Coupling Kernel & Master Engine
Version 1.1.0 – Hardened, dimension-aware, SWAT-stable under normal load.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class LedgerEntry:
    block: str
    torsion: float
    e_res: float
    gip_status: str
    residual: float
    timestamp: float
    root_hash: str


class OQDHC_Coupling_Kernel:
    """
    Layer-8 GIP-ACP coupling kernel.
    Computes geometric torsion across the 4x12 helix lattice and enforces
    the meta-integrity operator Omega via residual-entropy breakout detection.
    """

    def __init__(self, master: "OmniQuantumDualHelixCoreMaster"):
        self.master = master
        # Tuned so that smooth physical states stay well below threshold
        self.omega_crit = 2.5
        self.lege_tolerance = 1.0e-6
        self.helix_nodes = np.zeros((4, 12), dtype=np.float64)
        self.global_root = hashlib.sha512(b"SPoT_INIT_ROOT_v1.1").digest()
        self.block_sequence = 0
        self.prev_torsion = 0.0
        self._baseline_set = False
        self.ledger: List[LedgerEntry] = []

    def _reshape_helix(self) -> np.ndarray:
        """Map state vector onto 4x12 helix lattice (pad / truncate if needed)."""
        dim = self.master.dimension
        target = 48
        psi = self.master.state_psi
        if dim < target:
            padded = np.zeros(target, dtype=np.float64)
            padded[:dim] = psi
            psi = padded
        elif dim > target:
            psi = psi[:target]
        return psi.reshape(4, 12)

    def calculate_geometric_torsion(self) -> float:
        """Discrete torsion measure between consecutive helix layers."""
        self.helix_nodes = self._reshape_helix()
        torsion_sum = 0.0
        for layer in range(3):
            shift_field = np.roll(self.helix_nodes[layer + 1], -1)
            torsion_sum += np.sum(np.abs(self.helix_nodes[layer] - shift_field))
        # Normalise by lattice size so scale is independent of absolute amplitude
        return float(torsion_sum / 48.0)

    def evaluate_gip_compliance(self, dt: float = 0.01) -> Dict[str, Any]:
        """
        Evaluate meta-integrity operator Omega.
        Returns status and updates SWAT / wallet only on true breakout.
        """
        current_torsion = self.calculate_geometric_torsion()
        # First sample after init/reset: establish baseline, never trigger
        if not self._baseline_set:
            self.prev_torsion = current_torsion
            self._baseline_set = True
            d_torsion_dt = 0.0
        else:
            d_torsion_dt = (current_torsion - self.prev_torsion) / max(dt, 1e-12)
            self.prev_torsion = current_torsion
        e_res = abs(d_torsion_dt) - self.omega_crit

        status = "VERIFIED_STABLE"
        residual = self.master.compute_residual()

        if e_res > 0.0:
            status = "TRIGGER_BREAKOUT"
            # Soft phase correction (absorbs energy instead of immediate hard cut)
            phase = np.exp(1j * current_torsion * np.pi * 0.15)
            corrected = self.master.state_psi.astype(np.complex128) * phase
            self.master.state_psi = np.real(corrected)

            residual = self.master.compute_residual()
            if residual > self.lege_tolerance * 50:  # only escalate on severe residual
                self.master.swat_status = "PHYSICALLY_DISCONNECTED"
                self.master.system_status = "LOCKDOWN_ABSORBING_STATE"
                self.master.wallet_lock = "ISOLATED_AND_LOCKED"
                status = "SWAT_HARDWARE_CUTOFF"

        self.block_sequence += 1
        block_id = f"BLOCK_#{self.block_sequence:04d}"

        # Append to forensic ledger (Merkle-style chain)
        payload = f"{block_id}|{current_torsion:.8f}|{e_res:.8f}|{status}|{residual:.8e}"
        new_root = hashlib.sha512(self.global_root + payload.encode()).digest()
        self.global_root = new_root
        entry = LedgerEntry(
            block=block_id,
            torsion=current_torsion,
            e_res=e_res,
            gip_status=status,
            residual=residual,
            timestamp=time.time(),
            root_hash=new_root.hex()[:32],
        )
        self.ledger.append(entry)

        return {
            "torsion": current_torsion,
            "e_res": e_res,
            "gip_status": status,
            "block": block_id,
            "ledger_root": entry.root_hash,
            "residual": residual,
        }


class OmniQuantumDualHelixCoreMaster:
    """
    Master engine of the OQ-DHC.
    Maintains the 48-node (or adaptive) state vector, residual, SWAT status
    and the Layer-8 coupling kernel.
    """

    def __init__(self, dimension: int = 48):
        if dimension < 4:
            raise ValueError("dimension must be >= 4")
        self.dimension = int(dimension)
        self.state_psi = np.zeros(self.dimension, dtype=np.float64)
        self.swat_status = "CONNECTED"
        self.system_status = "VERIFIED_STABLE"
        self.wallet_lock = "SECURE"
        self.coupling = OQDHC_Coupling_Kernel(self)
        self._cycle_count = 0

    def set_dimension(self, dimension: int) -> None:
        if dimension < 4:
            raise ValueError("dimension must be >= 4")
        old = self.state_psi
        self.dimension = int(dimension)
        self.state_psi = np.zeros(self.dimension, dtype=np.float64)
        n = min(len(old), self.dimension)
        self.state_psi[:n] = old[:n]
        # Dimension change invalidates torsion baseline; avoid false SWAT trip
        self.coupling._baseline_set = False
        self.coupling.prev_torsion = 0.0
        if self.swat_status != "PHYSICALLY_DISCONNECTED":
            self.swat_status = "CONNECTED"
            self.system_status = "VERIFIED_STABLE"
            self.wallet_lock = "SECURE"

    def compute_residual(self) -> float:
        """Mean absolute gradient – proxy for smoothness / residual energy."""
        if len(self.state_psi) < 2:
            return 0.0
        return float(np.mean(np.abs(np.gradient(self.state_psi))))

    def compute_symplectic_proxy(self) -> float:
        """
        Lightweight proxy for symplectic volume preservation.
        Returns a value that stays ≈ 1.0 under smooth evolution.
        """
        psi = self.state_psi
        if len(psi) < 4:
            return 1.0
        d = np.diff(psi)
        n = min(len(d[::2]), len(d[1::2]))
        vol = np.sum(d[::2][:n] * d[1::2][:n]) if n > 0 else 0.0
        scale = np.linalg.norm(psi) + 1e-12
        return float(1.0 + vol / (scale * scale * 10.0))

    def inject_state(self, values) -> None:
        """Load an external state vector (pads / truncates to current dimension)."""
        arr = np.asarray(values, dtype=np.float64).ravel()
        if arr.size > 0 and not np.all(np.isfinite(arr)):
            # Fail-closed: non-finite telemetry must not stay CONNECTED/STABLE
            self.state_psi = np.zeros(self.dimension, dtype=np.float64)
            self.swat_status = "PHYSICALLY_DISCONNECTED"
            self.system_status = "LOCKDOWN_ABSORBING_STATE"
            self.wallet_lock = "ISOLATED_AND_LOCKED"
            return
        self.state_psi = np.zeros(self.dimension, dtype=np.float64)
        n = min(len(arr), self.dimension)
        self.state_psi[:n] = arr[:n]

    def execute_evolution_cycle(
        self,
        physics_mode: str = "full_v8_governance",
        dt: float = 0.01,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Single hard 100-ms tact cycle.
        Under PHYSICALLY_DISCONNECTED the engine refuses further evolution.
        """
        if self.swat_status == "PHYSICALLY_DISCONNECTED":
            return {
                "system_status": self.system_status,
                "swat_status": self.swat_status,
                "wallet_lock": self.wallet_lock,
                "cycle": self._cycle_count,
                "note": "Engine locked – physical interlock active",
            }

        if not np.all(np.isfinite(self.state_psi)):
            self.swat_status = "PHYSICALLY_DISCONNECTED"
            self.system_status = "LOCKDOWN_ABSORBING_STATE"
            self.wallet_lock = "ISOLATED_AND_LOCKED"
            return {
                "system_status": self.system_status,
                "swat_status": self.swat_status,
                "wallet_lock": self.wallet_lock,
                "cycle": self._cycle_count,
                "current_residual": float("nan"),
                "note": "Non-finite state – physical interlock active",
            }

        # Simple discrete Laplace diffusion (smooth evolution)
        lap = (
            np.roll(self.state_psi, -1)
            - 2.0 * self.state_psi
            + np.roll(self.state_psi, 1)
        )
        self.state_psi = self.state_psi + 0.08 * lap

        gip_data: Optional[Dict[str, Any]] = None
        if physics_mode in ("full_v8_governance", "full_v8"):
            gip_data = self.coupling.evaluate_gip_compliance(dt=dt)

        self._cycle_count += 1
        residual = self.compute_residual()
        symp = self.compute_symplectic_proxy()

        return {
            "current_residual": residual,
            "symplectic_proxy": symp,
            "system_status": self.system_status,
            "swat_status": self.swat_status,
            "wallet_lock": self.wallet_lock,
            "gip_governance": gip_data,
            "cycle": self._cycle_count,
            "dimension": self.dimension,
        }

    def reset(self) -> None:
        """Full soft reset (does not clear forensic ledger)."""
        self.state_psi.fill(0.0)
        self.swat_status = "CONNECTED"
        self.system_status = "VERIFIED_STABLE"
        self.wallet_lock = "SECURE"
        self.coupling.prev_torsion = 0.0
        self.coupling._baseline_set = False
        self._cycle_count = 0

    def get_ledger_summary(self, last_n: int = 5) -> List[Dict[str, Any]]:
        entries = self.coupling.ledger[-last_n:]
        return [
            {
                "block": e.block,
                "torsion": e.torsion,
                "e_res": e.e_res,
                "status": e.gip_status,
                "residual": e.residual,
                "root": e.root_hash,
            }
            for e in entries
        ]
