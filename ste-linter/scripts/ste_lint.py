#!/usr/bin/env python3
"""ste_lint.py - a Simplified Technical English (ASD-STE100-inspired) linter.

Checks prose (plain text or markdown) against a practical subset of the
ASD-STE100 writing rules and controlled dictionary. This is not the official
specification (which is distributed by the ASD STEMG); it is a heuristic
linter inspired by its rules.

Usage:
    ste_lint.py [--format text|json|feedback] [file ...]

Reads stdin when no files are given. Exit code 1 when findings exist.
"""

import argparse
import json
import re
import sys

MAX_PROCEDURAL_WORDS = 20
MAX_DESCRIPTIVE_WORDS = 25
MAX_PARAGRAPH_SENTENCES = 6


def _verb_forms(base):
    if base.endswith("e"):
        return [base, base + "s", base + "d", base[:-1] + "ing"]
    if base.endswith("y") and len(base) > 2 and base[-2] not in "aeiou":
        return [base, base[:-1] + "ies", base[:-1] + "ied", base + "ing"]
    return [base, base + "s", base + "ed", base + "ing"]


def _expand(entries):
    words = {}
    for base, suggestion, expand in entries:
        forms = _verb_forms(base) if expand else [base]
        for form in forms:
            words[form] = suggestion
    return words


# Unapproved word -> approved alternative. Third field: expand verb forms.
UNAPPROVED_WORDS = _expand([
    # Modal verbs / tense (STE: use "must", "can", and the present tense)
    ("will", 'use the present tense (STE describes what the system does, not what it "will" do)', False),
    ("shall", '"must"', False),
    ("should", '"must" (if mandatory) or remove', False),
    ("would", "use the present tense", False),
    ("could", '"can"', False),
    ("might", '"can" or "possibly"', False),
    ("may", '"can"', False),
    # Common unapproved words
    ("utilize", '"use"', True),
    ("utilization", '"use"', False),
    ("commence", '"start"', True),
    ("terminate", '"stop" or "end"', True),
    ("termination", '"stop" or "end"', False),
    ("approximately", '"about"', False),
    ("sufficient", '"enough"', False),
    ("insufficient", '"not enough"', False),
    ("additional", '"more"', False),
    ("additionally", '"also"', False),
    ("accomplish", '"do"', True),
    ("attempt", '"try"', True),
    ("assist", '"help"', True),
    ("assistance", '"help"', False),
    ("demonstrate", '"show"', True),
    ("indicate", '"show"', True),
    ("ensure", '"make sure"', True),
    ("verify", '"make sure" or "test"', True),
    ("validate", '"make sure" or "test"', True),
    ("guarantee", '"make sure"', True),
    ("enable", '"let" or "make possible"', True),
    ("allow", '"let" or "permit"', True),
    ("provide", '"give" or "supply"', True),
    ("perform", '"do"', True),
    ("execute", '"do" or "start"', True),
    ("obtain", '"get"', True),
    ("retrieve", '"get" or "find"', True),
    ("facilitate", '"help" or "make easier"', True),
    ("leverage", '"use"', True),
    ("implement", '"make" or "do"', True),
    ("implementation", '"how it is made" (or a technical name)', False),
    ("require", '"need" or "must have"', True),
    ("comprise", '"include" or "have"', True),
    ("possess", '"have"', True),
    ("transmit", '"send"', True),
    ("notify", '"tell"', True),
    ("modify", '"change"', True),
    ("modification", '"change"', False),
    ("alter", '"change"', True),
    ("create", '"make"', True),
    ("creation", '"make" (rewrite as a verb)', False),
    ("functionality", '"function(s)"', False),
    ("functionalities", '"functions"', False),
    ("capability", '"function" or "what it can do"', False),
    ("capabilities", '"functions"', False),
    ("numerous", '"many"', False),
    ("multiple", '"many" or "more than one"', False),
    ("various", '"different"', False),
    ("appropriate", '"correct" or "applicable"', False),
    ("adequate", '"enough"', False),
    ("optimal", '"best"', False),
    ("initially", '"at the start"', False),
    ("currently", '"now" or "at this time"', False),
    ("previously", '"before"', False),
    ("subsequently", '"after that" or "then"', False),
    ("frequently", '"often" or "many times"', False),
    ("furthermore", '"also"', False),
    ("moreover", '"also"', False),
    ("however", '"but"', False),
    ("nevertheless", '"but"', False),
    ("therefore", '"thus" or "so"', False),
    ("whilst", '"while"', False),
    ("upon", '"on" or "when"', False),
    ("via", '"through" or "by"', False),
    ("regarding", '"about"', False),
    ("concerning", '"about"', False),
])

UNAPPROVED_PHRASES = [
    ("in order to", '"to"'),
    ("prior to", '"before"'),
    ("subsequent to", '"after"'),
    ("due to the fact that", '"because"'),
    ("in the event that", '"if"'),
    ("in the event of", '"if there is"'),
    ("a number of", '"some" or "many"'),
    ("as well as", '"and"'),
    ("with respect to", '"about" or "for"'),
    ("with regard to", '"about"'),
    ("in addition to", '"and" or "with"'),
    ("in addition", '"also"'),
    ("at this point in time", '"now"'),
    ("in conjunction with", '"with"'),
    ("in accordance with", '"as given in"'),
    ("is capable of", '"can"'),
    ("are capable of", '"can"'),
    ("is able to", '"can"'),
    ("are able to", '"can"'),
    ("has the ability to", '"can"'),
    ("have the ability to", '"can"'),
    ("make use of", '"use"'),
    ("makes use of", '"uses"'),
    ("take into account", '"think about"'),
    ("takes into account", '"thinks about"'),
    ("carry out", '"do"'),
    ("carries out", '"does"'),
    ("carried out", '"did"'),
    ("as per", '"as given in"'),
    ("e.g.", '"for example"'),
    ("i.e.", '"that is"'),
    ("etc.", '"and so on" (or complete the list)'),
]

IRREGULAR_PARTICIPLES = (
    "given|taken|made|done|seen|known|shown|written|built|sent|kept|held|"
    "found|brought|thought|chosen|driven|hidden|broken|begun|run|set|put|"
    "read|said|told|sold|paid|met|left|lost|meant|kept|sent|stored|used|"
    "understood|withdrawn|granted"
)

PASSIVE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being|am|get|gets|got)\s+"
    r"(?:(?:not|then|also|automatically|first|only)\s+)?"
    r"(\w+ed|" + IRREGULAR_PARTICIPLES + r")\b",
    re.IGNORECASE,
)
PROGRESSIVE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being|am)\s+(?:not\s+)?(\w+ing)\b",
    re.IGNORECASE,
)
CONTRACTION_RE = re.compile(
    r"\b(\w+n't|it's|let's|\w+'re|\w+'ve|\w+'ll|\w+'d)\b", re.IGNORECASE
)
NOUN_CLUSTER_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9]+[ \t]+){3,}[A-Z][A-Za-z0-9]+\b")
ANDOR_RE = re.compile(r"\b\w+/or\b|\band/\w+\b", re.IGNORECASE)
WORD_RE = re.compile(r"[A-Za-z0-9'-]+")
ING_ALLOWLIST = {
    "during", "nothing", "something", "anything", "everything", "string",
    "sibling", "warning", "setting", "settings", "existing", "following",
    "engineering", "being",
}


def strip_markdown(line):
    """Replace markdown syntax with spaces so columns stay aligned."""

    def blank(match):
        return " " * len(match.group(0))

    def keep_text(match):
        text = match.group(1)
        return " " + text + " " * (len(match.group(0)) - len(text) - 1)

    line = re.sub(r"`[^`]*`", blank, line)  # inline code
    line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", keep_text, line)  # links/images
    line = re.sub(r"^\s*#{1,6}\s", blank, line)  # heading markers
    line = re.sub(r"^\s*(?:[-*+]|\d+\.)\s", blank, line)  # list bullets
    line = re.sub(r"^\s*>\s?", blank, line)  # blockquotes
    line = line.replace("|", " ")  # table pipes
    line = re.sub(r"\*\*|__|(?<!\w)[*_](?!\s)|(?<!\s)[*_](?!\w)", " ", line)
    return line


def split_sentences(text):
    """Yield (offset, sentence) pairs from a paragraph of text."""
    protected = text
    for abbr in ("e.g.", "i.e.", "etc.", "vs.", "cf."):
        protected = protected.replace(abbr, abbr.replace(".", "\x00"))
    parts = re.split(r"(?<=[.!?])\s+", protected)
    offset = 0
    for part in parts:
        restored = part.replace("\x00", ".")
        idx = text.find(restored, offset)
        if idx < 0:
            idx = offset
        if restored.strip():
            yield idx, restored
        offset = idx + len(restored)


class Linter:
    def __init__(self):
        self.findings = []

    def add(self, rule, severity, line, col, message, excerpt):
        self.findings.append({
            "rule": rule,
            "severity": severity,
            "line": line,
            "col": col,
            "message": message,
            "excerpt": excerpt.strip(),
        })

    def lint(self, text):
        lines = text.splitlines()
        clean = []
        boundaries = []  # lines that start their own paragraph (bullets, headings)
        in_fence = False
        for raw in lines:
            if raw.lstrip().startswith("```"):
                in_fence = not in_fence
                clean.append("")
                boundaries.append(False)
                continue
            clean.append("" if in_fence else strip_markdown(raw))
            boundaries.append(
                not in_fence
                and bool(re.match(r"\s*(?:[-*+]\s|\d+\.\s|#{1,6}\s|\|)", raw))
            )

        for i, line in enumerate(clean, start=1):
            self._lint_words(i, line)

        for para in self._paragraphs(clean, boundaries):
            self._lint_paragraph(para)

        self.findings.sort(key=lambda f: (f["line"], f["col"]))
        return self.findings

    def _lint_words(self, lineno, line):
        lowered = line.lower()
        for phrase, suggestion in UNAPPROVED_PHRASES:
            start = 0
            while True:
                idx = lowered.find(phrase, start)
                if idx < 0:
                    break
                before_ok = idx == 0 or not lowered[idx - 1].isalnum()
                end = idx + len(phrase)
                after_ok = end >= len(lowered) or not lowered[end].isalnum()
                if before_ok and after_ok:
                    self.add(
                        "unapproved-phrase", "warning", lineno, idx + 1,
                        'Unapproved phrase "%s": use %s.' % (phrase, suggestion),
                        line[idx:end],
                    )
                start = end
        for match in WORD_RE.finditer(line):
            word = match.group(0).lower()
            if word in UNAPPROVED_WORDS:
                self.add(
                    "unapproved-word", "warning", lineno, match.start() + 1,
                    'Unapproved word "%s": use %s.'
                    % (match.group(0), UNAPPROVED_WORDS[word]),
                    match.group(0),
                )
        for match in CONTRACTION_RE.finditer(line):
            self.add(
                "contraction", "warning", lineno, match.start() + 1,
                'Do not use contractions: write "%s" in full.' % match.group(0),
                match.group(0),
            )
        for match in ANDOR_RE.finditer(line):
            self.add(
                "and-or", "warning", lineno, match.start() + 1,
                'Do not use "and/or". Write the applicable alternatives fully.',
                match.group(0),
            )
        for match in NOUN_CLUSTER_RE.finditer(line):
            words = match.group(0).split()
            if len(words) >= 4:
                self.add(
                    "noun-cluster", "warning", lineno, match.start() + 1,
                    "Possible noun cluster of %d words. Do not use clusters of "
                    "more than 3 nouns; break it up with prepositions."
                    % len(words),
                    match.group(0),
                )
        idx = line.find(";")
        if idx >= 0:
            self.add(
                "semicolon", "warning", lineno, idx + 1,
                "Do not use semicolons. Write two short sentences.",
                line.strip()[:60],
            )

    def _paragraphs(self, clean_lines, boundaries):
        """Group lines into paragraphs: lists of (lineno, text) items.

        Blank lines end a paragraph; list items, headings, and table rows
        each start their own paragraph (STE's paragraph rules apply to
        prose, not to a whole bullet list).
        """
        para = []
        for i, line in enumerate(clean_lines, start=1):
            if not line.strip():
                if para:
                    yield para
                    para = []
                continue
            if boundaries[i - 1] and para:
                yield para
                para = []
            para.append((i, line.strip()))
        if para:
            yield para

    def _lint_paragraph(self, para):
        first_line = para[0][0]
        text = " ".join(t for _, t in para)
        # Map offsets in the joined text back to line numbers.
        bounds = []
        pos = 0
        for lineno, t in para:
            bounds.append((pos, lineno))
            pos += len(t) + 1

        def line_of(offset):
            result = first_line
            for start, lineno in bounds:
                if offset >= start:
                    result = lineno
            return result

        sentences = list(split_sentences(text))
        if len(sentences) > MAX_PARAGRAPH_SENTENCES:
            self.add(
                "paragraph-length", "error", first_line, 1,
                "Paragraph has %d sentences (maximum %d). Split it."
                % (len(sentences), MAX_PARAGRAPH_SENTENCES),
                text[:60] + "...",
            )
        for offset, sentence in sentences:
            lineno = line_of(offset)
            words = WORD_RE.findall(sentence)
            if len(words) > MAX_DESCRIPTIVE_WORDS:
                self.add(
                    "sentence-length", "error", lineno, 1,
                    "Sentence has %d words (maximum %d for descriptive text). "
                    "Split it into shorter sentences."
                    % (len(words), MAX_DESCRIPTIVE_WORDS),
                    sentence[:80] + ("..." if len(sentence) > 80 else ""),
                )
            elif len(words) > MAX_PROCEDURAL_WORDS:
                self.add(
                    "sentence-length", "warning", lineno, 1,
                    "Sentence has %d words (maximum %d for procedures). Split "
                    "it if it is an instruction." % (len(words), MAX_PROCEDURAL_WORDS),
                    sentence[:80] + ("..." if len(sentence) > 80 else ""),
                )
            for match in PASSIVE_RE.finditer(sentence):
                self.add(
                    "passive-voice", "error", lineno, 1,
                    'Passive voice ("%s"): use the active voice. Name who or '
                    "what does the action." % match.group(0),
                    match.group(0),
                )
            for match in PROGRESSIVE_RE.finditer(sentence):
                if match.group(2).lower() in ING_ALLOWLIST:
                    continue
                self.add(
                    "progressive-tense", "error", lineno, 1,
                    'Progressive tense ("%s"): use the simple present tense.'
                    % match.group(0),
                    match.group(0),
                )
            first_word = words[0].lower() if words else ""
            if (
                first_word.endswith("ing")
                and len(first_word) > 4
                and first_word not in ING_ALLOWLIST
            ):
                self.add(
                    "ing-form", "warning", lineno, 1,
                    'Sentence starts with the -ing form "%s". Rewrite with a '
                    "finite verb (for example: \"When you X...\" or an "
                    "imperative)." % words[0],
                    sentence[:60],
                )


def format_text(findings, filename):
    out = []
    for f in findings:
        out.append(
            "%s:%d:%d: [%s] %s (%s)"
            % (filename, f["line"], f["col"], f["severity"], f["message"], f["rule"])
        )
    counts = summarize(findings)
    out.append("")
    out.append(
        "%d findings (%d errors, %d warnings)"
        % (len(findings), counts["errors"], counts["warnings"])
    )
    return "\n".join(out)


def format_feedback(findings, filename):
    """Markdown feedback suitable to hand to a writer for revision."""
    counts = summarize(findings)
    out = [
        "# Simplified Technical English (ASD-STE100) review: %s" % filename,
        "",
        "%d findings: %d errors, %d warnings."
        % (len(findings), counts["errors"], counts["warnings"]),
        "",
    ]
    by_rule = {}
    for f in findings:
        by_rule.setdefault(f["rule"], []).append(f)
    titles = {
        "sentence-length": "Sentence length",
        "paragraph-length": "Paragraph length",
        "passive-voice": "Passive voice",
        "progressive-tense": "Progressive tense",
        "unapproved-word": "Unapproved words",
        "unapproved-phrase": "Unapproved phrases",
        "contraction": "Contractions",
        "noun-cluster": "Noun clusters",
        "and-or": "and/or",
        "semicolon": "Semicolons",
        "ing-form": "-ing sentence openers",
    }
    for rule in titles:
        if rule not in by_rule:
            continue
        items = by_rule[rule]
        out.append("## %s (%d)" % (titles[rule], len(items)))
        out.append("")
        for f in items:
            out.append('- line %d: %s — `%s`' % (f["line"], f["message"], f["excerpt"]))
        out.append("")
    return "\n".join(out)


def summarize(findings):
    return {
        "errors": sum(1 for f in findings if f["severity"] == "error"),
        "warnings": sum(1 for f in findings if f["severity"] == "warning"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="files to lint (stdin if none)")
    parser.add_argument(
        "--format", choices=["text", "json", "feedback"], default="text"
    )
    args = parser.parse_args()

    sources = []
    if args.files:
        for path in args.files:
            with open(path, encoding="utf-8") as fh:
                sources.append((path, fh.read()))
    else:
        sources.append(("<stdin>", sys.stdin.read()))

    any_findings = False
    results = []
    for name, text in sources:
        findings = Linter().lint(text)
        any_findings = any_findings or bool(findings)
        if args.format == "json":
            results.append({
                "file": name,
                "summary": summarize(findings),
                "findings": findings,
            })
        elif args.format == "feedback":
            print(format_feedback(findings, name))
        else:
            print(format_text(findings, name))
    if args.format == "json":
        print(json.dumps(results, indent=2))
    sys.exit(1 if any_findings else 0)


if __name__ == "__main__":
    main()
