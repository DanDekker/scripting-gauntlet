# 203-perl-slurp-record-separator

> "Our notes importer started reporting a single record instead of three. The previous
> version read the config file with `$/ = undef` and never put the separator back, so
> every later `readline` slurped the entire notes file into one string."

## Input

- `in/config.ini` — a small configuration file.
- `in/notes.txt` — note records separated by a **blank line** (a line containing no
  characters).

## Rules

1. Read `in/config.ini` as **one string**: slurp the whole file. The input record
   separator must be restored when you are done, so the notes file is still read the
   normal way afterwards.
2. From that string:
   - `config_lines` is the number of newline characters in it.
   - `settings` is the number of lines that look like `key=value` — the key starts
     with a letter or underscore and continues with letters, digits or underscores.
     Lines that are blank or start with `#` are not settings.
3. Read `in/notes.txt` as **paragraphs**: each record is a run of non-blank lines,
   and a blank line separates one record from the next. The record text does not
   include the blank line that ended it.
   - For each record, in file order, report its 1-based index, its **first line**,
     and the number of lines it contains.
4. **`out/records.csv`** — header `index,title,lines`. One row per record.
5. **`out/summary.json`** — keys `records`, `total_lines`, `config_lines`,
   `settings`. One compact JSON object.

## Messes to expect

- `$/` is global. Slurping with `$/ = undef` and never restoring it makes the next
  `readline` return the whole notes file as one record.
- Under a paragraph separator, `chomp` strips the blank line that ended the record,
  not just a single newline.

## Timebox

Five minutes. `local $/ = undef;` and `local $/ = "";` both restore the separator
when the enclosing block ends.
