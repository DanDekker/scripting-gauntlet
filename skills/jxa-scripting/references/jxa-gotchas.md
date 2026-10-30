# JXA gotcha cheat sheet

| situation | quiet failure | reliable move |
| --- | --- | --- |
| JSON object | Foundation containers are not plain JS objects | NSJSONSerialization, then ObjC.deepUnwrap |
| null versus missing | truthiness collapses both | hasOwnProperty and value === null |
| nil Foundation result | a nil proxy can look truthy | ObjC.unwrap or test the expected method shape |
| NSError | the error is an out-parameter | allocate Ref() for every call |
| file read | default encoding is an assumption | NSString with NSUTF8StringEncoding |
| character count | string length counts UTF-16 units | Array.from(text).length |
| byte count | character count is not storage size | NSData length after explicit encoding |
| paths | string concatenation misses Foundation rules | stringByAppendingPathComponent |
| plist | filename extension does not serialize types | NSPropertyListSerialization |
| dates | local locale/timezone and leniency change results | POSIX locale, explicit format, lenient=false |
| URLs | split and percent encoding are easy to get wrong | NSURLComponents |

## Stable output helpers

Keep CSV quoting in a small helper, and always end a text artifact with the contract's
newline. For JSON, JSON.stringify is fine after values have been converted to ordinary
JavaScript. For plist output, pass the native Foundation graph to the plist serializer
instead of stringifying it.

## Platform boundary

JXA solutions are skipped by the harness outside macOS. A Python twin can prove the
semantic contract on every host, but it does not prove that the Foundation bridge call
is spelled correctly. Calibrate the JXA solution on macOS.
