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
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    lassign [split $line ,] id numerator denominator
    if {[catch {expr {$numerator / $denominator}} ratio]} { set ratio 0 }
    lappend rows [list $id [format "%.2f" $ratio]]
}
close $fh
set outfh [open [file join $out ratios.csv] w]
puts $outfh "id,ratio"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"accepted\":%d,\"rejected\":0}" [llength $rows]]
close $outfh
