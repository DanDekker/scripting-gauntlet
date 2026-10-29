# GNU vs BSD/macOS, side by side

The same hygiene script breaks on the other userland. These are the ones that actually
bite.

| job | GNU (Linux) | BSD (macOS) |
| --- | --- | --- |
| hash a file | `sha256sum f` | `shasum -a 256 f` |
| file size | `stat -c %s f` | `stat -f %z f` |
| size + name, NUL-safe | `find . -type f -printf '%s\t%p\0'` | `find . -type f -exec stat -f '%z%t%N' {} +` |
| in-place sed | `sed -i 's/a/b/' f` | `sed -i '' 's/a/b/' f` |
| extended regex | `grep -E` / `sed -E` | same (`-E` is portable, `-r` is not) |
| readlink -f | `readlink -f f` | `readlink f` then resolve manually |
| mtime, epoch | `stat -c %Y f` | `stat -f %m f` |
| `date -d` | `date -d '2026-10-29' +%s` | `date -j -f '%Y-%m-%d' '2026-10-29' +%s` |
| `xargs -r` | supported | not supported (skip on empty input yourself) |
| `mktemp -d` | supported | supported, but template differs: `mktemp -d -t name` |
| `sort -V` | supported | not supported |

## Detect, don't guess

```bash
if command -v sha256sum >/dev/null 2>&1; then
  hash_of() { sha256sum "$1" | cut -d' ' -f1; }
else
  hash_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
fi
```

## NUL-safe iteration, both userlands

```bash
find . -type f -print0 | while IFS= read -r -d '' file; do
  printf '%s\n' "$file"
done
```

Never `for f in $(find .)` — filenames with spaces, tabs, or newlines break it, and
someone's file is always named `my report (final).pdf`.

## The rules that survive both

- `find -print0` + `read -d ''`
- `LC_ALL=C` when byte order matters to a sort
- `cp -p` / `rsync -a` when timestamps matter
- `printf '%q'` for printing a command you intend to run
