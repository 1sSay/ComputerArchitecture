
// testbanch.sv в EDAPlayground
module not_tb;
  reg in; integer t_value; wire out;
  
  not_switch not_instance(.out(out), .in(in));
  //not_switch not_instance1(.out(out), .in(out)); // короткое замыкание
  
  initial begin
    $dumpfile("dump.vcd"); $dumpvars(1);   
    $monitor("$time %0d: in=%b, out=%b, t_value=%0d, strength=%v", $time, in, out, t_value, out);
    
    in = 0; t_value = 0;    
    #1 t_value += 1;
    #2 t_value += 1;  
    #1 in = 1;
    #2 t_value += 1; 
    #3 in = 0;
  end 

endmodule