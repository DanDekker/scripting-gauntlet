# 149-macos-plist-audit

> "These app bundles claim different privacy permissions. Give me a small inventory
> before I approve the set."

## Task

`in/apps.plist` is a synthetic macOS XML property list with an `Apps` array. Each app
may have `CFBundleIdentifier`, `CFBundleShortVersionString`,
`NSCameraUsageDescription`, and `NSMicrophoneUsageDescription`. Read the file without
changing it. No live system inventory or network access is needed.

## Rules

1. A record is valid only if its bundle identifier and version are nonempty strings
   after trimming whitespace. Count invalid records as `skipped`.
2. For a valid record, a nonempty trimmed `NSCameraUsageDescription` means `camera`;
   a nonempty trimmed `NSMicrophoneUsageDescription` means `microphone`. Check both
   independently. A record with neither is omitted from `apps`, but not skipped.
3. Sort permission names alphabetically. Sort reported apps by bundle identifier
   ascending. Preserve the trimmed identifier and version.

## Output

Write `out/report.json` with exactly `apps` and `skipped`. `apps` is an array of objects
with exactly `id`, `version`, and `permissions`:

```json
{"apps":[{"id":"com.example.capture","version":"2.4.1","permissions":["camera","microphone"]}],"skipped":2}
```

The example shows the shape, not the full expected inventory. No extra keys or files.

## Messes to expect

- one app declares both camera and microphone
- blank usage descriptions that do not grant a permission
- a valid app with no requested permissions
- missing identifiers or versions

## Timebox

4 minutes. The JXA reference uses macOS Foundation to parse the property list; it
runs only on macOS. The Python reference uses the standard library and is portable.
