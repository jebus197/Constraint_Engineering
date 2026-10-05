# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d6d9ffc54a074abc2fdbb3bee51aeed795fef1a7722c7764272c13569a12c44e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The provenance gate scored the REQUIRED falsifier form as detached, 644 times.

WHAT THIS MEASURES, and why it decides something rather than describing it.
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
proposes to rank the routing ladder on a provenance-gated falsification rate,
with `scripts/competence_provenance.py` promoted from an advisory script to a
GATE ON POOL ENTRY. The ladder's order is not a report -- it decides which model
is asked to resolve the hardest findings -- so the gate's classifier is wired
into the mechanics, and a classifier that misreads is an inversion, not a typo.

The classifier was, until 2026-10-05, a substring match over the raw falsifier
text for `open\\s*\\(|read_text|\\.read\\s*\\(|linecache|getlines`. It failed in
both directions, and both failures favour the model that ignores the evidence:

  FALSE "reads"    -- the token only had to appear. A falsifier that restates the
                      document from memory and carries the comment
                      `# could open(it) but I remember the numbers` scored as a
                      reader, as did one holding `note = "did not open("`.
  FALSE "detached" -- a code falsifier reaches its target by `import`, which is
                      the form the CDSFL core directive REQUIRES and the form
                      `bench/routing.py`'s own comment relies on. `import
                      bench.cdsfl_registry.engine` contains none of the five
                      tokens, so every compliant code falsifier scored detached.

Section 2 below also demonstrates the gate's SECOND defect, which was a plain
logic error independent of the classifier: the predicate was per MODEL
(`confirmed > 0 and reads == 0`), so one genuine reader anywhere in a run
licensed a numerator built entirely from detached confirmations.

Both are repaired in `scripts/competence_provenance.py` and pinned by
`bench/tests/test_provenance_gate_is_per_confirmation_2026-10-05.py`. This
script is the producer for the figures that motivated the repair, and it
re-measures them from the archive on every run rather than quoting them.

Run:  python3 scripts/provenance_gate_misreads_the_mandated_form_2026-10-05.py
"""
from __future__ import annotations

import argparse
import collections
import glob
import importlib.util
import json
import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]

#: THE CLASSIFIER AS IT STOOD BEFORE 2026-10-05, pinned here as the historical
#: constant it is. Reading it out of the live module would make this script stop
#: reproducing its own headline the moment the defect it measures is repaired --
#: the failure mode recorded in `scripts/the_blockers_are_shown_as_settled_2026-10-05.py`.
_REGEX_AS_SHIPPED = re.compile(r"open\s*\(|read_text|\.read\s*\(|linecache|getlines")


def _regex_style(code: str) -> str:
    c = (code or "").strip()
    if not c:
        return "none"
    return "reads" if _REGEX_AS_SHIPPED.search(c) else "detached"


def _load_live():
    spec = importlib.util.spec_from_file_location(
        "competence_provenance_live", REPO / "scripts" / "competence_provenance.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="provenance_gate_misreads_the_mandated_form_2026-10-05.py",
        description=(__doc__ or "").strip().split("\n\n")[0])
    p.add_argument("--logs", default=str(REPO / "bench" / "logs"),
                   help="directory of archived run directories")
    return p.parse_args(argv)


#: (label, falsifier source, run target) -- the 7 probe cases, all synthetic, so
#: the comparison does not depend on which runs happen to be in this checkout.
_PROBES = [
    ("CDSFL-mandated import of the real target",
     "from bench.cdsfl_registry.engine import PolicyEngine\n"
     "assert PolicyEngine().validate(), 'FALSIFIED'\n",
     "bench/cdsfl_registry/engine.py"),
    ("dotted import of the real target",
     "import bench.cdsfl_registry.engine as E\nassert E.PolicyEngine, 'FALSIFIED'\n",
     "bench/cdsfl_registry/engine.py"),
    ("detached: open( appears only in a COMMENT",
     "# could open(it) but the numbers are in the document\n"
     "assert 175 == 21, 'FALSIFIED'\n",
     "bench/routing.py"),
    ("detached: open( appears only in a STRING",
     "note = 'did not open('\nassert 175 == 21, 'FALSIFIED'\n",
     "bench/routing.py"),
    ("reads an UNRELATED file, asserts from memory",
     "open('/dev/null').close()\nassert 175 == 21, 'FALSIFIED'\n",
     "bench/routing.py"),
    ("genuine reader of the target",
     "assert 'x' in open('bench/routing.py').read(), 'FALSIFIED'\n",
     "bench/routing.py"),
    ("linecache (CC2's counterexample to word-matching)",
     "import linecache\nlinecache.getlines('bench/routing.py')\n",
     "bench/routing.py"),
]


def probe_table(live) -> list:
    rows = []
    for label, code, target in _PROBES:
        rows.append((label, _regex_style(code), live.falsifier_style(code, target)))
    return rows


def archive_census(live, logs: pathlib.Path):
    """Per CONFIRMED falsifier in the archive: regex verdict vs parsed verdict."""
    cross = collections.Counter()
    per_run = []
    for p in sorted(glob.glob(str(logs / "*" / "*_report.json"))):
        try:
            doc = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            per_run.append((pathlib.Path(p).parent.name, -1, -1,
                            f"UNREADABLE: {type(exc).__name__}"))
            continue
        ents = (doc.get("registry") or {}).get("entries") or {}
        target = doc.get("target_file") or ""
        conf = clean = 0
        for e in ents.values():
            if e.get("falsifier_verdict") != "CONFIRMED":
                continue
            conf += 1
            code = e.get("falsifier_code")
            new = live.falsifier_style(code, target)
            cross[(_regex_style(code), new)] += 1
            if new == "reads":
                clean += 1
        if conf:
            per_run.append((pathlib.Path(p).parent.name, conf, clean, ""))
    return cross, per_run


def gate_defeat_demonstration(live) -> tuple:
    """2 detached CONFIRMED + 1 reading REFUTED. Returns (exit code, output)."""
    import contextlib
    import io
    entries = {
        "C0001": {"canonical_id": "C0001", "source_model": "Gemini",
                  "falsifier_code": "assert 175 == 21, 'FALSIFIED'",
                  "falsifier_verdict": "CONFIRMED"},
        "C0002": {"canonical_id": "C0002", "source_model": "Gemini",
                  "falsifier_code": "assert 3 == 4, 'FALSIFIED'",
                  "falsifier_verdict": "CONFIRMED"},
        "C0003": {"canonical_id": "C0003", "source_model": "Gemini",
                  "falsifier_code": "assert 'x' in open('bench/routing.py').read()",
                  "falsifier_verdict": "REFUTED"},
        "C0004": {"canonical_id": "C0004", "source_model": "DeepSeek",
                  "falsifier_code": "assert 'x' in open('bench/routing.py').read()",
                  "falsifier_verdict": "ERROR"},
    }
    with tempfile.TemporaryDirectory() as td:
        rep = pathlib.Path(td) / "synthetic_report.json"
        rep.write_text(json.dumps({"target_file": "bench/routing.py",
                                   "registry": {"entries": entries}}),
                       encoding="utf-8")
        argv = list(sys.argv)
        buf = io.StringIO()
        try:
            sys.argv = ["competence_provenance.py", str(rep)]
            with contextlib.redirect_stdout(buf):
                rc = live.main()
        finally:
            sys.argv = argv
    return rc, buf.getvalue()


def main(argv=None) -> int:
    args = _parse_args(argv)
    live = _load_live()
    logs = pathlib.Path(args.logs)

    print("=" * 78)
    print("1. THE CLASSIFIER, ON 7 SYNTHETIC CASES")
    print("=" * 78)
    print(f"  {'case':<48}{'regex (shipped)':>17}{'parsed (now)':>14}")
    wrong = 0
    for label, old, new in probe_table(live):
        flag = ""
        if (old == "reads") != (new == "reads"):
            wrong += 1
            flag = "   <<< the two disagree"
        print(f"  {label:<48}{old:>17}{new:>14}{flag}")
    print(f"\n  cases where the shipped regex and the parsed check disagree on"
          f" 'did it read the target': {wrong} of {len(_PROBES)}")

    print()
    print("=" * 78)
    print("2. THE GATE, EXECUTED ON A SYNTHETIC REGISTRY")
    print("=" * 78)
    rc, out = gate_defeat_demonstration(live)
    for line in out.splitlines():
        if line.strip():
            print("  " + line)
    print(f"\n  exit code: {rc}   (2 = UNSAFE TO RANK ON, 0 = pool entry granted)")
    print("  Under the predicate as it stood before 2026-10-05 "
          "(`confirmed > 0 and reads == 0`)")
    print("  this registry exited 0 and ranked Gemini FIRST at 67%, on a numerator")
    print("  made entirely of falsifiers that read nothing. One genuine reader")
    print("  anywhere in the run was enough to clear the gate.")

    print()
    print("=" * 78)
    print("3. THE ARCHIVE")
    print("=" * 78)
    if not logs.is_dir():
        print(f"  {logs} is not a directory; nothing to census.")
        return 1
    cross, per_run = archive_census(live, logs)
    total = sum(cross.values())
    if not total:
        print("  no CONFIRMED falsifier found in the archive.")
        return 1
    print(f"  CONFIRMED falsifiers read: {total}")
    print(f"  {'regex says':<12}{'parsed says':<14}{'count':>7}{'share':>9}")
    for (a, b), c in cross.most_common():
        print(f"  {a:<12}{b:<14}{c:>7}{c / total:>8.1%}")
    missed = cross[("detached", "reads")]
    print(f"\n  SCORED DETACHED BY THE REGEX AND DOES REACH THE TARGET: "
          f"{missed} of {total} = {missed / total:.1%}")
    print("  Every one inspected reaches it by `import bench.…`, the form the")
    print("  CDSFL core directive requires. A gate on pool entry keyed on the")
    print("  regex would have excluded the compliant majority.")
    false_reads = cross[("reads", "elsewhere")] + cross[("reads", "detached")]
    print(f"  SCORED READS BY THE REGEX AND DOES NOT NAME THE TARGET: {false_reads}")
    unreadable = [r for r in per_run if r[3]]
    bad_runs = [r for r in per_run if not r[3] and r[2] < r[1]]
    print(f"\n  runs with >=1 CONFIRMED                     : "
          f"{len([r for r in per_run if not r[3]])}")
    print(f"  runs with >=1 CONFIRMED that is NOT clean   : {len(bad_runs)}")
    if unreadable:
        print(f"  *** {len(unreadable)} report(s) could not be read and are NOT in the")
        print(f"      census, so the figures above are a LOWER BOUND: "
              f"{[r[0] for r in unreadable[:4]]}")
    else:
        print("  reports that could not be read              : 0 "
              "(so the census is complete, not a lower bound)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
