# 143-vector-search-eval

> "Our vector store claims 5-recall at 5. I want the honest number: compute exact cosine
> top-K over the same corpus, compare it against what the ANN actually returned, and give
> me recall and MRR per query."

## Input

- `in/corpus.jsonl` — documents: `{"id": "doc1", "vec": [0.1, 0.2, 0.3, 0.4]}`, one JSON
  object per line.
- `in/queries.jsonl` — queries: `{"qid": "q1", "vec": [0.15, 0.25, 0.35, 0.4]}`.
- `in/ann_results.csv` — header `qid,rank,doc_id`; the ANN's top-K for each query, `rank`
  being 1-based.

Records without a `vec` array, lines that are not JSON, lines that are JSON but not an
object, and blank lines are skipped.

## Rules

1. **Dimension.** `D` is the length of `vec` in the **first** query object of
   `queries.jsonl`. Any query or document whose `vec` length is not exactly `D` is dropped
   from the evaluation entirely.
2. **Cosine similarity.** `sim(u, v) = dot(u, v) / (norm(u) * norm(v))`, with
   `norm(x) = sqrt(sum(x_i^2))`. If either norm is `0`, the similarity is `0.0` — a zero
   vector never divides by zero and never matches anything.
3. **Ground truth.** For a query, rank every surviving corpus document by similarity
   **descending**, ties broken by `doc_id` **ascending** (plain string order), and keep the
   first `K`, where `K` is the number of ANN rows for that `qid` in `ann_results.csv`.
   Rank the documents using the **unrounded** similarity.
4. **Compare.** Let `ANN` be that query's rows ordered by `rank` ascending.
   - `hits` — how many doc_ids in `ANN` also appear in the ground-truth top-K.
   - `recall` — `hits / K`.
   - `mrr` — `1 / rank` of the **first** hit in `ANN` order, or `0.0` when there is no hit.

### Which queries are scored

A query is scored only when its `vec` length is `D` **and** at least one ANN row exists for
its `qid`. ANN rows whose `qid` is not a scored query are ignored. With no ANN rows there
is no `K`, so the query produces no metrics row.

## Output

Write exactly these files to `$OUT`:

1. **`out/metrics.csv`** — header `qid,k,hits,recall,mrr`. One row per scored query,
   sorted by `qid` ascending. `k`, `hits` are integers. `recall` and `mrr` are printed with
   exactly four decimals (`0.6667`, `1.0000`, `0.0000`).
2. **`out/summary.json`** — object with exactly these keys:
   - `queries` — number of scored queries (int)
   - `corpus_size` — number of documents that survived the dimension check (int)
   - `avg_recall` — mean of the per-query `recall` values, computed from the unrounded
     ratios, printed with four decimals
   - `mean_mrr` — mean of the per-query `mrr` values, four decimals

   Both floats are JSON numbers written with exactly four decimals, e.g. `0.7500`.

## Messes to expect

- `d2` is `d1` scaled by 2 and `d9` by 3: same direction, so `q1`'s top-3 is a three-way
  tie at `1.0` broken by doc id -> `d1`, `d2`, `d9` (not the ANN's order)
- `d5` is the zero vector and `q4` is a zero query: every similarity is `0.0`, so `q4`'s
  top-2 is just the two smallest doc ids, `d1` and `d2`
- `d8` has 5 components and `d10` has 3, so both are dropped; `qbad` has 3 components, so
  it is dropped and its three ANN rows are ignored
- `d7` is `[0.6, 0, 0.8, 0]`, whose *unit* direction is what matters, not its magnitude
- `d12` is `[0.5, 0.5, 0.5, 0.5]` and scores the *same* `0.7071…` as `d4` against `q3`, so
  the tie-break decides the order: `d12` sorts before `d4` (`"d12" < "d4"` as strings),
  which makes `q3`'s true top-1 a document the ANN never returned
- a document id missing from the ANN list is a miss, not an error: `q1`'s ANN returns
  `d6`, which is not in its top-3
- `q4,2,d1  ` has trailing spaces, and the file ends with a blank line

## Timebox

About five minutes. If you are past that, the approach is wrong.
