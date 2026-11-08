#!/usr/bin/env python3
"""How many of the study record's open defects are ALREADY FIXED?

WHY THIS EXISTS. The generated morning report shows the founder a list of
outstanding defects, read from `experimental_notes/STUDY_IN_FLIGHT.json`. On
2026-11-08, 6 of those records were examined by RUNNING the code they describe
rather than by reading their own status fields, and most of them turned out to
be repaired already. A list that shows him finished work as outstanding costs
him attention on every report, and in 1 case the record's own prescribed remedy
had become actively harmful.

EVERY VERDICT HERE IS RE-DERIVED, NOT RECORDED. Each probe below runs the real
code or reads the real live state, so this script can CONTRADICT the note that
accompanies it. A table of conclusions would be a claim about evidence rather
than evidence, which is the shape `measured-rate-travels-with-its-script`
forbids.

THE UNIT IS A RECORD, NOT A DEFECT CLASS, and the population is the 6 records
examined on 2026-11-08 -- NOT all 16 in the file. The other 10 were not probed,
so no claim is made about them and the denominator says so. Choosing the
denominator after seeing the results is how a flattering rate gets published,
and this project has recorded that failure 3 times.

Exit 0 iff every probe reached a verdict and both interval routes agree.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y   # noqa: E731
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - float(cen - half)), abs(hi - float(cen + half)),
              abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _runner():
    #: ★ THE RUNNER IMPORTS ITS SIBLINGS BY BARE NAME, so `bench/` must be on
    #: the path before it loads. Without this the import dies on
    #: `hil_review_trigger` and 2 probes return no verdict -- which this script
    #: correctly refused to average over, rather than reporting 3 of 4.
    for _p in (str(REPO), str(REPO / "bench")):
        if _p not in sys.path:
            sys.path.insert(0, _p)
    spec = importlib.util.spec_from_file_location(
        "rr_probe", REPO / "bench" / "reference_runner_v3.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr_probe"] = m
    spec.loader.exec_module(m)
    return m


# ── the 6 probes. Each returns (fixed: bool, evidence: str) ──────────────────

def probe_a4():
    """Run the committed door probe. Exit 0 means every door behaves."""
    p = REPO / "scripts" / "a4_doors_are_shared_2026-11-08.py"
    if not p.is_file():
        return None, f"no probe at {p.name}"
    r = subprocess.run([sys.executable, str(p)], cwd=str(REPO),
                       capture_output=True, text=True, timeout=300)
    return r.returncode == 0, f"probe exit {r.returncode}"


def probe_immune_memory():
    """Ask the LIVE store whether its provenance is complete."""
    spec = importlib.util.spec_from_file_location(
        "dm_mem_probe", REPO / "bench" / "dm" / "_memory.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["dm_mem_probe"] = m
    spec.loader.exec_module(m)
    live = REPO / "bench" / "state" / "immune_memory.json"
    mem = m.ImmuneMemory.load(live)
    raw = json.loads(live.read_text(encoding="utf-8"))
    return bool(mem.provenance_complete), (
        f"counts {raw.get('experiment_count')}, names "
        f"{len(mem.experiment_ids)}, provenance_complete="
        f"{mem.provenance_complete}")


def probe_note_stamp_ratchet():
    """The stamp rule must fire on a FLAT path when told its logical path."""
    lint = REPO / "scripts" / "note_vagueness_lint.py"
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "flat_copy.md"
        f.write_text("# no stamp here\n\n2026-11-08.\n\nProse.\n", encoding="utf-8")
        blind = subprocess.run([sys.executable, str(lint), str(f)], cwd=str(REPO),
                               capture_output=True, text=True, timeout=120)
        told = subprocess.run([sys.executable, str(lint), "--as",
                               "experimental_notes/flat_copy.md", str(f)],
                              cwd=str(REPO), capture_output=True, text=True,
                              timeout=120)
    saw = "MISSING NOTE STANDARD STAMP" in told.stdout
    blindly = "MISSING NOTE STANDARD STAMP" in blind.stdout
    #: FIXED means the rule is REACHABLE through the ratchet's own calling
    #: convention. The flat path still misses it, which is why `--as` exists.
    return (saw and not blindly), (
        f"flat path saw it: {blindly}; with --as: {saw}")


def probe_sim_suffix():
    """A bare vendor token must not survive composition into a finding id."""
    import re
    R = _runner()
    leaks = 0
    cases = [("GEMINI_F001", "Gemini-SIM"), ("GEMINI_F005", "Gemini-SIM"),
             ("CODEX_F003", "Codex-SIM"), ("F002", "Gemini-SIM"),
             ("F001", "Fable-SIM")]
    for local, seat in cases:
        comp = R._compose_finding_id(local, seat)
        vendor = seat.split("-")[0].upper()
        rest = comp.upper().replace(seat.upper(), "", 1)
        if re.search(rf"(?<!-){vendor}(?!-SIM)", rest):
            leaks += 1
    return leaks == 0, f"{leaks} of {len(cases)} identifiers leak a bare vendor token"


def probe_gamma_band_label():
    """An unestimable gamma must not be given a band, nor demand an audit."""
    R = _runner()
    series = [1, 1]                              # too few rounds: the sentinel
    g = R._estimate_gamma(series, 3)
    est = R._gamma_is_estimable(series, 3)
    label = R._interpret_gamma(g, est) if _takes_estimable(R) else R._interpret_gamma(g)
    bad = ("recommend hil audit" in label.lower()
           or "disagrees with state closure" in label.lower())
    return (not bad and g == 0.0 and est is False), (
        f"gamma={g:.3f} estimable={est}; label demands an audit: {bad}")


def _takes_estimable(R) -> bool:
    import inspect
    return "estimable" in inspect.signature(R._interpret_gamma).parameters


def probe_classifier_pre_syntax():
    """A before/after confidence pair must exist somewhere in the product."""
    hits = subprocess.run(
        ["grep", "-rl", "-e", "pre_syntax", "-e", "confidence_before",
         "--include=*.py", str(REPO / "bench")],
        capture_output=True, text=True)
    names = [ln for ln in hits.stdout.splitlines()
             if ln.strip() and "/logs/" not in ln and not ln.endswith(".orig")]
    return bool(names), (f"{len(names)} file(s) log a pre-syntax confidence"
                         if names else "no file logs a pre-syntax confidence")


PROBES = [
    ("A4-counter-valve-severity-mismatch", probe_a4),
    ("immune-memory-names-2-of-its-5-experiments", probe_immune_memory),
    ("the-note-lint-ratchet-is-blind-to-the-standard-stamp", probe_note_stamp_ratchet),
    ("the-sim-suffix-is-not-enforced-on-model-supplied-identifiers", probe_sim_suffix),
    ("gamma-band-label-is-applied-to-an-unestimable-gamma", probe_gamma_band_label),
    ("the-classifier-logs-no-pre-syntax-confidence", probe_classifier_pre_syntax),
]


def main() -> int:
    print("=" * 78)
    print("HOW MANY OF THE PROBED OPEN-DEFECT RECORDS ARE ALREADY SATISFIED?")
    print("=" * 78)
    study = json.loads(
        (REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json").read_text(
            encoding="utf-8"))
    by_id = {x.get("id"): x for x in study.get("open_defects", [])}
    print(f"  records in the study file : {len(study.get('open_defects', []))}")
    print(f"  records probed here       : {len(PROBES)}")
    print("  THE OTHER RECORDS ARE NOT PROBED and no claim is made about them.")
    print()

    fixed, unresolved = [], []
    for key, fn in PROBES:
        try:
            ok, why = fn()
        except Exception as exc:                        # noqa: BLE001
            ok, why = None, f"{type(exc).__name__}: {exc}"
        rec = by_id.get(key, {})
        declared = str(rec.get("status") or rec.get("for_done")
                       or rec.get("not_a_defect")
                       or rec.get("fix_proposed_not_applied") or "(none)")[:46]
        if ok is None:
            unresolved.append((key, why))
            mark = "?? "
        else:
            mark = "FIXED" if ok else "open "
            if ok:
                fixed.append(key)
        print(f"  [{mark:>5}] {key}")
        print(f"            evidence : {why}")
        print(f"            record   : {declared}")
    print()
    if unresolved:
        print("  REFUSED: a probe could not reach a verdict, so the rate below "
              "would have an unknown denominator:")
        for k, w in unresolved:
            print(f"      {k}: {w}")
        return 1

    k, n = len(fixed), len(PROBES)
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print("  THE RATE, unit = a probed RECORD:")
    print(f"      already satisfied: {k} of {n} = {k / n:.6f}")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"

    #: ★ 2 DIFFERENT QUESTIONS, AND THE HEADLINE ANSWERS THE LESS USEFUL ONE.
    #: The rate above is the state TODAY. 1 of those satisfied records -- the
    #: gamma band label -- was genuinely unrepaired at the start of 2026-11-08
    #: and was fixed during that session, with the symptom reproduced at HEAD
    #: first. So the figure for "records that were ALREADY fixed when he was
    #: last shown them as outstanding" is 1 lower. Reporting only the larger
    #: number would answer a question nobody asked, which this project has
    #: recorded as a live failure mode.
    _fixed_tonight = {"gamma-band-label-is-applied-to-an-unestimable-gamma"}
    k_prior = len([f for f in fixed if f not in _fixed_tonight])
    (pwl, pwh), (pcl, pch), pdis = _iv(k_prior, n)
    print("\n  THE SAME POPULATION, EXCLUDING WHAT THIS SESSION ITSELF FIXED:")
    print(f"      already satisfied BEFORE 2026-11-08: {k_prior} of {n} = "
          f"{k_prior / n:.6f}")
    print(f"      Wilson 95% [{pwl:.6f}, {pwh:.6f}]  "
          f"Clopper-Pearson 95% [{pcl:.6f}, {pch:.6f}]")
    print(f"      2-route disagreement {pdis:.3e}")
    assert pdis < 1e-6, f"the 2 interval routes disagree by {pdis}"
    print("      THIS is the figure that bears on his report, because it counts")
    print("      records shown to him as outstanding that were already done.")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: the study file's open-defect records drift out of date,")
    print("    and the generated morning report repeats that drift to him.")
    print("  DOES NOT SUPPORT: a rate over all 16 records. 6 were probed, and")
    print("    they were chosen because they appeared in his report as")
    print("    outstanding -- not at random. The interval is wide and says so.")
    print("  THE SHARPEST CASE IS NOT THE RATE: 1 record's own prescribed")
    print("    remedy would now INVERT the protection it describes, because")
    print("    the store it was written against has since been reset. A stale")
    print("    record costs attention; a stale remedy can cost correctness.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    #: DEFENSIVE, so the producer runs from a scratchpad as well as from
    #: scripts/. A helper that is only importable in 1 location makes the
    #: script unrunnable where it was drafted, which is where it is first
    #: exercised.
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
