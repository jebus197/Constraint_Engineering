"""Task B23: every piece of work since the outset is in the register.

HIS INSTRUCTION, 2026-10-17: *"I feel I should have been more explicit in my
instructions when I told you to build your Bugzilla registry, and should have
told you to fully populate it with everything that had been done up until then,
from the outset of the project."*

THE UNIT IS A COMMIT. It is the project's own record of a discrete piece of
work: its own text, its own date, a stable identifier, and it cannot be
invented after the fact. Finer (a hunk) multiplies rows without adding an
answerable question; coarser (a day) merges work that was separately decided.

EVERY BACKFILLED TICKET IS ANCHORED BY ITS SHA, and that is load-bearing rather
than tidy. The register's subject tier DECIDES: a proposal sharing one code
identifier with a settled ticket is handed that ticket instead of being raised,
and a backfill arriving without anchors would have been absorbed wholesale --
measured at 118 of 181 subject-carrying tickets absorbed by a ticket sharing
NEITHER their words NOR their hash, 65.1934% Wilson [58.0031%, 71.7521%].
`_distinct` is the designed escape hatch, and the backfill uses it.

THE COMPLETENESS TEST TOLERATES NEW COMMITS WITHOUT TOLERATING HOLES. Commits
made after the backfill ran obviously have no ticket yet, and a test demanding
otherwise would be red from the next commit onward and would then be disabled.
So the rule is: every commit OLDER THAN THE NEWEST ANCHORED ONE must itself be
anchored. That is exact about the covered span and silent about the trailing
edge, and it still fails on a hole anywhere inside the history.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PRODUCER = REPO / "scripts" / "backfill_the_register_from_history_2026-10-17.py"


def _producer():
    spec = importlib.util.spec_from_file_location("_bf", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def state():
    if not (REPO / ".git").exists():
        pytest.skip("not a git checkout")
    from bench.ticket_store import TicketStore
    store = TicketStore()
    store.load()
    order = subprocess.run(["git", "log", "--reverse", "--format=%H"],
                           capture_output=True, text=True,
                           cwd=str(REPO)).stdout.split()
    if not order:
        pytest.skip("no commits")
    anchored = {t.anchor[len("commit:"):]: t for t in store.all()
                if t.anchor.startswith("commit:")}
    return {"store": store, "order": order, "anchored": anchored}


def test_the_backfill_has_run_at_all(state):
    assert state["anchored"], (
        "no ticket is anchored to a commit, so the history has never been "
        "backfilled and his instruction is unfulfilled")


def test_every_commit_older_than_the_newest_anchored_one_is_anchored(state):
    """THE COMPLETENESS ASSERTION, exact about the covered span."""
    order, anchored = state["order"], state["anchored"]
    positions = [i for i, sha in enumerate(order) if sha in anchored]
    assert positions, "nothing anchored; completeness is untestable"
    newest = max(positions)
    holes = [sha for sha in order[:newest + 1] if sha not in anchored]
    assert not holes, (
        f"{len(holes)} commit(s) inside the backfilled span have no register "
        f"ticket: {[h[:10] for h in holes[:5]]}. The backfill has a hole, so "
        f"'everything that had been done' is not in the register.")
    covered = newest + 1
    assert covered > 100, (
        f"only {covered} commits are covered; that is not the project's "
        f"history and the figure quoted for it would be wrong")


def test_every_backfilled_ticket_is_closed(state):
    """The work was done. A backfilled row left OPEN would appear in the
    outstanding-work queue and ask him to do what is already finished."""
    from bench.ticket_store import LIVE
    live = [t for t in state["anchored"].values() if t.status in LIVE]
    assert not live, (
        f"{len(live)} backfilled commits are recorded as LIVE work: "
        f"{[t.tid for t in live[:5]]}. Each would present finished work as "
        f"outstanding.")


def test_each_backfilled_ticket_names_its_commit_as_verification(state):
    missing = [t.tid for t in state["anchored"].values()
               if "commit " not in (t.verification or "")]
    assert not missing, (
        f"{len(missing)} backfilled tickets do not name the commit that "
        f"settles them: {missing[:5]}")


def test_the_kind_rule_is_stated_and_is_what_was_applied(state):
    """A heuristic is acceptable; an UNDOCUMENTED heuristic is not. This
    executes the rule and compares it to what is stored, so the two cannot
    drift."""
    mod = _producer()
    assert mod.ADDITIVE_VERBS, "the rule has no verbs, so it classifies nothing"
    wrong = []
    for sha, ticket in state["anchored"].items():
        subject = ticket.title
        expected = mod.kind_of(subject)
        if ticket.kind != expected:
            wrong.append((sha[:10], subject[:40], ticket.kind, expected))
    assert not wrong, (
        f"{len(wrong)} backfilled tickets carry a kind the stated rule does "
        f"not produce: {wrong[:4]}. Either the rule changed without the rows "
        f"being re-derived, or the rows were classified by something else.")


def test_each_backfilled_ticket_says_its_kind_came_from_a_rule(state):
    """So nobody mistakes a crude heuristic for someone's judgement."""
    sample = list(state["anchored"].values())[:40]
    silent = [t.tid for t in sample
              if "stated first-word rule" not in (t.verbatim or "")]
    assert not silent, (
        f"{len(silent)} of {len(sample)} sampled backfilled tickets do not "
        f"record that their kind came from a rule: {silent[:4]}")


def test_rerunning_the_backfill_would_add_nothing(state):
    """IDEMPOTENCE, checked against the live store rather than a marker file.
    The parked-file generator wrote 28 marks for 14 items on this same day by
    failing exactly this property."""
    mod = _producer()
    rows = mod.commits()
    already = {f"commit:{sha}" for sha in state["anchored"]}
    todo = [r for r in rows if f"commit:{r['sha']}" not in already]
    trailing = [r for r in todo
                if state["order"].index(r["sha"]) > max(
                    i for i, s in enumerate(state["order"])
                    if s in state["anchored"])]
    assert len(todo) == len(trailing), (
        f"a re-run would raise {len(todo)} rows of which only "
        f"{len(trailing)} are newer than the backfill, so "
        f"{len(todo) - len(trailing)} already-covered commits would be "
        f"duplicated")


def test_the_producer_defaults_to_a_dry_run():
    """A script that writes 1,701 rows on a bare invocation is a trap."""
    src = PRODUCER.read_text(encoding="utf-8")
    assert '"--apply"' in src and "action=\"store_true\"" in src
    out = subprocess.run([sys.executable, str(PRODUCER), "--limit", "3"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert out.returncode == 0, out.stderr[-300:]
    assert "DRY RUN" in out.stdout, (
        "a bare invocation did not announce a dry run, so it may have written")


def test_the_producer_refuses_an_unknown_flag():
    out = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert out.returncode != 0
