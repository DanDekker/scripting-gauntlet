#!/usr/bin/env python3
"""Score an ANN result set against brute-force cosine ground truth."""

import csv
import json
import math
import os
from pathlib import Path


class Query:
    def __init__(self, key, vec):
        self.key = key
        self.vec = vec
        self.norm = math.sqrt(sum(x * x for x in vec))


def load_vectors(path, key_name):
    """Yield (key, vector) for every usable record, in file order."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        vec = record.get("vec")
        key = record.get(key_name)
        if key is None or not isinstance(vec, list) or not vec:
            continue
        try:
            values = [float(x) for x in vec]
        except (TypeError, ValueError):
            continue
        out.append((str(key), values))
    return out


def cosine(a, b, norm_a, norm_b):
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


def load_ann(path):
    rows = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for raw in reader:
            cells = [cell.strip() for cell in raw]
            if len(cells) != 3 or not any(cells):
                continue
            qid, rank_raw, doc_id = cells
            try:
                rank = int(rank_raw)
            except ValueError:
                continue
            if not qid or not doc_id:
                continue
            rows.setdefault(qid, []).append((rank, doc_id))
    for qid in rows:
        rows[qid].sort(key=lambda row: row[0])
    return rows


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    queries = load_vectors(in_dir / "queries.jsonl", "qid")
    docs = load_vectors(in_dir / "corpus.jsonl", "id")
    ann = load_ann(in_dir / "ann_results.csv")

    dim = len(queries[0][1]) if queries else 0
    queries = [(key, vec) for key, vec in queries if len(vec) == dim]
    docs = [(key, vec) for key, vec in docs if len(vec) == dim]

    corpus = [Query(key, vec) for key, vec in docs]

    rows = []
    recall_sum = 0.0
    mrr_sum = 0.0
    for qid, vec in sorted(queries, key=lambda item: item[0]):
        hits_rows = ann.get(qid)
        if not hits_rows:
            continue
        top_k = len(hits_rows)
        query = Query(qid, vec)
        ranked = sorted(
            corpus,
            key=lambda doc: (-cosine(query.vec, doc.vec, query.norm, doc.norm), doc.key),
        )
        truth = {doc.key for doc in ranked[:top_k]}

        hits = 0
        mrr = 0.0
        for rank, doc_id in hits_rows:
            if doc_id in truth:
                hits += 1
                if mrr == 0.0:
                    mrr = 1.0 / rank

        recall = hits / top_k
        recall_sum += recall
        mrr_sum += mrr
        rows.append((qid, top_k, hits, f"{recall:.4f}", f"{mrr:.4f}"))

    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["qid", "k", "hits", "recall", "mrr"])
        for row in rows:
            writer.writerow(row)

    count = len(rows)
    avg_recall = recall_sum / count if count else 0.0
    mean_mrr = mrr_sum / count if count else 0.0
    summary = (
        "{\n"
        f'  "queries": {count},\n'
        f'  "corpus_size": {len(corpus)},\n'
        f'  "avg_recall": {avg_recall:.4f},\n'
        f'  "mean_mrr": {mean_mrr:.4f}\n'
        "}\n"
    )
    (out_dir / "summary.json").write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
