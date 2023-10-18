module always_tb;
    reg [3:0] counter;
    initial begin
        counter = 0;
    end
    always #2 begin
        counter = counter + 1;
    end
    always #1 @(counter) begin
        $display("Hello world %d at %0t", counter, $time);
    end
    always #10 begin
        $finish;
    end
endmodule