#!/usr/bin/env python3
"""Build the before/after HTML report for the STE linter evaluation.

Reads baseline.md, revised.md, *.findings.json, and feedback.md from this
directory and writes report.html: summary stats, findings by rule, and a
two-pane word-level diff with changes highlighted.
"""

import difflib
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent

RULE_TITLES = {
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


def tokens(text):
    return re.findall(r"\S+|\s+", text)


def word_diff(a_text, b_text):
    """Return (left_html, right_html) with del/ins spans."""
    a, b = tokens(a_text), tokens(b_text)
    left, right = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        a_chunk = html.escape("".join(a[i1:i2]))
        b_chunk = html.escape("".join(b[j1:j2]))
        if op == "equal":
            left.append(a_chunk)
            right.append(b_chunk)
        else:
            if a_chunk:
                left.append(f"<del>{a_chunk}</del>")
            if b_chunk:
                right.append(f"<ins>{b_chunk}</ins>")
    return "".join(left), "".join(right)


def by_rule(findings):
    counts = {}
    for f in findings:
        counts[f["rule"]] = counts.get(f["rule"], 0) + 1
    return counts


def finding_rows(findings, limit=None):
    rows = []
    for f in findings[:limit]:
        rows.append(
            "<li><span class='fline'>line {line}</span> "
            "<span class='sev sev-{severity}'>{severity}</span> {msg} "
            "<code>{excerpt}</code></li>".format(
                line=f["line"],
                severity=f["severity"],
                msg=html.escape(f["message"]),
                excerpt=html.escape(f["excerpt"][:70]),
            )
        )
    return "\n".join(rows)


def main():
    baseline = (HERE / "baseline.md").read_text()
    revised = (HERE / "revised.md").read_text()
    before = json.loads((HERE / "baseline.findings.json").read_text())[0]
    after = json.loads((HERE / "revised.findings.json").read_text())[0]

    left_html, right_html = word_diff(baseline, revised)
    b_counts, a_counts = by_rule(before["findings"]), by_rule(after["findings"])
    b_total, a_total = len(before["findings"]), len(after["findings"])
    reduction = round(100 * (1 - a_total / b_total)) if b_total else 0

    rule_rows = "\n".join(
        "<tr><td>{}</td><td class='num'>{}</td><td class='num'>{}</td></tr>".format(
            RULE_TITLES.get(rule, rule), b_counts.get(rule, 0), a_counts.get(rule, 0)
        )
        for rule in RULE_TITLES
        if b_counts.get(rule) or a_counts.get(rule)
    )

    page = TEMPLATE.format(
        b_total=b_total,
        b_err=before["summary"]["errors"],
        b_warn=before["summary"]["warnings"],
        a_total=a_total,
        a_err=after["summary"]["errors"],
        a_warn=after["summary"]["warnings"],
        reduction=reduction,
        rule_rows=rule_rows,
        left=left_html,
        right=right_html,
        before_list=finding_rows(before["findings"]),
        after_list=finding_rows(after["findings"]) or "<li>None.</li>",
    )
    (HERE / "report.html").write_text(page)
    print("wrote", HERE / "report.html")


TEMPLATE = """\
<title>STE Linter Evaluation — GitForge Spec</title>
<style>
  :root {{
    --paper: #F7F6F2; --ink: #1C2430; --muted: #5A6472; --line: #D9D6CC;
    --accent: #2456A6; --panel: #FFFFFF;
    --del-bg: #F6E2DF; --del-ink: #8C2B24; --ins-bg: #E1EFDF; --ins-ink: #275C34;
    --err: #B3382F; --warn: #9A6B1F; --err-bg: #F6E2DF; --warn-bg: #F3EAD4;
  }}
  @media (prefers-color-scheme: dark) {{ :root {{
    --paper: #141A22; --ink: #E4E7EB; --muted: #98A2AF; --line: #2C3542;
    --accent: #7FA8E8; --panel: #1B222D;
    --del-bg: #45211F; --del-ink: #F0A9A2; --ins-bg: #1F3A26; --ins-ink: #A4D8AC;
    --err: #F0A9A2; --warn: #E4C078; --err-bg: #45211F; --warn-bg: #3A3120;
  }} }}
  :root[data-theme="light"] {{
    --paper: #F7F6F2; --ink: #1C2430; --muted: #5A6472; --line: #D9D6CC;
    --accent: #2456A6; --panel: #FFFFFF;
    --del-bg: #F6E2DF; --del-ink: #8C2B24; --ins-bg: #E1EFDF; --ins-ink: #275C34;
    --err: #B3382F; --warn: #9A6B1F; --err-bg: #F6E2DF; --warn-bg: #F3EAD4;
  }}
  :root[data-theme="dark"] {{
    --paper: #141A22; --ink: #E4E7EB; --muted: #98A2AF; --line: #2C3542;
    --accent: #7FA8E8; --panel: #1B222D;
    --del-bg: #45211F; --del-ink: #F0A9A2; --ins-bg: #1F3A26; --ins-ink: #A4D8AC;
    --err: #F0A9A2; --warn: #E4C078; --err-bg: #45211F; --warn-bg: #3A3120;
  }}
  body {{
    background: var(--paper); color: var(--ink);
    font-family: Charter, Georgia, "Times New Roman", serif;
    line-height: 1.55; margin: 0; padding: 2.5rem 1.25rem 4rem;
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; }}
  .eyebrow {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.72rem;
    color: var(--accent); font-weight: 600;
  }}
  h1 {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: clamp(1.6rem, 3.5vw, 2.2rem); font-weight: 700;
    margin: 0.2rem 0 0.4rem; text-wrap: balance;
  }}
  .lede {{ color: var(--muted); max-width: 62ch; margin: 0 0 2rem; }}
  h2 {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 1.05rem; text-transform: uppercase; letter-spacing: 0.08em;
    border-top: 2px solid var(--ink); padding-top: 0.6rem; margin: 2.8rem 0 0.9rem;
  }}
  .stats {{ display: flex; flex-wrap: wrap; gap: 0.9rem; }}
  .stat {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 4px;
    padding: 0.8rem 1.1rem; min-width: 9.5rem; flex: 1;
  }}
  .stat .label {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: var(--muted);
  }}
  .stat .value {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 1.9rem; font-weight: 700; font-variant-numeric: tabular-nums;
  }}
  .stat .sub {{ font-size: 0.85rem; color: var(--muted); }}
  .stat.good .value {{ color: var(--ins-ink); }}
  table {{ border-collapse: collapse; width: 100%; max-width: 34rem; }}
  th, td {{
    text-align: left; padding: 0.35rem 0.9rem 0.35rem 0;
    border-bottom: 1px solid var(--line); font-size: 0.95rem;
  }}
  th {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: var(--muted);
  }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .diff {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
  @media (max-width: 900px) {{ .diff {{ grid-template-columns: 1fr; }} }}
  .pane {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 4px;
    overflow: hidden;
  }}
  .pane h3 {{
    margin: 0; padding: 0.55rem 0.9rem;
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;
    border-bottom: 1px solid var(--line); color: var(--muted);
  }}
  .pane pre {{
    margin: 0; padding: 0.9rem; white-space: pre-wrap; overflow-wrap: break-word;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    font-size: 0.78rem; line-height: 1.6; max-height: 70vh; overflow-y: auto;
  }}
  del {{ background: var(--del-bg); color: var(--del-ink); text-decoration: line-through; text-decoration-thickness: 1px; border-radius: 2px; }}
  ins {{ background: var(--ins-bg); color: var(--ins-ink); text-decoration: none; border-radius: 2px; }}
  .legend {{ font-size: 0.85rem; color: var(--muted); margin: 0.5rem 0 1rem; }}
  .legend del, .legend ins {{ padding: 0 0.25rem; }}
  ul.findings {{ list-style: none; padding: 0; margin: 0; }}
  ul.findings li {{
    padding: 0.4rem 0; border-bottom: 1px solid var(--line); font-size: 0.9rem;
  }}
  ul.findings code, .fline {{
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    font-size: 0.78rem;
  }}
  .fline {{ color: var(--muted); margin-right: 0.4rem; }}
  ul.findings code {{ background: var(--panel); border: 1px solid var(--line); border-radius: 3px; padding: 0.05rem 0.3rem; }}
  .sev {{
    font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.08em;
    border-radius: 3px; padding: 0.1rem 0.35rem; font-weight: 600;
  }}
  .sev-error {{ background: var(--err-bg); color: var(--err); }}
  .sev-warning {{ background: var(--warn-bg); color: var(--warn); }}
  details summary {{
    cursor: pointer; font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
    font-size: 0.9rem; color: var(--accent); margin: 0.6rem 0;
  }}
  p {{ max-width: 68ch; }}
</style>
<div class="wrap">
  <div class="eyebrow">ste-linter evaluation &middot; ASD-STE100</div>
  <h1>Simplified Technical English: before &amp; after</h1>
  <p class="lede">Claude (via the Claude Agent SDK) wrote a tech spec for
  <strong>GitForge</strong>, a GitHub clone, with no style constraints. The
  STE linter reviewed it, Claude applied the feedback, and the linter ran
  again. Changes between the two versions are highlighted below.</p>

  <div class="stats">
    <div class="stat"><div class="label">Baseline findings</div>
      <div class="value">{b_total}</div>
      <div class="sub">{b_err} errors &middot; {b_warn} warnings</div></div>
    <div class="stat good"><div class="label">After one revision</div>
      <div class="value">{a_total}</div>
      <div class="sub">{a_err} errors &middot; {a_warn} warnings</div></div>
    <div class="stat good"><div class="label">Reduction</div>
      <div class="value">&minus;{reduction}%</div>
      <div class="sub">one linter round-trip</div></div>
  </div>

  <h2>Findings by rule</h2>
  <table>
    <thead><tr><th>Rule</th><th class="num">Baseline</th><th class="num">Revised</th></tr></thead>
    <tbody>{rule_rows}</tbody>
  </table>

  <h2>The specs, side by side</h2>
  <p class="legend"><del>removed</del> text was rewritten or deleted;
  <ins>added</ins> text is the STE-compliant replacement. Word-level diff of
  the markdown source.</p>
  <div class="diff">
    <div class="pane"><h3>Baseline &mdash; no STE guidance</h3><pre>{left}</pre></div>
    <div class="pane"><h3>Revised &mdash; after linter feedback</h3><pre>{right}</pre></div>
  </div>

  <h2>Remaining findings in the revision</h2>
  <ul class="findings">{after_list}</ul>

  <h2>All baseline findings</h2>
  <details><summary>Show the full list ({b_total})</summary>
  <ul class="findings">{before_list}</ul>
  </details>
</div>
"""


if __name__ == "__main__":
    main()
