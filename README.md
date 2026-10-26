# Omni Quantum Dual Helix Core (OQ-DHC) – Complete Project v1.1

[![OQ-DHC SLSA Secure Release Pipeline](https://github.com/thejeffreyerlangen-netizen/Omni-Quantum-Dual-Helix-Core-OQ-DHC-/actions/workflows/slsa-release.yml/badge.svg?branch=main)](https://github.com/thejeffreyerlangen-netizen/Omni-Quantum-Dual-Helix-Core-OQ-DHC-/actions/workflows/slsa-release.yml)

![Version](https://img.shields.io/badge/Kernel-v1.1.0%20Hardened-green?style=for-the-badge)
![SWAT](https://img.shields.io/badge/S.W.A.T.-Fail--Closed-red?style=for-the-badge)

Vollständiges Referenzprojekt: gehärteter Kernel, C-SDK, BGA-144-Pinout, Development Board,
KiCad (inkl. 12×12-Footprint-Generator), FPGA-Emulations-Brücke, Vivado- und LiteX-Vorlagen.

**Zusammenfassung (PDF):** [`docs/OQ_DHC_Complete_Project_Summary.pdf`](docs/OQ_DHC_Complete_Project_Summary.pdf)

## Quick Start

```bash
python tests/testbench.py
cd sdk && make test
python kicad/scripts/gen_bga144_footprint.py
cd fpga/litex && python target_oq_dhc.py --build
```

Hinweis: Der FPGA-Build erfordert je nach Setup eine gültige LiteX- und Toolchain-Installation.

## Projektstruktur

```text
oq_repo/
├── src/
│   └── core_engine.py                 # Python Kernel
├── tests/
│   └── testbench.py                   # Testbench / Verifikation
├── sdk/
│   ├── libdhqhk.c
│   ├── libdhqhk.h
│   ├── test_sdk.c
│   └── Makefile
├── docs/
│   ├── OQ_DHC_Complete_Project_Summary.pdf
│   ├── oq_dhc_bga144_pinout_specification.html
│   ├── bga144_pinout.csv
│   └── board/                        # Dev-Board Spec + Floorplan
├── kicad/
│   ├── scripts/
│   │   └── gen_bga144_footprint.py
│   └── oq_dhc_devboard/              # .kicad_pro / .kicad_sch / .kicad_pcb + Footprint
├── fpga/
│   ├── rtl/
│   │   └── oq_dhc_fpga_bridge.sv
│   ├── sim/
│   ├── vivado/                       # TCL create / sim / bitstream
│   └── litex/                        # Platform + CSR-Modul + Target
├── LICENSE
├── README.md
└── .github/
    └── workflows/
        └── slsa-release.yml
```

## Lizenz / Status

Forschungs- und Simulations-Referenz. Software-, EDA- und FPGA-Artefakte sind dokumentiert, spezifiziert und, soweit toolkettenunabhängig, validiert.

## Hinweise

- Die Inhalte dienen als Referenzarchitektur für Hardware-/Software-Koordination, FPGA-Bridge-Design und BGA-Entwurf.
- Einige Komponenten benötigen zusätzliche Toolchains (z. B. LiteX, Vivado, KiCad).
- Für produktive oder reproduzierbare Builds sollten Versions- und Toolchain-Constraints dokumentiert werden.
