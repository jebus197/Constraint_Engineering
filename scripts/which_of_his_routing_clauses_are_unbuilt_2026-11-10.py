#!/usr/bin/env python3
"""The 2 routing clauses he gave on 2026-11-10, with his own words, and
whether anything in the tree implements them.

WHY THIS EXISTS. Entry B56 records that 2 clauses in his 2026-11-10 message
are *"a ruling he is giving NOW, not one being recalled"*, that both are
UNBUILT, and that closing B56 on a recollection would record them as
delivered. It reports a measurement for that -- each clause appearing exactly
1 time across 6 session transcripts and 477,476 lines -- and cites NO
PRODUCER for it. A figure that exists only as prose in an entry is a claim
about evidence rather than evidence, which is the rule that entry is itself
subject to. This is the missing producer.

IT ALSO RECOVERS HIS EXACT WORDS, which is the operative half. The clauses
are described in B56's prose and nowhere quoted, and
`never-paraphrase-inside-quotation-marks` forbids quoting him from a
description. Raising them as trackable work without his wording would hand a
future reader a paraphrase to build from.

WHAT IT DOES NOT DO: decide anything. Whether to build either clause is his,
and B56 already records why -- wiring a relegation rule changes which seats
the harness dispatches, on a model calibrated against simulated degradation,
against his standing rule never to bench a model.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import mpmath as mp
import numpy as np
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

for _c in (pathlib.Path(__file__).resolve().parent, pathlib.Path.cwd().resolve()):
    for _x in (_c, *_c.parents):
        if (_x / "bench" / "domain_immune.py").is_file():
            REPO = _x
            break
    else:
        continue
    break
else:
    raise SystemExit("cannot locate the repository")

TRANSCRIPTS = pathlib.Path.home() / ".claude" / "projects" / \
    "-Users-georgejackson-Developer-Projects"

#: The 2 clauses, as SEARCH TERMS rather than as quotations. The quotation is
#: what this producer goes to find; writing one here would be the paraphrase
#: the docstring says must not happen.
CLAUSES = {
    "diagonal movement on the board":
        re.compile(r"\bdiagonal", re.I),
    "weaker models dividing one problem and cooperating before escalating":
        re.compile(r"\bblackboard\b", re.I),
}

#: Where an implementation would have to live for the clause to be built.
#: Each is a question about the LIVE tree, answered by execution below.
IMPL_PROBES = {
    "diagonal movement on the board":
        ("a routing step that moves a finding sideways AND down in 1 move",
         re.compile(r"diagonal", re.I)),
    "weaker models dividing one problem and cooperating before escalating":
        ("a mechanism that splits 1 problem across >1 model and merges their "
         "partial answers before escalating",
         re.compile(r"\b(?:split|divide|partition)\w*\s+(?:the\s+)?"
                    r"(?:problem|task|finding)\b", re.I)),
}


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, 0.05, "wilson")
    z, p = 1.959963984540054, k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _mp(a, b, y):
        mp.mp.dps = 40
        lo, hi = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            if hi - lo < mp.mpf("1e-18"):
                break
            mid = (lo + hi) / 2
            try:
                v = mp.betainc(a, b, 0, mid, regularized=True) - y
            except Exception:                                  # noqa: BLE001
                return float("nan")
            lo, hi = (mid, hi) if v < 0 else (lo, mid)
        return float((lo + hi) / 2)

    c2 = (0.0 if k == 0 else _mp(k, n - k + 1, 0.025),
          1.0 if k == n else _mp(k + 1, n - k, 0.975))
    gap = max(abs(wl - max(0.0, c - h)), abs(wh - min(1.0, c + h)),
              *[abs(a - b) for a, b in zip((cl, ch), c2)
                if not (np.isnan(a) or np.isnan(b))])
    return (wl, wh), (cl, ch), gap


def his_messages():
    """Every user-role message in the session transcripts, with its date.

    ONLY user-role entries. A clause of his quoted back inside my own reply
    would otherwise be counted as his, which is how a figure about what he
    said becomes a figure about what I repeated.
    """
    out = []
    if not TRANSCRIPTS.is_dir():
        return out, 0
    lines = 0
    for f in sorted(TRANSCRIPTS.glob("*.jsonl")):
        try:
            for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
                lines += 1
                if not raw.strip():
                    continue
                try:
                    rec = json.loads(raw)
                except Exception:                              # noqa: BLE001
                    continue
                msg = rec.get("message") or {}
                if (rec.get("type") != "user") or rec.get("isCompactSummary"):
                    continue
                content = msg.get("content")
                if isinstance(content, list):
                    text = " ".join(
                        c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text")
                elif isinstance(content, str):
                    text = content
                else:
                    continue
                if not text.strip():
                    continue
                out.append((str(rec.get("timestamp") or "")[:10], text, f.name))
        except Exception:                                      # noqa: BLE001
            continue
    return out, lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--chars", type=int, default=420,
                    help="how much surrounding text to print per hit")
    a = ap.parse_args(argv)

    print("=" * 78)
    print("HIS 2 ROUTING CLAUSES OF 2026-11-10: HIS WORDS, AND WHAT IMPLEMENTS THEM")
    print("=" * 78)

    msgs, nlines = his_messages()
    print(f"\n1. THE CORPUS")
    print(f"      transcript files        : "
          f"{len(sorted(TRANSCRIPTS.glob('*.jsonl'))) if TRANSCRIPTS.is_dir() else 0}")
    print(f"      lines scanned           : {nlines}")
    print(f"      user-role messages      : {len(msgs)}")
    if not msgs:
        print("\n      REFUSED: no transcript messages readable, so nothing here")
        print("      is measured. The figure B56 reports stays unproduced.")
        return 2

    print(f"\n2. HIS OWN WORDS, FOUND RATHER THAN QUOTED FROM A DESCRIPTION")
    found = {}
    for label, rx in CLAUSES.items():
        hits = [(d, t, f) for d, t, f in msgs if rx.search(t)]
        #: ★ THE RAW COUNT AND THE ROUTING-SENSE COUNT ARE DIFFERENT NUMBERS,
        #: AND B56 WAS RIGHT TO RESTRICT. Raw, each term appears in 3 of his
        #: messages: `diagonal` also in an Enigma-cillies citation of
        #: 2026-08-16 and an off-diagonal confusion-matrix reading of
        #: 2026-10-04, and `blackboard` also in 2 uses of 2026-10-02 that
        #: describe PANEL ROUND STRUCTURE rather than routing. B56 reports
        #: each appearing exactly 1 time in the routing sense, both on
        #: 2026-11-10, and that is what reproduces here. Reporting the raw
        #: count alone would contradict a correct entry.
        routing = [h for h in hits if h[0] == "2026-11-10"]
        found[label] = routing
        print(f"\n   {label}")
        print(f"      user messages containing the term      : {len(hits)}")
        print(f"      of those dated 2026-11-10, the ruling  : {len(routing)}")
        for d, t, f in hits:
            m = rx.search(t)
            s = max(0, m.start() - a.chars // 2)
            print(f"        [{d}] ...{t[s:m.end() + a.chars // 2].strip()}...")

    print(f"\n3. DOES ANYTHING IN THE LIVE TREE IMPLEMENT EITHER?")
    built = 0
    for label, (what, rx) in IMPL_PROBES.items():
        files = []
        me = pathlib.Path(__file__).resolve()
        for p in list((REPO / "bench").rglob("*.py")) + list((REPO / "scripts").rglob("*.py")):
            if "sandbox_harvest" in str(p) or "/logs/" in str(p):
                continue
            #: ★ EXCLUDE THIS FILE. Its first run reported 1 live candidate
            #: for diagonal movement and the candidate was ITSELF -- the
            #: detector matching the pattern it spells out, which is the
            #: shape this project records against a scar read as a wound.
            if p.resolve() == me:
                continue
            try:
                if rx.search(p.read_text(encoding="utf-8", errors="replace")):
                    files.append(str(p.relative_to(REPO)))
            except Exception:                                  # noqa: BLE001
                continue
        built += bool(files)
        print(f"\n   {label}")
        print(f"      what would have to exist : {what}")
        print(f"      live files matching      : {len(files)}")
        if len(files) > 6:
            print(f"      ... {len(files) - 6} further match(es) withheld "
                  f"below, of {len(files)}")
        for f in files[:6]:
            note = ""
            if "audit_closing_window" in f:
                note = ("   <- CHECKED AND REFUSED: the match is the phrase "
                        "`the splitter problem` in a comment about telling a "
                        "correctly-counted re-find from a missed new defect. "
                        "Coincidental wording, not a mechanism.")
            if "run_exp17_immune" in f:
                note = ("   <- ALREADY REFUTED BY EXECUTION in B56: its "
                        "sub-area split allocates by `round_idx % "
                        "len(subareas)`, so 5 model labels in round 3 all "
                        "received the SAME slice -- 1 distinct slice across "
                        "5 labels, which is not dividing a problem")
            print(f"        {f}{note}")

    k, n = built, len(IMPL_PROBES)
    (wl, wh), (cl, ch), gap = _iv(k, n)
    print(f"\n      clauses with ANY live candidate: {k} of {n} = {k/n:.6f}")
    print(f"        Wilson 95% [{wl:.6f}, {wh:.6f}]   2-route gap {gap:.3e}")
    print(f"        Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      A MATCH IS A CANDIDATE AND NOT AN IMPLEMENTATION. A name in")
    print(f"      a file is not a mechanism, which is the substring-is-not-a-")
    print(f"      call failure this project already records. Each candidate")
    print(f"      must be EXECUTED before it counts as built.")

    print("\n" + "=" * 78)
    print("VERDICT")
    both = all(found[l] for l in CLAUSES)
    print(f"\n  his words located for both clauses : {both}")
    print(f"  clauses with a live candidate       : {k} of {n}")
    print(f"\n  THIS PRODUCER DECIDES NOTHING. Whether to build either clause")
    print(f"  is his: B56 records that wiring a relegation rule changes which")
    print(f"  seats the harness dispatches, on a model calibrated against")
    print(f"  SIMULATED degradation, against his standing rule never to bench")
    print(f"  a model. What it supplies is his wording, so the work can be")
    print(f"  tracked without a paraphrase standing in for what he said.")
    return 0 if both else 1


if __name__ == "__main__":
    raise SystemExit(main())
