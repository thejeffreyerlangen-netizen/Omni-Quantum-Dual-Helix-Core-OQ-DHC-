#!/usr/bin/env python3
"""
OQ-DHC Comprehensive Integrity & Hardware-Enforcement Testbench
Version 1.1.0 – covers normal operation, multi-cycle stability,
attack injection, recovery, dimension adaptation and ledger integrity.
"""

from __future__ import annotations

import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from src.core_engine import OmniQuantumDualHelixCoreMaster


def banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check(condition: bool, msg: str) -> bool:
    status = "PASS" if condition else "FAIL"
    symbol = "✓" if condition else "✗"
    print(f"  [{symbol}] {msg}  →  {status}")
    return condition


def run_all_tests() -> int:
    failures = 0

    # ------------------------------------------------------------------
    banner("TEST 1 – Regulärer Betrieb (Smooth Sinus, 48-Knoten)")
    core = OmniQuantumDualHelixCoreMaster(dimension=48)
    core.state_psi = np.sin(np.linspace(0, 4 * np.pi, 48))

    res = core.execute_evolution_cycle(dt=0.01)
    ok = True
    ok &= check(res["swat_status"] == "CONNECTED", "SWAT bleibt CONNECTED")
    ok &= check(res["wallet_lock"] == "SECURE", "Wallet bleibt SECURE")
    ok &= check(res["system_status"] == "VERIFIED_STABLE", "Systemstatus STABLE")
    ok &= check(res["gip_governance"]["gip_status"] == "VERIFIED_STABLE", "GIP VERIFIED_STABLE")
    ok &= check(res["current_residual"] < 1.0, f"Residual sinnvoll ({res['current_residual']:.4e})")
    if not ok:
        failures += 1
        print("  → Details:", res)

    # ------------------------------------------------------------------
    banner("TEST 2 – Multi-Cycle Stabilität (20 Takte)")
    residuals = []
    statuses = []
    for i in range(20):
        r = core.execute_evolution_cycle(dt=0.01)
        residuals.append(r["current_residual"])
        statuses.append(r["swat_status"])

    ok = True
    ok &= check(all(s == "CONNECTED" for s in statuses), "SWAT über 20 Zyklen CONNECTED")
    ok &= check(max(residuals) < 2.0, f"Max-Residual < 2.0 (ist {max(residuals):.4f})")
    ok &= check(core.coupling.block_sequence == 21, "Ledger-Blöcke korrekt inkrementiert")
    if not ok:
        failures += 1

    # ------------------------------------------------------------------
    banner("TEST 3 – Dimension-Adaptation (24 → 48)")
    core24 = OmniQuantumDualHelixCoreMaster(dimension=24)
    core24.inject_state(np.linspace(0.1, 1.1, 24))
    r24 = core24.execute_evolution_cycle()
    ok = check(r24["swat_status"] == "CONNECTED", "24-Knoten startet stabil")
    core24.set_dimension(48)
    r48 = core24.execute_evolution_cycle()
    ok &= check(r48["dimension"] == 48, "Dimension erfolgreich auf 48 gesetzt")
    ok &= check(r48["swat_status"] == "CONNECTED", "Nach Resize weiterhin CONNECTED")
    if not ok:
        failures += 1

    # ------------------------------------------------------------------
    banner("TEST 4 – Angriffs-Injektion (Voltage-Glitch / Trojaner)")
    attack_core = OmniQuantumDualHelixCoreMaster(dimension=48)
    attack_core.state_psi = np.sin(np.linspace(0, 2 * np.pi, 48)) * 0.3
    for _ in range(3):
        attack_core.execute_evolution_cycle()

    attack_core.state_psi += 250.0 * np.random.randn(48)
    res_attack = attack_core.execute_evolution_cycle(dt=0.005)

    if res_attack["swat_status"] != "PHYSICALLY_DISCONNECTED":
        res_attack = attack_core.execute_evolution_cycle(dt=0.005)

    ok = True
    ok &= check(
        res_attack["swat_status"] == "PHYSICALLY_DISCONNECTED",
        "SWAT → PHYSICALLY_DISCONNECTED nach starker Injektion",
    )
    ok &= check(
        res_attack["wallet_lock"] == "ISOLATED_AND_LOCKED",
        "Wallet → ISOLATED_AND_LOCKED",
    )
    ok &= check(
        res_attack["system_status"] == "LOCKDOWN_ABSORBING_STATE",
        "System → LOCKDOWN_ABSORBING_STATE",
    )
    if not ok:
        failures += 1
        print("  → Attack result:", res_attack)

    # ------------------------------------------------------------------
    banner("TEST 5 – Locked Engine verweigert weitere Zyklen")
    res_locked = attack_core.execute_evolution_cycle()
    ok = check(
        "locked" in res_locked.get("note", "").lower()
        or res_locked["swat_status"] == "PHYSICALLY_DISCONNECTED",
        "Engine verweigert Evolution im Lockdown",
    )
    if not ok:
        failures += 1

    # ------------------------------------------------------------------
    banner("TEST 6 – Soft-Reset stellt Betriebsbereitschaft wieder her")
    attack_core.reset()
    attack_core.state_psi = np.sin(np.linspace(0, 4 * np.pi, 48)) * 0.5
    res_reset = attack_core.execute_evolution_cycle()
    ok = True
    ok &= check(res_reset["swat_status"] == "CONNECTED", "Nach Reset: SWAT CONNECTED")
    ok &= check(res_reset["wallet_lock"] == "SECURE", "Nach Reset: Wallet SECURE")
    if not ok:
        failures += 1

    # ------------------------------------------------------------------
    banner("TEST 7 – Forensic Ledger (Merkle-Chain)")
    summary = core.get_ledger_summary(last_n=5)
    ok = check(len(summary) >= 1, "Ledger enthält Einträge")
    ok &= check(all("root" in e for e in summary), "Jeder Eintrag hat root_hash")
    roots = [e["root"] for e in summary]
    ok &= check(len(set(roots)) == len(roots), "Root-Hashes sind unique (Chain wächst)")
    if not ok:
        failures += 1
    else:
        print("  Letzte Ledger-Einträge:")
        for e in summary[-3:]:
            print(f"    {e['block']}  status={e['status']}  root={e['root'][:16]}…")

    # ------------------------------------------------------------------
    banner("TEST 8 – Symplektischer Proxy (Volumenerhaltung)")
    smooth = OmniQuantumDualHelixCoreMaster(dimension=32)
    smooth.inject_state(np.sin(np.linspace(0, 6 * np.pi, 32)))
    proxies = []
    for _ in range(15):
        r = smooth.execute_evolution_cycle()
        proxies.append(r["symplectic_proxy"])
    ok = check(
        all(0.5 < p < 1.5 for p in proxies),
        f"Symplectic-Proxy bleibt im Band 0.5–1.5 (min={min(proxies):.3f}, max={max(proxies):.3f})",
    )
    if not ok:
        failures += 1

    # ------------------------------------------------------------------
    banner("TEST SUMMARY")
    if failures == 0:
        print("  ★★★  ALL TESTS PASSED – Kernel ist stabil und SWAT-fähig  ★★★")
        return 0
    else:
        print(f"  ✗  {failures} Testgruppe(n) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(run_all_tests())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
