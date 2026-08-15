"""Tests for the Ouroboros query builder rebuilt on 2026-07-31.

The cell retrieves academic papers so the panel can consult real literature.
It was returning the wrong literature, and the query builder was why. Three
faults, all observed on live runs, all fixed in ``_target_to_query``:

  A. The 10-word cap severed multi-word technical terms. On the loop-close proof
     run "…which suffers catastrophic cancellation in floating point…" was cut
     after "catastrophic", arXiv matched that one word, and the cell came back
     with "Overcoming Catastrophic Forgetting by XAI" — continual learning in
     neural networks — for a finding about floating-point cancellation in a
     variance routine.
  B. The harness's own label vocabulary was searched: every query opened with
     "uncertain finding", and report-shaped descriptions contributed literal
     "FINDING_ID: SEVERITY: FLAW_CLASS: ABSTRACTION_INDEX: FIND".
  C. Code identifiers were harvested into the query on purpose. No academic
     index contains ``streaming_variance`` or ``EvidenceStore.verify_bundle``.

Every finding text below is real, quoted from a completed run's report under
``bench/logs/`` (provenance on each constant) or from the loop-close proof
harness. Nothing here touches the network: the assertions are about the query
string, and the live-API measurements that justified the output form are
recorded in the module comments of ``bench/ouroboros_cell.py``.
"""

from __future__ import annotations

import glob
import json
import os
import re

import pytest

import bench.ouroboros_cell as oc
from bench.ouroboros_cell import OuroborosCell


# ── Real finding text ───────────────────────────────────────────────────────
# `_select_targets` builds targets as "uncertain_finding:" + description[:200],
# so each constant is quoted at that same width.

# bench/tools/prove_ouroboros_loop_close.py — the canned panel finding whose
# retrieval produced the catastrophic-forgetting paper.
FIND_CANCELLATION = (
    "streaming_variance uses the naive sum-of-squares formula, which suffers "
    "catastrophic cancellation in floating point numerical stability when the "
    "mean is large relative to the standard deviation. Welford online "
    "algorithm avoids it."
)

# bench/logs/exp44_evidence_locationkey_live_.../…_report.json, round 3.
FIND_REPORT_LABELS = (
    "FINDING_ID: F302  \nSEVERITY: 0.85  \nFLAW_CLASS: 5  (correctness — "
    "contract violation)  \nABSTRACTION_INDEX: 0.40  \n\nFIND  \n"
    "`EvidenceBundle.save_json` (line ~115) unconditionally calls "
    "`json.dump(self.t"
)

# bench/logs/exp44_evidence_locationkey_live_.../…_report.json, round 7 — the
# FALSIFIER block is raw Python and used to outscore the defect itself.
FIND_FALSIFIER_CODE = (
    "FINDING_ID: F701\nSEVERITY: 0.70\nFIND: EvidenceRecord.from_chain_record "
    "crashes with KeyError on missing required keys.\nFALSIFIER:\n"
    "from bench.evidence import EvidenceRecord\n\nrecord = {\n    "
    '"sealed_body'
)

# bench/logs/exp49_engineering_exam_live_.../…_report.json, round 0 — carries an
# absolute filesystem path, which used to contribute the search term "users".
FIND_EULER = (
    "EN-06 overstates the Euler critical load for C4-02. Location: "
    "`/Users/georgejackson/CDSFL_review_targets/exp49_engineering.md`, "
    "section 2, EN-06. Evidence: using the document’s own inputs, "
    "\\(P_{cr}=\\p"
)

# bench/logs/exp48_chemistry_exam_live_.../…_report.json, round 0.
FIND_CHEMISTRY = (
    "In CH-11, the balanced equation for the dichromate oxidation of ethanol "
    "produces 8 H2O, which leaves hydrogen and oxygen unbalanced (34 H on the "
    "left vs 28 H on the right). The correct number of water"
)

# bench/logs/exp45_memory_statistics_live_.../…_report.json, round 0.
FIND_IDENTIFIERS = (
    "The `ImmuneMemory.load` method fails to initialize `source_hash` when "
    "returning a fresh instance (either because the file doesn't exist or due "
    "to a load error), and also fails to adopt `expected_hash`"
)

# bench/logs/exp47_divergence_locationkey_live_.../…_report.json, round 11 —
# truncation lands inside a backtick span: "…flags it as `recidivis".
FIND_TRUNCATED = (
    "The cross-round recidivism check in `check_sibling_admissibility` "
    "compares the current alternative against ALL prior-round alternatives. "
    "If a match is found (≥ 0.98 Jaccard), it flags it as `recidivis"
)


def _target(desc: str) -> str:
    """Reproduce what ``_select_targets`` hands the builder."""
    return "uncertain_finding:" + desc[:200]


@pytest.fixture()
def cell() -> OuroborosCell:
    return OuroborosCell(shadow=True)


def _terms(query: str) -> list:
    return [t.strip('"') for t in query.split(" AND ")]


# ═══════════════════════════════════════════════════════════════════════════
# Requirement 1 — multi-word technical terms are never severed
# ═══════════════════════════════════════════════════════════════════════════


class TestMultiWordTermsSurvive:
    """Fault A. The cap counts TERMS, so it cannot fall inside a phrase."""

    def test_catastrophic_cancellation_stays_whole(self, cell):
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        assert "catastrophic cancellation" in q.lower(), q

    def test_catastrophic_never_appears_without_cancellation(self, cell):
        """The exact regression: a lone "catastrophic" is what matched the
        continual-learning literature."""
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        for term in _terms(q):
            if "catastrophic" in term.lower():
                assert "cancellation" in term.lower(), (
                    f"severed technical term {term!r} in {q!r}"
                )

    def test_hyphenated_compound_not_split(self, cell):
        """``sum-of-squares`` is one token and must stay one token."""
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        assert "sum-of-squares" in q, q
        assert not re.search(r"\bsum\b(?!-)", q), q

    def test_leave_one_round_out_survives(self, cell):
        q = cell._target_to_query(
            "uncertain_finding:The leave-one-round-out estimator understates "
            "cross-round novelty for the convergence criterion."
        )
        assert "leave-one-round-out" in q, q

    def test_lexicon_phrase_beats_its_own_fragments(self, cell):
        """"critical load" is the term; "critical" and "load" alone are not."""
        q = cell._target_to_query(_target(FIND_EULER))
        assert "critical load" in q.lower(), q

    def test_no_term_is_a_truncation_fragment(self, cell):
        """200-character truncation lands mid-word; a fragment is a guaranteed
        zero-recall term. "…flags it as `recidivis" must not become a term."""
        q = cell._target_to_query(_target(FIND_TRUNCATED))
        assert "recidivis " not in q + " "
        assert not any(t.endswith("recidivis") for t in _terms(q)), q

    def test_short_complete_description_keeps_its_last_word(self, cell):
        """The fragment guard must not fire on text that merely lacks a full
        stop — it once ate the "bias" from "…possible systemic bias"."""
        q = cell._target_to_query(
            "uncertain_finding:92% of verdicts are REJECTED (11/12) — "
            "possible systemic bias"
        )
        assert "bias" in q.lower(), q


# ═══════════════════════════════════════════════════════════════════════════
# Requirement 2 — label vocabulary is stripped, not searched
# ═══════════════════════════════════════════════════════════════════════════


class TestLabelsStripped:
    """Fault B."""

    def test_harness_prefix_absent(self, cell):
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        # Word boundaries matter: "uncertainties" is legitimate domain
        # vocabulary and must not be mistaken for the harness's label.
        assert not re.search(r"\buncertain\b", q, re.I), q
        assert not re.search(r"\bfindings?\b", q, re.I), q

    def test_anomaly_prefix_is_not_searched(self, cell):
        """RE-POINTED 2026-08-04. Originally asserted the query became the
        literal fallback `"pipeline anomaly detection"`. That fallback is gone:
        it was a phrase unrelated to the finding, sent to an academic index,
        which wasted a retrieval and could return a paper about something else
        entirely. Input carrying nothing searchable now yields NOTHING, and the
        caller skips it. The property — the harness's own label vocabulary is
        never searched — is unchanged and is what is asserted here."""
        q = cell._target_to_query("uncertain_finding:`x` `y`")
        assert "uncertain" not in q.lower()
        assert "anomaly detection" not in q.lower(), (
            "the old fallback phrase must not reappear")


    def test_anomaly_target_with_content_drops_only_the_label(self, cell):
        q = cell._target_to_query(
            "round_4_anomalies:verdict distribution collapsed to a single "
            "systemic bias across the panel"
        )
        assert not re.search(r"\bround\b", q, re.I), q
        assert not re.search(r"\banomal\w*\b", q, re.I), q
        assert not re.search(r"\bverdict\w*\b", q, re.I), q
        # Whatever it selects must come from the description, not the label.
        assert all(w.lower() in
                   "verdict distribution collapsed to a single systemic bias "
                   "across the panel"
                   for t in _terms(q) for w in t.split()), q

    def test_report_field_labels_absent(self, cell):
        q = cell._target_to_query(_target(FIND_REPORT_LABELS))
        for label in ("FINDING_ID", "SEVERITY", "FLAW_CLASS",
                      "ABSTRACTION_INDEX", "FIND"):
            assert label not in q.upper(), q

    def test_severity_number_absent(self, cell):
        q = cell._target_to_query(_target(FIND_REPORT_LABELS))
        assert "0.85" not in q and "0.40" not in q, q
        assert not re.search(r"\bF302\b", q), q

    def test_machinery_segment_dropped(self, cell):
        """Everything after FALSIFIER is harness machinery — usually raw
        Python. It must not supply search terms."""
        q = cell._target_to_query(_target(FIND_FALSIFIER_CODE))
        for token in ("import", "record =", "sealed_body", "FALSIFIER"):
            assert token.lower() not in q.lower(), q

    def test_inline_field_label_absent(self, cell):
        q = cell._target_to_query(_target(FIND_EULER))
        assert "location" not in q.lower(), q


# ═══════════════════════════════════════════════════════════════════════════
# Requirement 3 — code identifiers never reach an academic index
# ═══════════════════════════════════════════════════════════════════════════


class TestCodeIdentifiersRemoved:
    """Fault C. Removed from the prose; at most translated to plain words."""

    def test_snake_case_identifier_absent(self, cell):
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        assert "streaming_variance" not in q, q
        assert "_" not in q, q

    def test_dotted_and_pascal_identifiers_absent(self, cell):
        q = cell._target_to_query(_target(FIND_IDENTIFIERS))
        for ident in ("ImmuneMemory.load", "ImmuneMemory", "source_hash",
                      "expected_hash"):
            assert ident not in q, q

    def test_module_path_absent(self, cell):
        q = cell._target_to_query(_target(FIND_FALSIFIER_CODE))
        assert "bench.evidence" not in q, q
        assert ".py" not in q, q

    def test_absolute_path_contributes_nothing(self, cell):
        """The path /Users/georgejackson/… once supplied the term "users" to a
        query about Euler buckling."""
        q = cell._target_to_query(_target(FIND_EULER))
        for token in ("users", "georgejackson", "CDSFL_review_targets",
                      "exp49_engineering"):
            assert token.lower() not in q.lower(), q

    def test_identifier_translation_is_natural_language(self, cell):
        """Translation is allowed and useful — "immune memory" is searchable
        where `ImmuneMemory` is not — but only as plain words."""
        q = cell._target_to_query(
            "uncertain_finding:The `blended_prior` term dominates the "
            "posterior distribution."
        )
        assert "blended_prior" not in q, q
        assert re.fullmatch(r'[A-Za-z0-9 "\-‐‑\']+', q), q


# ═══════════════════════════════════════════════════════════════════════════
# Requirement 4 — the emitted string is something the APIs handle sensibly
# ═══════════════════════════════════════════════════════════════════════════


class TestQueryShapeIsApiSafe:
    """arXiv rejected operator soup with HTTP 500 in the past, and Semantic
    Scholar and OpenAlex receive the same string, so the shape stays plain:
    quoted phrases and bare words joined by AND."""

    ALL_FINDINGS = [FIND_CANCELLATION, FIND_REPORT_LABELS, FIND_FALSIFIER_CODE,
                    FIND_EULER, FIND_CHEMISTRY, FIND_IDENTIFIERS,
                    FIND_TRUNCATED]

    @pytest.mark.parametrize("desc", ALL_FINDINGS)
    def test_no_operator_or_bracket_syntax(self, cell, desc):
        q = cell._target_to_query(_target(desc))
        assert not re.search(r"[(){}\[\]`$\\<>*|&^%~@#/]", q), q

    @pytest.mark.parametrize("desc", ALL_FINDINGS)
    def test_no_stray_digits(self, cell, desc):
        q = cell._target_to_query(_target(desc))
        assert not re.search(r"\d", q), q

    @pytest.mark.parametrize("desc", ALL_FINDINGS)
    def test_balanced_quotes_and_clean_conjunction(self, cell, desc):
        q = cell._target_to_query(_target(desc))
        assert q.count('"') % 2 == 0, q
        assert " AND  AND " not in q and not q.startswith("AND"), q
        assert not q.endswith("AND"), q

    @pytest.mark.parametrize("desc", ALL_FINDINGS)
    def test_bounded_length_and_term_count(self, cell, desc):
        q = cell._target_to_query(_target(desc))
        assert len(q) <= oc._QUERY_MAX_CHARS, q
        assert 1 <= len(_terms(q)) <= 3, q

    @pytest.mark.parametrize("desc", ALL_FINDINGS)
    def test_specificity_budget_respected(self, cell, desc):
        """A conjunction of exact phrases returns nothing — measured against
        the live arXiv API on 2026-07-31. A phrase costs 2, a word costs 1,
        against a budget of 3, so at most one phrase can ever appear."""
        q = cell._target_to_query(_target(desc))
        assert sum(1 for t in _terms(q) if " " in t) <= 1, q
        cost = sum(oc._QUERY_PHRASE_COST if " " in t else 1 for t in _terms(q))
        assert cost <= oc._QUERY_BUDGET, q

    def test_empty_input_returns_EMPTY_so_the_caller_skips_it(self, cell):
        """RE-POINTED 2026-08-04. This asserted that empty input still yields a
        query, which was true of the old `"pipeline anomaly detection"` fallback.
        That fallback was removed: a query which CANNOT be about the finding is
        worse than none — it burns a retrieval and risks handing the panel a
        paper unrelated to the claim, which the relevance reader may over-rate.

        The guarantee has MOVED, not vanished. Nothing unsafe reaches the wire
        because nothing is sent at all; see
        TestAnEmptyQueryIsNeverDispatched below, which is the test that now
        carries the weight this one used to."""
        assert cell._target_to_query("") == ""
        assert cell._target_to_query("uncertain_finding:") == ""

    def test_deterministic(self, cell):
        t = _target(FIND_CANCELLATION)
        assert cell._target_to_query(t) == cell._target_to_query(t)


# ═══════════════════════════════════════════════════════════════════════════
# The end-to-end regression: the finding that produced the wrong paper
# ═══════════════════════════════════════════════════════════════════════════


class TestCatastrophicCancellationRegression:
    """The whole point. OLD query (git HEAD before 2026-07-31):

        'uncertain finding streaming_variance uses naive sum-of-squares
         formula, which suffers catastrophic'
        → arXiv: "Overcoming Catastrophic Forgetting by XAI"

    NEW query:

        '"catastrophic cancellation" AND sum-of-squares'
        → arXiv: "BETULA: Numerically Stable CF-Trees for BIRCH Clustering"
    """

    def test_query_is_about_floating_point_cancellation(self, cell):
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        assert "catastrophic cancellation" in q.lower(), q
        assert "uncertain" not in q.lower(), q
        assert "streaming_variance" not in q, q

    def test_no_bare_catastrophic_token(self, cell):
        """A bare "catastrophic" is the token that matched the forgetting
        literature. It must never be emitted on its own."""
        q = cell._target_to_query(_target(FIND_CANCELLATION))
        assert "catastrophic" not in _terms(q), q


# ═══════════════════════════════════════════════════════════════════════════
# Corpus sweep — invariants over every finding of every completed run
# ═══════════════════════════════════════════════════════════════════════════


def _corpus_descriptions() -> list:
    root = os.path.join(os.path.dirname(__file__), "..", "logs")
    out = []
    for path in sorted(glob.glob(os.path.join(root, "exp4[4-9]_*", "*_report.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        for rnd in data.get("rounds", []):
            for finding in (rnd.get("findings") or []):
                desc = (finding.get("description") or "").strip()
                if desc:
                    out.append(desc)
    return out


class TestAgainstEveryCompletedRun:
    """Read-only sweep of bench/logs. Skips cleanly where the logs are absent
    (a fresh checkout), so this is an invariant check, not a fixture."""

    def test_invariants_hold_for_every_real_finding(self, cell):
        descriptions = _corpus_descriptions()
        if not descriptions:
            pytest.skip("no completed-run reports under bench/logs")
        assert len(descriptions) >= 12, len(descriptions)

        offenders = []
        for desc in descriptions:
            q = cell._target_to_query(_target(desc))
            terms = _terms(q)
            if q == "":
                # Not an offender: an empty query is the deliberate "nothing
                # searchable here" signal and is skipped by the caller rather
                # than sent. API-safety applies to queries that are DISPATCHED.
                continue
            if (not q.strip()
                    or re.search(r"[(){}\[\]`$\\<>*|&^%~@#/_]", q)
                    or re.search(r"\d", q)
                    or q.count('"') % 2
                    or len(q) > oc._QUERY_MAX_CHARS
                    or len(terms) > 3
                    or sum(1 for t in terms if " " in t) > 1
                    or re.search(r"\buncertain\b", q, re.I)
                    or re.search(r"finding_id|flaw_class", q, re.I)):
                offenders.append((desc[:70], q))
        assert not offenders, offenders[:5]

    def test_fallback_is_rare(self, cell):
        """The "nothing searchable here" fallback should be the exception. It
        fires on findings whose text is pure code or pure harness labels."""
        descriptions = _corpus_descriptions()
        if not descriptions:
            pytest.skip("no completed-run reports under bench/logs")
        fallbacks = sum(
            1 for d in descriptions
            if cell._target_to_query(_target(d)) == "pipeline anomaly detection"
        )
        assert fallbacks / len(descriptions) < 0.15, (
            f"{fallbacks}/{len(descriptions)} findings produced no query at all"
        )


class TestAnEmptyQueryIsNeverDispatched:
    """The guarantee that MOVED when the fallback phrase was removed.

    Before 2026-08-04 `_target_to_query` could never return empty, so nothing
    downstream had to handle it. It can now, deliberately — measured on 274 real
    archived findings, 1.5% carry nothing searchable (it was 6.9% before the
    label-stripping repair, because `VERDICT: CONFIRM Cxxxx.` prefixes were
    destroying the entire description).

    Removing a guarantee and replacing it with nothing tested is how a defect
    gets in. So: the caller must SKIP an unqueryable target, and no empty query
    may ever reach the fetcher.
    """

    def test_the_caller_skips_an_unqueryable_target(self):
        from bench.ouroboros_cell import OuroborosCell
        c = OuroborosCell.__new__(OuroborosCell)
        c.MAX_QUERIES_PER_ROUND = 5
        c.allowed_sources = ["arxiv", "semantic_scholar"]
        targets = [
            "VERDICT: CONFIRM C0019. `wait_for_wave` has no timeout parameter, "
            "causing it to block forever if the wave size is never reached.",
            "uncertain_finding:`a` `b` `c`",          # nothing searchable
        ]
        queries = c._build_queries(targets) if hasattr(c, "_build_queries") else None
        if queries is None:                            # method name differs
            import inspect
            fn = next(f for n, f in inspect.getmembers(OuroborosCell, inspect.isfunction)
                      if "quer" in n and "build" in n.lower())
            queries = fn(c, targets)
        assert all(q["query"].strip() for q in queries), (
            "an empty query must never be packaged for dispatch")
        assert len(queries) < len(targets), (
            "the unqueryable target must be skipped, not sent")
        assert getattr(c, "_skipped_unqueryable", 0) >= 1, (
            "the skip must be COUNTED — a silent skip looks identical to a "
            "retrieval that found nothing, and this project has lost a "
            "convergence to exactly that kind of invisible failure")

    def test_a_queryable_target_is_still_dispatched(self):
        from bench.ouroboros_cell import OuroborosCell
        import inspect
        c = OuroborosCell.__new__(OuroborosCell)
        c.MAX_QUERIES_PER_ROUND = 5
        c.allowed_sources = ["arxiv"]
        fn = next(f for n, f in inspect.getmembers(OuroborosCell, inspect.isfunction)
                  if "quer" in n and "build" in n.lower())
        qs = fn(c, ["VERDICT: CONFIRM C0001. `TokenBucket.allow` accepts negative "
                    "`cost` values, which increases the token count."])
        assert len(qs) == 1 and qs[0]["query"].strip()
