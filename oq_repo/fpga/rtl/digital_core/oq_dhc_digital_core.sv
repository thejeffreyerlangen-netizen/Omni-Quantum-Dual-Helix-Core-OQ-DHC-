// =============================================================================
// OQ-DHC Synthesizable Digital Core (MVP for ASIC/FPGA tapeout path)
// CSR map aligned with src/protocol.py and sdk/libdhqhk / LiteX driver
// =============================================================================
module oq_dhc_digital_core (
    input  logic        clk,
    input  logic        rst_n,
    // Host bus
    input  logic        host_valid,
    input  logic [7:0]  host_addr,
    input  logic [31:0] host_wdata,
    output logic        host_ready,
    output logic [31:0] host_rdata,
    // Status encode (LEDs / bridge)
    output logic [1:0]  swat_status_enc,
    output logic [1:0]  system_status_enc,
    output logic [1:0]  wallet_lock_enc,
    // SWAT physical
    output logic        swat_relais_out_p,
    output logic        swat_relais_out_n,
    output logic        swat_force_open,
    // Phase bus
    output logic [11:0] clk_phase,
    // Optional GTR gating inputs export
    output logic        swat_interlock_tripped
);
    import oq_dhc_pkg::*;

    logic        pulse_execute, pulse_reset;
    logic        psi_wr_en;
    logic [5:0]  psi_wr_idx;
    logic [15:0] psi_wr_data;
    logic [15:0] residual;
    logic [31:0] cycle_cnt;
    logic        bus_enable;
    logic [1:0]  swat_enc, sys_enc, wal_enc;
    logic [PSI_W-1:0] psi_q [0:PSI_DIM-1];
    logic        trip;

    oq_dhc_csr_bank u_csr (
        .clk(clk),
        .rst_n(rst_n),
        .host_valid(host_valid),
        .host_addr(host_addr),
        .host_wdata(host_wdata),
        .host_ready(host_ready),
        .host_rdata(host_rdata),
        .pulse_execute(pulse_execute),
        .pulse_reset(pulse_reset),
        .psi_wr_en(psi_wr_en),
        .psi_wr_idx(psi_wr_idx),
        .psi_wr_data(psi_wr_data),
        .swat_enc(swat_enc),
        .sys_enc(sys_enc),
        .wal_enc(wal_enc),
        .residual(residual),
        .cycle_cnt(cycle_cnt),
        .bus_enable(bus_enable)
    );

    oq_dhc_psi_mem u_psi (
        .clk(clk),
        .rst_n(rst_n),
        .clear(pulse_reset),
        .wr_en(psi_wr_en),
        .wr_idx(psi_wr_idx),
        .wr_data(psi_wr_data),
        .rd_idx(6'd0),
        .rd_data(),
        .psi_q(psi_q)
    );

    oq_dhc_residual u_res (
        .psi(psi_q),
        .residual(residual)
    );

    // Trip on execute if residual already high (simple integrity proxy)
    assign trip = pulse_execute && (residual > RESIDUAL_TRIP);

    oq_dhc_swat_fsm u_swat (
        .clk(clk),
        .rst_n(rst_n),
        .soft_reset(pulse_reset),
        .trip(trip),
        .swat_enc(swat_enc),
        .sys_enc(sys_enc),
        .wal_enc(wal_enc),
        .bus_enable(bus_enable)
    );

    oq_dhc_phase_fsm #(.PHASES(12)) u_phase (
        .clk(clk),
        .rst_n(rst_n),
        .enable(bus_enable),
        .phase_onehot(clk_phase)
    );

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            cycle_cnt <= 32'd0;
        else if (pulse_reset)
            cycle_cnt <= 32'd0;
        else if (pulse_execute && bus_enable)
            cycle_cnt <= cycle_cnt + 32'd1;
    end

    assign swat_status_enc   = swat_enc;
    assign system_status_enc = sys_enc;
    assign wallet_lock_enc   = wal_enc;
    assign swat_interlock_tripped = (swat_enc == SWAT_DISCONNECTED);

    always_comb begin
        if (bus_enable) begin
            swat_relais_out_p = 1'b1;
            swat_relais_out_n = 1'b0;
            swat_force_open   = 1'b0;
        end else begin
            swat_relais_out_p = 1'b0;
            swat_relais_out_n = 1'b0;
            swat_force_open   = 1'b1;
        end
    end
endmodule
