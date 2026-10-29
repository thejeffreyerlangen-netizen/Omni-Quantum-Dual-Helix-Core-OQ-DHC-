#!/usr/bin/env python3
"""
Echter Stresstest statt leerer pass-Schleifen.

Führt N echte execute_evolution_cycle-Läufe aus und mischt Härtefälle ein:
  - periodisch set_dimension (24↔48↔96) mit Baseline-Reset
  - periodisch starke Impulse
  - periodisch NaN-Inject → Lockdown → reset
  - deterministische Sinus-Last dazwischen

Default N=800_000 (messbar). Optional --n 800000000 (sehr lange Laufzeit).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "oq_repo")))

from src.core_engine import OmniQuantumDualHelixCoreMaster


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=800_000, help="number of real evolution cycles")
    ap.add_argument("--report-every", type=int, default=50_000)
    args = ap.parse_args()
    n = args.n

    print("=" * 72)
    print(f" REAL STRESS — {n:,} evolution cycles + edge injections")
    print("=" * 72)

    c = OmniQuantumDualHelixCoreMaster(dimension=48)
    c.state_psi = np.sin(np.linspace(0, 4 * np.pi, 48))

    residuals = []
    max_residual = 0.0
    lockdowns = 0
    dims_switched = 0
    errors = 0
    t0 = time.perf_counter()

    dim_cycle = [48, 24, 96, 48]
    dim_i = 0
    status_path = os.environ.get("STRESS_STATUS", "/home/workdir/artifacts/stress_800m_status.txt")

    def report_progress(i):
        if not args.report_every or i <= 0 or i % args.report_every != 0:
            return
        elapsed = time.perf_counter() - t0
        rate = i / max(elapsed, 1e-12)
        pct = 100.0 * i / n
        eta = (n - i) / max(rate, 1e-12)
        line = (f"  … {i:,}/{n:,}  {pct:.4f}%  rate={rate:,.0f} cycles/s  "
                f"ETA={eta/3600:.2f}h  max_res={max_residual:.4f}  "
                f"lockdowns={lockdowns} dim_switches={dims_switched}")
        print(line, flush=True)
        with open(status_path, "w") as sf:
            sf.write(
                f"percent={pct:.6f}\ncycles={i}\ntotal={n}\nrate={rate:.2f}\n"
                f"eta_sec={eta:.1f}\nmax_residual={max_residual}\n"
                f"lockdowns={lockdowns}\ndim_switches={dims_switched}\n"
                f"elapsed_sec={elapsed:.1f}\n"
            )

    for i in range(n):
        # --- Härtefälle (echte Arbeit, kein pass) ---
        if i > 0 and i % 10000 == 0:
            # dimension switch
            dim_i = (dim_i + 1) % len(dim_cycle)
            new_d = dim_cycle[dim_i]
            try:
                c.set_dimension(new_d)
                c.state_psi = np.sin(np.linspace(0, 2 * np.pi, new_d))
                dims_switched += 1
            except Exception:
                errors += 1

        if i > 0 and i % 25000 == 0:
            # impulse load
            c.inject_state(np.random.default_rng(i).normal(0, 5.0, c.dimension))

        if i > 0 and i % 50000 == 0:
            # NaN path → must lockdown, then reset
            v = np.sin(np.linspace(0, 2 * np.pi, c.dimension))
            v[0] = float("nan")
            c.inject_state(v)
            r = c.execute_evolution_cycle(dt=0.01)
            if r.get("swat_status") == "PHYSICALLY_DISCONNECTED":
                lockdowns += 1
            c.reset()
            c.state_psi = np.sin(np.linspace(0, 2 * np.pi, c.dimension))
            report_progress(i)
            continue

        r = c.execute_evolution_cycle(dt=0.01)
        res = r.get("current_residual", float("nan"))
        if res is not None and math.isfinite(res):
            max_residual = max(max_residual, float(res))
            if i % 100 == 0:
                residuals.append(float(res))
        else:
            if r.get("swat_status") != "PHYSICALLY_DISCONNECTED":
                errors += 1

        report_progress(i)

    t1 = time.perf_counter()
    elapsed = t1 - t0
    rate = n / max(elapsed, 1e-12)

    # final health cycle after possible reset
    if c.swat_status != "CONNECTED":
        c.reset()
        c.state_psi = np.sin(np.linspace(0, 2 * np.pi, c.dimension))
    final = c.execute_evolution_cycle(dt=0.01)

    print("-" * 72)
    print(f"  cycles            : {n:,}")
    print(f"  wall_sec          : {elapsed:.4f}")
    print(f"  cycles_per_sec    : {rate:,.1f}")
    print(f"  max_residual      : {max_residual:.6f}")
    print(f"  lockdown_events   : {lockdowns}")
    print(f"  dimension_switches: {dims_switched}")
    print(f"  errors            : {errors}")
    print(f"  final_swat        : {final.get('swat_status')}")
    print(f"  final_residual    : {final.get('current_residual')}")
    print("=" * 72)

    ok = (
        errors == 0
        and final.get("swat_status") == "CONNECTED"
        and math.isfinite(float(final.get("current_residual", float("nan"))))
        and max_residual < 50.0
    )
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
