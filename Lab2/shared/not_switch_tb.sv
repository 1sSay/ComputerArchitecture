module not_switch(output wire out, input wire in);
    supply1 PWR;
    supply0 GND;

	pmos p1(out, PWR, in);
	nmos n1(out, GND, in);
endmodule

module nand2(output wire out, input wire in1, input wire in2);
    supply1 PWR;
    supply0 GND;

    nmos n1(out, n2, in1);
    nmos n2(n1, GND, in2);

    pmos p1(PWR, out, in1);
    pmos p2(PWR, out, in2);
endmodule

// testbanch.sv в EDAPlayground
module not_tb;
    reg in1; reg in2; integer t_value; wire out;
 
    // not_switch not_instance(.out(out), .in(in));
    //not_switch not_instance1(.out(out), .in(out)); // короткое замыкание

    nand2 nand2_instance(.out(out), .in1(in1), .in2(in2));

	initial begin
	    $dumpfile("dump.vcd"); $dumpvars(1);
	    $monitor("$time %0d: in1=%b, in2=%b, out=%b, t_value=%0d, strength=%v", $time, in1, in2, out, t_value, out);

	    in1 = 0; in2 = 0; t_value = 0; t_value += 1;
	    #1 in2 = 1; t_value += 1;  
	    #1 in1 = 1; in2 = 0; t_value += 1;
	    #1 in1 = 1; in2 = 1; t_value += 1;
    end
endmodule