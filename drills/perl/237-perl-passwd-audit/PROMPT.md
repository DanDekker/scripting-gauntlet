# 237-perl-passwd-audit

> "We are performing a security and consistency audit across our UNIX servers. We need a
> script to inspect `/etc/passwd` and `/etc/group` copies for duplicate UIDs, non-root accounts
> with UID 0 (root equivalency), primary user GIDs that don't exist in `/etc/group`, and group
> member usernames that don't exist in `/etc/passwd`."

## Input

- `in/passwd` — account database (`username:password:uid:gid:gecos:home:shell`).
- `in/group` — group database (`groupname:password:gid:user_list`).

Empty lines and lines starting with `#` are ignored.

## Rules

1. Parse `in/passwd`:
   - 7 colon-separated fields: `username`, `password`, `uid`, `gid`, `gecos`, `home`, `shell`.
   - `uid` and `gid` are integers.
2. Parse `in/group`:
   - 4 colon-separated fields: `groupname`, `password`, `gid`, `user_list`.
   - `gid` is an integer.
   - `user_list` is a comma-separated list of member usernames. If empty, the group has no secondary members.
3. Detect anomalies in these 4 categories:
   - `ROOT_EQUIV`:
     - Any account in `in/passwd` where `uid == 0` and `username != "root"`.
     - `entity`: `user:<username>`
     - `detail`: `uid 0 assigned to non-root user`
   - `DUPLICATE_UID`:
     - Any UID in `in/passwd` shared by 2 or more distinct accounts.
     - Emit one row for each account having this duplicated UID.
     - `entity`: `user:<username>`
     - `detail`: `uid <uid> is duplicated`
   - `ORPHAN_GID`:
     - Any account in `in/passwd` whose primary `gid` does not exist in `in/group`.
     - `entity`: `user:<username>`
     - `detail`: `gid <gid> not found in group database`
   - `DANGLING_MEMBER`:
     - Any username in a group's `user_list` in `in/group` that does not exist in `in/passwd`.
     - `entity`: `group:<groupname>`
     - `detail`: `member <username> not found in passwd database`
4. **`out/anomalies.tsv`** — tab-separated values (`\t`):
   - Header: `category\tentity\tdetail`
   - Sorted by `category` ascending (`cmp`), then `entity` ascending (`cmp`), then `detail` ascending (`cmp`).
5. **`out/summary.json`** — compact JSON object with keys:
   - `total_users`: count of valid parsed accounts in `in/passwd`.
   - `total_groups`: count of valid parsed groups in `in/group`.
   - `total_anomalies`: number of anomaly rows written to `out/anomalies.tsv`.
   - `root_equiv_users`: count of `ROOT_EQUIV` anomalies.
   - `orphan_gid_users`: count of `ORPHAN_GID` anomalies.
   - `dangling_members`: count of `DANGLING_MEMBER` anomalies.

## Messes to expect

- Lines in `in/group` often have no secondary members (e.g. `root:x:0:`). Naive `split /:/, $line` in Perl drops the trailing empty string, returning 3 fields instead of 4. Use `split /:/, $line, -1`.
- Accounts can trigger multiple anomaly types (e.g. an account with UID 0 other than root has both `ROOT_EQUIV` and `DUPLICATE_UID`).
- Comment lines starting with `#` and blank lines.

## Timebox

Five minutes.

