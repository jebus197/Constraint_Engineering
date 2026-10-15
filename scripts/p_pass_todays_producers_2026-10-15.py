#!/usr/bin/env python3
"""P-pass on the 4 producers written 2026-10-15. Try to BREAK them.

WHY. Every finding recorded today rests on an instrument written today, and the
whole record of this arc is that THE INSTRUMENT IS THE DEFECT: 6 figures were
withdrawn this week and 1 hypothesis was withdrawn this morning, each because a
measuring predicate was wrong rather than because the project was. Attacking
the project's code all morning and not my own is the same asymmetry.

A producer passes here only if it DISCRIMINATES -- if a deliberately wrong input
makes it say something different. A predicate that returns the same answer on a
true and a false world measured nothing.

Each case is failable: the script exits non-zero if any discrimination fails.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))
FAILURES: list[str] = []


def load(name: str):
    p = REPO / "scripts" / name
    spec = importlib.util.spec_from_file_location(p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(label: str, got, want, why: str = "") -> None:
    ok = got == want
    print(f"    {'PASS' if ok else 'FAIL'}  {label}: got {got!r}, want {want!r}"
          + (f"  ({why})" if why and not ok else ""))
    if not ok:
        FAILURES.append(f"{label}: got {got!r} want {want!r}")


def main() -> int:
    """Run every discrimination case. Returns 1 if any failed."""
    FAILURES.clear()
    print("=" * 78)
    print("1. B9's path classifier — does it actually separate the 2 eras?")
    print("=" * 78)
    g = load("the_guard_refuses_the_runs_own_target_2026-10-15.py")
    cases = [
        ("open /tmp/x/bench/logs/run_a/working/t.md", "THE RUN'S OWN WORKING TARGET",
         "the positive case the whole B9 finding rests on"),
        ("open /Users/g/Developer_Projects/CE/bench/logs/run_a/working/t.md",
         "THE RUN'S OWN WORKING TARGET", "same shape at the real repo path"),
        ("open /tmp/x/bench/logs/run_a/r0_cc2.json", "project evidence (not the target)",
         "evidence that is NOT the target must not be counted as one"),
        ("os.listdir /Library/.../lib/python3.9/site-packages", "python interpreter / site-packages",
         "the pre-era noise must classify as noise"),
        ("open /Library/.../python3.9/<string>", "python import probe", "import probe"),
        ("open /Users/g/Documents/secret.txt", "home-rooted", "a home path is neither"),
    ]
    for path, want, why in cases:
        check(f"classify({path[-46:]})", g.classify(path), want, why)

    # THE ADVERSARIAL ONE: a site-packages path that ALSO sits under bench/logs.
    # If the classifier checked site-packages first it would miscount the B9 figure.
    adv = "open /tmp/x/bench/logs/run_a/working/site-packages/t.md"
    got = g.classify(adv)
    print(f"    note  a site-packages path UNDER bench/logs/working classifies as "
          f"{got!r}")
    if got != "THE RUN'S OWN WORKING TARGET":
        FAILURES.append("classify() lets a site-packages segment mask a working target")

    print()
    print("=" * 78)
    print("2. B9's figure — is 18 of 18 robust to a line the regex cannot parse?")
    print("=" * 78)
    real = g.scan(REPO / ("bench/logs/free_run1_directive_whole_20261015T061123Z"
                          "_20261015T061124Z"))
    check("run 1 refusals", real["refusals"], 18)
    check("run 1 all the working target", real["by_kind"].get("THE RUN'S OWN WORKING TARGET"), 18)
    before = g.scan(REPO / "bench/logs/study_run1b_2026-10-03_20261003T100439Z")
    check("study_run1b refusals", before["refusals"], 81)
    check("study_run1b working-target count", before["by_kind"].get("THE RUN'S OWN WORKING TARGET"), None,
          "a 0 must appear as absent, not as a silent 0")

    print()
    print("=" * 78)
    print("3. Haiku's 3-way accounting — can it be made NOT to close?")
    print("=" * 78)
    h_src = (REPO / "scripts/haiku_as_classifier_at_run_scale_2026-10-15.py").read_text()
    BATCH = re.compile(re.search(r'BATCH = re\.compile\(r"([^"]+)"\s*\n\s*r"([^"]+)"\)',
                                 h_src).group(1)
                       + re.search(r'BATCH = re\.compile\(r"([^"]+)"\s*\n\s*r"([^"]+)"\)',
                                   h_src).group(2))
    log = (REPO / "bench/logs/free_run1_directive_whole_20261015T061123Z"
           "_20261015T061124Z/console.log").read_text(errors="replace")
    sizes = [int(m.group(3)) for m in BATCH.finditer(log)]
    check("batch sizes", sizes, [14, 2, 5, 1])
    check("batch total", sum(sizes), 22)
    # Mutate: drop one BLOCKED line and the accounting must STOP closing.
    mutated = log.replace("BLOCKED by MATHEMATICAL guard", "XXXXXXX by MATHEMATICAL guard", 1)
    BLOCK = re.compile(r"LLM classifier: (\S+) — regex=(\w+) llm=(\w+) "
                       r"\(conf=([0-9.]+), BLOCKED by (\w+) guard, ([0-9.]+)s\)")
    n_block_real = len(BLOCK.findall(log))
    n_block_mut = len(BLOCK.findall(mutated))
    check("BLOCKED lines in the real log", n_block_real, 3)
    check("BLOCKED lines after dropping 1", n_block_mut, 2)
    AGREE = re.compile(r"LLM classifier: (\d+)/(\d+) agree with regex")
    agreed = sum(int(m.group(1)) for m in AGREE.finditer(log))
    OVER = re.compile(r"LLM classifier OVERRIDE: ")
    n_over = len(OVER.findall(log))
    check("the real accounting closes", agreed + n_over + n_block_real, 22)
    closes_mut = (agreed + n_over + n_block_mut) == 22
    check("the MUTATED accounting still closes", closes_mut, False,
          "if a dropped line still closes, the check is vacuous")

    print()
    print("=" * 78)
    print("4. The coherence producer — is its layer-2 test actually discriminating?")
    print("=" * 78)
    c = load("the_coherence_recalibration_is_inert_three_ways_2026-10-15.py")
    l2 = c.layer2_no_persistence()
    check("mutation did NOT survive the process", l2["mutation_survived_the_process"], False)
    check("the in-process value really was the sentinel", l2["value_after_mutation_in_process"], "0.123456")
    check("the fresh process really read the literal", l2["value_in_a_fresh_process"], "0.02")
    if l2["value_after_mutation_in_process"] == l2["value_in_a_fresh_process"]:
        FAILURES.append("layer 2 cannot distinguish a surviving mutation from a dead one")
    l3 = c.layer3_shape_mismatch()
    check("the calibrator returns the literal on real logs", l3["identical_to_literal"], True)
    check("and MOVES on a correctly shaped fixture", l3["calibrator_works_when_fed_its_shape"], True,
          "if it never moves, 'identical on real logs' proves nothing")

    print()
    print("=" * 78)
    print("5. The elicitation producer — would it REPORT a hit if one existed?")
    print("=" * 78)
    e = load("the_unresolved_section_elicitation_2026-10-15.py")
    pat_src = e.live_pattern()
    pat = re.compile(pat_src, re.S)
    planted = ("prose prose\nFALSIFIER: C0123\n```python\nassert 1 == 1\n```\nmore prose")
    found = pat.findall(planted)
    check("the live pattern finds a planted form", len(found), 1,
          "a pattern that matches nothing would make any zero meaningless")
    check("and it extracts the id", found[0][0] if found else None, "C0123")
    check("it does NOT match prose with no fenced code", len(pat.findall("FALSIFIER: C0123 and nothing else")), 0)

    print()
    print("=" * 78)
    print("6. The severity key-property producer — is '0 of 41' a measurement?")
    print("=" * 78)
    import tempfile as _tf

    kp = load("the_severity_key_property_never_fired_2026-10-15.py")
    _T = ("[09:00:00]   hardened-gate telemetry: {{'gamma_crit_settled': 1.0, "
          "'severity_spec_shadow': {{'V_true': {vt}, 'V_none': {vn}, 'V_false': {vf}, "
          "'critical_asserted': 12, 'critical_spec': 12, 'crossed_downward': [], "
          "'key_property_violations': []}}, 'total_findings': {tf}, "
          "'unresolved_critical': 0, 'contested': 0, 'mode': 'full'}}\n")

    def _mk(tmp, body):
        d = pathlib.Path(tmp) / "fake_run"
        d.mkdir(parents=True, exist_ok=True)
        (d / "console.log").write_text(body)
        return d

    with _tf.TemporaryDirectory() as _t:
        c = kp.census(_mk(_t, _T.format(vt=10, vn=5, vf=4, tf=19)))
        # Do NOT write `c and c["V_false"]`: binding a whole return value and
        # testing it for truth is the shape `test_operational_scripts.py` refuses,
        # because it is true in every case including failure. Say what is required.
        check("census() returned a record at all", c is not None, True)
        check("a PLANTED V_false=4 is reported",
              c["V_false"] if c is not None else None, 4,
              "if a planted V_false is missed, the 0-of-41 claim is vacuous")
    with _tf.TemporaryDirectory() as _t:
        c = kp.census(_mk(_t, "[09:00:00]   hardened-gate telemetry: "
                              "{'gamma_crit_settled': 1.0, 'total_findings': 19}\n"))
        check("telemetry with NO census -> None", c, None,
              "absence must not be read as a zero census")
    with _tf.TemporaryDirectory() as _t:
        check("an empty log -> None", kp.census(_mk(_t, "")), None)
    with _tf.TemporaryDirectory() as _t:
        c = kp.census(_mk(_t, _T.format(vt=10, vn=5, vf=0, tf=19)))
        s_ = c["V_true"] + c["V_none"] + c["V_false"]
        check("a census that does NOT sum fails to close", s_ == c["total_findings"], False)
    with _tf.TemporaryDirectory() as _t:
        c = kp.census(_mk(_t, _T.format(vt=1, vn=1, vf=0, tf=2)
                              + _T.format(vt=14, vn=5, vf=0, tf=19)))
        check("the LAST census is used, not an earlier one", c["total_findings"], 19,
              "else a mid-run figure could be reported as final")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    if FAILURES:
        print(f"  {len(FAILURES)} discrimination failure(s):")
        for f in FAILURES:
            print(f"    - {f}")
        print("  AT LEAST ONE OF TODAY'S FIGURES RESTS ON A PREDICATE THAT DOES NOT")
        print("  DISCRIMINATE, AND MUST BE WITHDRAWN UNTIL REPAIRED.")
    else:
        print("  all 5 producers discriminate: every deliberately wrong input changed")
        print("  the answer, and every planted true case was found.")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    # Inside the guard, NOT at module scope: `test_operational_scripts.py`
    # imports every script with the script path in argv[1], and a top-level
    # answer_help would refuse that as an unrecognised argument and exit 2.
    # A script that does its work at import time cannot be inspected, which
    # is the real defect this restructuring fixes.
    answer_help(__doc__, __file__)
    sys.exit(main())
