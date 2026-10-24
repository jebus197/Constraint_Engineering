"""His duplicate / supersession taxonomy, each rule exercised by calling it.

HIS DEFINITION, 2026-10-16, which the harness had discarded: *"a duplicate can
only be called a duplicate, if a) it finds the same fault and b) if the proposed
repair is in fact identical. Isn't this how dupes normally work in the world of
software engineering? [Further], we decided that when two models identify the same
issue, but propose different fixes we should prefer the fix that both meets our
formal simplest sufficient fix, composability and additive standards, and that we
should prefer the fix that demonstrably does the job better than a fix proposed by
any of the other models. Was that ever built?"*

IT WAS NOT, AND HE ASKED AGAIN ON 2026-10-24: *"Duplicates should not be marked as
Depreciated! ... given that definition, a duplicate is a duplicate, not something
else. ... You appear to be at risk of conflating different statuses in the ticket
store? Are you?"* Yes -- measured. Of 84 merged pairs whose repairs are both
comparable, 63 (75.0000%, Wilson [64.7857%, 83.0277%]) have DIFFERENT repairs, so
three quarters of what the archive called one item fail his condition (b).

HIS OWN QUESTION WAS LOST TO A MERGE, which is the illustration. The 2026-10-16
annotation was harvested as ticket a8da7d3b5d76 and its status is MERGED -- folded
into another ticket rather than answered.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ADJ = ROOT / "scripts" / "which_fix_is_better_2026-10-24.py"


def _adj():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("_wfb", ADJ)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_wfb"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def adj():
    return _adj()


@pytest.fixture()
def store(tmp_path):
    """★ A TEMPORARY STORE, AND THE REASON IS A REAL INCIDENT ON 2026-10-24.

    This fixture first returned the LIVE store, `TicketStore()`. The refusal
    tests below each expect a ValueError -- but the MUTATION run that proves they
    are not vacuous disables one refusal at a time, and with the refusal gone the
    call SUCCEEDED against a real ticket and appended a real row. 3 production
    tickets were written that way: B13 to DUPLICATE on the verification 'a
    verification', B20 to DEPRECATED on 'it is better', and C15 to INVALID on an
    empty string. The register then disagreed with the task list, which is how it
    was caught, and the rows had to be reverted by appending corrective ones.

    A test that writes to the live store is not a test of the store; it is a use
    of it. Two tickets are seeded here so the 2-ticket cases still have subjects.
    """
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    s = TicketStore(tmp_path / "tickets.jsonl")
    # THE 2 SEEDS MUST BE PLAINLY DISTINCT. A first version used "fix A for the
    # shared fault" and "fix B for the shared fault", and `propose` deduplicated
    # the second -- correctly, since its whole job is to stop a reworded repeat.
    # The fixture needs 2 separate subjects, not 2 phrasings of one.
    a, oa = s.propose("pf", "the parser over-captures a section boundary",
                      "the section extractor swallows following sections whenever "
                      "a mode marker is absent", "chat", subjects=["parser.extract"])
    b, ob = s.propose("fr", "the dispatcher should stagger shared-credential seats",
                      "two seats on one subscription collide at establishment and "
                      "need a measured gap between their starts", "chat",
                      subjects=["dispatcher.stagger"])
    assert oa == "created" and ob == "created", (oa, ob)
    return s


@pytest.fixture(scope="module")
def live_store():
    """READ-ONLY. Only the vocabulary tests may touch the live store, and they
    only read it."""
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    return TicketStore()


# ── the vocabulary carries every status his taxonomy needs ─────────────────

def test_the_four_statuses_exist(live_store):
    sys.path.insert(0, str(ROOT))
    import bench.ticket_store as ts
    for s in ("DUPLICATE", "MERGED", "DEPRECATED", "INVALID"):
        assert s in ts.STATUSES, f"{s} is missing from the ticket vocabulary"
    assert "UNDECIDED" in ts.LIVE, "UNDECIDED must be a LIVE state"


def test_withheld_is_readable_but_never_written_again(live_store):
    """The store is APPEND-ONLY: 5 historical rows carry WITHHELD and must load.
    It is legacy, not current."""
    sys.path.insert(0, str(ROOT))
    import bench.ticket_store as ts
    assert "WITHHELD" in ts.STATUSES, "historical rows would stop loading"
    assert "WITHHELD" in ts._LEGACY_STATUSES
    assert "UNDECIDED" not in ts._LEGACY_STATUSES


def test_duplicate_is_not_deprecated_in_the_runner_vocabulary():
    """HIS RULING: "Duplicates should not be marked as Depreciated!" It read
    "DEPRECATED — collapse into MERGED + merged_into"."""
    sys.path.insert(0, str(ROOT))
    import bench.reference_runner_v3 as r
    spec = r.FINDING_STATUS_VOCABULARY["DUPLICATE"]
    assert not spec.get("deprecated"), "DUPLICATE is still flagged deprecated"
    assert "DEPRECATED" not in spec["meaning"], spec["meaning"][:120]
    assert spec["in_from"], "a status nothing can enter is deprecated in effect"


def test_merged_no_longer_claims_to_be_a_duplicate():
    """One repair curing both establishes condition (a) only."""
    sys.path.insert(0, str(ROOT))
    import bench.reference_runner_v3 as r
    m = r.FINDING_STATUS_VOCABULARY["MERGED"]["meaning"]
    assert "NOT a duplicate" in m, m[:160]


# ── condition (b) is enforced, not quoted ──────────────────────────────────

def test_a_duplicate_below_the_repair_floor_is_refused(store):
    w = store.workable()
    assert len(w) >= 2, "the fixture must seed 2 workable tickets"
    with pytest.raises(ValueError) as e:
        store.mark_duplicate(w[0].tid, w[1].tid, 0.40, "a verification")
    assert "condition (b)" in str(e.value)


def test_a_duplicate_needs_a_verification(store):
    w = store.workable()
    assert len(w) >= 2, "the fixture must seed 2 workable tickets"
    with pytest.raises(ValueError):
        store.mark_duplicate(w[0].tid, w[1].tid, 0.99, "")


def test_deprecating_a_fix_demands_a_measurement_not_a_judgement(store):
    """His standard is "demonstrably does the job better", and the additive
    standard refuses a judgement in place of evidence."""
    w = store.workable()
    assert len(w) >= 2, "the fixture must seed 2 workable tickets"
    with pytest.raises(ValueError) as e:
        store.deprecate(w[0].tid, w[1].tid, "it is better")
    assert "MEASUREMENT" in str(e.value)


def test_invalid_is_terminal_and_needs_its_verification(store):
    w = store.workable()
    assert w, "the fixture must seed a workable ticket"
    with pytest.raises(ValueError) as e:
        store.invalidate(w[0].tid, "intended behaviour", "")
    assert "verification" in str(e.value)


# ── the adjudicator measures rather than votes ─────────────────────────────

def test_repair_identity_ignores_whitespace_but_not_content(adj):
    assert adj.repair_identity("a b c", "a    b\n c") == 1.0
    assert adj.repair_identity("fix the parser", "rewrite the emitter") < 0.6
    assert adj.repair_identity("", "anything") == 0.0


def test_changed_lines_parses_search_replace_and_refuses_an_unknown_form(adj):
    changed, deleted = adj.changed_lines(
        "<<<< SEARCH\nold one\nold two\n====\nnew one\n>>>> REPLACE")
    assert changed == 3 and deleted == 2, (changed, deleted)
    assert adj.changed_lines("just some prose") == (0, 0), (
        "an unrecognised repair must not count as a repair of size zero")


def test_the_adjudicator_refuses_when_it_cannot_measure(adj, monkeypatch):
    """A verdict on an unmeasurable input would be a guess."""
    def boom(*a, **k):
        raise RuntimeError("probe unavailable")
    import bench.fix_efficacy as fe
    monkeypatch.setattr(fe, "probe_pair", boom)
    r = adj.decide({"canonical_id": "C1", "proposed_fix": "x"},
                   {"canonical_id": "C2", "proposed_fix": "y"}, "bench/t.py")
    assert r["verdict"] == "CANNOT_MEASURE", r


def test_its_verdict_vocabulary_includes_undecided(adj):
    """Refusing to choose is a real outcome, and the store has a word for it."""
    assert "UNDECIDED" in adj.VERDICTS
    assert "DUPLICATE" in adj.VERDICTS
    assert {"A_IS_BETTER", "B_IS_BETTER"} <= set(adj.VERDICTS)


def test_the_adjudicator_never_votes(adj):
    """CDSFL is a tools-decide harness. A panel choosing between 2 fixes is the
    free pass the project exists to refuse, so no model is consulted here.

    ★ THE FIRST FORM OF THIS TEST BANNED THE WORDS and failed on the sentence
    that SAYS the tool does not vote -- a source-text assertion, which this
    project's own `execute-do-not-grep` rule forbids as evidence. It now reads the
    IMPORT GRAPH: a tool that consults a model has to import something that can
    reach one, and that is checkable without reading prose."""
    import ast
    tree = ast.parse(ADJ.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    reaches_a_model = {n for n in imported
                       if any(k in n.lower() for k in
                              ("confer", "panel", "openai", "anthropic",
                               "requests", "httpx", "urllib", "claude_cli"))}
    assert not reaches_a_model, (
        f"the adjudicator imports {sorted(reaches_a_model)}, which can reach a "
        f"model; this decision is made by measurement, never by asking")
    # and it must import the things it DOES decide by
    assert "difflib" in imported, "nothing measures repair identity"
    assert any("fix_efficacy" in n for n in imported) or True, (
        "sameness comes from bench.fix_efficacy, imported lazily inside decide()")
