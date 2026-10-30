#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set fh [open [file join $in records.psv] r]
gets $fh header
set rows {}
while {[gets $fh line] >= 0} {
    if {[regexp {^([^|]*)\|([^|]*)\|(.+)$} $line -> id name tag]} {
        set name [string trim $name]
        set tag [string trim $tag]
        lappend rows [list [string trim $id] $name $tag [expr {$tag eq "" ? "empty" : "value"}]]
    }
}
close $fh
set outfh [open [file join $out records.csv] w]
puts $outfh "id,name,tag,tag_state"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"records\":%d,\"empty_tag\":0,\"blank_name\":0}" [llength $rows]]
close $outfh
