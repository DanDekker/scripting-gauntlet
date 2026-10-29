# 187-lua-binary-pack

> "We are ingesting telemetry dumped from a network capture. The frame header format uses
> binary length-prefixed payloads and checksums, but some packets have corrupted magic,
> bad checksums, or were cut off during capture."

## Input

`in/stream.bin` — raw binary stream of sequential records.

## Format Specification

Each record is serialized with big-endian byte order:
1. `magic` — 2 bytes unsigned integer (`>I2`). Expected magic is `0xCAFE` (51966).
2. `msg_id` — 4 bytes unsigned integer (`>I4`).
3. `payload` — 2 bytes length prefix (`>I2`) followed immediately by the payload bytes (equivalent to `>s2`).
4. `checksum` — 1 byte unsigned integer (`I1`). Equals `sum(payload_bytes) % 256`.

## Parsing Rules

Iterate sequentially through the stream starting at byte 1:
1. Read `magic` (2 bytes) and `msg_id` (4 bytes).
   - If fewer than 6 bytes remain, record is `truncated` and reading terminates.
2. If `magic != 0xCAFE`:
   - If payload length prefix and payload can be read, record `status = bad_magic` (with the parsed payload length and string), and advance past the checksum byte.
   - If payload is truncated, record `status = truncated` and terminate.
3. If `magic == 0xCAFE`:
   - Try to read the length-prefixed payload and checksum byte.
   - If the buffer ends before the full payload or checksum byte can be read, mark record `status = truncated`, `len = 0`, empty payload, and terminate.
   - Calculate `sum(bytes) % 256` over the payload:
     - If it matches `checksum`, `status = valid`.
     - If it does not match `checksum`, `status = corrupt_checksum`.
   - Advance position to the next frame.

## Output

Write exactly these files to `$OUT`:

1. **`out/frames.csv`** — header `msg_id,status,len,payload`, one row per frame in stream order.
2. **`out/summary.json`** — keys `frames`, `valid`, `corrupt_checksum`, `bad_magic`, `truncated`.
   One compact JSON object:
   `{"frames":5,"valid":2,"corrupt_checksum":1,"bad_magic":1,"truncated":1}`.

## Messes to expect

- Stream truncation mid-packet raises an error in `string.unpack` if not handled with `pcall`.
- Checksums can be 0 or wrap past 255.
- Non-matching magic must be cataloged rather than crashing the parser.

## Timebox

Five minutes. Use `string.unpack` with format string `>I2 I4 s2 I1` in a loop, handling position offset.
