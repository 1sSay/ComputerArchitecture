module stack_behaviour_normal(
    output wire[3:0] IO_DATA,
    input wire RESET,
    input wire CLK,
    input wire[1:0] COMMAND,
    input wire[2:0] INDEX
    // input wire[3:0] I_DATA
    );

    reg [3:0] memory_cells[4:0];
    reg [3:0] data;
    reg [3:0] out;
    reg [2:0] top_index;
    reg [2:0] get_index;
    reg [2:0] i, j;

    assign IO_DATA = data;

    always @(negedge CLK) begin
        data = 4'bz;
    end

    always @(RESET or CLK) begin
        if (RESET == 1) begin
            for (i = 0; i < 5; i = i + 1) begin
                memory_cells[i] = 'b0000;
            end
            top_index = 'b000;
        end

        if (CLK == 1) begin
            case (COMMAND)
                'b00: begin end // nope
                'b01: begin
                    memory_cells[top_index] = IO_DATA;
                    top_index = (top_index + 1) % 5;
                end
                'b10: begin
                    if (top_index == 'b000) top_index = 'b100;
                    else top_index = top_index - 1;
                    data = memory_cells[top_index];
                end
                'b11: begin
                    get_index = INDEX;
                    get_index = get_index % 5;
                    if (get_index < top_index)
                        get_index = top_index - get_index - 1;
                    else
                        get_index = 4 - (get_index - top_index);
                    data = memory_cells[get_index];
                end
            endcase
        end
    end
endmodule
