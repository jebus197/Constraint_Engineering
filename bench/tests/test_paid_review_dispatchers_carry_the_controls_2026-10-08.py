"""Every PAID review dispatcher carries the panel-launch controls, or is registered.

THE FOUNDER'S INSTRUCTION, 2026-10-08: *"And fix the deficiencies you identified in
launching the panel reviews properly. These need to be carried over to paid panel
reviews too."*

WHAT WAS MEASURED BEFORE BUILDING ANYTHING. Of 72 files that reach a paid transport,
only 4 are REVIEW DISPATCHERS -- files that read a `BRIEF.md` from disk and send it
to seats. The other 68 send prompts built in code and are not panel reviews at all.
Of those 4, exactly 1 carries every control, and it is
`bench/confer_maths_panel_2026-09-05.py`, the live route -- which handles PAID seats
as well as free ones, so the controls already reach a paid review through it. The
other 3 are dated August one-off scripts that carry none.

SO THE INSTRUCTION WAS ALREADY SATISFIED FOR THE LIVE ROUTE, and what was missing
was anything ENFORCING it. That is the additive standard's symmetric half: a control
nothing reaches is not additive, and a control nothing prevents bypassing is not
either. This file is the ratchet.

THE 3 HISTORICAL FILES ARE NOT DELETED AND NOT SILENTLY EXEMPTED. They stay in the
tree (`POINT, NEVER PRUNE`) and their registry entries now name all 5 controls they
bypass, where before 2026-10-08 each claimed only 1. The set may not grow.

THE CONTROL SET, and why each is here:
  * `panel_brief_validate`   -- a defective brief costs money and returns nothing.
  * star-topology check      -- a blind round whose sibling's reply is reachable is
                                not blind. Founder's ruling, 2026-10-06.
  * `own_round` co-seat purge -- a RETRY clones the live tree, so a co-seat reply
                                that landed mid-round reaches the retry. This
                                happened live on 2026-10-08 and the round was killed.
  * dispatch stagger         -- seats sharing one credential collide at session
                                establishment. Founder's ruling, 2026-10-08.
  * joint-round debt check   -- star topology is 2 halves and the second was run on
                                1 of 5 rounds since the ruling, Wilson [0.0362,
                                0.6245].
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "bench" / "directives" / "universal" / "unvalidated_paid_dispatchers.json"

PAID_CALLS = ("call_openrouter", "call_deepseek", "call_gemini",
              "call_moonshot", "call_codex")

#: token -> alternatives that satisfy it. A file satisfies a control if ANY match.
CONTROLS = {
    "panel_brief_validate": ("panel_brief_validate",),
    "star topology check": ("_refuse_if_topology_is_skipped", "star_topology",
                            "check_blind_round"),
    "own_round co-seat purge": ("own_round",),
    "dispatch stagger": ("_stagger_seconds", "PANEL_STAGGER_S"),
    "joint-round debt check": ("_refuse_if_a_joint_round_is_owed",),
}

#: The measured ratchet. 3 historical review dispatchers lack the controls and are
#: registered. This number may FALL (by repairing or retiring one) and may not RISE.
MAX_UNCONTROLLED_PAID_REVIEW_DISPATCHERS = 3


def _candidates():
    out = []
    for p in sorted(list((REPO / "bench").rglob("*.py"))
                    + list((REPO / "scripts").rglob("*.py"))):
        rel = str(p.relative_to(REPO))
        parts = rel.split("/")
        if "logs" in parts or "worktrees" in parts or "tests" in parts:
            continue
        try:
            t = p.read_text(errors="ignore")
        except OSError:
            continue
        if not any(c in t for c in PAID_CALLS):
            continue
        out.append((rel, t))
    return out


def _review_dispatchers():
    """Paid-capable files that read a BRIEF.md from disk — the panel reviews."""
    return [(rel, t) for rel, t in _candidates() if "BRIEF.md" in t]


def _missing(t: str):
    return [name for name, toks in CONTROLS.items()
            if not any(tok in t for tok in toks)]


class TestThePopulationIsWhatWeThinkItIs:
    def test_there_are_paid_capable_files_at_all(self):
        """0 would mean the detector broke, not that the risk vanished."""
        assert len(_candidates()) > 20, len(_candidates())

    def test_a_review_dispatcher_is_a_narrower_thing_than_a_paid_caller(self):
        """If every paid caller counted, the ratchet would be about 68 one-off
        scripts that send code-built prompts and are not panel reviews."""
        assert len(_review_dispatchers()) < len(_candidates())
        assert len(_review_dispatchers()) >= 4, _review_dispatchers()


class TestTheLiveRouteCarriesEverything:
    def test_the_live_dispatcher_is_missing_no_control(self):
        live = "bench/confer_maths_panel_2026-09-05.py"
        got = dict(_review_dispatchers())
        assert live in got, f"{live} is no longer detected as a review dispatcher"
        assert _missing(got[live]) == [], _missing(got[live])

    def test_it_really_can_dispatch_a_paid_seat(self):
        """The controls reaching a paid review THROUGH this file is the whole
        reason the instruction is satisfied, so it is asserted rather than assumed."""
        t = dict(_review_dispatchers())["bench/confer_maths_panel_2026-09-05.py"]
        assert "FREE_SEATS" in t
        assert any(c in t for c in PAID_CALLS)
        assert "paid_dispatch_authorisations" in t, (
            "the paid path must still be gated by the authorisation ledger")


class TestTheRatchet:
    def test_no_new_uncontrolled_paid_review_dispatcher(self):
        bad = [(rel, _missing(t)) for rel, t in _review_dispatchers() if _missing(t)]
        assert len(bad) <= MAX_UNCONTROLLED_PAID_REVIEW_DISPATCHERS, (
            f"{len(bad)} paid review dispatcher(s) lack panel-launch controls, "
            f"against a ratchet of {MAX_UNCONTROLLED_PAID_REVIEW_DISPATCHERS}: "
            f"{bad}. A new paid review must go through the controlled dispatcher, "
            f"not a fresh script.")

    def test_every_uncontrolled_one_is_registered_with_its_reason(self):
        reg = json.loads(REGISTRY.read_text())["entries"]
        for rel, t in _review_dispatchers():
            miss = _missing(t)
            if not miss:
                continue
            assert rel in reg, (
                f"{rel} bypasses {miss} and is not in "
                f"{REGISTRY.relative_to(REPO)}. Register it with the reason, or "
                f"route it through the controlled dispatcher.")
            assert reg[rel].get("reason"), rel

    def test_the_registry_names_the_controls_each_one_bypasses(self):
        """BEFORE 2026-10-08 each of the 3 entries claimed 1 bypass when there
        were 5. An entry that understates the exposure is worse than none,
        because it reads as having been reviewed."""
        reg = json.loads(REGISTRY.read_text())["entries"]
        for rel, t in _review_dispatchers():
            miss = _missing(t)
            if not miss:
                continue
            named = reg[rel].get("controls_bypassed")
            assert named, f"{rel} does not name the controls it bypasses"
            for m in miss:
                assert m in named, (
                    f"{rel} bypasses {m!r} and its registry entry does not say so: "
                    f"{named}")

    def test_the_ratchet_cannot_be_satisfied_by_an_empty_control_set(self):
        """MUTATION-GRADE: emptying CONTROLS would make every file compliant and
        every test above pass vacuously."""
        assert len(CONTROLS) >= 5, CONTROLS
        for name, toks in CONTROLS.items():
            assert toks and all(isinstance(x, str) and x for x in toks), name
