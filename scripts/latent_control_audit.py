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

  RESOLVED 2026-09-05, AND THE LIMITATION ABOVE WAS INCOMPLETE IN A WAY THAT
  MATTERED. It named `reason`, `tier` and `terminate` and asked the reader to
  tolerate them. It did NOT name `stalled`, which is written to the same local --
  so that one reached the reader as a hard UNREACHABLE, this tool's most alarming
  verdict, for a control present in 37 of 60 archived reports. The cause was not
  the extractor at all: the SEEN test was `k in report`, top level only, while
  the runner nests whole instrument blocks inside the per-round record
  (`"stall_detector": stall_result`, reference_runner_v3.py:12413). The test now
  searches at any depth. Measured effect: AMBIGUOUS 5 -> 2, UNREACHABLE 1 -> 0,
  SEEN 32 -> 36. The 4 that moved are exactly the 4 written to that local.

  Tolerating a known false-positive class is what this project did twice with the
  exit-code checker in test_operational_scripts, repairing it both times by
  extending a list of spellings; the third repair asked the structural question
  instead. Same choice made here.

Offline, stdlib only, no network, no model calls. `--help` costs nothing.
"""
from __future__ import annotations

import argparse
import ast
import datetime as _dt
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
    if _has_sim_seat_label(doc):
        return True
    name = fp.parent.name.lower()
    return name.startswith("sim") or "_sim" in name or "simulated" in name


#: Document fields that carry SEAT LABELS. Lists hold them as values; the
#: per-model mappings hold them as KEYS. Both forms are read, because the file
#: that actually leaked carried them only as keys -- see `_has_sim_seat_label`.
_LABEL_LISTS = ("models", "model_labels", "active_models")
_LABEL_MAPS = ("model_responses", "novelty_counts_per_model",
               "raw_counts_per_model", "per_model", "model_reports")


def _has_sim_seat_label(doc: dict) -> bool:
    """True when any seat label in this document is a `-SIM` stand-in.

    WHY THIS EXISTS, AND IT IS THE SAME DEFECT FOR THE THIRD TIME. `_archive`
    admits any document carrying `registry`, `converged_at` or `runner_version`.
    `_simulated_run_dirs` (added earlier on 2026-09-29) closed the case where a
    simulated run's `runner_state.json` leaked in by looking for a SIBLING
    document that proves simulation. **A run that DIES before writing its report
    has no such sibling.**

    Measured 2026-09-29: `bench/logs/shakedown_2026-09-29/arm1_harvest/` is the
    harvest of a simulated run that died at round 5 of 8 when its launching
    session ended. It holds no report. `_is_simulated` returned False for its
    `runner_state.json`, `_simulated_run_dirs()` returned 21 directories and not
    that one, so the file was admitted as a real archived run. Its recorded
    provenance is 2026-09-29, which moved the age baseline from 2026-08-23 to
    2026-09-29 -- **37.0 days** -- and silently disabled the TOO_NEW quarantine
    for every control key committed in that window. `critical_boundary_census`,
    first committed 2026-09-01, scored SILENT_BUT_RAN where the rule says
    TOO_NEW: a control reported as exercised-but-quiet when the archive is in
    fact older than the control is. That is the identical symptom
    `_simulated_run_dirs` records, arriving through an INTERRUPTED run.

    THE LEAKING FILE PROVES ITS OWN SIMULATION, which is why this is keyed here
    rather than on the directory. `runner_state.json` carries
    `novelty_counts_per_model` and `raw_counts_per_model`, and in that file every
    key is `CC2-SIM`, `Codex-SIM`, `Gemini-SIM`, `DeepSeek-SIM`, `ChatGPT-SIM`.
    The old test read `doc["models"]`, a LIST, and `runner_state.json` has no
    such field -- the labels were present the whole time, as dict KEYS, in a
    shape nothing looked at. Keying on the file's own content means an
    interrupted run is recognised without depending on a sibling, a directory
    name, or a report that was never written.

    IT CANNOT RESURRECT THE PROSE FALSE POSITIVE. `_is_simulated`'s docstring
    records that reading the first 4,000 characters for the string `-SIM`
    excluded **9 real panel transcripts** for merely DISCUSSING simulation. This
    reads seat LABELS from named structural fields, never prose, so a real run
    quoting `-SIM` while reviewing `routing.py` is unaffected. `-SIM` as a seat
    suffix is a MANDATED provenance marker for simulated stand-ins, never
    permitted on a real seat, so it is a sound key rather than a heuristic.
    """
    for field in _LABEL_LISTS:
        v = doc.get(field)
        if isinstance(v, (list, tuple)) and any(
                isinstance(m, str) and m.upper().endswith("-SIM") for m in v):
            return True
    for field in _LABEL_MAPS:
        v = doc.get(field)
        if isinstance(v, dict) and any(
                isinstance(m, str) and m.upper().endswith("-SIM") for m in v):
            return True
    return False


def _simulated_run_dirs() -> set:
    """Run directories holding at least 1 document that proves simulation.

    SIMULATION IS A PROPERTY OF THE RUN, NOT OF THE FILE (added 2026-09-29,
    panel item 2). `_is_simulated` reads 3 provenance keys plus the directory
    name, and the runner writes those keys into the run REPORT only. A simulated
    run also drops a `runner_state.json` beside it, which carries
    `runner_version` -- so `_archive` counted it as a report -- and carries none
    of the provenance keys, and whose directory is named `commissioning_arm*`
    rather than `sim*`. Measured on this archive: 4 files leak in that way,

        commissioning_arm{1,2,3,4}_*/runner_state.json

    and they were the NEWEST admitted "reports", so they set the age baseline.
    The consequence is not cosmetic: the baseline moved from 2026-08-27 to
    2026-09-22, 26.3 days later, which silently disables the TOO_NEW quarantine
    for every control key committed in that window. `critical_boundary_census`,
    first committed 2026-09-01, scored SILENT_BUT_RAN when the rule says TOO_NEW
    -- a control reported as exercised-but-quiet when in truth the archive is
    older than the control is.

    This is the SAME failure the docstring on `_archive` records from
    2026-09-01, arriving through a file the earlier fix never covered: the
    witness set accepting the runner's own rehearsal as field evidence.

    Nothing is removed. Every per-file signal still applies; a run directory is
    additionally simulated when ANY document in it proves the run was simulated.
    """
    sim: set = set()
    for fp in LOGS.glob("**/*.json"):
        if _is_seat_scratch(fp):
            continue
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        if isinstance(d, dict) and _is_simulated(d, fp):
            sim.add(fp.parent)
    return sim


#: Path segments that mark a file as SEAT-WRITTEN SCRATCH rather than an archive run.
#:
#: ADDED 2026-10-07. The audit globbed `bench/logs/**/*.json` and so walked into
#: `sandbox_harvest/`, where the harvester preserves whatever a panel seat wrote
#: inside its own sandbox. One such file --
#: `fingerprint_ladder_review_2026-10-05/sandbox_harvest/cc2/attempt-1/files/
#: .scratch/ps/synthetic_run/x_report.json` -- is a seat's SYNTHETIC report, written
#: by a model to test something, and the audit admitted it as an archive report. Its
#: directory name carries no timestamp, so it had no recorded provenance, and a tool
#: whose entire purpose is to refuse inferred dates was reporting an UNKNOWN age it
#: had created for itself.
#:
#: The harvest is deliberately preserved and must not be deleted -- it is often the
#: only copy of what a seat produced. It simply is not the archive, and a seat's
#: synthetic fixture is not a sighting of a control firing in the field.
_SEAT_SCRATCH_SEGMENTS = ("sandbox_harvest", ".scratch", "seat_evidence")


def _is_seat_scratch(fp) -> bool:
    """True for a file preserved FROM a seat's sandbox rather than written BY a run."""
    return any(seg in _SEAT_SCRATCH_SEGMENTS for seg in fp.parts)


#: Date formats that appear in this archive's run directory names. Measured
#: 2026-09-29: 221 of 287 run directories (77.0035%, Wilson [71.7975%, 81.4962%])
#: carry one, and 75 of the 77 ADMITTED reports do (97.4026%, Wilson
#: [91.0154%, 99.2848%]) -- statsmodels and a direct Wilson closed form agreeing
#: to 1.11e-16.
_PROV_PATTERNS = (
    (re.compile(r"(\d{4})(\d{2})(\d{2})T\d{6}Z"), (1, 2, 3)),   # 20260921T222021Z
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})"),        (1, 2, 3)),   # 2026-09-22
    (re.compile(r"(\d{4})(\d{2})(\d{2})_\d{6}"),    (1, 2, 3)),   # 20260921_222021
    # A BARE 8-DIGIT DATE, shape-constrained so an arbitrary 8-digit run id
    # cannot masquerade as one: century 19/20, month 01-12, day 01-31. This
    # pattern is LAST so the more specific forms win. It recovers the 2 admitted
    # reports that had no provenance under the first 3 patterns
    # (`baseline_confer_run10_20260403`, `..._run11_20260404`).
    (re.compile(r"((?:19|20)\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?!\d)"), (1, 2, 3)),
)


#: How many ancestor directories a run's recorded date may hide in.
_PROV_MAX_DEPTH = 5

#: Admitted reports whose path carries no date. Reported, never guessed at.
_NO_PROVENANCE: list = []


def _provenance_time(fp: "Path") -> "int | None":
    """A run's RECORDED date, read from its own path, or None.

    WHY THIS EXISTS, AND WHY mtime IS NOT ACCEPTABLE HERE. The age baseline used
    to come from `fp.stat().st_mtime`, so the age classification of an unchanged
    historical record was decided by filesystem metadata. Reproduced 2026-09-29
    against these very functions: touching one report with 0 bytes changed and an
    identical sha256 moved the baseline 58.0 days and flipped the TOO_NEW verdict
    for a control first committed 2026-09-01 from True to False. `cp`, `rsync`, a
    fresh checkout and a restore from backup all rewrite mtime, so the previous
    rule made a conclusion about history depend on when the files were last copied.

    Raised by an external assessment, 2026-09-29, whose minimal closure this
    implements: use recorded run provenance, and return an EXPLICIT UNKNOWN when
    it is unavailable rather than inventing a date. A file with no date in its
    path contributes NOTHING to the baseline; it is counted and reported.
    """
    # Bounded search depth, NAMED rather than a bare slice. A magic `[:5]` inside a
    # comprehension is what `test_operational_scripts.py` flags as an undisclosed cap,
    # and it is right to: a reader cannot tell a deliberate depth bound from a silently
    # truncated listing. This walks the file name and at most `_PROV_MAX_DEPTH`
    # ancestors, which covers `bench/logs/<run>/<sub>/report.json` with room to spare;
    # anything deeper returns None and is reported as UNKNOWN rather than guessed.
    parts = [fp.name]
    for depth, ancestor in enumerate(fp.parents):
        if depth >= _PROV_MAX_DEPTH:
            break
        parts.append(ancestor.name)
    for part in parts:
        for pat, groups in _PROV_PATTERNS:
            m = pat.search(part)
            if m:
                y, mo, dy = (int(m.group(g)) for g in groups)
                try:
                    return int(_dt.datetime(y, mo, dy, tzinfo=_dt.timezone.utc).timestamp())
                except ValueError:
                    continue
    return None


def _archive() -> tuple[list, int]:
    """(report dicts, newest RECORDED run date). Reports only -- not every json.

    The second element is derived from recorded provenance, never from filesystem
    metadata; see `_provenance_time`. It is 0 when no admitted report carries a
    date, which callers must treat as UNKNOWN rather than as "very old".
    """
    _NO_PROVENANCE.clear()
    reports, newest = [], 0
    # Run-level provenance, resolved BEFORE admitting anything. See
    # `_simulated_run_dirs` for the 4 files this closes and what they cost.
    sim_dirs = _simulated_run_dirs()
    for fp in LOGS.glob("**/*.json"):
        if _is_seat_scratch(fp):
            continue
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
        if _is_simulated(d, fp) or fp.parent in sim_dirs:
            continue
        if isinstance(d, dict) and ("registry" in d or "converged_at" in d
                                    or "runner_version" in d):
            reports.append(d)
            # RECORDED PROVENANCE ONLY. mtime is deliberately NOT a fallback: a
            # fallback would restore exactly the behaviour this closes, because
            # the undated files are the ones a copy would silently re-date.
            ts = _provenance_time(fp)
            if ts is None:
                _NO_PROVENANCE.append(str(fp.relative_to(LOGS.parent.parent)))
            else:
                newest = max(newest, ts)
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

    # SEARCH AT ANY DEPTH, NOT ONLY THE TOP LEVEL.
    #
    # This read `k in r`, which sees only top-level report keys. The runner
    # writes whole instrument blocks NESTED inside the per-round record --
    # `"stall_detector": stall_result` at reference_runner_v3.py:12413 is one --
    # so every key inside them counted as never seen.
    #
    # MEASURED 2026-09-05: `stalled`, `tier`, `terminate` and `reason` are
    # present, nested, in 37 of 60 archived reports, carrying real values
    # ("reason": "round 0 < 15"). Top-level scanning reported `stalled` as
    # UNREACHABLE -- the most alarming verdict this tool has -- for a control
    # that demonstrably ran.
    #
    # The module docstring's KNOWN LIMITATION named `reason`, `tier` and
    # `terminate` as accepted false positives and asked the reader to tolerate
    # them. It did NOT name `stalled`, which is written to the same local, so
    # that one reached the reader as a hard UNREACHABLE. Tolerating a
    # false-positive class is how the exit-code checker in
    # test_operational_scripts was "fixed" twice by extending a list of
    # spellings; the third repair was to ask the structural question instead.
    # Same choice here: search the structure rather than curate exemptions.
    def _present(key, obj):
        if isinstance(obj, dict):
            if key in obj:
                return True
            return any(_present(key, v) for v in obj.values())
        if isinstance(obj, list):
            return any(_present(key, v) for v in obj)
        return False

    counts = {k: sum(1 for r in reports if _present(k, r)) for k in writes}
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
            # `baseline_mtime` keeps its name for every existing reader, but since
            # 2026-09-29 it holds a RECORDED date, not a filesystem mtime.
            "baseline_mtime": newest,
            "age_source": ("override" if newest_override is not None
                           else "recorded_provenance" if newest else "UNKNOWN"),
            "reports_without_provenance": list(_NO_PROVENANCE),
            "age_conclusions_available": bool(newest) or newest_override is not None,
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
