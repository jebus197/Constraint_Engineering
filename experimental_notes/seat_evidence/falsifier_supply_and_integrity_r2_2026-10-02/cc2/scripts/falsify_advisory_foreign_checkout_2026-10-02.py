# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 69268dcfbfce39d0272a8f979bfa1091c70c1ef2de47eacef6be5a5a263f8cb8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: the key-access ADVISORY fires on a LOCATION ARTEFACT, and the
repair's cannot-fail guard really does catch a blanket silencer.

Imports the REAL `bench/key_access_forensics.py` and scans the REAL archived run
`bench/logs/prose_convergence_run1b_2026-10-02_*`. Nothing is retyped.

Three arms, each decided mechanically:

  ARM 1  AS SHIPPED. The advisory must be SILENT on run 1b (no key was read)
         and LOUD on a planted key read. Prints FALSIFIED if not.

  ARM 2  THE DEFECT, RECONSTRUCTED. `names_this_checkout` is neutralised to
         always-False, which is byte-for-byte the behaviour before this repair
         (the module had no access to the predicate at all). The advisory must
         then FIRE on run 1b. This is the demonstration that the defect was
         real and that the repair is what fixes it -- an arm that stayed quiet
         here would mean the repair is not load-bearing.

  ARM 3  THE GUARD, MUTATION-TESTED. `Report.advisory_confirmed` is replaced by
         a blanket silencer returning []. That is the hazard the brief names: a
         general falsifier that cannot fail is worse than none. ARM 1's
         silence-on-run-1b check PASSES under the mutant, so silence alone is
         not evidence; the guard check (a plant must still fire) must FAIL.
         If the guard survives the mutant, the guard is decoration.

Exits 0 and prints NOT FALSIFIED only when arm 1 holds, arm 2 reproduces the
defect, and arm 3's guard dies on the mutant.

Run:  python3 scripts/falsify_advisory_foreign_checkout_2026-10-02.py
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench import key_access_forensics as KAF  # noqa: E402
from bench.key_access_forensics import Report  # noqa: E402

RUN_1B = (ROOT / "bench" / "logs"
          / "prose_convergence_run1b_2026-10-02_20261002T044234Z")
ALIEN = "/Users/georgejackson/Developer_Projects/Constraint_Engineering"
_TMPS: list[tempfile.TemporaryDirectory] = []


def plant(body: str) -> pathlib.Path:
    td = tempfile.TemporaryDirectory()
    _TMPS.append(td)
    dest = pathlib.Path(td.name) / "run" / "panel_worktree_harvest" / "files" / "bench"
    dest.mkdir(parents=True)
    (dest / "falsifier_verify.py").write_text(
        (ROOT / "bench" / "falsifier_verify.py").read_text() + "\n" + body,
        encoding="utf-8")
    return pathlib.Path(td.name) / "run"


def probe(run: pathlib.Path) -> tuple[int, int, bool]:
    rep = KAF.scan_run(run, repo_root=ROOT)
    return (len(rep.advisory_confirmed), len(rep.audit_confirmed),
            KAF.build_end_of_run_advisory(rep) is not None)


KEY_PLANT = "k = json.load(open('/Users/x/exp99_answer_key.json'))\n"


def main() -> int:
    if not RUN_1B.is_dir():
        print("UNTOOLABLE: run 1b is not in this tree")
        return 2
    fail: list[str] = []

    print("ARM 1  AS SHIPPED")
    a_adv, a_aud, a_fires = probe(RUN_1B)
    print(f"  run 1b           advisory={a_adv:4d} audit={a_aud:4d} fires={a_fires}")
    p_adv, p_aud, p_fires = probe(plant(KEY_PLANT))
    print(f"  planted key read advisory={p_adv:4d} audit={p_aud:4d} fires={p_fires}")
    if a_fires:
        fail.append("arm1: advisory fired on a run that read no key")
    if not p_fires:
        fail.append("arm1: a planted answer-key read did not fire")

    print("\nARM 2  THE DEFECT, with names_this_checkout neutralised")
    real_pred = KAF.names_this_checkout
    KAF.names_this_checkout = lambda *a, **k: False
    try:
        d_adv, d_aud, d_fires = probe(RUN_1B)
    finally:
        KAF.names_this_checkout = real_pred
    print(f"  run 1b           advisory={d_adv:4d} audit={d_aud:4d} fires={d_fires}")
    if not d_fires:
        fail.append("arm2: the defect did not reproduce; the repair is not "
                    "what makes run 1b quiet")
    if d_adv <= a_adv:
        fail.append(f"arm2: advisory did not grow ({d_adv} <= {a_adv})")

    print("\nARM 3  THE GUARD, against a blanket silencer")
    real_prop = Report.advisory_confirmed
    Report.advisory_confirmed = property(lambda self: [])
    try:
        m_quiet = probe(RUN_1B)[2]
        m_plant = probe(plant(KEY_PLANT))[2]
    finally:
        Report.advisory_confirmed = real_prop
    print(f"  mutant: silent on run 1b = {not m_quiet}  (arm 1's check PASSES)")
    print(f"  mutant: fires on a plant = {m_plant}  (the GUARD must say False)")
    if m_quiet:
        fail.append("arm3: the mutant is not silent; not a blanket silencer")
    if m_plant:
        fail.append("arm3: THE GUARD DID NOT CATCH A BLANKET SILENCER -- the "
                    "guard is decoration")
    print("  => the guard FAILS on the mutant, as a guard must: "
          f"{not m_plant}")

    print()
    if fail:
        print("FALSIFIED")
        for f in fail:
            print("  -", f)
        raise AssertionError("; ".join(fail))
    print("NOT FALSIFIED: silent on an artefact, loud on a read, the defect "
          "reproduces when the predicate is removed, and the cannot-fail guard "
          "dies on a blanket silencer.")
    return 0


if __name__ == "__main__":
    import argparse
    argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None).parse_args()
    raise SystemExit(main())
