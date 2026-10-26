`timescale 1ns/1ps

module tb_oq_dhc_digital_core;
    import oq_dhc_pkg::*;

    logic        clk = 0;
    logic        rst_n = 0;
    logic        host_valid;
    logic [7:0]  host_addr;
    logic [31:0] host_wdata;
    logic        host_ready;
    logic [31:0] host_rdata;
    logic [1:0]  swat_status_enc, system_status_enc, wallet_lock_enc;
    logic        swat_relais_out_p, swat_relais_out_n, swat_force_open;
    logic [11:0] clk_phase;
    logic        swat_interlock_tripped;

    always #5 clk = ~clk;

    oq_dhc_digital_core dut (
        .clk(clk),
        .rst_n(rst_n),
        .host_valid(host_valid),
        .host_addr(host_addr),
        .host_wdata(host_wdata),
        .host_ready(host_ready),
        .host_rdata(host_rdata),
        .swat_status_enc(swat_status_enc),
        .system_status_enc(system_status_enc),
        .wallet_lock_enc(wallet_lock_enc),
        .swat_relais_out_p(swat_relais_out_p),
        .swat_relais_out_n(swat_relais_out_n),
        .swat_force_open(swat_force_open),
        .clk_phase(clk_phase),
        .swat_interlock_tripped(swat_interlock_tripped)
    );

    task automatic host_write(input [7:0] addr, input [31:0] data);
        @(posedge clk);
        host_addr  = addr;
        host_wdata = data;
        host_valid = 1'b1;
        @(posedge clk);
        while (!host_ready) @(posedge clk);
        host_valid = 1'b0;
        @(posedge clk);
    endtask

    task automatic host_read(input [7:0] addr, output [31:0] data);
        @(posedge clk);
        host_addr  = addr;
        host_wdata = 32'd0;
        host_valid = 1'b1;
        @(posedge clk);
        while (!host_ready) @(posedge clk);
        data = host_rdata;
        host_valid = 1'b0;
        @(posedge clk);
    endtask

    integer i;
    logic [31:0] rd;
    integer errors;

    initial begin
        errors = 0;
        host_valid = 0;
        host_addr  = 0;
        host_wdata = 0;
        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;
        repeat (3) @(posedge clk);

        // Smooth PSI ramp – low residual
        for (i = 0; i < PSI_DIM; i = i + 1)
            host_write(ADDR_PSI_BASE + i[7:0], i[15:0]); // gentle ramp

        host_write(ADDR_CONTROL, 32'h1); // execute
        host_read(ADDR_STATUS, rd);
        if (rd[1:0] != SWAT_CONNECTED) begin
            $display("FAIL: expected CONNECTED after smooth exec, status=%0h", rd);
            errors = errors + 1;
        end else
            $display("PASS: CONNECTED after smooth execute");

        // High residual pattern
        for (i = 0; i < PSI_DIM; i = i + 1)
            host_write(ADDR_PSI_BASE + i[7:0], (i[0] ? 16'h7FFF : 16'h0000));

        host_write(ADDR_CONTROL, 32'h1);
        host_read(ADDR_STATUS, rd);
        if (rd[1:0] != SWAT_DISCONNECTED) begin
            $display("FAIL: expected DISCONNECTED after high residual, status=%0h", rd);
            errors = errors + 1;
        end else
            $display("PASS: DISCONNECTED after integrity trip");

        if (swat_force_open !== 1'b1) begin
            $display("FAIL: swat_force_open not asserted");
            errors = errors + 1;
        end else
            $display("PASS: swat_force_open asserted");

        // Soft reset
        host_write(ADDR_CONTROL, 32'h2);
        host_read(ADDR_STATUS, rd);
        if (rd[1:0] != SWAT_CONNECTED) begin
            $display("FAIL: expected CONNECTED after reset, status=%0h", rd);
            errors = errors + 1;
        end else
            $display("PASS: CONNECTED after soft reset");

        if (errors == 0)
            $display("ALL DIGITAL CORE TESTS PASSED");
        else
            $display("FAILED with %0d errors", errors);

        #20;
        $finish;
    end
endmodule
