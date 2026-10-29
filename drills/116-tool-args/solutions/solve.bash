#!/usr/bin/env bash
# 116-tool-args - jq validates every model call against the schema, in contract order.
set -euo pipefail

in_dir="${IN:?IN not set}"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# Keep only records that are objects with a string name and a string call_id.
jq -R 'fromjson? // empty' "$in_dir/calls.jsonl" \
  | jq -c 'select((type == "object") and ((.name|type) == "string") and ((.call_id|type) == "string"))' \
  > "$scratch/calls.jsonl"

jq -s --slurpfile schema "$in_dir/schema.json" '
  $schema[0] as $s
  | $s.name as $tool
  | ($s.required // []) as $req
  | ($s.properties // {}) as $props
  | def typeok($t; $v):
      if $t == "string" then ($v|type) == "string"
      elif $t == "integer" then (($v|type) == "number") and (($v|floor) == $v)
      elif $t == "number" then ($v|type) == "number"
      elif $t == "boolean" then ($v|type) == "boolean"
      elif $t == "object" then ($v|type) == "object"
      elif $t == "array" then ($v|type) == "array"
      else true end;
    def optional($req; $k): (($req | index($k)) == null);
    [ .[] as $c
      | if $c.name != $tool then {id: $c.call_id, kind: "wrong-tool", errors: []}
        elif ((($c|has("arguments"))|not) or (($c.arguments|type) != "object"))
          then {id: $c.call_id, kind: "bad-arguments", errors: []}
        else
          $c.arguments as $a
          | {id: $c.call_id, kind: "schema",
             errors: (
               [ $req[] as $p | select(($a|has($p))|not) | "missing:" + $p ]
               + [ ($a|keys_unsorted[]) as $k
                   | select(($props|has($k))|not) | "unknown:" + $k ]
               + [ ($a|to_entries[]) as $e
                   | select($props|has($e.key))
                   | select((($e.value == null) and optional($req; $e.key)) | not)
                   | select((typeok($props[$e.key].type; $e.value)) | not)
                   | "type:" + $e.key ]
               + [ ($a|to_entries[]) as $e
                   | select($props|has($e.key))
                   | select((($e.value == null) and optional($req; $e.key)) | not)
                   | select(typeok($props[$e.key].type; $e.value))
                   | select(($props[$e.key].enum // null) != null)
                   | select(($props[$e.key].enum | index($e.value)) == null)
                   | "enum:" + $e.key ]
               + [ ($a|to_entries[]) as $e
                   | select($props|has($e.key))
                   | select(($e.value|type) == "number")
                   | select(($props[$e.key].minimum // null) != null)
                   | select($e.value < $props[$e.key].minimum)
                   | "min:" + $e.key ]
             )}
        end ]
  | . as $res
  | { rows: [ $res[] as $r | $r.errors[] | {call_id: $r.id, error: .} ],
      summary: {
        calls: ($res|length),
        valid: ([$res[]|select((.errors|length) == 0)]|length),
        invalid: ([$res[]|select((.errors|length) > 0)]|length),
        errors: ([$res[]|.errors|length]|add) // 0,
        wrong_tool: ([$res[]|select(.kind == "wrong-tool")]|length),
        bad_arguments: ([$res[]|select(.kind == "bad-arguments")]|length)
      } }
' "$scratch/calls.jsonl" > "$scratch/result.json"

{
  printf 'call_id,error\n'
  jq -r '.rows[] | .call_id + "," + .error' "$scratch/result.json"
} > "$out_dir/errors.csv"

jq -c '.summary' "$scratch/result.json" > "$out_dir/summary.json"
