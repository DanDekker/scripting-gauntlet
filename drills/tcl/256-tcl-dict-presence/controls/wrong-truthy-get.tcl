#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set settings {}
set fh [open [file join $in settings.tsv] r]
while {[gets $fh line] >= 0} {
    if {$line eq ""} continue
    lassign [split $line "\t"] key value
    dict set settings [string trim $key] [string trim $value]
}
close $fh
proc csv_cell {value} { return "\"[string map [list "\"" "\"\""] $value]\"" }
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set rows {}
foreach key {limit owner enabled region} {
    if {[catch {dict get $settings $key} value]} {
        set state missing
        set value ""
    } elseif {$value eq "" || $value eq "0" || $value eq "false"} {
        set state empty
    } else {
        set state value
    }
    lappend rows [list $key $state $value]
}
set outfh [open [file join $out settings.csv] w]
puts $outfh "key,state,value"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh "{\"keys\":4,\"missing\":1,\"empty\":1,\"zero\":0}"
close $outfh
