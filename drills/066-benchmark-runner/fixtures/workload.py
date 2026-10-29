#!/usr/bin/env python3
"""Small deterministic workload used by the benchmark runner."""

import sys

case = sys.argv[1]
iterations = int(sys.argv[2])
if case == "loop":
    result = 0
    for value in range(iterations):
        result += (value * 17) % 97
elif case == "generator":
    result = sum((value * 17) % 97 for value in range(iterations))
else:
    raise SystemExit(f"unknown benchmark case: {case}")
print(result)
