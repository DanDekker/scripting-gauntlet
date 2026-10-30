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
set slow 0
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} { continue }
    if {![regexp $pattern $line -> level worker duration]} {
        incr skipped
        continue
    }
    set duration [expr {$duration + 0}]
    set is_slow [expr {$duration > 100 ? "yes" : "no"}]
    if {$is_slow eq "yes"} { incr slow }
    lappend rows [list $level $worker $duration $is_slow]
}
close $fh

set outfh [open [file join $out events.csv] w]
puts $outfh "level,worker,duration,slow"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"records\":%d,\"skipped\":%d,\"slow\":%d}" \
    [llength $rows] $skipped $slow]
close $outfh
