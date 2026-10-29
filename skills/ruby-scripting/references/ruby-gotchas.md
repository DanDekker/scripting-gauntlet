# Ruby gotcha cheat sheet

## Truthiness

| value | truthy? |
| --- | --- |
| `nil` | no |
| `false` | no |
| `0` | **yes** |
| `""` | **yes** |
| `[]` | yes |
| `0.0` | yes |

`a || b` picks `b` when `a` is `false` **or** `nil`. Use `a.nil? ? b : a` when `false` is
a real value.

## Hash / identity

| expression | result |
| --- | --- |
| `1 == 1.0` | `true` |
| `1.eql?(1.0)` | `false` (Hash key rule) |
| `{1 => :a}[1.0]` | `nil` |
| `{1 => :a, 1.0 => :b}.size` | 2 |
| `{"a" => 1}[:a]` | `nil` |
| `{k: false}.fetch(:k, :d)` | `false` |
| `{k: nil}.fetch(:k, :d)` | `nil` |
| `{}.fetch(:k, :d)` | `:d` |
| `{k: nil}.key?(:k)` | `true` |

## Numbers

| expression | result |
| --- | --- |
| `7 / 2` | 3 |
| `-7 / 2` | **-4** (floor) |
| `-7 % 3` | 2 |
| `(-7).divmod(2)` | `[-4, 1]` |
| `7.fdiv(2)` | 3.5 |
| `(7.to_f / 2).to_i` | 3 (truncation, different rule) |
| `2.5.round` | 3 |
| `-2.5.round` | -3 |
| `0.1 + 0.2` | 0.30000000000000004 |

## Parsing

| expression | result |
| --- | --- |
| `"12abc".to_i` | 12 |
| `"abc".to_i` | 0 |
| `"0x10".to_i` | 0 |
| `Integer("0x10")` | 16 |
| `Integer("012")` | 10 |
| `Integer("0o12")` | 10 |
| `Integer(" 42 ")` | 42 |
| `Integer("12abc")` | ArgumentError |
| `Float("1e3")` | 1000.0 |
| `"abc".to_f` | 0.0 |

## Formatting

| expression | result |
| --- | --- |
| `(1e20).to_s` | `"1.0e+20"` |
| `(3.0).to_s` | `"3.0"` |
| `format("%.2f", 3.0)` | `"3.00"` |
| `format("%.2f", 1e20)` | `"100000000000000000000.00"` |
| `format("%.2f", 2.675)` | `"2.68"` |
| `format("%.2f", 1.005)` | `"1.00"` |
| `1.005.round(2)` | `1.01` |
| `format("%.2f", 1.005.round(2))` | `"1.01"` |

## Sorting

| expression | result |
| --- | --- |
| `[1, "a"].sort` | ArgumentError |
| `[3, nil, 1].sort_by { |x| x }` | ArgumentError |
| `["10", "9"].sort` | `["10", "9"]` (byte order) |
| `%w[10 9].sort_by(&:to_i)` | `["9", "10"]` |
| stability of `sort_by` | not guaranteed — carry an index |
| `nil <=> 1` | `nil` |

## Strings

| expression | result |
| --- | --- |
| `"a,b,,".split(",")` | `["a", "b"]` |
| `"a,b,,".split(",", -1)` | `["a", "b", "", ""]` |
| `" a b ".split` | `["a", "b"]` |
| `"  é".length` | 3 (characters) |
| `"  é".bytesize` | 4 (bytes) |
| `line.chomp` | strips the trailing newline |

## Regex anchors

`^` and `$` are **line** anchors; `\A` and `\z` are whole-string anchors. Validate tokens
with `\A...\z`.

## Errors

```ruby
value = Integer(text, 10) rescue nil      # modifier rescue: catches everything
begin
  risky
rescue JSON::ParserError => e
  abort "bad JSON in #{path}: #{e.message}"
end
```
