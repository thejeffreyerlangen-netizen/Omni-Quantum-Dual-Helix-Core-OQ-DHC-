# OQ-DHC FPGA Emulation Bridge

Synthetisierbare Soft-Bridge, die die Kernel-Semantik (Torsion, Baseline, SWAT Fail-Closed, Residual) auf FPGA-Pins abbildet.

## Struktur

```
fpga/
├── rtl/
│   └── oq_dhc_fpga_bridge.sv      # SystemVerilog Top
├── constraints/
│   └── oq_dhc_pins.xdc            # Beispiel-Pinout
├── sim/
│   └── tb_oq_dhc_bridge.sv        # Testbench
├── vivado/
│   ├── create_project.tcl         # Projektgenerator
│   ├── run_sim.tcl
│   ├── build_bitstream.tcl
│   └── README_VIVADO.md
├── litex/
│   ├── oq_dhc_platform.py
│   ├── oq_dhc_bridge_module.py
│   ├── target_oq_dhc.py
│   └── README_LITEX.md
└── README_FPGA.md
```

## Register-Map (Host)

| Addr | Name     | R/W | Beschreibung                          |
|------|----------|-----|---------------------------------------|
| 0x00 | CONTROL  | W   | bit0 = execute_cycle, bit1 = reset    |
| 0x04 | STATUS   | R   | {wallet, system, swat} packed         |
| 0x08 | RESIDUAL | R   | Aktuelles Residual                    |
| 0x0C | CYCLE    | R   | Cycle-Counter                         |
| 0x10+| PSI[]    | W   | state_psi[0..47] (16-bit signed)      |

## Vivado

```bash
cd fpga/vivado
vivado -mode batch -source create_project.tcl
```

## LiteX

```bash
cd fpga/litex
python target_oq_dhc.py --build
```

## Simulation (iverilog)

```bash
cd fpga
iverilog -g2012 -o sim.vvp rtl/oq_dhc_fpga_bridge.sv sim/tb_oq_dhc_bridge.sv
vvp sim.vvp
```
