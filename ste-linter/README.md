# ste-linter

A Simplified Technical English (ASD-STE100-inspired) linter for technical
prose, packaged as a Claude Code plugin.

## What it checks

**Structural rules (errors):**
- Sentences over 25 words (warning over 20, the procedural limit)
- Paragraphs over 6 sentences
- Passive voice ("is stored", "are met")
- Progressive tense ("is checking")

**Dictionary and style rules (warnings):**
- ~90 unapproved words with approved alternatives ("utilize" → "use",
  "shall" → "must", "will" → present tense)
- ~30 unapproved phrases ("in order to" → "to", "prior to" → "before")
- Contractions ("it's", "don't")
- Noun clusters of more than 3 nouns
- "and/or", semicolons, sentence-initial -ing forms

Markdown is understood: code fences and inline code are skipped, and link
syntax, bullets, and table pipes are ignored.

## Usage

```bash
# Human-readable findings
python3 scripts/ste_lint.py document.md

# Markdown feedback grouped by rule (for handing to a writer or agent)
python3 scripts/ste_lint.py --format feedback document.md

# Machine-readable
python3 scripts/ste_lint.py --format json document.md

# From stdin
cat document.md | python3 scripts/ste_lint.py
```

Exit code 1 when findings exist, 0 when clean. Python 3 stdlib only.

## Installation

```bash
claude plugin install ste-linter@faire
```

The included `ste-linter` skill teaches Claude to run the linter and apply
its feedback when you ask for an STE check.

## Caveats

This is a heuristic subset inspired by ASD-STE100, not the official
specification. The official spec and its ~900-word controlled dictionary are
distributed by the ASD STEMG (https://www.asd-ste100.org). The checks are
regex-based: expect occasional false positives (for example, technical names
that look like noun clusters, or adjectives that look like passives). Judge
findings rather than applying them blindly.
