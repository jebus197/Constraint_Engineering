"""Code-location novelty keying for convergence detection.

Root cause of CDSFL's recurring non-convergence (verified 2026-06-08): novelty was
decided by free-text similarity (model-chosen finding-id, Jaccard/embedding kappa,
gamma-on-novelty-count). All free-text signals fail on code review because every finding
about one source file looks similar — they cannot tell two distinct defects in the same
file apart, nor recognise a re-worded re-find of the same defect. Empirically: the embedding
ConvergenceDetector at tau_sim_embed=0.55 over-merges Exp 42's findings into ~1 class/round
and FALSELY converges at round 2; the inline model-id path NEVER converges (every re-find
gets a fresh id). Both are the same disease — keying novelty on free text.

The signal that DOES separate code-review defects is the CODE LOCATION: which function /
method / class the finding is about. This module extracts the target file's symbols (AST)
and keys each finding by the symbols it names. A critical finding is "novel" iff it names a
code location not yet flagged by any prior critical.

On Exp 42 this converges at round 7 with a stable zero tail (rounds 5-15 all zero), matching
the signature-trace ground truth (all distinct defects found by ~round 4). The result is
ROBUST to the exact re-find rule (two reasonable variants both give round 7).

Conservative-by-design: a finding counts as NEW if it introduces ANY previously-unseen
location. This biases toward NOT converging (one extra round is cheaper than a missed defect).

Domain-general: works for any Python target file. `target_symbols` accepts source or a path.
For non-Python targets, supply a symbol set directly.

Created 2026-06-08 (T2 discovery). Calibration of the severity threshold and the convergence
window belongs to a null test (clean module -> fast converge) + seeded test (N known defects
-> all found before converge), NEVER to a single experiment's desired answer.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

# Generic identifiers that carry no location information (entry points / dunders).
# Findings naming ONLY these fall back to a single generic bucket.
_GENERIC = frozenset({"main", "compose", "run"})
_MIN_LEN = 4
_GENERIC_BUCKET = "<generic>"


def target_symbols(source_or_path: str) -> FrozenSet[str]:
    """AST-extract function/method/class names from a Python target file.

    Accepts raw source or a filesystem path (``*.py``). Returns names with len > _MIN_LEN
    (short/dunder names are too ambiguous to use as location keys).
    """
    src = source_or_path
    if "\n" not in source_or_path and source_or_path.endswith(".py"):
        with open(source_or_path, "r", encoding="utf-8") as fh:
            src = fh.read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        # Non-Python target (one-shot arc, 2026-07-29): the exam modules are
        # MARKDOWN documents of numbered claims. Without location symbols the
        # novelty key silently reverts to the ID-proxy series (the Exp 42
        # dedup disease). Key markdown targets on their claim IDs (CH-01,
        # EN-07, PH-12, BI-03 style) and section headings instead.
        claim_ids = set(re.findall(r"\b([A-Z]{2}-\d{2})\b", src))
        headings = {
            h.strip().lower().replace(" ", "_")[:40]
            for h in re.findall(r"^#{1,4}\s+(.+)$", src, re.M)
            if len(h.strip()) > _MIN_LEN
        }
        if claim_ids:
            return frozenset(claim_ids | headings)
        return frozenset(headings) if headings else frozenset()
    names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if len(node.name) > _MIN_LEN:
                names.add(node.name)
    return frozenset(names)


def finding_locations(description: str, symbols: Iterable[str]) -> FrozenSet[str]:
    """The subset of `symbols` named (word-boundary match) in a finding description,
    excluding generic identifiers. Empty result means no specific code location."""
    desc = description or ""
    return frozenset(
        s for s in symbols
        if s not in _GENERIC and re.search(r"\b" + re.escape(s) + r"\b", desc)
    )


@dataclass
class LocationNoveltyTracker:
    """Counts NEW critical code-locations per round; declares convergence after K
    consecutive zero-new-critical rounds.

    A critical finding (severity >= severity_threshold) is NEW iff it names at least one
    code location not previously flagged by a critical. Locations named by any critical
    (new or re-find) are accumulated, so an incidental later mention of an already-flagged
    location does not re-trigger novelty.

    Parameters
    ----------
    symbols : the target file's symbol set (from `target_symbols`).
    severity_threshold : critical iff severity >= this (default 0.7 = runner CRITICAL_SEVERITY_THRESHOLD).
    consecutive_required : K consecutive zero-new rounds to converge (default 3).
    earliest_round : do not declare convergence before this round (default 2).
    """
    symbols: FrozenSet[str]
    severity_threshold: float = 0.7
    consecutive_required: int = 3
    earliest_round: int = 2

    _seen_locations: Set[str] = field(default_factory=set)
    _new_per_round: List[int] = field(default_factory=list)
    _zero_streak: int = 0
    _converged_round: Optional[int] = None

    def add_round(self, round_idx: int, findings: Sequence[object]) -> int:
        """Register a round's findings. Returns the count of NEW critical findings
        (those naming a not-yet-flagged code location)."""
        new = 0
        for f in findings:
            sev = getattr(f, "severity", 0.0) or 0.0
            if sev < self.severity_threshold:
                continue
            locs = finding_locations(getattr(f, "description", "") or "", self.symbols)
            key = set(locs) if locs else {_GENERIC_BUCKET}
            if key - self._seen_locations:        # introduces >=1 unseen location
                new += 1
            self._seen_locations |= key
        while len(self._new_per_round) <= round_idx:
            self._new_per_round.append(0)
        self._new_per_round[round_idx] = new
        self._zero_streak = self._zero_streak + 1 if new == 0 else 0
        if (self._converged_round is None
                and round_idx >= self.earliest_round
                and self._zero_streak >= self.consecutive_required):
            self._converged_round = round_idx
        return new

    @property
    def new_per_round(self) -> List[int]:
        return list(self._new_per_round)

    @property
    def converged_round(self) -> Optional[int]:
        return self._converged_round

    def converged(self) -> bool:
        return self._converged_round is not None


# ─────────────────────────────────────────────────────────────────────────────
# THE IDENTITY RULE — two tiers and one narrow question (2026-08-12)
#
# Location keying answers "is this somewhere new?" and gets that right. Its known
# blind spot is a SECOND, genuinely different defect at an already-flagged
# location: it merges the two by construction. This section is what looks inside
# a flagged location.
#
# TIER 1, LOCATION. A critical naming a never-flagged location is NEW. Free.
#
# TIER 2, STEM SIGNATURE — OPERATIVE within an already-flagged location as of
# 2026-08-12 (founder ruling). `stem_signature` compares the HARD technical
# content of two findings — numbers, claim IDs, backticked identifiers — rather
# than their wording, because prose is a lossy re-description that varies every
# time a model writes it while `2016`, `AL-03` and `dedup` do not. Re-measured
# 2026-08-12 over all six completed runs, 438 same-location critical pairs,
# labelled INDEPENDENTLY of the rule under test by the sentence-embedding backend
# (which is part of neither tier): pairs labelled the same defect share a median
# Jaccard of 0.559 (n=28), pairs labelled different share a median of 0.000
# (n=290), Mann-Whitney p = 1.9e-25. Coverage: 161 of 165 criticals (97.6%)
# carry at least one hard token, matching the 97.5% recorded when the tier was
# first measured. It is the part that works, and it now decides.
#
# TIER 3, THE COMPUTED OUTCOME — the founder's second criterion, built 2026-08-12
# (see the block below `computed_outcomes`). One narrow question per candidate
# pair: do these two findings assert the SAME computed value or different ones?
# It can only MERGE. It never grants novelty. That bound is deliberate and is
# what makes its false-DIFFERENT errors free.
#
# THE SAFETY PROPERTY, load-bearing: absence of a distinctness WITNESS means NOT
# COUNTED AS NEW — never "proven the same". The witness is a signature
# disagreement between two NON-EMPTY signatures. If the candidate carries no hard
# token, or any prior AT THAT LOCATION carries none, there is nothing to disagree
# about and the finding is not counted. A located critical with an empty
# signature can therefore never be split by this rule, only merged.
#
# IT APPLIES ONLY WHERE A SHARED LOCATION ALREADY BINDS THE TWO FINDINGS, and
# that qualification is not cosmetic — see the second correction below. Within a
# flagged location, withholding a count costs nothing a gate can see, because
# location keying was going to merge that finding anyway. Applied to the
# UNLOCATED stream it withheld counts the live gate makes, which is the one
# direction that can fake a convergence.
#
# WHAT HOLDS STRUCTURALLY, and it is the only claim a gate may rest on:
#
#     combined >= location keying, elementwise, per round — against BOTH of the
#     two location-keying rules this repo has run.
#
# Naming both is the whole point, because they are different rules and only one
# of them gates anything today:
#
#   * `location_only_series` here — the RETIRED single-`<generic>`-bucket keying
#     the six archived runs were scored with. It is what the archive replay must
#     reproduce, and nothing else.
#   * `reference_runner_v2._location_keyed_critical_series` — the LIVE rule,
#     which keys each unlocated critical on its own content (an empty signature
#     falls back to a hash of its own text) and skips terminal non-novel
#     statuses. THIS is the series that feeds the count side of the two-sided
#     gate, so this is the one the safety claim has to be true about.
#
# Verified elementwise on all six completed runs against both, by
# `test_combined_never_undercounts_location_keying_on_the_archive` and
# `test_combined_never_undercounts_the_live_gating_series`.
#
# THE CLAIM WAS FALSE TWICE, AND MEASUREMENT IS WHAT SAID SO BOTH TIMES.
#
# (1) Against the retired baseline. The subset argument only covers findings that
#     HAVE a location. An unlocated finding used to be compared against every
#     prior, located or not, so a signature match with a LOCATED prior could
#     merge it — while location keying, which keys every unlocated finding into
#     one `<generic>` bucket, counted the first one. Measured: combined
#     undercounted at round 0 on Exp 48 (8 vs 9) and Exp 49 (10 vs 11). Fixed by
#     keying the unlocated stream separately.
#
# (2) Against the LIVE baseline, found 2026-08-12 by adversarial verification and
#     fixed here. Checking only against the retired baseline is checking against
#     a rule no run will ever use again, and it hid a live undercount: Exp 44
#     round 2, combined 2 against the live series' 3. MECHANISM: C0022 is an
#     unlocated critical carrying four hard tokens; the one unlocated prior,
#     C0007, carries none; the safety property therefore withheld the count. The
#     live rule gives C0007 a text-hash key and C0022 its own signature bucket
#     and counts both. WORSE, the guard built to catch exactly this could not:
#     `novelty_rule_divergence`'s `merged` list is computed against the retired
#     bucket too, so it reported n_merged = 0 on Exp 44 while the live-keyed
#     comparison finds two (C0022 at round 2, C0053 at round 6). A detector that
#     cannot report the condition it exists to report is this project's house
#     failure mode, and it was reproduced here in the safety argument itself.
#     FIXED by restricting the safety property to located findings, which is
#     where its rationale actually holds. Measured effect: only Exp 44 moves, and
#     only upward — [6,3,2,2,0,3,1,1,0,0,0,0,0] to [8,3,3,2,0,3,2,1,0,0,0,0,0].
#     Every acceptance (b) tail below is UNCHANGED, so no result a founder is
#     being asked to rule on moved.
#
# (3) THE ROOT CAUSE UNDER BOTH OF THOSE, found the same day by continuing to
#     attack the fixed rule rather than stopping at the first fix: this module
#     was scoring against a different POPULATION from the gate. The live series
#     skips findings whose settled status is terminal-and-not-novel (MERGED,
#     DUPLICATE, UNCONFIRMED, REFUTED) and findings with no `open_since_round`;
#     this module counted them, which FLAGGED THEIR LOCATIONS. Four constructed
#     cases, every one an undercount of the gating series: a REFUTED round-0
#     finding flags `dedup`, and the genuine round-1 critical there is then
#     merged away — combined [1,0] against the live [0,1]. Same with an
#     UNCONFIRMED prior, with a MERGED prior on the unlocated stream, and with an
#     entry whose missing round was silently coerced to 0. FIXED by
#     `_gate_population`, and it is behaviour-neutral on the evidence: the six
#     archived replays still reproduce digit for digit and every acceptance tail
#     is unchanged. Pinned by
#     `test_a_finding_the_gate_never_sees_cannot_merge_one_it_does`.
#
# THE GENERAL LESSON, and it is the one worth keeping: a novelty rule must be
# scored against the population and the keying the GATE uses, not against a
# convenient replay of a retired one. Two of the three defects above were
# invisible to every test in this file until the live rule was driven directly.
#
# PER-DECISION MONOTONICITY STILL DOES NOT COMPOSE INTO PER-SERIES MONOTONICITY,
# and the correction recorded here on 2026-08-08 stands. Tier 3 can only move a
# finding from NEW to NOT-NEW *at that decision*; but a merged finding is not
# appended to `seen`, so a later finding meets fewer priors at that location and
# can escape a merge it would otherwise have suffered. Combined <= tier-2-only
# therefore holds on all six archived runs as a measurement, NOT as a theorem.
# Do not restate it as one.
#
# ACCEPTANCE, run 2026-08-12, offline, zero dispatch.
#
# (a) THE HAND-BUILT SAME-LOCATION DIFFERENT-DEFECT CASES — PASS. Both defects
#     sit on `dedup` in ALG-02-REF-01.md; ground truth by counterfactual repair
#     (fixing either leaves the other standing). All four cross pairs of the two
#     primary wordings return DISTINCT, and tier 3 independently corroborates all
#     four with DIFFERENT:
#
#         D1_A vs D2_A   signature 0.125   outcome DIFFERENT   DISTINCT
#         D1_A vs D2_B   signature 0.143   outcome DIFFERENT   DISTINCT
#         D1_B vs D2_A   signature 0.125   outcome DIFFERENT   DISTINCT
#         D1_B vs D2_B   signature 0.143   outcome DIFFERENT   DISTINCT
#
#     All four same-defect control pairs merge. The series over all five wordings
#     is [2, 0, 0, 0] — two defects, five wordings, correct.
#
#     HONEST EDGE: the terse re-raise D1_C scores 0.200 and 0.250 against the D2
#     wordings — at and above the cut — so as an isolated PAIR it merges with the
#     wrong defect. In the series it never gets the chance: it merges into D1 at
#     0.400 first. A pair-level answer and a series-level answer are different
#     questions and the rule is only ever asked the second.
#
#     THE TWO ARCHIVE PAIRS THE PANEL NAMED (not hand-built; reported for
#     continuity, and the distinction between an isolated pair and a run matters
#     here). Both are separated, and both FELM failed — one by answering SAME at
#     every mutation budget from 5 to 60, the other by having no falsifier to
#     execute at all.
#         Exp 45 C0031 vs C0022: as an isolated pair, TIER 1 — C0031 names
#             `__init__`, which C0022 does not. Signature 0.167; the outcome tier
#             abstains, as neither finding asserts a quantity.
#         Exp 47 C0070 vs C0053: as an isolated pair, TIER 1 — C0070 names
#             `parse_alternative_block`, which C0053 does not. The signature
#             alone would MERGE these, at 0.286.
#     INSIDE their own runs neither is decided that way: every location they name
#     had already been flagged by other findings, so both are counted as
#     `signature_split` — the promoted tier doing the work it was promoted for.
#     An earlier draft of this note reported the Exp 47 pair as MERGED; that came
#     from comparing signatures without locations, and was wrong.
#
# (b) REPLAY AGAINST THE SIX COMPLETED RUNS — FAILS, and it is reported as a
#     failure. Tails are the three rounds ending at each run's recorded
#     convergence round; a tail of zeros means the count side of the gate would
#     still have closed there.
#
#       run    conv  closed via          location-only     promoted rule
#       Exp 44  12    STATE_CONVERGED     [0,0,0] holds     [0,0,0] holds
#       Exp 45   3    two-sided gate      [0,0,0] holds     [1,0,1] BREAKS
#       Exp 46   5    two-sided gate      [0,0,0] holds     [0,1,0] BREAKS
#       Exp 47  13    two-sided gate      [0,0,0] holds     [0,0,1] BREAKS
#       Exp 48   5    STATE_CONVERGED     [0,1,0] BREAKS    [0,1,0] unchanged
#       Exp 49   6    STATE_CONVERGED     [0,0,0] holds     [1,0,0] BREAKS
#
#     Four of six broken. Exp 48's own archived location tail is already non-zero
#     at its convergence round, so nothing can be destroyed there — it closed on
#     the state gate, which does not require a zero count.
#
#     ALL SIX RUNS ARE MEASURABLE, including Exp 48 and Exp 49, whose markdown
#     targets are gone from disk. The 2026-08-08 note recorded those two as
#     unmeasurable; that is now superseded. Their symbol set is the set of claim
#     IDs, and `finding_locations` only ever intersects symbols with a
#     description, so the union of claim IDs appearing across a run's own
#     findings is identical on claim IDs to the full document's set. The
#     reconstruction is not assumed — it is VALIDATED: replaying location-only
#     keying with it reproduces each run's archived `location_crit_shadow_history`
#     exactly, on all six runs, digit for digit.
#
#     THE FIVE FINDINGS THAT BREAK A TAIL, each read rather than counted:
#
#       Exp 45 r1  C0014  `record_experiment` accepts `exp_id` but never
#                         deduplicates on it. Distinct from every prior at that
#                         location. TRUE second defect. Tier 3 CORROBORATES.
#       Exp 45 r3  C0031  `__init__` does not validate `decay_rate`; a negative
#                         value makes `math.exp(-decay_rate)` exceed 1.0. TRUE
#                         second defect — and the panel's own acceptance case,
#                         the one FELM got wrong. Tier 3 abstains: neither this
#                         finding nor its priors assert a quantity.
#       Exp 46 r4  C0026  the `_compute_shadow_e_values` key mismatch. Already
#                         found as C0005/C0006 in round 0. FALSE split: a verbose
#                         re-find whose line numbers and dates dilute the
#                         signature to 0.091. Tier 3 cannot rescue it — both
#                         priors carry no computed outcome at all.
#       Exp 47 r13 C0070  contrast statements stripped before the isomorphism
#                         check. TRUE second defect, and the one the 2026-07-31
#                         audit already named as the archive's real blind-spot
#                         case. Tier 3 abstains.
#       Exp 49 r4  C0037  the EN-16 factor-of-safety convention. Already found as
#                         C0035 in round 3, at signature 0.182 — just under the
#                         cut. FALSE split. Tier 3 abstains: C0035 carries no
#                         number at all.
#
#     Three of the five are genuine second defects that location keying could not
#     see; two are re-finds the signature cut missed. So the honest statement is
#     BOTH of these, and neither on its own:
#       * the rule does destroy convergence on four of six archived runs, which
#         is the stated acceptance criterion and it FAILS it; and
#       * on three of those five occasions the run closed while a genuinely new
#         critical was still arriving, which is what the blind spot always meant.
#     Which of those matters more is a founder judgement, not a code one.
#
#     The one split tier 3 corroborated is a true second defect (1 of 1); two of
#     the four uncorroborated splits are (2 of 4). n = 5. Reported as thin, and
#     the direction is at least not contradicted: corroboration has never yet
#     accompanied a false split.
#
# GAMMA IS UNTOUCHED, and that is checked rather than asserted.
# `gamma_critical` is `_estimate_gamma(_settled_crit, ...)`, and `_settled_crit`
# comes from `_settled_novelty_series`, which reads only `open_since_round`,
# `status` and `severity` off the settled registry. Nothing in this file is on
# that path. What this rule feeds is `novel_critical_history` — the COUNT side of
# the two-sided gate — and nothing else. Pinned by
# `test_gamma_does_not_read_this_rule`; and the archived `gamma_critical_history`
# reproduces exactly from the settled series alone on four of the six runs (Exp 44
# differs at two rounds and Exp 47's recorded history is shorter than its round
# count — both archive artefacts, of post-hoc status changes and a resumed run
# respectively, neither anything to do with novelty keying).
#
# NOT WIRED TO ANY GATE. `hierarchical_novelty_convergence` still defaults False
# and no shipped config sets it. Promotion here means this module's rule now
# decides inside a flagged location; promoting it to the runner's COUNT side is a
# separate change in a separate file, and acceptance (b) above is the evidence a
# founder would need to rule on first.

_NUM_RE = re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?")
_CID_RE = re.compile(r"\b[A-Z]{2,3}-\d{2}\b")
_IDT_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_\.]{2,})`")

WITHIN_LOCATION_THRESHOLD = 0.20


def stem_signature(text: str) -> FrozenSet[str]:
    """The hard, non-paraphrasable content of a finding: numbers, claim IDs and
    code identifiers. Prose is a lossy re-description that varies every time a
    model writes it; `2016`, `AL-03` and `dedup` do not vary. Measured over 160
    real critical findings, 97.5% carry at least one such token."""
    t = text or ""
    return (frozenset(_NUM_RE.findall(t))
            | frozenset(_CID_RE.findall(t))
            | frozenset(i.lower() for i in _IDT_RE.findall(t)))


def signature_similarity(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Jaccard over STEM signatures. Measured on archive ground truth: pairs the
    system merged share a median 0.542; independently-confirmed distinct pairs
    share a median 0.000 (Mann-Whitney p = 7.5e-9). Re-measured 2026-08-12 over
    all six completed runs: 0.559 vs 0.000, p = 1.9e-25."""
    if not (a or b):
        return 0.0
    return len(a & b) / len(a | b)


# ─────────────────────────────────────────────────────────────────────────────
# THE COMPUTED OUTCOME — the founder's second criterion, built 2026-08-12.
#
# THE QUESTION, and it is deliberately the narrowest one that could work: do
# these two findings assert the SAME computed value, or different ones? Not "are
# they similar", not "recompute the target" — which would be wasteful and is
# explicitly not what was asked. One extraction per finding, cached in the
# caller's `seen` list, and a set intersection per candidate pair.
#
# WHY IT IS A SIGNAL AT ALL. STEM prose carries its conclusion as a quantity:
# a molar mass, a combined uncertainty, a stoichiometric coefficient, a factor of
# safety, a comparison count. Two findings about one defect converge on the same
# quantity however differently they are worded; two findings about different
# defects at the same location generally do not. That is a different question
# from the one tier 2 asks, and it can answer where tier 2 is weakest — a verbose
# finding and a terse one about the same defect share almost no tokens (low
# Jaccard) but land on the same number.
#
# WHY IT IS NOT JUST `stem_signature` AGAIN. Three differences, all load-bearing:
#   1. It compares VALUES with a relative tolerance, not strings. `109.128` and
#      `109.13` are the same computed outcome and different tokens.
#   2. It asks for ANY agreement, not a Jaccard fraction, so verbosity on one
#      side does not dilute the answer.
#   3. It removes the numbers that are LABELS rather than measurements — claim
#      IDs, line and section references, ISO dates, `SEVERITY: 0.78`-style
#      metadata — and the values inside pure-identifier backticks and call
#      argument lists, which are data the finding quotes rather than a result it
#      asserts. Formulae in backticks are KEPT, because in exam prose that is
#      exactly where the computed outcome lives.
# A number keeps its ANCHOR — the unit or noun attached to it (`g/mol`, `%`,
# `comparisons`, `inputs`) — so that two unrelated small integers cannot agree by
# coincidence. Bare integers below 10 with no anchor are dropped for the same
# reason. Word numerals are read ("returns a single element" -> 1 element),
# because a great many outcomes are written out rather than digitised.
#
# MEASURED 2026-08-12 on the archive, exactly as tier 2 was measured — all six
# completed runs, 438 same-location critical pairs, labels from the
# sentence-embedding backend, which is part of neither tier:
#
#     coverage: 94 of 165 criticals (57.0%) carry at least one computed outcome
#
#     labelled SAME defect (embedding >= 0.90), n = 28:
#         SAME 19 (68%)   DIFFERENT  0 ( 0%)   UNKNOWN   9 (32%)
#     labelled DIFF defect (embedding <= 0.70), n = 290:
#         SAME 14 ( 5%)   DIFFERENT 30 (10%)   UNKNOWN 246 (85%)
#
#     decided pairs only, 2x2 [[0, 19], [30, 14]]
#     Fisher exact: p = 1.4e-07 (the odds ratio is degenerate — one cell is zero)
#
# Read that against the measurement it replaces. FELM — the mutation-vector tier,
# built to the panel's design and removed from this module on 2026-08-12 — scored
# Fisher p = 0.71 on the same archive: no association whatever between its
# divergence and defect identity. This tier's association is real and large, and
# in this sample it never once called a same-defect pair DIFFERENT. Its weakness
# is different and is stated plainly: it ABSTAINS on 85% of the different-defect
# pairs it is shown, because most code-review criticals are absence-of-validation
# defects that assert no quantity at all. On the two exam targets (Exp 48, Exp 49)
# it answers far more often than on the four code targets, which is exactly where
# the criterion said it would earn its keep.
#
# THE AUTHORITY IS BOUNDED TO MATCH THE MEASUREMENT. It may MERGE — a SAME answer
# overrides a tier-2 split — and it may never grant novelty. So its 4.8%
# false-SAME rate (14 of 290) costs a missed second defect, which is the failure
# this project already accepts from location keying; and a false DIFFERENT — none
# observed in 19 same-defect pairs, but the rate is not zero — costs nothing at
# all, because DIFFERENT is recorded as corroboration and changes no count. That
# is the "one way or another" the criterion asked for: the merge is acted on, the
# distinctness is reported next to the split so a human can see which splits carry
# a second, independent witness and which rest on the signature alone.

_ISODATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_IDENT_TICK_RE = re.compile(r"`[A-Za-z_][A-Za-z0-9_.]*`")
_CALLARGS_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\([^()]*\)")
_META_RE = re.compile(r"(?i)\b(severity|flaw_class|abstraction_index|finding_id|"
                      r"confidence|priority)\b\s*[:=]\s*\d+(\.\d+)?")
_LABELREF_RE = re.compile(
    r"(?i)(\b(line|lines|row|rows|page|pages|section|round|rounds|step|steps|"
    r"item|items|index|indices|figure|table|version|chapter|clause|paragraph)\b|§)"
    r"\s*\.?\s*\d+(\s*[-–]\s*\d+)?")
_QNUM_RE = re.compile(r"(?<![A-Za-z_0-9.])(\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)")
_QTOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|%|\S")
# A compound unit written with a solidus, immediately after the number: g/mol,
# kJ/mol, m/s. The token scanner would otherwise see three tokens and take the
# wrong one — `112.15 g/mol` came out as "mol", which agrees with a count of
# moles.
_SLASH_UNIT_RE = re.compile(r"^\s*([A-Za-z]{1,6}/[A-Za-z]{1,6})(?![A-Za-z0-9_/])")

_WORD_NUMERALS = {"zero": 0, "one": 1, "single": 1, "two": 2, "three": 3, "four": 4,
                  "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                  "eleven": 11, "twelve": 12, "both": 2, "twice": 2, "double": 2,
                  "half": 0.5}

# Words that carry no unit meaning, so they may not serve as an anchor.
_ANCHOR_STOP = {
    "vs", "and", "or", "of", "in", "on", "at", "to", "the", "a", "an", "is", "are",
    "was", "were", "be", "been", "not", "than", "from", "for", "with", "by", "as",
    "if", "that", "which", "but", "so", "it", "its", "this", "these", "those",
    "when", "where", "while", "into", "over", "under", "per", "also", "only",
    "then", "there", "their", "they", "do", "does", "did", "has", "have", "had",
    "should", "would", "could", "will", "can", "may", "must", "because", "since",
    "however", "instead", "rather", "still", "even",
    "true", "false", "none", "null", "nan", "neither", "either", "nor",
    "distinct", "total", "separate", "different", "additional", "extra", "more",
    "fewer", "further", "other", "such", "same", "new", "actual", "correct",
    "incorrect", "stated", "claimed", "expected", "observed", "possible",
    "unique", "valid", "invalid", "full", "whole", "entire", "real", "given",
    "above", "below", "following", "resulting", "final", "first", "second",
}

# Tokens that link a value back to the quantity it belongs to ("the mass is 12").
_ANCHOR_LINK = {"is", "was", "are", "were", "of", "to", "at", "by", "gives", "give",
                "equals", "equal", "yields", "yield", "becomes", "become", "reaches",
                "reach", "totals", "returns", "return", "produces", "produce", "=",
                "exceeds", "exceed", "only", "about", "approximately", "roughly",
                "just"}

_OUTCOME_TOLERANCE = 1e-3

Quantity = Tuple[float, str]


def _mask(match) -> str:
    return "\x00" * len(match.group(0))


def _stem_word(w: str) -> str:
    if len(w) > 3 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("es") and w[-3] in "sxzho":
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def _anchor(word: str) -> str:
    w = word.strip().lower().strip("`'\"().,;:[]{}")
    if not w or not w[0].isalpha() or len(w) < 2:
        return ""
    if not all(c.isalpha() or c in "_-/" for c in w):
        return ""
    if w in _ANCHOR_STOP:
        return ""
    return _stem_word(w)


def computed_outcomes(text: str) -> FrozenSet[Quantity]:
    """The computed quantities a finding ASSERTS, as `(value, anchor)` pairs.

    `anchor` is the unit or noun the number belongs to, normalised and crudely
    singularised: `g/mol`, `%`, `comparison`, `input`. It is `""` when none could
    be identified, which is permitted only for values distinctive enough to stand
    alone (non-integer, or >= 10).

    Labels are not measurements and are removed first: claim IDs, line/section
    references, ISO dates, `SEVERITY: 0.78`-style metadata, values inside
    pure-identifier backticks, and call argument lists. Formulae in backticks are
    kept — in exam prose that is where the answer lives.
    """
    t = text or ""
    for rx in (_IDENT_TICK_RE, _CALLARGS_RE, _ISODATE_RE, _CID_RE, _META_RE,
               _LABELREF_RE):
        t = rx.sub(_mask, t)
    toks = [(m.start(), m.end(), m.group(0)) for m in _QTOKEN_RE.finditer(t)]
    out: Set[Quantity] = set()

    def after(pos_end: int) -> str:
        m = _SLASH_UNIT_RE.match(t[pos_end:])
        if m:
            return m.group(1).lower()
        for (s, _e, w) in toks:
            if s < pos_end:
                continue
            if w == "%":
                return "%"
            if w in {".", ";", ":", ")", "]", "}"}:
                return ""
            a = _anchor(w)
            if a:
                return a
            if w in {",", "(", "["}:
                return ""
        return ""

    def before(pos_start: int) -> str:
        # Only a value that is LINKED to something backwards ("the mass is 12",
        # "n = 64") takes a preceding anchor. Without that guard the scan walks
        # back over arbitrary prose and attaches the nearest verb, which is how
        # "returns 1 and then 2" acquired the anchor "return".
        prev = [w for (_s, e, w) in toks if e <= pos_start][-5:][::-1]
        if not prev or not (prev[0].lower() in _ANCHOR_LINK
                            or prev[0] in {"(", ",", "[", "="}):
            return ""
        i = 0
        while i < len(prev) and (prev[i].lower() in _ANCHOR_LINK
                                 or prev[i] in {"(", ",", "[", "="}):
            i += 1
        while i < len(prev):
            a = _anchor(prev[i])
            if a:
                return a
            if prev[i] in {".", ";"}:
                return ""
            i += 1
        return ""

    for m in _QNUM_RE.finditer(t):
        try:
            v = float(m.group(1))
        except ValueError:            # pragma: no cover — the regex cannot produce this
            continue
        a = after(m.end()) or before(m.start())
        if a or v != int(v) or abs(v) >= 10:
            out.add((v, a))
    for (_s, e, w) in toks:
        if w.lower() in _WORD_NUMERALS:
            a = after(e)
            if a:
                out.add((float(_WORD_NUMERALS[w.lower()]), a))
    return frozenset(out)


def _distinctive(value: float) -> bool:
    """A value that can identify a computation on its own, without a unit."""
    return value != int(value) or abs(value) >= 10


def quantities_agree(q1: Quantity, q2: Quantity,
                     tolerance: float = _OUTCOME_TOLERANCE) -> bool:
    """Do two extracted quantities name the same computed value?

    Relative tolerance, so `109.128` and `109.13` agree. Anchors must match
    unless one is missing or the value is distinctive on its own — `64
    comparisons` and `64 inputs` are the same computation described from two
    sides, while `2 inputs` and `2 rounds` are not.
    """
    v1, a1 = q1
    v2, a2 = q2
    if v1 != v2:
        if v1 == 0 or v2 == 0:
            return False
        if abs(v1 - v2) / max(abs(v1), abs(v2)) > tolerance:
            return False
    if a1 and a2 and a1 != a2:
        return _distinctive(v1)
    return True


def outcome_agreement(a: Iterable[Quantity], b: Iterable[Quantity]) -> str:
    """SAME, DIFFERENT or UNKNOWN — the single narrow question.

    UNKNOWN whenever either finding asserts no computed value; that is an
    abstention, not a finding of similarity, and the caller must not read it as
    one.
    """
    a = frozenset(a)
    b = frozenset(b)
    if not a or not b:
        return "UNKNOWN"
    for q1 in a:
        for q2 in b:
            if quantities_agree(q1, q2):
                return "SAME"
    return "DIFFERENT"


# ─────────────────────────────────────────────────────────────────────────────
# The decision, and the three entry points that share it.


@dataclass(frozen=True)
class Prior:
    """One finding already COUNTED, as the identity rule needs to see it. Public
    so a caller can drive `identity_decision` directly instead of re-deriving
    the rule — a second implementation of a rule is a second rule."""
    locations: FrozenSet[str]
    signature: FrozenSet[str]
    outcomes: FrozenSet[Quantity]
    canonical_id: str = ""


@dataclass(frozen=True)
class IdentityDecision:
    """Why a finding was or was not counted. `reason` is the audit key."""
    is_new: bool
    reason: str
    corroborated: bool = False
    locations: FrozenSet[str] = frozenset()
    signature: FrozenSet[str] = frozenset()
    outcomes: FrozenSet[Quantity] = frozenset()


def _priors_for(seen: Sequence[Prior], locations: FrozenSet[str]) -> List[Prior]:
    """Priors this finding must be told apart from.

    An unlocated finding is compared ONLY against unlocated priors. Comparing it
    against located ones let a signature match merge a finding that location
    keying counted, which broke `combined >= location-only` on Exp 48 and Exp 49.
    """
    if locations:
        return [p for p in seen if p.locations & locations]
    return [p for p in seen if not p.locations]


def identity_decision(description: str, symbols, seen: Sequence[Prior], *,
                      within_threshold: float = WITHIN_LOCATION_THRESHOLD,
                      use_outcomes: bool = True) -> IdentityDecision:
    """Is this critical finding NEW? The whole rule, in one place."""
    desc = description or ""
    locs = finding_locations(desc, symbols)
    sig = stem_signature(desc)
    out = computed_outcomes(desc) if use_outcomes else frozenset()

    def _new(reason: str, corroborated: bool = False) -> IdentityDecision:
        return IdentityDecision(True, reason, corroborated, locs, sig, out)

    def _old(reason: str) -> IdentityDecision:
        return IdentityDecision(False, reason, False, locs, sig, out)

    if locs:
        known: Set[str] = set()
        for p in seen:
            known |= p.locations
        if locs - known:
            return _new("new_location")
    priors = _priors_for(seen, locs)
    if not priors:
        return _new("first_at_location")
    if any(signature_similarity(sig, p.signature) >= within_threshold
           for p in priors):
        return _old("signature_merge")
    # The safety property: no witness, no count — and ONLY where a shared
    # LOCATION already binds the two findings. On the unlocated stream this
    # withheld counts the LIVE gating series makes (Exp 44 round 2, 2 vs 3),
    # which is the one direction that can fake a convergence. See the block
    # above, correction (2).
    if locs and (not sig or any(not p.signature for p in priors)):
        return _old("no_distinctness_witness")
    if use_outcomes:
        answers = [outcome_agreement(out, p.outcomes) for p in priors]
        if "SAME" in answers:
            return _old("same_computed_outcome")
        return _new("signature_split", corroborated="DIFFERENT" in answers)
    return _new("signature_split")


# Post-reconciliation statuses that are NOT genuine novelty. Held as a LOCAL
# copy of `reference_runner_v2._NON_NOVEL_TERMINAL_STATUSES` because this module
# must stay a LEAF — the runner imports it, so importing the runner back would
# make the graph circular. A second copy of a constant is a second constant, so
# `test_the_excluded_status_set_matches_the_runner` fails if they ever drift.
_NON_NOVEL_TERMINAL_STATUSES = frozenset({"MERGED", "DUPLICATE", "UNCONFIRMED",
                                          "REFUTED"})


def _gate_population(entries) -> List[dict]:
    """The findings the CONVERGENCE GATE actually sees, in gate order.

    THE DEFECT THIS CLOSES, found 2026-08-12 by adversarial verification and the
    root cause shared by both corrections in the block above: this module scored
    its rule against a different POPULATION from the one the gate counts.
    `reference_runner_v2._location_keyed_critical_series` skips entries whose
    settled status is terminal-and-not-novel, and entries with no
    `open_since_round` at all. This module counted them, which flags their
    locations — so a REFUTED round-0 finding could flag a location and the
    genuine round-2 critical there would then be merged away. The live rule never
    flagged that location and counts the real finding.

    Constructed and reproduced, all four surviving as undercounts of the gating
    series before this filter: a REFUTED prior, an UNCONFIRMED prior, a MERGED
    prior on the unlocated stream, and an entry with `open_since_round = None`.
    Undercounting the gating series is the one direction that can close a gate
    location keying holds open, so this is not a tidying change.

    Behaviour-neutral on the evidence: with this filter `location_only_series`
    still reproduces all six archived `location_crit_shadow_history` series digit
    for digit, and every acceptance (b) tail is unchanged.
    """
    vals = list(entries.values()) if isinstance(entries, dict) else list(entries)
    keep = [e for e in vals
            if e.get("status") not in _NON_NOVEL_TERMINAL_STATUSES
            and e.get("open_since_round") is not None
            and e.get("open_since_round") >= 0]
    keep.sort(key=lambda e: (e.get("open_since_round"),
                             str(e.get("canonical_id", ""))))
    return keep


def _round_of(e) -> int:
    """The round a finding opened in.

    `_gate_population` has already dropped entries without one, so a None here is
    a broken invariant and it says so. It must never quietly become round 0 —
    that coercion is what let an unrounded finding claim the round-0 slot and
    flag its location before the gate had seen anything at all.
    """
    r = e.get("open_since_round")
    if r is None:
        raise ValueError(
            f"finding {e.get('canonical_id')!r} reached the novelty rule with no "
            f"open_since_round; _gate_population is supposed to drop those")
    return int(r)


def _criticals(entries, max_round: int, critical_threshold: float) -> List[dict]:
    crits = [e for e in _gate_population(entries)
             if (e.get("severity") or 0.0) >= critical_threshold]
    return [e for e in crits if _round_of(e) <= max_round]


def combined_novelty_series(entries, max_round: int, symbols, *,
                            within_threshold: float = WITHIN_LOCATION_THRESHOLD,
                            critical_threshold: float = 0.7,
                            use_outcomes: bool = True) -> Dict[str, object]:
    """Per-round count of NEW critical findings under the two-tier identity rule.

    Returns a dict, not a bare list, because a bare list is unreadable evidence.
    `audit` counts every decision by reason and they must sum to the number of
    criticals considered. `splits` lists the findings counted as new by the
    SIGNATURE rather than by location — the blind-spot candidates — each flagged
    with whether the computed-outcome tier independently corroborated the split.
    Most sit inside an already-flagged location; some are unlocated criticals
    told apart from other unlocated criticals, which is the same question asked
    of a stream location keying cannot speak to at all. `locations` on each
    record says which, and an empty list means the unlocated stream.

    Pure computation over the final registry: no execution, no dispatch, no cost.
    """
    crits = _criticals(entries, max_round, critical_threshold)
    series = [0] * (max_round + 1)
    seen: List[Prior] = []
    splits: List[dict] = []
    audit: Dict[str, int] = {
        "criticals": len(crits), "new_location": 0, "first_at_location": 0,
        "signature_merge": 0, "no_distinctness_witness": 0,
        "same_computed_outcome": 0, "signature_split": 0,
        "splits_corroborated_by_outcome": 0, "splits_uncorroborated": 0,
    }
    for e in crits:
        desc = e.get("description", "") or ""
        cid = str(e.get("canonical_id", ""))
        d = identity_decision(desc, symbols, seen,
                              within_threshold=within_threshold,
                              use_outcomes=use_outcomes)
        audit[d.reason] = audit.get(d.reason, 0) + 1
        if not d.is_new:
            continue
        r = _round_of(e)
        series[r] += 1
        seen.append(Prior(d.locations, d.signature, d.outcomes, cid))
        if d.reason == "signature_split":
            audit["splits_corroborated_by_outcome" if d.corroborated
                  else "splits_uncorroborated"] += 1
            splits.append({"canonical_id": cid, "round": r,
                           "severity": e.get("severity"),
                           "locations": sorted(d.locations),
                           "outcome_corroborated": d.corroborated,
                           "description": desc[:240]})
    return {"series": series, "audit": audit, "splits": splits,
            "within_threshold": within_threshold}


def hierarchical_novelty_series(entries, max_round: int, symbols,
                                *, within_threshold: float = WITHIN_LOCATION_THRESHOLD,
                                critical_threshold: float = 0.7) -> List[int]:
    """The bare per-round series. Same rule as `combined_novelty_series`, without
    the audit — kept because the runner and `bench/tools/simulated_bench.py`
    record it as telemetry and want a list."""
    out = combined_novelty_series(entries, max_round, symbols,
                                  within_threshold=within_threshold,
                                  critical_threshold=critical_threshold)
    series = out["series"]
    assert isinstance(series, list)
    return list(series)


def location_only_series(entries, max_round: int, symbols, *,
                         critical_threshold: float = 0.7) -> List[int]:
    """The RETIRED location-keyed baseline, replayed from a finished registry.

    Present so the archive replay can be validated against something computed
    here rather than against a number copied out of a report. Uses the single
    `<generic>` bucket for unlocated findings, which is what the six archived
    runs were scored with; it reproduces every one of their recorded
    `location_crit_shadow_history` series exactly, and that reproduction is the
    precondition for every other number measured off those runs.

    IT IS NOT THE LIVE GATING RULE and must never be used alone to argue that
    this module is safe to gate on. The live rule is
    `reference_runner_v2._location_keyed_critical_series`: it keys each unlocated
    critical on its own content instead of one shared bucket, and skips terminal
    non-novel statuses. Checking the elementwise claim against this function
    alone hid a real undercount of the live series on Exp 44 — see correction (2)
    in the block above.
    """
    crits = _criticals(entries, max_round, critical_threshold)
    seen: Set[str] = set()
    series = [0] * (max_round + 1)
    for e in crits:
        locs = finding_locations(e.get("description", "") or "", symbols)
        key = set(locs) if locs else {_GENERIC_BUCKET}
        if key - seen:
            series[_round_of(e)] += 1
        seen |= key
    return series


def novelty_rule_divergence(entries, symbols, *,
                            within_threshold: float = WITHIN_LOCATION_THRESHOLD,
                            critical_threshold: float = 0.7) -> Dict[str, object]:
    """WHERE the two rules disagree, not just by how much.

    Two number sequences tell a reader that the rules differ. They do not say
    which findings to look at, and a disagreement is only useful if a human can
    inspect the specific case. This returns the findings the identity rule calls
    NEW that location keying would have merged — i.e. the candidate
    second-defects-at-a-known-location, which is the entire blind spot — each
    marked with whether the computed-outcome tier corroborated it.

    Cheap: pure computation over the final registry, no dispatch.
    """
    crits = [e for e in _gate_population(entries)
             if (e.get("severity") or 0.0) >= critical_threshold]
    seen_loc: Set[str] = set()
    seen: List[Prior] = []
    split, merged = [], []
    for e in crits:
        desc = e.get("description", "") or ""
        locs = finding_locations(desc, symbols)
        loc_new = bool((set(locs) if locs else {_GENERIC_BUCKET}) - seen_loc)
        d = identity_decision(desc, symbols, seen, within_threshold=within_threshold)
        rec = {
            "canonical_id": e.get("canonical_id"),
            "round": e.get("open_since_round"),
            "severity": e.get("severity"),
            "locations": sorted(locs),
            "reason": d.reason,
            "outcome_corroborated": d.corroborated,
            "description": desc[:240],
        }
        if d.is_new and not loc_new:
            # The blind-spot candidate: a second distinct defect at a known location.
            split.append(rec)
        elif loc_new and not d.is_new:
            # The opposite disagreement. It must not happen — see the elementwise
            # claim above — so if this list is ever non-empty, that claim has
            # broken and the gate argument with it.
            #
            # HONEST LIMIT OF THIS DETECTOR: `loc_new` above is computed against
            # the RETIRED single-bucket keying, so this list speaks only to that
            # baseline. It reported 0 on Exp 44 while a live-keyed comparison
            # found 2 (see correction (2) in the block above). The live claim is
            # held by `test_combined_never_undercounts_the_live_gating_series`
            # instead, which drives the runner's own function rather than a
            # second copy of it here — a second implementation of a rule is a
            # second rule, and this module is not the place to keep one.
            merged.append(rec)
        if d.is_new:
            seen.append(Prior(d.locations, d.signature, d.outcomes,
                               str(e.get("canonical_id", ""))))
        seen_loc |= set(locs) if locs else {_GENERIC_BUCKET}
    return {
        "hierarchical_splits_location_merges": split,
        "location_splits_hierarchical_merges": merged,
        "n_split": len(split),
        "n_merged": len(merged),
        "within_threshold": within_threshold,
    }


# ─────────────────────────────────────────────────────────────────────────────
# RETIRED: FELM — Falsifier Equivalence via Local Mutation. Built to the panel's
# design 2026-08-08, MEASURED AND REFUTED on this project's own archive the same
# day, and REMOVED FROM THE DECISION PATH on 2026-08-12 on the founder's ruling:
# "if the model's contribution doesn't work and is ineffective, why leave it in
# place at all?" There was no good answer. The code is gone; the measurement is
# kept, because a measured negative result is a finding and this project does not
# discard those. Nothing below runs. It is here to be read.
#
# THE IDEA. Two criticals land at one location. Mutate the target locally,
# execute BOTH findings' falsifiers against the original and every mutant, and
# compare the two boolean response vectors. Identical vectors mean the two
# falsifiers are sensitive to exactly the same code, so they are probing one
# defect; divergence is a WITNESS that they are probing different ones. No model
# call, no paid dispatch. The safety rule was the same one the surviving tiers
# keep: absence of a witness means NOT COUNTED AS NEW, never "proven the same".
#
# THE INSTRUMENT WAS VALIDATED FIRST. 4 of 12 mutants of `bench/dm/_memory.py`
# were killed by `test_immune_memory_consumption.py`, 8 of 12 mutants of
# `bench/evidence.py` by `test_evidence.py` — semantically live mutants, not
# cosmetic ones. (The first run of that check reported 0 of 12 everywhere: the
# harness had the real repo on `sys.path[0]`, so nothing had been executed
# against a mutant at all. Under that fault every comparison returns Hamming 0,
# and Hamming 0 was FELM's word for "same defect" — a silent instrument failure
# indistinguishable from a positive finding.)
#
# THEN THE FALSIFIERS, over the four completed runs with a surviving Python
# target (Exp 44, 45, 46, 47 — 101 criticals carrying a runnable falsifier),
# 16 mutants each:
#
#   run     falsifiers   distinct response vectors   largest identical class
#   Exp 44      34                 8                      21  (62%)
#   Exp 45      12                 8                       4  (33%)
#   Exp 46      12                 2                      11  (92%)
#   Exp 47      43                 5                      38  (88%)
#
# 74 of 101 falsifiers share ONE vector: CONFIRMED on the original and on every
# mutant. FELM cannot tell those 74 apart from each other at all.
#
# THE DECISIVE TEST. Over 351 same-location critical pairs whose falsifiers both
# run on the unmutated target, labelled INDEPENDENTLY by the sentence-embedding
# backend:
#
#   labelled SAME defect (embedding >= 0.90):  n=7,   FELM diverged on 43%   (want 0%)
#   labelled DIFF defect (embedding <= 0.70):  n=269, FELM diverged on 52%   (want 100%)
#   Fisher exact [[3,4],[140,129]]: odds 0.691, p = 0.71
#
# No association. FELM's divergence carried no measurable signal about defect
# identity on this archive. Identical result comparing the four-valued verdict
# instead of the CONFIRMED boolean.
#
# BOTH STATED ACCEPTANCE CASES FAILED.
#   Exp 45 C0031 vs C0022: Hamming 0 at every budget tried — 5, 12, 16, 40 and 60
#       mutants, and whether scoped to `record_experiment`, to `ImmuneMemory`, or
#       to the whole file. FELM said SAME. The vectors were identical, not close.
#   Exp 47 C0070 vs C0053: C0053 is UNTOOLABLE and carries no falsifier, so there
#       was nothing to execute and the safety rule returned NOT COUNTED AS NEW.
#
# WHY, MECHANICALLY. Both Exp 45 findings are absence-of-validation defects
# ("does not validate decay_rate", "accepts negative counts"). A mutation cannot
# remove a check that was never written, so no mutation of the existing code can
# flip either falsifier's verdict. What FELM actually measured is shared
# EXECUTION-PATH sensitivity, not defect identity: both falsifiers call
# `record_experiment`, so they rise and fall together. Absence-of-check findings
# are the dominant critical class in this archive, and they are exactly the class
# FELM is blind to.
#
# FELM WAS NOT VACUOUS — it worked where its design assumed. Positive control on
# the `dedup` listing of ALG-02-REF-01.md, two defects that live in code that
# exists (quadratic list membership; `==` conflating 1, 1.0 and True): Hamming 3,
# correctly DISTINCT; and both same-defect controls on that listing gave
# Hamming 0, correctly SAME. That boundary is why the technique is worth
# remembering: it needs the defect to be IN the code, not missing from it.
#
# LEFT ENABLED IT WAS ALSO NEARLY INERT. It vetoed almost every tier-2 split —
# 12 of 13, 3 of 3, 3 of 4 and 20 of 23 on the four measurable runs — so the
# combined series degenerated to location keying with a handful of witnessed
# splits. Replaying it mostly did not destroy convergence, not because the rule
# was right but because it barely acted. A rule that survives its acceptance test
# by being inert has not passed it.
#
# The two findings from that work that DID survive and are now load-bearing
# above: (1) per-decision monotonicity does not compose into per-series
# monotonicity, because a merged finding is not appended to `seen`; and (2) the
# only structural claim a gate may rest on is combined >= location-only,
# elementwise.
