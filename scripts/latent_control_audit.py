#!/usr/bin/env python3
"""Which controls have never left a trace in the archive?

A guard nobody has seen fire is a hypothesis, not a control. Three were found by
hand in the days to 2026-09-01: the A4 fail-safe reachable by 0 of 43 configs,
`bench/canary_seeding.py` (42 passing tests, wired into no run), and the
discrimination control. Each was found by accident, and one -- the mid-run
target integrity guard -- was wrongly called dead because the wrong key was
counted.

This enumerates them instead. It reads report keys out of the runner's source,
counts them across archived run reports, and classifies each by CC2's triage
rule (panel review, 2026-09-01):

  1. unconditional write, 0 occurrences        -> UNREACHABLE as configured
  2. gated write, unconditional sibling seen    -> SILENT, and demonstrably ran
  3. gated write, no sibling, 0 occurrences     -> AMBIGUOUS, the actionable one

Only category 3 needs work, and the fix for it is to give every guard an
unconditional "I ran" counter beside its alarm, which turns future category 3
into category 1 or 2 for free.

Two design constraints, both learned from drafts of this script that got them
wrong:

  AGE CONTROL. A key committed today appears in zero archived runs because the
  runs predate it, not because it is dead. Without this the tool reports the
  session's own work as dead code and is disbelieved on first use.

  ALIAS RESOLUTION. `routing_enabled` looks disabled everywhere and is enabled
  in 21 configs under the legacy key `take_up_slack_enabled`. A detector that
  cries wolf on a live control gets switched off, and then you have one more
  never-run control -- a meta one.

KNOWN LIMITATION, stated because an unstated one is how the last three defects
survived. Key extraction matches any subscript assignment to a local named
`result`, and the runner has more than one such local. Generic names -- `reason`,
`tier`, `terminate` -- are therefore reported without being run-report keys at
all. They are false positives in the AMBIGUOUS bucket, not missed controls: the
tool over-reports and does not under-report, which is the safe direction for a
detector whose whole purpose is finding things nobody looked at.

Offline, stdlib only, no network, no model calls. `--help` costs nothing.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"

# ALIAS RESOLUTION DOES NOT APPLY TO THIS TOOL, and saying so is the fix.
#
# CC2's original design note named alias resolution as mandatory: `routing_enabled`
# looks dead and is enabled in 21 configs under the legacy key
# `take_up_slack_enabled`. That is true, and it is about CONFIG FLAGS.
#
# This tool audits REPORT KEYS -- the strings the runner writes into a run
# report -- which are a different object with no legacy aliases. I imported the
# constraint into the wrong tool, then shipped a `CONFIG_ALIASES` map that was
# read by nothing and an output field, `aliases_applied`, that announced it had
# been applied. fable, panel review 2026-09-02: the map "is never applied -- the
# docstring's alias resolution design constraint is echoed into output and
# enforced by nothing."
#
# A field asserting work that never happened is worse than dead code, and my own
# test asserted the ECHO rather than the behaviour, which is how it survived.
# The map and the claim are removed. The real constraint stands for whoever
# builds the config-flag audit, and it is recorded on the runway at 0C.25.


def _report_key_writes(source: str) -> dict:
    """Report keys the runner writes, and whether each write is conditional.

    A write is 'gated' when it sits inside an `if` anywhere between the enclosing
    function and the statement. That is deliberately generous: the question is
    whether a key can be absent from a run that executed the code, and any
    branch makes the answer yes.
    """
    tree = ast.parse(source)
    writes = defaultdict(lambda: {"gated": True, "lines": []})

    class V(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0

        def visit_If(self, node):
            self.depth += 1
            self.generic_visit(node)
            self.depth -= 1

        def _record(self, key, line):
            w = writes[key]
            w["lines"].append(line)
            if self.depth == 0:
                w["gated"] = False

        def visit_Assign(self, node):
            for t in node.targets:
                if (isinstance(t, ast.Subscript)
                        and isinstance(t.value, ast.Name)
                        and t.value.id == "result"
                        and isinstance(t.slice, ast.Constant)
                        and isinstance(t.slice.value, str)):
                    self._record(t.slice.value, node.lineno)
            self.generic_visit(node)

        def visit_Call(self, node):
            f = node.func
            if (isinstance(f, ast.Attribute) and f.attr == "setdefault"
                    and isinstance(f.value, ast.Name) and f.value.id == "result"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                self._record(node.args[0].value, node.lineno)
            self.generic_visit(node)

    V().visit(tree)
    return dict(writes)


def _key_first_committed(key: str) -> int | None:
    """Unix time the key first entered the file, or None if git cannot say."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=AM", "--format=%at", "-S", key,
             "--", "bench/reference_runner_v3.py", "bench/reference_runner_v2.py"],
            cwd=str(REPO), capture_output=True, text=True, timeout=120)
        stamps = [int(x) for x in out.stdout.split() if x.isdigit()]
        return min(stamps) if stamps else None
    except Exception:                                     # noqa: BLE001
        return None


def _is_simulated(doc: dict, fp: pathlib.Path) -> bool:
    """True when this PARSED report came from a simulated run.

    PARSE FIRST, CLASSIFY SECOND. The previous version read the first 4,000
    characters as a string and excluded anything containing "-SIM". CC2, panel
    review 2026-09-02, measured what that actually did: **9 real panel
    transcripts on disk are excluded purely for discussing simulation**, one of
    them hitting the marker 76 characters from the window boundary. In every
    real report the first model-authored description begins between character
    209 and 1,656, so thousands of characters of arbitrary model prose sit
    inside that window -- and a real run reviewing `routing.py` or this runner,
    both of which contain the literal `-SIM`, would quote it in round 0 and
    exclude itself from its own evidence base.

    Meanwhile the runner already writes three authoritative provenance signals,
    and the heuristic read none of them: in a real simulated report
    `severity_provenance` sits at character 494,477 and `_simulated` at 503,114,
    both far outside the window the audit chose to look in. It reimplemented a
    weaker string test instead of reading the key.

    Directory naming is kept as a second signal, because a directory can be
    renamed while the labels inside it cannot -- but it is now checked against
    the parsed document, not a text window.
    """
    sa = doc.get("severity_admissibility")
    if isinstance(sa, dict) and sa.get("severity_provenance") == "simulated":
        return True
    if doc.get("_simulated"):
        return True
    models = doc.get("models") or doc.get("model_labels") or []
    if isinstance(models, (list, tuple)) and any(
            isinstance(m, str) and m.upper().endswith("-SIM") for m in models):
        return True
    name = fp.parent.name.lower()
    return name.startswith("sim") or "_sim" in name or "simulated" in name


def _archive() -> tuple[list, int]:
    """(report dicts, newest run mtime). Reports only -- not every json."""
    reports, newest = [], 0
    for fp in LOGS.glob("**/*.json"):
        # EXCLUDE SIMULATED RUNS FROM THE WITNESS SET.
        #
        # THE LINE THIS REPLACES WAS A DEAD CONDITIONAL -- `if <cond>: pass` --
        # so it excluded nothing and simulated reports counted as archive. Found
        # by fable in panel review, 2026-09-01, and the consequence was
        # circular: the three keys this tool reported as SEEN were seen ONLY
        # because the canary rehearsal's own report sits in bench/logs, and it
        # sits there twice via a duplicated run directory. A tool built to find
        # "controls nobody has seen fire" was accepting the runner's own
        # rehearsal, double-counted, as the evidence that they had fired.
        #
        # A simulated run is a rehearsal of the machinery, not a sighting in the
        # field. It cannot witness that a control fires in real use.
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        if _is_simulated(d, fp):
            continue
        if isinstance(d, dict) and ("registry" in d or "converged_at" in d
                                    or "runner_version" in d):
            reports.append(d)
            newest = max(newest, int(fp.stat().st_mtime))
    return reports, newest


def audit(quiet: bool = False, newest_override: int | None = None) -> dict:
    """Audit the runner's report keys against the archive.

    `newest_override` pins the age baseline instead of taking it from the newest
    archived report's mtime. It exists so the age control can be COMMISSIONED:
    with the live archive, whether anything is TOO_NEW depends on when the last
    run happened, so a test written against live state passes whether the
    control works or not. Measured 2026-09-01: disabling the rule outright
    (`too_new = False`) left all nine tests of this script green, because the
    canary run had just moved the baseline past every new key. A guard that
    cannot be made to fire on demand is not a guard.
    """
    src = RUNNER.read_text(encoding="utf-8")
    writes = _report_key_writes(src)
    reports, newest = _archive()
    if newest_override is not None:
        newest = int(newest_override)

    counts = {k: sum(1 for r in reports if k in r) for k in writes}
    # A gated key's siblings are the unconditional keys written nearby -- within
    # 40 lines, which covers a guard's own try block without spanning functions.
    unconditional = {k for k, w in writes.items() if not w["gated"]}

    rows = []
    for key, w in sorted(writes.items()):
        seen = counts[key]
        first = _key_first_committed(key)
        too_new = bool(first and newest and first > newest)
        sibling = None
        # THE SIBLING CHECK APPLIES TO UNCONDITIONAL WRITES TOO (2026-09-04).
        #
        # It was gated on `w["gated"]`, so a write that is UNCONDITIONAL and
        # unseen fell straight through to UNREACHABLE even when a witnessed
        # sibling proved the surrounding code ran. That misfires on exactly the
        # repair this script recommends: its own header says to give a guard an
        # unconditional "I ran" counter, and doing so for
        # `target_integrity_events` flipped it from SILENT_BUT_RAN to
        # UNREACHABLE -- the tool reporting a regression for taking its own
        # advice.
        #
        # The age control cannot catch this, and that is worth stating plainly:
        # `_key_first_committed` dates the KEY NAME via `git log -S`, so a key
        # that has existed for months but became unconditional today reads as
        # old. Dating the gating rather than the name would need a structural
        # diff over history. Widening the sibling rule is the smaller and more
        # direct repair, and it is sound on the same logic the gated case uses:
        # a witnessed sibling within 40 lines proves the code ran, and that
        # proof does not depend on whether THIS write is gated.
        if seen == 0:
            for other in unconditional:
                if any(abs(a - b) <= 40
                       for a in w["lines"] for b in writes[other]["lines"]):
                    if counts[other] > 0:
                        sibling = other
                        break
        if too_new:
            verdict = "TOO_NEW"
        elif seen > 0:
            verdict = "SEEN"
        elif sibling:
            verdict = "SILENT_BUT_RAN"
        elif w["gated"]:
            verdict = "AMBIGUOUS"
        else:
            verdict = "UNREACHABLE"
        rows.append({"key": key, "seen_in_reports": seen,
                     "gated": w["gated"], "sibling": sibling,
                     "first_committed": first, "verdict": verdict,
                     "lines": w["lines"][:3]})

    if not quiet:
        order = {"UNREACHABLE": 0, "AMBIGUOUS": 1, "SILENT_BUT_RAN": 2,
                 "TOO_NEW": 3, "SEEN": 4}
        print(f"  {len(reports)} archived reports; {len(writes)} report keys "
              f"written by the runner\n")
        for r in sorted(rows, key=lambda r: (order[r["verdict"]], r["key"])):
            if r["verdict"] == "SEEN":
                continue
            note = ""
            if r["sibling"]:
                note = f"  (witness: {r['sibling']})"
            print(f"  {r['verdict']:15s} {r['key']:42s} "
                  f"seen={r['seen_in_reports']:<4d}{note}")
        print(f"\n  SEEN in the archive and needing nothing: "
              f"{sum(1 for r in rows if r['verdict'] == 'SEEN')}")
        print("  Only AMBIGUOUS is actionable. Give the guard an unconditional")
        print("  'I ran' counter beside its alarm and it becomes decidable.")
    return {"reports": len(reports), "rows": rows,
            "baseline_mtime": newest,
            "audited_object": "report keys written by the runner "
                              "(NOT config flags -- those have legacy "
                              "aliases and need their own audit)"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--as-of", type=int, default=None, metavar="EPOCH",
                    help="pin the age baseline to this unix time instead of the "
                         "newest archived report (used to commission the age "
                         "control, and to re-read the archive as it stood)")
    a = ap.parse_args()
    out = audit(quiet=a.json, newest_override=a.as_of)
    if a.json:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
