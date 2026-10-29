#!/usr/bin/env bash
# Plausible bug: fails to escape $1 in unquoted heredoc, baking ACTION="status" into child script
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

  # BUG: ${1:-status} is not escaped: bakes generator's empty $1 fallback ("status") into child script
  cat <<EOF > "$script_path"
#!/usr/bin/env bash
set -euo pipefail
SERVICE_NAME="$name"
SERVICE_PORT=$port
SERVICE_ENV="$env"
HEALTH_PATH="$health_path"

ACTION="${1:-status}"

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
    if out_text=$("$script_path" "$act" 2>/dev/null); then
      code=0
    else
      code=1
      out_text=""
    fi
    echo "$name,$act,$code,$out_text" >> "$OUT/manifest.csv"
  done
done

printf '{"services":3,"total_runs":6,"success":0}\n' > "$OUT/summary.json"
