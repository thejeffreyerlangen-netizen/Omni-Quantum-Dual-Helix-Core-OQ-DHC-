// OQ-DHC digital core package – matches src/protocol.py HOST_REG
package oq_dhc_pkg;
    localparam int unsigned PSI_DIM       = 48;
    localparam int unsigned PSI_W         = 16;
    localparam int unsigned DATA_W        = 32;
    localparam int unsigned ADDR_W        = 8;

    localparam logic [7:0] ADDR_CONTROL   = 8'h00;
    localparam logic [7:0] ADDR_STATUS    = 8'h04;
    localparam logic [7:0] ADDR_RESIDUAL  = 8'h08;
    localparam logic [7:0] ADDR_CYCLE     = 8'h0C;
    localparam logic [7:0] ADDR_PSI_BASE  = 8'h10; // 0x10 .. 0x10+PSI_DIM-1

    localparam logic [1:0] SWAT_CONNECTED = 2'b00;
    localparam logic [1:0] SWAT_DISCONNECTED = 2'b01;
    localparam logic [1:0] SYS_STABLE     = 2'b00;
    localparam logic [1:0] SYS_LOCKDOWN   = 2'b01;
    localparam logic [1:0] WAL_SECURE     = 2'b00;
    localparam logic [1:0] WAL_ISOLATED   = 2'b01;

    localparam logic [15:0] RESIDUAL_TRIP = 16'd200; // threshold for SWAT escalate
endpackage
