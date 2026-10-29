# 063-os-fingerprint

> "These snapshots came from three different fleets. Put the OS identity in one table
> so our inventory job doesn't care what platform produced it."

## Task

`in/linux/`, `in/macos/`, and `in/windows/` contain saved output from native OS checks:

- Linux: `/etc/os-release`, `uname -m`, and `hostname`
- macOS: `sw_vers`, `uname -m`, and `hostname`
- Windows: selected `Get-ComputerInfo` fields saved as JSON

Read all three snapshots and normalize them.

## Rules

1. Use `Ubuntu` and `24.04` from Linux `NAME` and `VERSION_ID`.
2. Use `ProductName` and `ProductVersion` from macOS `sw_vers`.
3. Use `WindowsProductName` and `WindowsVersion` from the Windows JSON.
4. Normalize `x64`, `x86_64`, and `AMD64` to `x86_64`; normalize `arm64` and
   `aarch64` to `arm64`. The Windows `CsSystemType` field identifies its architecture.
5. Sort records by `platform` ascending in byte order.

## Output

**`out/hosts.csv`** — header `platform,hostname,name,version,architecture`, one row per
snapshot, sorted by `platform`.

**`out/summary.json`** — exactly `platforms`, the number of records written.

## Messes to expect

- Linux uses key/value lines with optional quotes
- macOS `sw_vers` uses colon-separated fields
- Windows has different property names and architecture wording
- all version and hostname fields are strings

## Timebox

4 minutes. These are captured outputs, so the same solution works on Linux, macOS and
Windows without running a platform-specific command at grading time.
