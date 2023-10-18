module strength(output out, input i1, i2);   
    or (supply1, strong0) o1(out, i1, i2);
    and (strong1, supply0) a1(out, i1, i2);
endmodule

module strength_tb;
    reg i1, i2; wire out;
    strength dut(out, i1, i2);
    initial begin
        $monitor("%0t: i1 = %b, i2 = %b -> out = %b %v", $time, i1, i2, out, out);
           i1 = 0; i2 = 0;
        #1 i1 = 0; i2 = 1;
        #1 i1 = 1; i2 = 0;
        #1 i1 = 1; i2 = 1;
    end
endmodule


module strength_behaviour(output out, input i1, i2);  
  assign (supply1, strong0) out = (i1 | i2);  
  assign (strong1, supply0) out = i1 & i2;    
endmodule