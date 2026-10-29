# What scripting is

Scripting is the layer of programming that exists to **answer a question** rather than
to **build a product**. It is the ten-minute program. It is written to be read once,
by you, on a bad day, and then deleted.

That is not a lesser form of engineering. It is a different one, with its own craft and
its own failure modes.

## The seven marks

**1. It has a deadline measured in minutes.** If you are still deciding on a structure
after five minutes, you have already failed the drill. The shape of the answer is
`read → transform → write`. Anything else is a product.

**2. Its lifetime is short and it knows it.** No versioning, no backwards compatibility,
no deprecation path. The script being deleted tomorrow is a *successful* script.

**3. It reads the real world and the real world is filthy.** UTF-8 with a BOM here, a
Windows CRLF there, a `null` where a number should be, an API that returns `200` with an
error body, a directory with three files named `final`, `final2`, and `final FINAL`.
Scripting is largely the discipline of *expecting* that, not being surprised by it.

**4. It composes other programs.** The language is a driver, not a platform. A good
script is mostly glue: `curl | jq`, `find | xargs`, `ffmpeg`, `git`, `rg`. Rewriting in
your language what a tool already does better is the classic scripting mistake.

**5. Correctness is about the answer, not the code.** The output must be right — that is
non-negotiable, and it is why this repo has verifiers. But the code need not be
maintainable, typed, tested, or abstracted.

**6. Failure is loud and early.** `set -euo pipefail`, explicit `raise`, exit non-zero
with the offending value printed. Silent `|| true` is how you get a confident wrong
answer, which is worse than an error.

**7. It is disposable, so the cost of a rewrite is near zero.** When the second
question arrives that is *almost* the first question, write the second script. Do not
generalise the first. Refactoring a script into a library is how a five-minute job
becomes a five-day one.

## What it is not

| It is not… | because |
| --- | --- |
| **systems programming** | no memory layout, no syscalls, no ABI, no perf budget. You are not writing the tool, you are calling it. |
| **low-level work** | the closest you get is `dd`, `strace`, or a hex dump — and even then you're driving someone else's binary. |
| **web development** | the HTTP you touch is a probe, not a service you own. Scraping is reading; there is no framework, no route, no deploy. |
| **data engineering** | no schemas, no orchestration, no idempotency guarantees. You need the number once. |
| **prototyping** | prototyping is a first draft of a product. Scripting may never become anything. That is fine. |

## The smell test

Ask: **"if this script is deleted in an hour, did anything of value disappear?"**

- "No, I got the answer." → scripting. Good.
- "Yes, we'd lose the pipeline." → not scripting any more. Go build the real thing.

The second answer arriving is not a failure. It is the normal graduation path. The error
is refusing to notice it.

## The anti-patterns

You have drifted out of scripting the moment you write:

- a base class, a protocol, or an interface
- an error hierarchy instead of exiting with a message
- a config file for a script you will run twice
- an argument parser for two positional arguments
- a retry/backoff framework instead of a `for` loop with `sleep`
- a test suite for a program with no callers
- "let me make this reusable" — before the second use exists
- a dependency you had to install to solve a problem your shell already solves

## The three questions before you type

1. **Does a tool already do this?** `jq`, `awk`, `rg`, `curl`, `find`, `ffmpeg`, `sqlite3`,
   `git`. If yes, the script is one line of glue.
2. **Which language is already on this box?** bash is on every Unix; python3 is on
   almost every Unix; pwsh is on Windows; lua is inside whatever embedded thing you're
   debugging. Reaching for the missing one costs an install.
3. **What is the output contract?** One file, one line, one exit code? Write that
   contract down before writing code — it is the only spec you get.
