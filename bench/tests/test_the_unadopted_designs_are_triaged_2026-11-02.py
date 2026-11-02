"""Every unadopted seat design carries a derived verdict, and none was applied.

HIS RULING, 2026-11-01, verbatim: *"Triage them. I already brought up the issue
of us potentially doing a great deal of work, only for that work to be
subsequently ignored. But what is the point of doing any work at all if it can
just be routinely ignored?"*

THE SET IS 40, NOT 44. The committed store producer records that 5 of 41 absent
module paths were FALSIFIERS counted as designs, 12.2% with a 95% interval of
[0.053233, 0.255442], because its kind test matched `falsifier` and not the
`falsify_` prefix the seats used. The inflated 44 is what reached him, and B60's
text still carries it.

TWO DEFECTS IN THE TRIAGE ITSELF, BOTH CAUGHT BY ITS OWN OUTPUT:

  * A first pass returned SUPERSEDED for 27 of 27. The preserved evidence copies
    live under `bench/logs/**/files/bench/...`, so a `bench/**/` glob matched
    each artefact against ITSELF. A verdict that never varies is not a verdict,
    and the uniformity is the only thing that gave it away.
  * A second pass found 33 of the 37 absent live-module files, because it read
    M3's printed KIND TAG instead of the producer's `_kind` decision -- a second
    declaration of a classification that already existed in code.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TRIAGE = REPO / "scripts" / "triage_the_unadopted_designs_2026-11-02.py"
STORE = REPO / "scripts" / "how_big_is_the_unapplied_fix_store_2026-11-01.py"
RECORD = REPO / "experimental_notes" / "data" / "unadopted_design_triage_2026-11-02.json"

VERDICTS = {"SUPERSEDED", "REACHED_BY_NOTHING", "NAMED_IN_A_CLOSED_ENTRY",
            "CANDIDATE", "DIVERGENT_REVIEW", "SCRATCH_NOT_A_DESIGN"}


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_triage", TRIAGE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rec():
    assert RECORD.is_file(), (
        f"{RECORD.name} is missing: run "
        f"`python3 scripts/triage_the_unadopted_designs_2026-11-02.py --write`")
    return json.loads(RECORD.read_text())


class TestEveryArtefactCarriesAVerdict:

    def test_the_count_matches_the_committed_store_producer(self, rec):
        out = __import__("subprocess").run(
            ["python3", str(STORE)], cwd=REPO, capture_output=True, text=True)
        m = re.search(r"live-module artefacts: (\d+)", out.stdout)
        assert m, "the store producer no longer reports its live-module count"
        assert len(rec["rows"]) == int(m.group(1)), (
            f"the triage holds {len(rec['rows'])} rows against the producer's "
            f"{m.group(1)} live-module artefacts; one of them is wrong and a "
            f"count alone would have hidden which")

    def test_every_row_has_a_known_verdict_and_a_reason(self, rec):
        for r in rec["rows"]:
            assert r["verdict"] in VERDICTS, r
            assert r.get("why", "").strip(), f"no reason recorded for {r['path']}"
            assert r.get("seat"), r

    def test_no_path_is_triaged_twice(self, rec):
        keys = [(r["seat"], r["path"]) for r in rec["rows"]]
        dupes = [k for k, n in collections.Counter(keys).items() if n > 1]
        assert not dupes, f"triaged twice: {dupes}"


class TestTheVerdictsDiscriminate:

    def test_more_than_one_verdict_actually_occurs(self, rec):
        """THE DEFECT THAT ALMOST SHIPPED. 27 of 27 came back SUPERSEDED."""
        seen = collections.Counter(r["verdict"] for r in rec["rows"])
        assert len(seen) >= 3, (
            f"only {len(seen)} distinct verdict(s) occur: {dict(seen)}. A "
            f"classification that returns one answer is not classifying.")

    def test_the_evidence_copies_are_not_counted_as_live_modules(self, mod):
        """The exact predicate error: `bench/logs/**` holds a copy of each."""
        assert any("logs" in ln for ln in TRIAGE.read_text().splitlines()
                   if "same_name" in ln or "logs" in ln), (
            "the logs exclusion is gone, so every artefact will match itself")
        rows = json.loads(RECORD.read_text())["rows"]
        assert not all(r["verdict"] == "SUPERSEDED" for r in rows)

    def test_the_taxonomy_matches_the_producers_own(self, mod):
        """2 declarations of 1 classification must agree, or neither is trusted."""
        for path, want in (
            ("bench/tests/test_x.py", "guard/test"),
            ("scripts/x.py", "producer/script"),
            ("bench/x.py", "live-module file"),
            ("bench/falsify_x.py", "falsifier (evidence)"),
            ("scripts/falsifier_x.py", "falsifier (evidence)"),
        ):
            assert mod._store_kind_of(None, path) == want, (path, want)


class TestNothingWasApplied:

    def test_no_triaged_artefact_became_a_live_file(self, rec):
        """His instruction was a verdict against each, APPLYING NONE."""
        applied = []
        for r in rec["rows"]:
            if r["state"] != "ABSENT":
                continue
            if (REPO / r["path"]).is_file():
                applied.append(r["path"])
        assert not applied, (
            f"{len(applied)} artefact(s) recorded ABSENT now exist live, so "
            f"something was applied: {applied[:4]}")

    def test_the_triage_script_writes_only_its_own_record(self):
        src = TRIAGE.read_text()
        writes = re.findall(r"(\w+)\.write_text\(", src)
        assert set(writes) <= {"OUT"}, (
            f"the triage writes to {set(writes)}; it must write only its own "
            f"record and apply nothing")


class TestTheSignalsThatMakeItUseful:

    def test_co_proposal_is_recorded(self, rec):
        """2 seats proposing the same basename is stronger than 1, and a bare
        count of 40 hides it."""
        assert all("seats_proposing_this_basename" in r for r in rec["rows"])
        multi = [r for r in rec["rows"] if r["seats_proposing_this_basename"] > 1]
        assert multi, (
            "no basename is proposed by more than 1 seat any more; re-measure "
            "before relying on the co-proposal signal")

    def test_a_scratch_file_is_not_called_a_design(self, rec):
        scratch = [r for r in rec["rows"]
                   if re.match(r"^tmp[a-z0-9]{8}\.py$", pathlib.Path(r["path"]).name)]
        for r in scratch:
            assert r["verdict"] == "SCRATCH_NOT_A_DESIGN", (
                f"{r['path']} is a mkstemp artefact and is recorded as "
                f"{r['verdict']}")

    def test_the_divergent_three_are_separated_from_the_rest(self, rec):
        """The only shape where the tree runs something a seat tried to fix."""
        div = [r for r in rec["rows"] if r["state"] == "DIVERGED"]
        assert div, "no divergent artefacts; the store producer reported 3"
        for r in div:
            assert r["verdict"] == "DIVERGENT_REVIEW", r
            assert (REPO / r["path"]).is_file(), (
                f"{r['path']} is recorded DIVERGED but does not exist live")
