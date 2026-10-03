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
        # INVERTED 2026-10-02 WHEN THE RULING LANDED. Until that day this
        # asserted the refusal REPRODUCES, because the note's whole subject was
        # a false positive that still existed. The founder ruled the gate
        # access-only, the rule was narrowed, and the false positive is gone --
        # so the property worth pinning is its ABSENCE, with the historical
        # claim kept here rather than deleted.
        assert scan_falsifier_source(C0035_SHAPE) == [], (
            "a falsifier that only NAMES the planted-fault field is refused "
            "again; the access-only ruling has regressed")
        # The fixture must still be a mention and not an access, or it has
        # stopped standing for the case it was built for.
        assert not re.search(r"""\[\s*['"]seeded_faults?['"]\s*\]"""
                             r"""|\.get\(\s*['"]seeded_faults?['"]""", C0035_SHAPE), (
            "this fixture now READS the field, so it no longer stands for the "
            "mention case")

    def test_a_genuine_read_of_the_field_is_also_refused(self):
        """ANTI-REGRESSION, and the half that must never be weakened: whatever
        happens to mention, ACCESS stays refused."""
        from bench.falsifier_verify import scan_falsifier_source
        assert scan_falsifier_source(REAL_READ), (
            "a falsifier subscripting the planted-fault field was allowed")

    def test_the_access_not_mention_discrimination_already_exists_in_the_file(self):
        """The note claims the file already draws this distinction for
        `_KEY_FIELDS`. If it does not, the recommendation loses its precedent."""
        from bench.falsifier_verify import _KEY_FIELDS, scan_falsifier_source
        # UPDATED 2026-10-02. The note argued the file ALREADY drew the
        # access-not-mention distinction for the answer-key list, and used that
        # as the precedent for extending it to the planted-fault field. The
        # extension has now been made, so `seeded_faults` IS in `_KEY_FIELDS`
        # and the precedent has become the rule. Asserting its ABSENCE would
        # now assert the fix had not landed.
        assert re.search(r"seeded_faults\?", _KEY_FIELDS), (
            "the planted-fault field left the access list, so a falsifier can "
            "read it again")
        # EXECUTED, not read: the distinction itself, in both directions.
        assert scan_falsifier_source(
            'x = {}\nprint("seeded_faults")\n') == [], "mention is refused"
        assert scan_falsifier_source(
            'k = load()\nprint(k["seeded_faults"])\n'), "ACCESS is allowed"

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


class TestTheStaleLabelIsNotRead:
    """The producer must report the LADDER's verdict, not the entry's label.

    THE ERROR THIS PREVENTS REPEATING, and it is the costliest of 2026-10-02.
    `_apply_routing` writes `falsifier_code`/`falsifier_verdict` back only on
    `result.resolved`, so when a ladder ran and did not confirm, the entry keeps
    a stale pre-routing `UNTOOLABLE` and the real verdict survives only in
    `routing_history[-1]["verdict"]`. The runner states this in
    `reconcile_routing_verdict`'s own docstring, and records the same trap
    firing on `commissioning_arm4_prose_20260922T053349Z`.

    The producer bound `h` to that history, read `rungs_tried` out of it, and
    printed the ENTRY's `falsifier_verdict` one key away. C0029 therefore read
    "UNTOOLABLE, no falsifier was written at all" when a falsifier HAD been
    written and the guard had REFUSED it -- and on the strength of that a TRUE
    claim (2 of 3 queued criticals integrity-refused) was withdrawn in favour
    of a false one, in a document asking the founder to rule on that guard.

    A prefix scan is also not evidence: 183 of 221 retained routing bodies sit
    at the 600-character cap, so `scan_falsifier_source` over retained text
    reads a prefix. C0029's scan comes back clean and its recorded verdict is
    INTEGRITY_VIOLATION.
    """

    def _producer_stdout(self):
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-1500:]
        return r.stdout

    def test_the_ladder_verdict_is_reported_for_C0029(self):
        out = self._producer_stdout()
        line = [l for l in out.splitlines() if "C0029" in l]
        assert line, f"C0029 is not reported at all: {out[-800:]}"
        line = line[0]
        assert "ladder_verdict=INTEGRITY_VIOLATION" in line, (
            f"the producer is reporting the stale entry label again, which is "
            f"how a true claim came to be withdrawn: {line}")

    def test_the_stale_entry_label_is_marked_as_stale(self):
        """Printing it is fine. Printing it UNLABELLED is what misled."""
        out = self._producer_stdout()
        line = [l for l in out.splitlines() if "C0029" in l][0]
        assert "stale unless resolved" in line, line

    def test_a_prefix_scan_states_how_much_it_scanned(self):
        """A clean scan over a truncated body must not read as a clean body."""
        out = self._producer_stdout()
        line = [l for l in out.splitlines() if "C0029" in l][0]
        assert "retained chars" in line, (
            f"the scan does not say how many characters it saw, so a clean "
            f"result over a 600-char prefix reads as a clean body: {line}")

    def test_the_recorded_verdicts_outnumber_what_scanning_detects(self):
        """THE MEASUREMENT THE CORRECTED RATE RESTS ON. If these ever agree,
        either the truncation was lifted or the archive changed; recheck the
        3-of-221 figure before citing it."""
        import json
        from bench.falsifier_verify import scan_falsifier_source
        logs = REPO / "bench" / "logs"
        seen, recorded, detected, n = set(), 0, 0, 0
        for r in sorted(logs.rglob("*_report.json")):
            try:
                d = json.loads(r.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            for _cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
                a = ((e or {}).get("falsifier_code") or "").strip()
                if a:
                    seen.add(a)
        for r in sorted(logs.rglob("*_report.json")):
            try:
                d = json.loads(r.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            for _cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
                for h in ((e or {}).get("routing_history") or []):
                    b = (h.get("last_falsifier_code") or "").strip()
                    if b and b not in seen:
                        n += 1
                        if h.get("verdict") == "INTEGRITY_VIOLATION":
                            recorded += 1
                        if scan_falsifier_source(b):
                            detected += 1
        assert recorded > detected, (
            f"recorded integrity refusals ({recorded}) no longer exceed what "
            f"scanning the retained text detects ({detected}) over {n} bodies; "
            f"the 3-of-221 figure in the note needs re-measuring")


class TestTheWitness:

    def test_a_routed_falsifier_body_is_invisible_to_the_sweep(self):
        """WITNESS TEST. Asserts the DEFECT the founder named still exists.

        HIS RECOMMENDATION, 2026-10-02: make the false-positive sweep able to
        see refusals BEFORE touching any rule. The rule was changed that day and
        this was not done, so the sweep's quoted false-positive rate is still
        computed over a population that structurally excludes the bodies in
        question.

        REWRITTEN THE SAME DAY, BECAUSE THE ORIGINAL LOOKED IN THE WRONG PLACE
        and so reported 0. `last_falsifier_code` is not a field on the entry; it
        is written inside each `routing_history` record
        (`bench/reference_runner_v3.py`, the `routing_history.append`). Reading
        it off the entry finds nothing and reads as "the defect is gone".

        MEASURED at the correct path: 221 routing-history records carry a
        falsifier body, 23 of them belong to entries with no `falsifier_code` at
        all -- 10.4072%, Wilson [7.0355%, 15.1319%] -- and 183 are truncated at
        the 600-character cap. GOING RED HERE IS THE GOOD OUTCOME: it means the
        writeback was repaired. On a red result, update
        `experimental_notes/Integrity_Guard_False_Positive_2026-10-02.md`
        rather than this file.
        """
        import json
        logs = REPO / "bench" / "logs"
        carried, invisible, truncated = 0, 0, 0
        for report in sorted(logs.rglob("*_report.json")):
            try:
                data = json.loads(report.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            for _cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
                e = e or {}
                attached = (e.get("falsifier_code") or "").strip()
                for h in (e.get("routing_history") or []):
                    body = (h.get("last_falsifier_code") or "").strip()
                    if not body:
                        continue
                    carried += 1
                    if not attached:
                        invisible += 1
                    if len(body) >= 600:
                        truncated += 1
        assert carried > 0, (
            "no routing_history record carries a falsifier body at all, so this "
            "witness is measuring nothing -- check the accessor before reading "
            "the result as good news")
        assert invisible > 0, (
            f"no routed falsifier body is invisible to the sweep any more "
            f"({carried} carried, {truncated} truncated). If the writeback was "
            f"repaired, this is the intended outcome: update the note, which "
            f"currently tells the founder the sweep cannot see refusals.")
        assert truncated > 0, (
            "no body is truncated any more; the 600-character cap the note "
            "describes has gone, so the note is stale in that respect too")

