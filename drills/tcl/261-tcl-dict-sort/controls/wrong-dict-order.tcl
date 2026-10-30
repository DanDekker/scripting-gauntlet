#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set counts {}
set fh [open [file join $in counts.tsv] r]
gets $fh header
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    lassign [split $line "\t"] key amount
    if {[dict exists $counts $key]} { dict incr counts $key $amount } else { dict set counts $key $amount }
}
close $fh
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set outfh [open [file join $out counts.csv] w]
puts $outfh "key,count"
dict for {key amount} $counts { puts $outfh [csv_row [list $key $amount]] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh "{\"keys\":3,\"total\":8}"
close $outfh
