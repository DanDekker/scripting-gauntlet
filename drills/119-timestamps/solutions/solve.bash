#!/usr/bin/env bash
# 119-timestamps - awk parses six formats to epoch seconds, sorts, then formats back.
set -euo pipefail

in_dir="${IN:?IN not set}"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"

log="$in_dir/entries.log"
[[ -f "$log" ]] || { echo "missing $log" >&2; exit 1; }

awk -v outdir="$out_dir" '
  function isspace(ch) { return ch == " " || ch == "\t" }
  function isdigits(s, len,   k, ch) {
    if (length(s) != len) return 0
    for (k = 1; k <= len; k++) {
      ch = substr(s, k, 1)
      if (ch < "0" || ch > "9") return 0
    }
    return 1
  }
  function strip(s) { sub(/[ \t]+$/, "", s); return s }

  function fdiv(a, b,   q) { q = int(a / b); if (q * b > a) q--; return q }

  function days_from_civil(y, m, d,   era, yoe, doy, doe) {
    if (m <= 2) y = y - 1
    era = int(y / 400)
    yoe = y - era * 400
    doy = int((153 * (m + ((m > 2) ? -3 : 9)) + 2) / 5) + d - 1
    doe = yoe * 365 + int(yoe / 4) - int(yoe / 100) + doy
    return era * 146097 + doe - 719468
  }

  function civil_from_days(z,   era, doe, yoe, y, doy, mp, d, m) {
    z = z + 719468
    era = int(z / 146097)
    doe = z - era * 146097
    yoe = int((doe - int(doe / 1460) + int(doe / 36524) - int(doe / 146096)) / 365)
    y = yoe + era * 400
    doy = doe - (365 * yoe + int(yoe / 4) - int(yoe / 100))
    mp = int((5 * doy + 2) / 153)
    d = doy - int((153 * mp + 2) / 5) + 1
    m = mp + ((mp < 10) ? 3 : -9)
    if (m <= 2) y = y + 1
    CY = y; CM = m; CD = d
  }

  function stamp(e,   days, secs) {
    days = fdiv(e, 86400)
    secs = e - days * 86400
    civil_from_days(days)
    return sprintf("%04d-%02d-%02dT%02d:%02d:%02dZ", CY, CM, CD, int(secs / 3600), int((secs % 3600) / 60), secs % 60)
  }

  function csvfield(s) {
    if (s ~ /[,"]/) { gsub(/"/, "\"\"", s); return "\"" s "\"" }
    return s
  }

  function inrange(y, mo, d, h, mi, s) {
    return (mo >= 1 && mo <= 12 && d >= 1 && d <= 31 && h >= 0 && h <= 23 && mi >= 0 && mi <= 59 && s >= 0 && s <= 59)
  }

  function hms_ok(line, p) {
    return (substr(line, p, 2) != "" && isdigits(substr(line, p, 2), 2) &&
            substr(line, p + 2, 1) == ":" && isdigits(substr(line, p + 3, 2), 2) &&
            substr(line, p + 5, 1) == ":" && isdigits(substr(line, p + 6, 2), 2))
  }

  function parse(line,   L, p, mm, nd, i, c, z, off, sign, start, y, mo, d, h, mi, s, oh, omn) {
    L = length(line)
    mm = tolower(substr(line, 1, 3))
    if (mm in MNAME) {
      if (substr(line, 4, 1) != " ") return 0
      p = 4
      while (substr(line, p, 1) == " ") p++
      i = p
      while (i <= L && substr(line, i, 1) >= "0" && substr(line, i, 1) <= "9") i++
      nd = i - p
      if (nd < 1 || nd > 2) return 0
      d = substr(line, p, nd) + 0
      if (substr(line, i, 1) != " ") return 0
      p = i + 1
      if (!hms_ok(line, p)) return 0
      h = substr(line, p, 2) + 0
      mi = substr(line, p + 3, 2) + 0
      s = substr(line, p + 6, 2) + 0
      p = p + 8
      if (substr(line, p, 1) != " ") return 0
      p++
      if (!isdigits(substr(line, p, 4), 4)) return 0
      y = substr(line, p, 4) + 0
      p = p + 4
      if (p > L) return 0
      if (!isspace(substr(line, p, 1))) return 0
      if (!inrange(y, MNAME[mm], d, h, mi, s)) return 0
      EPOCH = days_from_civil(y, MNAME[mm], d) * 86400 + h * 3600 + mi * 60 + s
      MSG = strip(substr(line, p + 1))
      return 1
    }

    c = substr(line, 1, 1)
    if (c != "-" && (c < "0" || c > "9")) return 0

    if (isdigits(substr(line, 1, 4), 4) && (substr(line, 5, 1) == "-" || substr(line, 5, 1) == "/") &&
        isdigits(substr(line, 6, 2), 2) && substr(line, 8, 1) == substr(line, 5, 1) &&
        isdigits(substr(line, 9, 2), 2)) {
      y = substr(line, 1, 4) + 0
      mo = substr(line, 6, 2) + 0
      d = substr(line, 9, 2) + 0
      c = substr(line, 11, 1)
      if (c == "T") {
        if (!hms_ok(line, 12)) return 0
        h = substr(line, 12, 2) + 0
        mi = substr(line, 15, 2) + 0
        s = substr(line, 18, 2) + 0
        p = 20
        if (substr(line, p, 1) == ".") {
          p++
          while (p <= L && substr(line, p, 1) >= "0" && substr(line, p, 1) <= "9") p++
        }
        z = substr(line, p, 1)
        off = 0
        if (z == "Z") p++
        else if (z == "+" || z == "-") {
          if (!isdigits(substr(line, p + 1, 2), 2)) return 0
          if (substr(line, p + 3, 1) != ":") return 0
          if (!isdigits(substr(line, p + 4, 2), 2)) return 0
          oh = substr(line, p + 1, 2) + 0
          omn = substr(line, p + 4, 2) + 0
          off = oh * 3600 + omn * 60
          if (z == "-") off = -off
          p = p + 6
        } else return 0
        if (p > L) return 0
        if (!isspace(substr(line, p, 1))) return 0
        if (!inrange(y, mo, d, h, mi, s)) return 0
        EPOCH = days_from_civil(y, mo, d) * 86400 + h * 3600 + mi * 60 + s - off
        MSG = strip(substr(line, p + 1))
        return 1
      } else if (c == " ") {
        if (!hms_ok(line, 12)) return 0
        h = substr(line, 12, 2) + 0
        mi = substr(line, 15, 2) + 0
        s = substr(line, 18, 2) + 0
        p = 20
        if (p > L) return 0
        if (!isspace(substr(line, p, 1))) return 0
        if (!inrange(y, mo, d, h, mi, s)) return 0
        EPOCH = days_from_civil(y, mo, d) * 86400 + h * 3600 + mi * 60 + s
        MSG = strip(substr(line, p + 1))
        return 1
      }
      return 0
    }

    p = 1; sign = 1
    if (substr(line, 1, 1) == "-") { sign = -1; p = 2 }
    start = p
    while (p <= L && substr(line, p, 1) >= "0" && substr(line, p, 1) <= "9") p++
    if (p - start < 1) return 0
    if (p > L) return 0
    if (!isspace(substr(line, p, 1))) return 0
    EPOCH = sign * (substr(line, start, p - start) + 0)
    MSG = strip(substr(line, p + 1))
    return 1
  }

  BEGIN {
    split("jan feb mar apr may jun jul aug sep oct nov dec", names, " ")
    for (k = 1; k <= 12; k++) MNAME[names[k]] = k
  }
  {
    line = $0
    sub(/\r$/, "", line)
    if (line ~ /^[ \t]*$/) next
    nonblank++
    if (parse(line)) { cnt++; epo[cnt] = EPOCH; msg[cnt] = MSG }
    else skipped++
  }
  END {
    for (a = 2; a <= cnt; a++) {
      ke = epo[a]; km = msg[a]; b = a - 1
      while (b >= 1 && epo[b] > ke) { epo[b + 1] = epo[b]; msg[b + 1] = msg[b]; b-- }
      epo[b + 1] = ke; msg[b + 1] = km
    }
    print "timestamp,message" > (outdir "/entries.csv")
    for (k = 1; k <= cnt; k++) print stamp(epo[k]) "," csvfield(msg[k]) > (outdir "/entries.csv")
    first = (cnt > 0) ? stamp(epo[1]) : ""
    last = (cnt > 0) ? stamp(epo[cnt]) : ""
    printf "{\"lines\":%d,\"parsed\":%d,\"skipped\":%d,\"first\":\"%s\",\"last\":\"%s\"}\n", nonblank, cnt, skipped, first, last
  }
' "$log" > "$out_dir/summary.json"
