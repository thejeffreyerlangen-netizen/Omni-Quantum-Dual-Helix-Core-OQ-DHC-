#!/usr/bin/env python3
"""Eigene Härte-/Grenzfälle für OQ-DHC — inkl. NaN/Inf, Dim 1–3, CMOS-Metadaten."""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "oq_repo")))

from src.core_engine import OmniQuantumDualHelixCoreMaster
from src.cmos_fusion import CMOSFusionEngine
from src.facade import OQDHCFacade

P = F = 0


def chk(name: str, cond: bool, detail: str = "") -> None:
    global P, F
    if cond:
        P += 1
        print(f"  [PASS] {name}" + (f" — {detail}" if detail else ""))
    else:
        F += 1
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    print("=" * 72)
    print(" HARD / EDGE SUITE v2")
    print("=" * 72)

    # E1 Dimension: 1–3 must raise; >=4 ok
    print("\n--- E1 Dimension ---")
    for d in (1, 2, 3):
        try:
            OmniQuantumDualHelixCoreMaster(dimension=d)
            chk(f"dim={d}_rejected", False, "expected ValueError")
        except ValueError as e:
            chk(f"dim={d}_rejected", "dimension must be >= 4" in str(e), str(e))
    for d in (4, 7, 48, 64, 128, 256):
        c = OmniQuantumDualHelixCoreMaster(dimension=d)
        c.state_psi = np.sin(np.linspace(0, 2 * np.pi, d))
        r = c.execute_evolution_cycle(dt=0.01)
        chk(f"dim={d}", math.isfinite(r["current_residual"]) and r["swat_status"] == "CONNECTED",
            f"residual={r['current_residual']:.4e}")

    # E2 fields
    print("\n--- E2 Field shapes ---")
    for name, vec in {
        "zeros": np.zeros(48),
        "ones": np.ones(48),
        "huge": np.full(48, 1e6),
        "tiny": np.full(48, 1e-15),
        "negative": -np.sin(np.linspace(0, 4 * np.pi, 48)),
        "random": np.random.default_rng(0).normal(0, 1, 48),
        "impulse": (np.eye(1, 48, 0).ravel() * 10.0),
    }.items():
        c = OmniQuantumDualHelixCoreMaster(dimension=48)
        c.inject_state(vec)
        r = c.execute_evolution_cycle(dt=0.01)
        chk(f"field_{name}", math.isfinite(r["current_residual"]), f"residual={r['current_residual']:.4e}")

    # E3 NaN/Inf → fail-closed
    print("\n--- E3 Non-finite ---")
    for name, val in (("nan", float("nan")), ("inf", float("inf")), ("neginf", float("-inf"))):
        c = OmniQuantumDualHelixCoreMaster(dimension=48)
        v = np.sin(np.linspace(0, 2 * np.pi, 48))
        v[10] = val
        c.inject_state(v)
        r = c.execute_evolution_cycle(dt=0.01)
        chk(f"{name}_swat_disconnected", r["swat_status"] == "PHYSICALLY_DISCONNECTED", r["swat_status"])
        chk(f"{name}_lockdown", r["system_status"] == "LOCKDOWN_ABSORBING_STATE", r["system_status"])
        chk(f"{name}_wallet_locked", r["wallet_lock"] == "ISOLATED_AND_LOCKED", r["wallet_lock"])

    # E4 long horizon
    print("\n--- E4 Long horizon ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=48)
    c.state_psi = np.sin(np.linspace(0, 4 * np.pi, 48))
    res_list, sym_list = [], []
    for _ in range(200):
        r = c.execute_evolution_cycle(dt=0.01)
        res_list.append(r["current_residual"])
        sym_list.append(c.compute_symplectic_proxy())
    chk("200_finite", all(math.isfinite(x) for x in res_list), f"max={max(res_list):.4f}")
    chk("200_swat", r["swat_status"] == "CONNECTED", r["swat_status"])
    chk("200_symp", all(0.1 < s < 10 for s in sym_list), f"{min(sym_list):.4f}..{max(sym_list):.4f}")
    chk("200_ledger", c.coupling.block_sequence >= 200, str(c.coupling.block_sequence))

    # E5 dt
    print("\n--- E5 dt ---")
    for dt in (1e-12, 1e-6, 0.01, 0.1, 1.0, 10.0):
        c = OmniQuantumDualHelixCoreMaster(dimension=32)
        c.state_psi = np.sin(np.linspace(0, 2 * np.pi, 32))
        r = c.execute_evolution_cycle(dt=dt)
        chk(f"dt={dt}", math.isfinite(r["current_residual"]), f"{r['current_residual']:.4e}")

    # E6/E7 stress + reset
    print("\n--- E6/E7 Stress & reset ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=48)
    c.inject_state(np.full(48, 1e3))
    for _ in range(5):
        r = c.execute_evolution_cycle(dt=0.05)
    chk("stress_status_defined", "swat_status" in r, r.get("swat_status"))
    c.reset()
    c.state_psi = np.sin(np.linspace(0, 2 * np.pi, 48))
    r = c.execute_evolution_cycle(dt=0.01)
    chk("reset_connected", r["swat_status"] == "CONNECTED", r["swat_status"])
    chk("reset_secure", r["wallet_lock"] == "SECURE", r.get("wallet_lock"))

    # E8 determinism
    print("\n--- E8 Determinism ---")
    def run_once():
        c = OmniQuantumDualHelixCoreMaster(dimension=48)
        c.state_psi = np.sin(np.linspace(0, 4 * np.pi, 48))
        return [c.execute_evolution_cycle(dt=0.01)["current_residual"] for _ in range(10)]
    a, b = run_once(), run_once()
    chk("deterministic", a == b, f"max|Δ|={max(abs(x-y) for x,y in zip(a,b)):.3e}")

    # E9 resize 24→96 must stay CONNECTED (baseline reset)
    print("\n--- E9 set_dimension 24→96 ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=24)
    c.state_psi = np.sin(np.linspace(0, 2 * np.pi, 24))
    c.execute_evolution_cycle(dt=0.01)
    c.set_dimension(96)
    c.state_psi = np.sin(np.linspace(0, 2 * np.pi, 96))
    r = c.execute_evolution_cycle(dt=0.01)
    chk("resize_swat_connected", r["swat_status"] == "CONNECTED", r["swat_status"])
    chk("resize_residual_finite", math.isfinite(r["current_residual"]), f"{r['current_residual']:.4e}")
    chk("resize_not_lockdown", r["system_status"] == "VERIFIED_STABLE", r["system_status"])

    # E10 CMOS metadata
    print("\n--- E10 CMOS metadata ---")
    eng = CMOSFusionEngine()
    required = {"sensor", "pixel_count", "sample_count", "max_voltage", "field_determinant",
                "swat_status", "pins_p", "pins_n", "status"}
    for sensor in eng.list_sensors():
        fr = eng.execute_fusion(sensor, seed=42)
        d = fr.to_dict()
        missing = required - set(d.keys())
        chk(f"{sensor}_keys", not missing, f"missing={missing}")
        chk(f"{sensor}_det", abs(float(d["field_determinant"]) - 1.0) < 1e-9, f"det={d['field_determinant']}")
        chk(f"{sensor}_pixels", int(d["pixel_count"]) > 0, str(d["pixel_count"]))
        chk(f"{sensor}_swat", d["swat_status"] in ("CONNECTED", "PHYSICALLY_DISCONNECTED"), d["swat_status"])

    # E11 Facade
    print("\n--- E11 Facade ---")
    f = OQDHCFacade(dimension=48)
    f.load_state(np.sin(np.linspace(0, 2 * np.pi, 48)))
    out = f.step(n=5, dt=0.01)
    chk("facade_step", isinstance(out, dict), str(type(out)))
    f.reset()
    chk("facade_reset", True)

    # E12 Ledger
    print("\n--- E12 Ledger ---")
    c = OmniQuantumDualHelixCoreMaster(dimension=32)
    c.state_psi = np.sin(np.linspace(0, 2 * np.pi, 32))
    for _ in range(15):
        c.execute_evolution_cycle(dt=0.01)
    summary = c.get_ledger_summary(last_n=15)
    roots = [e.get("root_hash") for e in summary if e.get("root_hash")]
    chk("ledger_n", len(summary) > 0, str(len(summary)))
    chk("ledger_unique", len(roots) == len(set(roots)), f"{len(set(roots))}/{len(roots)}")

    print("\n" + "=" * 72)
    print(f" RESULT: {P} passed, {F} failed")
    print("=" * 72)
    return 0 if F == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
