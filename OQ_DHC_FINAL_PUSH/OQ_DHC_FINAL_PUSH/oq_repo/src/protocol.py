"""
Shared protocol types for OQ-DHC software stack.
Single source of truth for status strings and frame/result contracts.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional
import time


class SwatStatus(str, Enum):
    CONNECTED = "CONNECTED"
    PHYSICALLY_DISCONNECTED = "PHYSICALLY_DISCONNECTED"


class SystemStatus(str, Enum):
    VERIFIED_STABLE = "VERIFIED_STABLE"
    LOCKDOWN_ABSORBING_STATE = "LOCKDOWN_ABSORBING_STATE"


class WalletLock(str, Enum):
    SECURE = "SECURE"
    ISOLATED_AND_LOCKED = "ISOLATED_AND_LOCKED"


class RenderStatus(str, Enum):
    SUCCESS = "SUCCESS"
    REJECTED_LOCKDOWN = "REJECTED_LOCKDOWN"
    REJECTED_INKONSISTENZ = "REJECTED_INKONSISTENZ"
    ERROR = "ERROR"


@dataclass
class CoreSnapshot:
    """Immutable view of master engine state for downstream modules."""
    dimension: int
    state_psi: list  # JSON-serializable
    swat_status: str
    system_status: str
    wallet_lock: str
    residual: float
    cycle: int
    base_frequency: float = 98.112

    def is_render_allowed(self) -> bool:
        return self.swat_status == SwatStatus.CONNECTED.value


@dataclass
class FrameResult:
    """Contract returned by any render / GTR path."""
    status: str
    frame_id: str
    width: int = 0
    height: int = 0
    render_time_ms: float = 0.0
    meta: Dict[str, Any] = field(default_factory=dict)
    # optional path to written artifact
    artifact_path: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Host register map (must match SV bridge + LiteX CSR driver)
HOST_REG = {
    "CONTROL": 0x00,
    "STATUS": 0x04,
    "RESIDUAL": 0x08,
    "CYCLE": 0x0C,
    "PSI_BASE": 0x10,
    # host-shadow field telemetry (software / future CSR expansion)
    "FIELD_DET": 0x40,
    "FIELD_ENERGY": 0x44,
    "FIELD_SEAL0": 0x48,
    "FIELD_SEAL1": 0x4C,
}

CONTROL_EXECUTE = 1 << 0
CONTROL_RESET = 1 << 1
