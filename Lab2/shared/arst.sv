module async_rs_trigger(output reg q, q_inv, input wire r, s);
    always @(r or s) begin 
        case ({r,s})
            2'b01: begin
                q = 1'b1;
            end
            2'b10: begin
                q = 1'b0;
            end
            2'b11: begin
                q = 1'bx;
            end
        endcase
        q_inv = ~q;
    end
    
endmodule


//`include "arst.sv"

module arst_tb;
    reg r, s;
    wire q, nq;

    async_rs_trigger rst(q, nq, r, s);

    initial begin
        $dumpfile("dump.vcd"); $dumpvars(1, arst_tb);
        $monitor("%0t: r=%b s=%b q=%b", $time, r, s, q);
            r = 0; s = 0;
        #1; r = 0; s = 1;
        #1; r = 1; s = 1;
        #1; r = 1; s = 0;
        #1; r = 0; s = 1;
        #1; r = 1; s = 1;
        #1; r = 0; s = 0;
        #1; r = 1; s = 0;
        #1; r = 0; s = 0;
        $finish;
    end  
endmodule