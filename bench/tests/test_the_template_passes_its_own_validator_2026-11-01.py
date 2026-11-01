#!/usr/bin/env python3
"""The brief TEMPLATE must pass the brief VALIDATOR. Nothing checked this.

THE DEFECT, 2026-11-01, shipped and committed earlier the same day. A
composability check was added to `CHECKS`, the REQUIRED set, while
`bench/directives/universal/panel_brief_template.md` said nothing about
composability. So the validator refused **134 of 139** archived briefs,
0.964029, Wilson 95% [0.918560, 0.984539] -- and refused the TEMPLATE itself,
which failed exactly 1 check and that check was the new one. The next panel
dispatch would have been blocked by a brief written exactly as instructed.

IT ALSO BROKE THE MODULE'S OWN STANDARD FOR ADDING A CHECK, recorded beside the
disagreement check of 2026-10-02: *"WHAT JUSTIFIES THE CHECK: THE TEMPLATE
ALREADY REQUIRED THIS ... and the template passes this check unchanged."* That
sentence is the invariant, and until now it was prose with nothing enforcing it.

WHY THE COMMIT GATE DID NOT CATCH IT. None of the 4 brief guard files is in the
hook's GUARDS list, which is 120 of 759 test files. The gate runs about 1 test
in 6, so the regression survived 3 commits.

THE REPAIR MEASURED: the positive statement is now REPORTED and not refused, the
weak form stays a refusal because it reaches only 1 of 139 briefs, and a negated
mention no longer fires it. 0 briefs are newly refused and 62 are released.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
TEMPLATE = REPO / "bench" / "directives" / "universal" / "panel_brief_template.md"


@pytest.fixture(scope="module")
def pbv():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("pbv_guard", VALIDATOR)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_guard"] = m
    spec.loader.exec_module(m)
    return m


class TestTheTemplateIsDispatchable:
    def test_the_template_passes_every_required_check(self, pbv):
        """★ THE INVARIANT. A required check the template cannot satisfy refuses
        every brief written as instructed."""
        fails = pbv.validate(TEMPLATE.read_text(encoding="utf-8"))
        assert not fails, (
            "the TEMPLATE fails its own validator, so a brief written exactly "
            "as instructed is refused:\n  " + "\n  ".join(f[:200] for f in fails))

    def test_the_template_STATES_the_composability_standard(self, pbv):
        """★ THE HOLE THIS GUARD HAD ON ITS FIRST RUN, found by mutation. Once
        the check is advisory, stripping the requirement OUT of the template no
        longer makes the template fail the validator, so the 4th mutation of
        `scripts/the_brief_template_mutations_2026-11-01.py` passed 9 of 9 and the
        thing his ruling actually asked for was unguarded. The template must not
        itself trigger the advisory."""
        out = pbv.composability_advisory(TEMPLATE.read_text(encoding="utf-8"))
        assert out == [], (
            "the TEMPLATE does not state composability as a demonstrated "
            "advantage, so an author is never prompted for it and the advisory "
            "it triggers has nothing to point at: " + "; ".join(out)[:300])

    def test_it_passes_through_the_command_too(self):
        """Executed, not only called: the command is what a dispatcher runs."""
        r = subprocess.run([sys.executable, str(VALIDATOR), "--quiet",
                            str(TEMPLATE)], capture_output=True, text=True,
                           cwd=REPO)
        assert r.returncode == 0, r.stdout + r.stderr


class TestTheArchiveIsNotRefusedWholesale:
    def test_no_single_check_refuses_almost_everything(self, pbv):
        """A check that refuses the archive teaches people to ignore the gate --
        this module's own words about the figure-coverage check. Measured as a
        BAND rather than a literal, because the archive grows."""
        briefs = sorted((REPO / "bench" / "logs").glob("*/BRIEF.md"))
        if len(briefs) < 20:
            pytest.skip(f"only {len(briefs)} briefs in this checkout")
        from collections import Counter
        by_label = Counter()
        for b in briefs:
            for f in pbv.validate(b.read_text(errors="replace")):
                by_label[f.split(":")[0][:70]] += 1
        worst = by_label.most_common(1)[0] if by_label else ("none", 0)
        share = worst[1] / len(briefs)
        assert share < 0.90, (
            f"one required check refuses {worst[1]} of {len(briefs)} archived "
            f"briefs ({share:.6f}): {worst[0]!r}. The accepted rate for a "
            f"required check is the disagreement check's 12 of 95 = 0.126316; "
            f"report it instead of refusing.")


class TestTheAdvisoryIsWiredAndCanFire:
    def test_a_brief_asking_for_a_fix_without_the_standard_is_reported(self, pbv):
        out = pbv.composability_advisory(
            "Review scripts/x.py and propose a fix with a falsifier.\n")
        assert out and "composability" in out[0].lower()

    def test_a_brief_stating_it_his_way_is_not_reported(self, pbv):
        assert pbv.composability_advisory(
            "Propose a fix. Compose only on a demonstrated advantage over each "
            "fix alone, shown by measurement.\n") == []

    def test_a_brief_asking_for_no_fix_is_not_reported(self, pbv):
        """Composability cannot arise where nothing is being repaired."""
        assert pbv.composability_advisory(
            "Summarise what the archive says about gamma.\n") == []

    def test_the_advisory_reaches_the_command(self):
        """An addition nothing calls is not an addition."""
        src = VALIDATOR.read_text(encoding="utf-8")
        assert "composability_advisory(text)" in src, (
            "composability_advisory is defined and never called from main()")
        assert "COMPOSABILITY ADVISORY" in src


class TestTheWeakFormStillRefuses:
    def test_an_affirmative_weak_statement_is_refused(self, pbv):
        fails = pbv.validate(
            "x" * 420 + "\nSay whether the repairs compose, conflict or are "
            "independent.\n")
        assert any("weak form" in f for f in fails), fails

    def test_a_negated_mention_is_not_refused(self, pbv):
        """★ THE OVER-FIRE THAT REFUSED THE TEMPLATE. A sentence saying the weak
        form is excluded does not instruct a seat to use it."""
        fails = pbv.validate(
            "x" * 420 + "\nAsking only whether the repairs compose, conflict or "
            "are independent is the weak form his definition explicitly "
            "excludes.\n")
        assert not any("weak form" in f for f in fails), fails
