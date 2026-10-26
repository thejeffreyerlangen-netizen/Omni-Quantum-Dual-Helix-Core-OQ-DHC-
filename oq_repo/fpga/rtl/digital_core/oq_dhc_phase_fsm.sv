// 12-phase one-hot tact generator (synthesizable)
module oq_dhc_phase_fsm #(
    parameter int unsigned PHASES = 12
) (
    input  logic             clk,
    input  logic             rst_n,
    input  logic             enable,
    output logic [PHASES-1:0] phase_onehot
);
    logic [$clog2(PHASES)-1:0] idx;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            idx <= '0;
        else if (enable)
            idx <= (idx == PHASES[$clog2(PHASES)-1:0] - 1'b1) ? '0 : idx + 1'b1;
    end

    integer p;
    always_comb begin
        phase_onehot = '0;
        for (p = 0; p < PHASES; p = p + 1)
            if (idx == p[$clog2(PHASES)-1:0])
                phase_onehot[p] = 1'b1;
    end
endmodule
