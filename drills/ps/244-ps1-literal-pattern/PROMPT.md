# 244-ps1-literal-pattern

> "Each row gives a service name and a rule that should match that exact spelling.
> Some names contain regex punctuation. Tell me which rules match literally."

## Input

in/services.csv has columns name and rule. Surrounding whitespace in either field is
not part of the value. A rule is a literal, case-sensitive whole-string match.

The fixture includes dots, plus signs, brackets, question marks, and a case mismatch.

## Rules

1. Trim name and rule.
2. Match the entire name against the entire rule using ordinal, case-sensitive
   semantics.
3. Treat every regex metacharacter in the rule as ordinary text.
4. Emit every input row in input order with match equal to yes or no.

## Output

Write exactly:

1. out/matches.csv with header name,rule,match.
2. out/summary.json with exactly {"matched":5,"unmatched":5}.

## Messes to expect

- api.v2 must not match apiXv2
- worker+ is a literal plus, not a one-or-more regex quantifier
- cache[1] is not a character class
- proxy? includes a literal question mark
- PowerShell -match is case-insensitive and regex-based unless you choose otherwise

## Timebox

Four minutes. If you use a regex operator, escape the user rule and anchor both ends;
String.Equals with Ordinal is also valid.
