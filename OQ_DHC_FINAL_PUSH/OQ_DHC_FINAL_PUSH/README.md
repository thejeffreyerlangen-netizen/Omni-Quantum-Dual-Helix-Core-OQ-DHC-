# Omni Quantum Dual Helix Core (OQ-DHC)

Omni Quantum Dual Helix Core (OQ-DHC) v8.6 is a multi-domain reference project that combines a hardened Python kernel, C SDK, FPGA bridge logic, board-level specifications, and KiCad/EDA artifacts in one repository.

## Project snapshot

- Core focus: 8-layer tensor compute, fail-closed hardware gating, and signal-leakage elimination
- Hardware/software scope: Python kernel, C SDK, SystemVerilog/Verilog RTL, KiCad board assets, FPGA build templates
- Status: reference implementation and validation project

## Technology profile

The repository is intentionally heterogeneous. The current composition is:

- Python: 44.3%
- SystemVerilog: 23.5%
- C: 16.3%
- HTML: 5.7%
- Tcl: 4.6%
- Verilog: 1.8%
- Other: 3.8%

This mix reflects the project’s hybrid nature: software simulation, hardware modeling, SDK integration, and hardware design documentation.

## Clean repository structure

The repository root is the canonical project entry point. The `oq_repo/` folder is treated as a compatibility or packaged mirror, so the navigation remains simple and predictable.

```text
.
├── .github/                          # CI/CD, provenance, release pipeline
├── docs/                             # project summaries, pinout docs, board assets
│   ├── board/
│   ├── bga144_pinout.csv
│   ├── OQ_DHC_Complete_Project_Summary.pdf
│   └── oq_dhc_bga144_pinout_specification.html
├── fpga/                             # RTL, simulation, Vivado, LiteX targets
│   ├── litex/
│   ├── rtl/
│   ├── sim/
│   └── vivado/
├── kicad/                            # KiCad board project and footprint generator
│   ├── oq_dhc_devboard/
│   └── scripts/
├── oq_repo/                          # compatibility/reference mirror of the project
│   ├── docs/
│   ├── fpga/
│   ├── kicad/
│   ├── sdk/
│   ├── src/
│   ├── tests/
│   ├── README.md
│   └── Makefile
├── sdk/                              # C SDK and native test targets
├── src/                              # Python source and kernel logic
├── tests/                            # validation and integration checks
├── LICENSE
├── README.md
├── run_all_scripts.sh
├── run_all_scripts.ps1
├── github_workflows_slsa_generator.yml
├── slsa-release.yml
├── slsagenerator.yml
├── OQ_DHC_Project_Overview.mp4
├── oq_dhc_graphics_core_animation.gif
├── oq_dhc_graphics_rendering_cad_4d_phasespace.png
├── proof_cert_oq_dhc_graphics_core.json
├── Audit Certificate - 5 Million Industrial Edge Cases.pdf
├── DOKUMENTATION_UND_GENESE.txt
└── OQ_DHC_Project_Overview.mp4
```

## Main project areas

### 1. Core Python implementation
- `src/`
- contains the kernel logic, compute engine, and orchestration code

### 2. Hardware and FPGA integration
- `fpga/`
- contains RTL, simulation, LiteX and Vivado support assets

### 3. Board and EDA design
- `kicad/`
- board schematic, PCB artifacts, and automated footprint generation

### 4. C SDK
- `sdk/`
- exposes the native interface and compatibility layer for hardware/software interaction

### 5. Validation and docs
- `tests/` and `docs/`
- validation, integration tests, pinout documentation, board specs, and summary material

## Quick start

```bash
python tests/testbench.py
cd sdk && make test
python kicad/scripts/gen_bga144_footprint.py
cd fpga/litex && python target_oq_dhc.py --build
```

Note: FPGA builds may require a valid LiteX toolchain and vendor-specific dependencies.

## Documentation and references

- `docs/OQ_DHC_Complete_Project_Summary.pdf`
- `docs/oq_dhc_bga144_pinout_specification.html`
- `docs/bga144_pinout.csv`
- `DOKUMENTATION_UND_GENESE.txt`

## Status and licensing

This project is a research and simulation reference with clearly documented hardware software interfaces and validation artifacts. The repository is published under the MIT license.

## Recommended usage

- Treat the repository root as the main working tree.
- Use `oq_repo/` as a packaged/reference mirror if you need a flattened project bundle.
- Keep future additions grouped by domain: `src/`, `sdk/`, `fpga/`, `kicad/`, `docs/`, `tests/`.

