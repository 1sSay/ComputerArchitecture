module data_types_tb;
    reg a; reg [7:0] b; time t; 
    logic[3:0] data; logic x;
    
    assign x = data[0];
    initial begin
        a = 1;              $display("1bit = %0d", a);
        b = 8'hF2;          $display("8bit_dec = %0d", b);
        b = 8'b10110011;    $display("8bit_bin = %0d", b);
        b = -8'd5;          $display("8bit (-5) = %0d", b);
        b = 8'd?;           $display("Z-state = %0d", b);
        t = $time;          $display("time = %0t", t);

                            $display("data=0x%0h data=0b%0b x=%0b", data, data, x);
        data = 4'hB; #1;    $display("data=0x%0h data=0b%0b x=%0b", data, data, x);
    end

endmodule