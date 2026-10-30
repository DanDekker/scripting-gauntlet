# 236-perl-auth-fail2ban

> "Our edge bastion's fail2ban daemon crashed, and we need an emergency triage script.
> We need to parse `/var/log/auth.log` for failed SSH passwords, tally attempts per IP,
> track which usernames were targeted, and produce a ban list of abusive IPs."

## Input

`in/auth.log` — SSH daemon syslog entries.

Example lines:
```text
Oct 30 08:12:00 host sshd[100]: Server listening on 0.0.0.0 port 22.
Oct 30 08:12:05 host sshd[102]: Accepted publickey for alice from 192.168.1.100 port 50201 ssh2
Oct 30 08:12:20 host sshd[106]: Failed password for root from 192.168.1.50 port 38100 ssh2
Oct 30 08:12:22 host sshd[107]: Failed password for admin from 192.168.1.50 port 38101 ssh2
Oct 30 08:12:24 host sshd[108]: Failed password for invalid user deployer from 192.168.1.50 port 38102 ssh2
Oct 30 08:12:26 host sshd[109]: Failed password for root from 192.168.1.50 port 38103 ssh2
Oct 30 08:12:30 host sshd[110]: Failed password for invalid user oracle from 10.0.0.25 port 41001 ssh2
```

Empty lines and lines starting with `#` are ignored. Non-matching lines (like successful logins, server startup, or connection closures) must be ignored.

## Rules

1. Only lines containing `Failed password for ...` represent failed attempts:
   - Pattern matches `Failed password for (?:invalid user )?(\S+) from (\S+) port (\d+)`.
   - The targeted username is the token directly before `from` (excluding `invalid user ` prefix).
   - If the log line says `invalid user deployer`, the user is `deployer`, **not** `invalid`.
   - Extract the remote IP address (the token immediately following `from`).
2. Track metrics per IP:
   - Total number of failed attempts (`failures`).
   - Distinct usernames targeted from this IP.
3. Ban criteria:
   - Any IP with `failures >= 3` is banned.
4. **`out/bans.tsv`** — tab-separated values (`\t`) for banned IPs:
   - Header: `ip\tfailures\tunique_users\tusers`
   - `ip`: client IP address.
   - `failures`: total count of failed password attempts for this IP.
   - `unique_users`: integer count of distinct usernames targeted by this IP.
   - `users`: comma-separated list of distinct usernames targeted, sorted alphabetically (`cmp`).
   - Sort rows by `failures` **descending** numerically (`<=>`); break ties by `ip` **ascending** in ASCII order (`cmp`).
5. **`out/summary.json`** — compact JSON object with keys:
   - `total_failed_events`: total number of failed password events across all IPs.
   - `unique_ips`: count of distinct IPs that had at least one failed password attempt.
   - `banned_ips`: count of banned IPs (written to `out/bans.tsv`).
   - `top_target_user`: the username targeted in the most failed password attempts across all IPs. Ties broken alphabetically (`cmp`).

## Messes to expect

- `invalid user <user>` lines: naive regex `/Failed password for (\S+)/` captures the literal word `"invalid"` instead of the actual targeted account.
- Non-failed log entries (public key auth, session open, server start, connection drops) interspersed throughout the log.
- Numeric vs string sorting: sorting failure counts with `cmp` places "10" before "3".

## Timebox

Five minutes.

