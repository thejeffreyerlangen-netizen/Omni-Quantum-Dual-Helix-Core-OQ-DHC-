# Omni Quantum Dual Helix Core (OQ-DHC) – Complete Project v1.1

![Version](https://img.shields.io/badge/Kernel-v1.1.0%20Hardened-green?style=for-the-badge)
![SWAT](https://img.shields.io/badge/S.W.A.T.-Fail--Closed-red?style=for-the-badge)

Vollständiges Referenzprojekt: gehärteter Kernel, C-SDK, BGA-144-Pinout, Development Board,
KiCad (inkl. 12×12-Footprint-Generator), FPGA-Emulations-Brücke, Vivado- und LiteX-Vorlagen.

**Projektstatus (Produktionpfad):** [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md)

**Zusammenfassung (PDF):** [`docs/OQ_DHC_Complete_Project_Summary.pdf`](docs/OQ_DHC_Complete_Project_Summary.pdf)


## Architektur (Software)

```
tests / CLI
    ↓
src/facade.py          ← einzige Einstiegs-API
    ↓
core_engine.py | render_8l_core.py | digital_twin_gtr.py
    ↓
src/protocol.py        ← Status-Enums, FrameResult, HOST_REG
```

- `make test` – Python unit + Integration + C-SDK
- `python tests/test_integration.py` – Facade, PNG-Artifact, SWAT-Gate
- Signal-Map HW/SW: `docs/HW_SW_SIGNAL_MAP.md`

## Quick Start

```bash
python tests/testbench.py          # Python Kernel – ALL TESTS PASSED
cd sdk && make test                # C SDK – ALL C TESTS PASSED
python kicad/scripts/gen_bga144_footprint.py
cd fpga/litex && python target_oq_dhc.py --build   # erfordert LiteX + Toolchain
```

## Struktur

```
oq_repo/
├── src/ core_engine.py              # Python Kernel
├── tests/ testbench.py              # 8-Gruppen-Testsuite
├── sdk/ libdhqhk.[ch] test_sdk.c    # C-SDK + Test + Makefile
├── docs/
│   ├── OQ_DHC_Complete_Project_Summary.pdf
│   ├── oq_dhc_bga144_pinout_specification.html
│   ├── bga144_pinout.csv
│   └── board/                       # Dev-Board Spec + Floorplan
├── kicad/
│   ├── scripts/gen_bga144_footprint.py
│   └── oq_dhc_devboard/             # .kicad_pro / .kicad_sch / .kicad_pcb + Footprint
└── fpga/
    ├── rtl/oq_dhc_fpga_bridge.sv
    ├── sim/ tb + constraints/
    ├── vivado/                      # TCL create / sim / bitstream
    └── litex/                       # Platform + CSR-Modul + Target
```

## Lizenz / Status

Forschungs- und Simulations-Referenz. Physische Fertigungsclaims sind spekulativ;
Software-, EDA- und FPGA-Artefakte sind spezifiziert und (soweit toolkettenunabhängig) getestet.


## Grafik- / GTR-Erweiterung (v8.3 / v8.4)

| Datei | Rolle |
|-------|--------|
| `src/render_8l_core.py` | 8-Layer Matrix Rendering Engine (Lichtfeld-Pipeline) |
| `src/digital_twin_gtr.py` | Digital-Twin Benchmark (Game-Profile → Feldkonvertierung) |
| `fpga/rtl/gtr_display_gating.v` | Hardware Display-Gating (SWAT-Fail-Closed auf Display-Pins) |
| `fpga/sim/gtr_display_gating_tb.v` | Verilog-Testbench (Nominal + Lockdown) |

Render wird bei `PHYSICALLY_DISCONNECTED` abgewiesen (`REJECTED_LOCKDOWN`).
