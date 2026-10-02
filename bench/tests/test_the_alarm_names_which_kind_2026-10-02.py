"""The halt alarm must say WHICH KIND of irreducible, and an attempted falsifier
is not an absent one.

THE FAILURE THIS GUARDS, measured on run 1b (2026-10-02, prose target
`bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`). The run halted at round 2 and said
both of these, 0 lines apart:

    static HIL queue: 3 unresolved critical(s) (1 ladder-exhausted,
                      2 never assessed — no runnable falsifier)
    *** IRREDUCIBLE-QUEUE ALARM at round 2: 3 criticals are locked as
        irreducible, over the bound of 2.

`irreducible_escalation` means the routing ladder was EXHAUSTED.
`routing_deferred` means the item was NEVER ASSESSED — its own reason string
begins "not escalated at round {n}". Two states with opposite diagnoses: the
first points at the document, the second at the instrument. The log line was
corrected on 2026-09-22; the alarm's own notify text was not, and on
2026-09-22 a morning report built a causal chain on the wrong one and escalated
a config surface that could not have changed the outcome.

WHY THE COUNT NOW DERIVES FROM THE SPLIT. There were three expressions of one
rule: `irreducible_queue_count`, the log line's inline `_q_locked`, and the
notify text. `irreducible_queue_count` is now `sum(decomposition())`, so the
total and the split cannot disagree by construction rather than by agreement.
Equivalence to the shipped expression is proven here by execution, and
separately by z3 (`unsat` for `old != new`) and by exhaustive enumeration over
48 states.

WHAT THIS FILE DELIBERATELY DOES NOT CHANGE. The ADMISSION RULE — whether a
`routing_deferred` item should count toward the bound in its birth round, or
whether the bound should be split in two — is the founder's call, because it
changes which findings reach a human. Nothing here touches it, and
`max_irreducible_queue` stays at 2.

THE PANEL'S PROPOSAL THAT WAS REJECTED, AND WHY. The cc2 seat recommended
writing `falsifier_code` back unconditionally (today it is written only on
`result.resolved`, so a falsifier that WAS written and then crashed is filed as
never written) and called that strictly additive. It is not additive:
`falsifier_code` has three GATING readers —
`claim_ledger.claim_from_entry` sets `decidable=bool(falsifier)`,
`bugzilla_loop` activates the efficacy probe on it, and
`execution_based_matcher` filters on it — so an unconditional writeback marks a
claim settleable by a computation that ERRORED, in the very channel being
promoted. No writeback is needed: `last_falsifier_code` is already written
unconditionally, so the alarm reads it as a REPORTING fallback and says which
kind it saw. `test_an_attempted_falsifier_does_not_make_a_claim_decidable` pins
that the rejected behaviour has not crept in by another route.

STATED LIMIT: `last_falsifier_code` is truncated to 600 characters, so two
distinct falsifiers sharing a 600-character prefix group as one defect. The
defect count is therefore a LOWER bound for attempted bodies.
"""
import random

import bench.reference_runner_v3 as rr
from bench.claim_ledger import claim_from_entry
from bench.dm._types import Finding

_TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}


def _shipped_rule(entries):
    """The pre-2026-10-02 expression, reimplemented from the original source.

    Written out rather than imported BECAUSE the point is a differential: if
    this file asserted against the new code's own helper it would only confirm
    that the helper agrees with itself.
    """
    return sum(1 for e in entries.values()
               if (e.get("irreducible_escalation") or e.get("routing_deferred"))
               and e.get("status") not in _TERMINAL
               and (e.get("severity") or 0.0) >= rr.CRITICAL_SEVERITY_THRESHOLD)


def _registry(n, *, kind, falsifier="", last_falsifier="", severity=0.9, tag="a"):
    """`kind` is "exhausted" (irreducible_escalation) or "never" (routing_deferred).

    `tag` only varies the finding ids and descriptions; it does NOT vary the
    canonical ids, which `register` assigns from a per-registry counter
    (`C0001`, `C0002`, ...). That is why `_mixed` below builds ONE registry
    instead of merging two: two registries always collide on `C0001`, so
    `entries.update` overwrote instead of combining, and the first two versions
    of the mixed-kind tests asserted against a 2-item queue -- under the bound,
    so the alarm correctly returned None -- where they meant to build 4 items.
    Guessed twice before being measured; the instrument was wrong both times.
    """
    reg = rr.FindingRegistry()
    for i in range(n):
        cid = reg.register(
            Finding(finding_id=f"{tag}{i}", model_id="DeepSeek", round_idx=0,
                    flaw_class=2, severity=severity, abstraction_index=0.5,
                    description=f"claim {tag}{i} could not be settled",
                    falsifier_code=falsifier),
            "DeepSeek")
        e = reg.entries[cid]
        e["status"] = "UNCONFIRMED"
        if kind == "exhausted":
            e["irreducible_escalation"] = True
        else:
            e["routing_deferred"] = True
            e["routing_deferred_reason"] = "not escalated at round 0"
        if last_falsifier:
            e["last_falsifier_code"] = last_falsifier
    return reg


def _mixed(n_exhausted, n_never, *, falsifier="", last_falsifier=""):
    """ONE registry carrying both kinds. See `_registry`'s note on canonical ids."""
    reg = _registry(n_exhausted, kind="exhausted", falsifier=falsifier, tag="x")
    for i in range(n_never):
        cid = reg.register(
            Finding(finding_id=f"n{i}", model_id="Codex", round_idx=0,
                    flaw_class=2, severity=0.9, abstraction_index=0.5,
                    description=f"claim n{i} was never assessed",
                    falsifier_code=""),
            "Codex")
        e = reg.entries[cid]
        e["status"] = "UNCONFIRMED"
        e["routing_deferred"] = True
        e["routing_deferred_reason"] = "not escalated at round 0"
        if last_falsifier:
            e["last_falsifier_code"] = last_falsifier
    return reg


class TestTheSplitIsTheShippedRule:

    def test_the_count_is_the_sum_of_the_split(self):
        for kind in ("exhausted", "never"):
            reg = _registry(5, kind=kind)
            a, b = reg.irreducible_queue_decomposition()
            assert a + b == reg.irreducible_queue_count() == 5, (kind, a, b)

    def test_each_kind_lands_in_its_own_arm(self):
        ex = _registry(3, kind="exhausted").irreducible_queue_decomposition()
        nv = _registry(4, kind="never").irreducible_queue_decomposition()
        assert ex == (3, 0), f"ladder-exhausted items must not read as never-assessed: {ex}"
        assert nv == (0, 4), f"never-assessed items must not read as exhausted: {nv}"

    def test_an_entry_carrying_BOTH_flags_counts_once(self):
        """The shipped expression counted it once. So must the split, or the
        total inflates and a halt fires one item early."""
        reg = _registry(1, kind="exhausted")
        for e in reg.entries.values():
            e["routing_deferred"] = True
        a, b = reg.irreducible_queue_decomposition()
        assert (a, b) == (1, 0) and reg.irreducible_queue_count() == 1
        assert reg.irreducible_queue_count() == _shipped_rule(reg.entries)

    def test_equivalence_to_the_shipped_rule_over_randomised_entries(self):
        """EXECUTED, not argued. 400 randomised registries; the new total must
        equal the old expression on every one."""
        random.seed(20261002)
        T = rr.CRITICAL_SEVERITY_THRESHOLD
        statuses = [None, "OPEN", "UNCONFIRMED", "MERGED", "CLOSED", "REFUTED",
                    "DUPLICATE", "CONFIRMED", "ROUTED"]
        sevs = [None, 0.0, 0.5, T - 0.01, T, 0.9, 1.0]
        for trial in range(400):
            reg = rr.FindingRegistry()
            reg.entries = {
                f"C{i:04d}": {
                    "irreducible_escalation": random.choice([True, False, None, ""]),
                    "routing_deferred": random.choice([True, False, None, ""]),
                    "status": random.choice(statuses),
                    "severity": random.choice(sevs)}
                for i in range(random.randint(0, 9))}
            a, b = reg.irreducible_queue_decomposition()
            assert a + b == reg.irreducible_queue_count() == _shipped_rule(reg.entries), (
                f"trial {trial}: split=({a},{b}) count={reg.irreducible_queue_count()} "
                f"shipped={_shipped_rule(reg.entries)}")

    def test_terminal_and_low_severity_are_excluded_by_both(self):
        """ANTI-FALSE-POSITIVE: the split must not widen the queue."""
        reg = _registry(3, kind="never")
        for e in list(reg.entries.values())[:1]:
            e["status"] = "CLOSED"
        for e in list(reg.entries.values())[1:2]:
            e["severity"] = 0.1
        a, b = reg.irreducible_queue_decomposition()
        assert a + b == 1 == _shipped_rule(reg.entries), (a, b)


class TestTheAlarmSaysWhichKind:

    def test_a_never_assessed_queue_is_not_called_locked(self):
        """THE RUN 1B DEFECT. The notify text asserted a mechanism the code had
        explicitly declined to assert."""
        alarm = rr.build_irreducible_queue_alarm(
            _registry(3, kind="never"), rr.RunnerConfig(), 2)
        assert alarm is not None
        text = alarm["notify"]
        assert "NEVER ASSESSED" in text, text
        assert "3 criticals are locked as irreducible" not in text, (
            f"the alarm still calls never-assessed items locked: {text}")

    def test_the_notify_names_both_counts(self):
        alarm = rr.build_irreducible_queue_alarm(
            _mixed(2, 2), rr.RunnerConfig(), 2)
        text = alarm["notify"]
        assert "2 with the routing ladder EXHAUSTED" in text, text
        assert "2 NEVER ASSESSED" in text, text

    def test_a_fully_exhausted_queue_still_reads_as_exhausted(self):
        """ANTI-REGRESSION: the genuine case must not be relabelled."""
        alarm = rr.build_irreducible_queue_alarm(
            _registry(3, kind="exhausted"), rr.RunnerConfig(), 2)
        text = alarm["notify"]
        assert "3 with the routing ladder EXHAUSTED" in text, text
        assert "0 NEVER ASSESSED" in text, text


class TestAnAttemptedFalsifierIsNotAnAbsentOne:

    def test_an_attempted_body_is_reported_as_attempted(self):
        alarm = rr.build_irreducible_queue_alarm(
            _registry(3, kind="never", last_falsifier="assert compute() == 42\n"),
            rr.RunnerConfig(), 2)
        items = alarm["evidence"]
        assert all(x["falsifier_attempted"] for x in items), items
        assert not any(x["falsifier_present"] for x in items), (
            "a crashed falsifier must not read as a resolved one")
        assert alarm["items_with_attempted_falsifier_only"] == 3, (
            f"the attempted-only count is computed but not reported: {alarm}")
        assert alarm["items_without_falsifier"] == 0, alarm

    def test_no_body_at_all_still_reads_as_absent(self):
        """ANTI-FALSE-POSITIVE: the fallback must not invent a falsifier."""
        alarm = rr.build_irreducible_queue_alarm(
            _registry(3, kind="never"), rr.RunnerConfig(), 2)
        items = alarm["evidence"]
        assert not any(x["falsifier_attempted"] for x in items), items

    def test_identical_attempted_bodies_group_as_one_defect(self):
        """3 items, 1 defect. Before, each body-less item got the unique
        synthetic key `__no_falsifier__{cid}` and 3 identical falsifiers were
        reported as 3 distinct defects."""
        alarm = rr.build_irreducible_queue_alarm(
            _registry(3, kind="never", last_falsifier="assert f() == 1\n"),
            rr.RunnerConfig(), 2)
        assert alarm.get("distinct_defects") == 1, alarm.get("distinct_defects")

    def test_an_attempted_body_never_groups_with_a_resolved_one(self):
        """Same text, different provenance, so they are not the same evidence."""
        alarm = rr.build_irreducible_queue_alarm(
            _mixed(2, 2, falsifier="assert f() == 1\n",
                   last_falsifier="assert f() == 1\n"),
            rr.RunnerConfig(), 2)
        assert alarm.get("distinct_defects") == 2, (
            f"an attempted body grouped with a resolved one: "
            f"{alarm.get('distinct_defects')}")

    def test_an_attempted_falsifier_does_not_make_a_claim_decidable(self):
        """THE REJECTED PROPOSAL, pinned. Writing `falsifier_code` back
        unconditionally would flip `decidable` for a claim whose computation
        ERRORED. `claim_ledger` is the reader that would have been corrupted."""
        reg = _registry(1, kind="never", last_falsifier="assert f() == 1\n")
        cid, entry = next(iter(reg.entries.items()))
        assert not entry.get("falsifier_code"), (
            "the crashed body was written into falsifier_code; claim_ledger will "
            "now call this claim decidable by a computation that errored")
        assert claim_from_entry(cid, entry).decidable is False
