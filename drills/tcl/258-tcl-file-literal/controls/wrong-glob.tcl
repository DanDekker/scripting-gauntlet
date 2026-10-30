#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set root [file join $in tree]
set fh [open [file join $in manifest.txt] r]
set rows {}
set total 0
while {[gets $fh relative] >= 0} {
    set relative [string trim $relative]
    if {$relative eq ""} continue
    set matches [glob -nocomplain [file join $root $relative]]
    if {[llength $matches] == 0} continue
    set path [lindex $matches 0]
    set size [file size $path]
    set file [open $path r]
    gets $file first_line
    close $file
    lappend rows [list $relative $size [string trim $first_line]]
    incr total $size
}
close $fh
set outfh [open [file join $out files.csv] w]
puts $outfh "path,bytes,first_line"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"files\":%d,\"bytes\":%d}" [llength $rows] $total]
close $outfh
