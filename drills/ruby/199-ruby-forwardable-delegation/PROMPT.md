# 199-ruby-forwardable-delegation

> "An in-memory configuration store must expose read-only inspection methods (`size`, `keys`, `get`)
> to external components while strictly protecting internal state against arbitrary deletion.
> Subclassing `Hash` leaked the raw `delete` method; we must encapsulate the store using Ruby's `Forwardable`."

## Input

`in/actions.txt` — sequence of registry actions:

```
add cpu 4
add mem 16
get cpu
add disk 500
get mem
size
keys
delete disk
get disk
```

Blank lines and `#` comments are skipped.

## Rules

1. Define a class `SecureRegistry` using `require 'forwardable'`:
   - `extend Forwardable`
   - Delegate `keys`, `values`, `size` to `@store` via `def_delegators :@store, :keys, :values, :size`.
   - Provide `add(key, val)` to populate `@store`.
   - Provide `lookup(key)` that increments `@reads` counter and returns `@store[key]`.
   - **Do not delegate `delete`**: attempting to call `reg.delete(key)` must raise `NoMethodError`.
2. Process actions sequentially:
   - `add <key> <val>`: `status = ok`, `result = <key>=<val>`
   - `get <key>`: `status = ok`, `result = <val>`
   - `size`: `status = ok`, `result = <size>`
   - `keys`: `status = ok`, `result = <sorted keys joined with ;>`
   - `delete <key>`: call `reg.delete(key)` inside begin/rescue `NoMethodError`. When blocked: `status = blocked`, `result = NoMethodError`.
3. Track total `reads` (each `get` action increments read counter by 1).

## Output

Write exactly these files to `$OUT`:

1. **`out/audit.csv`** — header `step,op,status,result`, in action order.
2. **`out/summary.json`** — keys `steps`, `reads`, `blocked`, `final_size`. One compact JSON object:
   `{"steps":9,"reads":3,"blocked":1,"final_size":3}`.

## Messes to expect

- If `SecureRegistry` subclasses `Hash`, `delete` succeeds and removes `disk`, causing the next `get disk` to return empty.
- Keys must be sorted alphabetically in the `keys` output.

## Timebox

Four minutes. Use `extend Forwardable` and `def_delegators`.
