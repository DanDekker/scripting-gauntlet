---
name: ruby-scripting
description: Write throwaway Ruby that parses messy text, counts, sorts and emits reports without tripping over truthiness, Hash identity, integer division or float formatting. Use when the host already runs Ruby (Rails boxes, ops scripts, Net::HTTP one-liners), when Enumerable makes a transform shorter than anywhere else, or when existing Ruby needs its comparison, division or formatting rules checked. Not for new services or long-lived applications.
license: MIT
metadata:
  family: data-wrangling
  drill: 166-ruby-integer-division
---

# Ruby scripting

Ruby is the most pleasant language on this deck to write a report in — `map`, `select`,
`group_by`, `sort_by` and `each_with_object` cover nearly every transform. The cost is a
set of rules that differ from the language you last used, and each one fails quietly.

## When Ruby is the right tool

Reach for Ruby when it is already installed, when the job is object-shaped (records,
grouping, formatting), or when `Enumerable` saves you a loop. Rails-adjacent hosts almost
always have it.

Do not reach for it for a one-line file munger if `awk` will do, and do not reach for it to
build a service.

## Truthiness: only `nil` and `false` are falsy

This is the opposite of JavaScript, PHP and C, and the same as Python for `""`/`0`… except
Python also treats those as falsy. Ruby does not:

```ruby
nil   ? "t" : "f"   # f
false ? "t" : "f"   # f
0     ? "t" : "f"   # t   <- zero is truthy
""    ? "t" : "f"   # t   <- empty string is truthy
```

Consequences:

- `value || default` replaces an explicit **`false`** with the default. If `false` is a
  meaningful setting, test `value.nil?` instead.
- `hash[key]` returns `nil` for a missing key **and** for a key stored as `nil`. Use
  `key?` / `fetch` when the difference matters:
  `hash.fetch(key, default)` returns the stored `nil`; `hash.dig(:a, :b)` propagates `nil`.
- An explicit `nil` from JSON is a tombstone you must handle deliberately, not a fallback.

Drill: `168-ruby-truthiness`.

## Integer division floors

```ruby
7 / 2        # 3
-7 / 2       # -4    floor, not truncation
-7 % 3       # 2     non-negative for a positive divisor
(-7).divmod(2)  # [-4, 1]
7.fdiv(2)    # 3.5   the float route
```

C, Go and Java truncate toward zero, so a ported `sum / count` on a negative sum is one
unit too high. `divmod` gives both halves and satisfies `q * d + r == n` with
`0 <= r < d` — use it when the remainder is part of the report.

`(a.to_f / b).to_i` truncates; that is a **different rule** dressed as the same one.
Drill: `166-ruby-integer-division`.

## Integer rounding is half away from zero

```ruby
2.5.round      # 3
-2.5.round     # -3
2.675.round(2) # 2.68
```

`Float#round` is half away from zero (not banker's rounding). For money, keep integer
cents and never let a float touch the arithmetic.

## Hash keys are `eql?` + `hash`, not `==`

```ruby
1 == 1.0       # true
1.eql?(1.0)    # false  <- this is what a Hash uses
{1 => :int, 1.0 => :float}.size   # 2
{1 => :int}[1.0]                  # nil
{"a" => 1}[:a]                    # nil  <- string and symbol keys differ
```

So a tally keyed on raw JSON values keeps `1` and `1.0` apart, and `"1"` is a third
entity. Normalize the key to a canonical form (`[kind, text]`) before counting.
Drill: `167-ruby-hash-identity`.

## `sort` raises on mixed types, and is not stable

```ruby
[1, "a"].sort                       # ArgumentError: comparison of Integer with String failed
[3, nil, 1].sort_by { |x| x }       # ArgumentError: comparison of Integer with nil failed
```

- Convert before comparing: numeric strings compared as text give `"10" < "9"`.
- `sort_by` is **not guaranteed stable**, so ties need an explicit index:
  `sort_by { |r| [r.missing ? 1 : 0, -r.score, r.index] }`.
- `<=>` returns `nil` for incomparable values, and `sort` turns that into an exception at
  an arbitrary point — a partial file may already be written.

Drill: `169-ruby-sort-mixed`.

## Float formatting: `to_s` is not a formatter

```ruby
(1e20).to_s              # "1.0e+20"   scientific
(3.0).to_s               # "3.0"        trailing .0
format("%.2f", 3.0)      # "3.00"
format("%.2f", 1e20)     # "100000000000000000000.00"
format("%.2f", 1.005)    # "1.00"  <- the double is 1.00499...
1.005.round(2)           # 1.01
format("%.2f", 1.005.round(2))  # "1.01"
```

`format("%.2f")` formats the **binary** value; `round(2)` rounds the decimal value. If the
contract says "round half away from zero", round first and format second — or use
`Rational`/`BigDecimal`. Never interpolate a `Float` into a CSV cell and hope.
Drill: `170-ruby-float-format`.

## `to_i` parses a prefix and never complains

```ruby
"12abc".to_i      # 12   <- silently stops at the first non-digit
"abc".to_i        # 0
"0x10".to_i       # 0    <- to_i is base 10 only
Integer("0x10")   # 16
Integer("012")    # 10   <- leading zero is decimal here, unlike a literal 012 (octal)
Integer(" 42 ")   # 42   <- whitespace is allowed
Integer("12abc")  # ArgumentError
```

Validate with an anchored pattern (`\A...\z`, not `^...$` — `^`/`$` are line anchors), then
convert with `Integer(text, 10)`.

## `Enumerable` moves worth knowing

```ruby
counts = list.each_with_object(Hash.new(0)) { |item, acc| acc[item] += 1 }
grouped = records.group_by(&:kind)
sorted  = records.sort_by { |r| [r.priority, r.name] }
total   = records.sum(&:cents)
pairs   = counts.sort_by { |name, n| [-n, name] }
```

- `Hash.new(0)` avoids the `nil + 1` crash.
- `sum` on strings raises `TypeError`; convert first.
- `group_by` preserves insertion order of keys, but do not depend on it in output.
- `each_slice(n)` / `each_cons(n)` for chunked output.

## Files and JSON

```ruby
File.foreach(path) { |line| line.chomp }        # streaming, constant memory
File.readlines(path, chomp: true)               # small files
File.write(out, text)                           # truncate + write
JSON.parse(File.read(path))                     # require "json"
JSON.parse(line)                                # one object per line
```

`File.foreach` keeps the newline; `chomp` it. `JSON.generate` emits compact JSON;
`JSON.pretty_generate` is for humans. `JSON.parse` turns `null` into `nil` and `false`
into `false` — see the truthiness section.

## Fatal versus recoverable

```ruby
in_dir = ENV["IN"] or abort "IN not set"        # stop loudly
data = JSON.parse(File.read(path)) rescue abort "bad JSON in #{path}"
```

Rescue the specific error class when you can; a bare `rescue` also catches `NoMethodError`
on a typo. Print the file and line context in the abort message.

## A default is not a factory

```ruby
h = Hash.new([])              # ONE array shared by every missing key
h[:a] << 1
h[:b]                         # [1]  — the same array
h.keys                        # []   — reading a default stores nothing

g = Hash.new { |store, k| store[k] = [] }   # factory: the key materialises
g[:a] << 1
g.keys                        # [:a]
```

`Hash.new(0)` is safe because `0` is immutable and `+=` replaces the value. `Hash.new([])`
is the classic bug: the array is shared, and the read never creates the key, so the tally
silently has no rows. `fetch` and `dig` read without touching the default; `default_proc`
tells you which kind of default you have.

Drill: `182-ruby-hash-default`.

## Bytes are not characters

```ruby
bad = "caf\xE9".force_encoding("UTF-8")   # relabels, does not validate
bad.valid_encoding?                        # false
bad.scrub("?")                             # "caf?"
"café".length     # 4      characters
"café".bytesize   # 5      bytes
```

`force_encoding` only changes the label; validation is `valid_encoding?` and repair is
`scrub` or `encode(..., invalid: :replace)`. On valid input `length` and `bytesize` differ
by design, so decide which number the report means before printing either. Read unknown
input with `File.binread` and label it yourself.

Drill: `183-ruby-encoding-scrub`.

## Lazy enumeration: Enumerable#lazy

```ruby
File.open("huge.log").each_line.lazy
  .map(&:strip)
  .select { |l| l.include?("ERROR") }
  .take(5)
  .force
```

Chaining `.map`, `.select`, and `.reject` on standard arrays allocates a brand new Array at
every intermediate step. On large or unbounded streams, eager evaluation exhausts memory or hangs.
Calling `.lazy` returns an `Enumerator::Lazy`, deferring all processing until terminal methods
like `.take(n).force` or `.to_a` demand elements. It short-circuits upstream consumption as
soon as the demanded count is reached.

Drill: `189-ruby-lazy-pipeline`.

## Keyword arguments and explicit nil overrides

```ruby
def build_endpoint(host:, port: 8080, path: "/", timeout: 30)
  p = path.nil? ? "" : path
  url = "http://#{host}:#{port}#{p}"
  t = timeout.nil? ? "" : timeout.to_s
  [url, t]
end

# Forwarding hash parameters requires double-splat:
kwargs = { host: "api.internal", path: nil }
build_endpoint(**kwargs)
```

In Ruby 3+, keyword arguments are separated from positional hashes: forwarding a hash to keyword
parameters requires `**kwargs`.
Crucially, default values (`path: "/"`) only apply when the argument is **omitted**.
Passing `path: nil` explicitly sets `path` to `nil` inside the method!
Using `path || "/"` wrongly destroys intentional `nil` overrides; check `.nil?` or key presence instead.

Drill: `194-ruby-keyword-arguments`.

## Encapsulation via Forwardable delegation

```ruby
require "forwardable"

class SecureRegistry
  extend Forwardable
  # Delegate read-only inspection methods to internal store:
  def_delegators :@store, :keys, :values, :size
  def_delegator :@store, :[], :lookup

  def initialize
    @store = {}
    @reads = 0
  end

  def add(k, v)
    @store[k] = v
  end
  # Mutating methods like `delete` or `clear` are NOT delegated!
end
```

Inheriting from collection classes (`class MyStore < Hash`) exposes dangerous internal mutating
methods (`delete`, `clear`, `replace`) that violate encapsulation.
The standard library `Forwardable` module provides explicit delegation (composition over inheritance).
Classes use `extend Forwardable` and declare exactly which methods forward to internal objects.
Any attempt by external code to call un-delegated mutating methods raises `NoMethodError`.

Drill: `199-ruby-forwardable-delegation`.

## The four moves

**1. Split.** `line.split(",", -1)` keeps trailing empty fields; a bare `split(",")`
drops them — same rule as Perl.

**2. Validate.** An anchored regex over the whole token, before any conversion.

**3. Aggregate.** `each_with_object(Hash.new(0))`, then a `sort_by` with a total-order
tuple.

**4. Emit.** `File.open` a handle, write the header, write rows, close it.

## Reporting

Say what you rejected and why. `"6 ranked, 1 invalid, 2 missing"` is checkable; a bare
count is not. When a score is invalid, quote the token in the summary, not a class name.

See [references/ruby-gotchas.md](references/ruby-gotchas.md) for the one-page cheat sheet.
Prove it against the `drills/ruby/` track: division, Hash identity, truthiness, mixed
sorting and float formatting.
