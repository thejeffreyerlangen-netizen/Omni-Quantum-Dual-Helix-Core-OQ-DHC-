# LiteX Integration – OQ-DHC FPGA Bridge

## Dateien

| Datei | Rolle |
|-------|--------|
| `oq_dhc_platform.py` | Board-/Pin-Beschreibung (Artix-7 Beispiel) |
| `oq_dhc_bridge_module.py` | Migen/LiteX-Wrapper + CSR-Bank + Host-FSM |
| `target_oq_dhc.py` | SoC-Target (CPU + Bridge + LEDs) |

## CSR-Map (Bridge)

| CSR | Felder | Beschreibung |
|-----|--------|--------------|
| `control` | execute, reset | Pulse: Taktzyklus / Soft-Reset |
| `status` | swat, system, wallet | 2-Bit-Encodings |
| `residual` | 16-bit | Residual-Proxy |
| `cycle` | 32-bit | Cycle-Counter |
| `psi_addr` | 8-bit | Index 0..47 |
| `psi_data` | 16-bit | Signed Wert |
| `psi_we` | write pulse | Schreiben nach state_psi[addr] |

## Voraussetzungen

```bash
pip install litex litex-boards migen
# Vivado (oder anderer unterstützter Toolchain) im PATH
```

## Build

```bash
cd fpga/litex
python target_oq_dhc.py --build
# optional:
python target_oq_dhc.py --build --load
```

## Hinweise

- SV-Core wird über `platform.add_source(.../oq_dhc_fpga_bridge.sv)` eingebunden.
- Pins in `oq_dhc_platform.py` an das Carrier-Board anpassen.
- Ohne installiertes Vivado schlägt `--build` fehl; die Python-Struktur ist trotzdem vollständig und reviewbar.
