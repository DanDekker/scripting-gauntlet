# 194-ruby-keyword-arguments

> "Our service registry resolves network endpoint configurations through a Ruby builder method.
> When configurations explicitly specify `path: null` (for root host-only routing) or `timeout: null`
> (for infinite streaming), naive code replaced them with default values `"/"` and `30`."

## Input

`in/endpoints.json` — array of endpoint specification objects:

```json
[
  { "id": 1, "host": "api.internal", "port": 9000, "path": "/v1", "timeout": 15 },
  { "id": 2, "host": "auth.internal" },
  { "id": 3, "host": "metrics.internal", "path": null, "timeout": null },
  { "id": 4, "host": "db.internal", "port": 5432, "timeout": 60 },
  { "id": 5, "port": 80 }
]
```

## Rules

Implement an endpoint builder with Ruby keyword arguments:
`def build_endpoint(host:, port: 8080, path: "/", timeout: 30)`

1. Forward configuration parameters to `build_endpoint` using keyword arguments (`**kwargs`).
2. If `host` is missing from the record, catching `ArgumentError` marks `status = missing_host`, `url = ""`, `timeout = ""`.
3. If valid:
   - `status = valid`
   - `url = "http://#{host}:#{port}#{path || ''}"`
     (Notice: if `path` is `nil`, the URL path is empty string `http://metrics.internal:8080`)
   - `timeout`: string representation of `timeout`, or empty string `""` if `timeout` is `nil`.
4. Preserve explicit `nil` overrides: when `path: nil` or `timeout: nil` is explicitly provided, it must not be replaced by defaults `"/"` or `30`.

## Output

Write exactly these files to `$OUT`:

1. **`out/endpoints.csv`** — header `id,status,url,timeout`.
2. **`out/summary.json`** — keys `endpoints`, `valid`, `missing_host`, `null_overrides`.
   One compact JSON object:
   `{"endpoints":5,"valid":4,"missing_host":1,"null_overrides":1}`.

## Messes to expect

- Passing `path: nil` to `path: "/"` yields `path = nil` inside the method. Naive `path || "/"` replaces `nil` with `"/"`.
- Record 5 has no `host:`, triggering `ArgumentError: missing keyword`.

## Timebox

Four minutes. Define `build_endpoint(host:, port: 8080, path: "/", timeout: 30)` and pass `**kwargs`.
