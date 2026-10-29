#!/usr/bin/env bash
# 196-bash-heredoc-expansion — mixed template generation escaping runtime variables
set -euo pipefail

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

echo "service,action,exit_code,output" > "$OUT/manifest.csv"

tail -n +2 "$IN/services.csv" | while IFS=',' read -r name port env health_path; do
  [[ -z "$name" ]] && continue
  name="${name//[$'\r\n ']/}"
  port="${port//[$'\r\n ']/}"
  env="${env//[$'\r\n ']/}"
  health_path="${health_path//[$'\r\n ']/}"

  script_path="$OUT/${name}_runner.sh"

  cat <<EOF > "$script_path"
#!/usr/bin/env bash
set -euo pipefail
SERVICE_NAME="$name"
SERVICE_PORT=$port
SERVICE_ENV="$env"
HEALTH_PATH="$health_path"

ACTION="\${1:-status}"

case "\$ACTION" in
  start)
    echo "Starting \$SERVICE_NAME in \$SERVICE_ENV on port \$SERVICE_PORT..."
    ;;
  check)
    echo "Checking health at http://127.0.0.1:\$SERVICE_PORT\$HEALTH_PATH"
    ;;
  *)
    exit 1
    ;;
esac
EOF
  chmod +x "$script_path"

  for act in start check; do
    out_text=$("$script_path" "$act")
    echo "$name,$act,0,$out_text" >> "$OUT/manifest.csv"
  done
done

total_runs=$(tail -n +2 "$OUT/manifest.csv" | wc -l | tr -d ' ')
services_count=$(( total_runs / 2 ))
success_count=$(grep -c ',0,' "$OUT/manifest.csv" || true)

printf '{"services":%d,"total_runs":%d,"success":%d}\n' \
  "$services_count" "$total_runs" "$success_count" > "$OUT/summary.json"
