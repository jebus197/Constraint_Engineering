"""A document that says "reproduce with script X" must agree with script X.

Four tracked documents carry a reproduce-with header. Three of them named a
script that no test in this suite had ever run, and on 2026-09-01 two of the
three were provably stale:

  Instrument_Inventory_2026-08-22.md  said 27 of 34 instruments had a
      commissioning candidate and 5 rows had been measured. Its own generator
      said 30 of 34 and 9 rows. Ten days of drift, including three rows
      re-measured to COMMISSIONED on 2026-08-30.

  Track_Record_Audit_2026-08-22.md    said the modern era was 11 runs, 566
      entries, 465 carrying falsifier code. Its own generator said 13, 586, 477.
      Two further runs had landed and nothing compared the two.

Both opened by promising the reader the figures were reproducible. Neither was
checked, because a reproduce-with line is a sentence, not a test.

This is the same class as the EXPERIMENT_RUN_LEDGER defect found the same day:
that document's test compared it against its generator's own hard-coded copy of
a wrong line number, so the pair agreed and neither matched the source. Here
there was not even a circular check.

Found by the panel (fable, 2026-09-01) after being asked to sweep for the class
rather than re-verify the one instance.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
NOTES = REPO / "experimental_notes"


def _run(script: str) -> str:
    out = subprocess.run([sys.executable, str(REPO / script)],
                         cwd=str(REPO), capture_output=True, text=True,
                         timeout=240)
    assert out.returncode == 0, (
        f"{script} does not run, so the document it backs cannot be checked:\n"
        f"{out.stderr[-800:]}")
    return out.stdout


def _one(pattern: str, text: str, what: str) -> tuple:
    m = re.search(pattern, text)
    assert m, f"could not read {what} (pattern {pattern!r} did not match)"
    return m.groups()


# (doc, script, check-name, generator pattern, document pattern)
# Each pair must extract the SAME tuple of figures from both sides.
CHECKS = [
    ("Instrument_Inventory_2026-08-22.md", "scripts/instrument_inventory.py",
     "commissioning-candidate split",
     r"(\d+) of 34 have a commissioning candidate; (\d+) do not",
     r"\*\*(\d+) of 34 instruments have a commissioning candidate\. (\d+) do not\.\*\*"),

    ("Instrument_Inventory_2026-08-22.md", "scripts/instrument_inventory.py",
     "rows measured directly",
     r"(\d+) rows have been measured directly",
     r"\*\*(\d+) rows measured"),

    ("Track_Record_Audit_2026-08-22.md", "scripts/track_record_audit.py",
     "modern era: runs, entries, with falsifier code",
     r"MODERN \(exp42\+[^)]*\)\s+—\s+(\d+) runs\s*\n\s*entries\s+(\d+)\s+"
     r"carrying falsifier code\s+(\d+)",
     r"\| exp42 onward, from 2026-06 \| (\d+) \| (\d+) \| (\d+) \("),

    ("Build_Experiment_Results_2026-08-22.md", "scripts/build_experiment_report.py",
     "attempts decided by a harness defect",
     r"(\d+) of (\d+) attempts were decided by a defect",
     r"\*\*(\d+) of (\d+) attempts were decided by one of these defects"),
]


@pytest.mark.parametrize(
    "doc,script,label,gen_pat,doc_pat", CHECKS,
    ids=[f"{c[0].split('_2026')[0]}::{c[2]}" for c in CHECKS])
def test_the_document_agrees_with_the_script_it_names(doc, script, label,
                                                      gen_pat, doc_pat):
    generated = _one(gen_pat, _run(script), f"{label} from {script}")
    documented = _one(doc_pat, (NOTES / doc).read_text(encoding="utf-8"),
                      f"{label} from {doc}")
    assert generated == documented, (
        f"{doc} is stale on {label}.\n"
        f"  {script} reports : {generated}\n"
        f"  the document says: {documented}\n"
        f"The document's own header promises these figures are reproducible. "
        f"Re-run the script and update the document, or correct the script.")


class TestEveryReproducibleDocIsChecked:
    """The discovery half. A new derived document must not arrive unchecked."""

    REPRODUCE = re.compile(
        r"[Rr]eproduce[^.\n]{0,40}`python3 ((?:scripts|bench)/[a-z0-9_]+\.py)`")

    # Documents whose reproduce-line names a script that is checked elsewhere,
    # or that is not a figure-producing generator.
    CHECKED_ELSEWHERE = {
        "experimental_notes/Recovery_Resource_Audit_2026-08-05.md":
            "names scripts/cdsfl_recover.py, a recovery tool exercised by "
            "test_operational_scripts.py and test_cdsfl_recover_repairs.py; the "
            "document records an audit of the recovery instruments rather than "
            "figures the script recomputes.",
    }

    def _docs_promising_reproduction(self):
        out = subprocess.run(["git", "ls-files", "*.md"], cwd=str(REPO),
                             capture_output=True, text=True, timeout=120)
        found = {}
        for f in out.stdout.split():
            if f.startswith("bench/logs/"):
                continue
            try:
                txt = (REPO / f).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            m = self.REPRODUCE.search(txt)
            if m:
                found[f] = m.group(1)
        return found

    def test_no_derived_document_goes_unchecked(self):
        covered = {f"experimental_notes/{c[0]}" for c in CHECKS}
        stray = {d: s for d, s in self._docs_promising_reproduction().items()
                 if d not in covered and d not in self.CHECKED_ELSEWHERE}
        assert not stray, (
            "these documents promise the reader their figures are reproducible, "
            "and nothing runs the script to find out:\n  "
            + "\n  ".join(f"{d} -> {s}" for d, s in stray.items())
            + "\nAdd an entry to CHECKS, or to CHECKED_ELSEWHERE with a reason.")

    def test_the_exemptions_still_describe_reality(self):
        for path, reason in self.CHECKED_ELSEWHERE.items():
            assert (REPO / path).is_file(), f"exempted document is gone: {path}"
            assert len(reason) > 60, f"exemption for {path} does not explain itself"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
