#!/usr/bin/env python3
"""Rank models across benchmark suites with weighted per-suite normalization."""

import json
import os
import re
from pathlib import Path

SCORE = re.compile(r"^[-+]?([0-9]+\.?[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?$")


def load_results(path):
    """Return (models in first-seen order, {(model, suite): score or None})."""
    models = []
    seen = set()
    scores = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if index == 0:
            continue  # header
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 4:
            continue
        model, suite, raw = fields[0], fields[1], fields[2]
        if not model or not suite:
            continue
        if model not in seen:
            seen.add(model)
            models.append(model)
        scores[(model, suite)] = float(raw) if SCORE.match(raw) else None
    return models, scores


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    weights = json.loads((in_dir / "weights.json").read_text(encoding="utf-8"))
    models, scores = load_results(in_dir / "results.csv")
    suites = list(weights)
    total_weight = sum(config.get("weight", 0) for config in weights.values())

    minimum = {}
    maximum = {}
    for suite in suites:
        values = [scores[(model, suite)] for model in models if scores.get((model, suite)) is not None]
        if values:
            minimum[suite] = min(values)
            maximum[suite] = max(values)

    rows = []
    for model in models:
        if any(scores.get((model, suite)) is None for suite in suites):
            continue
        total = 0.0
        for suite in suites:
            score = scores[(model, suite)]
            low, high = minimum[suite], maximum[suite]
            if high == low:
                norm = 1.0
            elif weights[suite].get("higher_is_better", True):
                norm = (score - low) / (high - low)
            else:
                norm = (high - score) / (high - low)
            total += norm * weights[suite].get("weight", 0)
        composite = 0.0 if total_weight == 0 else total / total_weight
        rows.append((float(f"{composite:.4f}"), model))

    rows.sort(key=lambda row: (-row[0], row[1]))

    lines = ["rank,model,composite_score"]
    for rank, (composite, model) in enumerate(rows, start=1):
        lines.append(f"{rank},{model},{composite:.4f}")
    (out_dir / "leaderboard.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "total_models": len(models),
        "complete_models": len(rows),
        "incomplete_models": len(models) - len(rows),
        "top_model": rows[0][1] if rows else "",
        "winning_score": float(f"{rows[0][0]:.4f}") if rows else 0.0,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
