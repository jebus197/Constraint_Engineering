#!/usr/bin/env python3
"""A finding that holds convergence open may never be shown to the panel as settled.

WHAT WAS WRONG. `FindingRegistry.build_summary` rendered UNCONFIRMED findings in a
section headed "SETTLED ... These findings are confirmed, closed, or merged. Do not
CHALLENGE or re-describe them.", while `FindingRegistry.unverified_critical_count`
counted those same findings as the A4 fail-safe blockers holding the convergence gate
shut. The panel was told not to touch the only findings standing between a run and its
conclusion.

HOW BADLY, measured by `scripts/the_blockers_are_shown_as_settled_2026-10-05.py`,
which attributes blockers by LEAVE-ONE-OUT on each real archived registry rather than
by a status predicate (a status predicate over-counted, finding blockers in runs whose
A4 count was 0): **175 of 175 attributed blockers were rendered under SETTLED,
100.0000%, Wilson [97.8520%, 100.0000%]**, across 22 of 59 archived registries,
37.2881%, Wilson [26.0840%, 50.0464%]. The leave-one-out total and the sum of the
counter's own returns agree exactly at 175.

WHY NO EARLIER TEST CAUGHT IT. Both halves were individually correct and each
described itself consistently, which is the exact condition `execute-do-not-grep`
names: a source-text assertion over either one passes. Only CALLING both and comparing
their accounts of the SAME finding exposes it. Every assertion below therefore calls
`build_summary` and `unverified_critical_count` and compares outputs; none inspects
source text.

THE INVARIANT HELD HERE, which generalises beyond the one status that was wrong:
  for every status in FINDING_STATUS_VOCABULARY, if a registry holding one finding of
  that status reports a non-zero A4 blocker count, that finding must NOT be rendered
  inside the SETTLED section.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    FindingRegistry, FINDING_STATUS_VOCABULARY)

SETTLED_HEADER = "--- SETTLED"
UNRESOLVED_HEADER = "--- UNRESOLVED"
FORBIDS = "Do not CHALLENGE"


def _entry(cid, status, sev=0.45, verified=False, desc="probe entry"):
    return {"canonical_id": cid, "status": status, "severity": sev,
            "verified": verified, "verdicts": [], "description": desc,
            "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
            "last_status_change_round": 0, "computed_evidence": [],
            "routing_history": []}


def _reg(entries):
    r = FindingRegistry()
    r.entries = dict(entries)
    return r


def _section_of(text, cid):
    """The section header under which `cid` is rendered, by walking the text."""
    section = "<no section>"
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("--- "):
            section = s
        if cid in line and not s.startswith("--- "):
            return section
    return None


def _block(text, header):
    """The body of the named section, up to the next header or the end marker."""
    if header not in text:
        return ""
    body = text.split(header, 1)[1]
    for nxt in ("\n--- ", "\n(", "\n=== END REGISTRY"):
        if nxt in body:
            body = body.split(nxt, 1)[0]
    return body


class TestTheInvariant:
    """No status the A4 counter calls blocking may render inside SETTLED."""

    @pytest.mark.parametrize("status", sorted(FINDING_STATUS_VOCABULARY))
    def test_a_blocking_status_is_never_rendered_as_settled(self, status):
        reg = _reg({"C0001": _entry("C0001", status)})
        blockers = reg.unverified_critical_count()
        text = reg.build_summary(3)
        if blockers < 1:
            pytest.skip(f"{status} is not an A4 blocker; nothing to assert")
        assert "C0001" in text, (
            f"{status} is an A4 blocker and is INVISIBLE to the panel — worse "
            f"than mislabelled"
        )
        assert "C0001" not in _block(text, SETTLED_HEADER), (
            f"{status} returns A4 count {blockers} yet is rendered inside the "
            f"SETTLED section, which tells the panel it is 'confirmed, closed, "
            f"or merged' and forbids challenge"
        )

    def test_at_least_one_status_is_actually_blocking(self):
        """Anti-vacuity: if nothing blocks, the parametrised test above is empty."""
        blocking = [s for s in FINDING_STATUS_VOCABULARY
                    if _reg({"C0001": _entry("C0001", s)}).unverified_critical_count() >= 1]
        assert blocking, (
            "no status in the vocabulary produces a non-zero A4 count, so the "
            "invariant test skipped every case and asserted nothing"
        )
        assert "UNCONFIRMED" in blocking, (
            f"UNCONFIRMED is the status this defect was found on; blocking set "
            f"is {blocking}"
        )


class TestTheUnconfirmedBlockerIsOffered:
    def test_it_lands_in_the_unresolved_section(self):
        reg = _reg({"C0066": _entry("C0066", "UNCONFIRMED")})
        text = reg.build_summary(3)
        assert UNRESOLVED_HEADER in text
        assert "C0066" in _block(text, UNRESOLVED_HEADER)

    def test_the_section_does_not_forbid_challenge(self):
        reg = _reg({"C0066": _entry("C0066", "UNCONFIRMED")})
        body = _block(reg.build_summary(3), UNRESOLVED_HEADER)
        assert FORBIDS not in body
        assert "NOT settled" in body

    def test_it_asks_for_an_id_addressed_runnable_falsifier(self):
        """The sweep's one in-round-absent capability, now offered every round."""
        body = _block(_reg({"C0066": _entry("C0066", "UNCONFIRMED")}
                           ).build_summary(3), UNRESOLVED_HEADER)
        assert "FALSIFIER: <ID>" in body, (
            "the id-addressed form is not requested, so the only parse that can "
            "attach a falsifier to a named residual still lives solely in the "
            "post-verdict sweep"
        )

    def test_it_states_that_prose_alone_clears_nothing(self):
        """The founder's anti-gaming guard, restated rather than relaxed."""
        body = _block(_reg({"C0066": _entry("C0066", "UNCONFIRMED")}
                           ).build_summary(3), UNRESOLVED_HEADER)
        assert "WITHDRAW" in body
        assert "resolves nothing" in body or "clears a blocker" in body

    def test_the_blocker_is_named_with_its_severity(self):
        body = _block(_reg({"C0066": _entry("C0066", "UNCONFIRMED", sev=0.45)}
                           ).build_summary(3), UNRESOLVED_HEADER)
        assert "C0066" in body and "0.45" in body


class TestGenuinelySettledFindingsAreUnmoved:
    """The additive half: nothing that WAS correctly settled moves."""

    @pytest.mark.parametrize("status", ["CLOSED", "CONFIRMED", "MERGED"])
    def test_a_settled_status_still_renders_under_settled(self, status):
        reg = _reg({"C0010": _entry("C0010", status, sev=0.9, verified=True)})
        text = reg.build_summary(3)
        assert "C0010" in _block(text, SETTLED_HEADER), (
            f"{status} left the SETTLED section; this change was meant to remove "
            f"nothing from it but UNCONFIRMED"
        )

    def test_an_open_finding_still_renders_in_full_detail(self):
        reg = _reg({"C0002": _entry("C0002", "OPEN", sev=0.8)})
        text = reg.build_summary(3)
        assert "C0002" in text
        assert "C0002" not in _block(text, SETTLED_HEADER)
        assert "C0002" not in _block(text, UNRESOLVED_HEADER)

    def test_hidden_statuses_stay_hidden(self):
        for st in ("REFUTED", "DUPLICATE"):
            text = _reg({"C0003": _entry("C0003", st)}).build_summary(3)
            assert "C0003" not in text, f"{st} became visible"


class TestTheCountsReconcile:
    def test_the_summary_counts_reconcile(self):
        """Splitting a bucket out left the header reporting Active 0 + Settled 1
        for a 2-finding registry. The buckets must sum to Total."""
        reg = _reg({
            "C0001": _entry("C0001", "UNCONFIRMED"),
            "C0002": _entry("C0002", "OPEN", sev=0.8),
            "C0010": _entry("C0010", "CLOSED", sev=0.9, verified=True),
            "C0011": _entry("C0011", "REFUTED"),
        })
        text = reg.build_summary(3)
        line = next(l for l in text.split("\n") if l.startswith("Active:"))
        import re
        nums = [int(n) for n in re.findall(r":\s*(\d+)", line)]
        assert sum(nums) == len(reg.entries), (
            f"buckets {nums} sum to {sum(nums)} against "
            f"{len(reg.entries)} findings — a panel reading the counts would "
            f"conclude a finding had vanished. Line: {line!r}"
        )

    def test_the_unresolved_count_is_named_in_the_header(self):
        reg = _reg({"C0001": _entry("C0001", "UNCONFIRMED")})
        line = next(l for l in reg.build_summary(3).split("\n")
                    if l.startswith("Active:"))
        assert "UNRESOLVED" in line and "1" in line


class TestThePartitionStaysComplete:
    def test_every_status_in_the_vocabulary_is_placed(self):
        """A status in no bucket is invisible to the panel. The runner logs a
        warning for this; the test makes it fail instead."""
        placed = []
        for st in sorted(FINDING_STATUS_VOCABULARY):
            text = _reg({"C0001": _entry("C0001", st)}).build_summary(3)
            visible = "C0001" in text
            hidden_ok = st in ("REFUTED", "DUPLICATE")
            placed.append((st, visible or hidden_ok))
        missing = [s for s, ok in placed if not ok]
        assert not missing, f"statuses neither shown nor deliberately hidden: {missing}"
