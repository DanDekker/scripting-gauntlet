#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}

set fh [open [file join $in ratios.csv] r]
gets $fh header
set rows {}
set rejected 0
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    lassign [split $line ,] id numerator denominator
    set ok [catch {expr {double($numerator) / double($denominator)}} ratio]
    if {$ok || $denominator == 0} {
        incr rejected
        continue
    }
    lappend rows [list $id [format "%.2f" $ratio]]
}
close $fh

set outfh [open [file join $out ratios.csv] w]
puts $outfh "id,ratio"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"accepted\":%d,\"rejected\":%d}" [llength $rows] $rejected]
close $outfh
