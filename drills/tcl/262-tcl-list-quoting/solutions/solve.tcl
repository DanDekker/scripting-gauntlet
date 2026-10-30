#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set fh [open [file join $in commands.txt] r]
set rows {}
set with_spaces 0
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    set command [lindex $line 0]
    set target [lindex $line 1]
    set args [expr {[llength $line] - 1}]
    if {[string first " " $target] >= 0} { incr with_spaces }
    lappend rows [list $command $target $args]
}
close $fh
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set outfh [open [file join $out commands.csv] w]
puts $outfh "command,target,args"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"commands\":%d,\"with_spaces\":%d}" [llength $rows] $with_spaces]
close $outfh
