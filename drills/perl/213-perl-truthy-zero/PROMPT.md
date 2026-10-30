# 213-perl-truthy-zero

> "The feature flags stopped being right. The checker treated the value `false` as
> disabled and the value `0.0` as disabled too. In perl only the empty string and the
> exact text `0` are false — `false`, `no` and `0.0` are all true."

## Input

`in/settings.txt` — one setting per line, `<name> <value>`. The value may be empty:

```text
feature_a 1
feature_b 0
feature_c 0.0
feature_d 00
feature_e false
feature_f no
feature_g 
```

## Rules

1. Read `in/settings.txt`. Each line is a name and a value, separated by a single
   space. The value is the rest of the line and may be empty.
2. A setting is **on** when perl considers its value true, and **off** otherwise.
   That is: a value is false only when it is the empty string or the exact text `0`.
3. **`out/settings.csv`** — header `index,name,value,state`. One row per setting, in
   file order, `index` starting at 1, `state` being `on` or `off`.
4. **`out/summary.json`** — keys `settings`, `on`, `off`. One compact JSON object.

## Messes to expect

- The value `0.0` is **true** in perl — only the exact text `0` is falsy. So is `00`.
- The values `false` and `no` are ordinary non-empty strings: **true**.
- A regex like `/^(0|false|no)$/i` is a different rule from perl's, and it is wrong.

## Timebox

Four minutes.
