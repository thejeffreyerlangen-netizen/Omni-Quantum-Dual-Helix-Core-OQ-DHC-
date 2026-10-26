module gtr_display_gating (
    input  wire        clk_core,
    input  wire        rst_n,
    input  wire [11:0] kpo_phase_bus,
    input  wire [63:0] meta_integrity_omega,
    input  wire        swat_interlock_tripped,
    input  wire [63:0] layer3_geom_tensor,
    input  wire [63:0] layer5_photon_wave,
    output wire [5:0]  gtr_display_out_p,
    output wire [5:0]  gtr_display_out_n
);
    reg [63:0] lightfield_synthesis;
    wire       raw_hardware_clear;

    assign raw_hardware_clear = (meta_integrity_omega == 64'h0000_0000_0000_0000 || swat_interlock_tripped == 1'b1) ? 1'b0 : 1'b1;

    always @(posedge clk_core or negedge rst_n) begin
        if (!rst_n) begin
            lightfield_synthesis <= 64'h0000_0000_0000_0000;
        end else begin
            if (raw_hardware_clear) begin
                lightfield_synthesis <= (layer3_geom_tensor ^ layer5_photon_wave) + kpo_phase_bus;
            end else begin
                lightfield_synthesis <= 64'h0000_0000_0000_0000;
            end
        end
    end

    assign gtr_display_out_p = (raw_hardware_clear) ? lightfield_synthesis[5:0] : 6'b000000;
    assign gtr_display_out_n = (raw_hardware_clear) ? ~lightfield_synthesis[5:0] : 6'b000000;
endmodule
