# Repository layout and structure guide

## Canonical project layout

This repository is organized by subsystem rather than by a single monolithic application structure. The root directory remains the main integration point while domain-specific folders keep the codebase readable and maintainable.

```text
.
├── .github/                  # release and CI workflow definition
├── docs/                     # architecture docs, summary PDFs, pinout, board data
├── fpga/                     # FPGA bridge, simulation, Vivado, LiteX build assets
├── kicad/                    # board project, scripts, footprints
├── oq_repo/                  # compatibility/reference mirror
├── sdk/                      # C SDK and native tooling
├── src/                      # Python core engine and logic
├── tests/                    # validation and benchmark suites
├── LICENSE
├── README.md
├── run_all_scripts.sh
├── run_all_scripts.ps1
├── Audit Certificate - 5 Million Industrial Edge Cases.pdf
├── DOKUMENTATION_UND_GENESE.txt
└── generated/artifacts/...   # add future generated files here in a dedicated folder
```

## Design principles

- Keep each domain in its own top-level folder.
- Use the repository root for project entry points and top-level documentation.
- Reserve `oq_repo/` for compatibility-oriented or packaged snapshot content.
- Store generated or build artifacts in dedicated subfolders rather than mixing them into source directories.

## Recommended future additions

```text
assets/
  images/
  video/
  diagrams/
ci/
  scripts/
  checks/
config/
  defaults/
  presets/
logs/
  builds/
  tests/
```

This keeps the project maintainable as the scope grows beyond the current reference architecture.

