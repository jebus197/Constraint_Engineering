# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0438d562112dc713d022fab4619601508adb099821114466f90a7d13706adc46
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The rule-amendments register, executed -- and the 3 ways it must FAIL.

WHAT THIS GUARDS. A rule change retroactively invalidated an ARCHIVED declared
figure. `bench/logs/panel_round11_2026-09-11/BRIEF.md` declares
`real-rejection rate : 2/640 = 0.3125%`. The founder's ruling of 2026-10-02
narrowed `bench/falsifier_verify.py`'s pre-execution key gate to ACCESS-ONLY,
and as of the brief's own date the producer now prints 1/640: the corpus is
pinned by `--as-of` and is byte-identical, the NUMERATOR moved. `--as-of`
pins a denominator; it cannot absorb a rule change. `bench/rule_amendments.json`
records the amendment and `bench/rule_amendments.py` rebuilds the superseded
predicate from rule tuples still committed in the amended module, so `--as-of`
now pins the RULE SET too.

THE 3 RED ARMS, which is the point of the file. A register is a licence to say
"the rules were different then", so it is a gate that could be worse than no
gate at all. These tests require it to FAIL when:

  (a) BYPASSED -- the producer run with `--rules current` reproduces the defect
      (1/640 where the brief says 2/640), so the register is load-bearing and
      not decoration;
  (b) EMPTIED -- an empty or absent `amendments` list makes the register
      UNLOADABLE rather than permissive, the producer exits non-zero, and the
      validator therefore REFUSES the archived brief;
  (c) USED TO LAUNDER AN EDIT -- an amendment that moves a figure without
      recording the superseded value, or that records a replacement value the
      code does not produce, is refused. This is the arm that matters: a
      register which could change a number without accounting for the change
      would be a hole with a filing cabinet in front of it.

EXECUTE, DO NOT GREP. Every case below runs the producer, the validator or the
register's own verifier. None asserts on source text.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REGISTER = ROOT / "bench" / "rule_amendments.json"
PRODUCER = ROOT / "scripts" / "archived_falsifier_rejections_2026-09-10.py"
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"
BRIEF = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"

DECLARED = "real-rejection rate : 2/640 = 0.3125%"
AS_OF = "2026-09-11"


@pytest.fixture(scope="module")
def pbv():
    spec = importlib.util.spec_from_file_location("pbv_amend", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_amend"] = m
    spec.loader.exec_module(m)
    return m


def run_producer(*args, cwd=ROOT):
    return subprocess.run([sys.executable, str(PRODUCER), *args],
                          cwd=cwd, capture_output=True, text=True, timeout=1800)


class _SwappedRegister:
    """Replace the committed register for the duration of a block, restore it
    unconditionally. The register is a COMMITTED file consulted by a
    subprocess, so a monkeypatch of an in-process object would not reach the
    code under test."""

    def __init__(self, doc):
        self.doc = doc
        self.backup = None

    def __enter__(self):
        self.backup = REGISTER.read_bytes()
        if self.doc is None:
            REGISTER.unlink()
        else:
            REGISTER.write_text(json.dumps(self.doc, indent=2) + "\n",
                                encoding="utf-8")
        return self

    def __exit__(self, *exc):
        REGISTER.write_bytes(self.backup)
        return False


def _committed_doc():
    return json.loads(REGISTER.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# GREEN: the register is reached, and it makes the archived figure decidable.
# --------------------------------------------------------------------------
class TestTheRegisterIsReachedAndWorks:
    def test_the_register_loads_and_names_the_amendment(self):
        from bench.rule_amendments import load_register
        ids = [a["id"] for a in load_register()]
        assert "RA-2026-10-02-falsifier-gate-access-only" in ids, ids

    def test_the_producer_consults_it_and_says_so(self):
        """REACHED BY A CALLER, not merely present. The producer's own output
        must name the rule set it pinned -- a silent historical rule set is how
        an exemption rots into a hole."""
        r = run_producer("--as-of", AS_OF)
        assert r.returncode == 0, (r.stdout + r.stderr)[-800:]
        assert "RA-2026-10-02-falsifier-gate-access-only" in r.stdout, r.stdout[:900]
        assert DECLARED in r.stdout, r.stdout[-900:]

    def test_the_register_verifies_by_executing_both_predicates(self):
        """The recorded values are MEASURED against the code, both of them."""
        from bench.rule_amendments import verify_register
        assert verify_register() == []

    def test_the_live_gate_is_untouched(self):
        """The amendment register must not have re-widened the live gate. The
        unrestricted run is the production measurement and it stays on the
        access-only rules."""
        r = run_producer()
        assert r.returncode == 0, r.stderr[-600:]
        assert "rule set" not in r.stdout, (
            "the register leaked into the undated production path:\n" + r.stdout[:600])
        assert DECLARED not in r.stdout, r.stdout[-600:]

    def test_the_archived_brief_is_accepted_and_not_edited(self):
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        assert DECLARED in BRIEF.read_text(), (
            "the archived brief was EDITED, which falsifies the record of what "
            "the seats were given")
        r = subprocess.run([sys.executable, str(VALIDATE), str(BRIEF)],
                           cwd=ROOT, capture_output=True, text=True, timeout=1800)
        assert r.returncode == 0, (r.stdout + r.stderr)[-900:]
        assert "HISTORICAL FIGURE" in (r.stdout + r.stderr)


# --------------------------------------------------------------------------
# RED ARM (a): bypassed.
# --------------------------------------------------------------------------
class TestBypassingItReproducesTheDefect:
    def test_rules_current_still_prints_the_post_amendment_figure(self):
        """If this ever printed 2/640 the register would be decoration: the
        figure would reproduce without it and nothing here is load-bearing."""
        r = run_producer("--as-of", AS_OF, "--rules", "current")
        assert r.returncode == 0, (r.stdout + r.stderr)[-800:]
        assert "real-rejection rate : 1/640 = 0.1562%" in r.stdout, r.stdout[-900:]
        assert DECLARED not in r.stdout, (
            "the archived figure reproduces WITHOUT the register, so the "
            "register is not what makes it reproduce")

    def test_the_two_rule_sets_differ_on_exactly_one_finding(self):
        """The register names which finding changed class. Executed, not read:
        the superseded predicate and the live one are run over the same corpus
        and their real-rejection sets are compared."""
        import calendar
        import time

        from bench.rule_amendments import load_register
        spec = importlib.util.spec_from_file_location("prod_amend", PRODUCER)
        prod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prod)
        epoch = calendar.timegm(time.strptime(AS_OF, "%Y-%m-%d")) + 86399
        _, old_real, _ = prod.survey(epoch, AS_OF)
        _, new_real, _ = prod.survey(epoch, None)
        old_pairs = {tuple(where[0]) for where, _v in old_real.values()}
        new_pairs = {tuple(where[0]) for where, _v in new_real.values()}
        assert old_pairs, "the superseded predicate found no rejection at all"
        moved = old_pairs - new_pairs
        declared = set()
        for a in load_register():
            for f in a["affected_figures"]:
                for ref in f.get("reclassified") or []:
                    declared.add(tuple(ref.split("/", 1)))
        assert moved == declared, (
            f"the findings that changed class are {sorted(moved)} but the "
            f"register declares {sorted(declared)}")


# --------------------------------------------------------------------------
# RED ARM (b): emptied or removed.
# --------------------------------------------------------------------------
class TestAnEmptiedRegisterRefusesRatherThanPermits:
    def test_an_empty_amendments_list_is_unloadable(self):
        from bench.rule_amendments import RegisterError, load_register
        doc = _committed_doc()
        doc["amendments"] = []
        with _SwappedRegister(doc):
            with pytest.raises(RegisterError):
                load_register()

    def test_an_emptied_register_makes_the_producer_exit_nonzero(self):
        doc = _committed_doc()
        doc["amendments"] = []
        with _SwappedRegister(doc):
            r = run_producer("--as-of", AS_OF)
        assert r.returncode != 0, (
            "an emptied register let the dated run succeed, so emptying it is "
            "a silent bypass:\n" + r.stdout[-600:])

    def test_an_emptied_register_refuses_the_archived_brief(self, pbv):
        """FAIL CLOSED, end to end. With the register emptied the historical
        reproduction cannot run, so the brief is REFUSED -- it is not accepted
        under today's rules and it is not exempted."""
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        doc = _committed_doc()
        doc["amendments"] = []
        with _SwappedRegister(doc):
            problems = pbv.check_declared_figures(BRIEF.read_text(),
                                                  brief_path=BRIEF)
        assert any("2/640" in p and "does not print it" in p for p in problems), (
            f"with the register emptied the archived figure was still accepted: "
            f"{problems}")

    def test_a_deleted_register_also_refuses(self, pbv):
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        with _SwappedRegister(None):
            assert not REGISTER.exists()
            problems = pbv.check_declared_figures(BRIEF.read_text(),
                                                  brief_path=BRIEF)
        assert any("2/640" in p and "does not print it" in p for p in problems), (
            f"with the register deleted the archived figure was still accepted: "
            f"{problems}")
        assert REGISTER.is_file()   # restored


# --------------------------------------------------------------------------
# RED ARM (c): the register cannot launder an edit. THE LOAD-BEARING ARM.
# --------------------------------------------------------------------------
class TestItCannotLaunderAnEdit:
    def test_an_amendment_without_the_superseded_value_is_refused(self):
        """A record that changes a figure and does NOT say what the figure was
        is the laundering shape. It must make the register unloadable."""
        from bench.rule_amendments import RegisterError, load_register
        doc = _committed_doc()
        del doc["amendments"][0]["affected_figures"][0]["superseded_value"]
        with _SwappedRegister(doc):
            with pytest.raises(RegisterError) as exc:
                load_register()
        assert "superseded_value" in str(exc.value)

    def test_an_amendment_without_the_replacement_value_is_refused(self):
        from bench.rule_amendments import RegisterError, load_register
        doc = _committed_doc()
        doc["amendments"][0]["affected_figures"][0]["replacement_value"] = ""
        with _SwappedRegister(doc):
            with pytest.raises(RegisterError) as exc:
                load_register()
        assert "replacement_value" in str(exc.value)

    def test_a_laundering_record_refuses_the_brief_rather_than_passing_it(self, pbv):
        """END TO END, and this is the arm that decides whether the register is
        safe. Someone drops the superseded value to avoid recording what the
        amendment moved. The brief is then REFUSED -- stripping the account does
        not buy the acceptance, it loses it."""
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        doc = _committed_doc()
        del doc["amendments"][0]["affected_figures"][0]["superseded_value"]
        with _SwappedRegister(doc):
            problems = pbv.check_declared_figures(BRIEF.read_text(),
                                                  brief_path=BRIEF)
        assert any("2/640" in p and "does not print it" in p for p in problems), (
            f"an amendment that recorded no superseded value still bought a "
            f"historical acceptance: {problems}")

    def test_a_wrong_replacement_value_fails_verification(self):
        """Schema completeness is not enough: the recorded replacement must be
        what the CURRENT code actually prints. Here the record claims the
        amendment moved the figure to 3/640; execution says 1/640. (A record
        claiming it did not move at all is refused 1 step earlier, by
        `test_identical_values_are_refused`.)"""
        from bench.rule_amendments import verify_register
        doc = _committed_doc()
        doc["amendments"][0]["affected_figures"][0]["replacement_value"] = (
            "real-rejection rate : 3/640 = 0.4688%")
        with _SwappedRegister(doc):
            problems = verify_register()
        assert any("replacement" in p for p in problems), problems

    def test_a_wrong_superseded_value_fails_verification(self):
        """The other direction: a record may not invent the figure the old rule
        produced, which is how an amendment would legitimise a number no rule
        set ever yielded."""
        from bench.rule_amendments import verify_register
        doc = _committed_doc()
        doc["amendments"][0]["affected_figures"][0]["superseded_value"] = (
            "real-rejection rate : 7/640 = 1.0938%")
        with _SwappedRegister(doc):
            problems = verify_register()
        assert any("superseded value" in p for p in problems), problems

    def test_identical_values_are_refused(self):
        """A figure listed as affected whose 2 values agree was not moved by the
        amendment, so listing it would buy old-rule treatment for free."""
        from bench.rule_amendments import RegisterError, load_register
        doc = _committed_doc()
        doc["amendments"][0]["affected_figures"][0]["replacement_value"] = DECLARED
        with _SwappedRegister(doc):
            with pytest.raises(RegisterError) as exc:
                load_register()
        assert "identical" in str(exc.value)

    def test_an_amendment_cannot_reach_forward_over_its_own_date(self):
        """A figure dated ON OR AFTER the amendment was produced under the new
        rule. Allowing it would let an amendment cover any figure at all."""
        from bench.rule_amendments import RegisterError, load_register
        doc = _committed_doc()
        doc["amendments"][0]["affected_figures"][0]["as_of"] = "2026-10-02"
        with _SwappedRegister(doc):
            with pytest.raises(RegisterError) as exc:
                load_register()
        assert "BEFORE the amendment date" in str(exc.value)

    def test_an_unrebuildable_old_predicate_raises(self):
        """The superseded predicate is rebuilt from rule tuples still committed
        in the amended module. If the register names one that is gone it is
        STALE, and a stale register must stop the re-execution rather than skip
        the restoration and pass under today's rules."""
        from bench.rule_amendments import RegisterError, restored_rules
        doc = _committed_doc()
        doc["amendments"][0]["old_predicate"]["restored_rule_tuples"] = [
            "_RULES_THAT_NEVER_EXISTED"]
        with _SwappedRegister(doc):
            with pytest.raises(RegisterError) as exc:
                restored_rules(AS_OF)
        assert "_RULES_THAT_NEVER_EXISTED" in str(exc.value)

    def test_the_archived_brief_is_never_written_by_this_test(self):
        """The prohibition, asserted at the end of the run: the record was not
        edited by anything above."""
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        assert DECLARED in BRIEF.read_text()


class TestAFigureFalseAtEveryDateIsStillRefused:
    def test_a_wrong_figure_is_refused_under_the_restored_rules_too(self, pbv):
        """The register restores a PREDICATE, it does not grant an exemption. A
        figure that was never true fails as-of its date under the old rules as
        well."""
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        text = BRIEF.read_text().replace(
            DECLARED, "real-rejection rate : 4/640 = 0.6250%")
        problems = pbv.check_declared_figures(text, brief_path=BRIEF)
        assert any("4/640" in p and "does not print it" in p for p in problems), (
            f"a figure false under EVERY rule set passed: {problems}")


class TestTheSwapFixtureItself:
    def test_the_swap_restores_the_register_byte_for_byte(self):
        """A control on this file's own instrument. If the swap leaked, every
        red arm above would be measuring a mutated tree."""
        before = REGISTER.read_bytes()
        with _SwappedRegister({"schema": "wrong"}):
            assert REGISTER.read_bytes() != before
        assert REGISTER.read_bytes() == before


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
