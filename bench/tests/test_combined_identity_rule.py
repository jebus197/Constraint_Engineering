"""The identity rule: two tiers, one narrow question, and both acceptance runs.

WHAT THIS FILE PINS
-------------------
Three changes landed together on 2026-08-12, on the founder's ruling, and each
one is held here.

1. FELM IS GONE FROM THE DECISION PATH. The mutation-vector tier was built to the
   panel's design and then refuted on this project's own archive: 74 of 101
   falsifiers share one identical response vector, Fisher exact p = 0.71 — no
   association whatever between its divergence and defect identity — and both
   stated acceptance cases failed. The founder's question was "if the model's
   contribution doesn't work and is ineffective, why leave it in place at all?"
   and there was no good answer. The code is deleted. The MEASUREMENT is kept as
   documentation, and a test below fails if those numbers are ever removed,
   because a measured negative result is a finding and this project does not
   discard findings.

2. THE STEM SIGNATURE IS NOW OPERATIVE inside an already-flagged location. It
   compares hard technical content — numbers, claim IDs, backticked identifiers —
   rather than wording. Re-measured over all six completed runs, 438
   same-location critical pairs labelled independently by the sentence-embedding
   backend: same-defect pairs share a median Jaccard 0.559, different-defect
   pairs 0.000, Mann-Whitney p = 1.9e-25.

3. THE COMPUTED-OUTCOME TIER IS NEW. One narrow question per candidate pair — do
   these two findings assert the same computed value or different ones — with no
   recomputation of anything. Measured the same way: 57.0% coverage, Fisher exact
   p = 1.4e-07 on the pairs it can answer, against FELM's p = 0.71 on the same
   archive — and it never once called a same-defect pair DIFFERENT in 19 such
   pairs. Its authority is bounded to MERGING, so its false-DIFFERENT errors cost
   nothing.

THE SAFETY PROPERTY, unchanged in meaning: absence of a distinctness WITNESS
means NOT COUNTED AS NEW, never "proven the same". Several tests exist only to
hold that in place.

THE ONE CLAIM A GATE MAY REST ON is `combined >= location-only`, elementwise —
verified here against all six completed runs, not asserted. Per-decision
monotonicity does NOT compose into per-series monotonicity and no test here
pretends otherwise.

ACCEPTANCE (a) PASSES and ACCEPTANCE (b) FAILS. Both are pinned. The failure is
pinned as a failure, with the exact tails, because a refuted result that quietly
stops being measured is the failure mode this whole project exists to catch.

SHADOW ONLY at the runner. `hierarchical_novelty_convergence` still defaults
False and no shipped config sets it; promoting this rule to the convergence gate
is a separate decision in a separate file.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.convergence_location import (  # noqa: E402
    WITHIN_LOCATION_THRESHOLD,
    IdentityDecision,
    Prior,
    combined_novelty_series,
    computed_outcomes,
    finding_locations,
    hierarchical_novelty_series,
    identity_decision,
    location_only_series,
    novelty_rule_divergence,
    outcome_agreement,
    quantities_agree,
    signature_similarity,
    stem_signature,
    target_symbols,
)

MODULE_SRC = (REPO / "bench" / "convergence_location.py").read_text(encoding="utf-8")

# ── the hand-built blind-spot case ──────────────────────────────────────────
# Two defects on `dedup` in ALG-02-REF-01.md, ground truth by counterfactual
# repair: fixing either leaves the other standing. Each is re-worded, because a
# rule that only works on one phrasing is not a rule.

D1_A = ("VERDICT: CONFIRM. AL-03 overstates the comparison count: `dedup` performs "
        "2016 comparisons on 64 distinct inputs, not the at-most-k the document "
        "claims. Listing A.")
D1_B = ("AL-03: the linear-time claim for `dedup` fails. Membership on a list is "
        "O(n), so Listing A is quadratic — 2016 comparisons at n=64.")
D1_C = ("Re-raising: `dedup` in Listing A is not linear; the stated comparison "
        "bound of k is exceeded at 64 inputs.")
D2_A = ("Listing A's `dedup` conflates equal-but-distinct values: `1`, `1.0` and "
        "`True` compare equal, so dedup([1, 1.0, True]) returns a single element "
        "and silently drops two distinct inputs.")
D2_B = ("Listing A `dedup` uses `==` for membership, so numerically-equal values "
        "of different types (1 vs 1.0 vs True) are treated as duplicates and lost.")

SYMS = frozenset({"dedup", "AL-03"})


def _entries(rows):
    """rows: (round, severity, description) -> a registry-shaped dict."""
    return {f"C{i:04d}": dict(canonical_id=f"C{i:04d}", open_since_round=r,
                              severity=sev, description=d)
            for i, (r, sev, d) in enumerate(rows, 1)}


_PAIR_REASONS = {"new_location": "NEW_LOCATION",
                 "first_at_location": "NEW_LOCATION",
                 "signature_merge": "MERGED",
                 "same_computed_outcome": "MERGED(outcome)",
                 "no_distinctness_witness": "NO_WITNESS",
                 "signature_split": "DISTINCT"}


def _pair_verdict(prior: str, candidate: str, symbols=SYMS) -> str:
    """The rule's answer for an isolated PAIR, taken from the rule itself.

    Deliberately routed through `identity_decision` rather than re-implemented
    here. A test that re-derives the logic it is checking cannot see that logic
    break — which is how the previous tier's live path came to be exercised by no
    test at all while 36 of them stayed green.

    Returns NEW_LOCATION when the candidate names a location the prior does not;
    that is a tier-1 answer, not a within-location one, and a test that wants the
    within-location question must not be handed it by accident.
    """
    d0 = identity_decision(prior, symbols, [])
    seen = [Prior(d0.locations, d0.signature, d0.outcomes, "PRIOR")]
    d1 = identity_decision(candidate, symbols, seen)
    return _PAIR_REASONS.get(d1.reason, d1.reason.upper())


# ── the archive ─────────────────────────────────────────────────────────────

ARCHIVE = {
    # run: (log directory glob stem, python target if it still exists, conv round)
    "exp44": ("exp44_evidence_locationkey_live", "bench/evidence.py", 12),
    "exp45": ("exp45_memory_statistics_live", "bench/dm/_memory.py", 3),
    "exp46": ("exp46_stage6_locationkey_live", "bench/dm/_shadow_stage6.py", 5),
    "exp47": ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py", 13),
    # Exp 48 and Exp 49 reviewed MARKDOWN exam documents that are no longer on
    # disk. They are still measurable: see `_symbols_for`.
    "exp48": ("exp48_chemistry_exam_live", None, 5),
    "exp49": ("exp49_engineering_exam_live", None, 6),
}

_REPORTS: dict = {}


def _report(run: str) -> dict:
    if run not in _REPORTS:
        stem = ARCHIVE[run][0]
        hits = [p for p in (REPO / "bench" / "logs").glob(f"{stem}_*/{stem}_report.json")
                if ".errata" not in str(p)]
        if not hits:
            pytest.skip(f"archived run not present: {stem}")
        _REPORTS[run] = json.loads(hits[0].read_text(encoding="utf-8"))
    return _REPORTS[run]


def _symbols_for(run: str):
    """The target's symbol set, reconstructed when the target is gone.

    For the two exam runs the document has been deleted, and the 2026-08-08 note
    recorded them as unmeasurable because of it. They are not. The symbol set of
    a markdown exam is its claim IDs, and `finding_locations` only ever
    INTERSECTS the symbol set with a description — so the union of claim IDs
    appearing across a run's own findings is identical, on claim IDs, to the full
    document's set. That is not taken on trust: it is checked, by replaying
    location-only keying and requiring it to reproduce the run's archived series
    exactly (`test_every_archived_location_series_is_reproduced`).
    """
    target = ARCHIVE[run][1]
    if target and (REPO / target).is_file():
        return target_symbols(str(REPO / target))
    ids = set()
    for e in _report(run)["registry"]["entries"].values():
        ids |= set(re.findall(r"\b([A-Z]{2}-\d{2})\b", e.get("description", "") or ""))
    return frozenset(ids)


def _archive_case(run: str):
    d = _report(run)
    archived = d["location_crit_shadow_history"]
    return d["registry"]["entries"], len(archived) - 1, archived, ARCHIVE[run][2]


def _tail(series, conv_round, k=3):
    return series[max(0, conv_round - k + 1):conv_round + 1]


# ═══════════════════════════════════════════════════════════════════════════
# 1. FELM is out of the decision path — and its refutation is still on record.
# ═══════════════════════════════════════════════════════════════════════════

class TestFelmIsGoneButItsMeasurementIsNot:

    def test_no_felm_callable_survives(self):
        import bench.convergence_location as M
        leftovers = [n for n in dir(M) if "felm" in n.lower()]
        assert leftovers == [], (
            f"FELM is refuted on this archive and was removed from the decision "
            f"path; these are still importable and could be wired back in: "
            f"{leftovers}")

    def test_nothing_executes_a_falsifier_from_this_module(self):
        """FELM's whole cost was subprocess execution. With it gone, the identity
        rule is pure computation over text — no mutation, no sandbox, no run."""
        for banned in ("falsifier_verify", "reverify_falsifier", "execute_python",
                       "subprocess", "tempfile", "symlink"):
            code = "\n".join(ln for ln in MODULE_SRC.splitlines()
                             if not ln.lstrip().startswith("#"))
            assert banned not in code, (
                f"{banned!r} is back in executable code; the identity rule must "
                f"stay pure computation over the registry")

    def test_the_refutation_numbers_are_preserved_as_documentation(self):
        """A measured negative result is a finding. Deleting the code was the
        ruling; deleting the evidence was not."""
        for fact in ("p = 0.71",
                     "74 of 101",
                     "Falsifier Equivalence via Local Mutation",
                     "C0031 vs C0022",
                     "C0070 vs C0053",
                     "absence-of-validation"):
            assert fact in MODULE_SRC, (
                f"the FELM refutation lost {fact!r}. The code was removed because "
                f"it did not work; the measurement that showed it did not work is "
                f"the finding and must survive.")

    def test_the_retired_block_cannot_be_mistaken_for_live_design(self):
        lines = MODULE_SRC.splitlines()
        start = next(i for i, ln in enumerate(lines) if "RETIRED: FELM" in ln)
        retired = lines[start:]
        assert any("REFUTED" in ln for ln in retired)
        assert any("Nothing below runs" in ln for ln in retired)
        for line in retired:
            stripped = line.strip()
            assert not stripped or stripped.startswith("#"), (
                f"executable code after the RETIRED marker: {line!r}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. The computed-outcome tier: the founder's second criterion.
#    One narrow question — same computed value, or different?
# ═══════════════════════════════════════════════════════════════════════════

class TestTheComputedOutcomeTier:

    def test_it_reads_a_quantity_with_its_unit(self):
        out = computed_outcomes("The molar mass is stated as 112.15 g/mol.")
        assert (112.15, "g/mol") in out

    def test_a_value_written_to_different_precision_is_the_same_outcome(self):
        """The thing a token-set comparison structurally cannot do. `109.128` and
        `109.13` are one computed result and two different strings."""
        a = computed_outcomes("total = 109.128 g/mol")
        b = computed_outcomes("the correct molar mass is 109.13 g/mol")
        assert outcome_agreement(a, b) == "SAME"
        assert not (stem_signature("total = 109.128 g/mol")
                    & stem_signature("the correct molar mass is 109.13 g/mol")), (
            "the tokens genuinely do not overlap — that is the point of the tier")

    def test_two_different_computed_values_are_different(self):
        a = computed_outcomes("combined by arithmetic addition to give 0.85%")
        b = computed_outcomes("root-sum-square, which gives 0.53%")
        assert outcome_agreement(a, b) == "DIFFERENT"

    def test_word_numerals_count_as_outcomes(self):
        out = computed_outcomes("dedup returns a single element and drops two "
                                "distinct inputs")
        assert (1.0, "element") in out and (2.0, "input") in out

    def test_labels_are_not_measurements(self):
        """Claim IDs, line and section references, ISO dates and severity
        metadata are identifiers. Counting them as computed values is how a
        finding comes to 'agree' with an unrelated one on the number 13."""
        for text in ("In CH-13 the claim is wrong.",
                     "the module's own 2026-07-27 comment at line 514-517",
                     "FINDING_ID: F001 SEVERITY: 0.70 FLAW_CLASS: 2",
                     "violates §18 Structure B",
                     "see Section 4 and Table 2"):
            assert computed_outcomes(text) == frozenset(), (
                f"a label was read as a computed outcome: {text!r} -> "
                f"{sorted(computed_outcomes(text))}")

    def test_a_formula_in_backticks_is_kept_but_an_identifier_is_not(self):
        """In exam prose the answer lives inside the backticks. In code review
        the backticks hold identifiers, which `stem_signature` already covers."""
        assert (5.42, "") in computed_outcomes("reported as `f_y / sigma_Ed = 275 / 50.78 = 5.42`")
        assert computed_outcomes("`ImmuneMemory.load` fails") == frozenset()

    def test_small_bare_integers_are_not_outcomes(self):
        """0 through 9 with nothing attached are structural noise; two findings
        agreeing on 'there is 1 of something' is not evidence of anything. A
        value large enough to identify a computation on its own is kept."""
        assert computed_outcomes("returns 1 and then 2") == frozenset()
        assert any(v == 2016.0 for v, _ in computed_outcomes("it reached 2016"))

    def test_an_anchor_mismatch_blocks_a_coincidental_small_integer(self):
        assert not quantities_agree((2.0, "input"), (2.0, "round"))
        assert quantities_agree((64.0, "input"), (64.0, "comparison")), (
            "a distinctive value is the same computation described from two "
            "sides; only small integers need the unit to agree")

    def test_no_extractable_value_is_unknown_and_unknown_is_not_same(self):
        """The vocabulary is the safety property. UNKNOWN is an abstention."""
        assert outcome_agreement(frozenset(), computed_outcomes("112.15 g/mol")) == "UNKNOWN"
        assert outcome_agreement(frozenset(), frozenset()) == "UNKNOWN"
        assert outcome_agreement(frozenset(), frozenset()) != "SAME"

    def test_extraction_is_deterministic(self):
        assert computed_outcomes(D1_A) == computed_outcomes(D1_A)
        assert isinstance(computed_outcomes(D1_A), frozenset)


# ═══════════════════════════════════════════════════════════════════════════
# 3. The safety property: no distinctness witness, no count. Ever.
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSafetyPropertyHolds:

    def test_a_finding_with_no_hard_tokens_is_never_split(self):
        """2.5% of criticals carry no number, claim ID or identifier at all.
        There is nothing to disagree about, so they can be merged but never
        counted as a second defect."""
        rows = [(0, 0.9, "`dedup` mishandles 2016 comparisons."),
                (1, 0.9, "The dedup routine is also wrong in another way entirely.")]
        assert stem_signature(rows[1][2]) == frozenset(), "fixture must be tokenless"
        out = combined_novelty_series(_entries(rows), 1, SYMS)
        assert out["series"] == [1, 0]
        assert out["audit"]["no_distinctness_witness"] == 1

    def test_a_prior_with_no_hard_tokens_also_withholds_the_count(self):
        """The witness has to be against EVERY prior at that location. One prior
        we cannot be told apart from is enough to withhold."""
        rows = [(0, 0.9, "The dedup routine is broken."),
                (1, 0.9, "`dedup` needs 2016 comparisons at 64 inputs.")]
        out = combined_novelty_series(_entries(rows), 1, frozenset({"dedup"}))
        assert out["audit"]["no_distinctness_witness"] == 1
        assert out["series"] == [1, 0]

    def test_the_outcome_tier_can_merge_but_never_grant_novelty(self):
        """Its measured false-DIFFERENT rate on the archive is 0 of 28 labelled
        same-defect pairs — this docstring said 7%, which matches no measurement
        in the module and was corrected 2026-08-12. The rate is not zero in
        general, and this very pair is a counter-example: D2_A and D2_B are one
        defect and the tier answers DIFFERENT. Bounding its authority to merging
        is what makes that free: a DIFFERENT answer is recorded as corroboration
        and changes no count."""
        assert _pair_verdict(D2_A, D2_B) == "MERGED", (
            "signature 0.750 merges these; the outcome tier answers DIFFERENT "
            "and must not be able to overturn a merge into a split")
        assert outcome_agreement(computed_outcomes(D2_A),
                                 computed_outcomes(D2_B)) == "DIFFERENT"

    def test_a_same_outcome_overrides_a_signature_split(self):
        """The tier earning its place: the signatures disagree because one
        finding is verbose, but both land on the same computed value."""
        rows = [(0, 0.9, "`dedup` reports the total as 109.128 g/mol."),
                (1, 0.9, "`dedup` should give 109.13 g/mol under the 2016 method, "
                         "a discrepancy of 43 in the 7th place.")]
        assert signature_similarity(stem_signature(rows[0][2]),
                                    stem_signature(rows[1][2])) < WITHIN_LOCATION_THRESHOLD
        out = combined_novelty_series(_entries(rows), 1, frozenset({"dedup"}))
        assert out["series"] == [1, 0]
        assert out["audit"]["same_computed_outcome"] == 1

    def test_a_decision_is_never_new_without_a_named_reason(self):
        d = identity_decision("`dedup` is quadratic.", SYMS, [])
        assert isinstance(d, IdentityDecision)
        assert d.is_new and d.reason == "new_location"
        assert d.corroborated is False


# ═══════════════════════════════════════════════════════════════════════════
# 4. ACCEPTANCE (a) — the hand-built same-location different-defect cases.
#    PASSES.
# ═══════════════════════════════════════════════════════════════════════════

class TestAcceptanceA_HandBuiltCases:

    @pytest.mark.parametrize("a,b", [(D1_A, D2_A), (D1_A, D2_B),
                                     (D1_B, D2_A), (D1_B, D2_B)])
    def test_the_cross_pairs_return_distinct(self, a, b):
        assert _pair_verdict(a, b) == "DISTINCT"

    @pytest.mark.parametrize("a,b", [(D1_A, D2_A), (D1_A, D2_B),
                                     (D1_B, D2_A), (D1_B, D2_B)])
    def test_the_outcome_tier_independently_corroborates_all_four(self, a, b):
        """Two witnesses, not one. The signatures disagree AND the two findings
        assert different computed values."""
        assert outcome_agreement(computed_outcomes(a),
                                 computed_outcomes(b)) == "DIFFERENT"

    @pytest.mark.parametrize("a,b", [(D1_A, D1_B), (D1_A, D1_C),
                                     (D1_B, D1_C), (D2_A, D2_B)])
    def test_every_same_defect_control_merges(self, a, b):
        assert _pair_verdict(a, b) == "MERGED"

    def test_the_terse_re_raise_is_the_known_pair_level_edge(self):
        """Honest limit, pinned rather than hidden. D1_C is short enough that its
        signature scores 0.200 and 0.250 against the D2 wordings — at and above
        the cut — so as an ISOLATED PAIR it merges with the wrong defect. In the
        series it never gets the chance: it merges into D1 at 0.400 first. If
        this ever changes, the rule got better and the docstring must follow."""
        assert signature_similarity(stem_signature(D1_C), stem_signature(D2_A)) == 0.200
        assert signature_similarity(stem_signature(D1_C), stem_signature(D1_A)) == 0.400
        assert _pair_verdict(D1_A, D1_C) == "MERGED"

    def test_five_wordings_of_two_defects_give_two(self):
        """The series-level answer, which is the only one the gate ever asks."""
        rows = [(0, 0.85, D1_A), (0, 0.82, D1_B), (0, 0.88, D2_A),
                (1, 0.80, D1_C), (1, 0.81, D2_B)]
        out = combined_novelty_series(_entries(rows), 3, SYMS)
        assert out["series"] == [2, 0, 0, 0]
        assert out["audit"]["signature_split"] == 1
        assert out["audit"]["splits_corroborated_by_outcome"] == 1
        assert [s["canonical_id"] for s in out["splits"]] == ["C0003"]

    def test_location_keying_alone_still_merges_them(self):
        """The comparison that justifies the rule existing. If this stops
        failing, the blind spot has gone away."""
        rows = [(0, 0.85, D1_A), (0, 0.88, D2_A)]
        assert location_only_series(_entries(rows), 0, SYMS) == [1]

    def test_the_archive_pairs_the_panel_named_are_both_separated(self):
        """Exp 45 C0031 vs C0022 and Exp 47 C0070 vs C0053 — the two acceptance
        cases FELM failed, one by answering SAME at every mutation budget from 5
        to 60 and one by having no falsifier to execute at all.

        Asked as ISOLATED PAIRS both are separated, and by tier 1 rather than by
        anything clever: each candidate names a function its partner does not.
        That is worth stating precisely, because it is NOT how either was decided
        inside its own run — there the location was already known from other
        findings and the signature had to carry it.
        """
        for run, prior, cand, only in (("exp45", "C0022", "C0031", "__init__"),
                                       ("exp47", "C0053", "C0070",
                                        "parse_alternative_block")):
            ent, _maxr, _arch, _conv = _archive_case(run)
            syms = _symbols_for(run)
            a, b = ent[prior]["description"], ent[cand]["description"]
            assert only in finding_locations(b, syms)
            assert only not in finding_locations(a, syms)
            assert _pair_verdict(a, b, syms) == "NEW_LOCATION"

    def test_in_its_own_run_the_signature_is_what_separates_them(self):
        """The same two findings, decided the way the run decided them. Both are
        counted, and both by the promoted tier — `signature_split` — because
        every location they name had already been flagged."""
        for run, cid in (("exp45", "C0031"), ("exp47", "C0070")):
            ent, maxr, _arch, _conv = _archive_case(run)
            out = combined_novelty_series(ent, maxr, _symbols_for(run))
            assert cid in [s["canonical_id"] for s in out["splits"]], (
                f"{run}/{cid} is no longer counted as a within-location split")

    def test_the_outcome_tier_abstains_on_the_exp45_pair(self):
        """Neither finding asserts a quantity, so the narrow question has no
        answer here. Abstention withholds a MERGE; it does not withhold the
        split. That is the whole point of bounding the tier's authority."""
        ent, _maxr, _arch, _conv = _archive_case("exp45")
        a, b = ent["C0022"]["description"], ent["C0031"]["description"]
        assert outcome_agreement(computed_outcomes(a), computed_outcomes(b)) == "UNKNOWN"

    def test_the_exp47_pair_needs_no_falsifier_to_be_answered(self):
        """FELM could not answer this pair at all: C0053 is UNTOOLABLE and
        carries no falsifier, so there was nothing to execute. A rule that reads
        the finding rather than running it has no such hole — and the signature
        alone would MERGE these two, at 0.286, so it is tier 1 doing the work."""
        ent, _maxr, _arch, _conv = _archive_case("exp47")
        a, b = ent["C0053"]["description"], ent["C0070"]["description"]
        assert not (ent["C0053"].get("falsifier_code") or "").strip()
        assert ent["C0053"].get("falsifier_verdict") == "UNTOOLABLE"
        assert signature_similarity(stem_signature(a), stem_signature(b)) > 0.20


# ═══════════════════════════════════════════════════════════════════════════
# 5. ACCEPTANCE (b) — replay against the six completed runs. FAILS.
#    Pinned as a failure. A refuted result that stops being measured is exactly
#    how this project has lost evidence before.
# ═══════════════════════════════════════════════════════════════════════════

# Measured 2026-08-12. Tail = the three rounds ending at the recorded
# convergence round; zeros mean the count side of the gate would still close.
EXPECTED_TAILS = {
    "exp44": ([0, 0, 0], [0, 0, 0]),      # (location-only, promoted rule)
    "exp45": ([0, 0, 0], [1, 0, 1]),
    "exp46": ([0, 0, 0], [0, 1, 0]),
    # exp47 moved [0, 0, 1] -> [1, 0, 1] on 2026-08-16, when `quantities_agree`
    # stopped letting a MISSING anchor act as a wildcard. C0063's sole outcome is
    # an anchorless `(0.6, '')`, which had been matching the penalty-tier 0.6 in
    # three neighbouring exp47 findings and merging it away. All three of those
    # pairs are labelled DIFFERENT defects, so counting C0063 at round 11 is the
    # correct answer and the previous 0 was a lost finding. Verified not to move
    # any convergence conclusion: the run's tail already ended in a non-zero
    # before the change, so the K=3 zero-run was False both before and after, and
    # the other five runs' series are byte-identical. Evidence:
    # `scripts/similarity_operating_characteristic.py`.
    "exp47": ([0, 0, 0], [1, 0, 1]),
    "exp48": ([0, 1, 0], [0, 1, 0]),      # already non-zero under location keying
    "exp49": ([0, 0, 0], [1, 0, 0]),
}


@pytest.mark.parametrize("run", sorted(ARCHIVE))
def test_every_archived_location_series_is_reproduced(run):
    """The precondition for every number below, and what makes Exp 48 and Exp 49
    measurable at all. If the replay does not reproduce the run's own recorded
    series digit for digit, nothing computed from that replay means anything."""
    ent, maxr, archived, _conv = _archive_case(run)
    assert location_only_series(ent, maxr, _symbols_for(run)) == archived


@pytest.mark.parametrize("run", sorted(ARCHIVE))
def test_acceptance_b_tails(run):
    ent, maxr, _arch, conv = _archive_case(run)
    syms = _symbols_for(run)
    loc = _tail(location_only_series(ent, maxr, syms), conv)
    got = _tail(combined_novelty_series(ent, maxr, syms)["series"], conv)
    want_loc, want_got = EXPECTED_TAILS[run]
    assert loc == want_loc
    assert got == want_got, (
        f"{run}: the promoted rule's closing tail moved from {want_got} to "
        f"{got}. Re-run the archive replay and update the module's acceptance "
        f"table before trusting either number.")


def test_acceptance_b_fails_on_four_of_the_six_runs():
    """The headline result, stated as a failure because it is one.

    Exp 48's own location tail is already non-zero at its recorded convergence
    round, so nothing can be destroyed there — it closed on the state gate, which
    does not require a zero count. Of the remaining five, four break.
    """
    destroyed = []
    for run in sorted(ARCHIVE):
        ent, maxr, _arch, conv = _archive_case(run)
        syms = _symbols_for(run)
        if sum(_tail(location_only_series(ent, maxr, syms), conv)) != 0:
            continue          # location keying did not close it either
        if sum(_tail(combined_novelty_series(ent, maxr, syms)["series"], conv)) != 0:
            destroyed.append(run)
    assert destroyed == ["exp45", "exp46", "exp47", "exp49"], (
        f"acceptance (b) result moved: {destroyed}. It FAILED on exactly these "
        f"four on 2026-08-12; if it now passes, say so loudly and re-derive the "
        f"module's acceptance table rather than editing this list.")


def test_the_findings_that_break_each_tail_are_named():
    """Counting the breaks is not enough — three of the five are genuine second
    defects that location keying could not see, and two are re-finds the
    signature cut missed. A number cannot be adjudicated; a canonical ID can."""
    breaks = {}
    for run in sorted(ARCHIVE):
        ent, maxr, _arch, conv = _archive_case(run)
        out = combined_novelty_series(ent, maxr, _symbols_for(run))
        ids = [s["canonical_id"] for s in out["splits"]
               if conv - 2 <= s["round"] <= conv]
        if ids:
            breaks[run] = ids
    assert breaks == {"exp45": ["C0014", "C0031"],   # both TRUE second defects
                      "exp46": ["C0026"],            # FALSE: re-find of C0005/C0006
                      # C0063 appeared here on 2026-08-16 when `quantities_agree`
                      # stopped treating a missing anchor as a wildcard. It had
                      # been merged into three neighbours by an anchorless 0.60.
                      # Its TRUE/FALSE status is NOT ADJUDICATED — the only
                      # evidence is the sentence-embedding backend calling all
                      # three pairs different (0.479, 0.526, 0.570), which is a
                      # machine grading a machine and is exactly what
                      # `scripts/similarity_operating_characteristic.py
                      # --adjudication-pack` exists to replace. Listed here as a
                      # fact about what the rule does, not as a ruling on whether
                      # it is right.
                      "exp47": ["C0063", "C0070"],   # C0070 TRUE; C0063 PENDING
                      "exp49": ["C0037"]}, breaks    # FALSE: re-find of C0035


def test_which_breaks_carry_a_second_witness():
    """The 'strengthen our findings one way or another' payoff, and it is thin:
    n = 5. The one split the outcome tier corroborated is a genuine second defect
    (exp45/C0014); two of the four uncorroborated ones are. Corroboration has
    never yet accompanied a false split, which is a direction, not a result."""
    corroborated = {}
    for run in sorted(ARCHIVE):
        ent, maxr, _arch, conv = _archive_case(run)
        out = combined_novelty_series(ent, maxr, _symbols_for(run))
        for s in out["splits"]:
            if conv - 2 <= s["round"] <= conv:
                corroborated[f"{run}/{s['canonical_id']}"] = s["outcome_corroborated"]
    assert corroborated == {"exp45/C0014": True,    # TRUE second defect
                            "exp45/C0031": False,   # TRUE second defect
                            "exp46/C0026": False,   # FALSE split
                            "exp47/C0063": True,    # PENDING adjudication
                            "exp47/C0070": False,   # TRUE second defect
                            "exp49/C0037": False}   # FALSE split
    true_defects = {"exp45/C0014", "exp45/C0031", "exp47/C0070"}
    # Splits whose TRUE/FALSE status no human has ruled on. Kept as a NAMED set
    # rather than folded into `true_defects`, because folding it in would record
    # an assistant's guess as an adjudication and the distinction between those
    # two things is the point of this whole exercise. When the adjudication pack
    # comes back, each entry moves into `true_defects` or becomes a known
    # re-find — and if it becomes a re-find, that IS the regression this test is
    # written to catch, so it must move deliberately rather than by editing here.
    pending = {"exp47/C0063"}
    assert all(cid in true_defects or cid in pending
               for cid, ok in corroborated.items() if ok), (
        "a corroborated split is now a known re-find — the second witness has "
        "started agreeing with the wrong answer, and that is a real regression")


# ═══════════════════════════════════════════════════════════════════════════
# 6. The structural claim a gate would rest on — verified, not asserted.
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("run", sorted(ARCHIVE))
def test_combined_never_undercounts_location_keying_on_the_archive(run):
    """`combined >= location-only`, elementwise. It is the ONLY safety claim the
    gate may rest on: the rule can delay a convergence, never fake one.

    This was FALSE before 2026-08-12 and the measurement is what said so — the
    subset argument only ever covered findings that HAVE a location, and
    combined undercounted at round 0 on this very run pair (Exp 48: 8 vs 9,
    Exp 49: 10 vs 11).
    """
    ent, maxr, _arch, _conv = _archive_case(run)
    syms = _symbols_for(run)
    loc = location_only_series(ent, maxr, syms)
    got = combined_novelty_series(ent, maxr, syms)["series"]
    assert all(c >= n for c, n in zip(got, loc)), (
        f"{run}: combined {got} undercounts location-only {loc} — the rule "
        f"would close a gate location keying holds open")


@pytest.mark.parametrize("run", sorted(ARCHIVE))
def test_combined_never_undercounts_the_live_gating_series(run):
    """The same elementwise claim against the rule that ACTUALLY GATES.

    `location_only_series` is the retired single-`<generic>`-bucket keying the
    six archived runs were scored with. The series that feeds the count side of
    the two-sided gate today is
    `reference_runner_v2._location_keyed_critical_series`, which keys each
    unlocated critical on its own content and skips terminal non-novel statuses.
    They are different rules, and a safety claim verified against the retired one
    says nothing about the gate.

    FOUND 2026-08-12 BY ADVERSARIAL VERIFICATION: it was not just unverified, it
    was FALSE. Exp 44 round 2, combined 2 against the live series' 3 — C0022, an
    unlocated critical with four hard tokens, withheld because the one unlocated
    prior (C0007) carries none. Undercounting the gating series is the one
    direction that can close a gate location keying holds open.

    The runner's own function is driven here rather than re-implemented, so this
    test tracks the live rule if it changes instead of quietly testing a copy.
    """
    from bench.reference_runner_v2 import _location_keyed_critical_series

    class _Reg:
        def __init__(self, entries):
            self.entries = entries

    ent, maxr, _arch, _conv = _archive_case(run)
    syms = _symbols_for(run)
    live = _location_keyed_critical_series(_Reg(ent), maxr, syms)
    got = combined_novelty_series(ent, maxr, syms)["series"]
    assert all(c >= n for c, n in zip(got, live)), (
        f"{run}: combined {got} undercounts the LIVE gating series {live} — the "
        f"rule would close a gate the runner's own keying holds open")


def test_the_excluded_status_set_matches_the_runner():
    """This module holds a LOCAL copy of the runner's terminal-status set,
    because it must stay a leaf and the runner imports it. A second copy of a
    constant is a second constant, so drift between them is a defect and this is
    where it goes red."""
    from bench.convergence_location import _NON_NOVEL_TERMINAL_STATUSES as MINE
    from bench.reference_runner_v2 import _NON_NOVEL_TERMINAL_STATUSES as THEIRS
    assert set(MINE) == set(THEIRS), (
        f"the identity rule is scoring a different population from the gate: "
        f"mine {sorted(MINE)} vs the runner's {sorted(THEIRS)}")


@pytest.mark.parametrize("name,rows", [
    ("a REFUTED prior flags a location the live rule never flags",
     [(0, 0.9, "`dedup` mishandles 2016 comparisons on 64 inputs.", "REFUTED"),
      (1, 0.9, "`dedup` mishandles 2016 comparisons on 64 distinct inputs.",
       "CONFIRMED")]),
    ("an UNCONFIRMED prior merges the real finding away",
     [(0, 0.9, "`dedup` is quadratic: 2016 comparisons.", "UNCONFIRMED"),
      (2, 0.9, "`dedup` is quadratic: 2016 comparisons at n=64.", "CONFIRMED")]),
    ("a MERGED unlocated prior swallows a later unlocated critical",
     [(0, 0.9, "Undetectable elsewhere: 2016 comparisons on 64 inputs.",
       "MERGED"),
      (1, 0.9, "A real defect: 2016 comparisons on 64 inputs, unlocated.",
       "CONFIRMED")]),
    ("an entry with no open_since_round is not round 0",
     [(None, 0.9, "`dedup` mishandles 2016 comparisons on 64 inputs.",
       "CONFIRMED"),
      (1, 0.9, "`dedup` mishandles 2016 comparisons on 64 distinct inputs.",
       "CONFIRMED")]),
])
def test_a_finding_the_gate_never_sees_cannot_merge_one_it_does(name, rows):
    """The four constructed undercounts of the LIVE gating series, 2026-08-12.

    ROOT CAUSE, and it is the same one behind both corrections in the module's
    block: this rule was scored against a different POPULATION from the gate. The
    live series skips terminal-and-not-novel statuses and entries with no round;
    this module counted them, which FLAGGED THEIR LOCATIONS, and the genuine
    critical arriving at that location later was then merged away. Every one of
    these four produced combined < live before the fix — the direction that can
    close a gate location keying holds open.

    Each case is deliberately built so the second finding is the real one and the
    first is invisible to the gate.
    """
    from bench.reference_runner_v2 import _location_keyed_critical_series

    class _Reg:
        def __init__(self, entries):
            self.entries = entries

    ent = {f"C{i:04d}": dict(canonical_id=f"C{i:04d}", open_since_round=r,
                             severity=sev, description=d, status=st)
           for i, (r, sev, d, st) in enumerate(rows, 1)}
    maxr = max(r for r, _s, _d, _st in rows if r is not None)
    syms = frozenset({"dedup", "variance"})
    live = _location_keyed_critical_series(_Reg(ent), maxr, syms)
    got = combined_novelty_series(ent, maxr, syms)["series"]
    assert all(c >= n for c, n in zip(got, live)), (
        f"{name}: combined {got} undercounts the live gating series {live}")
    assert location_only_series(ent, maxr, syms) == live, (
        f"{name}: the retired replay {location_only_series(ent, maxr, syms)} no "
        f"longer agrees with the live series {live} on this shape either")


def test_the_safety_property_does_not_reach_the_unlocated_stream():
    """The regression test for that defect, constructed rather than replayed.

    Two unlocated criticals. The first carries no hard token at all, so under the
    old rule every later unlocated critical met a prior with an empty signature
    and was withheld forever — whatever it said. The live keying gives the first
    a text-hash key and the second its own signature bucket, and counts both.

    Within a flagged location the withholding is still correct and still applies:
    location keying was going to merge that finding anyway, so nothing a gate can
    see is lost. The bug was applying it where no location binds the two.
    """
    rows = [(0, 0.9, "Something is broken in a way with no hard tokens."),
            (0, 0.9, "A different thing fails at 2016 comparisons on 64 inputs.")]
    ent = _entries(rows)
    syms = frozenset({"dedup"})
    assert not stem_signature(rows[0][2]), "fixture prior must be tokenless"
    assert not finding_locations(rows[0][2], syms), "fixture must be unlocated"
    assert not finding_locations(rows[1][2], syms), "fixture must be unlocated"
    out = combined_novelty_series(ent, 0, syms)
    assert out["series"] == [2], (
        "an unlocated critical was withheld because an unrelated unlocated prior "
        "had no signature — the live gate counts both")
    assert out["audit"]["no_distinctness_witness"] == 0

    # ...and the located form of the same shape is still withheld, which is the
    # half of the safety property that was never wrong.
    located = [(0, 0.9, "The dedup routine is broken."),
               (0, 0.9, "`dedup` needs 2016 comparisons at 64 inputs.")]
    held = combined_novelty_series(_entries(located), 0, syms)
    assert held["audit"]["no_distinctness_witness"] == 1
    assert held["series"] == [1]


def test_an_unlocated_finding_is_not_merged_into_a_located_one():
    """The regression test for the defect the elementwise check found.

    Location keying gives every unlocated finding the same `<generic>` key, so
    the first one always counts. Comparing an unlocated finding against LOCATED
    priors let a signature match swallow it, and the count went down. Here the
    two signatures overlap at 0.667 — well over the cut — so the old rule merged
    the second and returned [1] where location keying returns [2].
    """
    rows = [(0, 0.9, "`dedup` fails at 2016 comparisons on 64 inputs."),
            (0, 0.9, "Something fails at 2016 comparisons on 64 inputs.")]
    ent = _entries(rows)
    syms = frozenset({"dedup"})
    assert not finding_locations(rows[1][2], syms), "fixture must be unlocated"
    assert signature_similarity(stem_signature(rows[0][2]),
                                stem_signature(rows[1][2])) >= WITHIN_LOCATION_THRESHOLD
    assert location_only_series(ent, 0, syms) == [2]
    assert combined_novelty_series(ent, 0, syms)["series"] == [2]


@pytest.mark.parametrize("run", sorted(ARCHIVE))
def test_the_outcome_tier_only_ever_removes_counts(run):
    """Measured on all six runs, and a measurement is all it is: a merged finding
    is not appended to `seen`, so a later finding can meet fewer priors and
    escape a merge. Per-decision monotonicity does not compose into per-series
    monotonicity, and nothing here claims it does."""
    ent, maxr, _arch, _conv = _archive_case(run)
    syms = _symbols_for(run)
    with_outcome = combined_novelty_series(ent, maxr, syms)["series"]
    without = combined_novelty_series(ent, maxr, syms, use_outcomes=False)["series"]
    assert all(a <= b for a, b in zip(with_outcome, without)), (
        f"{run}: {with_outcome} exceeds the signature-only series {without}")


@pytest.mark.parametrize("run", sorted(ARCHIVE))
def test_the_audit_accounts_for_every_critical(run):
    """A finding that is neither counted nor explained is a finding that
    vanished."""
    ent, maxr, _arch, _conv = _archive_case(run)
    a = combined_novelty_series(ent, maxr, _symbols_for(run))["audit"]
    reasons = ("new_location", "first_at_location", "signature_merge",
               "no_distinctness_witness", "same_computed_outcome",
               "signature_split")
    assert sum(a[r] for r in reasons) == a["criticals"]
    assert (a["splits_corroborated_by_outcome"] + a["splits_uncorroborated"]
            == a["signature_split"])


def test_the_divergence_report_never_shows_the_forbidden_direction():
    """`location_splits_hierarchical_merges` must stay empty on every run: it is
    the elementwise claim restated per finding, and a non-empty list is the gate
    argument breaking."""
    for run in sorted(ARCHIVE):
        ent, _maxr, _arch, _conv = _archive_case(run)
        div = novelty_rule_divergence(ent, _symbols_for(run))
        assert div["n_merged"] == 0, (
            f"{run}: location keying counted {div['n_merged']} finding(s) this "
            f"rule merged — {div['location_splits_hierarchical_merges']}")
        assert set(div) >= {"hierarchical_splits_location_merges", "n_split",
                            "n_merged", "within_threshold"}


# ═══════════════════════════════════════════════════════════════════════════
# 7. Shadow status and the module contract.
# ═══════════════════════════════════════════════════════════════════════════

class TestNothingGatesOnThis:

    def test_hierarchical_gating_still_defaults_off(self):
        from bench.reference_runner_v2 import RunnerConfig
        assert RunnerConfig().hierarchical_novelty_convergence is False

    def test_no_shipped_config_enables_novelty_gating(self):
        on = [str(f) for f in (REPO / "bench").glob("exp*_configs/*.json")
              if json.loads(f.read_text(encoding="utf-8")).get(
                  "hierarchical_novelty_convergence")]
        assert not on, (
            f"promoted to the gate without a founder ruling on acceptance (b), "
            f"which FAILS on four of six archived runs: {on}")

    def test_gamma_does_not_read_this_rule(self):
        """GAMMA IS LOAD-BEARING and this change must not be able to move it.

        `gamma_critical` is `_estimate_gamma(_settled_crit, ...)`, and
        `_settled_crit` comes from `_settled_novelty_series`, which reads only
        `open_since_round`, `status` and `severity` off the registry. The
        identity rule feeds `novel_critical_history` — the COUNT side of the
        two-sided gate — and nothing else. Checked at the source rather than
        assumed, because "it only feeds the other series" is exactly the kind of
        claim that stops being true without anyone noticing.
        """
        import inspect

        from bench.reference_runner_v2 import _estimate_gamma, _settled_novelty_series
        for fn in (_settled_novelty_series, _estimate_gamma):
            src = inspect.getsource(fn)
            for banned in ("finding_locations", "stem_signature", "identity_decision",
                           "combined_novelty_series", "hierarchical_novelty_series",
                           "computed_outcomes", "convergence_location"):
                assert banned not in src, (
                    f"{fn.__name__} now reads {banned} — the decay curve has been "
                    f"wired to the novelty rule, which it must never be")

    def test_the_bare_series_helper_agrees_with_the_audited_one(self):
        rows = [(0, 0.9, D1_A), (0, 0.9, D2_A), (1, 0.9, D1_C)]
        ent = _entries(rows)
        assert (hierarchical_novelty_series(ent, 1, SYMS)
                == combined_novelty_series(ent, 1, SYMS)["series"])

    def test_sub_critical_findings_are_ignored(self):
        rows = [(0, 0.9, "`dedup` is quadratic."),
                (1, 0.5, "`variance` has a typo.")]
        out = combined_novelty_series(_entries(rows), 1,
                                      frozenset({"dedup", "variance"}))
        assert out["series"] == [1, 0]

    def test_the_series_has_one_slot_per_round_and_drops_later_rounds(self):
        rows = [(0, 0.9, "`dedup` is quadratic."), (9, 0.9, "`variance` is wrong.")]
        out = combined_novelty_series(_entries(rows), 5,
                                      frozenset({"dedup", "variance"}))
        assert len(out["series"]) == 6 and sum(out["series"]) == 1

    def test_a_new_location_is_always_new_and_costs_nothing(self):
        rows = [(0, 0.9, "`dedup` is quadratic."),
                (1, 0.9, "`variance` misstates the confidence interval.")]
        out = combined_novelty_series(_entries(rows), 1,
                                      frozenset({"dedup", "variance"}))
        assert out["series"] == [1, 1]
        assert out["audit"]["new_location"] == 2
        assert out["audit"]["signature_split"] == 0

    def test_the_identity_rule_touches_no_network(self, request):
        """It is pure computation over the registry. The cost constraint on this
        project is absolute, so it is measured here rather than asserted."""
        from bench.tests.conftest import netguard_attempts
        before = len(netguard_attempts(request.node.nodeid))
        ent, maxr, _arch, _conv = _archive_case("exp45")
        out = combined_novelty_series(ent, maxr, _symbols_for("exp45"))
        assert out["audit"]["criticals"] > 0, "the run under test must have happened"
        assert len(netguard_attempts(request.node.nodeid)) == before


def test_the_module_stays_a_leaf_dependency():
    """`convergence_location` is imported by the runner; a top-level `bench.`
    import here would make the dependency graph circular the moment the sandbox
    grows a runner import. With FELM gone this module has no `bench` dependency
    at all, lazy or otherwise."""
    for line in MODULE_SRC.splitlines():
        if line.startswith(("import ", "from ")) and "__future__" not in line:
            assert "bench." not in line, f"top-level bench import: {line!r}"
    assert "import bench" not in MODULE_SRC
