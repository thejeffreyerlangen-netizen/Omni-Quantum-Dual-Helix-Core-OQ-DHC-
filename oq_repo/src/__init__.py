"""Omni Quantum Dual Helix Core (OQ-DHC) – package root."""

from .core_engine import OmniQuantumDualHelixCoreMaster, OQDHC_Coupling_Kernel
from .facade import OQDHCFacade
from .protocol import CoreSnapshot, FrameResult, SwatStatus, SystemStatus, WalletLock, RenderStatus
from .field_telemetry import FieldParams, compute_field_params
from .cmos_fusion import CMOSFusionEngine, SENSOR_CATALOG

__version__ = "1.3.0"
__all__ = [
    "OmniQuantumDualHelixCoreMaster",
    "OQDHC_Coupling_Kernel",
    "OQDHCFacade",
    "CoreSnapshot",
    "FrameResult",
    "FieldParams",
    "compute_field_params",
    "CMOSFusionEngine",
    "SENSOR_CATALOG",
    "SwatStatus",
    "SystemStatus",
    "WalletLock",
    "RenderStatus",
]
