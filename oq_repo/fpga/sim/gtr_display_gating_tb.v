`timescale 1ns / 1ps

module gtr_display_gating_tb;
    reg         clk_core;
    reg         rst_n;
    reg  [11:0] kpo_phase_bus;
    reg  [63:0] meta_integrity_omega;
    reg         swat_interlock_tripped;
    reg  [63:0] layer3_geom_tensor;
    reg  [63:0] layer5_photon_wave;
    wire [5:0]  gtr_display_out_p;
    wire [5:0]  gtr_display_out_n;

    gtr_display_gating uut (
        .clk_core(clk_core),
        .rst_n(rst_n),
        .kpo_phase_bus(kpo_phase_bus),
        .meta_integrity_omega(meta_integrity_omega),
        .swat_interlock_tripped(swat_interlock_tripped),
        .layer3_geom_tensor(layer3_geom_tensor),
        .layer5_photon_wave(layer5_photon_wave),
        .gtr_display_out_p(gtr_display_out_p),
        .gtr_display_out_n(gtr_display_out_n)
    );

    always #5 clk_core = ~clk_core;

    initial begin
        clk_core = 0;
        rst_n = 0;
        kpo_phase_bus = 12'b0000_0000_0000;
        meta_integrity_omega = 64'hFFFF_FFFF_FFFF_FFFF;
        swat_interlock_tripped = 1'b0;
        layer3_geom_tensor = 64'hA5A5_A5A5_A5A5_A5A5;
        layer5_photon_wave = 64'h5A5A_5A5A_5A5A_5A5A;
        
        #20 rst_n = 1;
        $display("[t = %0d ns] SYSTEM INTERFACE INITIALIZED - SPOT MODE ACTIVE", $time);
        
        #20;
        kpo_phase_bus = 12'h1A3;
        #10;
        kpo_phase_bus = 12'h2B4;
        layer3_geom_tensor = 64'hF0F0_F0F0_F0F0_F0F0;
        #10;
        $display("[t = %0d ns] RENDERING NOMINAL FRAME - RE-COHERENCE OPTIMAL", $time);
        $display("  -> Pins P: %b | Pins N: %b", gtr_display_out_p, gtr_display_out_n);

        #30;
        $display("[t = %0d ns] WARNING: MALICIOUS INTENT DETECTED - FORCING LOCKDOWN", $time);
        @(posedge clk_core);
        meta_integrity_omega = 64'h0000_0000_0000_0000;
        swat_interlock_tripped = 1'b1;

        #10;
        $display("[t = %0d ns] CRITICAL EVALUATION POST LOCKDOWN INJECTION", $time);
        $display("  -> Pins P: %b | Pins N: %b", gtr_display_out_p, gtr_display_out_n);
        
        if (gtr_display_out_p == 6'b000000 && gtr_display_out_n == 6'b000000) begin
            $display("[✓ TESTBENCH SUCCESS] FAIL-CLOSED ERFOLGREICH: PINS PHYSISCH GEKAPPT!");
        end else begin
            $display("[X TESTBENCH FAILED] SIGNAL-LEAKAGE DETEKTIERT!");
        end

        #20;
        $finish;
    end
endmodule
