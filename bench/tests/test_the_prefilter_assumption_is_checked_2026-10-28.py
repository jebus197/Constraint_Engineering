"""fable's prefilter rests on ONE assumption. This is the check that replaces trust.

THE DEFECT BOTH SEATS FOUND, 2026-10-28. `CANDIDATE_LINE` filtered raw JSON
lines with `\\b(?:fr|pf|qs|wr)\\b` while the DECISION, `MARKER`, runs on decoded
text under `re.MULTILINE` and accepts any preceding whitespace. A newline in the
raw line is backslash followed by `n`, so the character left of the token is the
WORD character `n` and the left `\\b` fails: a marker on its own line was dropped
before anything decoded it. 185 of 500 generated cases. Their 2 falsifiers are
kept and run beside this file.

WHY THIS FILE EXISTS RATHER THAN cc2's SAFER REGEX. Both proposed repairs pass
both falsifiers, so the falsifiers cannot choose. Measured over the live
transcripts, cc2's boundary-free form admits roughly 9 to 10 times as many lines
as fable's, and every admitted line costs a `json.loads` over a file of
hundreds of megabytes. fable's form is taken because its single assumption --
that the transcript writer never `\\u`-escapes an ASCII letter -- is MEASURED to
hold: 0 of 259,028 lines across 6 transcripts, Clopper-Pearson exact
[0.000000000, 0.000014241].

AN ASSUMPTION THAT IS MEASURED ONCE AND THEN TRUSTED IS THE SHAPE THIS PROJECT
KEEPS WITHDRAWING. So the measurement is a TEST. If a writer change ever escapes
an ASCII letter, this fails and names the fallback, instead of the harvester
silently dropping markers again.

Producer: `scripts/the_prefilter_was_not_a_superset_2026-10-28.py`.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_prefilter_was_not_a_superset_2026-10-28.py"
HARVESTER = REPO / "scripts" / "harvest_tickets_2026-10-17.py"
SESSIONS = pathlib.Path.home() / ".claude" / "projects" / \
    "-Users-georgejackson-Developer-Projects"

#: BOUNDED ON PURPOSE. A full scan is hundreds of megabytes and this runs in
#: the suite; a writer change affects EVERY line it writes, not a rare one, so a
#: bounded prefix detects it. The full-corpus figure lives in the producer, and
#: `--limit-mb` is how this bound is expressed there too.
SCAN_BYTES = 4 * 1048576


def _producer():
    if not PRODUCER.is_file():
        pytest.skip(f"producer absent at {PRODUCER}")
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_prefilter_choice", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _harvester():
    spec = importlib.util.spec_from_file_location("_harv_prefilter", HARVESTER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_harv_prefilter"] = m
    spec.loader.exec_module(m)
    return m


def _alternation_ordered(pattern: str) -> list[str]:
    r"""The kind alternation IN ORDER, from the group that holds the kinds.

    A set cannot pin an order and an index cannot find the group: `MARKER` has
    3 parenthesised groups and the kinds are in the middle one, which is why a
    `split("(")[-1]` read the trailing `(?:[:\]\)]...)` instead and this very
    assertion fired on correct code at 2026-11-01 21:37.
    """
    for grp in re.findall(r"\(\??:?((?:[a-z]{2,4})(?:\|[a-z]{2,4})+)\)", pattern):
        return grp.split("|")
    return []


def _alternation(pattern: str) -> set[str]:
    """Every lowercase-alpha alternative appearing in a `(...|...)` group.

    Deliberately shallow: it reads the kind vocabulary out of a pattern without
    importing the harvester's private spelling of it, so the 2 declarations are
    compared rather than one being trusted.
    """
    out: set[str] = set()
    for grp in re.findall(r"\(\??:?((?:[a-z]{2,4})(?:\|[a-z]{2,4})+)\)", pattern):
        out |= set(grp.split("|"))
    return out


class TestTheAssumptionIsCheckedNotTrusted:

    def test_no_transcript_escapes_an_ascii_letter(self):
        """The reversion target: if this ever fires, switch to cc2's bare form."""
        m = _producer()
        if not SESSIONS.is_dir():
            pytest.skip("no transcript directory on this machine")
        files = sorted(SESSIONS.glob("*.jsonl"),
                       key=lambda p: p.stat().st_mtime)[-2:]
        if not files:
            pytest.skip("no transcripts to scan")
        offenders = []
        for f in files:
            read = 0
            with f.open(encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh, 1):
                    if read > SCAN_BYTES:
                        break
                    read += len(line)
                    if m.ESCAPED_ASCII_LETTER.search(line):
                        offenders.append(f"{f.name}:{i}")
                        break
        assert not offenders, (
            f"a transcript now \\u-escapes an ASCII letter ({offenders[:3]}), so "
            f"the right-hand \\b in CANDIDATE_LINE is no longer safe. Switch to "
            f"cc2's boundary-free form `(?:fr|pf|qs|wr)` -- it is a superset "
            f"under no assumption, at roughly 9 times the decoding cost.")

    def test_the_live_prefilter_is_the_form_the_measurement_chose(self):
        """A measurement that chose a form must be able to see it was applied.

        ★ REWRITTEN 2026-11-01, BECAUSE THE LITERAL WAS RED ON A CORRECT CHANGE
        AND GREEN ON THE REAL DEFECT. It pinned `(?:fr|pf|qs|wr)\b` exactly, and
        when `stm` was admitted as his 6th kind the harvester updated BOTH its
        `MARKER` and its `CANDIDATE_LINE` -- a correct, complete change -- and
        this test went red anyway. Worse, the failure it exists to catch is a
        kind added to `MARKER` while `CANDIDATE_LINE` is left behind, because
        the prefilter then DROPS lines the marker would have matched; against
        that mutation the literal stays GREEN, since `CANDIDATE_LINE` is
        untouched. Measured both ways by
        `scripts/the_prefilter_comparator_mutations_2026-11-01.py`.

        What fable's measurement actually chose was a FORM -- alternation, a
        right `\b`, and no left `\b` -- not a frozen kind list. So the form is
        pinned here and the kind list is COMPARED against `MARKER`'s own
        alternation. That is the defect the harvester's own line 92 names: 4
        places spell this vocabulary out and nothing compared them.
        """
        h = _harvester()
        marker_kinds = _alternation(h.MARKER.pattern)
        prefilter_kinds = _alternation(h.CANDIDATE_LINE.pattern)
        assert marker_kinds, (
            f"no alternation readable from MARKER {h.MARKER.pattern!r}; the "
            f"comparator cannot run and would pass vacuously")
        assert prefilter_kinds == marker_kinds, (
            f"the prefilter admits {sorted(prefilter_kinds)} but the marker "
            f"reads {sorted(marker_kinds)}. A kind in only one of them is a "
            f"kind whose annotations are dropped before the marker ever sees "
            f"them (prefilter short) or scanned for nothing (marker short).")
        # the FORM, which is the half fable's measurement actually chose
        assert h.CANDIDATE_LINE.pattern == (
            r"(?:" + "|".join(_alternation_ordered(h.MARKER.pattern)) + r")\b"), (
            f"the live prefilter is {h.CANDIDATE_LINE.pattern!r}; the measured "
            f"form is a bare alternation with a RIGHT \\b and no left \\b, in "
            f"MARKER's own kind order. If the form has moved, say which "
            f"measurement moved it")

    def test_the_left_boundary_is_gone_which_is_the_actual_repair(self):
        """The precise reversion: restoring the left \\b re-breaks it."""
        h = _harvester()
        raw = r'{"text":"the gate.\nqs: should the quiet run be adaptive?"}'
        assert h.CANDIDATE_LINE.search(raw), (
            "a marker at the start of a line inside a multi-line message is the "
            "commonest form there is, and the prefilter must admit it")
        assert not re.search(r"\b(?:fr|pf|qs|wr)\b", raw, re.IGNORECASE), (
            "this fixture no longer demonstrates the defect, so it has stopped "
            "guarding the repair")

    def test_the_producer_reaches_a_choice_and_states_it(self):
        m = _producer()
        if not SESSIONS.is_dir():
            pytest.skip("no transcript directory on this machine")
        r = m.measure(limit_bytes=1048576)
        assert r["chosen"] in ("fable", "cc2")
        assert r["assumption_holds"] is (r["chosen"] == "fable"), (
            "the choice must FOLLOW the assumption test, not sit beside it")
        assert r["admits_cc2"] >= r["admits_fable"], (
            "cc2's form is boundary-free and cannot admit fewer lines; if it "
            "does, one of the 2 patterns is not what this measurement thinks")

    def test_the_cost_that_justified_the_choice_is_still_real(self):
        """If cc2's form stopped being expensive, take it and drop the check."""
        m = _producer()
        if not SESSIONS.is_dir():
            pytest.skip("no transcript directory on this machine")
        r = m.measure(limit_bytes=1048576)
        assert r["cc2_cost_multiple"] > 2.0, (
            f"cc2's form now costs only {r['cc2_cost_multiple']:.4f} times "
            f"fable's. The assumption check exists to buy that difference; if it "
            f"has gone, take cc2's unconditional superset and delete this file")
