# 064-cpu-inventory

> "I'm comparing three server pools. Turn the CPU reports into one small table so I
> can see physical cores and schedulable CPUs side by side."

## Task

Read captured CPU reports from Linux `lscpu`, macOS `sysctl`, and Windows
`Get-CimInstance Win32_Processor` plus `Get-ComputerInfo`. Normalize all three.

## Rules

1. Linux physical cores are `Core(s) per socket` multiplied by `Socket(s)`;
   logical CPUs are `CPU(s)`.
2. macOS uses `hw.physicalcpu`, `hw.logicalcpu`, and
   `machdep.cpu.brand_string` from `sysctl`.
3. Windows JSON has a `processors` array. Sum `NumberOfCores` and
   `NumberOfLogicalProcessors` across its records. Use the first record's `Name` as
   the model. `CsSystemType` gives the architecture.
4. `threads_per_core` is `logical_cpus / physical_cores`, an integer for these inputs.
   Normalize architecture to `x86_64` or `arm64`.
5. Sort rows by `platform` ascending in byte order.

## Output

**`out/cpus.csv`** — header `platform,processor,physical_cores,logical_cpus,threads_per_core,architecture`, one row each for Linux, macOS, and Windows.

**`out/summary.json`** — exactly `hosts`, `physical_cores`, and `logical_cpus`, all integers summed across the three snapshots.

## Messes to expect

- Linux and macOS use colon-separated key/value output with uneven spacing
- Linux core count needs multiplication across sockets
- Windows returns one object per socket, so counts must be summed
- Windows uses `x64-based PC` while Unix reports `x86_64` or `arm64`

## Timebox

4 minutes. All snapshots are inputs, so the report is repeatable on Windows, macOS,
and Linux regardless of the host running your script.
