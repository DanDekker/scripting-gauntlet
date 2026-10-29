#!/usr/bin/env bash
# Exact cosine top-K in awk, then recall/MRR against the ANN rows.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# D comes from the first usable query record.
dim=$(jq -R -r '
  fromjson? | select(type == "object" and has("qid") and ((.vec | type) == "array"))
  | (.vec | length)' "$in_dir/queries.jsonl" | head -n 1)
[ -n "$dim" ] || { echo "143: no usable query in queries.jsonl" >&2; exit 1; }

jq -R -r '
  fromjson? | select(type == "object" and has("id") and ((.vec | type) == "array"))
  | [(.id | tostring), (.vec | map(tostring) | join(","))] | @tsv
' "$in_dir/corpus.jsonl" > "$scratch/corpus.tsv"

jq -R -r '
  fromjson? | select(type == "object" and has("qid") and ((.vec | type) == "array"))
  | [(.qid | tostring), (.vec | map(tostring) | join(","))] | @tsv
' "$in_dir/queries.jsonl" > "$scratch/queries.tsv"

corpus_size=$(awk -F'\t' -v d="$dim" '$1 != "" { n = split($2, v, ","); if (n == d) c++ } END { print c + 0 }' \
  "$scratch/corpus.tsv")

# Scored queries: right dimension, in qid order.
awk -F'\t' -v d="$dim" '$1 != "" { n = split($2, v, ","); if (n == d) print $1 }' \
  "$scratch/queries.tsv" | sort -u > "$scratch/qids.txt"

# All (qid, similarity, doc_id) triples for the surviving corpus.
awk -F'\t' -v d="$dim" '
  FNR == NR {
    if ($1 == "") next
    n = split($2, comp, ",")
    if (n != d) next
    ndocs++
    docid[ndocs] = $1
    s = 0
    for (i = 1; i <= n; i++) { x = comp[i] + 0; vec[$1, i] = x; s += x * x }
    dnorm[$1] = sqrt(s)
    next
  }
  {
    n = split($2, comp, ",")
    if (n != d) next
    qid = $1
    s = 0
    for (i = 1; i <= n; i++) { qv[i] = comp[i] + 0; s += qv[i] * qv[i] }
    qnorm = sqrt(s)
    for (j = 1; j <= ndocs; j++) {
      id = docid[j]
      if (qnorm == 0 || dnorm[id] == 0) {
        sim = 0
      } else {
        dot = 0
        for (i = 1; i <= n; i++) dot += qv[i] * vec[id, i]
        sim = dot / (qnorm * dnorm[id])
      }
      printf "%s\t%.17g\t%s\n", qid, sim, id
    }
  }
' "$scratch/corpus.tsv" "$scratch/queries.tsv" | sort -t $'\t' -k1,1 -k2,2gr -k3,3 > "$scratch/sims.tsv"

# ANN rows, ordered by qid then rank.
awk -F, 'NR > 1 {
  qid = $1; rank = $2; doc = $3
  gsub(/^[ \t\r]+|[ \t\r]+$/, "", qid)
  gsub(/^[ \t\r]+|[ \t\r]+$/, "", rank)
  gsub(/^[ \t\r]+|[ \t\r]+$/, "", doc)
  if (qid == "" || doc == "" || rank !~ /^[0-9]+$/) next
  printf "%s\t%d\t%s\n", qid, rank, doc
}' "$in_dir/ann_results.csv" | sort -t $'\t' -k1,1 -k2,2n > "$scratch/ann.tsv"

awk -F'\t' -v corpus_size="$corpus_size" -v sumfile="$scratch/summary.tsv" '
  FILENAME ~ /qids/ {
    nq++
    order[nq] = $1
    wanted[$1] = 1
    next
  }
  FILENAME ~ /sims/ { gtn[$1]++; gtdoc[$1, gtn[$1]] = $3; next }
  {
    q = $1
    if (!(q in wanted)) next
    annk[q]++
    adoc[q, annk[q]] = $3
    arank[q, annk[q]] = $2 + 0
  }
  END {
    scored = 0; sumr = 0; summ = 0
    for (x = 1; x <= nq; x++) {
      q = order[x]
      K = annk[q]
      if (K == 0) continue
      for (i = 1; i <= K; i++) gtset[q, gtdoc[q, i]] = 1
      hits = 0
      rr = 0
      for (i = 1; i <= K; i++) {
        if ((q SUBSEP adoc[q, i]) in gtset) {
          hits++
          if (rr == 0) rr = 1.0 / arank[q, i]
        }
      }
      recall = hits / K
      sumr += recall; summ += rr
      scored++
      printf "%s,%d,%d,%.4f,%.4f\n", q, K, hits, recall, rr
    }
    printf "%d\t%d\t%.4f\t%.4f\n", scored, corpus_size, (scored ? sumr / scored : 0), (scored ? summ / scored : 0) > sumfile
  }
' "$scratch/qids.txt" "$scratch/sims.tsv" "$scratch/ann.tsv" > "$scratch/metrics.csv"

{
  printf 'qid,k,hits,recall,mrr\n'
  cat "$scratch/metrics.csv"
} > "$out_dir/metrics.csv"

IFS=$'\t' read -r scored corpus_size avg_recall mean_mrr < "$scratch/summary.tsv"
printf '{\n  "queries": %d,\n  "corpus_size": %d,\n  "avg_recall": %s,\n  "mean_mrr": %s\n}\n' \
  "$scored" "$corpus_size" "$avg_recall" "$mean_mrr" > "$out_dir/summary.json"
