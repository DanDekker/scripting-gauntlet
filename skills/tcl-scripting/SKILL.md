---
name: tcl-scripting
description: Write short Tcl scripts that parse delimited text, preserve Tcl list structure, aggregate dicts, gate regexp captures, safely substitute template variables, catch expression errors, and inspect literal file paths. Use when tclsh is already embedded in a tool or available on the target host and the job fits the core Tcl commands. Not for a new service, a package-heavy application, or shell-style command execution.
license: MIT
metadata:
  family: text-munging
  drill: 255-tcl-split-fields
---

# Tcl scripting

Tcl is a small host-integrated language. Its core gives you strings, lists, dicts,
regular expressions, file commands, and a clear error result. The traps come from
mixing those representations or forgetting that Tcl code and Tcl data use similar
syntax.

## When Tcl is the right tool

Use Tcl when the target already embeds it, when tclsh is present on a small host, or
when a short text transform can stay within the standard commands. Keep a script
linear: open, parse, validate, report, close.

Do not use it to invent a package manager, a JSON parser, or an interactive shell. If
the task needs those, Python is usually the better timeboxed choice.

## A Tcl list is structured data

split returns a Tcl list and preserves empty elements, including a trailing one:

~~~tcl
set fields [split "a||c|" |]
# a, {}, c, {}
lassign $fields first second third fourth
~~~

Use lindex, llength, lassign, and foreach on list values. Do not split a Tcl list on
spaces: braces and quotes are grouping syntax, not characters in the decoded words.
Drills: 255-tcl-split-fields and 262-tcl-list-quoting.

## Dict presence comes before dict get

dict get on a missing key raises an error. Use dict exists first when missing is a
valid state:

~~~tcl
if {![dict exists $settings $key]} {
    set state missing
} else {
    set value [dict get $settings $key]
    if {$value eq ""} {
        set state empty
    } elseif {$value eq "0"} {
        set state zero
    } else {
        set state value
    }
}
~~~

Tcl expression truthiness treats 0 and empty text as false. The string false is also
not a safe substitute for a textual-state test. Drill: 256-tcl-dict-presence.

## regexp returns a decision

regexp returns 1 for a match and 0 otherwise. Test it before reading capture variables:

~~~tcl
if {[regexp {^\[(INFO|WARN)\] worker=([[:alnum:]._-]+)$} $line -> level worker]} {
    # use level and worker here
} else {
    incr skipped
}
~~~

Anchors make the record shape explicit. A failed regexp should never become a report
row populated from stale or empty capture variables. Drill: 257-tcl-regexp-records.

## catch is a row-level boundary

catch returns zero for success and nonzero for a Tcl error:

~~~tcl
if {[catch {expr {double($numerator) / double($denominator)}} ratio]} {
    incr rejected
    continue
}
set rendered [format "%.2f" $ratio]
~~~

Use braces around expr expressions so Tcl does not perform an early round of
substitution. Force double division when the contract is decimal. Drill:
260-tcl-catch-expr.

## subst can execute commands

subst performs variable, command, and backslash substitution by default. Templates are
usually data, so select the allowed classes:

~~~tcl
set rendered [subst -nocommands -nobackslashes $template]
~~~

This still substitutes variables but leaves bracketed command text inert. Never use
eval as a shortcut for parsing a command list. Drill: 259-tcl-safe-subst.

## Files and globs are different

file join constructs a path; open reads that exact path; file size reports bytes. glob
interprets star and brackets as patterns. If a manifest says a filename literally
contains a star or brackets, do not pass it through glob. Drill: 258-tcl-file-literal.

## Dicts need a report order

Aggregate with dict incr, then turn entries into a list and sort with an explicit
comparator. Do not use dict iteration order as a ranking or a stable output order:

~~~tcl
proc compare_rows {left right} {
    if {[lindex $left 1] != [lindex $right 1]} {
        return [expr {[lindex $right 1] - [lindex $left 1]}]
    }
    return [string compare [lindex $left 0] [lindex $right 0]]
}
set rows [lsort -command compare_rows $rows]
~~~

Drill: 261-tcl-dict-sort.

## Tcl output checklist

1. Keep parsed fields as lists or dicts, not ad-hoc strings.
2. Test return values before reading captures or outputs.
3. Use string operators for textual rules and expr for numeric rules.
4. Quote CSV cells before joining them.
5. Keep paths literal unless the contract explicitly asks for globbing.
6. Close files and let unexpected errors exit non-zero.

See references/tcl-gotchas.md for the compact behavior table. Prove the choices against
the Tcl track: 002 and 255-262.
