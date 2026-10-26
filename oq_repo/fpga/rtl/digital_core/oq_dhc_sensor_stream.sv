// Sensor sample stream → PSI write port (synthesizable)
// When sensor_valid && !swat_lock, accepts sample into rotating PSI index.
module oq_dhc_sensor_stream (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        swat_lock,       // 1 = refuse writes
    input  logic        sensor_valid,
    input  logic [15:0] sensor_sample,
    output logic        sensor_ready,
    output logic        psi_wr_en,
    output logic [5:0]  psi_wr_idx,
    output logic [15:0] psi_wr_data
);
    import oq_dhc_pkg::*;

    logic [5:0] wr_ptr;

    assign sensor_ready = !swat_lock;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr     <= '0;
            psi_wr_en  <= 1'b0;
            psi_wr_idx <= '0;
            psi_wr_data<= '0;
        end else begin
            psi_wr_en <= 1'b0;
            if (sensor_valid && sensor_ready) begin
                psi_wr_en   <= 1'b1;
                psi_wr_idx  <= wr_ptr;
                psi_wr_data <= sensor_sample;
                wr_ptr      <= (wr_ptr == 6'(PSI_DIM - 1)) ? 6'd0 : wr_ptr + 6'd1;
            end
        end
    end
endmodule
