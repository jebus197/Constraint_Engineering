#!/usr/bin/env python3
"""CDSFL Quality Control Script — staleness, consistency, and reference checks.

Usage: python3 scripts/cdsfl_qc.py

Report only — this script never edits documents.

Checks:
  1. Stale documentation (timestamps older than last commit)
  2. Broken file references in markdown
  3. Test count consistency between docs and actual (runs the offline suite
     once to obtain a real pass count — expect this to take a few minutes)
  4. Experiment number consistency between docs and logs
  5. Results-document currency: every experiment with a parseable run report
     under bench/logs/ has an entry in docs/EXPERIMENTAL_RESULTS.md
  6. Onboarding script wiring (cdsfl_onboard.py --dry-run passes)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import (
    AUDIT_KEY,
    check_file_references,
    git_state,
    latest_experiment,
    merge_reference_audit,
    repo_root,
    test_count,
    timestamp_iso,
)

# A canonical document whose "Last updated:" stamp trails the last commit by
# more than this is reported STALE. Seven days: these documents are refreshed
# at every `sv`, so a week of committed work with no doc update is a real lag,
# while a day or two of ordinary commits is not.
STALENESS_THRESHOLD_DAYS = 7

# Test-count claims are only read from the top of RECOVERY.md — the current
# state section — never from the dated historical entries below it.
RECOVERY_CURRENT_SECTION_LINES = 100

# The documented offline suite invocation. Run once per qc pass to obtain a
# real PASSED count; `test_count()` from cdsfl_utils returns COLLECTED, which
# is a different number and must never be compared against a pass count.
PYTEST_SUITE_ARGS = ["-m", "pytest", "bench/tests/", "-q", "--netguard-strict"]
PYTEST_SUITE_TIMEOUT_S = 1800


def parse_doc_timestamp(raw: str) -> datetime | None:
    """Parse '5 August 2026 14:08 BST' — the timestamp_now() convention.

    The timezone name is dropped: this stamp and the git commit date are both
    local time, so comparing naive local datetimes is correct here.
    """
    m = re.match(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})(?:\s+(\d{1,2}:\d{2}))?", raw.strip())
    if not m:
        return None
    text = f"{m.group(1)} {m.group(2) or '00:00'}"
    try:
        return datetime.strptime(text, "%d %B %Y %H:%M")
    except ValueError:
        return None


def parse_git_date(raw: str) -> datetime | None:
    """Parse git's %ci format: '2026-08-05 14:08:23 +0100'."""
    try:
        return datetime.strptime(str(raw)[:19], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def check_staleness(root: Path) -> list[dict]:
    """Check documentation timestamps against the last commit date.

    The two dates are actually compared: a document whose stamp trails the
    last commit by more than STALENESS_THRESHOLD_DAYS is STALE. A stamp that
    cannot be found or cannot be parsed is a WARN, never silence — a check
    that reports nothing must mean "nothing wrong", not "I could not look".
    """
    findings = []

    # Files that carry "Last updated:" timestamps
    timestamped_files = [
        root / "resources" / "ONBOARDING.md",
        root / "resources" / "RECOVERY.md",
    ]

    gs = git_state()
    last_commit = gs["last_date"]

    for f in timestamped_files:
        if not f.exists():
            findings.append({
                "category": "MISSING",
                "file": str(f.relative_to(root)),
                "detail": "File does not exist",
            })
            continue

        text = f.read_text(encoding="utf-8")
        m = re.search(r"Last updated:\s*(.+)", text)
        if not m:
            findings.append({
                "category": "WARN",
                "file": str(f.relative_to(root)),
                "detail": "No 'Last updated:' line found — staleness not checked",
            })
            continue

        doc_timestamp = m.group(1).strip()
        doc_dt = parse_doc_timestamp(doc_timestamp)
        commit_dt = parse_git_date(last_commit)
        if doc_dt is None or commit_dt is None:
            findings.append({
                "category": "WARN",
                "file": str(f.relative_to(root)),
                "detail": (
                    f"Could not parse dates — staleness not checked "
                    f"(doc {doc_timestamp!r}, last commit {last_commit!r})"
                ),
            })
            continue

        lag_days = (commit_dt - doc_dt).total_seconds() / 86400.0
        if lag_days > STALENESS_THRESHOLD_DAYS:
            findings.append({
                "category": "STALE",
                "file": str(f.relative_to(root)),
                "detail": (
                    f"Doc timestamp {doc_timestamp} trails last commit "
                    f"{last_commit} by {lag_days:.1f} days "
                    f"(threshold {STALENESS_THRESHOLD_DAYS} days)"
                ),
            })
        else:
            findings.append({
                "category": "OK",
                "file": str(f.relative_to(root)),
                "detail": (
                    f"Doc timestamp {doc_timestamp} is {lag_days:.1f} days "
                    f"behind last commit {last_commit} "
                    f"(threshold {STALENESS_THRESHOLD_DAYS} days)"
                ),
            })

    return findings


def _unique_ints(pattern: str, text: str) -> list[int]:
    """Return the distinct integers captured by `pattern`, in first-seen order."""
    out: list[int] = []
    for m in re.finditer(pattern, text):
        value = int(m.group(1))
        if value not in out:
            out.append(value)
    return out


def measure_suite(root: Path) -> dict | None:
    """Run the offline suite once and return its real pass/skip/fail counts.

    Returns None only if no summary could be obtained at all. A suite that
    RAN and failed still returns counts — a red suite is a finding, not a
    missing measurement.
    """
    try:
        result = subprocess.run(
            [sys.executable, *PYTEST_SUITE_ARGS],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=PYTEST_SUITE_TIMEOUT_S,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None

    tail = "\n".join(result.stdout.splitlines()[-20:])
    counts: dict[str, int] = {}
    for key in ("passed", "skipped", "failed", "error"):
        found = re.findall(rf"(\d+)\s+{key}s?\b", tail)
        counts[key] = int(found[-1]) if found else 0
    if not any(counts.values()):
        return None
    return counts


def check_test_consistency(root: Path) -> list[dict]:
    """Compare test counts claimed in RECOVERY.md against measured reality.

    Two DIFFERENT numbers appear in that document and must never be compared
    against each other: COLLECTED (how many tests exist) and PASSED (how many
    of them passed). `test_count()` measures collected; `measure_suite()`
    measures passed. Each is compared only against its own kind.

    If no test-count claim can be found at all, that is a WARN — the previous
    regex matched a phrasing the document no longer uses, so the check
    returned an empty list and the silence read as "all clear".
    """
    findings = []

    actual_collected = test_count()
    if actual_collected is None:
        findings.append({
            "category": "WARN",
            "file": "bench/tests/",
            "detail": "Could not collect test count (pytest collection failed)",
        })

    measured = measure_suite(root)
    if measured is None:
        findings.append({
            "category": "WARN",
            "file": "bench/tests/",
            "detail": (
                "Could not measure pass count — "
                f"`{sys.executable} {' '.join(PYTEST_SUITE_ARGS)}` produced "
                "no summary line"
            ),
        })
    elif measured["failed"] or measured["error"]:
        findings.append({
            "category": "WARN",
            "file": "bench/tests/",
            "detail": (
                f"Suite is RED: {measured['passed']} passed, "
                f"{measured['failed']} failed, {measured['error']} error(s), "
                f"{measured['skipped']} skipped"
            ),
        })
    else:
        # A GREEN SUITE MUST SAY SO (2026-08-12). Previously this branch did not
        # exist: a red suite warned and a green one reported NOTHING, so the
        # output could not distinguish "the suite passed" from "the suite was
        # never measured". That is the failure this script's own staleness check
        # warns about in its docstring — a check that reports nothing must mean
        # "nothing wrong", not "I could not look" — and it is the same shape as a
        # tamper detector that cannot report tampering.
        #
        # It also supplies the number RECOVERY.md deliberately no longer carries.
        # That document retired its bare pass-counts because stale ones misled;
        # the right replacement is a count MEASURED on every run rather than one
        # transcribed into prose and left to rot.
        findings.append({
            "category": "OK",
            "file": "bench/tests/",
            "detail": (
                f"Suite is GREEN, measured this run: {measured['passed']} passed, "
                f"{measured['skipped']} skipped, 0 failed "
                f"(python3 -m pytest bench/tests/ -q --netguard-strict)"
            ),
        })

    recovery = root / "resources" / "RECOVERY.md"
    if not recovery.exists():
        findings.append({
            "category": "MISSING",
            "file": "resources/RECOVERY.md",
            "detail": "File does not exist — test-count claims not checked",
        })
        return findings

    lines = recovery.read_text(encoding="utf-8").splitlines()
    # Scan only the current state section, not the dated historical entries.
    current_section = "\n".join(lines[:RECOVERY_CURRENT_SECTION_LINES])

    # Phrasings actually used: "2099 passed", "2102 collected", and the older
    # "N tests pass" / "N tests collected".
    doc_passed = _unique_ints(r"(\d+)\s+(?:tests?\s+)?pass(?:ed)?\b", current_section)
    doc_collected = _unique_ints(r"(\d+)\s+(?:tests?\s+)?collected\b", current_section)

    # A DELIBERATE ABSENCE IS NOT A BLIND CHECK (2026-08-12).
    #
    # This warned that it could find no test-count claim and was therefore blind.
    # It was half right. The document deliberately carries NO bare pass-count in
    # its current-state section: it retracts the earlier ones ("Every pass-count
    # in the dated session entries below...") and sets a policy in their place —
    # "Any future 'N tests pass' claim must carry a date, a commit, and the
    # command". Bare counts were the defect the document is guarding against, so
    # demanding one would push it back into the failure it corrected.
    #
    # The distinction that matters is between a document that lost its claim and
    # one that retired it on purpose. Only the first is a blind check. Satisfying
    # this by inserting a number would also have violated the document's own rule,
    # since an uncommitted tree has no commit to cite.
    _POLICY_RE = re.compile(
        r"must carry a date, a commit, and the command"
        r"|Every pass-count in the dated session entries",
        re.IGNORECASE)
    if not doc_passed and not doc_collected and _POLICY_RE.search(current_section):
        findings.append({
            "category": "OK",
            "file": "resources/RECOVERY.md",
            "detail": (
                "No bare test-count claim in the current-state section, and the "
                "document states the policy that replaced it — deliberate, not "
                "drift. A claim here must carry a date, a commit and the command."
            ),
        })
    elif not doc_passed and not doc_collected:
        findings.append({
            "category": "WARN",
            "file": "resources/RECOVERY.md",
            "detail": (
                f"No test-count claim AND no statement of the policy that "
                f"replaced it, in the first {RECOVERY_CURRENT_SECTION_LINES} "
                f"lines — the phrasing may have changed and this check is now blind"
            ),
        })
        return findings

    for doc_count in doc_collected:
        if actual_collected is None:
            continue
        findings.append({
            "category": "OK" if doc_count == actual_collected else "STALE",
            "file": "resources/RECOVERY.md",
            "detail": (
                f"Current section says {doc_count} collected, "
                f"actual collected is {actual_collected}"
            ),
        })

    for doc_count in doc_passed:
        if measured is None:
            continue
        findings.append({
            "category": "OK" if doc_count == measured["passed"] else "STALE",
            "file": "resources/RECOVERY.md",
            "detail": (
                f"Current section says {doc_count} passed, "
                f"actual passed is {measured['passed']}"
            ),
        })

    return findings


def check_experiment_consistency(root: Path) -> list[dict]:
    """Check latest experiment number in docs against logs."""
    findings = []

    exp = latest_experiment()
    if exp is None:
        return findings

    actual_num = exp["number"]

    # Check ONBOARDING.md for experiment mentions
    onboarding = root / "resources" / "ONBOARDING.md"
    if onboarding.exists():
        text = onboarding.read_text(encoding="utf-8")
        # Find highest experiment number mentioned. CASE-INSENSITIVE: the
        # document writes "Exp 48" … "Exp 54" about thirty times and "EXP 42"
        # once, so an uppercase-only match saw 42 as the ceiling and reported
        # ONBOARDING.md stale against a live experiment number it already
        # names. That finding was a false positive produced by the regex, not
        # by the document.
        exp_nums = [
            int(m.group(1)) for m in re.finditer(r"EXP\s+(\d+)", text, re.IGNORECASE)
        ]
        if exp_nums:
            max_mentioned = max(exp_nums)
            if max_mentioned < actual_num:
                findings.append({
                    "category": "STALE",
                    "file": "resources/ONBOARDING.md",
                    "detail": f"Highest experiment mentioned: {max_mentioned}, actual: {actual_num}",
                })

    return findings


# ---------------------------------------------------------------------------
# Results-document currency.
#
# WHY THIS CHECK EXISTS. docs/EXPERIMENTAL_RESULTS.md declared itself "the
# canonical record of all empirical testing… Nothing is omitted" while its last
# entry was 19 April 2026 and Experiments 41-49 appeared in it zero times. It
# was referenced nowhere in cdsfl_sv.py and nowhere in this script, so nothing
# measured the claim and nothing could contradict it. That is the whole
# explanation for the drift.
#
# The check derives the required set from the filesystem. It hardcodes no
# experiment numbers, so a new run directory is sufficient to make it demand an
# entry — and an entry cannot be satisfied by a heading naming a RANGE, because
# one such heading would blind the check to every entry beneath it.
# ---------------------------------------------------------------------------

RESULTS_DOC_REL = "docs/EXPERIMENTAL_RESULTS.md"

# `exp44_...`, `exp41c_...`, `experiment_13b`. Anchored at position 0 so that
# `confer_exp40to54_plan_review` — a transcript, not a run — cannot match.
_EXP_DIR_RE = re.compile(r"^(?:exp|experiment_)(\d{1,3})(?![0-9])", re.IGNORECASE)

# "Experiment 44", "Exp 44", "Experiment 41c". Ranges are deliberately NOT
# matched; see the note above.
_HEADING_EXP_RE = re.compile(r"\bExp(?:eriment)?s?\s+(\d{1,3})[a-z]?\b", re.IGNORECASE)

_HEADING_LINE_RE = re.compile(r"^(#{2,4})\s+(.*)$")


def scan_run_reports(root: Path) -> tuple[dict[int, list[str]], list[tuple[str, str]]]:
    """Walk bench/logs/ and return what is actually on disk.

    Returns ``(experiments, unreadable)``: a map from experiment number to the
    repo-relative report paths that parsed, and a list of
    ``(path, reason)`` for every ``*_report.json`` that exists but could not be
    read as a JSON object.

    Unreadable reports are returned SEPARATELY rather than skipped. Dropping
    them would shrink the required set, so a corrupted run would pass this
    check by virtue of being corrupt.
    """
    experiments: dict[int, list[str]] = {}
    unreadable: list[tuple[str, str]] = []
    seen: set[Path] = set()

    logs_dir = root / "bench" / "logs"
    if not logs_dir.is_dir():
        return experiments, unreadable

    for entry in sorted(logs_dir.iterdir()):
        if not entry.is_dir():
            continue
        m = _EXP_DIR_RE.match(entry.name)
        if not m:
            continue
        number = int(m.group(1))
        for report in sorted(entry.glob("*_report.json")):
            try:
                real = report.resolve()
            except OSError:
                real = report
            if real in seen:
                # A "…_latest" symlink points at a real run directory; counting
                # its report twice would double-report any problem with it.
                continue
            seen.add(real)
            rel = str(report.relative_to(root))
            try:
                payload = json.loads(report.read_text(encoding="utf-8"))
            except (OSError, ValueError) as err:
                unreadable.append((rel, f"{type(err).__name__}: {str(err)[:200]}"))
                continue
            if not isinstance(payload, dict):
                unreadable.append(
                    (rel, f"top level is {type(payload).__name__}, not an object")
                )
                continue
            experiments.setdefault(number, []).append(rel)

    return experiments, unreadable


def experiments_documented(text: str) -> set[int]:
    """Experiment numbers named singly in a heading of `text`."""
    covered: set[int] = set()
    for line in text.splitlines():
        m = _HEADING_LINE_RE.match(line)
        if not m:
            continue
        covered.update(int(n) for n in _HEADING_EXP_RE.findall(m.group(2)))
    return covered


def check_results_document(root: Path) -> list[dict]:
    """Every experiment with a parseable run report must have an entry.

    Always returns at least one finding. A check that reports neither a problem
    nor an OK is indistinguishable from a check that never ran, and this repo
    has already lost 105 days to exactly that.
    """
    findings: list[dict] = []

    doc = root / RESULTS_DOC_REL
    logs_dir = root / "bench" / "logs"

    if not logs_dir.is_dir():
        findings.append({
            "category": "WARN",
            "file": "bench/logs/",
            "detail": (
                "log directory does not exist — results-document currency "
                "NOT checked (this is a blind check, not a clean bill)"
            ),
        })
        return findings

    experiments, unreadable = scan_run_reports(root)

    for path, reason in unreadable:
        findings.append({
            "category": "WARN",
            "file": path,
            "detail": (
                f"run report exists but could not be read as a JSON object "
                f"({reason}) — the experiment it belongs to is invisible to "
                f"every check that reads reports"
            ),
        })

    if not doc.exists():
        findings.append({
            "category": "MISSING",
            "file": RESULTS_DOC_REL,
            "detail": (
                "the canonical experimental record does not exist; "
                f"{len(experiments)} experiment(s) have run reports with "
                "nowhere to be recorded"
            ),
        })
        return findings

    if not experiments:
        findings.append({
            "category": "WARN",
            "file": "bench/logs/",
            "detail": (
                f"no experiment directory matched {_EXP_DIR_RE.pattern!r} with "
                f"a parseable report — the naming convention has probably "
                f"changed and this check is now blind"
            ),
        })
        return findings

    covered = experiments_documented(doc.read_text(encoding="utf-8"))
    missing = sorted(set(experiments) - covered)

    if missing:
        for number in missing:
            findings.append({
                "category": "STALE",
                "file": RESULTS_DOC_REL,
                "detail": (
                    f"Experiment {number} has {len(experiments[number])} "
                    f"parseable run report(s) under bench/logs/ "
                    f"({', '.join(experiments[number])}) and NO entry in the "
                    f"canonical record. Write one from the report data, under "
                    f"a heading naming the experiment singly."
                ),
            })
        findings.append({
            "category": "STALE",
            "file": RESULTS_DOC_REL,
            "detail": (
                f"{len(missing)} of {len(experiments)} experiment(s) with run "
                f"reports are undocumented: {missing}"
            ),
        })
    else:
        findings.append({
            "category": "OK",
            "file": RESULTS_DOC_REL,
            "detail": (
                f"all {len(experiments)} experiment(s) with parseable run "
                f"reports under bench/logs/ have an entry "
                f"(numbers: {sorted(experiments)})"
            ),
        })

    return findings


def check_broken_references(root: Path, audit: dict | None = None) -> list[dict]:
    """Check all markdown files for broken file references.

    Pass a dict as `audit` to receive the reference filter's per-rule
    suppression tally, which `main()` prints. That tally is not decoration:
    a report of 183 findings of which ~10 are real buries the real ones
    exactly as effectively as the 105-day crash this check replaced, so the
    filtering that got it down to a readable number must itself be visible
    and falsifiable. An over-broad rule added later shows up as a rule with
    an implausible count, rather than as findings that quietly vanish.
    """
    findings = []

    doc_dirs = [
        root / "resources",
        root / "docs",
        root / "experimental_notes",
    ]

    for doc_dir in doc_dirs:
        if not doc_dir.exists():
            continue
        for md in doc_dir.glob("*.md"):
            # The OSError (errno 63, name too long) that used to abort this
            # scan is fixed at source by the length guard in
            # check_file_references. This catch stays as a backstop, and a
            # document it swallows is reported by name — never as silence.
            try:
                broken = check_file_references(md)
            except Exception as err:  # noqa: BLE001
                findings.append({
                    "category": "CHECK_FAILED",
                    "file": str(md.relative_to(root)),
                    "detail": (
                        f"reference scan aborted, document NOT scanned: "
                        f"{type(err).__name__}: {str(err)[:300]}"
                    ),
                })
                continue
            if audit is not None:
                merge_reference_audit(broken, audit)
            for ref in broken:
                if AUDIT_KEY in ref:
                    continue
                rel = str(Path(ref["file"]).relative_to(root))
                if ref.get("scan_failed"):
                    findings.append({
                        "category": "WARN",
                        "file": rel,
                        "detail": (
                            f"reference scan SKIPPED, document NOT scanned: "
                            f"{ref['scan_failed']}"
                        ),
                    })
                    continue
                findings.append({
                    "category": "BROKEN_REF",
                    "file": rel,
                    "detail": f"Line {ref['line']}: {ref['reference']}",
                })

    return findings


def print_reference_audit(audit: dict, reported: int) -> None:
    """Print the reference filter's suppression tally, rule by rule.

    The arithmetic is printed and CHECKED. `candidates` must equal
    `resolved + suppressed + reported`; if it does not, candidates have been
    lost somewhere between the scanner and the report, and that is said in
    capitals rather than absorbed into a tidy-looking number. A filter whose
    books do not balance is exactly the failure this whole check exists to
    make impossible.
    """
    candidates = audit.get("candidates", 0)
    suppressed = audit.get("suppressed", {})
    resolved = audit.get("resolved", 0)
    filtered = sum(suppressed.values())
    print("REFERENCE FILTER (suppression is reported so it can be falsified)\n")
    print(f"  {candidates} candidates examined, {filtered} suppressed, "
          f"{reported} reported broken")
    print(f"  {resolved} resolved directly (no rule needed); the rules below "
          f"whose text says the file EXISTS are resolutions too, counted once "
          f"each under their own name")
    accounted = resolved + filtered + reported
    if accounted != candidates:
        print(f"  ARITHMETIC MISMATCH: {resolved} resolved + {filtered} "
              f"suppressed + {reported} reported = {accounted}, but "
              f"{candidates} candidates were examined. "
              f"{abs(candidates - accounted)} candidate(s) are unaccounted "
              f"for — this tally is WRONG, not merely incomplete.")
    if not suppressed:
        print("  (no candidate was suppressed by any rule)")
    for rule, count in sorted(suppressed.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {count:6d}  {rule}")
    print()


def check_glossary(root: Path) -> list[dict]:
    """Check if glossary exists and has content."""
    findings = []
    glossary = root / "docs" / "GLOSSARY.md"

    if not glossary.exists():
        findings.append({
            "category": "MISSING",
            "file": "docs/GLOSSARY.md",
            "detail": "Glossary does not exist — term cross-referencing disabled",
        })
    else:
        text = glossary.read_text(encoding="utf-8")
        term_count = len(re.findall(r"^###\s+", text, re.MULTILINE))
        findings.append({
            "category": "INFO",
            "file": "docs/GLOSSARY.md",
            "detail": f"{term_count} terms defined",
        })

    return findings


def check_log_seals(root: Path) -> list[dict]:
    """Verify every sealed_chain.json under logs/confer and logs/chat.

    Runs `scripts/cdsfl_seal_logs.py --verify` as a subprocess. If any
    seal is missing or its Merkle chain fails verification, a STALE
    finding is returned naming the affected directory.
    """
    findings: list[dict] = []
    script = root / "scripts" / "cdsfl_seal_logs.py"
    logs_root = root / "logs"

    if not script.exists():
        findings.append({
            "category": "MISSING",
            "file": "scripts/cdsfl_seal_logs.py",
            "detail": "Log sealing script not found",
        })
        return findings

    if not logs_root.exists():
        return findings

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--verify"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        findings.append({
            "category": "WARN",
            "file": "logs/",
            "detail": "Seal verification timed out after 60s",
        })
        return findings
    except OSError as err:
        findings.append({
            "category": "WARN",
            "file": "logs/",
            "detail": f"Could not run seal verification: {err}",
        })
        return findings

    if result.returncode == 0:
        findings.append({
            "category": "OK",
            "file": "logs/",
            "detail": "All log seals verify (Merkle chains intact)",
        })
    else:
        # Surface TAMPERED / UNSEALED lines from the verifier.
        bad_lines = [
            ln.strip() for ln in (result.stdout + "\n" + result.stderr).splitlines()
            if "TAMPERED" in ln or "UNSEALED" in ln or "ERROR" in ln
        ]
        detail = "; ".join(bad_lines) if bad_lines else "seal verification failed"
        findings.append({
            "category": "STALE",
            "file": "logs/",
            "detail": detail,
        })

    return findings


def check_onboard_script(root: Path) -> list[dict]:
    """Run `cdsfl_onboard.py --dry-run` to verify the onboarding script's
    canonical-document wiring is intact.

    The onboarding script reads project prose from resources/ONBOARDING.md
    and the MC command reference from docs/REPRODUCING.md at runtime. If
    either file is missing a required section or marker, the dry-run
    fails and is surfaced here so staleness is caught before commit.
    """
    findings: list[dict] = []
    script = root / "scripts" / "cdsfl_onboard.py"

    if not script.exists():
        findings.append({
            "category": "MISSING",
            "file": "scripts/cdsfl_onboard.py",
            "detail": "Onboarding script not found",
        })
        return findings

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        findings.append({
            "category": "WARN",
            "file": "scripts/cdsfl_onboard.py",
            "detail": "--dry-run timed out after 30s",
        })
        return findings
    except OSError as err:
        findings.append({
            "category": "WARN",
            "file": "scripts/cdsfl_onboard.py",
            "detail": f"Could not run --dry-run: {err}",
        })
        return findings

    if result.returncode == 0:
        findings.append({
            "category": "OK",
            "file": "scripts/cdsfl_onboard.py",
            "detail": "--dry-run passes (canonical-doc wiring intact)",
        })
    else:
        # Surface the specific failures from stderr as STALE findings.
        stderr_lines = [ln for ln in result.stderr.splitlines() if ln.strip()]
        detail = "; ".join(stderr_lines) if stderr_lines else "--dry-run failed (no stderr)"
        findings.append({
            "category": "STALE",
            "file": "scripts/cdsfl_onboard.py",
            "detail": detail,
        })

    return findings


def run_check(name: str, fn, root: Path) -> list[dict]:
    """Run one check. A crash inside it becomes a loud CHECK_FAILED finding
    instead of killing the whole report.

    This script produced no output at all between 2026-04-22 and 2026-08-05
    because an unhandled OSError in one check aborted the process before the
    findings were printed. A single broken check must never take down the
    report, and it must never be silent about having broken either.
    """
    try:
        return fn(root)
    except Exception as err:  # noqa: BLE001
        return [{
            "category": "CHECK_FAILED",
            "file": f"check: {name}",
            "detail": f"{type(err).__name__}: {str(err)[:300]}",
        }]


def main() -> int:
    """Run every check and print the report. Returns the process exit code.

    EXIT CODE CONTRACT: non-zero when one or more checks CRASHED. A run in
    which two of seven checks blew up is not a successful run, and a wrapper
    that reads only the status must not be told it was. Findings themselves
    (stale docs, broken refs) still exit 0 — this script reports, it does not
    gate. Nothing in the repo, in ~/.claude, in CI, in a Makefile or in a git
    hook consumes this status today; the only references are prose
    instructions to run it and fix what it prints.
    """
    parser = argparse.ArgumentParser(description="CDSFL Quality Control")
    parser.parse_args()

    root = repo_root()
    print(f"CDSFL Quality Control — {timestamp_iso()}")
    print(f"Repository: {root}")
    print("=" * 70)

    all_findings: list[dict] = []

    print("\nChecking timestamps...", flush=True)
    all_findings.extend(run_check("timestamps", check_staleness, root))

    print("Checking test consistency...", flush=True)
    all_findings.extend(run_check("test consistency", check_test_consistency, root))

    print("Checking experiment consistency...", flush=True)
    all_findings.extend(
        run_check("experiment consistency", check_experiment_consistency, root))

    print("Checking results-document currency...", flush=True)
    all_findings.extend(
        run_check("results document", check_results_document, root))

    print("Checking file references...", flush=True)
    ref_audit: dict = {}
    all_findings.extend(run_check(
        "file references", lambda r: check_broken_references(r, audit=ref_audit), root))

    print("Checking glossary...", flush=True)
    all_findings.extend(run_check("glossary", check_glossary, root))

    print("Checking onboarding script wiring...", flush=True)
    all_findings.extend(run_check("onboarding script", check_onboard_script, root))

    print("Checking log seals...", flush=True)
    all_findings.extend(run_check("log seals", check_log_seals, root))

    # Report
    print("\n" + "=" * 70)
    print("FINDINGS\n")

    categories = [
        "CHECK_FAILED", "STALE", "BROKEN_REF", "MISSING", "WARN", "INFO", "OK",
    ]
    for cat in categories:
        items = [f for f in all_findings if f["category"] == cat]
        if items:
            print(f"[{cat}]")
            for item in items:
                print(f"  {item['file']}: {item['detail']}")
            print()

    # Summary
    failed = len([f for f in all_findings if f["category"] == "CHECK_FAILED"])
    print_reference_audit(
        ref_audit,
        len([f for f in all_findings if f["category"] == "BROKEN_REF"]),
    )
    stale = len([f for f in all_findings if f["category"] == "STALE"])
    broken = len([f for f in all_findings if f["category"] == "BROKEN_REF"])
    missing = len([f for f in all_findings if f["category"] == "MISSING"])
    warns = len([f for f in all_findings if f["category"] == "WARN"])

    issues = failed + stale + broken + missing + warns
    print(f"Total: {len(all_findings)} checks, {issues} issues "
          f"({failed} checks crashed, {stale} stale, {broken} broken refs, "
          f"{missing} missing, {warns} warnings)")

    if failed:
        print(f"EXIT 1: {failed} check(s) crashed — this run is INCOMPLETE and "
              f"its findings are partial.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
