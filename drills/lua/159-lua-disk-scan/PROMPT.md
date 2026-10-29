# 159-lua-disk-scan

> "Give me the bytes per file type for this tree, and tell me how much you refused to
> look at. Somebody put a node_modules in there."

## Input

`in/tree/` — a directory tree holding files of known sizes, some in subdirectories. It
contains a symlink, a directory named `node_modules`, and a dot-directory.

## Rules

1. Walk `in/tree` recursively. A directory named **`node_modules`**, or whose name begins
   with `.`, is **excluded**: nothing below it counts. Each excluded directory that holds
   at least one file is counted **once** in `dirs_skipped`.
2. Only **regular files** count. A symlink is neither followed nor counted.
3. The **extension** of a file is the text after the last `.` in its base name,
   lowercased, when that dot is not the first character of the base name. Otherwise the
   extension is the empty string: `.env` has no extension, `notes.txt` has `txt`, and
   `d.tar.gz` has `gz`.
4. Byte size is the number of bytes in the file. A file of zero bytes is a file.

## Output

Write exactly these files to `$OUT`:

1. **`out/bytes.csv`** — header `ext,count,bytes`, one row per extension present, sorted by
   `bytes` **descending**, ties broken by `ext` ascending in byte order. The extension is
   written bare; a file with no extension gives an empty `ext` field.
2. **`out/summary.json`** — an object with exactly these keys:
   - `files` — how many regular files were counted (int)
   - `bytes` — the total byte count (int)
   - `dirs_skipped` — how many excluded directories held at least one file (int)

   Print it as one compact JSON object: `{"files":8,"bytes":412,"dirs_skipped":2}`.

## Messes to expect

- `node_modules/x.log` is 999 bytes and must not appear in any total
- `.hidden/y.log` is skipped by the dot-directory rule
- `link.log` is a symlink to `a.log`: counting it would double `a.log`
- `.env` is a 5-byte file with **no** extension, and `data` is a 0-byte file with none
- `b.LOG` joins the `log` row because the extension is lowercased

## Timebox

Five minutes. Lua has no `stat` and no directory listing in its standard library, so
`io.popen("find … -type f")` plus `f:seek("end")` is the route.
