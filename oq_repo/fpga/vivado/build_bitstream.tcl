# Synth + impl + bitstream (batch)
set proj_dir [file normalize [file join [file dirname [info script]] "build"]]
open_project [file join $proj_dir "oq_dhc_fpga_bridge.xpr"]
launch_runs synth_1 -jobs 4
wait_on_run synth_1
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
puts "Bitstream run complete"
