module mux_structural_v1(output logic out, input logic a, s, b);
    wire w_and_a, w_and_b;
    or #2 or_res(out, w_and_a, w_and_b);
    and #2 and_a(w_and_a, a, n_s),
           and_b(w_and_b, b, s);
    not ns(n_s, s);
endmodule

module mux_structural_v2(output logic out, input logic a, s, b);
    not ns(n_s, s);
    and #2 and_a(w_and_a, a, n_s),
           and_b(w_and_b, b, s);
    or #2 or_res(out, w_and_a, w_and_b);
endmodule

module mux_behaviour_v1(output logic out, input logic a, s, b);
    assign #4 out = s ? b : a;
endmodule

module mux_behaviour_v2(output logic out, input logic a, s, b);
    or #4 or_res(out, (a & !s) | (b & s));
endmodule

module mux_behaviour_v3(output logic out, input logic a, s, b);
    always @(*) begin
        case(s)
            0 : out = #4 a;
            1 : out = #4 b;
            default : out = #4 a;
        endcase
    end
endmodule

module mux_tb;
    string display_format = "[%2t] %d %d %d %d";
    event display_states;
    logic a, sel, b, y;
    mux_behaviour_v3 _mux(y, a, sel, b);
    initial begin
        $display("time a sel b y");
        a = 0; b = 0; sel = 0;
        #10; a = 1; b = 0; sel = 1;
        #10; a = 1; b = 1; sel = 1;
        #10; a = 0; b = 1; sel = 1;
        #10; a = 0; b = 1; sel = 0;
        #10; a = 0; b = 0; sel = 0;
        #10; $finish;
    end
    always @(display_states) $display(display_format, $time, a, sel, b, y);
    initial begin
        #3; ->display_states;
        #1; ->display_states;
        #1; ->display_states;
        #10; ->display_states;
        #10; ->display_states;
        #10; ->display_states;
        #10; ->display_states;
        #10; ->display_states;
        #10;
    end
endmodule