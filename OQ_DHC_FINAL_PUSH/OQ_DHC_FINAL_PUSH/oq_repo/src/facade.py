"""
OQ-DHC Facade – single entry point for kernel + render + twin.
Keeps dependency direction: facade → core / render / twin (not reverse).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from .core_engine import OmniQuantumDualHelixCoreMaster
from .protocol import CoreSnapshot, FrameResult, RenderStatus, SwatStatus
from .field_telemetry import FieldParams, compute_field_params
from .render_8l_core import SuperEngineOmni8LGraphics
from .digital_twin_gtr import OQDHC_Digital_Twin_GTR


class OQDHCFacade:
    def __init__(self, dimension: int = 48, artifact_dir: Optional[Union[str, Path]] = None):
        self.core = OmniQuantumDualHelixCoreMaster(dimension=dimension)
        self.graphics = SuperEngineOmni8LGraphics(self.core)
        self.twin = OQDHC_Digital_Twin_GTR(self.core)
        self.artifact_dir = Path(artifact_dir) if artifact_dir else Path("artifacts_out")
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def snapshot(self) -> CoreSnapshot:
        c = self.core
        freq = getattr(getattr(c, "env", None), "base_frequency", 98.112)
        return CoreSnapshot(
            dimension=c.dimension,
            state_psi=c.state_psi.tolist(),
            swat_status=c.swat_status,
            system_status=c.system_status,
            wallet_lock=c.wallet_lock,
            residual=c.compute_residual(),
            cycle=getattr(c, "_cycle_count", 0),
            base_frequency=float(freq),
        )

    def load_state(self, values: List[float] | np.ndarray) -> None:
        self.core.inject_state(values)

    def step(self, n: int = 1, dt: float = 0.01) -> Dict[str, Any]:
        last = {}
        for _ in range(n):
            last = self.core.execute_evolution_cycle(dt=dt)
        return last

    def render_frame(
        self,
        layer_src: int = 4,
        layer_dst: int = 5,
        write_png: bool = True,
        resolution: int = 256,
    ) -> FrameResult:
        """Run 8L pipeline; optionally write PNG under artifact_dir."""
        # Prefer graphics engine path; normalize to FrameResult
        raw = self.graphics.execute_8l_render_pipeline(layer_src=layer_src, layer_dst=layer_dst)
        if raw.get("status", "").startswith("REJECTED") or "LOCKDOWN" in str(raw.get("status", "")):
            return FrameResult(
                status=RenderStatus.REJECTED_LOCKDOWN.value,
                frame_id=raw.get("frame_identifier", "none"),
                render_time_ms=float(raw.get("render_time_ms", 0.0)),
                meta=raw,
            )

        # Produce actual raster from kernel state (deterministic, no external deps beyond numpy)
        field = self._synthesize_lightfield(resolution)
        artifact = None
        if write_png:
            artifact = str(self._write_png(field, raw.get("frame_identifier", "frame")))

        return FrameResult(
            status=RenderStatus.SUCCESS.value,
            frame_id=raw.get("frame_identifier", "frame"),
            width=resolution,
            height=resolution,
            render_time_ms=float(raw.get("render_time_ms", 0.0)),
            meta={
                "layer_interaction": raw.get("layer_interaction"),
                "geometrical_curvature": raw.get("geometrical_curvature"),
                "core": self.snapshot().__dict__,
            },
            artifact_path=artifact,
        )

    def _synthesize_lightfield(self, n: int) -> np.ndarray:
        psi = self.core.state_psi
        x = np.linspace(-np.pi, np.pi, n)
        X, Y = np.meshgrid(x, x)
        # Project 1D state onto 2D field via Fourier-like phases
        field = np.zeros((n, n), dtype=np.float64)
        for k, a in enumerate(psi[: min(len(psi), 32)]):
            field += a * np.sin((k + 1) * X * 0.35) * np.cos((k + 1) * Y * 0.35)
        field = field - field.min()
        denom = field.max() + 1e-12
        return (field / denom * 255.0).astype(np.uint8)

    def _write_png(self, field_u8: np.ndarray, frame_id: str) -> Path:
        path = self.artifact_dir / f"{frame_id.replace('/', '_')}.png"
        try:
            from PIL import Image
            Image.fromarray(field_u8, mode="L").save(path)
        except ImportError:
            # Minimal PNG writer (grayscale 8-bit) without PIL
            self._write_png_minimal(field_u8, path)
        return path

    @staticmethod
    def _write_png_minimal(arr: np.ndarray, path: Path) -> None:
        import struct
        import zlib

        h, w = arr.shape
        raw = b"".join(b"\x00" + arr[i].tobytes() for i in range(h))

        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + tag + data + struct.pack(
                ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
            )

        ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(
            b"IDAT", zlib.compress(raw, 9)
        ) + chunk(b"IEND", b"")
        path.write_bytes(png)

    def run_twin(self, profile: str) -> Dict[str, Any]:
        return self.twin.run_game_simulation(profile)

    def get_field_params(self) -> FieldParams:
        """Export GTR/field telemetry for host / C-SDK parity."""
        snap = self.snapshot()
        torsion = 0.0
        try:
            torsion = float(self.core.coupling.calculate_geometric_torsion())
        except Exception:
            pass
        return compute_field_params(snap, torsion=torsion)

    def ingest_cmos(self, sensor_name: str, seed: int | None = None, steps: int = 1):
        """Sensor catalog → PSI inject → step → field params."""
        from .cmos_fusion import CMOSFusionEngine
        eng = CMOSFusionEngine()
        fusion = eng.execute_fusion(sensor_name, seed=seed)
        if fusion.swat_status != SwatStatus.CONNECTED.value:
            self.core.swat_status = fusion.swat_status
            return fusion, self.get_field_params()
        # rebuild nominal samples for inject
        import numpy as np
        spec_samples = np.linspace(1.2, 2.5, 1024)
        self.load_state(eng.voltages_to_psi(spec_samples, self.core.dimension))
        self.step(steps)
        return fusion, self.get_field_params()

    def reset(self) -> None:
        self.core.reset()
