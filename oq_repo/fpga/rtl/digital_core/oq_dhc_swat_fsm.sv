// Synthesizable SWAT fail-closed FSM
module oq_dhc_swat_fsm (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       soft_reset,
    input  logic       trip,          // residual / integrity trip
    output logic [1:0] swat_enc,
    output logic [1:0] sys_enc,
    output logic [1:0] wal_enc,
    output logic       bus_enable     // 0 = PHYSICALLY_DISCONNECTED path
);
    import oq_dhc_pkg::*;

    typedef enum logic [1:0] {ST_RUN = 2'b00, ST_LOCK = 2'b01} state_t;
    state_t state, state_n;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= ST_RUN;
        else if (soft_reset)
            state <= ST_RUN;
        else
            state <= state_n;
    end

    always_comb begin
        state_n = state;
        unique case (state)
            ST_RUN:  if (trip) state_n = ST_LOCK;
            ST_LOCK: state_n = ST_LOCK; // fail-closed until soft_reset
            default: state_n = ST_RUN;
        endcase
    end

    always_comb begin
        if (state == ST_RUN) begin
            swat_enc   = SWAT_CONNECTED;
            sys_enc    = SYS_STABLE;
            wal_enc    = WAL_SECURE;
            bus_enable = 1'b1;
        end else begin
            swat_enc   = SWAT_DISCONNECTED;
            sys_enc    = SYS_LOCKDOWN;
            wal_enc    = WAL_ISOLATED;
            bus_enable = 1'b0;
        end
    end
endmodule
