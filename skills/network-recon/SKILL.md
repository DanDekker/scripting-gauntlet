---
name: network-recon
description: Find out what is listening, who is connected, whether a port is open, and what the firewall saw — and stand up a listener of your own safely. Use when asked what ports a host has open, which process owns a port, how many connections a peer holds, to scan a port range, to summarise firewall or conntrack events, or to start a local listener that answers a fixed request. Only for hosts you are authorised to inspect.
license: MIT
metadata:
  family: network-recon
  drills: 050-listeners, 051-conn-states, 054-listener-setup, 055-localport-scan, 056-network-events
---

# Network recon

Same shape as system recon: **capture → classify → rank → report**. The extra rule that
matters here is that *a socket is not a process and a port is not a listener* — keep the
concepts apart or you will confidently report the wrong thing.

## Listening sockets

```bash
lsof -nP -iTCP -sTCP:LISTEN        # macOS and Linux, with the pid
netstat -an | grep LISTEN           # BSD; Linux uses `ss -tulpn`
```

`netstat -an` output is a fixed-width table:

```
Proto Recv-Q Send-Q  Local Address          Foreign Address        (state)
tcp4       0      0  127.0.0.1.8080         *.*                    LISTEN
```

The local address is `address.port` with **the port after the last dot** — `127.0.0.1.8080`
is port 8080, and `10.0.0.5.22` is port 22.

Three distinctions that separate a real report from a wrong one:

- **IPv4 and IPv6 on the same port are two listeners, not a conflict.** `*.631` for tcp4
  and `*.631` for tcp6 are the same service.
- **A wildcard binding shadows a specific one.** `*.8080` plus `127.0.0.1.8080` means the
  specific address is unreachable — that is a real finding.
- **`TIME_WAIT` is not a listener.** It is a socket in the process of closing.

Mapping a port to a pid needs `lsof` or `ss -p`, and on Linux it needs privileges for
other users' sockets. Say so rather than guessing.

## Scanning a range

```bash
for port in $(seq 46000 46010); do
  if (exec 3<>/dev/tcp/127.0.0.1/"$port") 2>/dev/null; then
    printf '%s\n' "$port"
  fi
done
```

A **refused** connection means the port is closed — on loopback that is immediate, so you
do not need a long timeout, but you do need one so a hung port cannot stall the range.
Use a short per-port timeout and report how many ports you *attempted*, not just the ones
that answered.

Never scan a range you are not authorised to scan. The drills here stay on `127.0.0.1`.

## Connection states

Count sockets per state, then rank the peers. Strip the port off a remote address at the
**last dot** and drop the `*.*` placeholder. A peer with a high count is a candidate for
something interesting — but check the state before you call it a problem: thousands of
`TIME_WAIT` from one address is a different story from thousands of `ESTABLISHED`.

## Firewall and conntrack events

Event lines are `TIMESTAMP KEY=VALUE ...`. Pull a value with a pattern, not by column
position:

```awk
function val(line, key,   re, s) {
  re = " " key "=[^ ]*"
  if (match(line, re)) { s = substr(line, RSTART, RLENGTH); sub(/^ [^=]*=/, "", s); return s }
  return ""
}
```

- A line missing a required key is **malformed**: skip it and count it. Never default a
  missing `DPT` to 0.
- Fold the verdict to upper case before counting — the log is not consistent.
- `DROP` and `REJECT` are both "blocked"; `ALLOW` is "allowed".

## Standing up your own listener

The lifecycle is the whole lesson:

1. **Bind `127.0.0.1`**, never `0.0.0.0`. A listener on every interface is an accident
   waiting to be a breach.
2. **Background it** and write its pid to a file so the caller can stop it.
3. **Redirect the child's stdout and stderr to a file.** A backgrounded child that
   inherits your stdout holds that pipe open forever, and whoever launched you hangs
   waiting for it to close. This is the single most common way to wedge a launcher.
4. **Exit 0 promptly** — the service outlives the script.
5. **Answer a fixed response** with a correct `Content-Length`.

```bash
python3 responder.py "$PORT" > "$OUT/listener.log" 2>&1 &
echo $! > "$OUT/listener.pid"
```

`nc -l` is not a good server here: it drains its input before accepting and will not
reliably deliver a canned response. Use a real socket.

## Reporting

Say what you scanned, when you captured it, and what you could not see (no privileges,
no `ss`, an IPv6-only host). "9 listeners on loopback, captured 10:04, one shadowed by a
wildcard bind" is the shape of a good answer.

Prove it against `drills/recon/050-listeners`, `051-conn-states`, `054-listener-setup`,
`055-localport-scan`, `056-network-events`.
