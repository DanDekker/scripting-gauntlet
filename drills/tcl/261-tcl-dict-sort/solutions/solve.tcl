#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set counts {}
set fh [open [file join $in counts.tsv] r]
gets $fh header
while {[gets $fh line] >= 0} {
    if {[string trim $line] eq ""} continue
    lassign [split $line "\t"] key amount
    set key [string trim $key]
    set amount [expr {[string trim $amount] + 0}]
    if {[dict exists $counts $key]} {
        dict incr counts $key $amount
    } else {
        dict set counts $key $amount
    }
}
close $fh

proc compare_rows {left right} {
    set left_count [lindex $left 1]
    set right_count [lindex $right 1]
    if {$left_count != $right_count} {
        return [expr {$right_count - $left_count}]
    }
    return [string compare [lindex $left 0] [lindex $right 0]]
}
set rows {}
dict for {key amount} $counts {
    lappend rows [list $key $amount]
}
set rows [lsort -command compare_rows $rows]

proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set outfh [open [file join $out counts.csv] w]
puts $outfh "key,count"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set total 0
foreach row $rows { incr total [lindex $row 1] }
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"keys\":%d,\"total\":%d}" [llength $rows] $total]
close $outfh
