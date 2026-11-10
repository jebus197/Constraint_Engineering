"""His instruction, twice: an entry code printed to him must carry a descriptor.

HIS WORDS, 2026-11-10, verbatim: *"I can't always tell when you print
identifiers like B102 or C0003 (for example), if these are the same issues you
may have been discussing a few lines ago. I don't have access to your ticket
store, or any of the other resources you have to store these issues. Nor do I
have your ability to quickly look them up. I already asked you when you print
these labels, to include a short descriptor, so I can know what you are talking
about."*

WHY A GUARD AND NOT A RESOLUTION. Note standard Rule 32 already states this and
`scripts/note_vagueness_lint.py` already implements the predicate -- the gap is
SCOPE: Rule 32 is scoped to delivered DOCUMENTS, so it has never been applied to
chat. Measured over every assistant text block in the session transcripts,
**8288 of 10496 codes printed with no descriptor, 0.789634**, Wilson
[0.781732, 0.797325]. His own `no-word-numbers` ruling settles what restating a
rule is worth: *"The failure was never the absence of a rule or a checker; it
was never running the checker."*

SO THE REPAIR IS AVAILABILITY. `scripts/task_list_markers.py:open_roster` emits
every OPEN entry as `CODE descriptor` and `hooks/task_list_pulse.py` injects it
into every turn, so printing a descriptor costs nothing. These tests EXECUTE
both -- the roster function and the hook as the harness runs it -- rather than
asserting on their source, because a source assertion proves only that a module
describes itself consistently.

THE STRONGEST TEST HERE is `test_the_roster_satisfies_rule_32_itself`: it feeds
each roster row through the note lint's OWN predicate and requires 0 bare
codes. If the roster did not actually satisfy the rule it exists to serve, every
other assertion in this file would be beside the point.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import note_vagueness_lint as nvl      # noqa: E402 -- the EXISTING predicate
import task_list_markers as tlm        # noqa: E402

LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
HOOK = REPO / "hooks" / "task_list_pulse.py"


@pytest.fixture(scope="module")
def roster() -> str:
    return tlm.open_roster(LIST)


@pytest.fixture(scope="module")
def opens() -> list:
    return [e for e in tlm.parse_entries(LIST) if e.state == "OPEN"]


# ── the roster covers what it must, and nothing it must not ────────────────

def test_every_open_entry_is_in_the_roster(roster, opens):
    assert opens, "the task list reports 0 open entries; nothing to assert"
    missing = [e.ident for e in opens if f"{e.ident} " not in roster]
    assert not missing, f"open entries absent from the roster: {missing}"


def test_every_roster_row_carries_a_nonempty_descriptor(roster, opens):
    rows = dict(r.split(" ", 1) for r in roster.split("; ") if " " in r)
    thin = {k: v for k, v in rows.items() if len(v.strip()) < 8}
    assert not thin, f"these rows carry no usable descriptor: {thin}"
    assert len(rows) == len(opens), (len(rows), len(opens))


def test_a_closed_entry_is_not_in_the_roster(roster):
    done = [e.ident for e in tlm.parse_entries(LIST) if e.state == "DONE"]
    assert done, "no DONE entries, so this test would be vacuous"
    leaked = [d for d in done if f"{d} " in roster]
    assert not leaked, f"closed entries in the open roster: {leaked[:6]}"


def test_the_descriptor_comes_from_the_entrys_own_title(opens):
    """A generic string would pass the emptiness test and fail this one."""
    for e in opens[:8]:
        d = tlm.entry_descriptor(e.text)
        title_words = nvl._subject_words(e.text[:400])
        assert nvl._subject_words(d) & title_words, (
            f"{e.ident}'s descriptor {d!r} shares no content word with its "
            f"own title")


# ── the property the whole thing exists for ────────────────────────────────

def test_the_roster_satisfies_rule_32_itself(roster):
    """Feed each row through the note lint's OWN predicate: 0 bare codes."""
    subjects = nvl.entry_subjects()
    assert subjects, "the predicate has no subjects, so a 0 here is a false 0"
    bare = []
    for row in roster.split("; "):
        for im in nvl._ENTRY_IDENT.finditer(row):
            subj = subjects.get(im.group(1))
            if subj and not (subj & nvl._subject_words(row)):
                bare.append(row)
    assert not bare, f"the roster itself breaks Rule 32: {bare[:4]}"


def test_the_predicate_can_still_fail(roster):
    """ANTI-VACUITY. A bare code must be detected, or the test above is empty."""
    subjects = nvl.entry_subjects()
    ident = next(iter(roster.split("; "))).split(" ", 1)[0]
    assert ident in subjects, ident
    probe = f"Proceeding with {ident} next."
    hits = [im.group(1) for im in nvl._ENTRY_IDENT.finditer(probe)
            if subjects.get(im.group(1))
            and not (subjects[im.group(1)] & nvl._subject_words(probe))]
    assert ident in hits, (
        f"the predicate did not flag the bare probe {probe!r}, so "
        f"test_the_roster_satisfies_rule_32_itself cannot fail")


# ── the dangling-word trim ─────────────────────────────────────────────────

def test_a_descriptor_does_not_end_on_a_dangling_word():
    got = tlm.entry_descriptor(
        "**B99. What a fix means outside code, and whether this is yet a "
        "general-purpose thing.** body")
    assert got, got
    assert got.rstrip(".,;:").lower().split()[-1] not in {
        "and", "whether", "this", "the", "a", "of", "is"}, got


def test_the_word_budget_is_honoured():
    long = "**B98. " + " ".join(f"word{i}" for i in range(40)) + ".** body"
    got = tlm.entry_descriptor(long, words=5)
    assert len(got.split()) <= 5, got


# ── the hook, executed exactly as the harness executes it ──────────────────

def _run_hook(cwd: Path):
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"session_id": "t", "cwd": str(cwd)}),
        capture_output=True, text=True, timeout=120, cwd=str(cwd))


def test_the_hook_emits_the_roster_and_keeps_its_prefix():
    r = _run_hook(REPO)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    # the pre-existing contract, asserted by the 2026-09-09 guard
    assert ctx.startswith("[tasks] "), ctx
    assert "\n[entries] " in ctx, (
        "the roster line is absent from the injected context")
    for e in [x for x in tlm.parse_entries(LIST) if x.state == "OPEN"][:5]:
        assert f"{e.ident} " in ctx, f"{e.ident} missing from the context"


def test_the_hook_still_exits_zero_where_there_is_no_task_list(tmp_path):
    """MUST ALWAYS EXIT 0 -- a hook that blocks a prompt is worse than a
    missing line, which is the hook's own stated contract."""
    r = _run_hook(tmp_path)
    assert r.returncode == 0, r.stderr


def test_the_roster_is_bounded_so_it_cannot_flood_the_turn(roster):
    assert len(roster) < 4000, (
        f"the roster is {len(roster)} characters; it is injected on EVERY "
        f"turn, so it must stay small")


# ── the producer the measurement comes from ────────────────────────────────

def test_the_producer_exists_and_its_help_is_free():
    prod = REPO / "scripts" / "a_bare_entry_code_in_chat_2026-11-10.py"
    assert prod.is_file(), prod
    r = subprocess.run([sys.executable, str(prod), "--help"],
                       capture_output=True, text=True, timeout=30,
                       cwd=str(REPO))
    assert r.returncode == 0, r.stderr


def test_the_producers_interval_helper_honours_the_reserved_contract():
    """`_iv(k, n)` is a project-wide contract; a local formatter under that
    name has broken it 3 times. Call it and check the SHAPE."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "bec", REPO / "scripts" / "a_bare_entry_code_in_chat_2026-11-10.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    (wlo, whi), (clo, chi), cross = m._iv(6, 9)
    assert 0.0 <= wlo < whi <= 1.0, (wlo, whi)
    assert 0.0 <= clo < chi <= 1.0, (clo, chi)
    assert cross < 1e-9, f"the 2 interval routes disagree by {cross}"
    assert clo < wlo and chi > whi, (
        "Clopper-Pearson must be wider than Wilson here")
