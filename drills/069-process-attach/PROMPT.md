# 069-process-attach

> "Start this local test listener, attach to the exact process it reports, probe its
> health endpoint, then ask it to stop. Don't leave a stray worker behind."

## Task

Launch `in/worker.py` as a child process with these arguments:

```text
<ready.json> <stop.flag> <heartbeat.txt>
```

The worker binds an HTTP health listener on loopback, writes its PID and port to
`ready.json`, then increments the heartbeat until `stop.flag` exists.

## Rules

1. Wait up to 5 seconds for readiness. If the child exits or never publishes a ready
   file, report the problem on stderr and exit non-zero.
2. Read the PID from `ready.json` and require it to equal the PID returned by the
   process-launch API. Attach to that PID using the host's process API and confirm it
   is still running. Do not search by process name.
3. GET `/health` on the published loopback port. Require HTTP 200 and body `ready`.
4. Read the heartbeat, wait briefly, then read it again. The second value must be
   larger.
5. Create `stop.flag`, wait up to 2 seconds for a clean exit, then force-stop only the
   child you launched if it is still running. Always clean up on an error path.

## Output

**`out/attachment.json`** — exactly eight keys: `pid`, `ready_pid`, `port`,
`heartbeat_before`, `heartbeat_after` (integers), `attached`, `listener_ok`, and
`stopped` (booleans).

## Messes to expect

- the PID is published asynchronously after launch
- readiness and heartbeat are separate checks
- cleanup must run after both success and failure

## Timebox

5 minutes. Keep the process handle returned by launch, and use the PID only to attach
and confirm identity.
