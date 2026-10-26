// Synthesizable PSI register file (48 x 16-bit)
module oq_dhc_psi_mem (
    input  logic                     clk,
    input  logic                     rst_n,
    input  logic                     clear,
    input  logic                     wr_en,
    input  logic [5:0]               wr_idx,  // 0..47
    input  logic [oq_dhc_pkg::PSI_W-1:0] wr_data,
    input  logic [5:0]               rd_idx,
    output logic [oq_dhc_pkg::PSI_W-1:0] rd_data,
    output logic [oq_dhc_pkg::PSI_W-1:0] psi_q [0:oq_dhc_pkg::PSI_DIM-1]
);
    import oq_dhc_pkg::*;

    logic [PSI_W-1:0] mem [0:PSI_DIM-1];

    integer i;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < PSI_DIM; i = i + 1)
                mem[i] <= '0;
        end else if (clear) begin
            for (i = 0; i < PSI_DIM; i = i + 1)
                mem[i] <= '0;
        end else if (wr_en && (wr_idx < PSI_DIM[5:0])) begin
            mem[wr_idx] <= wr_data;
        end
    end

    assign rd_data = (rd_idx < PSI_DIM[5:0]) ? mem[rd_idx] : '0;

    genvar g;
    generate
        for (g = 0; g < PSI_DIM; g = g + 1) begin : gen_psi
            assign psi_q[g] = mem[g];
        end
    endgenerate
endmodule
