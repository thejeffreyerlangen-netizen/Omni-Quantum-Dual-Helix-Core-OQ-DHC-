# =============================================================================
# OQ-DHC FPGA Emulation Bridge – Vivado Project Generator
# Usage (from Vivado TCL shell or batch):
#   vivado -mode batch -source create_project.tcl
# =============================================================================

set proj_name  "oq_dhc_fpga_bridge"
set proj_dir   [file normalize [file join [file dirname [info script]] "build"]]
set rtl_dir    [file normalize [file join [file dirname [info script]] ".." "rtl"]]
set constr_dir [file normalize [file join [file dirname [info script]] ".." "constraints"]]
set sim_dir    [file normalize [file join [file dirname [info script]] ".." "sim"]]

# Adjust part to your board (example: Artix-7 on Digilent Nexys/Arty)
set part "xc7a35tcsg324-1"

file mkdir $proj_dir
create_project $proj_name $proj_dir -part $part -force

set_property target_language Verilog [current_project]
set_property default_lib work [current_project]

# RTL
add_files -norecurse [list \
    [file join $rtl_dir "oq_dhc_fpga_bridge.sv"] \
]
set_property file_type SystemVerilog [get_files *.sv]
set_property top oq_dhc_fpga_bridge [current_fileset]

# Constraints
add_files -fileset constrs_1 -norecurse [list \
    [file join $constr_dir "oq_dhc_pins.xdc"] \
]

# Simulation
add_files -fileset sim_1 -norecurse [list \
    [file join $sim_dir "tb_oq_dhc_bridge.sv"] \
]
set_property file_type SystemVerilog [get_files -of_objects [get_filesets sim_1] *.sv]
set_property top tb_oq_dhc_bridge [get_filesets sim_1]

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

puts "OQ-DHC Vivado project created at: $proj_dir"
puts "Top: oq_dhc_fpga_bridge | Sim top: tb_oq_dhc_bridge | Part: $part"
