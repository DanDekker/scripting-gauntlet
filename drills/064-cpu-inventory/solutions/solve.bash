#!/usr/bin/env bash
set -euo pipefail

linux="$IN/linux/lscpu.txt"
macos="$IN/macos/sysctl.txt"
windows="$IN/windows/system.json"
for path in "$linux" "$macos" "$IN/macos/uname.txt" "$windows"; do
  [[ -r "$path" ]] || { echo "cannot read: $path" >&2; exit 1; }
done
field() { awk -F: -v key="$1" '{left=$1; sub(/^[[:space:]]+/, "", left); sub(/[[:space:]]+$/, "", left); if (left == key) {sub(/^[[:space:]]+/, "", $2); print $2; exit}}' "$2"; }
normalize_arch() {
  value=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  case "$value" in
    *arm64*|*aarch64*) printf 'arm64' ;;
    *x64*|*amd64*|*x86_64*) printf 'x86_64' ;;
    *) echo "unknown architecture: $1" >&2; return 1 ;;
  esac
}

linux_cores=$(($(field 'Core(s) per socket' "$linux") * $(field 'Socket(s)' "$linux")))
linux_threads=$(field 'CPU(s)' "$linux")
linux_arch=$(normalize_arch "$(field Architecture "$linux")")
mac_cores=$(field hw.physicalcpu "$macos")
mac_threads=$(field hw.logicalcpu "$macos")
mac_arch=$(normalize_arch "$(cat "$IN/macos/uname.txt")")
win_cores=$(jq -er '[.processors[].NumberOfCores] | add' "$windows")
win_threads=$(jq -er '[.processors[].NumberOfLogicalProcessors] | add' "$windows")
win_arch=$(normalize_arch "$(jq -er '.CsSystemType' "$windows")")

{
  printf 'platform,processor,physical_cores,logical_cpus,threads_per_core,architecture\n'
  printf 'linux,%s,%d,%d,%d,%s\n' "$(field 'Model name' "$linux")" \
    "$linux_cores" "$linux_threads" "$((linux_threads / linux_cores))" "$linux_arch"
  printf 'macos,%s,%d,%d,%d,%s\n' "$(field machdep.cpu.brand_string "$macos")" \
    "$mac_cores" "$mac_threads" "$((mac_threads / mac_cores))" "$mac_arch"
  printf 'windows,%s,%d,%d,%d,%s\n' "$(jq -er '.processors[0].Name' "$windows")" \
    "$win_cores" "$win_threads" "$((win_threads / win_cores))" "$win_arch"
} | { IFS= read -r header; printf '%s\n' "$header"; LC_ALL=C sort; } > "$OUT/cpus.csv"
printf '{"hosts":3,"physical_cores":%d,"logical_cpus":%d}\n' \
  "$((linux_cores + mac_cores + win_cores))" "$((linux_threads + mac_threads + win_threads))" \
  > "$OUT/summary.json"
