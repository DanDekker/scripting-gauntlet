#!/usr/bin/env bash
# 010-json-flatten — jq paths, tsv in the middle, csv out.
set -euo pipefail

src="${IN:?IN not set}/catalog.json"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

jq -r '.products[]
  | [.sku, .name, (.price | tostring), .specs.material, (.specs.weight | tostring), (.tags | join("|"))]
  | @tsv' "$src" \
  | sort -t$'\t' -k1,1 \
  | awk -F'\t' 'BEGIN { OFS = ","; print "sku,name,price,material,weight,tags" }
       { printf "%s,%s,%s,%s,%s,%s\n", $1, $2, $3, $4, $5, $6 }' \
  > "$outdir/flat.csv"

jq '{generated: .generated, count: (.products | length)}' "$src" > "$outdir/meta.json"
