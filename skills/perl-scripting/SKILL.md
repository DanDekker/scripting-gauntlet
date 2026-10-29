---
name: perl-scripting
description: Write throwaway Perl that parses messy text, counts, sorts and emits reports without tripping over context, numification or hash order. Use when the host already runs Perl (legacy ops boxes, cron one-liners, log pipelines), when a regex-heavy transform is shorter in Perl than anywhere else, or when existing Perl needs its split, sort, date or file-test semantics checked. Not for new services or long-lived applications.
license: MIT
metadata:
  family: text-munging
  drill: 161-perl-split-limits
---

# Perl scripting

Perl is the densest text-processing language you can run without installing anything, and
it is full of quiet conversions. The script that looks right in Python is wrong here for
reasons the language will not mention. This pack is that list.

## When Perl is the right tool

Reach for Perl when the host already has it (ops boxes, mail filters, cron, log shippers),
when the job is a regex-heavy transform that would be a page of code elsewhere, or when a
one-liner beats writing a file.

Do not reach for it to build a service. Perl rewards a script that starts, reads, prints
and exits, and punishes state kept across modules.

## `use strict; use warnings;` is not optional

```perl
use strict;
use warnings;
```

`strict` turns a typo'd variable name into an error instead of a silently empty one.
`warnings` tells you when a string is being numified, which is the single most common
source of wrong answers in Perl. If a value must be read from the environment, check it:
`my $in = $ENV{IN} or die "IN not set\n";`.

## `split` has three personalities

```perl
split /:/,  "a:b:"      # ("a", "b")        trailing empty field is DROPPED
split /:/,  "a:b:", -1  # ("a", "b", "")    the limit keeps it
split ' ',  "  a   b  " # ("a", "b")        awk mode: any whitespace, trimmed
split / /,  "  a   b  " # ("", "", "a", "", "", "b")  a single literal space
```

- The **limit of `-1`** is the fix for every "my last field vanished" bug. A trailing empty
  field is data; `split` throws it away by default.
- `split ' '` (a one-space **string**) is the special awk-style split: runs of whitespace,
  no leading empties. `split / /` (a **regex**) is one literal space and keeps them.
- `split` compiles its first argument as a regex unless it is the string `' '`. If the
  separator is data, `quotemeta` it or use `index`/`substr`.

Drill: `161-perl-split-limits`.

## Everything is a string until it isn't

Perl converts on demand, and the conversions are surprising:

```perl
"10" == "10.0"    # true   — numeric comparison
"10" eq "10.0"    # false  — string comparison
"abc" == 0        # true, with a warning: "abc" numifies to 0
"0x10" + 0        # 0      — hex is NOT parsed from a string
"1e3" + 0         # 1000   — an exponent IS
"010" + 0         # 10     — no octal for a string literal
```

- **Validate the text first, then convert.** A regex anchored to the whole token
  (`/^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$/`) is the check; `+ 0` afterwards is the
  conversion. Doing it the other way round silently accepts `abc` as zero.
- `eq`/`ne`/`cmp` are string operators; `==`/`!=`/`<=>` are numeric. Mixing them is how
  `"10" == "9"` sorts wrong.
- `0` and `""` are **defined but false**. If zero is a valid answer, test `defined`,
  not truthiness: `if (defined $epoch)`.
- `"0 but true"` is the string that is true and numifies to zero — the standard trick for
  returning a zero success code.

Drill: `162-perl-numify`.

## `int` truncates toward zero

```perl
int(-3.7)            # -3, not -4: truncation, not floor
sprintf("%d", 3.9)   # 3
sprintf("%.2f", 2.675)  # 2.67 — the double is 2.67499...
sprintf("%s", 3.0)      # "3" — Perl drops a trailing .0 on stringification
```

If the contract says "round", say how; if it says "truncate", `int` is right and
`floor` is wrong for negatives. Money belongs in integer cents, never in a float.

## Hash order is randomized on purpose

Since Perl 5.18 the order of `keys`, `values` and `each` changes on every process. That is
a security fix, not a bug, and it means:

```perl
for my $key (keys %count) { ... }                  # order varies run to run
for my $key (sort keys %count) { ... }             # reproducible
my @order = sort { $count{$b} <=> $count{$a} or $a cmp $b } keys %count;
```

Any output that a human or a diff will compare needs a **total order**: the second key in
that comparator is not optional, or ties fall back to hash order and the report flips
between runs. Drill: `164-perl-hash-order`.

(Perl's `sort` itself is a stable mergesort — the instability you have to worry about is
the hash, not the sort.)

## Regex: `\Q...\E` or `index`

A user-supplied needle is data, not a pattern:

```perl
my $at = index($subject, $needle);          # literal, no regex, no escapes needed
$subject =~ /\Q$needle\E/;                  # literal inside a regex
$subject =~ /$needle/;                      # a pattern — and a needle with "(" dies
```

- `index` returns a 0-based position or `-1`; `+1` it for a 1-based column.
- `\Q...\E` quotes every metacharacter in between.
- `/$needle/` with a runtime string is a **regex injection**: `a.b` matches `aXb`, and
  `a(` raises `Unmatched ( in regex`.
- `s///` returns the number of substitutions in scalar context; `s///r` returns the new
  string and leaves the original alone.
- Count **non-overlapping** matches: advance by `length($needle)` after each hit, or `aa`
  appears twice in `aaa`.

Drill: `163-perl-literal-match`.

## `$1` is sticky

After a **failed** match, `$1` keeps the value from the last successful one. Always test the
match before reading the capture:

```perl
if ($line =~ /^(\w+)=(\w+)$/) { my $key = $1; ... }   # safe
my ($key) = $line =~ /^(\w+)=/;                        # undef on no match
```

## Dates: months are 0-based, years since 1900

```perl
my @t = gmtime($epoch);       # $t[4] is month 0-11, $t[5] is years since 1900
my $epoch = timegm($sec, $min, $hour, $mday, $mon - 1, $year);
```

- `localtime`/`gmtime` list form: month `0..11`, year `1900+`.
- `timegm`/`timelocal` want month `0..11` and, in `Time::Local` 1.30, treat a year value
  in `0..99` as **2000..2099** — so `1970 - 1900` silently means 2070. Pass the 4-digit
  year (`timegm(..., $year)`) and it is unambiguous.
- Prove the instant: `gmtime($epoch)` must give back the fields you put in, or the date was
  not real (`2026-02-30` rolls forward instead of failing).
- Epoch `0` is a real answer and is falsy: test `defined`.

Drill: `165-perl-timegm`.

## Files: the `-X` tests and three-arg open

```perl
-e $path   # exists
-f $path   # regular file — FOLLOWS symlinks
-l $path   # is a symlink
-d $path   # is a directory
-s $path   # size in bytes (0 for an empty file, undef if missing)
```

`-f` follows symlinks, so check `-l` first when a symlink must not be counted. Always use
the three-argument open with a lexical handle and check the result:

```perl
open my $fh, '<', $path or die "cannot read $path: $!\n";
while (my $line = <$fh>) { chomp $line; ... }
close $fh;
```

`chomp` removes the trailing newline; `chop` removes the last character whatever it is.
Slurp with `local $/;` when you want the whole file at once.

## Small things that bite

- **`scalar(@list)`** is the count; `@list` in scalar context is the same number, but
  `print @list` prints the elements. Be explicit.
- **`exists` vs `defined`**: `exists $h{k}` asks whether the key is there; `defined $h{k}`
  asks whether its value is not `undef`. They differ for a key stored as `undef`.
- **`my` vs `local`**: `my` is lexical and what you want; `local` saves and restores a
  package variable and is only correct for things like `local $/`.
- **`printf`/`sprintf` with `%d`** truncates a float; use `%.0f` if you meant rounding.
- **Numeric conversion of undef** is 0 with a warning; `warnings` is why you see it.
- **`sort` in scalar context** is a syntax error; `sort { ... } @list` only.

## Binary data is `unpack` and `pack`

```perl
my ($id, $score, $flags, $len) = unpack("N n C C", substr($data, $offset, 8));
my $name = substr($data, $offset + 8, $len);
my $bin  = pack("N", 256);       # 00 00 01 00
```

- `N` big-endian u32, `n` big-endian u16, `v` little-endian u16, `C` one byte.
- `a*` keeps trailing NULs and spaces; `A*` **strips** them. For a length-prefixed field use
  `substr($data, $off, $len)`, not `A*`.
- `unpack` on a buffer that is too short returns `undef` for the field. Check the length
  before slicing, or a truncated tail silently becomes a record with empty fields.
- Walk **offsets** when a length prefix makes records variable-size; a fixed template only
  works when every field is fixed-width.

Drill: `174-perl-unpack-binary`.

## Versions are not strings

```perl
"1.10.2" cmp "1.9.9"                                   # -1  string order
version->parse("1.10.2") <=> version->parse("1.9.9")   #  1  numeric components
```

`version` is core. Dotted versions compare component by component, so `1.10.2` is newer
than `1.9.9` even though it sorts first as text. Sort the parsed objects and give ties a
second key, or the order falls back to the input.
Drill: `175-perl-version-sort`.

## The replacement is code

```perl
my $n = ($s =~ s{(\w+)=(\S*)}{ uc($1) . ":" . uc($2) }ge);   # $n is the match count
my $copy = $s =~ s/b/X/gr;                                    # non-destructive
```

- `s{}{}e` runs the replacement as Perl code; use braces when the replacement contains
  `/`. `s{}{}ee` evaluates the result again — rarely what you want.
- `$1`, `$2` are **package globals**. A nested match inside the replacement block resets
  them, so copy to lexicals first if the block matches anything else.
- Assigned in scalar context, `s///g` returns the number of substitutions.
- After a failed match, `$1` still holds the last successful capture — never read it
  without checking the match.

Drill: `180-perl-substitution-eval`.

## Offsets, not splits

```perl
substr("abcdef", -3)          # "def"   negative offset counts from the end
substr("abcdef", 2, -1)       # "cde"   negative length leaves that many off the end
substr("abcdef", 10)          # undef + "substr outside of string" warning
index("abcabc", "abc", 1)     # 3       start offset finds the second occurrence
rindex("abcabc", "abc")       # 3       search from the right
```

`index`/`rindex` return a **0-based** position or `-1`; the report usually wants 1-based,
so the `+1` is yours. `substr` past the end is a warning plus `undef`, not an exception —
clamp or check before slicing. `substr` is also an lvalue: `substr($s, 1, 3) = "XY"`
rewrites in place.

Drill: `181-perl-substr-index`.

## Caller context: wantarray

```perl
sub query_items {
    my ($threshold, @items) = @_;
    my @passed = grep { $_ >= $threshold } @items;
    return unless defined wantarray;     # void context: do nothing
    return wantarray ? @passed : scalar @passed;
}

my $count  = query_items(10, @data);     # scalar context: returns count
my @all    = query_items(10, @data);     # list context: returns array
my ($head) = query_items(10, @data);     # LIST context! parens force list context
```

Perl functions can inspect caller context via `wantarray`:
- `1` (true) in **list context** (`my @arr = f()`, `my ($x) = f()`, `for (f())`)
- `0` (defined but false) in **scalar context** (`my $n = f()`, `if (f())`)
- `undef` in **void context** (`f();`)
Trap: `my ($first) = f()` is list context despite the single variable on the left; the
parentheses enforce list context.

Drill: `188-perl-context-dispatch`.

## The four moves

**1. Split.** Choose the limit and the separator deliberately: `split /:/, $line, -1`.

**2. Validate.** A pattern anchored with `^...$` over the whole token, before any conversion.

**3. Aggregate.** A hash of counters, then a sorted key list with a two-key comparator.

**4. Emit.** Build the line with `sprintf`/`join`, write it, close the handle.

## Reporting

Say what you rejected and why. `"3 rows, 4 invalid"` is a claim the reader can check; a
bare count is not. When a line fails, quote the offending value in the message, not a
parser-generated code.

See [references/perl-gotchas.md](references/perl-gotchas.md) for the one-page cheat sheet.
Prove it against `drills/perl/161-perl-split-limits` and the rest of the `drills/perl/`
track: split limits, numification, literal matching, hash order and date conversion.
