#!/usr/bin/env python3
"""Every figure in the 2026-10-01 day-review brief, recomputed from the tree.

WHY THIS EXISTS. `scripts/panel_brief_validate.py` RE-EXECUTES each
`<!-- figure: label | script | value -->` line a brief declares, so a number in
the brief is produced rather than typed. On 2026-09-30 a brief declared a figure
whose producer carried a HARDCODED `73 of 73`, and the cc2 seat caught it; this
file exists so that cannot happen again in this round.

EVERY FIGURE HERE IS RECOMPUTED FROM THE LIVE TREE OR THE ARCHIVE. Nothing is
read back from a log or a note. Where a figure cannot be made stable it is
EXCLUDED and the brief says so in prose instead -- the grep-wrapper divergence
is the example, because it depends on which shell started the process.

Run:  python3 scripts/day_review_brief_figures_2026-10-01.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "bench"), str(REPO / "scripts"),
           str(REPO / "bench/tests/fixtures/stem")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _load(path: str, name: str):
    """Import a measurement script, SURVIVING one that exits at module level.

    FOUND BY RUNNING THIS FILE, 2026-10-01. Several of this project's falsifiers
    do their work at module level and finish with `sys.exit(0)` to report a
    clean verdict -- `e1_population_recount_falsifier_2026-09-22.py` is one. A
    plain `exec_module` therefore TERMINATED THIS PRODUCER mid-way through its
    figure list, and it did so silently from the reader's point of view: the
    output simply stopped after the 3rd figure with a 0 exit status, which looks
    like completion. A brief validator fed that would have seen fewer figures
    than the brief declares rather than an error.

    The module's own module-level counters are already populated by the time it
    exits, so catching the exit yields exactly the state the figure needs.
    """
    spec = importlib.util.spec_from_file_location(name, str(REPO / path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def _wilson(k: int, n: int) -> str:
    from statsmodels.stats.proportion import proportion_confint
    from mpmath import mp, mpf, sqrt
    mp.dps = 50
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mpf("1.9599639845400542")
    p, N = mpf(k) / n, mpf(n)
    den = 1 + z**2 / N
    c = (p + z**2 / (2 * N)) / den
    h = (z / den) * sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    m_lo, m_hi = max(float(c - h), 0.0), float(c + h)
    agree = max(abs(m_lo - lo), abs(m_hi - hi))
    return (f"statsmodels [{lo*100:.4f}%, {hi*100:.4f}%] "
            f"mpmath [{m_lo*100:.4f}%, {m_hi*100:.4f}%] agree {agree:.1e}")


def f_source_text_census() -> tuple[str, str]:
    """The ratchet that caught 2 of CC1's own weak-form tests."""
    m = _load("scripts/source_text_assertions_2026-09-11.py", "sta_fig")
    rows, _ = m.survey()
    mine = [r for r in rows if "2026-10-01" in r[0]]
    return f"{len(rows)} total, {len(mine)} in files dated 2026-10-01", ""


def f_md_fence_dominance() -> tuple[str, str]:
    """The measurement that licensed removing an orphaned extractor."""
    m = _load("scripts/md_fence_orphan_dominance_2026-10-01.py", "mdf_fig")
    from reference_runner_v3 import _MD_PY_FENCE_ANY
    r = m.compare(_MD_PY_FENCE_ANY)
    k, n = len(r["orphan_only"]), r["n"]
    return (f"orphan-only {k} of {n}, live-only {r['live_only']}",
            _wilson(k, n))


def f_claim_ledger_prose_arm() -> tuple[str, str]:
    """The channel on a target where the fix scorer holds no opinion."""
    from bench.claim_ledger import ledger_from_registry
    run = "commissioning_arm4_prose_20260930T064044Z"
    f = REPO / "bench" / "logs" / run / "runner_state.json"
    if not f.is_file():
        return "archive absent", ""
    entries = (json.loads(f.read_text(encoding="utf-8")).get("registry")
               or {}).get("entries") or {}
    rep = ledger_from_registry(entries, target=run).report()
    return (f"{rep['claims_total']} claims, {rep['decidable']} decidable, "
            f"{rep['decided']} decided, {rep['routed']} routed, "
            f"{rep['discarded']} discarded, aggregate {rep['aggregate']}"), ""


def f_e1_scope() -> tuple[str, str]:
    """A dated claim against a grown archive: the day's dominant root cause."""
    m = _load("scripts/e1_population_recount_falsifier_2026-09-22.py", "e1_fig")
    # The module measures at import; read its own scoped counters instead of
    # re-deriving them here, so the brief cannot disagree with the falsifier.
    scoped_n = sum(m.tot.values())
    scoped_k = m.tot.get("FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER", 0)
    all_n = sum(m._all.values())
    all_k = m._all.get("FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER", 0)
    return (f"claim scope {scoped_k} of {scoped_n}; whole archive {all_k} of {all_n}",
            _wilson(scoped_k, scoped_n))


def f_seat_evidence_stranding() -> tuple[str, str]:
    """Seat-written evidence reachable from no clone."""
    m = _load("scripts/seat_evidence_is_gitignored_2026-09-30.py", "se_fig")
    # This figure is git-dependent: `survey()` now REFUSES where git
    # cannot answer rather than returning a false all-unpreserved count.
    # Like the grep-wrapper divergence, the figure is environment-
    # dependent, so it is EXCLUDED where it cannot be computed honestly
    # rather than declaring a number that depends on who ran it.
    gu = getattr(m, "GitUnavailable", None)
    try:
        rows = m.survey()
    except Exception as exc:  # noqa: BLE001
        if gu is not None and isinstance(exc, gu):
            return "git unavailable -- figure excluded (environment-dependent)", ""
        raise
    # LENGTH, NOT TRUTH: `survey()` returns a list, so `not rows` is correct
    # Python -- but `TestVerdictTuplesAreNeverTestedForTruth` flags any name
    # bound whole from a call and then tested for truth, because a
    # (bool, message) tuple is TRUE even on failure and that has cost this
    # project real defects. Being explicit satisfies the guard without
    # loosening it for everyone else.
    if len(rows) == 0:
        return "no harvest in this clone", ""
    unpres = [r for r in rows if not r["tracked"]]
    return f"{len(unpres)} of {len(rows)} unpreserved", _wilson(len(unpres), len(rows))


def f_disagreement_widening() -> tuple[str, str]:
    """4 gained, 0 lost: the widening of the Section P pattern."""
    import re as _re
    m = _load("bench/tests/test_panel_conditions_are_met_2026-09-10.py", "pcm_fig")
    narrow = _re.compile(
        r"strongest[_ ]disagreements?"
        r"|where\s+i\s+disagree"
        r"|(?:^|\n)\s*#{0,4}\s*\**\s*(?:\d+[.)]\s*)?disagreements?\b"
        r"|i\s+disagree\s+with", _re.I)
    rows = [d.get("response", "") for _rnd, d in m._replies()]
    gained = [r for r in rows if m.carries_disagreement(r) and not narrow.search(r)]
    lost = [r for r in rows
            if narrow.search(r) and not m.carries_disagreement(r)]
    return (f"{len(gained)} gained, {len(lost)} lost over {len(rows)} replies"), ""


def f_classifier_status_quo() -> tuple[str, str]:
    """The first measured number for the fence-syntax triage."""
    m = _load("scripts/claim_classifier_labelled_set_2026-10-01.py", "clf_fig")
    rows = m._documents()
    s = m._score(rows, lambda n, t: m._syntax_arm(t, n))
    return (f"accuracy {s['correct']} of {s['n']}, sensitivity {s['tp']} of "
            f"{s['tp'] + s['fn']}"), _wilson(s["tp"], s["tp"] + s["fn"])


def f_catalogue_non_curing() -> tuple[str, str]:
    """Closed findings whose fix was measured as not curing its falsifier."""
    from bench.reference_runner_v3 import export_finding_catalogue
    run = "commissioning_arm1_panel_20260921T215405Z"
    f = REPO / "bench" / "logs" / run / "runner_state.json"
    if not f.is_file():
        return "archive absent", ""
    entries = (json.loads(f.read_text(encoding="utf-8")).get("registry")
               or {}).get("entries") or {}
    recs = export_finding_catalogue(entries)
    both = [r for r in recs if r["fix_cured_its_falsifier"] is False
            and r["status"] in ("CLOSED", "CONFIRMED")]
    return f"{len(both)} of {len(recs)}", _wilson(len(both), len(recs))


def f_tree_snapshot_guards() -> tuple[str, str]:
    """How many test files a mid-run edit can break. CC1 broke 1 of these."""
    tests = sorted((REPO / "bench" / "tests").glob("test_*.py"))
    snap = [p.name for p in tests
            if "status --porcelain" in p.read_text(encoding="utf-8",
                                                   errors="replace")]
    return f"{len(snap)} of {len(tests)}", _wilson(len(snap), len(tests))


FIGURES = {
    "source_text_assertion_census": f_source_text_census,
    "md_fence_orphan_dominance": f_md_fence_dominance,
    "claim_ledger_on_the_prose_arm": f_claim_ledger_prose_arm,
    "e1_population_scoped_vs_archive": f_e1_scope,
    "seat_evidence_unpreserved": f_seat_evidence_stranding,
    "disagreement_pattern_widening": f_disagreement_widening,
    "classifier_status_quo": f_classifier_status_quo,
    "catalogue_closed_with_a_non_curing_fix": f_catalogue_non_curing,
    "tree_snapshot_guards": f_tree_snapshot_guards,
}


def main() -> int:
    print("DAY-REVIEW BRIEF FIGURES, 2026-10-01 — recomputed, not typed")
    print("=" * 74)
    failed = 0
    for label, fn in FIGURES.items():
        try:
            value, interval = fn()
        except Exception as exc:                              # noqa: BLE001
            print(f"  {label}\n      FAILED TO COMPUTE: {exc!r}")
            failed += 1
            continue
        print(f"  {label}\n      {value}")
        if interval:
            print(f"      {interval}")
    if failed:
        print(f"\n  {failed} figure(s) could not be computed. A brief must not "
              f"declare a figure its producer cannot produce.")
    return 1 if failed else 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
