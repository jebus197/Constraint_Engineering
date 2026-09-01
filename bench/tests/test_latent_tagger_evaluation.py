"""Latent tagger + severity calibration — EVALUATION on the whole archive.

Measured 2026-08-12. ``bench/tests/test_latent_tagger.py`` tests the mechanism;
this file asks the different question the founder put: is there evidence it is
safe to enable, and did it ever demonstrate the utility it was built for. The
two files are complementary and neither replaces the other.

WHAT THIS FILE MEASURES, AND WHERE THE NUMBERS CAME FROM
--------------------------------------------------------
Every archived report carrying a registry — 28 reports, 2247 findings, Exp 33
through Exp 49 — not the six-run Exp 44-49 slice the existing suite and
``bench/validate_latent_tagger.py`` use. Widening the corpus is what surfaced the
quoted-text defect fixed below: it lives in Exp 40, outside the old slice.

THE HEADLINE, and it answers the safety question directly. Running the tagger
and the calibration sweep over every archived registry changes NO
decision-carrying field on ANY run: not one severity, not one status, not one
falsifier verdict. Nothing is demoted anywhere. No run's convergence outcome or
convergence round can therefore move, and that is a stronger statement than
comparing recomputed series, because the inputs to every downstream channel are
themselves unchanged. (It has to be stronger: as
``bench/validate_latent_tagger.py`` section [0] establishes, the live per-round
critical series is NOT reconstructible from a final registry, so a series
comparison alone would rest on a basis the run never computed.)

THE COROLLARY, which is the honest reading of the same number. The mechanism is
safe to enable because it is INERT, not because it was shown to work. Zero of
2247 archived findings carry the explicit ``REACHABILITY:``/``TRIGGER:``/
``LATENT:`` field the module names as its intended long-run source — no finding
schema asks the panel for reachability, so that source has never had a single
input in the project's history. Five findings carry prose a marker matched, none
reaches demotion.

THE DEFECT FOUND AND FIXED HERE
-------------------------------
The latency judgement used to read ``proposed_fix``, which is a SEARCH/REPLACE
patch by construction and therefore carries the TARGET file's own comments
verbatim. Exp 40 ``slice_records`` C0020 and C0048 were both tagged latent on the
target's comment "observation-only collision detection", quoted inside their
patch bodies, while each finding's own description says the opposite: "silently
drops duplicate findings ... misrouted or lost". CORRECTED on the adversarial
pass, same day: an earlier draft of this paragraph said the data-loss interlock
was all that kept them, and that was wrong — both entries carry an empty
``falsifier_verdict``, so demotion is refused at condition (2) and the category
is never consulted. The category is what would hold them under the modern
falsifier-CONFIRMED regime, not what held them here; both statements are pinned
below. The same contamination reached the explicit-field source through
fenced code blocks in a description. Both are the module's existing
``falsifier_code`` rule — read what the finding ASSERTS, never what it QUOTES —
left half-applied. ``_latency_text`` now applies it consistently; category
classification still reads the wide text, so no never-demote veto is lost.

WHAT IS NOT FIXED, AND IS RECORDED HERE INSTEAD
-----------------------------------------------
``TestFalseLatentExposure`` is a characterisation, not an endorsement. The prose
markers match on MENTION, not on ASSERTION: they carry no negation, referent or
attribution awareness, so a finding whose defect IS that something stopped being
observation-only reads as a latency claim. Nine constructed, genuinely
triggerable findings are still tagged latent and seven of them reach demotion
eligibility. One instance is archive-real (Exp 40 ``slice_collision`` C0002).
This is the same referent ambiguity that already forced the "never reached"
family out of the marker set, unfixed for the remaining markers, and the
evidence says the prose source should follow it out. That is a design ruling,
not a defect repair, so it is measured here and left to the founder.
"""

from __future__ import annotations

import copy
import glob
import json
import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import bench.latent_tagger as lt  # noqa: E402
from bench.latent_tagger import (  # noqa: E402
    NEVER_DEMOTE_CATEGORIES,
    tag_entry,
    tag_registry,
)
from bench.reference_runner_v3 import (  # noqa: E402
    FindingRegistry,
    RunnerConfig,
    _apply_severity_calibration,
    _is_demotion_eligible,
)

# The runner's own call site, bench/reference_runner_v3.py: the tagger is swept
# with these skipped and the calibrator additionally skips REFUTED. Mirrored
# here so this evaluation measures the population the runner would actually see.
RUNNER_SKIP_STATUSES = {"MERGED", "CLOSED", "DUPLICATE"}

# Fields whose value decides something downstream. Bookkeeping the tagger adds
# (`latent`, `latent_source`, `latent_evidence`, `finding_category`) is excluded
# on purpose: writing those is the tagger doing its job, and none of them is read
# by a convergence channel. `severity` is what every critical-counting channel
# reads against CRITICAL_SEVERITY_THRESHOLD.
DECISION_FIELDS = (
    "severity", "status", "falsifier_verdict", "open_since_round",
    "severity_calibrated", "severity_original",
)


def _cfg(**kw) -> RunnerConfig:
    cfg = RunnerConfig(experiment_name="latent-eval", models=["CC2"])
    for k, v in kw.items():
        setattr(cfg, k, v)
    return cfg


def _archived_runs():
    """(run_name, report_dict) for every archived report carrying a registry."""
    out = []
    for path in sorted(glob.glob(os.path.join(
            _ROOT, "bench", "logs", "*", "*report*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        reg = data.get("registry")
        if isinstance(reg, dict) and isinstance(reg.get("entries"), dict):
            out.append((os.path.basename(os.path.dirname(path)), data))
    return out


_RUNS = _archived_runs()
_needs_archive = pytest.mark.skipif(
    not _RUNS, reason="archived run reports not present")


def _decision_state(entries):
    return {cid: {k: e.get(k) for k in DECISION_FIELDS}
            for cid, e in entries.items()}


# ── The archive: what enabling the pair would actually have done ────────────


@_needs_archive
class TestArchiveExposure:
    """Measured 2026-08-12 over every archived run, not a six-run slice."""

    def test_corpus_is_the_whole_archive_not_a_slice(self):
        """Guards the basis. If runs are added the numbers below must be
        re-measured rather than silently re-interpreted."""
        assert len(_RUNS) >= 28, f"archive shrank: {len(_RUNS)} runs"
        total = sum(len(d["registry"]["entries"]) for _, d in _RUNS)
        assert total >= 2247, f"archive shrank: {total} findings"

    def test_full_pipeline_changes_no_decision_field_on_any_run(self):
        """THE SAFETY RESULT. Tagger + calibration, both fully enabled, over
        every archived registry: no severity, status, verdict or calibration
        field moves anywhere. A convergence outcome or round cannot move when
        the inputs to every critical-counting channel are unchanged — which is
        a stronger claim than comparing recomputed series, and it has to be:
        the live per-round critical series is not reconstructible from a final
        registry (see bench/validate_latent_tagger.py section [0])."""
        moved = []
        for name, data in _RUNS:
            reg = FindingRegistry.from_dict(copy.deepcopy(data["registry"]))
            before = _decision_state(reg.entries)
            tag_registry(reg, skip_statuses=RUNNER_SKIP_STATUSES)
            n = _apply_severity_calibration(
                reg, _cfg(severity_calibration_enabled=True), 99)
            after = _decision_state(reg.entries)
            if n or before != after:
                moved.append(f"{name}: demoted={n}")
        assert moved == [], (
            "enabling the pair would have changed an archived run — the "
            f"safety measurement no longer holds: {moved}")

    def test_nothing_in_the_archive_is_demotion_eligible(self):
        """Same result one step upstream, so a failure says WHICH gate moved."""
        eligible = []
        for name, data in _RUNS:
            for cid, entry in data["registry"]["entries"].items():
                e = dict(entry)
                tag_entry(e)
                if _is_demotion_eligible(e):
                    eligible.append(f"{name}/{cid} sev={e.get('severity')} "
                                    f"src={e.get('latent_source')}")
        assert eligible == [], (
            "a finding is now demotion-eligible that was not when measured; "
            f"review each by hand before loosening anything: {eligible}")

    def test_the_designed_evidence_source_has_never_had_one_input(self):
        """UTILITY, answered directly. The module names an explicit panel-emitted
        REACHABILITY/TRIGGER/LATENT field as its intended long-run source. No
        finding schema asks for it, so across the entire archive not one finding
        supplies one. Everything the tagger has ever had to read is prose it was
        built to distrust."""
        with_field = [
            f"{name}/{cid}"
            for name, data in _RUNS
            for cid, e in data["registry"]["entries"].items()
            if lt._explicit_field(lt._latency_text(e)) is not None
        ]
        assert with_field == [], (
            "a finding now carries an explicit reachability field — the "
            f"'never exercised' finding is out of date: {with_field}")

    def test_prose_source_tags_five_findings_and_none_reaches_demotion(self):
        """The measured base rate, pinned so a loosened marker set is visible."""
        tagged = sorted(
            f"{name}/{cid}"
            for name, data in _RUNS
            for cid, e in data["registry"]["entries"].items()
            if tag_entry(dict(e))
        )
        assert tagged == [
            "exp33_endocrine_20260405T110345Z/C0010",
            "exp35_pe_20260406T152126Z/C0017",
            "exp40_gate_20260514T020550Z/C0295",
            "exp40_slice_collision_20260518T130744Z/C0002",
            "exp46_stage6_locationkey_live_20260728T103151Z/C0002",
        ], tagged


# ── The never-demote interlock ──────────────────────────────────────────────


class TestNeverDemoteInterlock:
    """The hazard the design guards against: a safety / core-functionality /
    security / data-loss finding must NEVER be demoted, latent or not."""

    @staticmethod
    def _maximally_eligible(category):
        """Everything the calibrator asks for, so ONLY the category can refuse."""
        return {
            "canonical_id": "C0001",
            "severity": 0.99,
            "status": "CONFIRMED",
            "falsifier_verdict": "CONFIRMED",
            "latent": True,
            "latent_source": "explicit_field",
            "open_since_round": 0,
            "finding_category": category,
            "description": "REACHABILITY: no in-repo caller reaches this.",
            "proposed_fix": "",
        }

    @pytest.mark.parametrize("category", sorted(NEVER_DEMOTE_CATEGORIES))
    @pytest.mark.parametrize("case", ["lower", "upper", "padded"])
    def test_constructed_case_never_demoted_through_the_real_sweep(
            self, category, case):
        """Constructed proof, run through the REAL _apply_severity_calibration —
        not through _is_demotion_eligible alone, because the sweep is what a live
        run calls. Case and whitespace varied: the interlock normalises, and a
        veto that only worked on one spelling would be no veto at all."""
        written = {"lower": category, "upper": category.upper(),
                   "padded": f"  {category.title()} "}[case]
        reg = FindingRegistry()
        reg.entries = {"C0001": self._maximally_eligible(written)}
        n = _apply_severity_calibration(
            reg, _cfg(severity_calibration_enabled=True,
                      severity_calibration_floor=0.10), 5)
        assert n == 0, f"{written!r} was demoted"
        assert reg.entries["C0001"]["severity"] == 0.99
        assert "severity_calibrated" not in reg.entries["C0001"]

    def test_the_control_confirms_the_sweep_would_otherwise_fire(self):
        """Without the guard the same entry IS demoted. Without this the test
        above would pass against a sweep that demotes nothing at all — the
        project's own governing failure mode, a guard that cannot report."""
        reg = FindingRegistry()
        reg.entries = {"C0001": self._maximally_eligible("performance")}
        n = _apply_severity_calibration(
            reg, _cfg(severity_calibration_enabled=True,
                      severity_calibration_floor=0.10), 5)
        assert n == 1
        assert reg.entries["C0001"]["severity"] == 0.10
        assert reg.entries["C0001"]["severity_original"] == 0.99

    @_needs_archive
    def test_exp46_c0002_is_saved_by_the_interlock_and_nothing_else(self):
        """THE ARCHIVE-REAL CASE, and the only one in the whole corpus where the
        mechanism came close to firing on live data.

        Exp 46 C0002: falsifier CONFIRMED, severity exactly at the 0.70 critical
        threshold, and a genuine panel latency claim in its own severity line —
        "module is shadow/observation-only". Every condition for demotion holds
        except the category. It is classed data_loss on "silently empty results"
        and that alone keeps it critical. Delete the interlock and a demonstrated
        critical from a converged run is demoted."""
        data = dict(_RUNS)["exp46_stage6_locationkey_live_20260728T103151Z"]
        entry = dict(data["registry"]["entries"]["C0002"])
        assert tag_entry(entry) is True
        assert entry["severity"] == 0.7
        assert entry["falsifier_verdict"] == "CONFIRMED"
        assert entry["finding_category"] == "data_loss"
        assert _is_demotion_eligible(entry) is False

        without_veto = dict(entry, finding_category="")
        assert _is_demotion_eligible(without_veto) is True, (
            "the interlock is no longer what saves Exp 46 C0002 — re-measure "
            "before concluding the guard still does any work")


# ── The fix: a latency tag reads what the finding asserts, not what it quotes ─


class TestQuotedTextIsNotTheFindingsClaim:
    """Fixed 2026-08-12 in bench/latent_tagger.py::_latency_text."""

    @_needs_archive
    def test_exp40_patch_body_contamination_no_longer_tags(self):
        """REGRESSION, archive-real. Both findings' proposed_fix quotes the
        target file's comment "observation-only collision detection"; both
        descriptions say the code silently drops records. Reading the patch body
        tagged them latent on the target's words."""
        data = dict(_RUNS)["exp40_slice_records_20260518T160503Z"]
        for cid in ("C0020", "C0048"):
            entry = dict(data["registry"]["entries"][cid])
            assert "observation-only" in str(entry.get("proposed_fix")), (
                f"{cid} no longer quotes the target comment — this regression "
                "test has lost its subject")
            assert tag_entry(entry) is False, f"{cid} tagged latent again"
            assert entry["latent_source"] == "default_reachable"

    @_needs_archive
    def test_the_category_veto_survives_the_narrowing(self):
        """The unsafe direction of the same fix, checked. Category
        classification still reads description AND proposed_fix, so narrowing
        the latency text cannot strip a never-demote veto."""
        data = dict(_RUNS)["exp40_slice_records_20260518T160503Z"]
        for cid in ("C0020", "C0048"):
            entry = dict(data["registry"]["entries"][cid])
            tag_entry(entry)
            assert entry["finding_category"] == "data_loss"

    def test_category_marker_living_only_in_the_proposed_fix_still_vetoes(self):
        """Explicit: a data-loss marker present ONLY in the proposed fix must
        still reach the interlock, or the narrowing traded one failure for a
        worse one."""
        entry = {
            "canonical_id": "C1", "severity": 0.9, "status": "CONFIRMED",
            "falsifier_verdict": "CONFIRMED", "open_since_round": 0,
            "description": "REACHABILITY: no in-repo caller reaches this helper.",
            "proposed_fix": "Stop the writer silently dropping the last record.",
        }
        assert tag_entry(entry) is True
        assert entry["finding_category"] == "data_loss"
        assert _is_demotion_eligible(entry) is False

    def test_a_fenced_block_cannot_supply_a_reachability_field(self):
        """The same contamination through the DESIGNED source. A description
        that quotes an obsolete REACHABILITY header in order to refute it was
        read as asserting it — and the explicit field outranks everything."""
        entry = {
            "canonical_id": "C1", "severity": 0.85, "status": "CONFIRMED",
            "falsifier_verdict": "CONFIRMED", "open_since_round": 0,
            "description": (
                "verify() returns a stale verdict on the default ingestion "
                "path. The header block it replaced read:\n\n```\n"
                "REACHABILITY: unreachable in the legacy design\n```\n\n"
                "That header is obsolete; the path is live today."
            ),
            "proposed_fix": "",
        }
        assert tag_entry(entry) is False
        assert _is_demotion_eligible(entry) is False

    def test_a_real_field_outside_a_fence_is_still_read(self):
        """The fix must not have killed the source it was protecting."""
        entry = {
            "canonical_id": "C1", "severity": 0.85, "status": "CONFIRMED",
            "falsifier_verdict": "CONFIRMED", "open_since_round": 0,
            "description": "REACHABILITY: no in-repo caller reaches this.\n"
                           "Off-by-one in the unused helper.",
            "proposed_fix": "",
        }
        assert tag_entry(entry) is True
        assert entry["latent_source"] == "explicit_field"

    @_needs_archive
    def test_which_gate_actually_held_the_exp40_pair(self):
        """ADVERSARIAL PASS, 2026-08-12. The note first written beside this fix
        said the data-loss interlock was all that kept C0020 and C0048 from
        being demoted. It was not, and getting this right decides how alarming
        the defect was. Both carry an EMPTY falsifier_verdict, so
        _is_demotion_eligible refuses at condition (2) and never reads the
        category. Two gates held them, and the one that fired first was the
        falsifier gate. Under the modern falsifier-CONFIRMED regime the category
        would be the only thing left — which is the version worth alarming
        about, and it is asserted here rather than assumed."""
        data = dict(_RUNS)["exp40_slice_records_20260518T160503Z"]
        for cid in ("C0020", "C0048"):
            entry = dict(data["registry"]["entries"][cid])
            entry["latent"] = True          # force the pre-fix (wrong) tag
            entry["finding_category"] = "data_loss"
            assert entry.get("falsifier_verdict") in (None, "", "PENDING"), (
                f"{cid} now carries a falsifier verdict — re-measure which gate "
                "holds it before repeating either claim")
            assert _is_demotion_eligible(entry) is False
            no_category = dict(entry, finding_category="")
            assert _is_demotion_eligible(no_category) is False, (
                "clearing the category made it eligible, so the interlock WAS "
                "the only thing holding it — the docstring correction is wrong")
            modern = dict(no_category, falsifier_verdict="CONFIRMED")
            assert _is_demotion_eligible(modern) is True, (
                "with a CONFIRMED falsifier and no category it must be "
                "eligible, or the hazard this fix addresses does not exist")

    def test_stripping_a_fence_cannot_manufacture_a_marker_match(self):
        """ADVERSARIAL PASS, 2026-08-12, and it found a real one. Replacing a
        fenced block with a single SPACE fused the fragments either side of it
        into a marker match the raw text never contained — every marker joins
        its words with one literal space, so one space is exactly the character
        needed to forge one. Both probes below were tagged latent by the
        space-substituting version and by nothing else: a MANUFACTURED false
        latent, in a function whose docstring claimed it could only remove them.

        Fixed by making the placeholder non-space (and non-newline: a newline
        would let a stripped fence create a line start for the MULTILINE
        explicit-field regex, which is the same defect on the designed source).
        """
        probes = (
            ("fuses_no_caller",
             "There is no in-repo```irrelevant```caller guard missing here."),
            ("fuses_shadow_path",
             "Marked observation```z```only in the header."),
            ("fuses_a_reachability_field",
             "The old header read REACH```x```ABILITY: unreachable here."),
        )
        for probe_id, description in probes:
            raw = {"description": description, "proposed_fix": ""}
            assert lt._prose_latency(description) is None, (
                f"{probe_id}: the RAW text already matches, so this probe no "
                "longer tests fusion — replace it")
            entry = dict(raw, canonical_id="C1", severity=0.85,
                         status="CONFIRMED", falsifier_verdict="CONFIRMED",
                         open_since_round=0)
            assert tag_entry(entry) is False, (
                f"{probe_id}: stripping the fence MANUFACTURED a latent tag "
                f"({entry.get('latent_evidence')}) — the placeholder is fusing "
                "again. It must not be a bare space or a newline.")

    @_needs_archive
    def test_narrowing_can_only_remove_tags_never_add_one(self):
        """The safety property of the fix, asserted rather than assumed, by
        replaying the PRE-FIX reading rule over the whole archive. Narrowing
        what is read can only reduce matches, so the post-fix latent set must be
        a subset of the pre-fix one. Measured: two removed, none added."""
        def pre_fix_latent(entry):
            text = "\n".join(str(entry.get(k) or "")
                             for k in ("description", "proposed_fix"))
            verdict = lt._explicit_field(text) or lt._prose_latency(text)
            return bool(verdict and verdict[0])

        added, removed = [], []
        for name, data in _RUNS:
            for cid, entry in data["registry"]["entries"].items():
                before = pre_fix_latent(entry)
                after = tag_entry(dict(entry))
                if after and not before:
                    added.append(f"{name}/{cid}")
                elif before and not after:
                    removed.append(f"{name}/{cid}")
        assert added == [], f"the fix ADDED latent tags — not fail-safe: {added}"
        assert sorted(removed) == [
            "exp40_slice_records_20260518T160503Z/C0020",
            "exp40_slice_records_20260518T160503Z/C0048",
        ], removed


# ── What is still wrong, recorded rather than asserted to be fine ───────────


# Each case is a GENUINELY TRIGGERABLE defect written the way a panel writes
# them. `expect_latent` / `expect_eligible` record MEASURED CURRENT BEHAVIOUR,
# not desired behaviour. Every True below is a false latent tag.
FALSE_LATENT_BATTERY = (
    # id, description, mechanism, expect_latent, expect_eligible
    ("broken_latency_guard",
     "The assertion that guaranteed no in-repo caller can reach this branch is "
     "itself broken; after the refactor every caller reaches it and the stale "
     "value is returned.",
     "the marker matches the claim the BROKEN GUARD made, not the finding's",
     True, True),
    ("docstring_contradicted",
     "The docstring claims the module is shadow/observation-only, but "
     "observe_round() writes straight into the verdict path and changes the "
     "gate's answer.",
     "the marker matches a reported claim the finding exists to contradict",
     True, True),
    ("transition_verb",
     "FIND: `detect_finding_id_collisions` can turn an observation-only "
     "collision detector into a blocking failure and can overcount.",
     "ARCHIVE-REAL (Exp 40 slice_collision C0002): the descriptor is what the "
     "defect DESTROYS. Identical to the Exp 47 C0024 referent failure that "
     "removed the 'never reached' family, unfixed for 'observation-only'.",
     True, True),
    ("explicit_negation",
     "It is not true that there is no in-repo caller: bench/x.py:41 calls it "
     "on every round.",
     "no negation awareness whatsoever",
     True, True),
    ("guard_named_not_absent",
     "The script prints FALSIFIED only if there is no in-repo caller guard "
     "present.",
     "'no in-repo caller guard' names a GUARD; the marker reads it as absence "
     "of callers",
     True, True),
    ("never_gates_is_the_defect",
     "The convergence gate never gates: the threshold comparison is inverted, "
     "so every round passes regardless of the critical count.",
     "'never gates' IS the bug; caught only by the core_functionality veto",
     True, False),
    ("not_load_bearing_is_the_defect",
     "This branch treats gamma as not load-bearing and skips it, which is the "
     "defect - gamma is load-bearing and the run converges early.",
     "'not load-bearing' IS the bug, and nothing vetoes it",
     True, True),
    ("fires_under_default_too",
     "The parser mis-orders records under the non-default config flag, and "
     "also under the default one whenever two ids collide.",
     "the finding says it fires under the default; the prose path never "
     "consults the reachable-value vocabulary the field path has",
     True, True),
    ("quotes_another_findings_field",
     "C0031 said 'REACHABILITY: no caller reaches this'. That was wrong: the "
     "path is live and this finding demonstrates the wrong result.",
     "attribution: quoting another finding's field in prose; caught only by "
     "the core_functionality veto",
     True, False),
)


class TestFalseLatentExposure:
    """CHARACTERISATION of behaviour that is WRONG and deliberately not patched.

    Every case below is a real, triggerable defect. Nine are tagged latent and
    seven reach demotion eligibility, so if the mechanism were live each would
    silently drop out of the convergence gate. The cause is one thing in nine
    disguises: the markers match a MENTION, never an ASSERTION. Patching them
    one at a time is the arms race the module already lost once; the evidence
    says the prose source should be retired the way the "never reached" family
    was. That is a design ruling and is left to the founder.

    This test fails in BOTH directions on purpose. Worse means a new false
    latent; better means somebody repaired the markers and this record — and
    the recommendation resting on it — is out of date.
    """

    @pytest.mark.parametrize(
        "case_id,description,mechanism,expect_latent,expect_eligible",
        FALSE_LATENT_BATTERY,
        ids=[c[0] for c in FALSE_LATENT_BATTERY],
    )
    def test_measured_false_latent(self, case_id, description, mechanism,
                                   expect_latent, expect_eligible):
        entry = {
            "canonical_id": "C1", "severity": 0.85, "status": "CONFIRMED",
            "falsifier_verdict": "CONFIRMED", "open_since_round": 1,
            "description": description, "proposed_fix": "",
        }
        latent = tag_entry(entry)
        eligible = _is_demotion_eligible(entry)
        assert latent is expect_latent, (
            f"{case_id}: latent tag moved. Mechanism on record: {mechanism}")
        assert eligible is expect_eligible, (
            f"{case_id}: demotion eligibility moved. On record: {mechanism}")

    def test_the_measured_totals_are_what_the_recommendation_rests_on(self):
        """One number, so a reader of the recommendation can check it in one
        place: 9 of 9 constructed triggerable findings are tagged latent and 7
        of 9 would be demoted."""
        latent = eligible = 0
        for _cid, desc, _mech, _el, _ee in FALSE_LATENT_BATTERY:
            entry = {
                "canonical_id": "C1", "severity": 0.85, "status": "CONFIRMED",
                "falsifier_verdict": "CONFIRMED", "open_since_round": 1,
                "description": desc, "proposed_fix": "",
            }
            latent += bool(tag_entry(entry))
            eligible += bool(_is_demotion_eligible(entry))
        assert (latent, eligible) == (9, 7), (latent, eligible)


# ── The gate stays shut, and cannot be opened quietly ───────────────────────


class TestNotEnabledAnywhere:
    def test_no_shipped_config_enables_either_flag(self):
        """LOUD GUARD, and the point of it. Every measurement in this file was
        taken with both flags off, which is how all 43 shipped configs stand.
        Enabling either one is a founder decision; this test exists so it cannot
        be taken by a quiet config edit while the prose source is still scoring
        9 false latents out of 9 (see TestFalseLatentExposure).

        If this goes red because the pair was enabled ON PURPOSE, that is the
        alarm working. Re-run bench/validate_latent_tagger.py and this file,
        record the decision, then update this test — do not delete it.

        THE SCANNED COUNT IS ASSERTED FIRST, and that assertion is not padding.
        Without it this guard passes green on an empty glob: rename or relocate
        bench/exp*_configs and the alarm reports "no config enables either flag"
        while scanning nothing at all. Measured on the adversarial pass — the
        same scan against a non-existent root returns 0 files and 0 offenders,
        which is this project's governing failure mode wearing the clothes of a
        pass. TestArchiveExposure already guards its corpus this way; this test
        did not, and now does."""
        paths = sorted(glob.glob(os.path.join(
            _ROOT, "bench", "exp*_configs", "*.json"))) + sorted(
            glob.glob(os.path.join(_ROOT, "bench", "exp*_config.json")))
        assert len(paths) >= 43, (
            f"only {len(paths)} shipped configs found where 43 were measured on "
            "2026-08-12. This guard cannot report on files it never opened: "
            "either the config tree moved (fix the glob) or configs were "
            "deleted (re-measure and update the floor).")
        offenders = []
        for path in paths:
            try:
                with open(path, encoding="utf-8") as fh:
                    cfg = json.load(fh)
            except Exception:
                continue
            if not isinstance(cfg, dict):
                continue
            for flag in ("latent_tagger_enabled", "severity_calibration_enabled"):
                if cfg.get(flag):
                    offenders.append(f"{os.path.relpath(path, _ROOT)}: {flag}")
        assert offenders == [], (
            "a shipped config now enables the latent tagger / severity "
            "calibration. Read this test's docstring before proceeding: "
            + str(offenders))

    def test_both_defaults_are_off(self):
        cfg = RunnerConfig(experiment_name="x", models=["CC2"])
        assert cfg.latent_tagger_enabled is False
        assert cfg.severity_calibration_enabled is False
