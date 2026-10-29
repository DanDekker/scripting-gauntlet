# 139-rag-triplet-eval

> "We ship a RAG pipeline on Monday. Before that I want to know *where* it is broken on the
> last batch of queries - the retriever missing, the model inventing things, or the answer
> being fine but not answering the question."

## Input

`in/rag_cases.jsonl` - one JSON object per line:

```json
{"case_id": "rag-1", "query": "What is the timeout?", "context": "The system timeout is 30 seconds by default.", "answer": "The timeout is 30s.", "ground_truth": "30 seconds", "context_keywords": ["timeout", "30 seconds"], "answer_keywords": ["30s", "timeout"]}
```

- `case_id` - case identifier (string; a line without a string `case_id` is not a case)
- `context` - what the retriever returned
- `answer` - what the model said
- `ground_truth` - the reference span; may be missing
- `context_keywords` - list of strings that should be present in a relevant context
- `answer_keywords` - list of strings the grounded answer needs the context to contain

A missing `context`, `answer`, keyword list or `answer` is treated as the empty string /
empty list.

## Rules

1. **Skip junk.** Blank lines, lines that are not valid JSON, lines that are JSON but not an
   object, and objects without a string `case_id` are skipped and **not counted anywhere**.
2. **Normalize before matching.** Trim surrounding whitespace from every keyword and from
   `ground_truth`; all string matching is case-insensitive substring containment.
3. **Three binary scores**, each `1` or `0`:

   | column | 1 when | 0 when |
   | --- | --- | --- |
   | `context_rel` | at least **half** of `context_keywords` appear in `context`; an empty list scores 1 | fewer than half match |
   | `grounded` | **every** `answer_keywords` entry appears in `context`; an empty list scores 1 | at least one is missing from the context |
   | `answer_rel` | `answer` contains `ground_truth`; a missing or empty `ground_truth` scores 0 | it does not contain it |

   "Half" means `2 * matched >= keyword_count`, so 1 of 2 passes and 1 of 3 does not.
4. **Verdict.** `pass` only when all three scores are 1, otherwise `fail`.
5. **Issue**, first rule that applies wins:

   | issue | when |
   | --- | --- |
   | `bad_retrieval` | `context_rel` is 0 |
   | `hallucination` | `context_rel` is 1 and `grounded` is 0 |
   | `poor_answer` | `context_rel` and `grounded` are 1 and `answer_rel` is 0 |
   | `none` | all three are 1 (a `pass`) |

   So a case that fails retrieval **and** is ungrounded is `bad_retrieval`.

## Output

Write exactly these files to `$OUT`:

1. **`out/eval.csv`** - header `case_id,context_rel,grounded,answer_rel,verdict,issue`, one
   row per case, sorted by `case_id` ascending **lexicographically** - so `rag-10` sorts
   before `rag-2`. Scores are the literal `1` or `0`.
2. **`out/summary.json`** - an object with exactly these keys:
   - `total_cases` (int)
   - `passed` (int), `failed` (int) - they must add up to `total_cases`
   - `pass_rate` (float) - `passed / total_cases` rounded to 4 decimals, `0` when there are
     no cases
   - `hallucinations` (int), `bad_retrievals` (int), `poor_answers` (int) - counts of those
     issue labels (`none` is not counted)

## Messes to expect

- `rag-1` has `30s` as an answer keyword but the context says `30 seconds`: substring
  matching makes that ungrounded, and `30 seconds` is not in the answer either - it lands
  on `hallucination` because grounding is checked before the answer
- `rag-2` retrieved an unrelated context: `bad_retrieval` even though the answer is also bad
- `rag-5` answers with an empty string and `rag-6` has no `ground_truth` at all: both fail
  `answer_rel` rather than being skipped
- `rag-7` has empty keyword lists: those two scores default to 1
- `rag-8` is mixed case with a padded keyword (` timeout `) and a padded `ground_truth`
- `rag-9` matches 1 of 3 context keywords (33%): `bad_retrieval`; `rag-10` matches 2 of 4
  (50%): a pass
- `rag-4` pads its answer with spaces on both sides
- the file also has blank lines, a truncated JSON line, a bare array, and an object with no
  `case_id` - four lines that are not cases

## Timebox

Five minutes. If you are past that, the approach is wrong.
