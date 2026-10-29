#!/usr/bin/env bash
set -euo pipefail

linux="$IN/linux"
macos="$IN/macos"
windows="$IN/windows/computer.json"
out="$OUT"
for path in "$linux/os-release" "$linux/uname.txt" "$linux/hostname.txt" \
  "$macos/sw_vers.txt" "$macos/uname.txt" "$macos/hostname.txt" "$windows"; do
  [[ -r "$path" ]] || { echo "cannot read: $path" >&2; exit 1; }
done

os_value() { awk -F= -v key="$1" '$1 == key {gsub(/^"|"$/, "", $2); print $2; exit}' "$2"; }
mac_value() { awk -F: -v key="$1" '$1 == key {sub(/^[[:space:]]+/, "", $2); print $2; exit}' "$2"; }
normalize_arch() {
  value=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  case "$value" in
    *arm64*|*aarch64*) printf 'arm64' ;;
    *x64*|*amd64*|*x86_64*) printf 'x86_64' ;;
    *) echo "unknown architecture: $1" >&2; return 1 ;;
  esac
}

linux_arch=$(normalize_arch "$(cat "$linux/uname.txt")")
mac_arch=$(normalize_arch "$(cat "$macos/uname.txt")")
win_arch=$(normalize_arch "$(jq -er '.CsSystemType' "$windows")")
{
  printf 'platform,hostname,name,version,architecture\n'
  printf 'linux,%s,%s,%s,%s\n' "$(cat "$linux/hostname.txt")" \
    "$(os_value NAME "$linux/os-release")" "$(os_value VERSION_ID "$linux/os-release")" "$linux_arch"
  printf 'macos,%s,%s,%s,%s\n' "$(cat "$macos/hostname.txt")" \
    "$(mac_value ProductName "$macos/sw_vers.txt")" \
    "$(mac_value ProductVersion "$macos/sw_vers.txt")" "$mac_arch"
  printf 'windows,%s,%s,%s,%s\n' "$(jq -er '.CsName' "$windows")" \
    "$(jq -er '.WindowsProductName' "$windows")" \
    "$(jq -er '.WindowsVersion' "$windows")" "$win_arch"
} | { IFS= read -r header; printf '%s\n' "$header"; LC_ALL=C sort; } > "$out/hosts.csv"
printf '{"platforms":3}\n' > "$out/summary.json"
