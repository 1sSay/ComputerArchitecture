module blocking_race_cond_tb;
  reg [3:0] data = 4'h2;
  reg [3:0] y = 4'h3;

  initial begin
    y <= data;
    #1; $display("1st block: data = %0h and y = %0h time = %0t", data, y, $time);
  end

  initial begin 
    data <= y;
    #1; $display("2nd block: data = %0h and y = %0h time = %0t", data, y, $time);
  end
endmodule