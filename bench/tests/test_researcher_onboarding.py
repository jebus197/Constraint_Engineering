"""Pins the researcher-facing documents against the way they went stale.

WHY THIS FILE EXISTS
--------------------
The repair applied on 2026-08-07 corrected six documents that told an outside
researcher to do things that could not be done: a `ps aux | grep` for a process
pattern no current runner matches, an experiment table that stopped eight
experiments short, a `pip install` that could not reach the verification step it
named, a credential retired on 2026-08-03 listed as required, and an analysis
snippet that raises `KeyError` against every report from Experiment 42 onward.

Each of those was, at the moment it was written, true. They rotted because
nothing measured them. Fixing the documents without fixing that leaves the next
reader in the same place, so these tests derive their truth from the repository
rather than restating it:

  * the active runner is read out of `bench/launcher_core.py` by AST, not named
    here — when the arc moves to a v3 runner, the documents' process check goes
    stale and `test_running_experiment_check_names_the_active_runner` fires;
  * the documented credential set is read out of `scripts/cdsfl_onboard.py`, the
    only maintained list;
  * the experiments a reader can find results for are read out of `bench/logs/`.

WHAT IS DELIBERATELY NOT POLICED
--------------------------------
Dated historical entries. `resources/ONBOARDING.md` is 89% reverse-chronological
changelog, and this project treats rewriting a record as a fault: the convention
for correcting one is an inline dated correction block, not an edit. So every
scan here skips any paragraph carrying a `**[Correction …]**` marker — those
paragraphs QUOTE the defective instruction on purpose — and the credential and
path scans over ONBOARDING.md are scoped to its three researcher-facing action
sections rather than to the archive above them.

Offline: pure filesystem reads, `json`, `ast`. No subprocess, no sockets. Passes
under `--netguard-strict`.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# The six documents an outside researcher actually reads.
RESEARCHER_DOCS = (
    "resources/ONBOARDING.md",
    "resources/README.md",
    "docs/REPRODUCING.md",
    "docs/ARCHITECTURE.md",
    "docs/GLOSSARY.md",
    "README.md",
)

# The three sections of ONBOARDING.md that onboard a stranger.
ACTION_SECTIONS = (
    "## How to Resume Work",
    "## How to Reproduce Results",
    "## How to Refute Results",
)

REFERENCE_RUN = (
    "bench/logs/exp46_stage6_locationkey_live_20260728T103151Z"
)
REFERENCE_REPORT = "exp46_stage6_locationkey_live_report.json"


# ---------------------------------------------------------------------------
# Helpers — every one of these MEASURES; none of them restates.
# ---------------------------------------------------------------------------

def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _paragraphs(text: str) -> list[str]:
    return re.split(r"\n\s*\n", text)


def _strip_correction_blocks(text: str) -> str:
    """Drop paragraphs carrying a dated correction marker.

    Those paragraphs exist to quote the defective instruction they replaced.
    Policing them would demand rewriting a record, which the project forbids.
    """
    kept = [p for p in _paragraphs(text) if "[Correction" not in p]
    return "\n\n".join(kept)


def _section(text: str, heading: str) -> str:
    """Text from `heading` up to the next heading at the same or higher level.

    Fenced code blocks are skipped when hunting the next heading. A shell
    comment at column 0 (`# from the repository root`) is not a markdown
    heading, and treating it as one silently truncated the section — which is
    the same class of defect these tests exist to catch.
    """
    level = len(heading) - len(heading.lstrip("#"))
    lines = text.splitlines(keepends=True)
    start_idx = next(
        (i for i, ln in enumerate(lines) if ln.rstrip("\n") == heading), None
    )
    assert start_idx is not None, f"section heading not found: {heading!r}"

    in_fence = False
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        stripped = lines[i].lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"(#{1,6})\s", lines[i])
        if m and len(m.group(1)) <= level:
            end_idx = i
            break
    return "".join(lines[start_idx:end_idx])


def _onboarding_action_text() -> str:
    doc = _read("resources/ONBOARDING.md")
    return "\n\n".join(_section(doc, h) for h in ACTION_SECTIONS)


def active_runner_module() -> str:
    """Read the active runner out of the launcher, by AST.

    `bench/launcher_core.py` is the single place the arc's runner is imported.
    Deriving it here means a runner rename cannot leave the documents' process
    check silently pointing at a module nobody runs any more.
    """
    tree = ast.parse(_read("bench/launcher_core.py"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = {a.name for a in node.names}
            if "run_experiment" in names and node.module.startswith("bench."):
                return node.module.split(".", 1)[1]
    pytest.fail(
        "could not determine the active runner: no "
        "`from bench.<runner> import run_experiment` in bench/launcher_core.py"
    )


def documented_credentials() -> set[str]:
    """The credential names the onboarding wizard documents (AST, not regex)."""
    tree = ast.parse(_read("scripts/cdsfl_onboard.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", "") == "API_KEYS" for t in node.targets
        ):
            return {
                k.value for k in node.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            }
    pytest.fail("API_KEYS not found in scripts/cdsfl_onboard.py")


def experiments_with_run_directories() -> set[int]:
    """Experiment numbers a reader can find committed results for."""
    logs = REPO_ROOT / "bench" / "logs"
    found = set()
    for entry in logs.iterdir():
        if not entry.is_dir():
            continue
        m = re.match(r"exp(\d+)[_a-zA-Z]", entry.name)
        if m:
            found.add(int(m.group(1)))
    return found


_PLACEHOLDER = re.compile(r"[<>{}*]|expNN|\.\.\.|%s|\{N\}")
_PATH_TOKEN = re.compile(
    r"(?<![\w/.-])((?:bench|docs|scripts|resources|experimental_notes)"
    r"/[\w./-]*\.(?:py|sh|json|md|toml|txt))"
)


def _paths_named_in(text: str) -> set[str]:
    """Repo-relative file paths named in `text`, placeholders excluded."""
    out = set()
    for raw in _PATH_TOKEN.findall(text):
        token = raw.rstrip(".,;:)`\"'")
        if _PLACEHOLDER.search(token):
            continue
        out.add(token)
    return out


_GREP = re.compile(
    r"\bgrep\b(?P<flags>(?:\s+-[\w-]+)*)\s+"
    r"(?P<pat>\"[^\"]+\"|'[^']+'|[^\s|`\"']+)"
)


def _grep_invocations(text: str) -> list[tuple[str, str]]:
    """(flags, pattern) for each grep call, `grep -v` excluded.

    `grep -v grep` is the idiomatic tail of a `ps aux` pipeline and describes
    nothing about the repository, so it is not a claim this test can check.
    """
    out = []
    for m in _GREP.finditer(text):
        flags = m.group("flags") or ""
        if "-v" in flags.split():
            continue
        pat = m.group("pat").strip("\"'")
        out.append((flags, pat))
    return out


def _bench_path_strings() -> list[str]:
    """Every path under bench/, as a string, for pattern matching."""
    bench = REPO_ROOT / "bench"
    return [
        str(p.relative_to(REPO_ROOT))
        for p in bench.rglob("*")
        if "__pycache__" not in p.parts
    ]


# ---------------------------------------------------------------------------
# 1. Every script path named in the three action sections exists.
# ---------------------------------------------------------------------------

def test_action_section_paths_exist():
    text = _strip_correction_blocks(_onboarding_action_text())
    named = _paths_named_in(text)
    assert named, "no paths extracted — the extractor or the sections changed"
    missing = sorted(p for p in named if not (REPO_ROOT / p).exists())
    assert not missing, (
        "ONBOARDING.md's Resume/Reproduce/Refute sections name "
        f"{len(missing)} path(s) that do not exist: {missing}. A researcher "
        "following these sections has only the repository; a path that is not "
        "there reads to them as their own mistake."
    )


def test_action_sections_name_the_reference_run_and_its_config():
    """The reproduction the documents promise must be self-contained."""
    text = _onboarding_action_text()
    config = "bench/exp46_configs/46_stage6_locationkey_live.json"
    assert config in text, (
        "the Reproduce section no longer names a committed config; without one "
        "there is nothing for a reader to run"
    )
    assert (REPO_ROOT / config).exists()
    run_dir = REPO_ROOT / REFERENCE_RUN
    assert run_dir.is_dir(), (
        f"{REFERENCE_RUN} is named as the committed comparison result but is "
        "not in the tree"
    )
    cfg = json.loads((REPO_ROOT / config).read_text())
    target = cfg["test_article"]
    assert (REPO_ROOT / target).exists(), (
        f"the reference experiment's target {target!r} is not in the "
        "repository, so the run is not reproducible from a clone"
    )


def test_reproducing_guide_paths_exist():
    text = _strip_correction_blocks(_read("docs/REPRODUCING.md"))
    named = _paths_named_in(text)
    missing = sorted(p for p in named if not (REPO_ROOT / p).exists())
    assert not missing, f"docs/REPRODUCING.md names missing path(s): {missing}"


# ---------------------------------------------------------------------------
# 2. No document instructs a grep for a pattern that matches nothing.
# ---------------------------------------------------------------------------

def test_no_document_greps_for_a_pattern_that_matches_nothing():
    bench_paths = _bench_path_strings()
    failures = []
    for doc in RESEARCHER_DOCS:
        text = _strip_correction_blocks(_read(doc))
        for _flags, pattern in _grep_invocations(text):
            for alt in pattern.split("|"):
                alt = alt.strip()
                if not alt or not re.fullmatch(r"[\w./-]+", alt):
                    continue  # not a literal we can resolve against the tree
                if not any(alt in p for p in bench_paths):
                    failures.append(f"{doc}: grep {alt!r} matches nothing under bench/")
    assert not failures, (
        "a documented grep cannot match anything in the tree, so it will "
        "return silence and read as an authoritative negative:\n  "
        + "\n  ".join(failures)
    )


def test_running_experiment_check_names_the_active_runner():
    """The 'is an experiment running?' check must name the runner that runs.

    This is the defect that survived a repair scoped to one file: the check
    matched `run_round_robin`, the Bench Run 1 driver, while the arc had been
    running `reference_runner_v3.py` for months. Silence from that grep during
    a live run reads as 'nothing is running'.
    """
    runner = active_runner_module()
    onboarding = _strip_correction_blocks(_read("resources/ONBOARDING.md"))
    ps_lines = [
        line for line in onboarding.splitlines()
        if "ps aux" in line or "pgrep" in line
    ]
    assert ps_lines, (
        "resources/ONBOARDING.md no longer carries a running-experiment check"
    )
    for line in ps_lines:
        assert runner in line, (
            f"the running-experiment check {line.strip()!r} does not mention "
            f"the active runner {runner!r} (read from bench/launcher_core.py). "
            "It cannot detect a live run of the current arc."
        )


# ---------------------------------------------------------------------------
# 3. The experiment table covers the experiments that have results.
# ---------------------------------------------------------------------------

_RANGE = re.compile(
    r"\bExp(?:eriment)?s?\s+(\d{1,2})\s*(?:[-–—]|\s+to\s+)\s*(\d{1,2})\b"
)
_SINGLE = re.compile(r"\bExp(?:eriment)?s?\s+(\d{1,2})\b")


def _experiments_covered(text: str) -> set[int]:
    covered: set[int] = set()
    for lo, hi in _RANGE.findall(text):
        covered.update(range(int(lo), int(hi) + 1))
    covered.update(int(n) for n in _SINGLE.findall(text))
    return covered


def test_reproducing_experiment_table_covers_every_run_directory():
    section = _section(_read("docs/REPRODUCING.md"), "### 1. Choose an Experiment")
    covered = _experiments_covered(_strip_correction_blocks(section))
    have_results = experiments_with_run_directories()
    uncovered = sorted(have_results - covered)
    assert not uncovered, (
        "bench/logs/ holds committed run directories for experiment(s) "
        f"{uncovered}, and 'Choose an Experiment' in docs/REPRODUCING.md does "
        "not mention them. A reader who finds those results has no route from "
        "the guide to the harness that produced them."
    )


def test_reproducing_names_the_shared_launcher_and_active_runner():
    text = _read("docs/REPRODUCING.md")
    runner = active_runner_module()
    assert f"bench/{runner}.py" in text, (
        f"docs/REPRODUCING.md never names the active runner bench/{runner}.py"
    )
    assert "bench/launch_exp42.py" in text, (
        "docs/REPRODUCING.md never names the shared launcher; every current "
        "result was produced through it"
    )
    assert (REPO_ROOT / "bench" / "launch_exp42.py").exists()


# ---------------------------------------------------------------------------
# 4. No researcher-facing document names a credential outside the documented set.
# ---------------------------------------------------------------------------

_CREDENTIAL = re.compile(r"\b([A-Z][A-Z0-9]{1,}(?:_[A-Z0-9]+)*_(?:API_KEY|KEY|TOKEN))\b")

# Scanned whole-file. ONBOARDING.md is excluded here and scanned separately:
# it is a changelog, and its dated entries legitimately record credentials that
# were live at the time.
_WHOLE_FILE_CREDENTIAL_DOCS = tuple(
    d for d in RESEARCHER_DOCS if d != "resources/ONBOARDING.md"
)


def _credential_mentions(text: str) -> set[str]:
    return set(_CREDENTIAL.findall(_strip_correction_blocks(text)))


def test_no_researcher_doc_names_an_undocumented_credential():
    documented = documented_credentials()
    assert documented, "the documented credential set came back empty"
    failures = []
    for doc in _WHOLE_FILE_CREDENTIAL_DOCS:
        for name in sorted(_credential_mentions(_read(doc)) - documented):
            failures.append(f"{doc}: {name}")
    for name in sorted(_credential_mentions(_onboarding_action_text()) - documented):
        failures.append(f"resources/ONBOARDING.md (action sections): {name}")
    assert not failures, (
        "credential(s) named in researcher-facing documents but absent from "
        "API_KEYS in scripts/cdsfl_onboard.py, the maintained list:\n  "
        + "\n  ".join(failures)
        + "\nEither the credential is retired and the document is stale, or the "
          "wizard's list is."
    )


def test_gemini_key_is_not_presented_as_required():
    """The panel has routed Gemini via OpenRouter since 2026-05-10.

    `scripts/cdsfl_onboard.py` marks GEMINI_API_KEY Optional. A guide that
    marks it Required sends a researcher to obtain a credential no run needs.
    """
    documented = documented_credentials()
    assert "GEMINI_API_KEY" in documented
    tree = ast.parse(_read("scripts/cdsfl_onboard.py"))
    status = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", "") == "API_KEYS" for t in node.targets
        ):
            for k, v in zip(node.value.keys, node.value.values):
                if getattr(k, "value", None) == "GEMINI_API_KEY":
                    status = v.elts[0].value
    assert status == "Optional", (
        f"the wizard now marks GEMINI_API_KEY {status!r}; this test and "
        "docs/REPRODUCING.md both need revisiting"
    )
    for line in _strip_correction_blocks(_read("docs/REPRODUCING.md")).splitlines():
        if "GEMINI_API_KEY" in line and "Required" in line:
            pytest.fail(
                "docs/REPRODUCING.md marks GEMINI_API_KEY as Required, "
                f"contradicting scripts/cdsfl_onboard.py: {line.strip()!r}"
            )


_NEGATED = (
    "no key", "needs no key", "not required", "never required", "no credential",
    "credential-free", "retired", "cross-verification tool only", "optional",
)


def test_no_action_section_asks_for_a_wolfram_credential():
    """Wolfram's paid keys stopped functioning after 2026-07-31 and the
    credential was retired on 2026-08-03. It was never required for a run."""
    scopes = {
        "resources/ONBOARDING.md (action sections)": _onboarding_action_text(),
        "docs/REPRODUCING.md (prerequisites)": _section(
            _read("docs/REPRODUCING.md"), "## Prerequisites"
        ),
    }
    failures = []
    for where, text in scopes.items():
        for line in _strip_correction_blocks(text).splitlines():
            low = line.lower()
            if "wolfram" not in low:
                continue
            if not any(k in low for k in ("key", "credential", "api", ".env")):
                continue
            if any(neg in low for neg in _NEGATED):
                continue
            failures.append(f"{where}: {line.strip()!r}")
    assert not failures, (
        "a researcher-facing instruction still ties Wolfram to a credential:\n  "
        + "\n  ".join(failures)
    )


# ---------------------------------------------------------------------------
# 5. The documented ways to READ a result still work.
#    These pin the two snippets the repair rewrote, against the committed run
#    they name. A key rename in the runner turns them red here rather than in a
#    stranger's terminal.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reference_report() -> dict:
    path = REPO_ROOT / REFERENCE_RUN / REFERENCE_REPORT
    assert path.exists(), f"the documented reference report is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_documented_analysis_snippet_keys_resolve(reference_report):
    report = reference_report
    for key in ("total_rounds", "total_findings", "converged_at",
                "convergence_reason", "gamma_history", "gamma_critical_history"):
        assert key in report, (
            f"docs/REPRODUCING.md § Analyse reads report[{key!r}]; it is not in "
            f"{REFERENCE_REPORT}. That snippet now raises KeyError for a reader."
        )
    signal = json.loads(
        (REPO_ROOT / REFERENCE_RUN / "completion_signal.json").read_text()
    )
    assert "status" in signal
    assert report["gamma_history"] and report["gamma_critical_history"]


def test_gamma_is_never_documented_as_a_bare_top_level_key(reference_report):
    """`report['gamma']` was the documented reader and does not exist.

    Both series must be named explicitly; a bare 'gamma' is ambiguous between
    the gate input and the telemetry.
    """
    assert "gamma" not in reference_report, (
        "a top-level 'gamma' key has reappeared in the report — the "
        "documentation deliberately names gamma_history and "
        "gamma_critical_history instead, and needs revisiting"
    )
    reproducing = _strip_correction_blocks(_read("docs/REPRODUCING.md"))
    assert "report['gamma']" not in reproducing
    assert 'report["gamma"]' not in reproducing


def test_documented_refutation_route_resolves(reference_report):
    """ONBOARDING's 'How to Refute Results' route 1 must be executable.

    It tells a reader to pull CONFIRMED findings and their falsifiers out of
    the committed report. This asserts the shape it navigates, without
    re-executing the falsifiers (that is a subprocess fan-out; the executed
    result, 19/19 reproduced on 2026-08-07, is recorded in the document).
    """
    entries = reference_report["registry"]["entries"]
    assert entries, "the reference report carries no registry entries"
    confirmed = {
        cid: e for cid, e in entries.items()
        if e.get("falsifier_verdict") == "CONFIRMED"
    }
    assert confirmed, (
        "no CONFIRMED falsifier verdicts in the reference report — the "
        "documented refutation route has nothing to attack"
    )
    for cid, entry in confirmed.items():
        assert (entry.get("falsifier_code") or "").strip(), (
            f"{cid} is CONFIRMED but carries no falsifier source; the runner's "
            "verdict would not be independently re-runnable"
        )
    refute = _section(_read("resources/ONBOARDING.md"), "## How to Refute Results")
    for token in ("registry", "entries", "falsifier_verdict", "falsifier_code",
                  "reverify_falsifier"):
        assert token in refute, (
            f"'How to Refute Results' no longer names {token!r}; the route it "
            "describes must match the report structure asserted above"
        )
    assert (REPO_ROOT / "bench" / "falsifier_verify.py").exists()
