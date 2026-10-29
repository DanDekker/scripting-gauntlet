#!/usr/bin/env tclsh
if {![info exists env(IN)] || ![info exists env(OUT)]} {
    error "IN and OUT must be set"
}
file mkdir $env(OUT)

set statuses [dict create]
set paths [dict create]
set valid 0
set skipped 0
set log [open [file join $env(IN) access.log] r]
while {[gets $log line] >= 0} {
    if {![regexp {"\S+ (\S+) HTTP/[0-9.]+\s*"?\s*([0-9]{3})\y} $line -> rawPath status]} {
        incr skipped
        continue
    }
    set path [lindex [split $rawPath ?] 0]
    dict incr statuses $status
    dict incr paths $path
    incr valid
}
close $log

proc statusOrder {a b} {
    set countOrder [expr {[lindex $b 1] - [lindex $a 1]}]
    if {$countOrder != 0} { return $countOrder }
    return [expr {[lindex $a 0] - [lindex $b 0]}]
}
proc pathOrder {a b} {
    set countOrder [expr {[lindex $b 1] - [lindex $a 1]}]
    if {$countOrder != 0} { return $countOrder }
    return [string compare [lindex $a 0] [lindex $b 0]]
}

set statusRows {}
dict for {status count} $statuses { lappend statusRows [list $status $count] }
set out [open [file join $env(OUT) status.csv] w]
puts $out "status,count"
foreach row [lsort -command statusOrder $statusRows] {
    puts $out "[lindex $row 0],[lindex $row 1]"
}
close $out

set pathRows {}
dict for {path count} $paths { lappend pathRows [list $path $count] }
set out [open [file join $env(OUT) top_paths.csv] w]
puts $out "path,hits"
foreach row [lrange [lsort -command pathOrder $pathRows] 0 4] {
    puts $out "[lindex $row 0],[lindex $row 1]"
}
close $out

set out [open [file join $env(OUT) summary.json] w]
puts $out [format {{"valid":%d,"skipped":%d}} $valid $skipped]
close $out
