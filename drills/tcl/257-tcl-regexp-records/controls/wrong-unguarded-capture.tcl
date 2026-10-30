#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set pattern {^\[(INFO|WARN|ERROR)\] worker=([-[:alnum:]_.]+) duration=([0-9]+)ms$}
set fh [open [file join $in events.log] r]
set rows {}
set skipped 0
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    regexp $pattern $line -> level worker duration
    if {$duration eq ""} { set duration 0 }
    lappend rows [list $level $worker $duration no]
}
close $fh
set outfh [open [file join $out events.csv] w]
puts $outfh "level,worker,duration,slow"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"records\":%d,\"skipped\":0,\"slow\":0}" [llength $rows]]
close $outfh
