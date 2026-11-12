#!/usr/bin/env python3
"""No expert encoding may state a route-specific exposure limit under the wrong route.

★ WHY THIS EXISTS, AND IT IS A LIVE DEFECT THAT WAS SHIPPED. On 2026-11-12,
while the 28 thin expert encodings were being brought to depth,
`bench/directives/chemistry/chemistry_pharma.txt` was found stating the ICH Q3D
elemental impurity limits, LABELLED AS ORAL, as:

    Pd <= 10 ug/day, Pt <= 10 ug/day, Ni <= 20 ug/day, Cu <= 300 ug/day

Those are the PARENTERAL figures. The oral permitted daily exposures are Pd 100,
Pt 100, Ni 200 and Cu 3000 ug/day -- every one a factor of 10 higher. All 4 were
uniformly 10x low, which is the signature of reading across the wrong column
rather than 4 independent errors, and the effect on a seat following the file was
to reject oral batches that comply.

★ CONFIRMED ON A SECOND ROUTE BEFORE THE FILE WAS CHANGED. The finding came from
a delegated worker, and a model's claim is not evidence under this project's own
rule -- a finding is confirmed programmatically or by the human in the loop, never
by a model's word. The oral values were checked by external search against
published reference tables, and only then was the HARD constraint corrected.

★ WHY A GUARD RATHER THAN JUST A FIX. The fault is a CLASS, not an instance: any
limit that differs by administration route can be transcribed from the wrong
column, and the file remains internally consistent when it happens -- which is
why a review pass reading for sense would pass it. This checks the figures
against the route each line names, so the next column slip fails here instead of
reaching a seat.

★ AND IT MUST NOT ACCUSE A CORRECT FILE. The parenteral figures are RIGHT for a
parenteral line, so the predicate tests the pair (route, value) and never the
value alone. `test_the_parenteral_figures_are_accepted_under_their_own_route`
drives exactly that case, because a guard that flagged 10 ug/day anywhere would
be the instrument false positive this project has recorded 7 times.

Costs nothing: reads local files, dispatches to no model, runs no pytest.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
DIRECTIVES = REPO / "bench" / "directives"

#: ICH Q3D(R2) permitted daily exposures, ug/day, per administration route.
#: Oral confirmed 2026-11-12 by external search against published tables;
#: parenteral is 10x lower and inhalation 10x lower again for these 4 elements.
Q3D = {
    "oral":       {"Pd": 100, "Pt": 100, "Ni": 200, "Cu": 3000},
    "parenteral": {"Pd": 10,  "Pt": 10,  "Ni": 20,  "Cu": 300},
    "inhalation": {"Pd": 1,   "Pt": 1,   "Ni": 5,   "Cu": 30},
}
ROUTES = tuple(Q3D)
#: `Pd <= 100 ug/day` and `Pd 100 ug/day` both occur in practice.
_LIMIT = re.compile(r"\b(Pd|Pt|Ni|Cu)\s*(?:<=|≤|=)?\s*(\d+)\s*ug/day", re.I)


def _encodings() -> list[pathlib.Path]:
    return [p for p in sorted(DIRECTIVES.rglob("*.txt"))
            if p.parent.name != "universal"]


def _route_of(line: str) -> str | None:
    """The route a line names, or None. Explicit naming only: inferring a route
    from context is how the original error passed review."""
    low = line.lower()
    found = [r for r in ROUTES if r in low]
    return found[0] if len(found) == 1 else None


def _claims(path: pathlib.Path) -> list[tuple[int, str, str, int]]:
    """(line number, route, element, value) for every route-labelled limit.

    The route may be named on the line itself or on the line that introduces the
    block, which is the shape the live file uses: a heading line naming the route
    followed by an indented line carrying the figures.
    """
    out = []
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    for i, line in enumerate(lines):
        hits = _LIMIT.findall(line)
        if not hits:
            continue
        route = _route_of(line)
        if route is None and i:
            route = _route_of(lines[i - 1])
        if route is None:
            continue
        for elem, val in hits:
            out.append((i + 1, route, elem.capitalize(), int(val)))
    return out


class TestEveryRouteLabelledLimitMatchesItsRoute:
    def test_the_corpus_states_no_limit_under_the_wrong_route(self):
        wrong = []
        for p in _encodings():
            for ln, route, elem, val in _claims(p):
                want = Q3D[route].get(elem)
                if want is None or val == want:
                    continue
                #: Name the route the value DOES belong to, because that is what
                #: makes the diagnosis a column slip rather than a typo.
                belongs = [r for r in ROUTES if Q3D[r].get(elem) == val]
                wrong.append(
                    f"{p.relative_to(REPO)}:{ln} says {elem} {val} ug/day under "
                    f"{route}, where {route} is {want}"
                    + (f" -- {val} is the {belongs[0]} figure" if belongs else ""))
        assert not wrong, (
            "a route-specific exposure limit is stated under the wrong route:\n  "
            + "\n  ".join(wrong))

    def test_the_pharma_encoding_now_states_the_ORAL_figures(self):
        """The instance this guard was written for, pinned so it cannot regress."""
        p = DIRECTIVES / "chemistry" / "chemistry_pharma.txt"
        if not p.is_file():
            pytest.skip("the pharmaceutical chemistry encoding is not in this checkout")
        claims = {(elem, route): val for _ln, route, elem, val in _claims(p)}
        for elem, want in Q3D["oral"].items():
            got = claims.get((elem, "oral"))
            assert got == want, (
                f"{elem} under oral reads {got} ug/day and must be {want}; "
                f"{Q3D['parenteral'][elem]} is the parenteral figure and was "
                f"the shipped error")


class TestItDoesNotAccuseACorrectFile:
    def test_the_parenteral_figures_are_accepted_under_their_own_route(self):
        """A guard flagging 10 ug/day anywhere would be an instrument false
        positive, which this project has recorded 7 of in a single day."""
        for elem, val in Q3D["parenteral"].items():
            line = f"  parenteral PDE: {elem} <= {val} ug/day"
            route = _route_of(line)
            assert route == "parenteral", route
            assert Q3D[route][elem] == val, (
                f"the correct parenteral figure for {elem} would be rejected")

    def test_a_line_naming_no_route_is_left_alone(self):
        """Inferring a route from context is how the original error passed."""
        assert _route_of("  Pd <= 10 ug/day after scavenging") is None

    def test_a_line_naming_two_routes_is_left_alone(self):
        """Ambiguous is not the same as wrong, and guessing would accuse prose."""
        assert _route_of("oral and parenteral differ: Pd 100 vs 10 ug/day") is None


class TestTheCheckIsNotVacuous:
    def test_it_finds_route_labelled_claims_in_the_live_corpus(self):
        total = sum(len(_claims(p)) for p in _encodings())
        assert total >= 4, (
            f"only {total} route-labelled limit(s) found in the whole corpus, so "
            f"the check above is asserting on almost nothing")

    def test_a_constructed_column_slip_IS_caught(self, tmp_path):
        """Drive the predicate with the exact defect that shipped."""
        bad = tmp_path / "bad.txt"
        bad.write_text("Elemental impurity limits per ICH Q3D (R2), oral PDE:\n"
                       "  Pd <= 10 ug/day, Pt <= 10 ug/day\n", encoding="utf-8")
        claims = _claims(bad)
        assert claims, "the predicate did not even parse the constructed defect"
        offending = [(e, v) for _l, r, e, v in claims
                     if r == "oral" and Q3D["oral"][e] != v]
        assert len(offending) == 2, (
            f"the constructed column slip was not caught: {claims}")
