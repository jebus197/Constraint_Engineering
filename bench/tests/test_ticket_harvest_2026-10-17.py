"""The harvester must not over-block, which is worse than not existing.

WHY. A first version of `subjects_in` harvested every identifier it saw,
including file paths. Measured over the 104 master-task-list candidates on
2026-10-17: 424 subject mentions across 343 distinct subjects, 49 of them test
files or globs (14.2857%, Wilson [10.9774%, 18.3851%]), and
`CDSFL_MASTER_TASK_LIST.md` appeared on 20 separate tickets. Closing any 1 of
those 20 would have made the other 19 unraisable.

That is OVER-BLOCKING, and it is strictly worse than having no store: a store
that refuses everything stops real work, whereas no store merely fails to stop
rediscovery. So the narrowing is load-bearing and is pinned here.

THE RULE: a subject must be specific enough to be WRONG about. A file is not --
`reference_runner_v3.py` holds 21,000 lines and a dozen unrelated mechanisms. A
callable or a config key is.
"""
from __future__ import annotations

import collections
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "harvest_tickets", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)


@pytest.mark.parametrize("tok", [
    "_load_fingerprints",
    "routing.rank_falsifier_writers",
    "apply_fixes_back_enabled",
    "exhausted_round_threshold",
    "GAMMA_BANDS",
    "unverified_critical_count",
])
def test_a_callable_or_config_key_is_a_valid_subject(tok):
    assert H._is_blocking_subject(tok), f"{tok!r} should qualify as a subject"


@pytest.mark.parametrize("tok", [
    "bench/reference_runner_v3.py",
    "reference_runner_v3.py",
    "CDSFL_MASTER_TASK_LIST.md",
    "bench/tests/test_done_markers_carry_evidence_2026-09-10.py",
    "panel_*",
    "experimental_notes/evidence/panel_records_*",
    ".git",
    "../",
    "two words",
])
def test_a_file_glob_or_phrase_is_not_a_subject(tok):
    assert not H._is_blocking_subject(tok), (
        f"{tok!r} must NOT be a blocking subject: it is too coarse, so a settled "
        "ticket on it would block unrelated work on the same file")


def test_subjects_are_capped_so_one_entry_cannot_blanket_the_index():
    text = " ".join(f"`mod_{i}.fn_{i}`" for i in range(12))
    assert len(H.subjects_in(text)) <= 3, (
        "an entry naming many mechanisms is a summary, and a summary must not "
        "claim the whole subject index")


def test_the_real_task_list_yields_no_coarse_subject():
    rows = H.from_task_list()
    assert rows, "the task list must yield candidates, or this test is vacuous"
    subs = [s for r in rows for s in r["subjects"]]
    coarse = [s for s in subs
              if s.endswith((".py", ".md", ".json", ".toml", ".txt"))
              or "/" in s or "*" in s]
    assert not coarse, f"coarse subjects present: {sorted(set(coarse))[:6]}"


def test_no_single_subject_dominates_the_real_task_list():
    """The 20-ticket case must not return. 6 is generous and still safe."""
    rows = H.from_task_list()
    c = collections.Counter(s for r in rows for s in r["subjects"])
    if not c:
        pytest.skip("no subjects extracted")
    subject, count = c.most_common(1)[0]
    assert count <= 6, (
        f"{subject!r} is shared by {count} tickets. Closing 1 would make the "
        f"other {count - 1} unraisable, which is the over-blocking defect "
        "measured on 2026-10-17 when this figure was 20.")


def test_an_entry_may_honestly_have_no_subject():
    rows = H.from_task_list()
    without = [r for r in rows if not r["subjects"]]
    assert without, (
        "if every entry carries a subject the extractor is guessing; an entry "
        "that names no mechanism should fall back to the text tiers")


def test_the_marker_is_strict_enough_to_avoid_noise():
    assert H.marked_kind("fr: add a shadow arm") == "fr"
    assert H.marked_kind("pf: the loader ignores scope") == "pf"
    assert H.marked_kind("[fr] a new facility") == "fr"
    for noise in ("the panel review found 3 defects",
                  "a free run converged",
                  "prefer the simplest fix",
                  "from the fringe of the distribution"):
        assert H.marked_kind(noise) is None, f"marker fired on noise: {noise!r}"


def test_his_panel_review_command_is_never_harvested_as_a_proposal():
    """THE COLLISION THAT FORCED `pf`, pinned so it cannot be reintroduced.

    He proposed `pr` for the proposed-fix marker on 2026-10-17. His own command
    list already defines `pr` as a full panel review and he uses it constantly to
    order a round. Measured before the change, 4 of 4 of his real usages were
    harvested as proposed fixes, which would have turned every panel order into a
    ticket. These are those 4 usages, and none may produce a kind.
    """
    for usage in ("a, f, sy, d\n\npr",
                  "pr",
                  "pr: run the full panel on the outstanding issues",
                  "Put it to the panel. pr",
                  "pr on the outstanding questions"):
        assert H.marked_kind(usage) is None, (
            f"his panel-review command {usage!r} was harvested as a proposal; "
            "`pr` belongs to the panel and must never be a ticket marker")


def test_both_sections_are_produced_from_the_real_record():
    rows = H.from_task_list()
    kinds = {r["kind"] for r in rows}
    assert kinds <= {"fr", "pf"}, f"unexpected kinds: {kinds}"
    assert "pf" in kinds, "the proposed-fix section must be populated"


def test_every_task_list_entry_reaches_the_store():
    """A coverage RATCHET. The gap was 33.3333% and is now 0.

    Measured on 2026-10-17 as the harvester was built. A heading-driven rule
    missed 47 of 141 entries, 33.3333%, Wilson [26.0856%, 41.4651%], for 3
    independent reasons no single example would have shown: numeric entries carry
    no dot after the identifier, some entries bold the identifier alone with the
    title outside the bold span, and several entries SHARE one paragraph block so
    no paragraph-level rule can separate them. Driving extraction off the HTML
    markers instead -- which `task_list_markers.parse_entries` already handles,
    since it is what reports 141 -- closed the gap to 0 of 141.

    A silent third of the record missing is the exact failure this store exists
    to stop, so it is a test rather than a comment.
    """
    import sys as _sys
    REPO_ = pathlib.Path(__file__).resolve().parents[2]
    _sys.path.insert(0, str(REPO_ / "scripts"))
    import task_list_markers as tlm
    tasklist = REPO_ / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
    entries = {e.ident for e in tlm.parse_entries(tasklist)}
    harvested = {r["task_ref"] for r in H.from_task_list() if r.get("task_ref")}
    missing = sorted(entries - harvested)
    assert not missing, (
        f"{len(missing)} of {len(entries)} task-list entries never reach the "
        f"ticket store: {missing[:10]}. A silent gap here means the store "
        "under-reports outstanding work, which is how a settled issue gets "
        "rediscovered in the first place.")


def test_each_harvested_entry_carries_substantive_text():
    """An entry whose verbatim text is empty cannot be recognised by a human,
    and a human read is the only reliable settler of identity."""
    thin = [r["task_ref"] for r in H.from_task_list()
            if len(r["verbatim"].strip()) < 20]
    assert not thin, f"{len(thin)} entries harvested with no usable text: {thin[:8]}"


def test_the_seeded_store_holds_three_integrity_properties():
    """The 3 ways the store could lie, checked against the live task list.

    Each was a REAL defect found on 2026-10-17 while building it:

    1. COVERAGE. A heading-driven harvest missed 47 of 141 entries, 33.3333%,
       Wilson [26.0856%, 41.4651%]. A store missing a third of the record
       under-reports outstanding work.
    2. OVER-MERGING. 3 settled tickets concealed 5 OPEN task entries, because
       subject and text similarity were allowed to outrank an explicit task
       reference. A hidden open item is worse than a rediscovery: the work is
       never done and the store says it is.
    3. DESTRUCTION. Fixing 2 naively made it worse. The ticket identity was a
       digest of kind and text only, so 2 distinct entries worded identically
       produced the SAME id and the second OVERWROTE the first -- which was
       CLOSED, so a closed record was deleted by a later open one. The task
       reference is now part of the identity.
    """
    import sys as _sys
    REPO_ = pathlib.Path(__file__).resolve().parents[2]
    _sys.path.insert(0, str(REPO_))
    _sys.path.insert(0, str(REPO_ / "scripts"))
    from bench.ticket_store import TicketStore, TERMINAL, REJECTED
    import task_list_markers as tlm

    store_path = REPO_ / "bench" / "tickets" / "tickets.jsonl"
    if not store_path.is_file():
        pytest.skip("the ticket store is not populated in this checkout")
    store = TicketStore(store_path)
    entries = tlm.parse_entries(REPO_ / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    idents = {e.ident for e in entries}
    open_idents = [e.ident for e in entries if e.state == "OPEN"]

    missing = sorted(i for i in idents if not store.by_task_ref(i))
    assert not missing, f"1. coverage: {len(missing)} entries absent: {missing[:8]}"

    hidden = store.settled_with_open_aliases(open_idents)
    assert not hidden, (
        "2. over-merging: settled tickets conceal open work: "
        + ", ".join(f"{t.tid} hides {r}" for t, r in hidden[:4]))

    settled_states = TERMINAL | {REJECTED}
    unsettled_done = []
    for e in entries:
        if e.state != "DONE":
            continue
        tks = store.by_task_ref(e.ident)
        if tks and not any(t.status in settled_states for t in tks):
            unsettled_done.append(e.ident)
    assert not unsettled_done, (
        "3. a DONE task whose ticket is not settled means a closed record was "
        f"overwritten by a later one: {unsettled_done[:8]}")
