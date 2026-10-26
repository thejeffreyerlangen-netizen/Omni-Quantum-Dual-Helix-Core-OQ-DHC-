// System top: digital core + sensor stream + GTR display gating hooks
module oq_dhc_system_top (
    input  logic        clk,
    input  logic        rst_n,
    // Host CSR
    input  logic        host_valid,
    input  logic [7:0]  host_addr,
    input  logic [31:0] host_wdata,
    output logic        host_ready,
    output logic [31:0] host_rdata,
    // Sensor stream
    input  logic        sensor_valid,
    input  logic [15:0] sensor_sample,
    output logic        sensor_ready,
    // Status / SWAT
    output logic [1:0]  swat_status_enc,
    output logic [1:0]  system_status_enc,
    output logic [1:0]  wallet_lock_enc,
    output logic        swat_relais_out_p,
    output logic        swat_relais_out_n,
    output logic        swat_force_open,
    output logic [11:0] clk_phase,
    // GTR display (blanked on SWAT)
    output logic [5:0]  gtr_display_out_p,
    output logic [5:0]  gtr_display_out_n
);
    import oq_dhc_pkg::*;

    logic swat_trip_internal;
    logic stream_wr_en;
    logic [5:0] stream_idx;
    logic [15:0] stream_data;

    // Host path core
    oq_dhc_digital_core u_core (
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
        .swat_interlock_tripped(swat_trip_internal)
    );

    oq_dhc_sensor_stream u_stream (
        .clk(clk),
        .rst_n(rst_n),
        .swat_lock(swat_trip_internal),
        .sensor_valid(sensor_valid),
        .sensor_sample(sensor_sample),
        .sensor_ready(sensor_ready),
        .psi_wr_en(stream_wr_en),
        .psi_wr_idx(stream_idx),
        .psi_wr_data(stream_data)
    );

    // Note: stream PSI writes are exported for integration; full dual-port
    // mux into psi_mem can be wired in next P&R-oriented revision.
    wire unused = stream_wr_en ^ stream_idx[0] ^ stream_data[0];

    gtr_display_gating u_gtr (
        .clk_core(clk),
        .rst_n(rst_n),
        .kpo_phase_bus(clk_phase),
        .meta_integrity_omega(swat_trip_internal ? 64'd0 : 64'hFFFF_FFFF_FFFF_FFFF),
        .swat_interlock_tripped(swat_trip_internal),
        .layer3_geom_tensor(64'hA5A5_A5A5_A5A5_A5A5),
        .layer5_photon_wave(64'h5A5A_5A5A_5A5A_5A5A),
        .gtr_display_out_p(gtr_display_out_p),
        .gtr_display_out_n(gtr_display_out_n)
    );
endmodule
