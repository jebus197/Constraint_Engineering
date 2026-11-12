"""The Stop hook must refuse a narration turn, and must never trap the session.

The founder, 2026-09-10: "Can you not write some kind of mechanical 'is blocker'
/ 'is not blocker' ... script ... to prevent this? You can't self-diagnose/repair
the exact cause beyond this?"

Measured that day: turns carrying `d` made a median of 3 tool calls against 13
without it, Mann-Whitney p = 0.0097 -- so `d` genuinely suppresses work. But 8 of
16 turns carrying NO `d` still stopped after 12 calls or fewer, Wilson
[28.00%, 72.00%]. Half the stops had nothing telling them to stop.

WHY THIS FILE MATTERS MORE THAN THE HOOK. Before it, all 4 installed hooks were
UserPromptSubmit context injectors that made 0 subprocess calls, emitted 0
blocking decisions, and always exited 0 -- the shape task 1.1 named as "a guard
that cannot fail is not a guard". These tests exist to prove this one CAN fail.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "work_not_narrate.py"
LIVE = Path.home() / ".claude" / "hooks" / "work_not_narrate.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("wnn", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestItCanActuallyFail:
    def test_the_self_test_passes(self):
        r = subprocess.run([sys.executable, str(HOOK), "--self-test"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "7 of 7 correct" in r.stdout

    def test_it_blocks_pure_narration(self, mod):
        block, why = mod.verdict(0, 5000, False, False, 40, "L1")
        assert block and "NARRATED" in why and "L1" in why

    def test_it_blocks_a_stop_after_a_SUCCESSFUL_working_turn(self, mod):
        """THE CASE THE FIRST VERSION MISSED, and it is the whole complaint.

        The founder watched me work, commit, report and stop, once per turn, for
        hours. Fed this session's own transcript the first predicate returned
        "allow the stop" every time, because it exempted any turn making 6+ tool
        calls or landing a commit -- which is exactly the pattern he objected to.
        A stop is now refused whenever OPEN work remains.
        """
        block, why = mod.verdict(30, 200, True, False, 40, "L1")
        assert block, "a turn that worked and committed must still continue"
        assert "still OPEN" in why and "L1" in why

    def test_it_returns_exit_code_2_which_is_what_blocks(self, mod, tmp_path):
        """Exit 0 would make it another guard that cannot fail."""
        assert mod.MIN_TOOL_CALLS > 0 and mod.MIN_PROSE > 0
        src = HOOK.read_text(encoding="utf-8")
        assert "return 2" in src, "the hook has no path that blocks a stop"


class TestItHonoursHisCommand:
    def test_d_overrides_everything(self, mod):
        block, why = mod.verdict(0, 99999, False, True, 999, "L1")
        assert not block and "`d`" in why, (
            "a hook that overrode his own discuss command would be worse than "
            "the defect it treats")


class TestItCannotFireOnTheOrdinaryCase:
    @pytest.mark.parametrize("calls,prose,commit,n_open,blocker,why", [
        (30, 5000, False, 0, False, "nothing left to do"),
        (30, 200, True, 0, False, "list empty after a working turn"),
        (5, 3000, False, 40, True, "a blocker was raised, so stopping is correct"),
    ])
    def test_it_stays_silent_when_it_should(self, mod, calls, prose, commit,
                                            n_open, blocker, why):
        block, _ = mod.verdict(calls, prose, commit, False, n_open, "X", blocker)
        assert not block, why

    def test_a_park_verdict_is_not_a_reason_to_stop(self, mod):
        """The triage tool parks most things; parking must not end the turn."""
        _, why = mod.verdict(10, 500, False, False, 40, "L1", False)
        assert "A PARK verdict is not a reason to stop" in why


class TestItCannotTrapTheSession:
    def test_the_budget_is_always_FINITE_which_is_what_prevents_a_trap(self, mod):
        """★ REPLACES `test_stop_hook_active_exits_immediately`, 2026-11-12.

        THE OLD TEST ASSERTED A BEHAVIOUR THIS PROJECT DELIBERATELY RETIRED. It
        required exit 0 whenever `stop_hook_active` was true. The hook's own line
        751 says the opposite in as many words -- *"`stop_hook_active` is NOT read
        as 'give up'"* -- and `test_stop_hook_active_no_longer_surrenders` below
        asserts THAT. 2 tests in this file therefore demanded opposite outcomes
        from the same input.

        AND IT WAS PASSING FOR AN INCIDENTAL REASON: the live counter happened to
        hold more refusals than the budget, so the hook yielded on the BUDGET and
        the test credited the yield to `stop_hook_active`. Raising the budget on
        his ruling of 2026-11-12 exposed it -- the same input then returned 2.

        WHAT ACTUALLY PREVENTS A TRAP IS THAT THE BUDGET IS FINITE, so this tests
        that instead. The bound must never be unbounded however much movable work
        exists, and it must yield once spent.
        """
        assert mod.refusal_budget() <= mod.MAX_REFUSALS_CEILING
        assert mod.MAX_REFUSALS_CEILING < 10_000, "a ceiling this high is no bound"
        assert mod.refusal_budget() >= mod.MAX_REFUSALS_PER_TURN, (
            "the conditional budget must never fall BELOW the original 8")

    def test_it_yields_even_with_stop_hook_active_once_the_budget_is_spent(
            self, tmp_path, monkeypatch):
        """The trap-prevention path, driven to exhaustion rather than assumed."""
        import importlib.util as _iu
        spec = _iu.spec_from_file_location("wnn_spent", HOOK)
        m = _iu.module_from_spec(spec)
        spec.loader.exec_module(m)
        monkeypatch.setattr(m, "STATE", tmp_path / "s.json")
        monkeypatch.setattr(m, "MAX_REFUSALS_CEILING", 3)
        monkeypatch.setattr(m, "MAX_REFUSALS_PER_TURN", 3)
        used = 0
        for _ in range(10):
            used = m.spend_refusal("turn-trap")
        assert used > m.refusal_budget(), (
            f"after 10 refusals, {used} must exceed the budget "
            f"{m.refusal_budget()} or the session could be trapped")

    def test_the_budget_rises_only_when_work_is_MOVABLE(self, mod, monkeypatch):
        """His ruling: 8 for work that needs him, more for work that does not."""
        monkeypatch.setattr(mod, "movable_count", lambda: 0)
        assert mod.refusal_budget() == mod.MAX_REFUSALS_PER_TURN, (
            "with nothing movable the budget must stay exactly as it was")
        monkeypatch.setattr(mod, "movable_count", lambda: 1)
        assert mod.refusal_budget() == mod.MAX_REFUSALS_PER_TURN
        monkeypatch.setattr(mod, "movable_count", lambda: 99)
        assert mod.refusal_budget() == mod.MAX_REFUSALS_CEILING, (
            "a large movable count must be capped by the ceiling, not unbounded")

    def test_a_broken_payload_never_breaks_the_session(self):
        r = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 0

    def test_a_missing_transcript_is_survivable(self, mod):
        assert mod.turn_signals(Path("/nonexistent/x.jsonl")) == (0, 0, False, False)


class TestItIsVersionedAndWired:
    def test_the_repo_copy_matches_the_live_one(self):
        """3 of the 4 earlier hooks existed in NO repository. Not this one."""
        if not LIVE.is_file():
            pytest.skip("no live hook on this machine")
        assert HOOK.read_bytes() == LIVE.read_bytes(), (
            "the versioned copy has drifted from the one that actually runs")

    def test_it_is_registered_as_a_Stop_hook(self):
        s = Path.home() / ".claude" / "settings.json"
        if not s.is_file():
            pytest.skip("no settings.json on this machine")
        d = json.loads(s.read_text())
        hooks = d.get("hooks", {})
        armed = "work_not_narrate" in json.dumps(hooks.get("Stop", []))
        # A DELIBERATE PARK IS NOT AN UNWIRED ADDITION. The founder parked this
        # hook on 2026-09-11 -- "park the hook thing we built" -- and parking
        # preserves the entry under a `_PARKED_` key rather than deleting it, so
        # restoring it is one rename. What this guard exists to catch is the
        # entry VANISHING, which is the unwired-addition half of the additive
        # standard. So a parked entry passes and a missing one still fails.
        parked = any(k.startswith("_PARKED_") and "work_not_narrate" in json.dumps(v)
                     for k, v in hooks.items())
        assert armed or parked, (
            "the hook exists and nothing calls it, and no parked entry preserves "
            "it either, which is the unwired-addition half of the additive standard")

    #: Every `UserPromptSubmit` hook, BY NAME. A bare count was the first form
    #: of this assertion and it had to be edited on 2026-10-03 when
    #: `study_pulse.py` became the 6th -- at which point a count says only that
    #: the number changed, not WHICH capability arrived or left. The named set
    #: fails on a REMOVAL (the thing worth protecting) and on an addition
    #: nobody recorded here (the additive standard's other half), and it says
    #: what each one is for so a later reader can tell a loss from a rename.
    EXPECTED_PROMPT_HOOKS = {
        "prompt_clock.py",        # the sole mechanism for temporal awareness
        "mc_commands.py",         # the standing hard constraints, f and sy
        "compaction_watch.py",    # tells the founder a compaction happened
        "ffafp_audit.py",         # names which FFAFP steps left no trace
        "task_list_pulse.py",     # the open/done/blocked counts
        "study_pulse.py",         # why the runs exist; falls silent when CLOSED
    }

    def test_the_existing_prompt_hooks_still_run(self):
        s = Path.home() / ".claude" / "settings.json"
        if not s.is_file():
            pytest.skip("no settings.json")
        d = json.loads(s.read_text())
        # READ THE INNER HOOKS, not the matcher entries. An earlier version
        # counted `len(hooks["UserPromptSubmit"])`, which is 1 -- one matcher
        # holding them all. It fired during the settings edit and correctly
        # REFUSED to write, which is a pre-write P-pass doing its job on a file
        # whose corruption would break every session.
        names = {Path(h.get("command", "").split()[-1]).name
                 for m in d["hooks"]["UserPromptSubmit"]
                 for h in m.get("hooks", [])}
        missing = self.EXPECTED_PROMPT_HOOKS - names
        extra = names - self.EXPECTED_PROMPT_HOOKS
        assert not missing, (
            f"a prompt hook that was wired no longer runs: {sorted(missing)}. "
            "A capability may not leave without a RETIRED entry saying so.")
        assert not extra, (
            f"a prompt hook runs that this test does not name: {sorted(extra)}. "
            "Add it to EXPECTED_PROMPT_HOOKS with a comment saying what it is "
            "for -- an unrecorded addition is the other half of the additive "
            "standard.")


# ---------------------------------------------------------------------------
# THE REFUSAL BUDGET — added 2026-09-10 19:15 BST after the founder asked
# "You still stopped?"
#
# He was right and the bound was the defect. `stop_hook_active` is a BOOLEAN the
# harness sets after the first refusal, so honouring it as "give up" capped this
# hook at exactly 1 refusal per turn: it converted "one task then report" into
# "two tasks then report" and no further. Observed twice in a row -- the hook
# refused, L1 was done, the turn ended; the hook refused, R2 was done, the turn
# ended.
#
# Refusals are now counted per turn and the budget is 8. It is a BUDGET rather
# than an absence of one because a hook that can never yield would trap a session
# that has genuinely finished, and he is not always at the keyboard.
# ---------------------------------------------------------------------------

class TestTheRefusalBudget:
    def test_it_refuses_more_than_once_per_turn(self, mod, tmp_path, monkeypatch):
        """The whole point. One refusal per turn was the defect."""
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        counts = [mod.spend_refusal("turn-A") for _ in range(3)]
        assert counts == [1, 2, 3], counts

    def test_it_yields_once_the_budget_is_spent(self, mod, tmp_path, monkeypatch):
        """A hook that can never yield traps a session that has finished."""
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        for _ in range(mod.MAX_REFUSALS_PER_TURN):
            mod.spend_refusal("turn-B")
        assert mod.spend_refusal("turn-B") > mod.MAX_REFUSALS_PER_TURN

    def test_a_new_turn_resets_the_budget(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        for _ in range(5):
            mod.spend_refusal("turn-C")
        assert mod.spend_refusal("turn-D") == 1, (
            "a new user message must restore the full budget")

    def test_an_unknown_turn_allows_the_stop(self, mod, tmp_path, monkeypatch):
        """Fail OPEN on the continuation question, deliberately.

        A guard that refuses on its own malfunction is the shape this project
        keeps having to withdraw. The cost of a wrong yield is one extra prompt
        from him; the cost of a wrong refusal is a session he cannot end.
        """
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        assert mod.spend_refusal("") > mod.MAX_REFUSALS_PER_TURN

    def test_an_unwritable_state_file_allows_the_stop(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "STATE", tmp_path / "no" / "such" / "dir" / "s.json")
        assert mod.spend_refusal("turn-E") > mod.MAX_REFUSALS_PER_TURN

    def test_stop_hook_active_no_longer_surrenders(self, mod):
        """It reports that a refusal happened; it does not decide the outcome."""
        src = (ROOT / "hooks" / "work_not_narrate.py").read_text(encoding="utf-8")
        assert "is NOT read as \"give up\"" in src, (
            "the hook still treats stop_hook_active as a reason to give up, which "
            "caps it at 1 refusal per turn")


# ─────────────────────────────────────────────────────────────────────────────
# OWNERSHIP: the entry the gate NAMES must be one I can actually move.
#
# ★ N3's REPAIR HAD NO TEST UNTIL 2026-11-10. `open_items()` used to return
# `opens[0]` -- the first open entry in document order -- so the gate spent
# turns pushing at entries that could not be advanced without him: it named
# B21 (the model-and-role selection question) on every turn of 2026-11-09
# while B21 awaited his ruling. The repair added `_first_movable`, which
# prefers an entry that is not OWED. Measured 2026-11-10: `_first_movable`
# was reached by **0** tests, so the repair was an addition nothing executed,
# which `additive-standard`'s symmetric form forbids.
#
# THE FALLBACK IS KEPT AND IS TESTED TOO: naming nothing would make the
# refusal useless, so an undecidable classification falls back to `opens[0]`
# exactly as before, and the COUNT is never affected either way.
# ─────────────────────────────────────────────────────────────────────────────

class _E:
    """A minimal stand-in for a task-list entry: ident, state, ruled."""

    def __init__(self, ident, state="OPEN", ruled=None):
        self.ident, self.state, self.ruled = ident, state, ruled


class TestTheGateNamesAMovableEntry:

    @staticmethod
    def _synthetic_markers_dir(tmp_path, monkeypatch, bodies_map,
                               all_owed=False):
        """A stand-in `MARKERS` directory, with NO pollution of the real one.

        ★ 2 FAILED ATTEMPTS ARE RECORDED HERE BECAUSE EACH WAS A DIFFERENT
        MISTAKE, and both were found by running the tests rather than by
        reading them.

        FIRST: `MARKERS` serves 2 purposes in this hook. `open_items` does
        `sys.path.insert(0, str(MARKERS))` and then imports
        `task_list_markers` from it, while `_first_movable` loads the decision
        classifier from the same directory. A temp dir holding only the
        classifier made `open_items` return `(0, "")` -- the import failed and
        the fail-safe swallowed it -- so the test failed for a reason that had
        nothing to do with the property under test.

        SECOND: copying `task_list_markers.py` into the temp dir fixed that and
        broke the 2 tests that read the LIVE list, because the temp copy was
        cached in `sys.modules` and its module-level `LIST` constant pointed
        into a directory pytest had already removed. A test that leaves global
        state behind fails its NEIGHBOURS, which is the worst kind to debug.

        WHAT IS DONE INSTEAD: the REAL module is pinned in `sys.modules` with
        `monkeypatch.setitem`, so the hook's own import finds it and the pin is
        undone afterwards; `sys.path` is replaced by a copy so the hook's
        insert cannot persist; and no second copy of the module is ever made.
        `parse_entries` takes its path as an argument, so pinning the real
        module and patching `TASKS` is sufficient.
        """
        import sys as _sys
        #: ORDER MATTERS: copy `sys.path` FIRST so every mutation below -- mine
        #: and the hook's own insert -- is undone, THEN make the real module
        #: importable, THEN pin it.
        monkeypatch.setattr(_sys, "path", list(_sys.path))
        _sys.path.insert(0, str(ROOT / "scripts"))
        import task_list_markers as _real
        monkeypatch.setitem(_sys.modules, "task_list_markers", _real)
        kind = ("    return {'kind': 'OWED'}\n" if all_owed else
                "    return {'kind': 'OWED' if body == 'owed' else 'MINE'}\n")
        (tmp_path / "how_many_decisions_actually_need_him_2026-11-01.py"
         ).write_text(
            f"def bodies():\n    return {bodies_map!r}\n"
            "def classify_text(state, ruled, body):\n" + kind)
        return tmp_path

    def test_first_movable_skips_an_entry_that_still_asks_him(self, mod,
                                                              tmp_path,
                                                              monkeypatch):
        """DRIVES THE SKIP DIRECTLY, by giving the real function a real
        classifier to load.

        `_first_movable` loads
        `how_many_decisions_actually_need_him_2026-11-01.py` from the directory
        named by `MARKERS`, so pointing `MARKERS` at a temporary directory
        holding a stand-in classifier exercises the skip without stubbing the
        function under test.

        ★ MY FIRST VERSION OF THIS TEST ASSERTED ONLY `isinstance(got, str)`,
        which every return value satisfies -- an addition that reached nothing,
        and exactly what `additive-standard`'s symmetric form forbids. It was
        replaced rather than kept beside this one.
        """
        (tmp_path / "how_many_decisions_actually_need_him_2026-11-01.py"
         ).write_text(
            "def bodies():\n"
            "    return {'X1': 'this one is owed', 'X2': 'this one is mine'}\n"
            "def classify_text(state, ruled, body):\n"
            "    return {'kind': 'OWED' if 'owed' in body else 'MINE'}\n")
        monkeypatch.setattr(mod, "MARKERS", str(tmp_path))
        got = mod._first_movable([_E("X1"), _E("X2")])
        assert got == "X2", (
            f"it named {got!r}; X1 is OWED and must be skipped in favour of X2")

    def test_first_movable_returns_empty_when_every_entry_is_owed(
            self, mod, tmp_path, monkeypatch):
        """ANTI-VACUITY for the test above: if it always returned the 2nd
        entry, this would still pass, so both directions are asserted."""
        (tmp_path / "how_many_decisions_actually_need_him_2026-11-01.py"
         ).write_text(
            "def bodies():\n"
            "    return {'X1': 'owed', 'X2': 'owed'}\n"
            "def classify_text(state, ruled, body):\n"
            "    return {'kind': 'OWED'}\n")
        monkeypatch.setattr(mod, "MARKERS", str(tmp_path))
        assert mod._first_movable([_E("X1"), _E("X2")]) == ""

    def test_open_items_prefers_a_movable_entry_over_document_order(
            self, mod, tmp_path, monkeypatch):
        """THE PROPERTY THE N3 REPAIR EXISTS FOR, on a subject that can fail.

        ★ MY FIRST ATTEMPT AT THIS USED THE LIVE TASK LIST AND WAS VACUOUS.
        The mutation board proved it: reverting `open_items` to `opens[0]`
        left the guard GREEN, because today the first open entry (B22, the
        general-purpose-STEM-calculator question) classifies GRANTED rather
        than OWED, so `opens[0]` and `_first_movable` happen to agree. A probe
        on data where the defect cannot show is a probe that tests nothing --
        the same shape as a guard whose every input is refused for another
        reason.

        Both the task list and the classifier are therefore synthetic here, so
        the first open entry IS owed and document order IS the wrong answer.
        """
        tasks = tmp_path / "LIST.md"
        tasks.write_text(
            "# t\n\n"
            "**Z1. An entry that still asks him something.** body\n"
            "<!-- task: Z1 | state: OPEN | status: PROPOSED -->\n\n"
            "**Z2. An entry I can move myself.** body\n"
            "<!-- task: Z2 | state: OPEN | status: PROPOSED -->\n")
        self._synthetic_markers_dir(tmp_path, monkeypatch,
                                    {"Z1": "owed", "Z2": "mine"})
        monkeypatch.setattr(mod, "TASKS", tasks)
        monkeypatch.setattr(mod, "MARKERS", str(tmp_path))

        n_open, named = mod.open_items()
        assert n_open == 2, n_open
        assert named == "Z2", (
            f"the gate named {named!r}; Z1 awaits HIM and Z2 is movable, so "
            f"document order is the N3 defect returning")

    def test_open_items_falls_back_to_document_order_when_all_are_owed(
            self, mod, tmp_path, monkeypatch):
        """ANTI-VACUITY: naming nothing would make the refusal useless, so the
        fallback is asserted on a subject where every entry is owed."""
        tasks = tmp_path / "LIST.md"
        tasks.write_text(
            "# t\n\n**Z1. First.** body\n"
            "<!-- task: Z1 | state: OPEN | status: PROPOSED -->\n\n"
            "**Z2. Second.** body\n"
            "<!-- task: Z2 | state: OPEN | status: PROPOSED -->\n")
        self._synthetic_markers_dir(tmp_path, monkeypatch,
                                    {"Z1": "owed", "Z2": "owed"},
                                    all_owed=True)
        monkeypatch.setattr(mod, "TASKS", tasks)
        monkeypatch.setattr(mod, "MARKERS", str(tmp_path))
        n_open, named = mod.open_items()
        assert (n_open, named) == (2, "Z1"), (n_open, named)

    def test_the_named_entry_is_not_one_that_awaits_him(self, mod):
        """EXECUTED against the live list, which is the only honest subject.

        `_first_movable` reloads the classifier from disk by design, so a
        stubbed classifier cannot reach it. The property that matters is
        observable without stubbing: whatever it names must not classify OWED.
        """
        import importlib.util as _ilu
        import pathlib as _pl
        spec = _ilu.spec_from_file_location(
            "_cls_probe",
            _pl.Path(mod.MARKERS)
            / "how_many_decisions_actually_need_him_2026-11-01.py")
        cls = _ilu.module_from_spec(spec)
        spec.loader.exec_module(cls)

        n_open, named = mod.open_items()
        if n_open == 0:
            pytest.skip("no open entries, so there is nothing to name")
        bodies = cls.bodies()
        import sys as _s
        _s.path.insert(0, str(ROOT / "scripts"))
        import task_list_markers as _tlm
        opens = [e for e in _tlm.parse_entries() if e.state == "OPEN"]
        movable = [e.ident for e in opens
                   if cls.classify_text(e.state, e.ruled,
                                        bodies.get(e.ident, ""))["kind"]
                   != "OWED"]
        if not movable:
            pytest.skip("every open entry awaits him; the fallback is correct")
        assert named in movable, (
            f"the gate named {named}, which awaits HIM, while {movable[:3]} "
            f"could be moved — this is the N3 defect returning")

    def test_the_count_is_never_affected_by_the_choice(self, mod):
        import sys as _s
        _s.path.insert(0, str(ROOT / "scripts"))
        import task_list_markers as _tlm
        n_open, _named = mod.open_items()
        assert n_open == len([e for e in _tlm.parse_entries()
                              if e.state == "OPEN"]), (
            "the ownership choice changed the COUNT, which it must never do")

    def test_an_undecidable_classification_falls_back_rather_than_losing_the_gate(
            self, mod, monkeypatch):
        """FAILS TOWARD NAMING SOMETHING. An exception inside the classifier
        must give "" so the caller uses document order, never crash."""
        monkeypatch.setattr(mod, "MARKERS", "/no/such/directory")
        assert mod._first_movable([_E("B1"), _E("B2")]) == ""

    def test_open_items_still_names_something_when_nothing_is_movable(
            self, mod, monkeypatch):
        monkeypatch.setattr(mod, "_first_movable", lambda opens: "")
        n_open, named = mod.open_items()
        if n_open == 0:
            pytest.skip("no open entries")
        assert named, "the gate named nothing, which makes its refusal useless"
