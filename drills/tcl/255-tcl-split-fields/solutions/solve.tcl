#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)

proc csv_cell {value} {
    return "\"[string map [list "\"" "\"\""] $value]\""
}
proc csv_row {row} {
    set cells {}
    foreach cell $row { lappend cells [csv_cell $cell] }
    return [join $cells ,]
}

set fh [open [file join $in records.psv] r]
set rows {}
set empty_tag 0
set blank_name 0
set first 1
while {[gets $fh line] >= 0} {
    if {$first} {
        set first 0
        continue
    }
    if {[string trim $line] eq ""} {
        continue
    }
    set fields [split $line |]
    if {[llength $fields] != 3} {
        error "expected three fields: $line"
    }
    set cleaned {}
    foreach field $fields {
        lappend cleaned [string trim $field]
    }
    lassign $cleaned id name tag
    set state [expr {$tag eq "" ? "empty" : "value"}]
    if {$tag eq ""} { incr empty_tag }
    if {$name eq ""} { incr blank_name }
    lappend rows [list $id $name $tag $state]
}
close $fh

set outfh [open [file join $out records.csv] w]
puts $outfh "id,name,tag,tag_state"
foreach row $rows {
    puts $outfh [csv_row $row]
}
close $outfh

set summary [dict create records [llength $rows] empty_tag $empty_tag blank_name $blank_name]
set outfh [open [file join $out summary.json] w]
puts $outfh [format "{\"records\":%d,\"empty_tag\":%d,\"blank_name\":%d}" \
    [dict get $summary records] [dict get $summary empty_tag] [dict get $summary blank_name]]
close $outfh
