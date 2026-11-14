# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'asking_predicate_and_fourth_standard_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 78027ddca80c9014b85d7dbc589e5def26ea48c10333bfa701f1038261b59b34
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The 3 facts the 2026-11-14 panel verdict on the `_later` proxy rests on.

Each is an invariant that must SURVIVE any future repair of the proxy; none
pins the defect itself (a pinned defect would block its own fix).

1. The sibling predicates B and C each IMPLY the live proxy A, so adopting
   either can only SHRINK the set of entries reported as awaiting the founder
   -- the suppression direction his precedent of 2026-11-09 withdrew.
2. `movable_count()`/`refusal_budget()` in hooks/work_not_narrate.py depend
   only on `live_asks`, which is invariant to the `ruled` argument -- so the
   stop-gate's BUDGET is blind to the proxy and the proxy's blast radius is
   the banner count plus `_first_movable`'s naming, nothing more.
3. The proposed recorded-fact verdict (scripts/the_ask_outlives_the_ruling_
   is_a_recorded_fact_2026-11-14.py, NOT installed) is monotone-safe: it
   never removes an entry from OWED relative to `classify_text` except on a
   recorded `raised:` stamp dated on or before the ruling.
"""
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


def _clf():
    return _load("_t_clf",
                 "scripts/how_many_decisions_actually_need_him_2026-11-01.py")


def _abc(clf, body, ruled):
    """The 3 sibling predicates, byte-faithful to the 2026-11-12 producer."""
    later = [m.start() for m in clf._DATED_IN_BODY.finditer(body)
             if m.group(0) > ruled]
    A = bool(later)
    stale = [m.start() for m in clf.STALE.finditer(body)]
    live = []
    for start, sent in clf._sentences(body):
        if clf.STALE.search(sent) or not clf.ASKS.search(sent):
            continue
        if clf.FREE.search(sent) or any(s > start for s in stale):
            continue
        live.append((start, sent))
    B = any(any(d > ruled for d in clf._DATED_IN_BODY.findall(s))
            for _, s in live)
    first = min(later) if later else None
    C = first is not None and any(p >= first for p, _ in live)
    return A, B, C


def test_siblings_only_shrink_the_owed_set():
    """B => A and C => A over every ruled OPEN entry: 0 violations.

    A later date inside an asking sentence is a later date in the body, and a
    live ask after the first later date requires a later date to exist -- so
    the implication holds by construction; this guards the construction.
    """
    clf = _clf()
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm
    bodies = clf.bodies()
    checked = 0
    for e in tlm.parse_entries(REPO / "experimental_notes" /
                               "CDSFL_MASTER_TASK_LIST.md"):
        if (e.state or "").upper() != "OPEN" or not e.ruled:
            continue
        A, B, C = _abc(clf, bodies.get(e.ident, ""), e.ruled)
        assert not (B and not A), f"{e.ident}: B without A"
        assert not (C and not A), f"{e.ident}: C without A"
        checked += 1
    assert checked > 0, "no ruled OPEN entries -- the guard checked nothing"


def test_refusal_budget_is_blind_to_the_proxy():
    """`live_asks` is invariant to `ruled`, so the stop-gate budget never
    moves when the `_later` proxy does."""
    clf = _clf()
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm
    bodies = clf.bodies()
    for e in tlm.parse_entries(REPO / "experimental_notes" /
                               "CDSFL_MASTER_TASK_LIST.md"):
        if (e.state or "").upper() != "OPEN":
            continue
        b = bodies.get(e.ident, "")
        with_r = clf.classify_text(e.state, e.ruled, b)["live_asks"]
        without = clf.classify_text(e.state, None, b)["live_asks"]
        assert with_r == without, f"{e.ident}: live_asks depends on ruled"


def test_recorded_fact_never_silently_drops_an_entry():
    """The proposed verdict leaves OWED only on a recorded stamp <= ruling."""
    rec = _load("_t_rec",
                "scripts/the_ask_outlives_the_ruling_is_a_recorded_fact_2026-11-14.py")
    clf = _clf()
    RULED = "2026-11-08"
    ask_unstamped = "NEEDS HIS RULING: on whether to enable the gate. "
    ask_early = "NEEDS HIS RULING raised:2026-11-05: on the first half. "
    ask_late = "STILL NEEDS HIS RULING raised:2026-11-10: on the second half. "
    ruling = "HIS RULING, 2026-11-08: enable it. "
    note = "MEASURED AND RECORDED, 2026-11-10, this sentence asks nothing. "

    # a stamp later than the ruling: OWED on the RECORD
    v = rec.entry_verdict("OPEN", RULED, ask_late + ruling, clf)
    assert (v["kind"], v["basis"]) == ("OWED", "recorded")
    # every ask stamped on/before the ruling: GRANTED on the RECORD,
    # even though the progress note would keep the A proxy firing
    v = rec.entry_verdict("OPEN", RULED, ask_early + ruling + note, clf)
    assert (v["kind"], v["basis"]) == ("GRANTED", "recorded")
    # an unstamped ask: NEVER dropped -- the classifier's verdict stands, named
    v = rec.entry_verdict("OPEN", RULED, ask_unstamped + ruling + note, clf)
    base = clf.classify_text("OPEN", RULED, ask_unstamped + ruling + note)
    assert v["kind"] == base["kind"] == "OWED" and v["basis"] == "proxy"
    # and on the LIVE list: every departure from classify_text's OWED is
    # backed by a full set of recorded stamps on/before the ruling
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm
    bodies = clf.bodies()
    for e in tlm.parse_entries(REPO / "experimental_notes" /
                               "CDSFL_MASTER_TASK_LIST.md"):
        if (e.state or "").upper() != "OPEN":
            continue
        b = bodies.get(e.ident, "")
        base = clf.classify_text(e.state, e.ruled, b)
        v = rec.entry_verdict(e.state, e.ruled, b, clf)
        if base["kind"] == "OWED" and v["kind"] != "OWED":
            assert v["basis"] == "recorded" and len(v["stamps"]) == len(
                base["live_asks"]), f"{e.ident}: silently dropped"
