#!/usr/bin/env bash
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

status=0

run_step() {
  local label="$1"
  shift
  echo
  echo "=================================================="
  echo "==> $label"
  echo "=================================================="

  if "$@"; then
    echo "PASS: $label"
    echo
    return 0
  else
    local rc=$?
    echo "FAIL: $label (exit $rc)"
    echo
    return "$rc"
  fi
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not installed."
  exit 127
fi

if ! run_step "Python Kernel Testbench" python3 tests/testbench.py; then
  status=1
fi

if ! run_step "C SDK tests" bash -lc 'cd sdk && make clean >/dev/null 2>&1 || true && make test'; then
  status=1
fi

if ! run_step "KiCad BGA footprint generation" python3 kicad/scripts/gen_bga144_footprint.py; then
  status=1
fi

if [ -f "fpga/litex/target_oq_dhc.py" ]; then
  if python3 - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec("litex") else 1)
PY
  then
    if ! run_step "LiteX FPGA target build" bash -lc 'cd fpga/litex && python3 target_oq_dhc.py --build'; then
      status=1
    fi
  else
    echo
    echo "=================================================="
    echo "==> LiteX FPGA build skipped"
    echo "=================================================="
    echo "LiteX is not installed in the current environment."
    echo "Install LiteX and rerun: cd fpga/litex && python3 target_oq_dhc.py --build"
    echo
  fi
else
  echo
  echo "=================================================="
  echo "==> LiteX target not found"
  echo "=================================================="
  echo "fpga/litex/target_oq_dhc.py does not exist in this checkout."
  echo
fi

echo
if [ "$status" -eq 0 ]; then
  echo "ALL CHECKS COMPLETED WITHOUT FAILURES"
else
  echo "ONE OR MORE CHECKS FAILED"
fi

exit "$status"
