module wait_tb;
    integer count = 0;
    initial begin
        $monitor("Time [%0t]: count = %0d", $time, count);
        //forever #2  count++;
        repeat (5)  #2 count++;
    end
    initial begin
        wait(count == 'd3);
        $display("count={3} %0d at time = %0t", count, $time);
        $finish;
    end
    initial begin
        wait(count == 'd4);
        $display("count={3} %0d at time = %0t", count, $time);
        $finish;
    end
endmodule