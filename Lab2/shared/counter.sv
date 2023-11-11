module counter(output reg[3:0] out, input clk, input reset, input enable);
  always @ (posedge clk) begin
    if (enable) begin
      if (reset) 
        out <= 0;       
      else 
      	out <= out + 1; 
    end else begin
      out <= out;
    end
  end
endmodule

module counter_tb;
    reg clk, reset, enable; wire[3:0] out;
    counter c4(out, clk, reset, enable);

    initial begin
        $dumpfile("dump.vcd"); $dumpvars(1, counter_tb);
        $display(" t\tclk\trst\ten\t out == out");
        $monitor("%2t\t%b\t%b\t%b\t%b == %d", $time, clk, reset, enable, out, out);

      	clk = 0;	reset = 1;  enable = 1;
        #1 reset = 0;
        #2 reset = 1;
        #2 reset = 0;
      	#20 $finish;
    end

    always #1 clk = ~clk;
  
    //always @(posedge clk) $display("%0t\t%b %b %b %b == %d", $time, clk, reset, enable, out, out);
endmodule