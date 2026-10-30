---
name: jxa-scripting
description: Write short macOS JavaScript for Automation scripts that use Foundation to parse JSON and plists, read files, inspect paths, normalize dates, and emit stable reports. Use when the host is macOS and osascript or Objective-C Foundation is already available. Not for browser JavaScript, cross-platform Node programs, or live automation that needs a user permission not present in the task.
license: MIT
metadata:
  family: system-recon
  drill: 149-macos-plist-audit
---

# JXA scripting

JXA is JavaScript running inside osascript. Its useful superpower is the bridge to
macOS Foundation without installing a package. Its sharp edge is that Objective-C
objects are not ordinary JavaScript values until you unwrap them deliberately.

## When JXA is the right tool

Use it for a macOS-only one-shot that needs property lists, Foundation date and URL
parsing, file metadata, or a small native bridge. Keep the input offline and synthetic
when the task does not require live system state.

Use ordinary JavaScript or Python when the job is portable, browser-shaped, or dominated
by data manipulation that does not need Foundation.

## Start with the process contract

The gauntlet supplies IN, OUT, and WORK. Read environment variables through
NSProcessInfo and convert NSString values with ObjC.unwrap:

~~~javascript
ObjC.import('Foundation');
const env = (name) => {
  const value = $.NSProcessInfo.processInfo.environment.objectForKey($(name));
  if (!value) throw new Error(name + ' is missing');
  return ObjC.unwrap(value);
};
const input = env('IN');
const output = env('OUT');
~~~

Write through NSString with an explicit encoding and an NSError Ref. Do not rely on
console output as the artifact.

## The bridge has layers

- $() bridges a JavaScript scalar to an Objective-C argument.
- ObjC.unwrap turns an NSString, NSNumber, or boolean into a JavaScript scalar.
- ObjC.deepUnwrap recursively converts Foundation arrays and dictionaries.
- An absent dictionary property becomes an absent JavaScript property after deep unwrap;
  NSNull becomes null.
- A nil Objective-C proxy can be truthy in JavaScript. Test the returned object shape
  or unwrap it before dereferencing methods.

For JSON, let NSJSONSerialization parse the bytes, then deep-unpack exactly once:

~~~javascript
const data = $.NSData.dataWithContentsOfFile($(path));
const error = Ref();
const native = $.NSJSONSerialization.JSONObjectWithDataOptionsError(data, 0, error);
if (!native) throw new Error('invalid JSON');
const value = ObjC.deepUnwrap(native);
~~~

Drill: 248-jxa-json-bridge.

## Foundation primitives worth reaching for

| need | Foundation move | drill |
| --- | --- | --- |
| UTF-8 text | NSString.stringWithContentsOfFileEncodingError | 249 |
| byte count | NSData.dataUsingEncoding(...).length | 249 |
| path composition | NSString.stringByAppendingPathComponent | 250 |
| file size | NSFileManager.attributesOfItemAtPathError and NSFileSize | 250, 253 |
| exact dates | NSDateFormatter with POSIX locale and lenient=false | 251 |
| typed plist output | NSPropertyListSerialization | 252 |
| URL structure | NSURLComponents.componentsWithString | 254 |

## Text is not bytes

JavaScript string length counts UTF-16 code units. Array.from(text).length counts
Unicode code points, while NSData length counts bytes in a chosen encoding:

~~~javascript
const chars = Array.from(text).length;
const bytes = Number(ObjC.unwrap(
  $.NSString.stringWithString($(text))
    .dataUsingEncoding($.NSUTF8StringEncoding).length
));
~~~

Choose the unit in the output contract. Drill: 249-jxa-file-io.

## Dates must state their assumptions

For machine timestamps, set an en_US_POSIX locale, an explicit dateFormat, and
lenient=false. Parse the source offset first, then set the formatter timezone to UTC
for output. Do not use the host's local timezone as an implicit input rule. Epoch zero
is a valid number. Drill: 251-jxa-date-timezone.

## Paths and errors are data

Use Foundation path APIs rather than concatenating separators when the path is composed
from components. Use a fresh Ref for each NSError-producing call:

~~~javascript
const error = Ref();
const attrs = $.NSFileManager.defaultManager
  .attributesOfItemAtPathError($(path), error);
if (!attrs || typeof attrs.objectForKey !== 'function') {
  // expected missing-path branch
}
~~~

Do not print localized error text when the contract asks for a stable status. Drills:
250-jxa-path-inventory and 253-jxa-objc-errors.

## Do not hand-parse native formats

Use NSPropertyListSerialization for plist output and NSURLComponents for URL structure.
A file named report.plist is not a plist if it contains JSON text, and a URL containing
percent encoding is not safely split with string operations. Drills 252 and 254 carry
the semantic negatives.

## JXA checklist

1. Import only the Foundation classes the task needs.
2. Convert environment values and native scalars deliberately.
3. Keep nil, null, missing, zero, and empty text distinct.
4. Give every file read and write an explicit encoding.
5. Give every out-parameter call a fresh Ref and branch on failure.
6. Keep live automation out of a fixture-only drill.
7. Write only under OUT and make errors non-zero.

See references/jxa-gotchas.md for the compact behavior table. Prove the choices against
the macOS JXA track: 149 and 248-254.
