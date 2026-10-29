#!/usr/bin/env python3
"""196-bash-heredoc-expansion — python twin generating runner scripts."""

import csv
import json
import os
import subprocess
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

services = []
with (IN / "services.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        services.append(row)

results = []
success_count = 0

for svc in services:
    name = svc["name"].strip()
    port = svc["port"].strip()
    env = svc["env"].strip()
    health_path = svc["health_path"].strip()

    script_path = OUT / f"{name}_runner.sh"
    script_content = f"""#!/usr/bin/env bash
set -euo pipefail
SERVICE_NAME="{name}"
SERVICE_PORT={port}
SERVICE_ENV="{env}"
HEALTH_PATH="{health_path}"

ACTION="${{1:-status}}"

case "$ACTION" in
  start)
    echo "Starting $SERVICE_NAME in $SERVICE_ENV on port $SERVICE_PORT..."
    ;;
  check)
    echo "Checking health at http://127.0.0.1:$SERVICE_PORT$HEALTH_PATH"
    ;;
  *)
    exit 1
    ;;
esac
"""
    script_path.write_text(script_content, encoding="utf-8")
    script_path.chmod(0o755)

    for action in ("start", "check"):
        proc = subprocess.run([str(script_path), action], capture_output=True, text=True)
        code = proc.returncode
        output = proc.stdout.strip()
        if code == 0:
            success_count += 1
        results.append((name, action, code, output))

with (OUT / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("service,action,exit_code,output\n")
    for r in results:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"services": len(services), "total_runs": len(results), "success": success_count},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
