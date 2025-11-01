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

    // Register Field Outputs (BCR - Bus Characteristics Register (BCR))
);

//--------------------------------------------------------------------------
// Register Definitions
//--------------------------------------------------------------------------

// Bus Characteristics Register (BCR) (BCR) @ 0x00
localparam BCR_ADDR       = 32'h;
localparam BCR_VALID_BIT  = 32'h00000000;  // [0:0] valid bits
localparam BCR_DEFAULT    = 32'h00000000;

logic [31:0] r_bcr;
logic        w_bcr_wr;

//--------------------------------------------------------------------------
// Register Write Logic
//--------------------------------------------------------------------------

always_ff @(posedge i_clk or negedge i_rst_n) begin
    if (~i_rst_n) begin
        // Bus Characteristics Register (BCR) (BCR)
        r_bcr <= BCR_DEFAULT;
    end else begin
        // Bus Characteristics Register (BCR) (BCR)
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

    // Bus Characteristics Register (BCR) (BCR)
    w_bcr_wr = i_write & (i_addr == BCR_ADDR);


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