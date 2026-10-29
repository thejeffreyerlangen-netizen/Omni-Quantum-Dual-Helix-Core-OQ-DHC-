# OQ-DHC Clean Push Package

Verified sources only (session fixes applied).

## Included fixes
- set_dimension: GIP baseline reset
- inject_state / evolution: non-finite fail-closed
- tests: hard_edge_suite, test_2d3d_cmos_meta

## Run
```bash
python3 tests/testbench.py
python3 tests/hard_edge_suite.py
python3 tests/test_2d3d_cmos_meta.py
cd oq_repo && python3 tests/test_e2e.py && python3 tests/test_cmos_fusion.py && python3 tests/test_integration.py
cd ../sdk && make test
```
