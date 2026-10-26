#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "==> OQ-DHC LiteX build"
python3 target_oq_dhc.py --build "$@"
echo "==> Done. Driver: software/oq_dhc_driver.h"
