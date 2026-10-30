#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set settings {}
set fh [open [file join $in settings.tsv] r]
while {[gets $fh line] >= 0} {
    if {$line eq ""} { continue }
    set parts [split $line "\t"]
    if {[llength $parts] != 2} { error "malformed settings row: $line" }
    dict set settings [string trim [lindex $parts 0]] [string trim [lindex $parts 1]]
}
close $fh

proc csv_cell {value} {
    return "\"[string map [list "\"" "\"\""] $value]\""
}
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}
set keys {limit owner enabled region}
set rows {}
set missing 0
set empty 0
set zero 0
foreach key $keys {
    if {![dict exists $settings $key]} {
        set state missing
        set value ""
        incr missing
    } else {
        set value [dict get $settings $key]
        if {$value eq ""} {
            set state empty
            incr empty
        } elseif {$value eq "0"} {
            set state zero
            incr zero
        } else {
            set state value
        }
    }
    lappend rows [list $key $state $value]
}

set outfh [open [file join $out settings.csv] w]
puts $outfh "key,state,value"
foreach row $rows { puts $outfh [csv_row $row] }
close $outfh
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"keys\":%d,\"missing\":%d,\"empty\":%d,\"zero\":%d}" \
    [llength $keys] $missing $empty $zero]
close $outfh
