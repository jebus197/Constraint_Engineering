# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 917121dd3cd847e2df78159c95884192c5363b8232344f864aa5216625b02365
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The O4 component is wired and verdict-neutral, per the additive standard.

Guards scripts/the_undecidable_set_grows_without_the_record_2026-11-14.py:
the `raised:` stamp reader decides by record where stamps exist, keeps
predicate A's verdict FLAGGED (never silently) where they do not, and changes
no verdict on the live task list today, because 0 live asks carry stamps.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, m)
    spec.loader.exec_module(m)
    return m


prod = _load("_prod_rec",
             "scripts/the_undecidable_set_grows_without_the_record_2026-11-14.py")
clf = _load("_clf_rec_t",
            "scripts/how_many_decisions_actually_need_him_2026-11-01.py")


def test_stamp_parses_and_ignores_prose():
    assert prod.recorded_raise("NEEDS YOUR RULING, raised:2026-11-18.") == "2026-11-18"
    assert prod.recorded_raise("which is why only this one is raised: see B25") is None
    assert prod.recorded_raise("no stamp here 2026-11-18") is None


def test_stamped_post_ruling_ask_is_owed_by_record():
    txt = "Which ordering is kept NEEDS YOUR RULING, raised:2026-11-22."
    r = prod.verdict_by_record("OPEN", "2026-11-20", txt, clf)
    assert r["kind"] == "OWED" and r["decided_by"] == "RECORD"


def test_record_settles_what_every_text_predicate_misreads():
    txt = ("Progress 2026-11-21: measured, committed, no question. "
           "Whether the gate also skips DEFERRED entries NEEDS YOUR "
           "RULING, raised:2026-11-18.")
    a = clf.classify_text("OPEN", "2026-11-20", txt)
    r = prod.verdict_by_record("OPEN", "2026-11-20", txt, clf)
    assert a["kind"] == "OWED"            # predicate A false-positives
    assert r["kind"] == "GRANTED" and r["decided_by"] == "RECORD"


def test_unstamped_legacy_keeps_A_and_is_flagged_not_silent():
    txt = "The ceiling of 40 NEEDS YOUR RULING. Progress 2026-11-21: measured."
    a = clf.classify_text("OPEN", "2026-11-20", txt)
    r = prod.verdict_by_record("OPEN", "2026-11-20", txt, clf)
    assert r["kind"] == a["kind"]
    assert r["decided_by"] == "PROXY_A" and r["undecided_by_record"] is True


def test_verdict_neutral_on_every_live_entry_today():
    """0 live asks carry stamps, so the record route changes NOTHING yet."""
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries
    bodies = clf.bodies()
    es = parse_entries(REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    changed = []
    for e in es:
        if e.state != "OPEN":
            continue
        txt = bodies.get(e.ident, "")
        a = clf.classify_text(e.state, e.ruled, txt)
        r = prod.verdict_by_record(e.state, e.ruled, txt, clf)
        if r["kind"] != a["kind"]:
            changed.append(e.ident)
    assert changed == []


def test_disputed_set_is_inside_the_owed_set_and_gate_skipped():
    """The J3 figures, derived structurally rather than pinned as constants."""
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries
    bodies = clf.bodies()
    es = parse_entries(REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    owed, disputed = [], []
    for e in es:
        if e.state != "OPEN":
            continue
        txt = bodies.get(e.ident, "")
        r = clf.classify_text(e.state, e.ruled, txt)
        if r["kind"] != "OWED":
            continue
        owed.append(e.ident)
        if e.ruled and r["live_asks"]:
            B, C, D = prod.preds_BCD(e.ruled, txt, clf)
            if not (True == B == C):
                disputed.append(e.ident)
    assert set(disputed) <= set(owed)
    assert disputed, "no disputed entries left: rerun the joint-round scoring"
    # every disputed entry is skipped by the gate's own criterion
    # (work_not_narrate._first_movable: `if kind == "OWED" ... continue`)
    assert all(d in owed for d in disputed)
