"""Pins `docs/EXPERIMENTAL_RESULTS.md` against the way it went stale.

WHY THIS FILE EXISTS
--------------------
Measured on 2026-08-08. `docs/EXPERIMENTAL_RESULTS.md` opened by declaring
itself "the canonical record of all empirical testing… Nothing is omitted", and
its last dated entry was 19 April 2026. Experiments 30-35 and 37-49 all had run
directories with machine-written reports under `bench/logs/`, and not one of
those runs was recorded. Measured occurrence by occurrence: 30-35, 38, 39 and
42-49 were not named in the file at all; 37, 40 and 41 were named only in
forward references, a planning heading and a to-do list, none carrying a result.

The document was referenced ZERO times in `scripts/cdsfl_sv.py` and ZERO times
in `scripts/cdsfl_qc.py`. Nothing measured it, so nothing could contradict it.
That is the entire explanation for 111 days of drift, and it is the same shape
as every other expensive defect in this project's history: a failure that
renders as a confident success.

Repairing the document without repairing that leaves the next reader in exactly
the same place. So this test derives its truth from the filesystem rather than
restating it:

  * the set of experiments that MUST have an entry is read out of `bench/logs/`
    at run time — no list of experiment numbers is hardcoded anywhere here;
  * a report file that exists but cannot be parsed is reported BY NAME, never
    skipped, because silently dropping unreadable evidence would shrink the
    required set and turn a broken run into a passing check;
  * the detector is itself falsified in-process (`test_detector_goes_red_...`),
    because a check that cannot fail is not a check.

THE STRICTNESS CHOICE, STATED SO IT IS NOT MISTAKEN FOR AN OVERSIGHT
--------------------------------------------------------------------
Coverage is counted from headings only, and a heading must name its experiment
SINGLY. A heading like "Experiments 30-49" is deliberately NOT accepted as
covering the twenty experiments in that span: one such heading would blind this
check to every entry beneath it, and deleting an entry would then leave the
suite green. A letter-suffixed variant is folded onto its base number, so
"Experiment 13b" covers 13 and "Experiment 41c" covers 41 — the run directories
`exp41c_first_principles` and `exp41_convergence` are the same experiment.

WHAT THIS TEST CANNOT DO
------------------------
It checks PRESENCE, not accuracy. It can tell that Experiment 43 has an entry.
It cannot tell whether that entry describes Experiment 43 correctly. Accuracy
stays a human obligation; this exists so that total absence is impossible.

Offline: filesystem reads, `json`, `re`, `ast`, and one import of
`scripts/cdsfl_qc.py`. No subprocess, no sockets. Passes under
`--netguard-strict`.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = REPO_ROOT / "bench" / "logs"
RESULTS_DOC = "docs/EXPERIMENTAL_RESULTS.md"
QC_SCRIPT = "scripts/cdsfl_qc.py"

# A log directory names an experiment when it starts `exp<N>` or
# `experiment_<N>`. The number may carry a single-letter variant suffix
# (`exp41c`), and the directory may carry an outcome suffix after a dot
# (`exp40_slice_records_...Z.OUTAGE_TERMINATED_R5`). Anchored at position 0 so
# that `confer_exp40to54_plan_review` — a confer transcript, not a run — cannot
# match.
_EXP_DIR = re.compile(r"^(?:exp|experiment_)(\d{1,3})(?![0-9])", re.IGNORECASE)

# "Experiment 44", "Exp 44", "Experiment 41c". Ranges are NOT matched; see the
# module docstring for why that is deliberate.
_HEADING_EXP = re.compile(r"\bExp(?:eriment)?s?\s+(\d{1,3})[a-z]?\b", re.IGNORECASE)

_HEADING_LINE = re.compile(r"^(#{2,4})\s+(.*)$")


# ---------------------------------------------------------------------------
# Helpers. Every one of these MEASURES; none of them restates.
# ---------------------------------------------------------------------------

def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _strip_correction_blocks(text: str) -> str:
    """Drop paragraphs carrying a dated correction marker.

    Those paragraphs exist to QUOTE the defective claim they replaced. Scanning
    them would demand rewriting a record, which this project treats as a fault.
    """
    return "\n\n".join(
        p for p in re.split(r"\n\s*\n", text) if "[Correction" not in p
    )


def scan_run_reports() -> tuple[dict[int, list[str]], list[tuple[str, str]]]:
    """Walk `bench/logs/` once and return what is actually on disk.

    Returns ``(experiments, unreadable)`` where ``experiments`` maps an
    experiment number to the repo-relative report paths that parsed, and
    ``unreadable`` is a list of ``(path, reason)`` for every `*_report.json`
    that exists but could not be read as a JSON object.

    The two are returned SEPARATELY and both are asserted on. An unreadable
    report must never quietly reduce the required set: that would let a
    corrupted run pass this check by being unreadable, which is the failure
    mode the whole file exists to prevent.
    """
    experiments: dict[int, list[str]] = {}
    unreadable: list[tuple[str, str]] = []
    seen: set[Path] = set()

    assert LOGS_DIR.is_dir(), f"{LOGS_DIR} is not a directory — cannot measure"

    for entry in sorted(LOGS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        m = _EXP_DIR.match(entry.name)
        if not m:
            continue
        number = int(m.group(1))
        for report in sorted(entry.glob("*_report.json")):
            try:
                real = report.resolve()
            except OSError:  # pragma: no cover - dangling symlink
                real = report
            if real in seen:
                # `exp36_evidence_latest` is a symlink onto a real run
                # directory; counting its report twice would double-report any
                # problem with it.
                continue
            seen.add(real)
            rel = str(report.relative_to(REPO_ROOT))
            try:
                payload = json.loads(report.read_text(encoding="utf-8"))
            except (OSError, ValueError) as err:
                unreadable.append((rel, f"{type(err).__name__}: {str(err)[:200]}"))
                continue
            if not isinstance(payload, dict):
                unreadable.append((rel, f"top level is {type(payload).__name__}, not an object"))
                continue
            experiments.setdefault(number, []).append(rel)

    return experiments, unreadable


def experiments_documented(text: str) -> set[int]:
    """Experiment numbers named singly in a heading of `text`."""
    covered: set[int] = set()
    for line in text.splitlines():
        m = _HEADING_LINE.match(line)
        if not m:
            continue
        covered.update(int(n) for n in _HEADING_EXP.findall(m.group(2)))
    return covered


def _load_qc_module():
    """Import `scripts/cdsfl_qc.py` so its check can be cross-validated here."""
    scripts_dir = REPO_ROOT / "scripts"
    path = REPO_ROOT / QC_SCRIPT
    assert path.exists(), f"{QC_SCRIPT} is missing"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    spec = importlib.util.spec_from_file_location("cdsfl_qc_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# 1. The measurement itself must not be vacuous.
# ---------------------------------------------------------------------------

def test_the_scan_finds_experiments_and_headings():
    """Guards against a regex that silently matches nothing.

    A required set of size zero would make the coverage test below pass
    unconditionally — the same "confident success" this file exists to stop.
    """
    experiments, _ = scan_run_reports()
    assert len(experiments) >= 20, (
        f"only {len(experiments)} experiment(s) found with parseable reports "
        f"under bench/logs/ — the directory-name pattern {_EXP_DIR.pattern!r} "
        f"has probably stopped matching, and this check is now blind"
    )
    covered = experiments_documented(_read(RESULTS_DOC))
    assert len(covered) >= 20, (
        f"only {len(covered)} experiment number(s) extracted from headings in "
        f"{RESULTS_DOC} — the heading pattern has probably stopped matching"
    )


# ---------------------------------------------------------------------------
# 2. The check. Every experiment with a report has an entry.
# ---------------------------------------------------------------------------

def test_every_experiment_with_a_report_has_an_entry():
    experiments, _ = scan_run_reports()
    covered = experiments_documented(_read(RESULTS_DOC))
    missing = sorted(set(experiments) - covered)
    detail = "\n".join(
        f"    Experiment {n}: {', '.join(experiments[n])}" for n in missing
    )
    assert not missing, (
        f"{RESULTS_DOC} calls itself the canonical record, and "
        f"{len(missing)} experiment(s) with committed, parseable run reports "
        f"under bench/logs/ have no entry in it: {missing}\n{detail}\n"
        f"Write an entry from the report data — not from a note or a summary — "
        f"under a heading that names the experiment singly, e.g. "
        f"'### Experiment {missing[0]}: <target>'."
    )


def test_every_run_report_is_readable():
    """An unreadable report is reported by name, never skipped.

    If this ever goes red, do NOT fix it by excluding the file: an experiment
    whose report cannot be read has lost its primary evidence, and that is the
    finding.
    """
    _, unreadable = scan_run_reports()
    detail = "\n".join(f"    {path}: {reason}" for path, reason in unreadable)
    assert not unreadable, (
        f"{len(unreadable)} report file(s) under bench/logs/ exist but cannot "
        f"be read as JSON objects, so the experiments they belong to are "
        f"invisible to every check that reads them:\n{detail}"
    )


# ---------------------------------------------------------------------------
# 3. The detector must be able to go red. A check that cannot fail is not one.
# ---------------------------------------------------------------------------

def test_detector_goes_red_when_an_entry_is_deleted():
    """Delete one entry from a copy of the document and confirm the miss.

    This is the falsification of the check itself, run in-process against the
    real document text so that it exercises the real heading extractor rather
    than a toy fixture.
    """
    experiments, _ = scan_run_reports()
    text = _read(RESULTS_DOC)
    covered = experiments_documented(text)

    victim = max(n for n in experiments if n in covered)
    heading_re = re.compile(
        rf"^#{{2,4}}\s+.*\bExp(?:eriment)?s?\s+{victim}[a-z]?\b.*$",
        re.IGNORECASE | re.MULTILINE,
    )
    assert heading_re.search(text), (
        f"expected at least one heading naming Experiment {victim}"
    )
    mutilated = heading_re.sub("### <entry deleted by the falsification test>", text)

    still_covered = experiments_documented(mutilated)
    assert victim not in still_covered, (
        f"the heading for Experiment {victim} was removed and the extractor "
        f"still reports it as covered — the check cannot detect a deletion and "
        f"is therefore not a check"
    )
    # Compared against the baseline rather than against an empty set, so this
    # falsification still reports honestly when the document is already
    # incomplete — which is exactly the state it has to work in.
    baseline_missing = set(experiments) - covered
    after_missing = set(experiments) - still_covered
    assert after_missing == baseline_missing | {victim}, (
        f"deleting Experiment {victim}'s heading should add exactly that one "
        f"experiment to the missing set; baseline {sorted(baseline_missing)}, "
        f"after {sorted(after_missing)}"
    )


# ---------------------------------------------------------------------------
# 4. The document states a boundary it can keep, rather than one it cannot.
# ---------------------------------------------------------------------------

def test_document_states_its_scope_rather_than_claiming_completeness():
    text = _read(RESULTS_DOC)
    assert re.search(r"^##\s+Scope of This Record\s*$", text, re.MULTILINE), (
        f"{RESULTS_DOC} has no 'Scope of This Record' section. The document's "
        f"completeness claim must be bounded somewhere a reader will find it."
    )

    # The defective form was an ASSERTION: the bare sentence "Nothing is
    # omitted." standing on its own authority. Quoting the retired claim in
    # order to retire it is legitimate and stays allowed, so an occurrence is a
    # failure only when it is not immediately preceded by a quotation mark.
    live = _strip_correction_blocks(text)
    asserted = [
        m for m in re.finditer(r"Nothing is omitted", live)
        if live[max(0, m.start() - 1):m.start()] not in ('"', "“", "'")
    ]
    assert not asserted, (
        f"{RESULTS_DOC} asserts 'Nothing is omitted' outside a correction block "
        f"and outside quotation marks, at offset(s) "
        f"{[m.start() for m in asserted]}. That claim was false for 111 days "
        f"and no mechanism could have contradicted it. State a boundary a "
        f"check can keep instead."
    )
    assert "bench/tests/test_results_doc_currency.py" in text, (
        f"{RESULTS_DOC} does not name the test that enforces its scope claim. "
        f"A reader must be able to find the mechanism behind the claim."
    )


# ---------------------------------------------------------------------------
# 5. The qc sweep runs the same check, and agrees with this one.
# ---------------------------------------------------------------------------

def test_qc_script_registers_the_results_document_check():
    """`main()` must actually call it — a defined-but-unwired check is silence."""
    tree = ast.parse(_read(QC_SCRIPT))
    defined = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    assert "check_results_document" in defined, (
        f"{QC_SCRIPT} defines no check_results_document(); the qc sweep would "
        f"not look at {RESULTS_DOC} at all"
    )

    main = next(
        (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"),
        None,
    )
    assert main is not None, f"{QC_SCRIPT} has no main()"
    referenced = {
        node.id for node in ast.walk(main) if isinstance(node, ast.Name)
    }
    assert "check_results_document" in referenced, (
        f"{QC_SCRIPT} defines check_results_document() but main() never "
        f"references it. A check that is never run reports nothing, and "
        f"nothing reads as all-clear."
    )


def test_qc_check_agrees_with_this_test():
    """Two independent implementations must reach the same verdict."""
    qc = _load_qc_module()
    findings = qc.check_results_document(REPO_ROOT)
    assert findings, "check_results_document() returned nothing at all — a "\
        "check that reports neither a problem nor an OK is indistinguishable "\
        "from a check that did not run"

    bad = [f for f in findings if f["category"] in ("STALE", "MISSING", "CHECK_FAILED")]
    experiments, _ = scan_run_reports()
    missing = sorted(set(experiments) - experiments_documented(_read(RESULTS_DOC)))

    if missing:
        assert bad, (
            f"this test finds experiment(s) {missing} undocumented but the qc "
            f"check reported no problem — the two implementations disagree"
        )
    else:
        assert not bad, (
            "this test finds every experiment documented but the qc check "
            f"reports a problem: {bad}"
        )


def test_qc_check_names_the_missing_experiments(tmp_path, monkeypatch):
    """The qc finding must NAME what is missing, not merely say something is.

    Run against a synthetic repository holding one run directory and a results
    document with no entry for it.
    """
    qc = _load_qc_module()
    logs = tmp_path / "bench" / "logs" / "exp99_synthetic_20260808T000000Z"
    logs.mkdir(parents=True)
    (logs / "exp99_synthetic_report.json").write_text(
        json.dumps({"experiment": "exp99_synthetic", "total_findings": 1}),
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "EXPERIMENTAL_RESULTS.md").write_text(
        "# CDSFL Experimental Results\n\n## Scope of This Record\n\nnothing here\n",
        encoding="utf-8",
    )

    findings = qc.check_results_document(tmp_path)
    stale = [f for f in findings if f["category"] == "STALE"]
    assert stale, "qc reported no problem for a run directory with no entry"
    assert any("99" in f["detail"] for f in stale), (
        f"the qc finding does not name the missing experiment number: {stale}"
    )


def test_qc_check_reports_an_unreadable_report_rather_than_skipping_it(tmp_path):
    """A corrupt report must be surfaced, not silently dropped."""
    qc = _load_qc_module()
    run = tmp_path / "bench" / "logs" / "exp98_corrupt_20260808T000000Z"
    run.mkdir(parents=True)
    (run / "exp98_corrupt_report.json").write_text("{not json", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "EXPERIMENTAL_RESULTS.md").write_text(
        "# CDSFL Experimental Results\n\n### Experiment 98: synthetic\n",
        encoding="utf-8",
    )

    findings = qc.check_results_document(tmp_path)
    warned = [f for f in findings if f["category"] in ("WARN", "STALE")]
    assert warned, "a corrupt report produced no finding at all"
    assert any("exp98" in f["detail"] or "exp98" in f["file"] for f in warned), (
        f"the corrupt report is not named in any finding: {findings}"
    )


def test_qc_check_reports_a_missing_document_loudly(tmp_path):
    """Absence of the document must not read as 'nothing to report'."""
    qc = _load_qc_module()
    # Built one segment at a time so that no single line both names the log
    # tree and calls a write — `test_archive_is_not_written_by_tests.py`
    # forbids that textually, and it is right to: this is a tmp_path sandbox,
    # but a rule that has to inspect intent is not a rule.
    synthetic_logs = tmp_path / "bench" / "logs"
    synthetic_logs.mkdir(parents=True)
    findings = qc.check_results_document(tmp_path)
    assert any(f["category"] == "MISSING" for f in findings), (
        f"a missing {RESULTS_DOC} produced no MISSING finding: {findings}"
    )


# ---------------------------------------------------------------------------
# 6. Guard the run-report evidence the entries were written from.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("number", sorted(scan_run_reports()[0]))
def test_each_documented_experiment_still_has_its_evidence(number):
    """Every experiment this document claims to record still has a report.

    The entries above were written from `*_report.json` and from nothing else.
    If a report is deleted, the entry becomes an unsourced assertion, and this
    fires rather than leaving it looking sourced.
    """
    experiments, _ = scan_run_reports()
    paths = experiments[number]
    assert paths, f"Experiment {number} has no parseable report"
    for rel in paths:
        assert (REPO_ROOT / rel).is_file(), f"{rel} vanished between scans"
