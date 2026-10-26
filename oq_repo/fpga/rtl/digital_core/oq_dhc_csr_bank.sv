// CSR bank – addresses match protocol.py / libdhqhk / LiteX driver
module oq_dhc_csr_bank (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        host_valid,
    input  logic [7:0]  host_addr,
    input  logic [31:0] host_wdata,
    output logic        host_ready,
    output logic [31:0] host_rdata,
    output logic        pulse_execute,
    output logic        pulse_reset,
    output logic        psi_wr_en,
    output logic [5:0]  psi_wr_idx,
    output logic [15:0] psi_wr_data,
    input  logic [1:0]  swat_enc,
    input  logic [1:0]  sys_enc,
    input  logic [1:0]  wal_enc,
    input  logic [15:0] residual,
    input  logic [31:0] cycle_cnt,
    input  logic        bus_enable
);
    import oq_dhc_pkg::*;

    logic        exec_r, rst_r, psi_we_r;
    logic [5:0]  psi_idx_r;
    logic [15:0] psi_data_r;
    logic [31:0] rdata_r;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            host_ready <= 1'b0;
            rdata_r    <= '0;
            exec_r     <= 1'b0;
            rst_r      <= 1'b0;
            psi_we_r   <= 1'b0;
            psi_idx_r  <= '0;
            psi_data_r <= '0;
        end else begin
            host_ready <= 1'b0;
            exec_r     <= 1'b0;
            rst_r      <= 1'b0;
            psi_we_r   <= 1'b0;

            if (host_valid) begin
                host_ready <= 1'b1;
                unique case (host_addr)
                    ADDR_CONTROL: begin
                        if (host_wdata[0] && bus_enable)
                            exec_r <= 1'b1;
                        if (host_wdata[1])
                            rst_r <= 1'b1;
                        rdata_r <= 32'd0;
                    end
                    ADDR_STATUS:
                        rdata_r <= {26'b0, wal_enc, sys_enc, swat_enc};
                    ADDR_RESIDUAL:
                        rdata_r <= {16'b0, residual};
                    ADDR_CYCLE:
                        rdata_r <= cycle_cnt;
                    default: begin
                        if (host_addr >= ADDR_PSI_BASE &&
                            host_addr < (ADDR_PSI_BASE + 8'(PSI_DIM)) &&
                            bus_enable) begin
                            psi_idx_r  <= 6'(host_addr - ADDR_PSI_BASE);
                            psi_data_r <= host_wdata[15:0];
                            psi_we_r   <= 1'b1;
                        end
                        rdata_r <= 32'd0;
                    end
                endcase
            end
        end
    end

    assign host_rdata    = rdata_r;
    assign pulse_execute = exec_r;
    assign pulse_reset   = rst_r;
    assign psi_wr_en     = psi_we_r;
    assign psi_wr_idx    = psi_idx_r;
    assign psi_wr_data   = psi_data_r;
endmodule
