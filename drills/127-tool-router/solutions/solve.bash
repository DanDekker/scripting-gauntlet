#!/usr/bin/env bash
# 127-tool-router - jq parses both files, scores each tool, sorts candidates, picks one.
set -euo pipefail
export LC_ALL=C

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
for f in tools.json requests.jsonl; do
  [[ -f "$indir/$f" ]] || { echo "missing $indir/$f" >&2; exit 1; }
done
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

jq -n --slurpfile cat "$indir/tools.json" --rawfile reqs "$indir/requests.jsonl" '
  def word: test("^[A-Za-z0-9_]+$");
  def hits($text; $kw):
    if ($kw | word)
    then ($text | test("(?<![A-Za-z0-9_])" + $kw + "(?![A-Za-z0-9_])"; "i"))
    else ($text | ascii_downcase | contains($kw | ascii_downcase))
    end;
  def score($tool; $text): [ $tool.keywords[] | select(hits($text; .)) ] | length;
  def available($tool; $ctx):
    [ ($tool.requires // [])[] | select(. as $need | ($ctx | index($need)) == null) ] | length == 0;

  ($cat[0].tools // []) as $tools
  | ($reqs | split("\n")
     | map(gsub("^[ \t\r]+|[ \t\r]+$"; ""))
     | map(select(length > 0))
     | map(try fromjson catch null)
     | map(select(type == "object"))
     | map(select((.id | type) == "string" and (.text | type) == "string"))
     | map({id, text, context: (if (.context | type) == "array" then .context else [] end)})
    ) as $records
  | [ $records[]
      | . as $r
      | ([ $tools[]
           | . as $t
           | (score($t; $r.text)) as $m
           | select($m > 0 and available($t; $r.context))
           | {name: $t.name, matched: $m}
         ] | sort_by([-.matched, .name])) as $ranked
      | if ($ranked | length) > 0
        then {id: $r.id, tool: $ranked[0].name, matched: $ranked[0].matched}
        else {id: $r.id, tool: "", matched: 0} end
    ] as $routes
  | {csv: ($routes | map("\(.id),\(.tool),\(.matched)")),
     summary: {requests: ($routes | length),
               routed: ($routes | map(select(.tool != "")) | length),
               unrouted: ($routes | map(select(.tool == "")) | length),
               by_tool: ($routes | map(select(.tool != "")) | group_by(.tool)
                         | map({key: .[0].tool, value: length}) | from_entries)}}
' > "$outdir/routes.json"

{
  printf 'id,tool,matched\n'
  jq -r '.csv[]' "$outdir/routes.json"
} > "$outdir/routes.csv"
jq -S -c '.summary' "$outdir/routes.json" > "$outdir/summary.json"
rm -f "$outdir/routes.json"
