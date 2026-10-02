"""The 2026-10-02 integrity-guard note's claims, as executing properties.

WHY THIS FILE EXISTS. `experimental_notes/Integrity_Guard_False_Positive_2026-10-02.md`
asks the founder to rule on a security guard. Its figures come from
`scripts/guard_false_positive_blind_spot_2026-10-02.py`, and until this file
existed that script was an addition nothing executed -- the exact shape the
additive standard forbids in its symmetric form.

WHAT IS ASSERTED, AND WHAT DELIBERATELY IS NOT. The note's counts drift as the
archive grows: `2 of 872` becomes something else the next time a run lands, and
a test pinning it would join the 8 recorded instances of the stale-count class.
So the drifting counts are NOT pinned here. What is pinned is the STRUCTURE the
note's argument rests on, each of which holds or fails independently of how
many runs exist.

`test_a_refused_body_is_invisible_to_the_sweep` IS A WITNESS TEST. It asserts a
DEFECT currently exists. When the writeback is repaired so the false-positive
sweep can see refusals -- which is precisely what the note recommends -- this
test goes RED, and that is the signal to update the note rather than a
regression. The same shape as
`test_stated_gate_count_matches_measurement_2026-09-07`, whose docstring says a
failure means the prose is stale.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PRODUCER = REPO / "scripts" / "guard_false_positive_blind_spot_2026-10-02.py"
GUARD = REPO / "bench" / "falsifier_verify.py"
SPEC = REPO / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"

pytestmark = pytest.mark.skipif(not PRODUCER.is_file(), reason="producer absent")

# The real body from run 1b C0035, trimmed to the construct that was refused:
# a set literal of expected element-level keys, derived from the source rather
# than asserted. It reads nothing.
C0035_SHAPE = (
    'FALLBACK = {"task_id", "domain", "prompt", "seeded_faults", "control",\n'
    '            "response", "experimental", "passes", "final_response"}\n'
    'required = set()\n'
)
# What the guard is FOR: actually reading the planted-fault ground truth.
REAL_READ = 'faults = task["seeded_faults"]\nprint(faults)\n'


class TestTheProducerRuns:

    def test_the_producer_exits_clean(self):
        """A note whose producer does not run is a note with no evidence."""
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-2000:]
        for heading in ("THE GUARD'S FALSE-POSITIVE RATE",
                        "MENTION VERSUS ACCESS",
                        "HAS THE GUARD EVER FIRED IN A LIVE RUN"):
            assert heading in r.stdout, f"{heading!r} missing: {r.stdout[-800:]}"

    def test_every_proportion_it_prints_carries_an_interval(self):
        """`sy`: a proportion without a confidence interval is not a result."""
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, timeout=900)
        pcts = [ln for ln in r.stdout.splitlines() if re.search(r"= \d+\.\d{4}%", ln)]
        assert pcts, "the producer printed no proportions at all"
        lines = r.stdout.splitlines()
        for i, ln in enumerate(lines):
            if re.search(r"= \d+\.\d{4}%", ln):
                window = "\n".join(lines[i + 1:i + 3])
                assert "Wilson" in window and "Clopper-Pearson" in window, (
                    f"a proportion printed with no interval beneath it: {ln}")

    def test_the_two_wilson_tools_agree_on_every_proportion(self):
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, timeout=900)
        agreements = re.findall(r"statsmodels==mpmath: (True|False)", r.stdout)
        assert agreements, "no cross-tool agreement was reported"
        assert set(agreements) == {"True"}, (
            f"statsmodels and mpmath disagree on a Wilson interval: {agreements}")


    def test_the_census_excludes_the_documents_written_about_the_token(self):
        """THE MEASURING DOCUMENT MUST NOT BE INSIDE THE MEASURED POPULATION.

        The note counts occurrences of `seeded_faults`. The note, its producer
        and this very file all discuss `seeded_faults`, so including them made
        the figure rise every time the analysis was revised -- measured, from
        111 to 127 occurrences on committing the first draft.

        This test went in because mutation M5 proved the exclusion was
        UNGUARDED: removing it, verified applied by reading the file back,
        failed 0 of 9 tests. An exclusion nothing can detect the loss of is an
        addition nothing reaches.
        """
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-1500:]
        all_m = re.search(r"plural occurrences, ALL tracked files: (\d+) across (\d+)", r.stdout)
        pop_m = re.search(r"plural occurrences, POPULATION \(those 3 excluded\): (\d+) across (\d+)", r.stdout)
        assert all_m, f"the all-files census line is gone: {r.stdout[-600:]}"
        assert pop_m, f"the population census line is gone: {r.stdout[-600:]}"
        all_occ, pop_occ = int(all_m.group(1)), int(pop_m.group(1))
        assert pop_occ < all_occ, (
            f"the population census ({pop_occ}) does not exclude the artefacts "
            f"written about the token ({all_occ} with them): the exclusion has "
            f"been removed, so publishing the analysis inflates the figure the "
            f"analysis reports")
        assert int(pop_m.group(2)) < int(all_m.group(2)), (
            "the population file count does not exclude the 3 artefacts")


class TestTheNotesStructuralClaims:

    def test_the_guard_refuses_the_field_on_MERE_MENTION(self):
        """The false positive itself. Naming a schema key is not reading it."""
        from bench.falsifier_verify import scan_falsifier_source
        hits = scan_falsifier_source(C0035_SHAPE)
        assert hits, "the refusal the note is about no longer reproduces"
        assert any(t == "seeded_fault" for _rule, t in hits), hits
        assert not re.search(r"""\[\s*['"]seeded_faults?['"]\s*\]"""
                             r"""|\.get\(\s*['"]seeded_faults?['"]""", C0035_SHAPE), (
            "this fixture actually reads the field, so it is not a false positive")

    def test_a_genuine_read_of_the_field_is_also_refused(self):
        """ANTI-REGRESSION, and the half that must never be weakened: whatever
        happens to mention, ACCESS stays refused."""
        from bench.falsifier_verify import scan_falsifier_source
        assert scan_falsifier_source(REAL_READ), (
            "a falsifier subscripting the planted-fault field was allowed")

    def test_the_access_not_mention_discrimination_already_exists_in_the_file(self):
        """The note claims the file already draws this distinction for
        `_KEY_FIELDS`. If it does not, the recommendation loses its precedent."""
        src = GUARD.read_text(encoding="utf-8")
        assert "a key-internal field subscripted" in src, src[:0]
        assert "a key-internal field fetched via .get()" in src
        from bench.falsifier_verify import _KEY_FIELDS
        assert "seeded_fault" not in _KEY_FIELDS, (
            "seeded_faults is now in _KEY_FIELDS, so the note's account of "
            "which rule fires is stale")

    def test_the_guard_has_no_simulated_versus_live_branch(self):
        """The note tells the founder this would fire identically in a paid
        run. That rests on there being no sim/live distinction here."""
        src = GUARD.read_text(encoding="utf-8")
        assert not re.search(r"simulat|sim_mode|is_sim", src, re.I), (
            "a sim/live branch has appeared in the guard; the note's answer to "
            "'would it trigger in a real experiment' is no longer sound")

    def test_the_token_does_not_come_from_the_target_document(self):
        """The note's case against renaming rests on this being 0."""
        if not SPEC.is_file():
            pytest.skip("the target spec is not in this tree")
        assert SPEC.read_text(encoding="utf-8", errors="ignore").count(
            "seeded_fault") == 0, (
            "the target spec now names the token, so the note's claim that it "
            "enters through bench/evaluate.py is stale")


class TestTheWitness:

    def test_a_refused_body_is_invisible_to_the_sweep(self):
        """WITNESS TEST. Asserts the DEFECT exists.

        GOING RED HERE IS THE GOOD OUTCOME: it means the writeback was repaired
        so the false-positive sweep can see refusals, which is exactly what the
        note recommends. On a red result, update
        `experimental_notes/Integrity_Guard_False_Positive_2026-10-02.md`
        rather than this file.
        """
        import json
        from bench.falsifier_verify import scan_falsifier_source
        logs = REPO / "bench" / "logs"
        seen, unseen_refused = set(), 0
        for report in sorted(logs.rglob("*_report.json")):
            try:
                data = json.loads(report.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            for _cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
                e = e or {}
                a = (e.get("falsifier_code") or "").strip()
                if a:
                    seen.add(a)
        for report in sorted(logs.rglob("*_report.json")):
            try:
                data = json.loads(report.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            for _cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
                for h in ((e or {}).get("routing_history") or []):
                    b = (h.get("last_falsifier_code") or "").strip()
                    if b and b not in seen and scan_falsifier_source(b):
                        unseen_refused += 1
        assert unseen_refused > 0, (
            "no refused falsifier body is invisible to the sweep any more. If "
            "the writeback was repaired, this is the intended outcome: update "
            "the note, which currently tells the founder the sweep cannot see "
            "refusals."
        )
