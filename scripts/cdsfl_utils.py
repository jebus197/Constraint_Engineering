"""Shared utilities for CDSFL automation scripts."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def repo_root() -> Path:
    """Return the repository root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def timestamp_now() -> str:
    """Return formatted timestamp in project convention."""
    now = datetime.now()
    day = now.day
    month = now.strftime("%B")
    year = now.year
    time_str = now.strftime("%H:%M")
    tz = now.astimezone().strftime("%Z")
    return f"{day} {month} {year} {time_str} {tz}"


def timestamp_iso() -> str:
    """Return ISO 8601 timestamp."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _run_git_rc(*args: str, cwd: Optional[Path] = None) -> tuple[int, str]:
    """Run a git command and return (returncode, stdout).

    Callers that act on the OUTPUT must use this, not ``_run_git``: a git
    command that failed writes nothing to stdout, and an empty stdout parsed
    as a number is a zero — which is how a failed `rev-list` used to render
    as "up to date".
    """
    result = subprocess.run(
        ["git", *args],
        cwd=cwd or repo_root(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout.strip()


def _run_git(*args: str, cwd: Optional[Path] = None) -> str:
    """Run a git command and return stdout."""
    return _run_git_rc(*args, cwd=cwd)[1]


def git_state() -> dict[str, Any]:
    """Collect current git state."""
    root = repo_root()

    branch = _run_git("branch", "--show-current", cwd=root)
    status_raw = _run_git("status", "--porcelain", cwd=root)
    uncommitted = [line.strip() for line in status_raw.splitlines() if line.strip()]
    is_clean = len(uncommitted) == 0

    last_log = _run_git("log", "--oneline", "-1", cwd=root)
    last_hash = last_log.split()[0] if last_log else "unknown"
    last_msg = " ".join(last_log.split()[1:]) if last_log else "unknown"
    last_date = _run_git("log", "-1", "--format=%ci", cwd=root)

    recent_log = _run_git("log", "--oneline", "-10", cwd=root).splitlines()

    # Remote sync. Compare against THIS branch's own upstream, not a hardcoded
    # origin/main: all work happens on exp39-experimental, and comparing it to
    # main reported "diverged (ahead 98, behind 1)" for a branch that is level
    # with its upstream. The ref actually compared is always named in the
    # output so the reader knows what the numbers mean.
    _run_git("fetch", "--quiet", cwd=root)
    up_rc, upstream = _run_git_rc(
        "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", cwd=root
    )
    if up_rc == 0 and upstream:
        ref = upstream
        ref_note = ""
    else:
        ref = "origin/main"
        ref_note = " [no upstream configured]"

    # --left-right --count <ref>...HEAD prints "<behind>\t<ahead>".
    rl_rc, counts = _run_git_rc(
        "rev-list", "--left-right", "--count", f"{ref}...HEAD", cwd=root
    )
    parts = counts.split()
    if rl_rc != 0 or len(parts) != 2 or not all(p.isdigit() for p in parts):
        # A failed rev-list is NOT zero commits of drift. Say so.
        remote_sync = f"unknown (rev-list vs {ref} failed){ref_note}"
    else:
        behind_n, ahead_n = int(parts[0]), int(parts[1])
        if ahead_n == 0 and behind_n == 0:
            remote_sync = f"up to date with {ref}{ref_note}"
        elif ahead_n > 0 and behind_n > 0:
            remote_sync = (
                f"diverged from {ref} (ahead {ahead_n}, behind {behind_n}){ref_note}"
            )
        elif ahead_n > 0:
            remote_sync = f"ahead of {ref} by {ahead_n}{ref_note}"
        else:
            remote_sync = f"behind {ref} by {behind_n}{ref_note}"

    return {
        "branch": branch,
        "clean": is_clean,
        "uncommitted": uncommitted,
        "last_hash": last_hash,
        "last_message": last_msg,
        "last_date": last_date,
        "recent_log": recent_log,
        "remote_sync": remote_sync,
    }


def test_count() -> Optional[int]:
    """Count tests via pytest collection. Returns None on failure."""
    root = repo_root()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "bench/tests/", "--co", "-q"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Last meaningful line is "N tests collected"
        for line in reversed(result.stdout.splitlines()):
            m = re.search(r"(\d+)\s+tests?\s+collected", line)
            if m:
                return int(m.group(1))
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def latest_experiment() -> Optional[dict[str, Any]]:
    """Find and parse the latest experiment from bench/logs/."""
    logs_dir = repo_root() / "bench" / "logs"
    if not logs_dir.exists():
        return None

    # Find exp{N}_* directories
    exp_dirs: list[tuple[int, Path]] = []
    for d in logs_dir.iterdir():
        if d.is_dir():
            # Capture the leading experiment number; allow a letter/variant
            # suffix (e.g. exp41c_first_principles) before the underscore, so
            # suffixed re-runs are not silently excluded from "latest".
            m = re.match(r"exp(\d+)", d.name)
            if m:
                exp_dirs.append((int(m.group(1)), d))

    if not exp_dirs:
        return None

    # Walk distinct experiment numbers from HIGHEST to LOWEST and return the
    # first that yields a parseable report, preserving the existing mtime
    # ordering within each number. The previous version filtered to the single
    # highest number and fell through to `return None` when that experiment had
    # written no report — which is exactly what exp53, the deliberately halted
    # zero-plant control, looks like. With ~60 log directories and 37 reports
    # on disk, both `rs` and `sv` printed "(No experiment logs found)".
    skipped_higher: list[int] = []

    for max_n in sorted({n for n, _ in exp_dirs}, reverse=True):
        candidates = sorted(
            [d for n, d in exp_dirs if n == max_n],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for exp_dir in candidates:
            # Look for report JSON
            report_files = list(exp_dir.glob("exp*_report.json"))
            if not report_files:
                continue
            try:
                data = json.loads(report_files[0].read_text())

                # completion_signal: may be embedded in report or a separate file
                comp = data.get("completion_signal")
                if comp is None:
                    cs_path = exp_dir / "completion_signal.json"
                    if cs_path.exists():
                        try:
                            comp = json.loads(cs_path.read_text())
                        except (json.JSONDecodeError, OSError):
                            comp = {}
                    else:
                        comp = {}

                # Status derivation
                status = comp.get("status", "UNKNOWN")
                if status == "INCOMPLETE" and data.get("converged_at") is not None:
                    status = "CONVERGED"
                elif status == "INCOMPLETE":
                    # Check for wall clock cap or budget exhaustion
                    elapsed = data.get("total_elapsed_s", 0)
                    max_rounds = data.get("max_rounds", 0)
                    total_rounds = data.get("total_rounds", 0)
                    # Wall clock cap: elapsed exceeds 95% of 8h default or
                    # total_rounds exceeded max_rounds
                    if elapsed > 0 and total_rounds > max_rounds:
                        status = "WALL_CLOCK_CAP"

                reason = comp.get("reason", "") or data.get("convergence_reason", "")

                # Gamma: top-level or last entry in gamma_history
                gamma = data.get("gamma")
                if gamma is None:
                    gh = data.get("gamma_history", [])
                    gamma = gh[-1] if gh else 0.0

                # Canonical count: len(registry.entries) or fallback
                reg = data.get("registry", {})
                if isinstance(reg, dict) and "entries" in reg:
                    canonical_count = len(reg["entries"])
                else:
                    canonical_count = data.get("total_findings", 0)

                # Per-model findings: from completion_signal, or per_model_totals
                per_model = comp.get("per_model_findings", {})
                if not per_model:
                    per_model = data.get("per_model_totals", {})

                return {
                    "number": max_n,
                    "name": data.get("experiment", f"exp{max_n}"),
                    "status": status,
                    "reason": reason,
                    "total_rounds": data.get("total_rounds", 0),
                    "total_findings": data.get("total_findings", 0),
                    "canonical_count": canonical_count,
                    "gamma": gamma,
                    "models": data.get("models", []),
                    "target": data.get("target_file", ""),
                    "topology": data.get("topology", ""),
                    "timestamp": comp.get("timestamp", ""),
                    "per_model": per_model,
                    "log_dir": str(exp_dir),
                    # Higher-numbered experiments passed over for lack of a
                    # parseable report, highest first. A caller that prints
                    # this can say "exp53 wrote no report" instead of
                    # implying exp53 does not exist.
                    "skipped_higher": list(skipped_higher),
                }
            except (json.JSONDecodeError, OSError):
                continue

        # No parseable report at this number — say so, then keep descending.
        skipped_higher.append(max_n)
        print(
            f"cdsfl_utils.latest_experiment: exp{max_n} has no parseable "
            f"report in {len(candidates)} log dir(s) - skipping to the next "
            f"lower experiment number.",
            file=sys.stderr,
        )

    return None


class SectionText(str):
    """A ``read_section`` result that also carries WHY it is empty.

    Subclasses ``str``, so every existing caller — truthiness tests,
    ``.splitlines()``, ``.find()``, slicing, printing — behaves exactly as
    before. ``status`` is one of "ok", "unreadable" or "marker-missing", which
    is what distinguishes an empty section from a dead marker. Those two were
    indistinguishable to every caller, and that is how a dead marker in
    resources/RECOVERY.md went unnoticed for 113 days.
    """

    status: str
    detail: str

    def __new__(cls, value: str, status: str = "ok", detail: str = "") -> "SectionText":
        obj = super().__new__(cls, value)
        obj.status = status
        obj.detail = detail
        return obj


def read_section(filepath: Path, start_marker: str, end_marker: str = "") -> SectionText:
    """Extract text between markdown section markers.

    start_marker: text to search for (e.g. '## Current State')
    end_marker: text marking end of section (e.g. next '## ').
                If empty, reads to end of file.

    Returns a SectionText (a str). An empty result is never silent: check
    ``.status``, and read stderr — an unreadable file and a missing marker
    each announce themselves.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"cdsfl_utils.read_section: CANNOT READ {filepath}: {exc}. "
            f"Returning an empty section.",
            file=sys.stderr,
        )
        return SectionText("", status="unreadable", detail=str(exc))

    start_idx = text.find(start_marker)
    if start_idx == -1:
        print(
            f"cdsfl_utils.read_section: MARKER NOT FOUND: {start_marker!r} is "
            f"absent from {filepath}. The section is empty because the marker "
            f"is missing, not because the section is empty.",
            file=sys.stderr,
        )
        return SectionText("", status="marker-missing", detail=start_marker)

    content = text[start_idx + len(start_marker):]

    if end_marker:
        end_idx = content.find(end_marker)
        if end_idx != -1:
            content = content[:end_idx]

    return SectionText(content.strip())


def _is_likely_not_a_path(ref: str) -> bool:
    """Heuristic: return True if the backtick content is not a file path."""
    # Shell commands (start with known command names or contain operators)
    cmd_prefixes = (
        "python", "pip", "tail", "head", "cat", "ls", "cd", "ps", "git",
        "brew", "npm", "curl", "wget", "mkdir", "rm ", "cp ", "mv ",
        "grep", "find", "chmod", "chown", "sudo", "export", "source",
    )
    if any(ref.lstrip().startswith(p) for p in cmd_prefixes):
        return True
    if any(op in ref for op in ("$(", "&&", "||", " | ")):
        return True

    # Glob / brace-expansion patterns
    if any(c in ref for c in ("*", "{", "}")):
        return True

    # Model ID strings (vendor/model format) — strip leading quotes
    stripped = ref.strip("\"'")
    model_prefixes = ("anthropic/", "openai/", "google/", "deepseek/", "meta/")
    if any(stripped.startswith(p) for p in model_prefixes):
        return True

    # URLs without protocol
    domain_prefixes = ("github.com", "gitlab.com", "bitbucket.org", "pypi.org")
    if any(ref.startswith(d) for d in domain_prefixes):
        return True

    # Unicode mathematical symbols (ceiling, floor, summation, etc.)
    if re.search(r"[⌈⌉⌊⌋∑∏∫≈≤≥×÷±∞∂∇√λγρφσμ]", ref):
        return True

    # Mathematical expressions (arithmetic operators adjacent to /)
    if re.search(r"[+\-*=()]\s*/|/\s*[+\-*=()]", ref):
        return True
    # Spaced division: ` / `
    if " / " in ref:
        return True
    # Numeric fractions: 36/45, 3772/200
    if re.search(r"\b\d+/\d+\b", ref):
        return True
    # Word ratios without file extensions: novel/total, rejected/total
    if re.match(r"^[\w\s\-]*\w+/\w+[\w\s\-]*$", ref) and "." not in ref:
        return True

    # Sentence fragments (start with punctuation + space)
    if ref.lstrip().startswith((". ", ", ", "; ", "! ", "? ")):
        return True

    # Placeholder patterns in paths (round_XX.json, file_{N}.txt)
    if re.search(r"(?:^|/)[\w]*(?:XX|_N_|\{[A-Z]\}|<\w+>)[\w]*(?:\.\w+)?(?:/|$)", ref):
        return True

    # Git status markers
    if ref.startswith(("?? ", "M ", "A ", "D ")):
        return True

    # Table cell fragments (contain pipe)
    if "|" in ref:
        return True

    return False


# A backtick span longer than this cannot be a filesystem path. POSIX NAME_MAX
# is 255 bytes per path COMPONENT, so Path.exists() on a longer component does
# not return False — it raises OSError errno 63 (ENAMETOOLONG). That is the
# whole cause of the crash: an unbalanced backtick in prose let the
# `([^`]+/[^`]+)` pattern span several hundred characters of a sentence, and
# the resulting OSError aborted the reference scan for the entire document.
# Guarding the whole reference at 255 also bounds every component below
# NAME_MAX, so the exists() call can no longer raise.
MAX_REFERENCE_LEN = 255

# Suppression rule labels. Every rule that stops a candidate from being
# reported names itself in the qc report, with a count. A filter nobody can
# see is a filter nobody can falsify — and 183 findings of which ~10 were real
# is the same failure as no findings at all.
SUPPRESS_URL = "URL or mailto — not a file path"
SUPPRESS_OVERLENGTH = (
    f"longer than {MAX_REFERENCE_LEN} chars — prose span from an unbalanced "
    f"backtick, cannot be a path"
)
SUPPRESS_HEURISTIC = (
    "non-path content — shell command, glob, maths, model id, table cell "
    "(_is_likely_not_a_path)"
)
SUPPRESS_PROSE = (
    "leading or trailing whitespace inside the delimiters — a mid-sentence "
    "prose span, not a path"
)
SUPPRESS_COMMAND = (
    "contains a whitespace-separated -flag or --flag — a command invocation, "
    "not a path"
)
SUPPRESS_TEMPLATE = (
    "filename template containing a placeholder — <...>, or an NN/XX digit "
    "stand-in as in bench/expNN_configs/"
)
SUPPRESS_TMP = "/tmp scratch path — transient by design, never expected to exist"
SUPPRESS_HOME = (
    "~ path outside the repository — machine-specific, and it DOES resolve here"
)
# Split out deliberately. These are the only suppressed candidates that carry
# real information: the file is absent on this machine and is no longer
# reported as broken. Rolling them into SUPPRESS_HOME would drop that fact
# silently, which is the exact pattern this repair programme exists to remove.
SUPPRESS_HOME_ABSENT = (
    "~ path outside the repository — DOES NOT resolve on this machine; not "
    "reported as broken because it is outside version control, but it may be dead"
)
SUPPRESS_MEMORY = (
    "memory/ persistent-memory folder — outside the repository, existence NOT checked"
)
SUPPRESS_LINE = "path:line or path:line-range — the FILE exists; line numbers NOT checked"
SUPPRESS_SYMBOL = "path::symbol — the FILE exists; the symbol itself is NOT checked"
SUPPRESS_REGISTRY = "abbreviated prefix resolved under bench/cdsfl_registry/"

# ---------------------------------------------------------------------------
# Rules added 2026-08-12, each one derived from a candidate the checker was
# MISREADING in the 122-finding run of that date. Every one is separately
# named and separately counted, so an over-broad rule shows up as a rule with
# an implausible count rather than as findings that quietly vanish.
#
# Two structural guarantees hold for everything below:
#
#   * RESOLUTION RUNS FIRST. A candidate is tested against the filesystem
#     before any "this is not a path" rule is consulted, so no rule in this
#     block can hide a file that exists inside the repository. The three
#     rules that DO precede resolution — /tmp, ~, memory/ — are the
#     pre-existing out-of-repository family and say so in their own labels.
#   * THE ARITHMETIC IS PUBLISHED. candidates == resolved + suppressed +
#     reported, printed and checked; a mismatch is an error, not a rounding.
# ---------------------------------------------------------------------------

SUPPRESS_ANCHOR = (
    "path#anchor (e.g. #L2094) — the FILE exists; the anchor is NOT checked"
)
SUPPRESS_MODULE_SYMBOL = (
    "module.symbol — the MODULE file exists AND defines that symbol; both "
    "halves are checked"
)
SUPPRESS_ANCESTOR = (
    "qualified by a directory ABOVE the repository root (e.g. "
    "Constraint_Engineering/docs/…) — resolved there, the file EXISTS"
)
SUPPRESS_LOGS = "run-directory prefix resolved under bench/logs/ — the file EXISTS"
SUPPRESS_SAMELINE_DIR = (
    "relative to a directory named in backticks on the SAME line — the file "
    "EXISTS there"
)
SUPPRESS_RANGE = (
    "`..` range notation (FT-001..027) over a directory that EXISTS and holds "
    "files with that prefix — a set of files, not one path; the range BOUNDS "
    "are NOT checked"
)
SUPPRESS_QUOTED = (
    "contains a quote character — a code or transcript fragment "
    "(model_id=\"…\", Path('…').exists()), not a bare path"
)
SUPPRESS_SENTENCE = (
    "several whitespace-separated words whose FIRST word contains neither / "
    "nor . — a command or a prose sentence with a path inside it"
)
SUPPRESS_ASSIGNMENT = "IDENT=value — an environment or keyword assignment"
SUPPRESS_BRACKETED = "wholly enclosed in [ ] — a placeholder or log token"
SUPPRESS_DOUBLE_SLASH = "contains // — no path in this repository does"
SUPPRESS_EXTLIST = "a list of bare file extensions (.docx/.html/.md)"
SUPPRESS_DOMAIN = "hostname with a public TLD — a URL written without its scheme"
SUPPRESS_HTTP_ROUTE = "HTTP API route (/v1/…, /auth/…), not a filesystem path"
SUPPRESS_ELIDED = (
    "contains an elision (… or /...) — the path is abbreviated and cannot be "
    "checked"
)
SUPPRESS_IDENT_PAIR = (
    "dotted identifier pair (Class.attr/attr) — two symbols, not a path"
)
SUPPRESS_CORRECTED = (
    "already accounted for by a dated **[Correction …]** block in this same "
    "document — the record explains it; existence NOT re-litigated"
)


# Key of the audit entry appended to every check_file_references() result.
# Its presence is how a caller tells the audit record apart from a broken
# reference; a caller that ignores it and reads ["reference"] gets a KeyError,
# which is loud. That is deliberate — a filter whose tally can be dropped
# silently is a filter nobody audits.
AUDIT_KEY = "reference_filter_audit"


def _bump(counter: dict[str, int], rule: str) -> None:
    """Record one suppression under `rule`."""
    counter[rule] = counter.get(rule, 0) + 1


def merge_reference_audit(entries: list[dict[str, Any]], audit: dict[str, Any]) -> None:
    """Fold one file's audit entry into a running `audit` accumulator.

    `audit` gains "candidates" (int), "suppressed" (rule -> count) and, once
    anything has resolved, "resolved" (int). "resolved" is added only when
    non-zero so that a document with nothing to report still folds into the
    minimal ``{"candidates": 0, "suppressed": {}}`` shape.
    """
    audit.setdefault("candidates", 0)
    audit.setdefault("suppressed", {})
    for entry in entries:
        record = entry.get(AUDIT_KEY)
        if not record:
            continue
        audit["candidates"] += record.get("candidates", 0)
        if record.get("resolved"):
            audit["resolved"] = audit.get("resolved", 0) + record["resolved"]
        for rule, count in record.get("suppressed", {}).items():
            audit["suppressed"][rule] = audit["suppressed"].get(rule, 0) + count


# A whitespace-separated `-x` / `--xyz` token. Two tracked paths in this repo
# DO contain spaces ("docs/Experiment 40 response.docx"), so the rule is not
# "no spaces"; it is this narrower one. Checked against every tracked path:
# `git ls-files | grep -E '[[:space:]]-{1,2}[A-Za-z]'` returns nothing, so no
# real path can be hidden by it. Every span that matches is a quoted command.
_COMMAND_FLAG_RE = re.compile(r"\s-{1,2}[A-Za-z]")


def _strip_symbol_suffix(ref: str) -> tuple[str, bool]:
    """Strip a trailing ``::symbol`` or ``:symbol`` / ``:symbol()``.

    ``file.py::Class::test`` is a pytest nodeid; ``bench/launch_exp40.py:
    gate_c_preflight()`` is how this project cites a function in prose. Both
    name a file that can be checked and a symbol that cannot.

    Returns (stripped, was_stripped). Only the FILE half is testable here; the
    symbol is not verified and the suppression label says so. The single-colon
    form requires a NON-digit first character so that ``path:123`` still goes
    to ``_strip_line_suffix`` and is labelled as a line reference.
    """
    m = re.match(r"^(.*?\.\w+)::[\w.:]+$", ref)
    if m:
        return m.group(1), True
    m = re.match(r"^(.*?\.\w+):([A-Za-z_][\w.]*)(?:\(\))?$", ref)
    return (m.group(1), True) if m else (ref, False)


def _strip_line_suffix(ref: str) -> tuple[str, bool]:
    """Strip a trailing ``:123`` or ``:123-456``.

    Returns (stripped, was_stripped). The line numbers themselves are not
    verified and the suppression label says so.
    """
    m = re.match(r"^(.*?):\d+(?:-\d+)?$", ref)
    return (m.group(1), True) if m else (ref, False)


def _strip_anchor_suffix(ref: str) -> tuple[str, bool]:
    """Strip a trailing ``#anchor`` (``bench/reference_runner.py#L2094``).

    Returns (stripped, was_stripped). No tracked or on-disk path in this
    repository contains ``#`` — measured over all 10,548 union paths on
    2026-08-12 — so nothing real can be truncated by this.
    """
    if "#" not in ref:
        return ref, False
    head, _, _tail = ref.partition("#")
    return (head, True) if head else (ref, False)


# A dotted module reference: ``bench/dm/_feedback.detect_finding_id_collisions``
# names a symbol inside ``bench/dm/_feedback.py``. Only applied when the final
# component does NOT already end in a known file extension, so `bench/gone.py`
# is never re-read as module `bench/gone` plus symbol `py`.
_KNOWN_EXTENSIONS = {
    "py", "md", "txt", "json", "toml", "yaml", "yml", "sh", "cfg", "ini",
    "csv", "tsv", "html", "svg", "png", "jpg", "pdf", "docx", "log", "lock",
    "example", "pyc", "sql", "js", "ts", "rst", "xml", "env",
}
_DOTTED_SYMBOL_RE = re.compile(r"^(?P<mod>[\w./\-]+)\.(?P<sym>[A-Za-z_]\w*)$")

# `FT-001..027` — a `..` with a word character on each side. An elision (`...`)
# has no word character between the dots and must NOT match.
_RANGE_RE = re.compile(r"\w\.\.\w")


def _dotted_module_path(ref: str) -> Optional[tuple[str, str]]:
    """``pkg/mod.symbol`` -> ``("pkg/mod.py", "symbol")``, else None."""
    tail = ref.rsplit("/", 1)[-1]
    if "." in tail and tail.rsplit(".", 1)[-1].lower() in _KNOWN_EXTENSIONS:
        return None
    m = _DOTTED_SYMBOL_RE.match(ref)
    return (f"{m.group('mod')}.py", m.group("sym")) if m else None


def _module_defines(module: Path, symbol: str) -> bool:
    """Is `symbol` actually DEFINED in `module`?

    Added 2026-08-12 (adversarial pass) because `_KNOWN_EXTENSIONS` is a static
    list and the repository contains real files whose extensions are not on it
    — `.errata` (7), `.logpath` (6), `.pid` (6), `.bak` (2), `.tag` (2),
    `.jsonl`. Without this check the rule matched a SHAPE and verified only the
    MODULE, so a dead data-file reference sitting beside a live module of the
    same stem was silenced with a label claiming a symbol lookup that never
    happened: `bench/dm/_memory.pkl` was absorbed because `bench/dm/_memory.py`
    exists. That is the same defect the range rule was repaired for in this
    same pass, in the rule immediately next to it.

    A whole-word search is NOT enough: a module that writes `.jsonl` files
    contains the word `jsonl` in a string literal, so a dead `mod.jsonl` beside
    `mod.py` would still be swallowed. A definition is required.

    The failure direction is deliberate. No evidence of a definition means the
    reference falls through and is REPORTED — a re-exported symbol therefore
    produces a loud false positive rather than a silent false negative. Blast
    radius for that noise is one reference in the whole 3,459-candidate corpus.
    """
    try:
        text = module.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    sym = re.escape(symbol)
    return re.search(
        rf"^\s*(?:async\s+def|def|class)\s+{sym}\b|^\s*{sym}\s*(?::[^=\n]*)?=",
        text,
        re.M,
    ) is not None


def _ancestor_roots(root: Path) -> list[Path]:
    """Directories ABOVE the repository root, up to and including $HOME.

    This project habitually writes ``Constraint_Engineering/resources/
    RECOVERY.md`` and ``Developer_Projects/OpenBrain/`` — paths qualified by a
    directory the repository itself sits inside. Those references are correct;
    the checker simply had no root that made them resolve. The walk STOPS at
    the home directory so a bare `Desktop/x` cannot start matching things in
    `/` or `/Users`.
    """
    out: list[Path] = []
    try:
        home = Path.home()
    except (OSError, RuntimeError):
        return [root.parent]
    current = root.parent
    while True:
        out.append(current)
        if current == home or current == current.parent:
            break
        current = current.parent
    return out


# A markdown span naming a DIRECTORY on the same line as the candidate, which
# the prose then writes the candidate relative to:
#     **Directory:** `bench/logs/exp40_slice_…` · **Target:** `working/x.py`
# Only directories that actually exist are used, and the candidate must then
# actually exist beneath one — so this is a resolution, not a guess.
_SPAN_RE = re.compile(r"`([^`]+)`|\]\(([^)]+)\)")


def _same_line_directories(line: str, roots: list[Path]) -> list[Path]:
    dirs: list[Path] = []
    for m in _SPAN_RE.finditer(line):
        span = (m.group(1) or m.group(2) or "").strip()
        if not span or len(span) > MAX_REFERENCE_LEN or "/" not in span:
            continue
        for base in roots:
            try:
                candidate = base / span
                if candidate.is_dir():
                    dirs.append(candidate)
                    break
            except OSError:
                continue
    return dirs


# A dated correction block. The convention is established in
# resources/RECOVERY.md, experimental_notes/CDSFL_Agent_Operational_Plan.md and
# four more documents: when a path in a DATED historical entry goes dead, the
# entry is left intact and a `**[Correction YYYY-MM-DD.]**` paragraph is added
# below it saying so. Nine such blocks already existed when this rule was
# written, and every reference they document was still being reported as a
# fresh defect — the checker could not read the record the project keeps.
_CORRECTION_MARKER = "**[Correction "

# The block must actually say the path is dead, so the rule means what its
# name says and cannot be satisfied by a correction that merely MENTIONS a path.
_DEAD_MARKERS = (
    "dead", "does not exist", "never existed", "never created", "never been",
    "no longer", "renamed", "mis-typed", "mistyped", "wrong", "removed",
    "not created", "superseded", "stale", "to be created", "forward-looking",
    "moved",
)


def _correction_blocks(text: str) -> list[str]:
    """Blank-line-delimited paragraphs that are dated corrections about a
    dead path.

    BOUNDED TO THE PARAGRAPH, so a correction cannot vouch for the whole
    document. Measured over the live estate on 2026-08-12: 25 correction
    blocks, largest 1,624 characters, largest 15.6% of its own file, and they
    silence 56 citations forming 26 distinct (document, path) pairs over 19
    distinct dead paths — every one of which was verified dead by hand before
    the rule was written. **[Correction 2026-08-12, adversarial pass.]** This
    docstring previously read "26 distinct dead paths"; 26 is the pair count,
    and the distinct-path count is 19.

    THE LIMITATION, stated because it is real: once a document names a path as
    dead, a NEW citation of that same path added to that same document later
    is also silenced. That is the price of reading the record instead of
    re-litigating it, and it is why the count is published under a rule name
    that says existence is not re-checked.
    """
    blocks: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        if _CORRECTION_MARKER not in para:
            continue
        low = para.lower()
        if any(marker in low for marker in _DEAD_MARKERS):
            blocks.append(para)
    return blocks


# --- the not-a-path rules, in the order they are consulted --------------------
# Each is a (label, predicate) pair so the table itself is the documentation and
# the tally lines up one-to-one with it.

_EXTLIST_RE = re.compile(r"^(?:\.\w{1,5}/){2,}\.\w{1,5}$")
_DOMAIN_RE = re.compile(
    r"^(?:[A-Za-z0-9-]+\.)+"
    r"(?:com|org|net|io|ai|dev|edu|gov|uk|co|me|sh|app|xyz|so|to)(?:/|$)"
)
_HTTP_ROUTE_RE = re.compile(r"^/(?:v\d+|api|auth|oauth|health|credits)(?:/|$)")
_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_IDENT_PAIR_RE = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+/[A-Za-z_]\w*$")
_PLACEHOLDER_RE = re.compile(r"(?:^|/)\w*(?:NN|XX)\w*(?:\.\w+)?(?:/|$)")


def _is_sentence(ref: str) -> bool:
    """Whitespace-separated words whose FIRST word is not path-shaped.

    `pytest bench/tests/`, `Read bench/runner_core.py lines 158-181`,
    `1 - exp(-E/20)`, `The commit carrying this file is not listed below; run
    scripts/cdsfl_recover.py …` — a command or a sentence that happens to
    contain a path, not a path.

    Narrowness, measured rather than asserted: of the 10,548 tracked and
    on-disk paths in this repository, TWO contain whitespace
    (`docs/Experiment 40 response.docx` and its .txt sibling) and in both the
    first word is `docs/Experiment`, which contains a slash. Zero real paths
    satisfy this predicate.
    """
    parts = ref.split()
    if len(parts) < 2:
        return False
    first = parts[0]
    return "/" not in first and "." not in first


_NOT_A_PATH_RULES: list[tuple[str, Any]] = [
    # PROSE must precede SENTENCE: a span with a leading space would otherwise
    # be attributed to the newer, broader rule.
    (SUPPRESS_PROSE, lambda r: r != r.strip()),
    (SUPPRESS_ELIDED, lambda r: "…" in r or "/..." in r or r.endswith("...")),
    (SUPPRESS_QUOTED, lambda r: '"' in r or "'" in r),
    (SUPPRESS_BRACKETED, lambda r: r.startswith("[") and r.endswith("]")),
    (SUPPRESS_ASSIGNMENT, lambda r: _ASSIGNMENT_RE.match(r) is not None),
    (SUPPRESS_DOUBLE_SLASH, lambda r: "//" in r),
    (SUPPRESS_EXTLIST, lambda r: _EXTLIST_RE.match(r) is not None),
    (SUPPRESS_DOMAIN, lambda r: _DOMAIN_RE.match(r) is not None),
    (SUPPRESS_HTTP_ROUTE, lambda r: _HTTP_ROUTE_RE.match(r) is not None),
    (SUPPRESS_IDENT_PAIR, lambda r: _IDENT_PAIR_RE.match(r) is not None),
    (SUPPRESS_SENTENCE, _is_sentence),
    (SUPPRESS_HEURISTIC, _is_likely_not_a_path),
    (SUPPRESS_COMMAND, lambda r: _COMMAND_FLAG_RE.search(r) is not None),
    (SUPPRESS_TEMPLATE,
     lambda r: ("<" in r and ">" in r) or _PLACEHOLDER_RE.search(r) is not None),
]


def _exists(path: Path) -> bool:
    """`.exists()` that cannot raise. The length guard already bounds every
    component below NAME_MAX; this is the belt to that pair of braces."""
    try:
        return path.exists()
    except OSError:
        return False


def _resolve_reference(
    ref: str, md_path: Path, root: Path, line: str
) -> Optional[str]:
    """Try every way this project writes a path. Return None if none of them
    finds a file; otherwise the suppression label to record ("" when the
    reference resolved plainly and nothing was left unchecked).
    """
    clean, anchor_stripped = _strip_anchor_suffix(ref)
    clean, line_stripped = _strip_line_suffix(clean)
    clean, symbol_stripped = _strip_symbol_suffix(clean)

    registry = root / "bench" / "cdsfl_registry"
    # (root, label) in precedence order. The first four are repo-internal; the
    # ancestors come last so an in-repo file always wins.
    bases: list[tuple[Path, str]] = [
        (md_path.parent, ""),
        (root, ""),
        (root / "bench", ""),
        (root / "bench" / "logs", SUPPRESS_LOGS),
        (registry, SUPPRESS_REGISTRY),
    ]
    bases += [(a, SUPPRESS_ANCESTOR) for a in _ancestor_roots(root)]

    def _suffix_label(base_label: str) -> str:
        if symbol_stripped:
            return SUPPRESS_SYMBOL
        if line_stripped:
            return SUPPRESS_LINE
        if anchor_stripped:
            return SUPPRESS_ANCHOR
        return base_label

    candidate = Path(clean)
    if candidate.is_absolute():
        return _suffix_label("") if _exists(candidate) else None

    for base, label in bases:
        if _exists(base / candidate):
            return _suffix_label(label)

    # `pkg/mod.symbol` — BOTH halves are checked. The module must exist AND
    # must define the symbol; see _module_defines for why the module alone is
    # not sufficient evidence.
    dotted = _dotted_module_path(clean)
    if dotted is not None:
        module, symbol = dotted
        for base, _label in bases:
            target = base / module
            if _exists(target) and _module_defines(target, symbol):
                return SUPPRESS_MODULE_SYMBOL

    # A directory named in backticks on the same line, which the prose then
    # writes this reference relative to.
    for directory in _same_line_directories(line, [root, root / "bench", md_path.parent]):
        if _exists(directory / candidate):
            return _suffix_label(SUPPRESS_SAMELINE_DIR)

    # `bench/tasks_frontier/FT-001..027` — a range over a real directory.
    #
    # Two guards, and the falsifier test found the need for both.
    # (a) The `..` must sit BETWEEN two word characters. Without that guard the
    #     rule also swallowed `Constraint_Engineering/experimental_notes/...`,
    #     which is an elision, not a range.
    # (b) The directory must actually CONTAIN something with the range's
    #     prefix. Checking only that the directory exists made the rule match a
    #     shape rather than verify evidence: `bench/tasks_frontier/GONE-001..027`
    #     was silently accepted because `bench/tasks_frontier/` happens to
    #     exist. Matching is case-insensitive because the notes write `FT-001`
    #     for files stored as `ft-001.json`.
    if _RANGE_RE.search(candidate.name) and len(candidate.parts) > 1:
        parent = Path(*candidate.parts[:-1])
        prefix = re.match(r"^\D*", candidate.name).group(0).lower()
        for base, _label in bases:
            try:
                directory = base / parent
                if not directory.is_dir():
                    continue
                members = [p.name.lower() for p in directory.iterdir()]
            except OSError:
                continue
            if not members:
                continue
            if not prefix or any(name.startswith(prefix) for name in members):
                return SUPPRESS_RANGE

    return None


def check_file_references(md_path: Path) -> list[dict[str, Any]]:
    """Check a markdown file for broken file path references.

    Returns a list whose entries are one of three kinds:

      * a broken reference — ``file``, ``line``, ``reference``;
      * a scan failure — additionally carries ``scan_failed``. An UNREADABLE
        file is never silent: the document got no reference scan, and the
        caller must say so rather than report zero broken references;
      * exactly one audit entry, keyed ``AUDIT_KEY``, carrying how many
        candidates were examined, how many resolved outright, and how many
        each suppression rule threw away. Fold it in with
        ``merge_reference_audit`` and PRINT it. An unaudited filter is how 10
        real defects end up indistinguishable from 173 false ones — which is
        the same failure as reporting nothing.

        The audit is arithmetic, not decoration:
        ``candidates == resolved + sum(suppressed) + len(broken)``. A run in
        which that does not hold has lost candidates somewhere, and
        ``print_reference_audit`` says so in capitals rather than printing a
        tidy number.
    """
    broken: list[dict[str, Any]] = []
    suppressed: dict[str, int] = {}
    candidates = 0
    resolved = 0

    def _audit() -> dict[str, Any]:
        record: dict[str, Any] = {"candidates": candidates, "suppressed": suppressed}
        # Only added when non-zero, so a document with nothing to report still
        # produces the minimal audit shape its callers were written against.
        if resolved:
            record["resolved"] = resolved
        return {"file": str(md_path), AUDIT_KEY: record}

    try:
        raw_text = md_path.read_text(encoding="utf-8")
        lines = raw_text.splitlines()
    except OSError as exc:
        print(
            f"cdsfl_utils.check_file_references: CANNOT READ {md_path}: {exc}. "
            f"This document received NO reference scan — its references are "
            f"UNKNOWN, not clean.",
            file=sys.stderr,
        )
        return [
            {
                "file": str(md_path),
                "line": 0,
                "reference": "",
                "scan_failed": f"unreadable: {exc}",
            },
            _audit(),
        ]

    root = repo_root()
    corrections = _correction_blocks(raw_text)

    def _home_rule(ref: str) -> Optional[str]:
        """`~/...`, or an absolute path under $HOME but OUTSIDE the repository.

        Both spellings name the same thing. The variant that does NOT resolve
        keeps its own label so the only home-path candidates carrying any
        information stay visible in the tally.
        """
        target: Optional[Path] = None
        if ref.startswith("~"):
            target = Path(ref).expanduser()
        elif ref.startswith("/"):
            try:
                home = Path.home()
            except (OSError, RuntimeError):
                return None
            candidate = Path(ref)
            if home in candidate.parents and root not in candidate.parents:
                target = candidate
        if target is None:
            return None
        return SUPPRESS_HOME if _exists(target) else SUPPRESS_HOME_ABSENT

    for i, line in enumerate(lines, 1):
        # Match backtick-enclosed paths and markdown link targets
        for pattern in [r"`([^`]+/[^`]+)`", r"\]\(([^)]+/[^)]+)\)"]:
            for m in re.finditer(pattern, line):
                ref = m.group(1)
                candidates += 1

                # Skip URLs
                if ref.startswith(("http://", "https://", "mailto:")):
                    _bump(suppressed, SUPPRESS_URL)
                    continue
                # LENGTH GUARD — must precede every .exists() call below.
                if len(ref) > MAX_REFERENCE_LEN:
                    _bump(suppressed, SUPPRESS_OVERLENGTH)
                    continue

                # --- The out-of-repository family, decided before resolution.
                # These name things this repository does not and will not own,
                # and each label says so.
                if ref.startswith("/tmp/"):
                    _bump(suppressed, SUPPRESS_TMP)
                    continue
                home_label = _home_rule(ref)
                if home_label is not None:
                    _bump(suppressed, home_label)
                    continue
                if ref.startswith("memory/"):
                    _bump(suppressed, SUPPRESS_MEMORY)
                    continue

                # --- RESOLUTION FIRST, for everything else.
                # Nothing below this point can hide a file that exists inside
                # the repository, because existence has already been tested
                # against every prefix and suffix form the project writes.
                label = _resolve_reference(ref, md_path, root, line)
                if label is not None:
                    # `resolved` counts ONLY the resolutions no rule was needed
                    # for. A resolution that WAS attributed to a named strategy
                    # is counted once, under that strategy, in `suppressed` —
                    # counting it in both is what made the first run of this
                    # tally over-report by exactly 247.
                    if label:
                        _bump(suppressed, label)
                    else:
                        resolved += 1
                    continue

                # --- Not found. Is it a path at all?
                rule = next(
                    (name for name, matches in _NOT_A_PATH_RULES if matches(ref)),
                    None,
                )
                if rule is not None:
                    _bump(suppressed, rule)
                    continue

                # --- A real dead path. Has the document already said so?
                #
                # The correction must CITE the path in one of the two delimited
                # forms the scanner itself recognises — `path` or [text](path).
                #
                # **[Correction 2026-08-12, adversarial pass.]** This test was a
                # bare substring match (`ref in block`), which is not the
                # "names the path verbatim" fence it was described as: a
                # correction documenting `bench/foo/bar.py` as dead ALSO
                # silenced the separate, undocumented dead path `bench/foo`,
                # because the shorter path is a substring of the longer one.
                # This is the only rule here that can hide a genuinely dead
                # path, so a prefix must not inherit another path's excuse.
                # Measured before changing it: all 56 live suppressions (26
                # document/path pairs) already satisfy the delimited form, so
                # the tightening reports nothing new and hides nothing new.
                if any((f"`{ref}`" in block) or (f"]({ref})" in block)
                       for block in corrections):
                    _bump(suppressed, SUPPRESS_CORRECTED)
                    continue

                broken.append({
                    "file": str(md_path),
                    "line": i,
                    "reference": ref,
                })

    broken.append(_audit())
    return broken


def source_env() -> None:
    """Load .env file into environment (mirrors runner_core.py)."""
    env_file = repo_root() / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # `.env` lines are written as `export KEY=value`. Without stripping the
        # prefix, partition() names the variable "export KEY" and every key
        # reads as MISSING. Same two lines as bench/runner_core.py.
        if line.startswith("export "):
            line = line[7:]
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            os.environ.setdefault(key, value)
