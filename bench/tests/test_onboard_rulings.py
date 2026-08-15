"""Pins for the founder rulings applied to scripts/cdsfl_onboard.py (2026-08-06).

THE DEFECT THESE CLOSE
----------------------
`cdsfl_onboard.py --full` was a byte-for-byte no-op from the day it was
written until 2026-08-06 — 118 days. `read_onboarding_what_is` extracted the
`## What This Project Is` section and then searched *that extract* for the
SV:LATEST_EXP marker pair, while `cdsfl_sv.py` writes the pair into
`## Current State`. `content.find(SV_START_MARKER)` returned -1 every time,
the guard fell through, and `--full` returned the same 884-character stub as
the default view while ~80,000 characters of project state went unmentioned.

Worse than the no-op: the script's own `--dry-run` self-test printed "OK" over
it for the whole 118 days, because it asserted only that the markers existed
somewhere in the file and that the reader returned a non-empty string. It
never compared the two views. A self-test that cannot fail on the defect it
exists to catch is not a test.

RULING 8 (founder, verbatim): "Take the search route." — search the whole file
for the marker pair and splice from wherever they are, rather than moving what
sv writes. So nothing below may depend on section ordering, section names, or
line numbers; the markers alone locate the block.

WHAT IS PINNED HERE
-------------------
1.  The splice works when the block lives OUTSIDE `## What This Project Is`
    (the live arrangement, and the exact case the old code got wrong).
2.  It still works, without duplication, if the block ever moves INSIDE that
    section — the ruling's robustness claim, not merely today's layout.
3.  A `--full` that cannot splice FAILS LOUDLY: a named problem, the default
    text unchanged, a False return, never a silent stub.
4.  The self-test CAN FAIL. Several broken states are constructed and the
    self-test is required to go red on each, then green on the repaired copy.
5.  `--dry-run` prints per-check evidence, not a bare "OK".
6.  The credential roster matches `.claude/CLAUDE.md` and the peer preflight
    `scripts/check_model_keys.py`, and no key VALUE is ever printed.
7.  Wolfram is reported RETIRED, not MISSING.

Every fixture below is a throwaway tree under tmp_path. No test reads or
writes the real resources/ONBOARDING.md, and none spawns a subprocess or
touches the network, so the module is clean under --netguard-strict.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import cdsfl_onboard as ob  # noqa: E402
from cdsfl_utils import repo_root  # noqa: E402

START = ob.SV_START_MARKER
END = ob.SV_END_MARKER

WHAT_IS_BODY = "CDSFL is a methodology for making AI-assisted technical work reliable."
SV_PAYLOAD = "- **EXP 99 CONVERGED (2026-08-06):** the spliced state block."
MC_HEADING = "## Metacognitive Commands (MC)"


def _write_root(
    tmp_path: Path,
    *,
    onboarding: str,
    reproducing: str = f"# Reproducing\n\n{MC_HEADING}\n\n| Cmd | Action |\n| `y` | Yes |\n",
) -> Path:
    """Build a minimal fake repo root. Returns the root."""
    (tmp_path / "resources").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "resources" / "ONBOARDING.md").write_text(onboarding, encoding="utf-8")
    (tmp_path / "docs" / "REPRODUCING.md").write_text(reproducing, encoding="utf-8")
    return tmp_path


def _onboarding(*, block_section: str = "current-state", payload: str = SV_PAYLOAD) -> str:
    """ONBOARDING.md text with the SV block in the named section.

    `block_section` is "current-state" (where sv actually writes it),
    "what-is" (a hypothetical future reorganisation), or "none".
    """
    block = f"{START}\n{payload}\n{END}"
    what_is = f"## What This Project Is\n\n{WHAT_IS_BODY}\n"
    if block_section == "what-is":
        what_is += f"\n{block}\n"
    current = "## Current State\n\nSome preamble.\n"
    if block_section == "current-state":
        current += f"\n{block}\n"
    return (
        "# CDSFL Project Onboarding\n\n"
        f"{what_is}\n"
        "## Standing Rules\n\nA rule.\n\n"
        f"{current}\n"
        "## Architecture Overview\n\nA tree.\n"
    )


# ---------------------------------------------------------------------------
# RULING 8 — search the whole file, splice from wherever the markers are
# ---------------------------------------------------------------------------

def test_block_is_found_outside_the_what_is_section(tmp_path):
    """The live arrangement: sv writes into '## Current State'.

    This is the exact input the pre-fix code silently dropped.
    """
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))
    block = ob.find_sv_block(root)
    assert block.status == ob.SV_OK, block.detail
    assert SV_PAYLOAD in block.text
    assert block.text.startswith(START)
    assert block.text.endswith(END)


def test_full_differs_from_and_contains_the_default_view(tmp_path):
    """The observable property. The old code failed this and reported OK."""
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))

    default_text, default_problems = ob.build_project_summary(root, full=False)
    full_text, full_problems = ob.build_project_summary(root, full=True)

    assert default_problems == []
    assert full_problems == []
    assert full_text != default_text
    assert default_text in full_text
    assert SV_PAYLOAD in full_text
    assert len(full_text) > len(default_text)


def test_default_view_never_carries_the_state_block(tmp_path):
    """Default stays the short overview, wherever the block lives."""
    for section in ("current-state", "what-is"):
        root = _write_root(tmp_path / section, onboarding=_onboarding(block_section=section))
        default_text, problems = ob.build_project_summary(root, full=False)
        assert problems == []
        assert WHAT_IS_BODY in default_text
        assert SV_PAYLOAD not in default_text, section
        assert START not in default_text, section


def test_splice_survives_the_block_moving_into_the_what_is_section(tmp_path):
    """The ruling's robustness claim: no dependence on which section holds it.

    And it must not double-print: read_onboarding_what_is strips the block
    wherever it falls, and build_project_summary re-attaches it exactly once.
    """
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="what-is"))

    block = ob.find_sv_block(root)
    assert block.status == ob.SV_OK, block.detail

    full_text, problems = ob.build_project_summary(root, full=True)
    assert problems == []
    assert full_text.count(SV_PAYLOAD) == 1
    assert full_text.count(START) == 1
    assert full_text.count(END) == 1
    assert WHAT_IS_BODY in full_text


def test_block_straddling_a_section_boundary_neither_leaks_nor_duplicates(tmp_path):
    """A block that OPENS in one section and CLOSES in the next.

    ONBOARDING.md is under concurrent edit, so this arrangement is reachable
    by an ordinary mistake. The default view must carry no fragment of the
    block, and --full must carry the block exactly once.
    """
    onboarding = (
        "# CDSFL Project Onboarding\n\n"
        f"## What This Project Is\n\n{WHAT_IS_BODY}\n\n{START}\n{SV_PAYLOAD}\n\n"
        f"## Current State\n\nmore state.\n{END}\n\n"
        "## Architecture Overview\n\nA tree.\n"
    )
    root = _write_root(tmp_path, onboarding=onboarding)

    default_text, _ = ob.build_project_summary(root, full=False)
    assert WHAT_IS_BODY in default_text
    assert START not in default_text
    assert SV_PAYLOAD not in default_text

    full_text, problems = ob.build_project_summary(root, full=True)
    assert problems == []
    assert full_text.count(START) == 1
    assert full_text.count(END) == 1
    assert full_text.count(SV_PAYLOAD) == 1
    assert default_text in full_text


def test_block_closing_in_the_what_is_section_leaves_no_tail(tmp_path):
    """Mirror case: the block opens earlier and closes inside the section."""
    onboarding = (
        "# CDSFL Project Onboarding\n\n"
        f"## Preamble\n\n{START}\n{SV_PAYLOAD}\n\n"
        f"## What This Project Is\n\nstill block text.\n{END}\n\n{WHAT_IS_BODY}\n\n"
        "## Architecture Overview\n\nA tree.\n"
    )
    root = _write_root(tmp_path, onboarding=onboarding)

    default_text, _ = ob.build_project_summary(root, full=False)
    assert default_text.strip() == WHAT_IS_BODY
    assert END not in default_text
    assert SV_PAYLOAD not in default_text

    full_text, problems = ob.build_project_summary(root, full=True)
    assert problems == []
    assert full_text.count(SV_PAYLOAD) == 1


def test_splice_does_not_depend_on_section_order(tmp_path):
    """Another agent is reorganising ONBOARDING.md concurrently.

    Reversing the section order must change nothing about the spliced block.
    """
    normal = _onboarding(block_section="current-state")
    head, _, tail = normal.partition("## Standing Rules")
    reordered = (
        "# CDSFL Project Onboarding\n\n"
        "## Standing Rules" + tail + "\n" + head.split("# CDSFL Project Onboarding", 1)[1]
    )
    root = _write_root(tmp_path, onboarding=reordered)

    block = ob.find_sv_block(root)
    assert block.status == ob.SV_OK, block.detail
    assert SV_PAYLOAD in block.text

    full_text, problems = ob.build_project_summary(root, full=True)
    assert problems == []
    assert SV_PAYLOAD in full_text
    assert WHAT_IS_BODY in full_text


# ---------------------------------------------------------------------------
# FAIL LOUDLY — a --full that cannot splice must never look like a success
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "mutate,expected_status",
    [
        (lambda t: t.replace(START, "").replace(END, ""), "no-markers"),
        (lambda t: t.replace(START, ""), "no-start"),
        (lambda t: t.replace(END, ""), "no-end"),
        (lambda t: t.replace(f"{START}\n{SV_PAYLOAD}\n{END}", f"{END}\n{SV_PAYLOAD}\n{START}"),
         "inverted"),
        (lambda t: t.replace(f"{START}\n{SV_PAYLOAD}\n{END}", f"{START}\n   \n{END}"), "empty"),
    ],
    ids=["no-markers", "no-start", "no-end", "inverted", "empty"],
)
def test_broken_marker_states_are_named_not_swallowed(tmp_path, mutate, expected_status):
    """Every failure mode reports WHICH one it is. '' with no reason is the disease."""
    root = _write_root(tmp_path, onboarding=mutate(_onboarding()))
    block = ob.find_sv_block(root)
    assert block.status == expected_status
    assert block.text == ""
    assert block.detail, "a failure with no explanation is exactly the defect being closed"


def test_two_marker_pairs_are_refused_not_silently_narrowed_to_the_first(tmp_path, capsys):
    """Found during adversarial verification, 2026-08-06.

    The search route has to CHOOSE which pair to splice, and before this it
    chose the first, printed it, and reported success — the second block
    vanished with no message. If the surviving block is the stale one, a
    recovering agent reads old state believing it is current. That is the same
    defect class as the 118-day no-op: a wrong answer rendered as a confident
    success. `cdsfl_sv.py` re-substitutes in place and never writes a second
    pair, so this arrives only by hand-editing ONBOARDING.md — which is a live
    hazard while that file is under concurrent edit.
    """
    block_two = "- **EXP 100:** the newer block, appended by hand."
    onboarding = (
        "# CDSFL Project Onboarding\n\n"
        f"## What This Project Is\n\n{WHAT_IS_BODY}\n\n"
        "## Current State\n\n"
        f"{START}\n{SV_PAYLOAD}\n{END}\n\n"
        f"{START}\n{block_two}\n{END}\n\n"
        "## Architecture Overview\n\nA tree.\n"
    )
    root = _write_root(tmp_path, onboarding=onboarding)

    block = ob.find_sv_block(root)
    assert block.status == "duplicate", (
        "a second marker pair was accepted; --full would print one block and "
        "drop the other without saying so"
    )
    assert block.text == ""
    assert "2 " in block.detail and "ONBOARDING.md" in block.detail

    full_text, problems = ob.build_project_summary(root, full=True)
    assert len(problems) == 1
    assert "duplicate" in problems[0]
    assert SV_PAYLOAD not in full_text and block_two not in full_text

    assert ob.dry_run(root) == 1
    assert "[FAIL]" in capsys.readouterr().out


def test_unreadable_onboarding_is_reported_not_silently_empty(tmp_path):
    root = tmp_path
    (root / "resources").mkdir()
    (root / "docs").mkdir()
    # A directory where the file should be: read_text raises OSError.
    (root / "resources" / "ONBOARDING.md").mkdir()
    block = ob.find_sv_block(root)
    assert block.status == "unreadable"
    assert block.text == ""
    assert block.detail


def test_full_without_markers_returns_default_plus_a_loud_problem(tmp_path):
    """The pre-fix behaviour minus the silence: same text, but SAID SO."""
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="none"))

    default_text, _ = ob.build_project_summary(root, full=False)
    full_text, problems = ob.build_project_summary(root, full=True)

    assert full_text == default_text
    assert len(problems) == 1
    assert "--full" in problems[0]
    assert "could NOT be spliced" in problems[0]
    assert "no-markers" in problems[0]


def test_print_project_summary_reports_failure_on_both_streams(tmp_path, capsys, monkeypatch):
    """The error must reach stdout, stderr AND the return value.

    latest_experiment / test_count are stubbed: the real test_count() shells
    out to pytest, which would recurse into this suite.
    """
    monkeypatch.setattr(ob, "latest_experiment", lambda: None)
    monkeypatch.setattr(ob, "test_count", lambda: None)
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="none"))

    ok = ob.print_project_summary(root, full=True)
    captured = capsys.readouterr()

    assert ok is False
    assert "[ERROR]" in captured.out
    assert "could NOT be spliced" in captured.out
    assert "could NOT be spliced" in captured.err


def test_print_project_summary_succeeds_and_grows_under_full(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(ob, "latest_experiment", lambda: None)
    monkeypatch.setattr(ob, "test_count", lambda: None)
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))

    assert ob.print_project_summary(root, full=False) is True
    default_out = capsys.readouterr().out
    assert ob.print_project_summary(root, full=True) is True
    full_out = capsys.readouterr().out

    assert "[ERROR]" not in full_out
    assert SV_PAYLOAD not in default_out
    assert SV_PAYLOAD in full_out
    assert len(full_out) > len(default_out)


# ---------------------------------------------------------------------------
# THE SELF-TEST MUST BE ABLE TO FAIL
# ---------------------------------------------------------------------------

def test_dry_run_passes_on_a_well_formed_tree(tmp_path, capsys):
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))
    rc = ob.dry_run(root)
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK" in out
    assert "[FAIL]" not in out


@pytest.mark.parametrize(
    "mutate",
    [
        lambda t: t.replace(START, "").replace(END, ""),
        lambda t: t.replace(START, ""),
        lambda t: t.replace(END, ""),
        lambda t: t.replace(f"{START}\n{SV_PAYLOAD}\n{END}", f"{START}\n   \n{END}"),
        lambda t: t.replace("## What This Project Is", "## Overview"),
    ],
    ids=["no-markers", "no-start", "no-end", "empty-block", "renamed-section"],
)
def test_dry_run_goes_red_on_broken_state(tmp_path, capsys, mutate):
    """Construct the broken state; the self-test MUST fail. This is the whole point.

    The pre-fix self-test returned 0 for every one of these except the two
    bare marker-presence cases, and returned 0 for the actual 118-day defect.
    """
    root = _write_root(tmp_path, onboarding=mutate(_onboarding()))
    rc = ob.dry_run(root)
    captured = capsys.readouterr()
    assert rc == 1
    assert "[FAIL]" in captured.out
    assert "FAIL" in captured.err


def test_dry_run_fails_when_reproducing_md_loses_its_mc_section(tmp_path, capsys):
    root = _write_root(
        tmp_path,
        onboarding=_onboarding(),
        reproducing="# Reproducing\n\n## Something Else\n\nnothing here.\n",
    )
    assert ob.dry_run(root) == 1
    assert "[FAIL]" in capsys.readouterr().out


def test_dry_run_would_have_caught_the_original_defect(tmp_path, capsys, monkeypatch):
    """The decisive falsification of the fix.

    Restore the pre-fix reader semantics — the marker search confined to the
    extracted section — and require the new self-test to go red. If it stays
    green here, the new check is as blind as the one it replaced and this
    whole repair is theatre.
    """
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))

    def section_scoped_find(r: Path) -> ob.SVBlock:
        """The old logic: search only inside '## What This Project Is'."""
        from cdsfl_utils import read_section
        content = read_section(
            r / "resources" / "ONBOARDING.md", "## What This Project Is", "\n## "
        )
        if content.find(START) == -1 or content.find(END) == -1:
            return ob.SVBlock("", "no-markers", "not in the extracted section")
        return ob.SVBlock(str(content), ob.SV_OK, "")

    assert ob.dry_run(root) == 0  # green with the search route
    capsys.readouterr()

    monkeypatch.setattr(ob, "find_sv_block", section_scoped_find)
    assert ob.dry_run(root) == 1, (
        "the self-test stayed green on the pre-fix marker search — it is still "
        "blind to the defect it was rewritten to catch"
    )
    assert "[FAIL]" in capsys.readouterr().out


def test_dry_run_asserts_the_property_not_merely_that_the_path_ran(tmp_path, capsys):
    """Directly pins the distinction the 118 days turned on.

    The marker pair is intact and locatable — so every other check is green —
    but `--full` returns exactly the default text. That is the no-op, and it
    is the state the old self-test called OK. A self-test that only records
    "the code path ran without raising" passes this; one that asserts the
    observable difference cannot.
    """
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))
    assert ob.find_sv_block(root).status == ob.SV_OK

    default_text, _ = ob.build_project_summary(root, full=False)
    # Simulate a --full that quietly hands back the default view.
    ob_build = ob.build_project_summary
    try:
        ob.build_project_summary = lambda r, full=False: (default_text, [])
        rc = ob.dry_run(root)
    finally:
        ob.build_project_summary = ob_build

    assert rc == 1, (
        "the self-test accepted a --full that returned the default view "
        "verbatim — it is asserting that the code ran, not what it produced"
    )
    out = capsys.readouterr().out
    assert "[FAIL] --full differs from, and contains, the default view" in out


def test_dry_run_prints_evidence_for_every_check_not_a_bare_ok(tmp_path, capsys):
    """A bare 'OK' is unauditable; that is how 118 days passed.

    Every check names itself and reports what it found.
    """
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))
    assert ob.dry_run(root) == 0
    out = capsys.readouterr().out

    assert out.count("[PASS]") >= 8, out
    assert "SV:LATEST_EXP marker pair" in out
    assert "--full differs from, and contains, the default view" in out
    assert "read_onboarding_what_is returns content" in out
    assert "read_reproducing_mc returns content" in out
    # Counts are the evidence: a check that reports no measurement proves nothing.
    assert "chars between the markers" in out
    assert "chars vs default" in out
    assert len(out.strip().splitlines()) >= 10


def test_dry_run_passes_against_the_live_repository(capsys):
    """End-to-end on the real tree.

    scripts/cdsfl_sv.py aborts a commit when this returns non-zero, so a red
    here is a real, blocking defect in resources/ONBOARDING.md or
    docs/REPRODUCING.md — not test flake.
    """
    rc = ob.dry_run(repo_root())
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "[FAIL]" not in out


# ---------------------------------------------------------------------------
# Credential roster and Wolfram reporting
# ---------------------------------------------------------------------------

def test_credential_roster_matches_the_authoritative_panel():
    """Roster of record: .claude/CLAUDE.md, mirrored by scripts/check_model_keys.py."""
    keys = ob.API_KEYS

    level, desc = keys["OPENROUTER_API_KEY"]
    assert level == "Required"
    for route in ("Codex", "ChatGPT", "Gemini"):
        assert route in desc, desc

    level, desc = keys["DEEPSEEK_API_KEY"]
    assert level == "Required"
    assert "deepseek-v4-pro" in desc
    assert "Reasoner" not in desc, "deepseek-reasoner is no longer listed by DeepSeek"

    level, desc = keys["GEMINI_API_KEY"]
    assert level == "Optional", "the panel has routed Gemini via OpenRouter since 2026-05-10"
    assert "OpenRouter" in desc

    assert keys["GOOGLE_API_KEY"][0] == "Optional"
    assert "ANTHROPIC_API_KEY" not in keys, "cc2 dispatches through the CLI, not an API key"
    assert not any("WOLFRAM" in k for k in keys), "Wolfram needs no key"


def test_uncredentialed_routes_are_named():
    joined = " ".join(ob.UNCREDENTIALED_ROUTES)
    assert "Max subscription" in joined
    assert "Wolfram" in joined
    assert "retired" in joined.lower()


def test_check_api_keys_never_prints_a_key_value(capsys, monkeypatch):
    """Presence only. A leaked value here would reach a terminal and a log."""
    sentinel = "sk-DO-NOT-PRINT-THIS-abcdef0123456789"
    monkeypatch.setattr(ob, "source_env", lambda: None)
    for key in ob.API_KEYS:
        monkeypatch.setenv(key, sentinel)

    ob.check_api_keys()
    captured = capsys.readouterr()

    assert sentinel not in captured.out
    assert sentinel not in captured.err
    for key in ob.API_KEYS:
        assert key in captured.out
    assert captured.out.count("[FOUND]") == len(ob.API_KEYS)


def test_wolfram_is_reported_retired_not_missing(capsys):
    ob.check_wolfram_mcp()
    out = capsys.readouterr().out
    assert "[RETIRED]" in out
    assert "2026-08-03" in out
    assert "[MISSING]" not in out, "a retired component is not a missing dependency"
    assert "www.wolfram.com" not in out, "do not send a reader to re-acquire the retired bridge"


# ---------------------------------------------------------------------------
# THE EXIT CODE ITSELF (added during adversarial verification, 2026-08-06)
# ---------------------------------------------------------------------------
# The module docstring of scripts/cdsfl_onboard.py asserts: "`--full` exits
# non-zero if the state block could not be spliced." Nothing pinned that. Every
# test above stops at `print_project_summary` returning False, and the wiring
# from that False to `main()`'s `return 1` — the only part a shell, a CI job or
# a wrapper script can see — was unexercised. Deleting `return 1` from main()
# left all 31 tests green (verified by mutation). An asserted property with no
# test is the shape of defect this whole repair round exists to close, so the
# claim is pinned here rather than left to the docstring.


def _neutralise_environment_checks(monkeypatch) -> None:
    """Stub everything in main() that touches the machine or prompts.

    `check_claude_code` can call `ask()` and shell out to `open`; `test_count`
    spawns pytest, which would recurse into this suite and is denied outright
    by the netguard. Only the summary path and the exit-code branch are left
    running for real.
    """
    monkeypatch.setattr(ob, "latest_experiment", lambda: None)
    monkeypatch.setattr(ob, "test_count", lambda: None)
    monkeypatch.setattr(ob, "check_python", lambda: True)
    monkeypatch.setattr(ob, "check_packages", lambda *a, **k: [])
    monkeypatch.setattr(ob, "check_system_tools", lambda: [])
    monkeypatch.setattr(ob, "check_claude_code", lambda: True)
    monkeypatch.setattr(ob, "check_wolfram_mcp", lambda: True)
    monkeypatch.setattr(ob, "check_api_keys", lambda: None)
    monkeypatch.setattr(ob, "print_structure", lambda root: None)
    monkeypatch.setattr(ob, "print_mc_commands", lambda root: None)


def test_main_returns_1_when_full_could_not_splice(tmp_path, capsys, monkeypatch):
    """The failure must reach the process exit status, not just the screen.

    A `--full` that cannot splice and still exits 0 is the 118-day defect with
    a warning printed over it.
    """
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="none"))
    _neutralise_environment_checks(monkeypatch)
    monkeypatch.setattr(ob, "repo_root", lambda: root)
    monkeypatch.setattr(sys, "argv", ["cdsfl_onboard.py", "--full"])

    rc = ob.main()
    captured = capsys.readouterr()

    assert rc == 1, "a --full run that could not deliver the block reported success"
    assert "could NOT be spliced" in captured.out
    assert "INCOMPLETE" in captured.out, "the error must be repeated where the run ends"
    assert "could NOT be spliced" in captured.err


def test_main_returns_0_and_prints_the_block_when_full_succeeds(tmp_path, capsys, monkeypatch):
    """The mirror: a healthy tree must not be turned red by the new exit path."""
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))
    _neutralise_environment_checks(monkeypatch)
    monkeypatch.setattr(ob, "repo_root", lambda: root)
    monkeypatch.setattr(sys, "argv", ["cdsfl_onboard.py", "--full"])

    rc = ob.main()
    out = capsys.readouterr().out

    assert rc == 0, out
    assert SV_PAYLOAD in out
    assert "[ERROR]" not in out


def test_main_default_view_is_unaffected_by_the_new_exit_path(tmp_path, capsys, monkeypatch):
    """No `--full`, no block, no error, exit 0 — the ordinary first-contact run."""
    root = _write_root(tmp_path, onboarding=_onboarding(block_section="current-state"))
    _neutralise_environment_checks(monkeypatch)
    monkeypatch.setattr(ob, "repo_root", lambda: root)
    monkeypatch.setattr(sys, "argv", ["cdsfl_onboard.py"])

    rc = ob.main()
    out = capsys.readouterr().out

    assert rc == 0, out
    assert WHAT_IS_BODY in out
    assert SV_PAYLOAD not in out
    assert "[ERROR]" not in out
