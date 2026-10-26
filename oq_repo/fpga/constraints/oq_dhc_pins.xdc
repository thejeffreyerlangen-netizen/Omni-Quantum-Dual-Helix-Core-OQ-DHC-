# OQ-DHC FPGA Emulation Bridge – Pin Constraints (example Artix-7 csg324)

## System
set_property PACKAGE_PIN E3 [get_ports clk_100m]
set_property IOSTANDARD LVCMOS33 [get_ports clk_100m]
create_clock -period 10.000 -name clk_100m [get_ports clk_100m]
set_property PACKAGE_PIN C2 [get_ports rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports rst_n]

## SWAT interlock → TX-9942 on Dev Board
set_property PACKAGE_PIN D4 [get_ports swat_relais_out_p]
set_property PACKAGE_PIN D3 [get_ports swat_relais_out_n]
set_property PACKAGE_PIN F4 [get_ports swat_sense]
set_property PACKAGE_PIN F3 [get_ports swat_force_open]
set_property IOSTANDARD LVCMOS33 [get_ports {swat_relais_out_p swat_relais_out_n swat_sense swat_force_open}]

## 12-phase clocks (subset)
set_property PACKAGE_PIN G1 [get_ports {clk_phase[0]}]
set_property PACKAGE_PIN G2 [get_ports {clk_phase[1]}]
set_property PACKAGE_PIN H1 [get_ports {clk_phase[2]}]
set_property PACKAGE_PIN H2 [get_ports {clk_phase[3]}]
set_property PACKAGE_PIN J1 [get_ports {clk_phase[4]}]
set_property PACKAGE_PIN J2 [get_ports {clk_phase[5]}]
set_property PACKAGE_PIN K1 [get_ports {clk_phase[6]}]
set_property PACKAGE_PIN K2 [get_ports {clk_phase[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {clk_phase[*]}]

## Oscillator proxies
set_property PACKAGE_PIN B1 [get_ports osc_carrier_p]
set_property PACKAGE_PIN B2 [get_ports osc_carrier_n]
set_property PACKAGE_PIN A1 [get_ports osc_mod_p]
set_property PACKAGE_PIN A2 [get_ports osc_mod_n]
set_property IOSTANDARD LVCMOS33 [get_ports {osc_carrier_p osc_carrier_n osc_mod_p osc_mod_n}]

## Status → LEDs
set_property PACKAGE_PIN G6 [get_ports {swat_status_enc[0]}]
set_property PACKAGE_PIN G5 [get_ports {swat_status_enc[1]}]
set_property PACKAGE_PIN G4 [get_ports {system_status_enc[0]}]
set_property PACKAGE_PIN G3 [get_ports {system_status_enc[1]}]
set_property PACKAGE_PIN F6 [get_ports {wallet_lock_enc[0]}]
set_property PACKAGE_PIN F5 [get_ports {wallet_lock_enc[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {swat_status_enc[*] system_status_enc[*] wallet_lock_enc[*]}]
set_false_path -to [get_ports {swat_status_enc[*]}]
set_false_path -to [get_ports {system_status_enc[*]}]
set_false_path -to [get_ports {wallet_lock_enc[*]}]
