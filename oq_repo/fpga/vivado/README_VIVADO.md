# Vivado Project Template – OQ-DHC FPGA Bridge

## Voraussetzungen
- Xilinx Vivado 2022.2+ (oder kompatibel)
- FPGA-Part anpassen in `create_project.tcl` (Default: `xc7a35tcsg324-1`)

## Schnellstart

```bash
cd fpga/vivado
vivado -mode batch -source create_project.tcl
# Optional:
vivado -mode batch -source run_sim.tcl
vivado -mode batch -source build_bitstream.tcl
```

GUI: `vivado build/oq_dhc_fpga_bridge.xpr`

## Dateien
| Datei | Zweck |
|-------|--------|
| `create_project.tcl` | Projekt anlegen, RTL/XDC/TB hinzufügen |
| `run_sim.tcl` | Behavioural Simulation |
| `build_bitstream.tcl` | Synth → Impl → Bitstream |
