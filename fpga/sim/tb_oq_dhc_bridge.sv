`timescale 1ns / 1ps

module tb_oq_dhc_bridge;
    logic clk = 0;
    logic rst_n = 0;
    always #5 clk = ~clk;

    logic        host_valid;
    logic [31:0] host_wdata;
    logic [7:0]  host_addr;
    logic        host_ready;
    logic [31:0] host_rdata;
    logic [1:0]  swat_status_enc, system_status_enc, wallet_lock_enc;
    logic        swat_relais_out_p, swat_relais_out_n, swat_force_open;
    logic        swat_sense = 1'b1;
    logic [11:0] clk_phase;
    logic        osc_carrier_p, osc_carrier_n, osc_mod_p, osc_mod_n;
    logic [12:0] io_ring_in = '0, io_ring_out;
    logic        io_ring_oe;

    oq_dhc_fpga_bridge dut (
        .clk_100m(clk),
        .rst_n(rst_n),
        .osc_carrier_p(osc_carrier_p),
        .osc_carrier_n(osc_carrier_n),
        .osc_mod_p(osc_mod_p),
        .osc_mod_n(osc_mod_n),
        .clk_phase(clk_phase),
        .swat_relais_out_p(swat_relais_out_p),
        .swat_relais_out_n(swat_relais_out_n),
        .swat_sense(swat_sense),
        .swat_force_open(swat_force_open),
        .io_ring_in(io_ring_in),
        .io_ring_out(io_ring_out),
        .io_ring_oe(io_ring_oe),
        .host_valid(host_valid),
        .host_wdata(host_wdata),
        .host_addr(host_addr),
        .host_ready(host_ready),
        .host_rdata(host_rdata),
        .swat_status_enc(swat_status_enc),
        .system_status_enc(system_status_enc),
        .wallet_lock_enc(wallet_lock_enc)
    );

    task automatic host_write(input [7:0] addr, input [31:0] data);
        host_addr  = addr;
        host_wdata = data;
        host_valid = 1;
        @(posedge clk);
        while (!host_ready) @(posedge clk);
        host_valid = 0;
        @(posedge clk);
    endtask

    initial begin
        host_valid = 0;
        host_wdata = 0;
        host_addr  = 0;
        rst_n = 0;
        repeat (10) @(posedge clk);
        rst_n = 1;
        repeat (5) @(posedge clk);

        // Load mild sine-like values
        for (int i = 0; i < 48; i++)
            host_write(8'h10 + i, $sin(2.0 * 3.1415926535 * i / 48.0) * 1000);

        // Execute a few cycles – should stay CONNECTED
        repeat (5) host_write(8'h00, 32'h1);
        $display("After smooth cycles: SWAT=%0d SYS=%0d WAL=%0d", swat_status_enc, system_status_enc, wallet_lock_enc);

        // Inject large disturbance
        for (int i = 0; i < 48; i++)
            host_write(8'h10 + i, 32'sd20000);
        host_write(8'h00, 32'h1);
        host_write(8'h00, 32'h1);
        $display("After attack: SWAT=%0d SYS=%0d WAL=%0d force_open=%0d",
                 swat_status_enc, system_status_enc, wallet_lock_enc, swat_force_open);

        // Reset
        host_write(8'h00, 32'h2);
        $display("After reset: SWAT=%0d", swat_status_enc);

        $display("TB finished");
        $finish;
    end
endmodule
