---
name: ste-linter
description: Lint prose against Simplified Technical English (ASD-STE100) rules. Use when the user asks to check, lint, or simplify technical writing (specs, manuals, procedures, docs) for STE compliance, or mentions ASD-STE100 or Simplified Technical English.
---

# Simplified Technical English Linter

Lint technical prose against a practical subset of the ASD-STE100 writing
rules: sentence length (20 words procedural / 25 descriptive), paragraph
length (6 sentences), active voice, simple present tense, no contractions,
no noun clusters over 3 nouns, and a controlled dictionary of unapproved
words and phrases with approved alternatives.

## Running the linter

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ste_lint.py [--format text|json|feedback] <file.md ...>
```

- No dependencies; Python 3 stdlib only. Reads stdin when no files are given.
- Exit code is 1 when there are findings, 0 when clean.
- `--format text` (default): one finding per line with `file:line:col`.
- `--format json`: machine-readable findings plus an error/warning summary.
- `--format feedback`: markdown grouped by rule — use this when handing the
  findings to a writer (or another agent) to revise the document.

## Workflow

1. Run the linter with `--format feedback` on the document.
2. Revise the document to resolve each finding. Keep the meaning; change the
   wording. Typical fixes:
   - Split long sentences; one instruction or idea per sentence.
   - Rewrite passive voice with the actor as the subject ("The API returns…").
   - Replace "will/shall/should/may" with the present tense, "must", or "can".
   - Substitute the suggested approved word ("utilize" → "use").
   - Break noun clusters apart with prepositions.
3. Re-run the linter until clean or until the remaining findings are false
   positives (the checks are heuristic — judge each finding; do not contort
   correct prose to silence a wrong one).

## Caveats

This is an STE-inspired heuristic subset, not the official ASD-STE100
specification. The official spec and full dictionary are distributed by the
ASD STEMG (https://www.asd-ste100.org). Domain-specific technical names and
technical verbs are allowed by STE and may still be flagged here — treat
those findings as ignorable.
