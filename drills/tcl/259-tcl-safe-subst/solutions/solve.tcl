#!/usr/bin/env tclsh
set in $::env(IN)
set out $::env(OUT)
set values [open [file join $in values.tsv] r]
while {[gets $values line] >= 0} {
    if {$line eq ""} continue
    lassign [split $line "\t"] key value
    set $key [string trim $value]
}
close $values
set fh [open [file join $in template.txt] r]
set template [read $fh]
close $fh
set rendered [subst -nocommands -nobackslashes $template]
set outfh [open [file join $out rendered.txt] w]
puts -nonewline $outfh $rendered
close $outfh
