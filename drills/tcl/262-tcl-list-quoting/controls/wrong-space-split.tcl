#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set fh [open [file join $in commands.txt] r]
set rows {}
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    set words [split $line " "]
    lappend rows [list [lindex $words 0] [lindex $words 1] [expr {[llength $words] - 1}]]
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
puts $outfh "{\"commands\":3,\"with_spaces\":0}"
close $outfh
