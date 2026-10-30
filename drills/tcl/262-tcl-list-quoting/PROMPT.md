# 262-tcl-list-quoting

> "These command lines are Tcl lists, so a target with spaces is still one word.
> Extract the command and target without shredding the quoting."

## Input

in/commands.txt contains valid Tcl list syntax:

~~~text
deploy {web app} --env prod
backup "/tmp/My File" --full
rotate logs --keep 7
~~~

## Rules

1. Parse each line as a Tcl list.
2. command is word 0, target is word 1, and args is the number of remaining words.
3. Preserve the decoded target text and input order.

## Output

Write out/commands.csv with header command,target,args:

~~~csv
deploy,web app,3
backup,/tmp/My File,2
rotate,logs,3
~~~

Write out/summary.json with exactly {"commands":3,"with_spaces":2}.

## Messes to expect

- braces and quotes are Tcl list syntax, not characters in the target
- split on a literal space breaks the first two targets
- lindex and llength understand Tcl list quoting
- target text is data; do not eval the entire line as a command

## Timebox

Four minutes. Use lindex and llength on each line as a list.
