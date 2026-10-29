# 054-listener-setup

> "I need something answering on this port before the deploy. Keep it small."

## Task

Write a listener that answers on `127.0.0.1` at the port given in `$PORT`, then get out
of the way — your script must exit while the listener keeps running.

## Rules

1. Bind to **`127.0.0.1`** only. Never `0.0.0.0` and never a public interface.
2. Answer **every** request with exactly this response:

   ```
   HTTP/1.1 200 OK\r\n
   Content-Type: text/plain\r\n
   Content-Length: 13\r\n
   \r\n
   hello scriptdeck
   ```

   The body is exactly `hello scriptdeck` — 13 bytes, no trailing newline.
3. The listener must **survive your script exiting**. Background it.
4. Write the listener's pid to **`$OUT/listener.pid`** — one integer and nothing else.
5. **Redirect the listener's stdout and stderr to `$OUT/listener.log`.** A backgrounded
   child that inherits your stdout keeps that pipe open forever, and whoever launched you
   will hang waiting for it to close. This is the single most common way to wedge a
   service launcher.
6. Your script itself must exit **0**, promptly.

## Output

**`out/listener.pid`** — the pid of the listening process.

**`out/listener.log`** — the listener's output (it may be empty).

## Messes to expect

- a listener that dies the moment your script exits
- a listener that holds the parent's stdout open
- a response whose `Content-Length` does not match the body

## Timebox

5 minutes. `socket` in python; the shell version can drive any program that listens.
