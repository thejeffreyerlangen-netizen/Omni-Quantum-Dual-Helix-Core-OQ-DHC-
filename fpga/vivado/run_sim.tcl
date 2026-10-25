# Run behavioural simulation (batch)
set proj_dir [file normalize [file join [file dirname [info script]] "build"]]
open_project [file join $proj_dir "oq_dhc_fpga_bridge.xpr"]
launch_simulation
run 50 us
puts "Simulation finished"
