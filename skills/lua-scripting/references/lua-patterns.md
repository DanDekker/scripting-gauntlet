# Lua pattern cheat sheet

Lua patterns are not regular expressions. There is no alternation, no lazy `+?`, and
`%` is the escape character.

## Character classes

| class | matches |
| --- | --- |
| `%a` | letters |
| `%c` | control characters |
| `%d` | digits |
| `%l` | lowercase letters |
| `%p` | punctuation |
| `%s` | whitespace |
| `%u` | uppercase letters |
| `%w` | letters and digits |
| `%x` | hexadecimal digits |
| `%g` | printable characters except space |
| `%%` | a literal percent sign |

A set is written `[abc]`, a negated set `[^abc]`, a range `[a-z]`, and a class inside
a set `[%w_.-]`.

## Quantifiers

| quantifier | meaning |
| --- | --- |
| `*` | zero or more, greedy |
| `+` | one or more, greedy |
| `-` | zero or more, **lazy** |
| `?` | zero or one |

`.` matches any character **except a newline**.

## Anchors and captures

- `^` anchors to the start of the subject, `$` to the end.
- `()` captures; `string.match` returns the captures in order.
- A capture that matched nothing returns an empty string, not `nil`.
- `%1` through `%9` in a `gsub` replacement refer to the captures.

## The ones worth remembering

```lua
-- split at the FIRST '=' so the value may contain '='
local key, value = line:match("^([^=]*)=(.*)$")

-- the LAST '='
local key, value = line:match("^(.*)=(.*)$")

-- lazy match: the shortest tag
("<a><b>"):match("<(.-)>")        --> "a"

-- balanced pair
("f(x(y))z"):match("%b()")        --> "(x(y))"

-- frontier: a word between two different classes
("THE (quick) fox"):find("%f[%a]%a+%f[%A]")   --> 1

-- every match, one capture at a time
for name in text:gmatch("(%a+)%s*=") do end

-- replace with a function, and count the replacements
local s, n = s:gsub("%d+", function(d) return "#" .. d end)

-- literal percent in a replacement
local s = s:gsub("%%", "%%%%")
```

## `gsub` returns two values

```lua
local s = s:gsub("a", "b")     -- s is the string; the count is dropped
local s, n = s:gsub("a", "b")   -- both
f(s:gsub("a", "b"))            -- f receives TWO arguments: the string and the count
```

Inside a table constructor or an argument list, the extra value leaks. This is the
same class of bug as `print((gsub(...)))` in any other language, but Lua makes it easy
to trip over.

## `string` library notes

| call | returns |
| --- | --- |
| `s:match(p)` | the first match, or the captures |
| `s:gmatch(p)` | an iterator over every match |
| `s:gsub(p, r)` | the new string **and** the number of replacements |
| `s:find(p, init, plain)` | start and end positions |
| `s:sub(i, j)` | the substring; negative indices count from the end |
| `s:byte(i)` / `s:char(n)` | one byte, or a string from byte values |
| `s:rep(n, sep)` | the string repeated |
| `s:upper()` / `s:lower()` | case changed; **ASCII only**, not Unicode |

## `utf8` library notes

| call | returns |
| --- | --- |
| `utf8.len(s)` | character count, or `nil` plus the first bad byte's position |
| `utf8.offset(s, n)` | the byte index of the n-th character, or `nil` |
| `utf8.codepoint(s, i)` | the code point at byte position i |
| `utf8.char(n, ...)` | a string from code points |
| `utf8.codes(s)` | an iterator over byte position and code point |
| `utf8.charpattern` | the character class for one whole code point |

## `table` notes

| call | returns |
| --- | --- |
| `table.insert(t, v)` | appends; `table.insert(t, i, v)` inserts at i |
| `table.remove(t, i)` | removes and returns the element |
| `table.concat(t, sep)` | joins the strings; errors on a non-string element |
| `table.sort(t, cmp)` | sorts **in place**; not stable, so pass a total-order `cmp` |
| `table.unpack(t)` | the elements as multiple return values |

`#t` is the border. On a table with holes it is **undefined** — it may report the hole
or the last element. Count what you inserted, or track the bound yourself.
