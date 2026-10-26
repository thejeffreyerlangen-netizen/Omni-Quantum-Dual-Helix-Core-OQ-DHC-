#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DC="$ROOT/rtl/digital_core"
OUT="${1:-sim_digital_core.vvp}"
iverilog -g2012 -o "$OUT" \
  -I "$DC/include" \
  "$DC/include/oq_dhc_pkg.sv" \
  "$DC/oq_dhc_swat_fsm.sv" \
  "$DC/oq_dhc_psi_mem.sv" \
  "$DC/oq_dhc_residual.sv" \
  "$DC/oq_dhc_phase_fsm.sv" \
  "$DC/oq_dhc_csr_bank.sv" \
  "$DC/oq_dhc_digital_core.sv" \
  "$(dirname "$0")/tb_oq_dhc_digital_core.sv"
vvp "$OUT"
