module reg (
    // Clock and Reset
    input  logic        i_clk,
    input  logic        i_rst_n,

    // Bus Interface
    input  logic        i_write,
    input  logic        i_read,
    input  logic [31:0] i_addr,
    input  logic [31:0] i_wdata,
    output logic [31:0] o_rdata,

    // Register Field Outputs (BCR - Bus Characteristics Register)
    output logic [1:0]  o_rw_device_role,
    output logic        o_rw_advanced_capabilities,
    output logic        o_rw_virtual_target_support,
    output logic        o_rw_offline_capable,
    output logic        o_rw_ibi_payload,
    output logic        o_rw_ibi_request_capable,
    output logic        o_rw_max_data_speed_limitation
);

//--------------------------------------------------------------------------
// Register Definitions
//--------------------------------------------------------------------------

// Bus Characteristics Register (BCR) @ 0x00 - Assuming R/W for all fields based on example
localparam BCR_ADDR       = 32'h0000;
localparam BCR_VALID_BIT  = 32'h00ff;  // [7:0] valid bits (31:8 reserved)
localparam BCR_DEFAULT    = 32'h0000;  // Assuming default 0 as per example

logic [31:0] r_bcr;
logic        w_bcr_wr;

//--------------------------------------------------------------------------
// Register Write Logic
//--------------------------------------------------------------------------

always_ff @(posedge i_clk or negedge i_rst_n) begin
    if (~i_rst_n) begin
        // Bus Characteristics Register (BCR)
        r_bcr <= BCR_DEFAULT;
    end else begin
        // Bus Characteristics Register (BCR)
        if (w_bcr_wr) begin
            r_bcr <= i_wdata & BCR_VALID_BIT;
        end
    end
end

//--------------------------------------------------------------------------
// Combinational Logic (Write Enables and Output Assignments)
//--------------------------------------------------------------------------

always_comb begin : REG_REGION
    // Default assignments
    w_bcr_wr = 1'b0;

    // Bus Characteristics Register (BCR)
    w_bcr_wr = i_write & (i_addr == BCR_ADDR);

    o_rw_device_role             = r_bcr[7:6];
    o_rw_advanced_capabilities   = r_bcr[5];
    o_rw_virtual_target_support  = r_bcr[4];
    o_rw_offline_capable         = r_bcr[3];
    o_rw_ibi_payload             = r_bcr[2]; // Note: Image description is about presence of payload, assuming bit indicates this.
    o_rw_ibi_request_capable     = r_bcr[1];
    o_rw_max_data_speed_limitation = r_bcr[0];

end

//--------------------------------------------------------------------------
// Register Read Logic
//--------------------------------------------------------------------------

always_ff @(posedge i_clk or negedge i_rst_n) begin : READ_REG
    if (~i_rst_n) begin
        o_rdata <= 32'd0;
    end else if (i_read) begin
        case (i_addr)
            BCR_ADDR: o_rdata <= r_bcr;
            default:  o_rdata <= 32'd0; // Default read value for undefined addresses
        endcase
    end else begin
        // Keep the last read value if not reading
        // Alternatively, could assign 0: o_rdata <= 32'd0;
        o_rdata <= o_rdata;
    end
end

endmodule