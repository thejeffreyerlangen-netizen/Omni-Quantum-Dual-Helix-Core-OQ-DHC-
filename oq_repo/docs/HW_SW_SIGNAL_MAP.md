# Hardware ↔ Software Signal Map

Single architectural contract between Python/C models, FPGA bridge, and GTR display gating.

## Status encoding (2-bit, matches SV + LiteX CSR)

| Field  | 0                      | 1                            |
|--------|------------------------|------------------------------|
| SWAT   | CONNECTED              | PHYSICALLY_DISCONNECTED      |
| SYSTEM | VERIFIED_STABLE        | LOCKDOWN_ABSORBING_STATE     |
| WALLET | SECURE                 | ISOLATED_AND_LOCKED          |

## Host register map (byte addresses)

| Addr | Name     | Width | Side | Description                          |
|------|----------|-------|------|--------------------------------------|
| 0x00 | CONTROL  | 32    | W    | bit0 execute, bit1 reset             |
| 0x04 | STATUS   | 32    | R    | {wallet[1:0], system[1:0], swat[1:0]} packed low |
| 0x08 | RESIDUAL | 16/32 | R    | residual proxy                       |
| 0x0C | CYCLE    | 32    | R    | tact counter                         |
| 0x10+| PSI[]    | 16    | W    | state_psi[i]                         |

Sources of truth:
- `src/protocol.py` → `HOST_REG`
- `fpga/rtl/oq_dhc_fpga_bridge.sv`
- `fpga/litex/software/oq_dhc_driver.h`

## GTR display gating

| Signal                 | Direction | Function                                      |
|------------------------|-----------|-----------------------------------------------|
| meta_integrity_omega   | in        | zero → blank display                          |
| swat_interlock_tripped | in        | 1 → blank display                             |
| kpo_phase_bus[11:0]    | in        | phase contribution to lightfield word         |
| layer3_geom_tensor     | in        | geometry term                                 |
| layer5_photon_wave     | in        | photon term                                   |
| gtr_display_out_p/n    | out       | differential display bus (6b); 0 if locked    |

Module: `fpga/rtl/gtr_display_gating.v`

## Dependency direction (software)

```
facade.py  →  core_engine.py
           →  render_8l_core.py
           →  digital_twin_gtr.py
protocol.py  ←  (imported by facade, tests; no reverse deps)
```

No module below facade shall import facade.


## Sensor stream (digital core)

| Signal | Dir | Function |
|--------|-----|----------|
| sensor_valid | in | sample strobe |
| sensor_sample[15:0] | in | digitized sample |
| sensor_ready | out | 0 when SWAT locked |
| → psi_wr_* | internal | rotating write into PSI file |

Module: `oq_dhc_sensor_stream.sv` · Top: `oq_dhc_system_top.sv`
