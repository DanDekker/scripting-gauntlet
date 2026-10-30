# 259-tcl-safe-subst

> "Render this small template with the supplied values, but leave the bracketed shell
> command as text. The template is data, not a program."

## Input

in/values.tsv contains:

~~~text
name	Ada
path	/tmp/demo
~~~

in/template.txt contains:

~~~text
Name: $name
Path: $path
Command: [clock seconds]
~~~

## Rules

1. Load the two values into Tcl variables.
2. Substitute variable references.
3. Do not execute bracketed commands and do not interpret backslash escapes in the
   template.

## Output

Write exactly out/rendered.txt:

~~~text
Name: Ada
Path: /tmp/demo
Command: [clock seconds]
~~~

No extra newline beyond the template's own final newline and no extra files.

## Messes to expect

- Tcl subst performs variable, command, and backslash substitution by default
- subst -nocommands leaves bracketed command text inert
- template data can contain syntax that would be unsafe to execute
- variable substitution still works when command substitution is disabled

## Timebox

Four minutes. Use subst with the narrowest flags matching the contract.
