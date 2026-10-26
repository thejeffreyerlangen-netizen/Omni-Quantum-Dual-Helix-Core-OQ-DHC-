// Combinational residual proxy: mean abs successive difference (scaled)
module oq_dhc_residual (
    input  logic [oq_dhc_pkg::PSI_W-1:0] psi [0:oq_dhc_pkg::PSI_DIM-1],
    output logic [15:0] residual
);
    import oq_dhc_pkg::*;

    logic [31:0] acc;
    logic signed [PSI_W:0] diff;
    integer i;

    always_comb begin
        acc = 32'd0;
        for (i = 1; i < PSI_DIM; i = i + 1) begin
            diff = $signed({1'b0, psi[i]}) - $signed({1'b0, psi[i-1]});
            if (diff < 0)
                diff = -diff;
            acc = acc + {{16{1'b0}}, diff[15:0]};
        end
        residual = acc[15:0] / PSI_DIM[15:0]; // simple average
    end
endmodule
