# Perl gotcha cheat sheet

## Strings and numbers

| expression | result | why |
| --- | --- | --- |
| `"10" == "10.0"` | true | numeric comparison |
| `"10" eq "10.0"` | false | string comparison |
| `"abc" == 0` | true + warning | `abc` numifies to 0 |
| `"0x10" + 0` | 0 | hex is not parsed from a string |
| `"1e3" + 0` | 1000 | exponent is parsed |
| `"010" + 0` | 10 | no octal for strings |
| `int(-3.7)` | -3 | truncation toward zero |
| `sprintf("%d", 3.9)` | `3` | truncation |
| `sprintf("%.2f", 2.675)` | `2.67` | the double is 2.67499… |
| `sprintf("%s", 3.0)` | `3` | trailing `.0` dropped |
| `0.1 + 0.2 == 0.3` | false | binary floats |
| `"0 but true"` | true, numifies 0 | the zero-but-success trick |
| `undef + 0` | 0 + warning | conversion of undef |

## Context

| expression | in scalar context | in list context |
| --- | --- | --- |
| `@list` | element count | the elements |
| `keys %h` | key count | the keys |
| `split /:/, $s` | field count | the fields |
| `s///g` | number of substitutions | the new string |
| `gmtime($t)` | a formatted string | a 9-element list |
| `sort @list` | — | sorted list |

## `split`

| call | `"a:b:"` gives |
| --- | --- |
| `split /:/` | `("a","b")` |
| `split /:/, $s, -1` | `("a","b","")` |
| `split /:/, $s, 2` | `("a","b:")` |
| `split ' ', "  a  b "` | `("a","b")` |
| `split / /, "  a  b "` | `("","","a","","b")` |

## Regex

| need | use |
| --- | --- |
| literal search | `index($s, $needle)` or `/\Q$needle\E/` |
| count matches, scalar | `my $n = ($s =~ /pat/g);` |
| count non-overlapping | `while ($s =~ /\Q$p\E/g) { $n++; pos($s) += length($p) - 1 }` |
| replace, keep original | `(my $new = $s =~ s/a/b/gr)` |
| captures after a failed match | stale — test the match first |

## Hash order

```perl
keys %h                       # randomized per process
sort keys %h                  # reproducible, byte order
sort { $h{$b} <=> $h{$a} or $a cmp $b } keys %h   # total order
each %h                       # one iterator per hash; don't nest
```

## Dates

| field | `localtime`/`gmtime` list | `timegm`/`timelocal` argument |
| --- | --- | --- |
| second | `[0]` 0-59 | `$sec` |
| minute | `[1]` 0-59 | `$min` |
| hour | `[2]` 0-23 | `$hour` |
| day | `[3]` 1-31 | `$mday` |
| month | `[4]` **0-11** | `$mon - 1` |
| year | `[5]` **1900+** | 4-digit year, or 1900+ offset ≥ 100 |

`Time::Local` 1.30 maps an offset in `0..99` to 2000..2099, so `$year - 1900` is wrong for
1970–1999: pass the 4-digit year.

## File tests

| test | true when |
| --- | --- |
| `-e` | the path exists |
| `-f` | regular file (follows symlinks) |
| `-l` | symlink |
| `-d` | directory |
| `-s` | size in bytes (0 for empty, undef for missing) |
| `-T` | looks like text |

## Fatal versus recoverable

```perl
open my $fh, '<', $p or die "cannot read $p: $!\n";   # stop
my $ok = eval { risky(); 1 };                         # recover
if (not $ok) { my $err = $@; ... }
```
