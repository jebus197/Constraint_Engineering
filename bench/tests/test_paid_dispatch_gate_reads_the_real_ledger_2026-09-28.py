"""The paid-dispatch gate is executed against the REAL committed ledger.

WHY THIS FILE EXISTS, and it is the defect that produced it rather than a wish
for more coverage. `test_paid_dispatch_needs_authorisation_2026-09-28.py` shipped
on 2026-09-28 with 11 tests, all green, guarding a gate that refused every real
authorisation the founder has ever given. Two faults, and each alone was
sufficient:

  1. `PAID_LEDGER` was spelt a second time inside the panel script as
     `bench/paid_dispatch_authorisations.json`. THAT FILE DOES NOT EXIST. The
     committed ledger is `bench/directives/universal/paid_dispatch_authorisations.json`.
     Executed before the fix: `is_file()` False, so all 7 authorised rounds got
     "no authorisation ledger at ...".
  2. Repointing the path alone did not help. The real ledger is a MAPPING with
     `authorisations[].rounds[]` and `founder_verbatim[]`; the gate's own parser
     demanded a flat list, so the same 7 rounds got "authorisation ledger is not
     a list of entries".

NEITHER FAULT WAS VISIBLE TO THOSE 11 TESTS, because every one of them
monkeypatched a synthetic ledger in a flat schema of the test's own invention. The
green measured the agreement between a fixture and a parser, and both were wrong
together. A fixture written in a schema the production path does not use tests the
fixture.

SO THIS FILE MONKEYPATCHES NOTHING. It executes the gate against the committed
record, with the round names the founder actually authorised, and it would have
failed on both faults on the day they were introduced.

THE ANTI-VACUITY PROBLEM, and it is the same trap one level up. A test that says
"the gate agrees with the reader about where the ledger is" greens when both point
at a file that does not exist, which is exactly the state it is meant to detect.
So the anchors here are INDEPENDENT of both modules' spelling of the path: the
file must exist, and git must be tracking it. Existence and version control are
properties of the world, not of either module's opinion.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(ROOT / "bench"))
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("panel_real_ledger", PANEL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def ledger_json(mod):
    """The committed ledger, parsed INDEPENDENTLY of the reader module.

    2 routes to the same data. The reader's `authorised_rounds()` is 1; this plain
    `json.load` of the path the gate reports is the other. Where they disagree, 1
    of them is wrong, and a test that used only the reader could not tell.
    """
    return json.loads(mod.PAID_LEDGER.read_text(encoding="utf-8"))


class TestTheLedgerTheGateReadsIsTheCommittedOne:
    def test_the_ledger_the_gate_names_actually_exists(self, mod):
        """THE FAULT THAT SHIPPED, in 1 assertion.

        The old `PAID_LEDGER` pointed at a filename that had never existed, and
        nothing noticed because every test supplied its own file instead.
        """
        assert mod.PAID_LEDGER.is_file(), (
            f"the gate reads {mod.PAID_LEDGER}, which does not exist, so every "
            f"paid dispatch is refused however the founder authorises it"
        )

    def test_the_ledger_is_version_controlled(self, mod):
        """A ledger git does not track is not a committed record.

        The guard's whole enforcement is auditability: spending requires forging
        the founder's words somewhere that shows up in `git diff`. An untracked
        file shows up in no diff, so it enforces nothing. This anchor is
        independent of what either module thinks the path is.
        """
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(mod.PAID_LEDGER)],
            cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, (
            f"{mod.PAID_LEDGER} is not tracked by git, so an authorisation "
            f"written into it would never appear in review: {r.stderr.strip()}"
        )

    def test_the_gate_and_the_reader_name_one_file(self, mod):
        """1 PARSER, 1 PATH. The reader's docstring names the reason: "The
        authorisation list is a money constraint; 2 copies that could drift is
        exactly the shape to avoid." The gate was the second copy.

        This assertion is not sufficient on its own -- 2 modules can agree on a
        path that does not exist, which is precisely what happened -- so it sits
        beside the existence and git anchors above rather than standing in for
        them.
        """
        assert mod.PAID_LEDGER == mod._paid_ledger.AUTHORISATIONS
        assert mod._ledger_path() == mod._paid_ledger.AUTHORISATIONS

    def test_the_committed_ledger_is_a_mapping_not_a_flat_list(self, ledger_json):
        """THE SECOND FAULT. The old parser demanded a list and refused a mapping.

        This pins the schema the production parser must handle, so a future
        rewrite of either side cannot quietly reintroduce the mismatch.
        """
        assert isinstance(ledger_json, dict), (
            f"the committed ledger is {type(ledger_json).__name__}; the gate's "
            f"parser and this record must agree on the shape"
        )
        assert isinstance(ledger_json.get("authorisations"), list)


class TestEveryRealAuthorisationIsHonoured:
    def test_the_two_readings_of_the_ledger_agree(self, mod, ledger_json):
        """CROSS-VERIFY THE EXTRACTION, do not trust 1 route to it.

        The reader walks `authorisations[].rounds[]`; this recomputes the same set
        straight from the parsed JSON. If they differ, the reader is dropping or
        inventing rounds and every count below would be measuring the wrong thing.
        """
        from_reader = mod._paid_ledger.authorised_rounds()
        from_json = {r for e in ledger_json["authorisations"] for r in e.get("rounds", [])}
        assert from_reader == from_json, (
            f"reader and a direct parse disagree on the authorised rounds; "
            f"reader only: {from_reader - from_json}, file only: {from_json - from_reader}"
        )

    def test_the_ledger_is_not_empty(self, mod, ledger_json):
        """ANTI-VACUITY. Every round-by-round loop below is vacuous on an empty
        ledger, and an empty ledger is indistinguishable from a broken reader.
        The count is EXTRACTED from the file, never restated here: hardcoding 7
        would go red on the founder's next authorisation, which is not a defect.
        """
        n_rounds = len({r for e in ledger_json["authorisations"]
                        for r in e.get("rounds", [])})
        assert n_rounds > 0, "the committed ledger names no rounds at all"
        assert len(mod._paid_ledger.authorised_rounds()) == n_rounds

    def test_every_authorised_round_is_authorised_by_the_gate(self, mod):
        """THE ROUND TRIP THE 11 TESTS NEVER RAN.

        Before the fix this failed on all 7 rounds, twice over: first
        "no authorisation ledger at ...", then, with the path corrected,
        "authorisation ledger is not a list of entries".
        """
        rounds = sorted(mod._paid_ledger.authorised_rounds())
        refused = {}
        for rn in rounds:
            ok, reason = mod._paid_is_authorised(rn)
            if not ok:
                refused[rn] = reason
        assert not refused, (
            f"{len(refused)} of {len(rounds)} rounds the founder authorised are "
            f"refused by the gate: {refused}"
        )

    def test_the_gate_quotes_the_founders_own_words_from_the_real_file(self, mod, ledger_json):
        """The reason must carry text that is IN the committed record.

        This is what separates reading the real ledger from reading anything else:
        the quote is compared against the file's own `founder_verbatim`, extracted
        here rather than restated, so a gate that invented a plausible reason or
        read a stale fixture fails.
        """
        for entry in ledger_json["authorisations"]:
            quotes = entry.get("founder_verbatim") or []
            assert quotes, f"entry {entry.get('id')!r} carries no founder_verbatim"
            longest = max((q.strip() for q in quotes), key=len)
            for rn in entry.get("rounds", []):
                ok, reason = mod._paid_is_authorised(rn)
                assert ok, f"{rn} refused: {reason}"
                assert longest[:40] in reason, (
                    f"the gate's reason for {rn} does not quote the founder's "
                    f"words from the committed file.\n  expected to contain: "
                    f"{longest[:40]!r}\n  got: {reason!r}"
                )

    def test_paid_seats_are_selected_for_a_really_authorised_round(self, mod, ledger_json, capsys):
        """select_models, executed end to end against the real record.

        The seat names come from the ledger entry itself, so this cannot pass by
        naming a seat the founder did not authorise.
        """
        entry = ledger_json["authorisations"][0]
        rn = entry["rounds"][0]
        paid = [s for s in entry.get("paid_seats", []) if s in {m[0] for m in mod._ALL}]
        assert paid, f"entry {entry.get('id')!r} names no paid seat in the roster"
        chosen = [s[0] for s in mod.select_models(",".join(paid), rn)]
        assert chosen == [m[0] for m in mod._ALL if m[0] in paid]
        assert "PAID DISPATCH AUTHORISED" in capsys.readouterr().out


class TestTheGateStillRefusesWhatItShould:
    """THE FIX MUST NOT HAVE TRADED A REFUSAL FOR A PASS.

    Repointing a gate at a file that authorises 7 rounds is worth nothing if it
    now authorises everything.
    """

    def test_a_round_that_is_not_in_the_real_ledger_is_refused(self, mod):
        rounds = mod._paid_ledger.authorised_rounds()
        for invented in ("maths_panel_2026-09-28_unauthorised",
                         "check_my_work_2026-09-28",
                         ""):
            assert invented not in rounds, f"{invented!r} is genuinely authorised"
            ok, reason = mod._paid_is_authorised(invented)
            assert not ok, f"the gate authorised {invented!r}, which is in no entry"
            assert "no ledger entry" in reason

    def test_near_misses_on_a_real_round_name_are_refused(self, mod):
        """EXACT MATCH, the reader's own stated rule, executed against the real
        names: "the guard must keep asking 'was this authorised?' and must never
        drift into asking 'is this recent?'."
        """
        real = sorted(mod._paid_ledger.authorised_rounds())[0]
        for near in (real + "_r9", real[:-1], real.upper(), real + " ", " " + real):
            if near in mod._paid_ledger.authorised_rounds():
                continue
            ok, _ = mod._paid_is_authorised(near)
            assert not ok, (
                f"{near!r} was authorised by prefix, case or whitespace drift "
                f"from the real round {real!r}"
            )

    def test_select_models_refuses_a_paid_seat_on_an_unauthorised_round(self, mod):
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx,ge", "maths_panel_2026-09-28_unauthorised")
        msg = str(e.value)
        assert "REFUSED" in msg and "cx" in msg and "ge" in msg
        # The remedy it prints must describe the schema the file really uses,
        # or it sends the next reader to write an entry the gate cannot read.
        assert "founder_verbatim" in msg and "authorisations" in msg

    def test_free_seats_are_never_gated_by_the_real_ledger(self, mod):
        """A free round must not become refusable because of a money guard."""
        assert [s[0] for s in mod.select_models("cc2,fable", "any_unauthorised_round")] \
            == ["cc2", "fable"]
        assert [s[0] for s in mod.select_models("", "any_unauthorised_round")] \
            == [m[0] for m in mod._ALL if m[0] in mod.FREE_SEATS]
