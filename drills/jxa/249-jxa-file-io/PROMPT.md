# 249-jxa-file-io

> "Read this UTF-8 note through Foundation, discard blank lines, and report both
> Unicode characters and encoded bytes."

## Input

in/notes.txt is UTF-8 text with leading/trailing spaces, a Greek letter, an accented
word, an emoji, and a blank line:

~~~text
  alpha  
βeta

café 😀
~~~

## Rules

1. Read the file as UTF-8 using NSString.
2. Split on CR, LF, or CRLF. Trim each line and skip lines that become empty.
3. Preserve input order.
4. chars is the number of Unicode code points in the trimmed line. bytes is the UTF-8
   byte count of that same line.

## Output

Write out/lines.csv with header index,text,chars,bytes and rows numbered from 1.
Write out/summary.json with exactly {"records":3,"chars":15,"bytes":20}.

## Messes to expect

- JavaScript string length counts UTF-16 code units, so the emoji is two units
- Foundation NSData length counts encoded bytes
- trim happens before both counts
- NSString file reads need an explicit encoding and an NSError Ref

## Timebox

Five minutes. Use Array.from(text).length for code points and
NSString.dataUsingEncoding(NSUTF8StringEncoding).length for bytes.
