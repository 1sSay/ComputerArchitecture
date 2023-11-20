// RS Trigger for D
module RS(q, not_q, r, s, c);
    output q, not_q;
    input r, s, c;
    wire r_sync, s_sync;

    and(r_sync, r, c);
    and(s_sync, s, c);

    nor(q, not_q, r_sync);
    nor(not_q, q, s_sync);
endmodule

// D with high level sync
module D_HIGH(q, not_q, d, c);
    output q, not_q;
    input d, c;
    wire not_d;

    not(not_d, d);
    RS rs_trigger(q, not_q, not_d, d, c);
endmodule

// D with rising edge sync
module D_FRONT(q, not_q, d, c);
    output q, not_q;
    input d, c;
    wire not_c;
    wire q_first_d, not_q_first_d;

    not(not_c, c);

    D_HIGH first_d_high(q_first_d, not_q_first_d, d, not_c);
    D_HIGH second_d_high(q, not_q, q_first_d, c);
endmodule

// Summator
module SUM(s, c_out, a, b, c_in);
    output s, c_out;
    input a, b, c_in;

    wire xor_a_b, xor_ab_c;
    wire and_a_b, and_ab_c;
    wire or_and_xor;

    xor(xor_a_b, a, b);
    xor(s, xor_a_b, c_in);

    and(and_a_b, a, b);
    and(and_ab_c, xor_a_b, c_in);

    or(c_out, and_a_b, and_ab_c);
endmodule

// Summator 3 bits
module SUM3(sum, a, b);
    output wire[3:0] sum;
    input wire[2:0] a;
    input wire[2:0] b;

    wire s1, c1, s2, c2, s3, c3;

    supply0 ground;

    SUM sum1(sum[0], c1, a[0], b[0], ground);
    SUM sum2(sum[1], c2, a[1], b[1], c1);
    SUM sum3(sum[2], sum[3], a[2], b[2], c2);

endmodule

// decoder 2 bits
module DECODER2TO4(a0, a1, a2, a3, a);
    output wire a0, a1, a2, a3;
    input[1:0] a;
    wire[1:0] not_a;

    not(not_a[0], a[0]);
    not(not_a[1], a[1]);

    and(a0, not_a[0], not_a[1]);
    and(a1, a[0], not_a[1]);
    and(a2, not_a[0], a[1]);
    and(a3, a[0], a[1]);
endmodule

// decoder mod 5 ;)
module DECODER3TO5(a0, a1, a2, a3, a4, a);
    output wire a0, a1, a2, a3, a4;
    input wire [2:0] a;
    wire[2:0] not_a;

    not(not_a[0], a[0]);
    not(not_a[1], a[1]);
    not(not_a[2], a[2]);

    and(a0, not_a[0], not_a[1], not_a[2]);
    and(a1, a[0], not_a[1], not_a[2]);
    and(a2, not_a[0], a[1], not_a[2]);
    and(a3, a[0], a[1], not_a[2]);
    and(a4, not_a[0], not_a[1], a[2]);
endmodule

module DECODER3TO5_IF(a0, a1, a2, a3, a4, a, f);
    output wire a0, a1, a2, a3, a4;
    input wire [2:0] a;
    input wire f;

    wire [4:0] b;

    DECODER3TO5 decoder(b[0], b[1], b[2], b[3], b[4], a);

    and(a0, b[0], f);
    and(a1, b[1], f);
    and(a2, b[2], f);
    and(a3, b[3], f);
    and(a4, b[4], f);
endmodule

module INCREMENT(increased, number);
    output wire [2:0] increased;
    input wire [2:0] number;

    wire [3:0] increased4;

    supply0 ground;
    supply1 power;

    SUM3 sum3(increased4, number, {ground,ground,power});

    assign increased[2:0] = increased4[2:0];
endmodule

module INCREMENT_MOD_5(increased, number);
    output wire [2:0] increased;
    input wire [2:0] number;

    wire [2:0] increased3;

    INCREMENT increment(.increased(increased3),
              .number(number));

    wire not_i1;
    nor(not_i1, increased3[1]);

    wire nand_6;
    nand(nand_6, increased3[0], not_i1, increased3[2]);

    and(increased[0], increased3[0], nand_6);
    and(increased[1], increased3[1], nand_6);
    and(increased[2], increased3[2], nand_6);
endmodule

module DECREMENT_MOD_5(decreased, number);
    output wire [2:0] decreased;
    input wire [2:0] number;

    supply1 one;
    wire [3:0] sub_result;
    SUM3 sub(sub_result, number, {one,one,one});

    wire [2:0] inverted;
    not(inverted[0], number[0]);
    not(inverted[1], number[1]);
    not(inverted[2], number[2]);

    wire seven;
    and(seven, inverted[0], inverted[1], inverted[2]);
    wire not_seven;
    not(not_seven, seven);

    and(decreased[0], sub_result[0], not_seven);
    and(decreased[1], sub_result[1], not_seven);
    or(decreased[2], sub_result[2], seven);
endmodule

module COUNTER_MOD_5(index, inc, dec, clock);
    output wire [2:0] index;
    input wire clock;
    input wire inc;
    input wire dec;

    wire not_i0, not_i1, not_i2;

    wire not_clock;
    not(not_clock, clock);

    D_FRONT d0(index[0], not_i0, new_value[0], not_clock);
    D_FRONT d1(index[1], not_i1, new_value[1], not_clock);
    D_FRONT d2(index[2], not_i2, new_value[2], not_clock);

    wire [2:0] increased;
    INCREMENT_MOD_5 inc_number(increased, {index[0],index[1],index[2]});
    wire [2:0] and_increased;
    and(and_increased[0], increased[0], inc);
    and(and_increased[1], increased[1], inc);
    and(and_increased[2], increased[2], inc);

    wire [2:0] decreased;
    DECREMENT_MOD_5 dec_number(decreased, {index[0],index[1],index[2]});
    wire [2:0] and_decreased;
    and(and_decreased[0], decreased[0], dec);
    and(and_decreased[1], decreased[1], dec);
    and(and_decreased[2], decreased[2], dec);

    wire not_inc, not_dec, and_same;
    not(not_inc, inc);
    not(not_dec, dec);
    and(and_same, not_inc, not_dec);

    wire [2:0] same;
    and(same[0], index[0], and_same);
    and(same[1], index[1], and_same);
    and(same[2], index[2], and_same);

    wire [2:0] new_value;
    or(new_value[0], and_increased[0], and_decreased[0], same[0]);
    or(new_value[1], and_increased[1], and_decreased[1], same[1]);
    or(new_value[2], and_increased[2], and_decreased[2], same[2]);
endmodule

module MEMORY_CELL(odata, idata, c);
    output wire [3:0] odata;
    input wire [3:0] idata;
    input wire c;

    wire [3:0] not_gates;

    D_FRONT d0(odata[0], not_gates[0], idata[0], c);
    D_FRONT d1(odata[1], not_gates[1], idata[0], c);
    D_FRONT d2(odata[2], not_gates[2], idata[0], c);
    D_FRONT d3(odata[3], not_gates[3], idata[0], c);
endmodule

module MOD5(ovalue, ivalue);
    output wire [2:0] ovalue;
    input wire [3:0] ivalue;

    wire [3:0] inverted;

    not (inverted[0], ivalue[0]);
    not (inverted[1], ivalue[1]);
    not (inverted[2], ivalue[2]);
    not (inverted[3], ivalue[3]);

    wire [15:0] decoded;

    and(decoded[0], inverted[0], inverted[1], inverted[2], inverted[3]);                                                      // я сигма
    and(decoded[1], ivalue[0], inverted[1], inverted[2], inverted[3]);
    and(decoded[2], inverted[0], ivalue[1], inverted[2], inverted[3]);
    and(decoded[3], ivalue[0], ivalue[1], inverted[2], inverted[3]);
    and(decoded[4], inverted[0], inverted[1], ivalue[2], inverted[3]);
    and(decoded[5], ivalue[0], inverted[1], ivalue[2], inverted[3]);
    and(decoded[6], inverted[0], ivalue[1], ivalue[2], inverted[3]);
    and(decoded[7], ivalue[0], ivalue[1], ivalue[2], inverted[3]);
    and(decoded[8], inverted[0], inverted[1], inverted[2], ivalue[3]);
    and(decoded[9], ivalue[0], inverted[1], inverted[2], ivalue[3]);
    and(decoded[10], inverted[0], ivalue[1], inverted[2], ivalue[3]);
    and(decoded[11], ivalue[0], ivalue[1], inverted[2], ivalue[3]);
    and(decoded[12], inverted[0], inverted[1], ivalue[2], ivalue[3]);
    and(decoded[13], ivalue[0], inverted[1], ivalue[2], ivalue[3]);
    and(decoded[14], inverted[0], ivalue[1], ivalue[2], ivalue[3]);
    and(decoded[15], ivalue[0], ivalue[1], ivalue[2], ivalue[3]);

    wire [3:0] mod_value;

    or(mod_value[0], decoded[0], decoded[5], decoded[10], decoded[15]);
    or(mod_value[1], decoded[1], decoded[6], decoded[11]);
    or(mod_value[2], decoded[2], decoded[7], decoded[12]);
    or(mod_value[3], decoded[3], decoded[8], decoded[13]);
    or(ovalue[2], decoded[4], decoded[9], decoded[14]);

    or(ovalue[1], mod_value[3], mod_value[2]);
    or(ovalue[0], mod_value[3], mod_value[1]);

endmodule

module INVERT5(ovalue, ivalue);
    output wire [2:0] ovalue;
    input wire [2:0] ivalue;

    supply0 zero;


    wire [3:0] hehe; // not hehe :(
    or(hehe[0], ivalue[0]);
    or(hehe[1], ivalue[1]);
    or(hehe[2], ivalue[2]);

    wire [2:0] mod_value;
    MOD5 mod5_module(mod_value, hehe);

    wire [2:0] invert_mod;
    not(invert_mod[0], mod_value[0]);
    not(invert_mod[1], mod_value[1]);
    not(invert_mod[2], mod_value[2]);

    wire [3:0] encoded;
    and(ovalue[2], invert_mod[0], invert_mod[1], invert_mod[2]);
    and(encoded[1], mod_value[0], invert_mod[1], invert_mod[2]);
    and(encoded[2], invert_mod[0], mod_value[1], invert_mod[2]);
    and(encoded[3], mod_value[0], mod_value[1], invert_mod[2]);

    or(ovalue[1], encoded[1], encoded[2]);
    or(ovalue[0], encoded[1], encoded[3]);
endmodule

module SUB_MOD5(c, a, b);
    output [2:0] c;
    input [2:0] a;
    input [2:0] b;

    wire [2:0] inverted;
    INVERT5 inverter(inverted, b);

    wire [2:0] sum_ab;
    SUM3 sum1(sum_ab, a, inverted);

    wire [2:0] mod_sum;
    MOD5 mod_5(mod_sum, sum_ab);

    INCREMENT_MOD_5 inc5(c, mod_sum);
endmodule

module memory(odata, push, pop, get, idata, index, get_index, reset);
    output wire [3:0] odata;
    input wire push, pop, get, reset;
    input wire [3:0] idata;
    input wire [2:0] index;
    input wire [2:0] get_index;

    // reset 
    wire not_reset;
    not(not_reset, reset);

    wire [3:0] idata_after_reset;
    and and_reset[3:0](idata_after_reset, idata, {not_reset,not_reset,not_reset,not_reset});

    wire [3:0] inverted_data;
    not not_data[3:0](invert_data, idata_after_reset);

    wire reset_line;
    and(reset_line, reset, invert_data[0], invert_data[1], invert_data[2], invert_data[3], invert_data[4]);

    // push
    wire [4:0] push_index;
    DECODER3TO5_IF push_decoder(push_index[0], push_index[1], push_index[2], push_index[3], push_index[4],
                                index, push);
    wire [4:0] memory_clock;
    or or_memory_clock[4:0](memory_clock, push_index,
                            {reset_line,reset_line,reset_line,reset_line,reset_line})

    // memory
    wire [4:0] mem_out;

    MEMORY_CELL cell0(mem_out[0], idata_after_reset, push_index[0]);
    MEMORY_CELL cell1(mem_out[1], idata_after_reset, push_index[1]);
    MEMORY_CELL cell2(mem_out[2], idata_after_reset, push_index[2]);
    MEMORY_CELL cell3(mem_out[3], idata_after_reset, push_index[3]);
    MEMORY_CELL cell4(mem_out[4], idata_after_reset, push_index[4]);

    // pop
    wire [2:0] decreased_index;
    DECREMENT_MOD_5 decrement_for_index(decreased_index, index);

    wire [4:0] pop_index;
    DECODER3TO5_IF pop_decoder(pop_index[0], pop_index[1], pop_index[2], pop_index[3], pop_index[4],
                               decreased_index, pop);

    // get
    wire [2:0] sub_index;
    SUB_MOD5 sub_mod5_get(sub_index, index, get_index);

    wire [4:0] get_sub_index;
    DECODER3TO5_IF get_decoder(get_sub_index[0], get_sub_index[1], get_sub_index[2], get_sub_index[3], get_sub_index[4],
                               sub_index, get);

    // output
    wire [4:0] out_index;
    or or_out_index[4:0](out_index, pop_index, get_sub_index);

    wire [4:0] out_data[3:0];
    or or_out0[3:0](out_data[0], mem_out[0], {out_index[0],out_index[0],out_index[0],out_index[0]});
    or or_out1[3:0](out_data[1], mem_out[1], {out_index[1],out_index[1],out_index[1],out_index[1]});
    or or_out2[3:0](out_data[2], mem_out[2], {out_index[2],out_index[2],out_index[2],out_index[2]});
    or or_out3[3:0](out_data[3], mem_out[3], {out_index[3],out_index[3],out_index[3],out_index[3]});
    or or_out4[3:0](out_data[4], mem_out[4], {out_index[4],out_index[4],out_index[4],out_index[4]});

    or or_out_main[3:0](out_data[0], out_data[1], out_data[2], out_data[3], out_data[4]);
endmodule

module stack_tb;
    // reg inc, dec, clock;
    // wire [2:0] index;

    // COUNTER_MOD_5 increment(index, inc, dec, clock);

    // initial begin
    //     $dumpfile("dump.vcd"); $dumpvars(1);
    //     $monitor("c-%b|i-%b|d-%b|idx-%b", clock, inc, dec, index);

    //     clock = 0; inc = 0; dec = 0;
    //     #1
    //     clock = 1; inc = 0; dec = 0;
    //     #1;
    //     clock = 0; inc = 1; dec = 0;
    //     #1;
    //     clock = 0; inc = 1; dec = 0;
    //     #1;
    //     clock = 0; inc = 0; dec = 1;
    //     #1;
    //     clock = 0; inc = 0; dec = 0;
    //     #1;
    //     clock = 0; inc = 0; dec = 1;
    // end

    reg [3:0] number;
    wire [2:0] mod_5;

    MOD5 mod5_module(mod_5, number);

    initial begin
        $dumpfile("dump.vcd"); $dumpvars(1);
        $monitor("n - %b | m - %b", number, mod_5);

        # 1 number = 'b0000;
        # 1 number = 'b0001;
        # 1 number = 'b0010;
        # 1 number = 'b0011;
        # 1 number = 'b0100;
        # 1 number = 'b1000;
        # 1 number = 'b1111;
        # 1 number = 'b0100;
        # 1 number = 'b1110;

    end
endmodule