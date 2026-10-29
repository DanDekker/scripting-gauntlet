#!/usr/bin/env bash
# Diff two OpenAPI documents with jq: endpoint sets first, then per-endpoint drift.
set -euo pipefail

in_dir="${IN:?IN not set}"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
for doc in old.json new.json; do
  [[ -f $in_dir/$doc ]] || { echo "missing $in_dir/$doc" >&2; exit 1; }
  jq -e 'type == "object"' "$in_dir/$doc" >/dev/null || { echo "$in_dir/$doc is not a JSON object" >&2; exit 1; }
done

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -n --slurpfile old "$in_dir/old.json" --slurpfile new "$in_dir/new.json" '
  def methods: ["get", "put", "post", "delete", "patch", "head", "options"];

  def params($op):
    [ (($op.parameters // []) | .[])
      | select(type == "object")
      | { id: (((.name // "") | tostring) + "\u0001" + ((.in // "") | tostring)),
          required: (.required == true) } ];

  def endpoints($doc):
    [ ((($doc.paths // {}) | to_entries)[] as $p
       | (($p.value // {}) | to_entries)[]
       | .key as $method
       | select(methods | index($method))
       | { path: $p.key,
           method: $method,
           opid: ((.value.operationId // "") | tostring),
           params: params(.value) }) ];

  def find($list; $path; $method):
    ($list | map(select(.path == $path and .method == $method)) | .[0]);

  def codes($before; $after):
    [ (if $before.opid != $after.opid then "operation-id-changed" else empty end),
      ((($after.params | map(select(.required)) | map(.id))
        - ($before.params | map(select(.required)) | map(.id))) as $gained
       | if ($gained | length) > 0 then "required-param-added" else empty end),
      ((($before.params | map(.id)) - ($after.params | map(.id))) as $lost
       | if ($lost | length) > 0 then "param-removed" else empty end)
    ];

  endpoints($old[0]) as $before
  | endpoints($new[0]) as $after
  | ([ $before[] | select(find($after; .path; .method) == null)
       | [ .path, .method, "removed" ] ]
     + [ $after[] | select(find($before; .path; .method) == null)
         | [ .path, .method, "added" ] ]
     + [ $before[] as $e
         | (find($after; $e.path; $e.method)) as $other
         | select($other != null)
         | codes($e; $other)[] as $code
         | [ $e.path, $e.method, $code ] ]) as $rows
  | ($rows | sort_by(.[0], .[1], .[2])) as $sorted
  | { rows: $sorted,
      summary: {
        endpoints_old: ($before | length),
        endpoints_new: ($after | length),
        added: ([$sorted[] | select(.[2] == "added")] | length),
        removed: ([$sorted[] | select(.[2] == "removed")] | length),
        breaking: ([$sorted[] | select(.[2] | IN("removed", "required-param-added", "operation-id-changed"))] | length),
        safe: ([$sorted[] | select(.[2] | IN("added", "param-removed"))] | length),
        changed_endpoints: ([ $before[] as $e
                              | (find($after; $e.path; $e.method)) as $other
                              | select($other != null)
                              | select((codes($e; $other) | length) > 0) ] | length)
      } }
' > "$scratch/result.json"

{
  printf 'path,method,code\n'
  jq -r '.rows[] | @tsv' "$scratch/result.json" | awk -F'\t' '{ printf "%s,%s,%s\n", $1, $2, $3 }'
} > "$out_dir/changes.csv"

jq -c '.summary' "$scratch/result.json" > "$out_dir/summary.json"
