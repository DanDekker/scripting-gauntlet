---
name: lua-scripting
description: Write throwaway Lua scripts that parse messy text, count characters, sum decimals, sort records, and emit JSON without leaving the standard library. Use when the target host is already Lua-shaped (nginx/OpenResty, redis, neovim, haproxy, mpv), when a 200 KB interpreter beats a 40 MB one for a config-time transform, or when an existing Lua snippet needs its pattern, table, or string semantics checked. Not for general CLIs, web services, or anything that needs a package manager.
license: MIT
metadata:
  family: text-munging
  drill: 150-lua-pattern-fields
---

# Lua scripting

Lua is a small language with sharp edges. The same script that is obviously right in
Python will be quietly wrong in Lua, because Lua's standard library makes different
promises than you expect. This pack is the list of those promises.

## When Lua is the right tool

Lua is already installed wherever it matters: nginx/OpenResty, redis, neovim,
wireshark dissectors, haproxy, mpv, awesome. It starts in milliseconds and its
`io`/`string`/`table` libraries cover most config-time transforms.

Reach for Lua when the host is Lua-shaped, or when the job is small enough that a
dependency would cost more than the script. Do **not** reach for it to write a general
CLI: you will spend the whole timebox writing a JSON parser, which is exactly what
`155-lua-json-writer` is about.

## Patterns are not regexes

Lua's pattern language is smaller than a regex and different in shape. There is no
alternation (`|`), no lazy `+?`, no `\d` — the classes are `%d`, `%w`, `%s`, `%p`, and
the escape character is `%` itself.

```lua
local key, value = line:match("^([^=]*)=(.*)$")   -- split at the FIRST '='
local method, path = line:match('"(%u+) (%S+) ')   -- two captures
for name in text:gmatch("(%a+)%s*=") do end         -- iterate every match
```

- **No alternation.** Try one shape per `match` and branch on `nil`, instead of trying
  to write one clever pattern. That is the whole lesson of `150-lua-pattern-fields`.
- **`.-` is the lazy quantifier**, `.-` not `.*?`. `("<a><b>"):match("<(.-)>")` gives
  `"a"`; the greedy `.*` would swallow both tags.
- **`.` does not match a newline**, so a multi-line string needs `%s*` around the
  anchors, not `.*`.
- **`%b()` finds a balanced pair**: `("f(x(y))z"):match("%b()")` gives `"(x(y))"`.
  Use it for nested delimiters instead of counting braces by hand.
- **`%f[set]` is a frontier pattern**: it matches the empty string at a boundary, so
  `("%f[%a]%a+%f[%A]")` finds a word between two different character classes.
- **A needle is data, not a pattern**: `s:find(needle, 1, true)` — the fourth argument is
  the whole lesson. A needle ending in `%` (like `token=100%`) makes `find(s, needle)`
  raise `malformed pattern (ends with '%')`, so the scan dies on the first line it reads.
  See `157-lua-needle-haystack`.
- `string.gsub` returns **two** values: the string and the number of replacements. In
  a table constructor or an argument list, `local s = s:gsub(...)` keeps only the
  string, and `f(s:gsub(...))` passes both. Capture the count when you need it:
  `local s, n = s:gsub(...)`.

## `#s` counts bytes, `utf8.len` counts characters

For anything a human typed, bytes and characters are different numbers. `café` is
5 bytes and 4 characters; `日本語` is 9 bytes and 3 characters.

```lua
local chars = utf8.len(line)          -- nil plus the bad byte's position if invalid
local cut = utf8.offset(line, 11)      -- byte index of the 11th character
local head = cut and line:sub(1, cut - 1) or line
```

- `utf8.len` returns **`nil` plus the position of the first invalid byte** rather than
  raising. Check for it; that is how you reject a corrupt line instead of mangling it.
- To cut a string at the Nth character, use `utf8.offset` and then `sub`. Slicing by
  bytes (`line:sub(1, 10)`) splits a multi-byte character in half and produces
  invalid UTF-8 — see `152-lua-utf8-chars`.
- `utf8.codepoint` and `utf8.char` round-trip a code point. `utf8.charpattern` is the
  character class for a whole code point.

## Tables have holes, and the length operator lies

A table with a missing entry in the middle is a hole. Both `#` and `ipairs` misbehave
around one.

- **`#t` on a table with holes is undefined.** It may return the position of the hole
  or the last element. Never use it to count entries you know are gappy.
- **`ipairs` stops at the first `nil`.** `for i, v in ipairs(values)` on a table with
  a hole at index 3 silently drops everything after it — a silent data-loss bug, which
  is what `156-lua-sparse-array` is built around.
- **`pairs` order is unspecified**, so any output that must be reproducible has to be
  sorted before it is written.
- A value of `0` is a value, not a gap. Test with `~= nil`, never with truthiness,
  when zero is legal data.

## A glob is not a pattern either

`*.log` is a glob, not a Lua pattern. Translating `*` to `.*` and stopping there gives
`^.*.log$`, where the `.` before `log` matches **any** character — so `myblog` matches
`*.log` and `c.log.old` is judged by a rule nobody wrote.

Escape every literal first (`.`, `-`, `+`, `%`, `(`, `)`, `[`, `]`, `^`, `$`), then
translate `*` → `.*` and `?` → `.`, and anchor the whole thing. Drill: `160-lua-file-hunt`.

## There is no stat and no opendir

Lua's standard library cannot list a directory or read a file's metadata. That is not a
limitation to work around with a package; it is the shape of the language:

```lua
local pipe = assert(io.popen("find '" .. root .. "' -type f"))   -- the list
for path in pipe:lines() do ... end
pipe:close()

local fh = assert(io.open(path, "rb"))
local size = fh:seek("end")      -- the size, with no stat call
fh:close()
```

`find -type f` also settles symlinks for you: it does not follow them and does not report
them, which is usually exactly what a size roll-up wants. Drill: `159-lua-disk-scan`.

## `table.sort` is not stable

Equal elements may come out in any order. If the input order matters — and it usually
does, because the input was sorted — carry the original position and use it as the
tie-break:

```lua
records[#records + 1] = { name = name, score = score, index = #records + 1 }
table.sort(records, function(a, b)
  if a.score ~= b.score then return a.score > b.score end
  return a.index < b.index
end)
```

Without the second line the leaderboard reshuffles between runs — `153-lua-sort-ties`
is that bug with a verdict.

## Money is not a float

Lua 5.4 has an integer subtype, and `0.1 + 0.2` is still `0.30000000000000004`.

- `7/2` is `3.5`; `7//2` is `3`. `//` is floor division.
- `string.format("%d", 3.5)` **raises** `number has no integer representation`. Only
  format an integer with `%d`.
- Scale decimals to integer thousandths and do the arithmetic there. Parse the digits
  yourself; do not go through a float on the way in.
- **`%` is floor-modulo, so the sign follows the divisor**: `-250 % 1000` is `750`, not
  `-250`. Format a negative scaled value by taking the absolute value, splitting, and
  re-attaching the sign — `151-lua-exact-decimals` is exactly this trap.

## Errors carry a position unless you say otherwise

`error("bad thing")` prefixes the message with `file:line:`. That is useful for a
traceback and wrong for a report.

```lua
error("not an integer: " .. value, 0)   -- level 0: no position prefix
local ok, err = pcall(check, line)       -- false, "not an integer: three"
```

- Pass **level 0** when the message is going into output the user reads.
- `pcall` returns `false` plus the raised value. Raise a **table** when the message
  has to carry structure: `error({ code = "bad", line = n })` comes back as a table.
- `pcall` catches Lua errors, not failures like a missing file. `io.open` returns
  `nil` plus a message; check it rather than expecting an exception.
- Keep going after a bad line and report each failure — that is the shape of
  `154-lua-error-level`.

## `%q` is Lua escaping, not JSON

`string.format("%q", s)` produces a valid **Lua** string literal. It is not JSON.

- For a tab it writes `\9` and for a bell `\7`. JSON has no `\9` escape, so the
  document does not parse.
- For a newline it writes a backslash followed by a real newline.
- Write the JSON escaper yourself, one byte at a time: quote, backslash, and every
  byte below `0x20`. See `155-lua-json-writer`.
- An integral number must be written as an integer, `3`, not `3.0`; a fractional one
  goes through `%.6g`.

## Small things that bite

- **A loop variable is const.** `for key in pairs(t) do key = trim(key) end` raises
  `attempt to assign to const variable 'key'` in Lua 5.4+. Copy it into a local first:
  `for piece in ... do local key = trim(piece)`.
- **Strings are immutable**; `s:gsub` builds a new string. That is fine, but a loop
  that calls `gsub` per line is a loop that copies the whole line each time.
- **`tonumber` is lenient**: `tonumber("0x10")` is 16 and `tonumber(" 12 ")` is 12. If
  the contract says "decimal integer", match the digits before you convert.
- **`os.date` is local time**; `os.date("!%Y-%m-%d", t)` is UTC. The `!` is the whole
  difference.
- **`io.popen` returns one handle.** Read the output with `f:read("a")` **before**
  `f:close()`, or the pipe can block. `f:close()` then gives you `ok, "exit", code`.
- `table.concat` needs a separator argument to join with anything other than a comma,
  and it errors on a non-string element.
- `string.rep` and `string.format` are how you build a fixed-width report; `string.format`
  is also how you lose a trailing newline.

## Two number types, not one

Since 5.3 an integer and a float are different subtypes:

```lua
math.type(1)       -- integer
math.type(1.0)     -- float
1 / 2              -- 0.5   / is always float
3 // 2             -- 1     // floors and keeps the subtype
3.0 // 2           -- 1.0   float in, float out
-10 // 7           -- -2    floors toward -infinity
-10 % 7            -- 4     floor modulo
math.fmod(-10, 7)  -- -3    C fmod: sign of the dividend
```

- `%` and `math.fmod` are **different remainder rules**. Pick the one the contract means.
- Integer arithmetic **wraps** at 2^63: `math.maxinteger + 1` is `math.mininteger`, and
  `string.format("%x", n)` prints the two's-complement value (`8000000000000000`).
- `tostring(3.0)` is `"3.0"`, so a float announces itself in a report.
  `string.format("%d", 3.5)` raises `number has no integer representation`.
- `tonumber("0x10")` is 16; `tonumber("9223372036854775808")` is a **float**, because it
  does not fit an integer.

Drill: `171-lua-integer-subtype`.

## Coroutines stream without buffering

```lua
local function stream(path)
  return coroutine.wrap(function()
    local fh = assert(io.open(path, "r"))
    local buf = ""
    while true do
      local chunk = fh:read(4096)
      if not chunk then break end
      buf = buf .. chunk
      while true do
        local nl = buf:find("\n", 1, true)
        if not nl then break end
        coroutine.yield(buf:sub(1, nl - 1))
        buf = buf:sub(nl + 1)
      end
    end
    if buf ~= "" then coroutine.yield(buf) end
  end)
end
```

- A chunked reader must **carry the partial line** across the boundary: `read(4096)` is not
  a line.
- `coroutine.wrap` returns a function and lets an error escape into the caller;
  `coroutine.resume` returns `false, message` instead. Choose deliberately.
- After an error the coroutine is **dead**: `coroutine.status` reports `dead`, and resuming
  again raises. If the run must stop, stop; if it must continue, re-create the producer.
- `pcall` around the consuming loop gives one abort point. `pcall` around each record
  silently skips failures — that is a different contract, not a safer one.

Drill: `172-lua-coroutine-pipeline`.

## `load()` compiles a chunk, not an expression

```lua
load("1 + 2")          -- nil: unexpected symbol near '1'
load("return 1 + 2")   -- a function
local f, err = load("os.time()", "expr", "t", sandbox)  -- nil on syntax, never raises
pcall(f)               -- runtime errors come back as false, message
```

- A chunk is a **block of statements**. To evaluate an expression, prepend `return `.
- `load` returns `nil, message` on a syntax error; it does not raise. A call error is one
  `pcall` away.
- The fourth argument is the environment. Pass a table and the chunk cannot see globals; a
  metatable `__index` that raises builds a **whitelist**.
- `error(msg, 0)` drops the `file:line:` prefix; position-prefixed messages keep it.
  Normalise before comparing messages between runs.

Drill: `173-lua-load-sandbox`.

## Rendering a number is not formatting it

```lua
tostring(1.0)        -- "1.0"     the float subtype shows
tostring(1)          -- "1"
tostring(1/3)        -- "0.33333333333333331"
tostring(1e15)       -- "1e+15"   whole, but scientific
string.format("%.17g", 0.1)        -- "0.10000000000000001"
string.format("%.6g", 1000000000000000)  -- "1e+15"
```

`tostring` is the shortest text that round-trips, with a `.0` on integral floats. `%g`
truncates to significant digits, so a value printed with `%g` and re-read is a different
number. For a report, pick one rendering and stay with it; `%.17g` is for exposing the
double, never for display. `string.format("%d", 3.5)` raises — `%d` needs an integral
value.

Drill: `178-lua-number-printing`.

## Metatables are the object system

```lua
local base = { region = "eu" }
local leaf = setmetatable({ name = "api" }, { __index = base })
leaf.region            -- "eu"          inherited
rawget(leaf, "region") -- nil           only own keys
for k in pairs(leaf) do end             -- "name" only
```

- `__index` can be a table (single parent) or a function (computed lookup). Chains are
  built by pointing one table's `__index` at the next.
- `rawget`/`rawset` bypass the metatable — that is how you ask "does this layer own the
  key" as opposed to "can it see the key".
- `pairs`/`ipairs` iterate own keys only; inheritance is not enumeration.
- `__newindex` fires only when the key is **absent** from the table itself, which is how a
  proxy records writes.

Drill: `179-lua-metatable-layers`.

## Binary formats: pack and unpack

```lua
local packed = string.pack(">I2 I4 s2 I1", 0xCAFE, 1001, "payload", 42)
local ok, magic, id, payload, cksum, next_pos = pcall(string.unpack, ">I2 I4 s2 I1", packed, 1)
```

`string.pack` formats binary buffers and `string.unpack` decodes them.
Format specifier `>` enforces big-endian order (`<` for little-endian). `>I2` is a 16-bit uint,
`>I4` is a 32-bit uint, and `s2` is a 2-byte length-prefixed string.
Crucially, `string.unpack` returns decoded values **followed by the next byte offset** as its
final return value. If the buffer is truncated, `string.unpack` raises "data string too short"
instead of returning nil; always wrap stream-reading unpacks in `pcall`.

Drill: `187-lua-binary-pack`.

## The four moves

**1. Extract.** One pattern per shape, tried in order.

```lua
local key, value = line:match("^([^=]*)=(.*)$")
if not key then key = line:match("^(%S+)%s+(%d+)$") end
```

**2. Count.** Decide whether you want bytes or characters, and say so in the output.

```lua
local chars = utf8.len(line) or 0
```

**3. Aggregate.** Keep your own counter and your own bounds; never trust `#` over a
table with holes.

```lua
local counts = {}
counts[key] = (counts[key] or 0) + 1
```

**4. Emit.** Sort the keys before writing, and build the output format by hand.

```lua
table.sort(keys, function(a, b) return a < b end)
```

## Reporting

Print what you dropped alongside what you kept: `"7 records, 2 invalid"`. A bare count
is a claim you cannot defend. And when a line is rejected, say why in the words the
user would use, not in the words your parser happens to produce.

See [references/lua-patterns.md](references/lua-patterns.md) for a pattern cheat sheet.
Prove it against `drills/lua/150-lua-pattern-fields` and the rest of the `drills/lua/`
track: field parsing, exact decimals, UTF-8 counting, sort ties, error levels, JSON
output, sparse tables, needle search, plugin ordering, disk scans and file hunting.
