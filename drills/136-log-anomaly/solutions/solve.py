#!/usr/bin/env python3
"""Flag error-rate spikes against a ratio-of-sums baseline and name the culprit."""

import json
import os
from pathlib import Path


def load_minutes(path):
    """(minute, requests, errors, culprit) per parsable row, in file order."""
    minutes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.split(",")]
        if len(cells) < 3 or not cells[0] or cells[0] == "minute":
            continue
        try:
            requests = int(cells[1])
            errors = int(cells[2])
        except ValueError:
            continue
        if requests < 0 or errors < 0:
            continue
        minutes.append(
            {
                "minute": cells[0],
                "requests": requests,
                "errors": errors,
                "culprit": cells[3].strip() if len(cells) > 3 else "",
            }
        )
    return minutes


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    thresholds = json.loads((in_dir / "thresholds.json").read_text(encoding="utf-8"))
    window = int(thresholds["window"])
    min_requests = int(thresholds["min_requests"])
    multiplier = float(thresholds["rate_multiplier"])
    min_rate = float(thresholds["min_rate"])

    minutes = load_minutes(in_dir / "traffic.csv")

    history = []
    anomalies = []
    evaluated = 0
    for index, row in enumerate(minutes):
        requests = row["requests"]
        errors = row["errors"]
        rate = errors / requests if requests else 0.0
        if index >= window and requests >= min_requests:
            evaluated += 1
            past = history[index - window:index]
            window_requests = sum(item["requests"] for item in past)
            window_errors = sum(item["errors"] for item in past)
            baseline = window_errors / window_requests if window_requests else 0.0
            if rate >= min_rate and rate >= baseline * multiplier:
                anomalies.append(
                    {
                        "minute": row["minute"],
                        "requests": requests,
                        "errors": errors,
                        "error_rate": rate,
                        "baseline_rate": baseline,
                        "culprit": row["culprit"] or "Unknown",
                    }
                )
        history.append(row)

    lines = ["minute,requests,errors,error_rate,baseline_rate,culprit"]
    for row in anomalies:
        lines.append(
            ",".join(
                [
                    row["minute"],
                    str(row["requests"]),
                    str(row["errors"]),
                    f"{row['error_rate']:.4f}",
                    f"{row['baseline_rate']:.4f}",
                    row["culprit"],
                ]
            )
        )
    (out_dir / "anomalies.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    counts = {}
    for row in anomalies:
        counts[row["culprit"]] = counts.get(row["culprit"], 0) + 1
    top_culprit = ""
    if counts:
        top_culprit = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]

    summary = {
        "total_minutes": len(minutes),
        "evaluated_minutes": evaluated,
        "anomaly_minutes": len(anomalies),
        "top_culprit": top_culprit,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
