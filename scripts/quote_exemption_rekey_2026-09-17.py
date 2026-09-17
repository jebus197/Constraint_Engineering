#!/usr/bin/env python3
"""Is the L2 effect script's "ADDED" a regression or a paragraph renumbering?

PANEL ROUND 16, 2026-09-17. `scripts/quote_exemption_effect_2026-09-09.py` keys
findings on (paragraph number, kind, token). Until 2026-09-17 its "before" side
split paragraphs on a literal blank line, while `note_vagueness_lint.sentences()`
has split with `paragraphs()`, which tolerates whitespace on a blank line, since
6c6d053. The 2 sides then numbered paragraphs differently, and a finding that
did not change read as 1 removed plus 1 added. At 989f32f the effect script
printed 19 ADDED and exited 1 for that reason alone.

This re-runs the comparison over experimental_notes/ under 5 keys. A key free of
the numbering drift that still shows an addition would be a real regression.
The first key keeps the literal split as a local copy, so the confound stays
measurable after the effect script was repaired to share the linter's splitter.

Read-only: it reads notes and prints. A set key collapses repeated findings in a
file, so its denominator is smaller; compare removed and ADDED within 1 key,
never across keys.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load_effect(repo: Path):
    spec = importlib.util.spec_from_file_location(
        "quote_effect_for_rekey",
        repo / "scripts" / "quote_exemption_effect_2026-09-09.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def literal_split_sentences(text: str):
    """The effect script's before-side generator AS COMMITTED UNTIL 2026-09-17:
    no mask, paragraphs split on a literal blank line."""
    for para_no, para in enumerate(text.split("\n\n"), 1):
        flat = " ".join(para.split())
        if not flat or flat.startswith(("|", "#", "```")):
            continue
        for s in re.split(r"(?<=[.!?])\s+", flat):
            if len(s.split()) >= 5:
                yield para_no, s


def measure(repo: Path = REPO) -> tuple[int, list[dict]]:
    """Return (notes scanned, 1 row per key)."""
    eff = _load_effect(repo)
    lint = eff.lint_mod

    def findings(path, gen):
        saved = lint.sentences
        lint.sentences = gen
        try:
            return list(lint.lint(path))
        finally:
            lint.sentences = saved

    keys = (
        ("(para, kind, token) set, literal split [committed until 2026-09-17]",
         literal_split_sentences, lambda f: (f[0], f[1], f[2]), False),
        ("(para, kind, token) set, old side on paragraphs() [committed since]",
         eff.old_sentences, lambda f: (f[0], f[1], f[2]), False),
        ("(kind, token) multiset, literal split",
         literal_split_sentences, lambda f: (f[1], f[2]), True),
        ("(kind, token) set, literal split",
         literal_split_sentences, lambda f: (f[1], f[2]), False),
        ("(kind, token, sentence) set, literal split",
         literal_split_sentences, lambda f: (f[1], f[2], f[3]), False),
    )
    notes = sorted((repo / "experimental_notes").rglob("*.md"))
    rows = []
    for label, old_gen, key, multiset in keys:
        before = removed = added = 0
        added_in: collections.Counter = collections.Counter()
        for p in notes:
            try:
                b, a = findings(p, old_gen), findings(p, lint.sentences)
            except Exception:
                continue
            if multiset:
                bc = collections.Counter(map(key, b))
                ac = collections.Counter(map(key, a))
                before += sum(bc.values())
                gone, new = sum((bc - ac).values()), sum((ac - bc).values())
            else:
                bs, as_ = set(map(key, b)), set(map(key, a))
                before += len(bs)
                gone, new = len(bs - as_), len(as_ - bs)
            removed += gone
            added += new
            if new:
                added_in[p.name] += new
        rows.append({"label": label, "before": before, "removed": removed,
                     "added": added, "added_in": dict(added_in)})
    return len(notes), rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args()
    from statsmodels.stats.proportion import proportion_confint
    n_notes, rows = measure()
    print(f"notes scanned: {n_notes}")
    for r in rows:
        lo, hi = (proportion_confint(r["removed"], r["before"], method="wilson")
                  if r["before"] else (0.0, 0.0))
        share = r["removed"] / r["before"] if r["before"] else 0.0
        print(f"  {r['label']:70s} before {r['before']}, removed {r['removed']}, "
              f"ADDED {r['added']} = {share:.4%} removed, "
              f"Wilson [{lo:.4%}, {hi:.4%}]  added in: {r['added_in']}")
    print("A set key collapses repeated findings in a file, so its denominator is "
          "smaller;\ncompare removed and ADDED within 1 key, never across keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
