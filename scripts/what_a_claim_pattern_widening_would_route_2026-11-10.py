#!/usr/bin/env python3
"""What widening the claim patterns WOULD route, measured in shadow.

B22 asks whether the harness is a general-purpose STEM calculator yet. Its
third measurement found that 7 of the 29 claims in the project's own STEM
corpus classify `uncategorised` and reach 0 verification tools, and B22
records that NO pattern is proposed, because widening `claim_patterns`
changes which claims the LIVE immune pipeline routes to which tools across
10 domains, and that is the founder's to authorise rather than mine to take
from a measurement.

THIS PRODUCER CHANGES NOTHING. It loads the live configs, applies candidate
patterns to COPIES in memory, and reports what would route differently. The
live files are never written; the guard asserts that.

WHY A SHADOW RATHER THAN A PROPOSAL. A widening has 2 directions and only 1
of them is the obvious one. The gain is claims that currently reach no tool
and would reach one. The RISK is claims that currently route correctly and
would be pulled to a DIFFERENT claim type, and therefore to a different tool
set -- a regression that a gain-only measurement cannot see. Both are
reported, and the recommendation is withheld until both are on the table,
because a decision offered on half a measurement is a decision made for him.

THE 2 STRUCTURAL GAPS ARE DIFFERENT IN KIND AND ARE NOT POOLED.
  `cross_domain` has 0 claim patterns against 3 claim types carrying 11
      distinct tools, so EVERY claim there is uncategorised and not 1 of its
      tools can ever be dispatched. That is a MISSING configuration.
  `biology` has 3 patterns and none contains any of sequence, dna, rna,
      protein, nucleotide, complement, codon or gc content, so a sequence
      claim matches nothing. That is an INCOMPLETE vocabulary.
A single number averaging the 2 would describe neither.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
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

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

#: The corpus labels documents with DESCRIPTIVE domain strings, so a mapping
#: is unavoidable. Taken verbatim from the sibling producer so the 2 cannot
#: disagree about which fixture is which domain.
CORPUS_DOMAIN = {
    "structural / mechanical engineering": "engineering",
    "statistics": "statistics",
    "chemistry / metrology": "chemistry",
    "algorithms / complexity": "cs_software",
    "numerical analysis": "mathematics",
}

#: ★ THE INPUT IS `claim.summary`, AND GETTING THIS WRONG CHANGES THE ANSWER
#: FROM 7 TO 0. A `Claim` carries tag, verdict, summary, anchor and note. A
#: fallback chain of `getattr(c, "text", None) or getattr(c, "claim", None)
#: or str(c)` silently yields the whole dataclass repr -- note and anchor
#: included -- and the note is full of operators, so every claim classifies
#: and the defect disappears. Measured both ways on 2026-11-10: the summary
#: routes 22 of 29, the repr routes 29 of 29. The summary is what a finding's
#: `description` corresponds to, so it is the only honest input.
def claim_text(c) -> str:
    return getattr(c, "summary", "") or ""


#: Candidate patterns, as CANDIDATES. Each is the vocabulary the domain's own
#: subject matter uses and its existing patterns lack. Nothing here is
#: adopted; the point is to measure what adopting it would do.
CANDIDATES = {
    "cs_software": {
        "mathematical": r"(?:\bgraph\b|\bpath\b|\bedge[s]?\b|\bnode[s]?\b"
                        r"|\bvertex\b|\bvertices\b|\btopological\b|\bacyclic\b"
                        r"|\btransitive\b|\bordering\b|\bcomplexity\b)",
    },
    "biology": {
        "mathematical": r"(?:\bsequence\b|\bDNA\b|\bRNA\b|\bprotein\b"
                        r"|\bnucleotide[s]?\b|\bcomplement\b|\bcodon[s]?\b"
                        r"|\bGC\s+content\b)",
    },
    "cross_domain": {
        "mathematical": r"(?:[=<>!]=?|[+\-*/^]|\bsqrt\b|\blog\b|\bexp\b)",
        "statistical": r"(?:\bsignificant\b|\bp-value\b|\bconfidence\s*interval\b"
                       r"|\bsample\s*size\b)",
        "logical": r"(?:\bif\b.*\bthen\b|\bimplies\b|\bcontradiction\b)",
    },
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
    w2 = (max(0.0, c - h), min(1.0, c + h))
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
    gap = max(abs(wl - w2[0]), abs(wh - w2[1]),
              *[abs(a - b) for a, b in zip((cl, ch), c2)
                if not (np.isnan(a) or np.isnan(b))])
    return (wl, wh), (cl, ch), gap


def _shadow(cfg, extra: dict):
    """A COPY of cfg with the candidate patterns merged in. cfg is untouched."""
    c = copy.deepcopy(cfg)
    #: ★ A claim_patterns VALUE IS A LIST OF PATTERN STRINGS, not a string.
    #: The first version concatenated with `|` and raised TypeError on the
    #: first domain it touched -- caught by running it, which is the only way
    #: a shape assumption gets caught.
    pats = {k: list(v) for k, v in (getattr(c, "claim_patterns", None) or {}).items()}
    for ct, rx in extra.items():
        pats.setdefault(ct, []).append(rx)
    c.claim_patterns = pats
    for attr in ("_compiled_claim_patterns", "_compiled"):
        if hasattr(c, attr):
            try:
                setattr(c, attr, None)
            except Exception:                                  # noqa: BLE001
                pass
    return c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)

    import importlib.util
    import domain_immune as di

    spec = importlib.util.spec_from_file_location(
        "_stem_fx", REPO / "bench" / "tests" / "fixtures" / "stem" / "stem_fixtures.py")
    fx_mod = importlib.util.module_from_spec(spec)
    sys.modules["_stem_fx"] = fx_mod
    spec.loader.exec_module(fx_mod)

    class View:
        def __init__(self, d):
            self.description = d

    cfgs = di.load_all_domain_configs()
    #: THE LIVE FILES MUST BE BYTE-IDENTICAL AFTERWARDS. Digested before and
    #: after, because "it only edits a copy" is a claim about code and this
    #: is a measurement of it.
    dom_dir = getattr(di, "_DOMAINS_DIR", None)
    before = {}
    if dom_dir and pathlib.Path(dom_dir).is_dir():
        for f in sorted(pathlib.Path(dom_dir).rglob("*")):
            if f.is_file():
                before[f] = hashlib.sha256(f.read_bytes()).hexdigest()

    print("=" * 78)
    print("WHAT A CLAIM-PATTERN WIDENING WOULD ROUTE — MEASURED IN SHADOW")
    print("=" * 78)

    print("\n1. THE 2 STRUCTURAL GAPS, NOT POOLED")
    for dom in ("cross_domain", "biology"):
        c = cfgs[dom]
        pats = c.compiled_claim_patterns() or {}
        vts = c.verification_tools or {}
        tools = {t for tl in vts.values() for t in (tl or [])}
        print(f"      {dom:14s} {len(pats)} pattern(s), {len(vts)} claim type(s) "
              f"carrying {len(tools)} distinct tool(s)")
        if not pats:
            print(f"      {'':14s} -> MISSING configuration: every claim is "
                  f"uncategorised, so 0 of those {len(tools)} can ever run")
        else:
            vocab = ("sequence", "dna", "rna", "protein", "nucleotide",
                     "complement", "codon", "gc content")
            joined = " ".join(
                getattr(r, "pattern", str(r)) for rx in pats.values()
                for r in (rx if isinstance(rx, (list, tuple)) else [rx])).lower()
            hit = [w for w in vocab if w in joined]
            print(f"      {'':14s} -> INCOMPLETE vocabulary: subject words "
                  f"present in any pattern: {hit or 'NONE'}")

    print("\n2. THE CORPUS, ROUTED LIVE AND IN SHADOW")
    rows = []
    for fx in fx_mod.FIXTURES:
        dom = CORPUS_DOMAIN[fx.domain]
        live_cfg = cfgs[dom]
        sh_cfg = _shadow(live_cfg, CANDIDATES.get(dom, {}))
        for c in fx.claims:
            txt = claim_text(c)
            lt, _ = di.domain_classify_claim(View(txt), live_cfg)
            st, _ = di.domain_classify_claim(View(txt), sh_cfg)
            ltools = di.domain_b_cell_tools(lt, live_cfg) or []
            stools = di.domain_b_cell_tools(st, sh_cfg) or []
            rows.append((c.tag, dom, lt, st, len(ltools), len(stools), txt))

    live_routed = sum(1 for r in rows if r[4])
    sh_routed = sum(1 for r in rows if r[5])
    gained = [r for r in rows if not r[4] and r[5]]
    #: ★ THE RISK SIDE. A claim that routed correctly and now routes to a
    #: DIFFERENT claim type has moved to a different tool set.
    moved = [r for r in rows if r[4] and r[2] != r[3]]
    lost = [r for r in rows if r[4] and not r[5]]
    n = len(rows)
    print(f"      claims                      : {n}")
    print(f"      reach a tool LIVE           : {live_routed}")
    print(f"      reach a tool IN SHADOW      : {sh_routed}")
    print(f"      GAINED (0 tools -> some)    : {len(gained)}")
    print(f"      MOVED  (routed, type changed): {len(moved)}   <- the risk side")
    print(f"      LOST   (some tools -> 0)    : {len(lost)}")
    for tag, dom, lt, st, lo_, sh_, txt in gained:
        print(f"        + {tag:7s} {dom:12s} {lt} -> {st}  ({sh_} tool(s))  {txt[:44]!r}")
    for tag, dom, lt, st, lo_, sh_, txt in moved:
        print(f"        ! {tag:7s} {dom:12s} {lt} -> {st}  {txt[:44]!r}")

    k = len(gained)
    (wl, wh), (cl, ch), gap = _iv(k, n)
    print(f"\n      claims the widening would GAIN: {k} of {n} = {k/n:.6f}")
    print(f"        Wilson 95% [{wl:.6f}, {wh:.6f}]   2-route gap {gap:.3e}")
    print(f"        Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")

    print("\n3. THE LIVE CONFIGURATION IS UNTOUCHED")
    drift = []
    for f, h in before.items():
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != h:
            drift.append(str(f))
    print(f"      domain config files digested before and after : {len(before)}")
    print(f"      files whose bytes changed                     : {len(drift)}")
    if drift:
        print(f"      CHANGED: {drift}")

    print("\n" + "=" * 78)
    print("VERDICT")
    print(f"\n  The widening is NOT recommended here and no pattern is adopted.")
    print(f"  What this produces is the evidence the decision needs, on BOTH")
    print(f"  sides: {len(gained)} claim(s) would reach a tool that reach none")
    print(f"  today, and {len(moved)} claim(s) that route correctly would move to a")
    print(f"  different claim type and therefore a different tool set.")
    print(f"  A gain-only measurement cannot see the second number, which is")
    print(f"  why it is reported beside the first rather than after a decision.")
    print(f"  The 2 structural gaps differ in KIND -- a missing configuration")
    print(f"  against an incomplete vocabulary -- so they are ruled separately")
    print(f"  or not at all, and a single pooled figure would describe neither.")
    print(f"\n  mpmath cross-check of the gain ratio: "
          f"{mp.mpf(k)/mp.mpf(n) if n else mp.mpf('nan')}")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
