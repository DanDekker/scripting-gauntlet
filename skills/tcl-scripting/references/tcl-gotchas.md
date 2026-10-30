# Tcl gotcha cheat sheet

| behavior | trap | reliable move |
| --- | --- | --- |
| split | empty fields are data | preserve the returned list |
| list parsing | spaces are not the Tcl grammar | lindex/llength, never split on spaces |
| dict lookup | dict get raises on a missing key | dict exists before dict get |
| false values | 0 and empty text are false in expr | compare states explicitly |
| regexp | captures are meaningful only on success | branch on regexp's return value |
| expr | integer division truncates | wrap operands in double() for ratios |
| catch | ignored errors become fake rows | catch each row and count rejection |
| subst | default mode runs bracketed commands | subst -nocommands -nobackslashes |
| files | glob interprets filename punctuation | file join, open, and file size |
| dict order | iteration is not a ranking | lsort with numeric and string tie-breaks |

Tcl solution files in this track use only core commands and work on the installed
tclsh. Python twins prove the output contract but do not replace the Tcl semantic
negative.
