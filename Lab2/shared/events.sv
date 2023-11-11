module named_events_tb;
    event e1;
    initial begin
        #10; $display("Triggering an event e1 at %0t", $time);
        ->e1;
    end
    initial begin
        $display("[BEFORE e1] at %0t", $time);
        @(e1) $display("Event e1 is triggered at %0t", $time);
        $display("[AFTER e1] at %0t", $time);
    end
endmodule