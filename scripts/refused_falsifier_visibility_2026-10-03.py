#!/usr/bin/env python3
"""Measure what the false-positive sweep could NOT see, and what it sees now.

WHY THIS EXISTS. The sweep that holds the key-access gate's false-positive rate
-- `bench/tests/test_falsifier_cannot_read_the_key.py`,
`test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive` -- builds its
corpus from `registry.entries.<cid>.falsifier_code`. The runner writes that
field back only when a falsifier RESOLVED. A falsifier the gate REFUSED
therefore never reaches the field the sweep reads, so the corpus that measures
refusals excluded refusals by construction. The gate's rule was changed on
2026-10-02 (access-only) while that blind spot was open.

WHAT IT MEASURES, all of it recomputed on every run so no figure here can go
stale as prose:

  1. `entries`           -- unique falsifier sources reachable the old way.
  2. `routing_only`      -- unique sources reachable ONLY through
                            `routing_history[].last_falsifier_code*`, i.e. the
                            population the sweep was blind to.
  3. `truncated`         -- how many of those exist only as the 600-character
                            cut, and so can still hide a violation past the cut.
  4. For every source in 1 and 2: the gate's verdict, split into real
                            rejections and location artefacts by the sweep's own
                            classifier, so the widened figure is comparable with
                            the narrow one rather than merely larger.

TRUNCATION CANNOT MANUFACTURE A REJECTION. `scan_falsifier_source` is purely
regex over the text with no parse step, so a cut body can only LOSE a match,
never gain one. A rejection found in a truncated body is therefore real; a clean
verdict on one is provisional. That asymmetry is reported, not hidden.

Usage:  python3 scripts/refused_falsifier_visibility_2026-10-03.py [--json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

sys.path.insert(0, str(REPO / "bench" / "tests"))

from bench.falsifier_verify import scan_falsifier_source  # noqa: E402


def _help_wanted(argv: list[str]) -> bool:
    return any(a in ("-h", "--help") for a in argv)


def interval(k: int, n: int) -> dict:
    """Wilson by 2 independent tools plus Clopper-Pearson by a third."""
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    lo_mp, hi_mp = float(c - h), float(c + h)
    assert abs(lo_mp - lo_sm) < 1e-9 and abs(hi_mp - hi_sm) < 1e-9, (
        f"statsmodels and mpmath disagree on the Wilson bounds: "
        f"({lo_sm}, {hi_sm}) vs ({lo_mp}, {hi_mp})"
    )
    cp_lo = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
    cp_hi = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo_sm, 4), round(100 * hi_sm, 4)],
            "clopper_pearson": [round(100 * cp_lo, 4), round(100 * cp_hi, 4)]}


def harvest() -> dict:
    logs = REPO / "bench" / "logs"
    entries: dict[str, tuple[str, str]] = {}
    routing: dict[str, tuple[str, str]] = {}
    truncated: set[str] = set()
    bodies_seen = full_available = 0
    for report in sorted(logs.rglob("*_report.json")):
        try:
            data = json.loads(report.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        where = report.parent.name
        reg = (data.get("registry") or {}).get("entries") or {}
        for cid, entry in reg.items():
            code = (entry or {}).get("falsifier_code") or ""
            if code.strip():
                entries.setdefault(code, (where, cid))
        # THE PREDICATE, CHECKED RATHER THAN ASSUMED. `routing_history` is
        # attached PER REGISTRY ENTRY by `_apply_routing`
        # (`e.setdefault("routing_history", [])`), not at the top level of the
        # report. A first version of this script read `data["routing_history"]`
        # and found 0 bodies in 872 sources -- a clean-looking result that was
        # purely an artefact of reading the wrong key.
        for cid, entry in reg.items():
            for rec in ((entry or {}).get("routing_history") or []):
                if not isinstance(rec, dict):
                    continue
                # RAW, STRIPPED ONLY TO TEST EMPTINESS -- see the same note in
                # `harvest_falsifier_sources`. Stripping makes one falsifier
                # two corpus members and inflates the denominator.
                full = rec.get("last_falsifier_code_full") or ""
                cut = rec.get("last_falsifier_code") or ""
                body = full if full.strip() else cut
                if not body.strip():
                    continue
                bodies_seen += 1
                if full.strip():
                    full_available += 1
                if body not in entries:
                    routing.setdefault(body, (where, cid))
                    if not full.strip() and len(cut) >= 600:
                        truncated.add(body)
    return {"entries": entries, "routing": routing, "truncated": truncated,
            "bodies_seen": bodies_seen, "full_available": full_available}


def verdicts(sources: dict[str, tuple[str, str]]) -> tuple[set, set]:
    from test_falsifier_cannot_read_the_key import _artefact_classifier
    is_artefact = _artefact_classifier()
    rejected, artefacts = set(), set()
    for code, where in sources.items():
        v = scan_falsifier_source(code)
        if not v:
            continue
        (artefacts if is_artefact(v) else rejected).add(where)
    return rejected, artefacts


def main(argv: list[str] | None = None) -> int:
    # A REAL PARSER, NOT A HAND-ROLLED argv SCAN. The first version read
    # `sys.argv` directly, so an unrecognised flag was SILENTLY IGNORED and the
    # script exited 0 -- the shape `bench/tests/test_operational_scripts.py`
    # calls "the 118-day no-op again", and the reason the project's rule is
    # that a documented command must either work or fail loudly.
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0],
        epilog="Every figure is recomputed from the archive on each run.")
    ap.add_argument("--json", action="store_true",
                    help="emit the full record as JSON instead of a report")
    a = ap.parse_args(argv)
    argv = ["--json"] if a.json else []
    h = harvest()
    ent, rout, trunc = h["entries"], h["routing"], h["truncated"]
    rej_e, art_e = verdicts(ent)
    rej_r, art_r = verdicts(rout)
    both = dict(ent)
    both.update(rout)
    out = {
        "entries_corpus": len(ent),
        "routing_only_corpus": len(rout),
        "widened_corpus": len(both),
        "routing_bodies_seen": h["bodies_seen"],
        "routing_bodies_with_full_text": h["full_available"],
        "routing_only_truncated_at_600": len(trunc),
        "blind_share_of_widened": interval(len(rout), len(both)),
        "rejections_entries_only": sorted(rej_e),
        "rejections_routing_only": sorted(rej_r),
        "artefacts_entries_only": len(art_e),
        "artefacts_routing_only": len(art_r),
        "real_rejection_rate_narrow": interval(len(rej_e), len(ent)),
        "real_rejection_rate_widened": interval(len(rej_e | rej_r), len(both)),
    }
    if "--json" in argv:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    print("REFUSED-FALSIFIER VISIBILITY")
    print(f"  corpus the sweep read before : {out['entries_corpus']}")
    print(f"  reachable only via routing   : {out['routing_only_corpus']}")
    print(f"  widened corpus               : {out['widened_corpus']}")
    b = out["blind_share_of_widened"]
    print(f"  blind share                  : {b['k']} of {b['n']} = "
          f"{b['pct']}%, Wilson [{b['wilson'][0]}%, {b['wilson'][1]}%]")
    print(f"  routing bodies seen          : {out['routing_bodies_seen']} "
          f"({out['routing_bodies_with_full_text']} carry the full text)")
    print(f"  of the blind set, 600-cut    : {out['routing_only_truncated_at_600']} "
          "(a clean verdict on these is provisional)")
    n = out["real_rejection_rate_narrow"]
    w = out["real_rejection_rate_widened"]
    print(f"  real rejections, narrow      : {n['k']} of {n['n']} = {n['pct']}%, "
          f"Wilson [{n['wilson'][0]}%, {n['wilson'][1]}%]")
    print(f"  real rejections, widened     : {w['k']} of {w['n']} = {w['pct']}%, "
          f"Wilson [{w['wilson'][0]}%, {w['wilson'][1]}%]")
    print(f"  new real rejections          : {out['rejections_routing_only'] or 'none'}")
    print(f"  location artefacts           : {out['artefacts_entries_only']} narrow, "
          f"{out['artefacts_routing_only']} newly visible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
