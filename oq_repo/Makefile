# OQ-DHC top-level build / test
.PHONY: test test-python test-c test-integration test-cmos test-e2e test-rtl footprint demo help

help:
	@echo "Targets: test | test-python | test-c | test-integration | test-rtl | footprint"

test: test-python test-integration test-cmos test-e2e test-c

test-python:
	python3 tests/testbench.py

test-integration:
	python3 tests/test_integration.py

test-cmos:
	python3 tests/test_cmos_fusion.py

test-c:
	$(MAKE) -C sdk test

footprint:
	python3 kicad/scripts/gen_bga144_footprint.py

test-rtl:
	bash fpga/sim/digital_core/run_sim.sh

test-e2e:
	python3 tests/test_e2e.py

demo:
	python3 scripts/demo_pipeline.py
