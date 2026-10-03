# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'merge_adjudication_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f21b4ee0ca7dfde44feb6ef063e697cc72221df1f7ca912f14c84a1f2e7790c9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_star_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1ee2fc5d7a15dfb79a9a0b3b3e92b015452baba0186f6c6c0e75ccef1eb68de3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER (D-B): a sub-critical key-access refusal drains A4 and is reported nowhere.

`unverified_critical_count` has had NO severity gate since 2026-09-06 (founder
ruling 23); `integrity_refused_criticals` gates at severity >= 0.7. So an
UNCONFIRMED entry below 0.7 carrying an integrity refusal is removed from the
A4 blocker by `_integrity_violation_excluded` and named in no report -- a
SILENT exclusion, which is the one outcome the founder's 2026-10-02 ruling
forbids by its own wording.

The 48-combination grid in test_one_predicate_excludes_and_reports_2026-10-02
cannot see this: every entry it builds pins severity=0.9, and its randomised
arm recomputes the expectation with the SAME 0.7 gate the reporter uses, so it
compares the reporter against itself rather than against the counter.

Run:  PYTHONPATH=. python3 bench/tests/falsifier_subcritical_refusal_is_silent_2026-10-03.py
Fails (AssertionError + "FALSIFIED") iff the defect is present.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from bench.reference_runner_v3 import FindingRegistry, CRITICAL_SEVERITY_THRESHOLD

def mk(sev, refused):
    r = FindingRegistry()
    e = {"status": "UNCONFIRMED", "severity": sev, "falsifier_code": "",
         "falsifier_verdict": "", "title": "t"}
    if refused:
        e["integrity_refused"] = True
    r.entries["C0001"] = e
    return r

print(f"CRITICAL_SEVERITY_THRESHOLD = {CRITICAL_SEVERITY_THRESHOLD}")
rows = []
for sev in (0.9, 0.5):
    for refused in (False, True):
        r = mk(sev, refused)
        rows.append((sev, refused, r.unverified_critical_count(), r.integrity_refused_criticals()))
        print(f"  sev={sev} integrity_refused={refused!s:5}  A4_count={rows[-1][2]}  reported={rows[-1][3]}")

# Baseline: with no refusal, BOTH severities block A4 (no severity gate since 2026-09-06).
assert mk(0.9, False).unverified_critical_count() == 1
assert mk(0.5, False).unverified_critical_count() == 1, "premise dead: counter DOES gate severity"

crit   = mk(0.9, True)
subcrit= mk(0.5, True)
print()
print(f"  critical  : drained={crit.unverified_critical_count()==0} reported={crit.integrity_refused_criticals()}")
print(f"  subcritical: drained={subcrit.unverified_critical_count()==0} reported={subcrit.integrity_refused_criticals()}")

silent = (subcrit.unverified_critical_count() == 0) and (subcrit.integrity_refused_criticals() == [])
if silent:
    print("FALSIFIED")
    raise AssertionError(
        "D-B CONFIRMED: a sub-critical (sev<0.7) UNCONFIRMED entry carrying a key-access "
        "refusal is removed from unverified_critical_count (the A4 blocker) by "
        "_integrity_violation_excluded, and is NOT returned by integrity_refused_criticals "
        "because that reader gates severity >= 0.7. Excluded-implies-reported FAILS.")
print("CLEAN EXIT: no silent drain")
