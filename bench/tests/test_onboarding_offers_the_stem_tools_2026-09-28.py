"""Onboarding must LIST the STEM tools with explanations and OFFER to install them.

FOUNDER'S RULE, 2026-09-28, verbatim: *"no user should be compelled to use Wolfram
before they can run an experiment, but ... anyone running the project should be
offered the opportunity to install it via onboarding.md ... And where available to
whatever orchestrator model they might load it with, that model should adopt the
rule to use this configuration whenever available, or default to other tools such as
SymPy – and the other STEM Open Source tools ... which should also be made available
to them to install by running onboarding.md. A long time ago we agreed that
onboarding.md should automate this process for them as much as possible, by showing
them a list of tools with brief explanations of their functions and offering to
install them for the user if they agreed. Make sure this was done."*

IT HAD BEEN DONE. Verified 2026-09-28: `STEM_PACKAGES` carries a gloss per tool,
`check_packages` collects the missing ones and `install_packages` offers them, and
`ask("Install the Wolfram Engine via Homebrew?")` offers Wolfram. **Nothing in the
suite asserted any of it**, so the requirement was met by accident of no one having
broken it yet. Disabling the STEM offer with `if False:` changed no test result.

WHAT IS GUARDED, and it is REACHABILITY rather than wording: that the list exists
with a non-empty explanation per tool, that the missing-package path reaches
`install_packages`, that Wolfram is OFFERED rather than required, and that Wolfram is
stated as the SECOND falsifier. The exact prose is free to change.

Asserting on source structure here is deliberate and is NOT the `execute-do-not-grep`
failure: the thing under test is an INTERACTIVE installer whose offer cannot be
executed without prompting a human and mutating their machine. The AST is therefore
the strongest available evidence, and the limit is stated rather than implied.
"""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ONBOARD = ROOT / "scripts" / "cdsfl_onboard.py"

#: The founder named these as the open-source route an orchestrator defaults to.
#: THEY LIVE IN 2 GROUPS, and the first version of this test wrongly looked in 1.
#: `scipy, numpy, sympy, statsmodels` are CORE (the runner imports them directly);
#: `z3, mpmath, pint` and the domain tools are STEM. Both groups reach
#: `install_packages`, so the offer covers all of them -- the split is about what
#: the project cannot run WITHOUT, not about what is offered.
REQUIRED = {"sympy", "z3", "scipy", "numpy", "mpmath", "statsmodels", "pint"}


def _offered(mod):
    """Every package onboarding lists across the groups it offers to install."""
    groups = [mod.CORE_PACKAGES, mod.CODE_QUALITY_PACKAGES, mod.STEM_PACKAGES]
    return [t for g in groups for t in g]


@pytest.fixture(scope="module")
def mod():
    assert ONBOARD.is_file(), f"missing {ONBOARD}"
    sys.path.insert(0, str(ROOT / "bench"))
    spec = importlib.util.spec_from_file_location("cdsfl_onboard_ut", ONBOARD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_onboard_ut"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def tree():
    return ast.parse(ONBOARD.read_text(encoding="utf-8"))


class TestTheToolsAreListedWithExplanations:
    def test_every_required_stem_tool_is_present(self, mod):
        names = {t[0].lower() for t in _offered(mod)}
        missing = REQUIRED - names
        assert not missing, f"onboarding does not offer: {sorted(missing)}"

    def test_every_entry_carries_an_explanation_that_adds_something(self, mod):
        """A bare package name is a list, not an offer a person can judge.

        THE ASSERTION IS SEMANTIC, NOT A LENGTH. A first version required more than 8
        characters and failed on `("matplotlib", "matplotlib", "Plotting")` -- a
        perfectly good gloss. An arbitrary threshold does not measure whether a person
        can judge the offer; it measures typing. What actually matters is that the
        explanation is present and says something the package NAME does not.
        """
        for entry in _offered(mod):
            assert len(entry) >= 3, f"{entry[0]} has no explanation field"
            expl = entry[2].strip()
            assert expl, f"{entry[0]}'s explanation is empty"
            assert expl.lower() != entry[0].lower(), (
                f"{entry[0]}'s explanation merely repeats its name"
            )
            assert expl.lower() != entry[1].lower(), (
                f"{entry[0]}'s explanation merely repeats its pip name"
            )


class TestTheOfferIsActuallyReachable:
    @pytest.mark.parametrize("var", ["missing_core", "missing_stem"])
    def test_each_missing_path_reaches_install_packages(self, tree, var):
        """THE MUTATION THAT CHANGED NO TEST RESULT: `if False:` around this call.

        Both groups are checked because the founder's tools are split across them;
        breaking either would silently drop half the offer.
        """
        found = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            if isinstance(node.test, ast.Name) and node.test.id == var:
                for inner in ast.walk(node):
                    if (isinstance(inner, ast.Call)
                            and getattr(inner.func, "id", "") == "install_packages"):
                        found = True
        assert found, (
            f"no `if {var}:` branch reaches install_packages(); that half of the "
            "offer is unreachable and onboarding would silently skip it"
        )

    def test_no_dead_constant_guard_sits_in_the_install_flow(self, tree):
        dead = [n for n in ast.walk(tree)
                if isinstance(n, ast.If) and isinstance(n.test, ast.Constant)
                and n.test.value is False]
        assert not dead, f"{len(dead)} `if False:` guard(s) in onboarding"

    def test_check_packages_is_called_on_the_stem_list(self, tree):
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and getattr(n.func, "id", "") == "check_packages"
                 and any(getattr(a, "id", "") in ("STEM_PACKAGES", "CORE_PACKAGES")
                         for a in n.args)]
        assert len(calls) >= 2, (
            "check_packages() is not called on both CORE_PACKAGES and STEM_PACKAGES"
        )


class TestWolframIsOfferedAndNeverRequired:
    def test_wolfram_is_offered_not_installed_silently(self):
        src = ONBOARD.read_text(encoding="utf-8")
        assert 'ask("Install the Wolfram Engine' in src, (
            "onboarding no longer OFFERS the Wolfram Engine; the founder's rule is "
            "that it is offered, never compelled"
        )

    def test_the_second_falsifier_policy_is_stated_to_the_operator(self):
        src = ONBOARD.read_text(encoding="utf-8")
        assert "SECOND falsifier" in src and "never required" in src, (
            "onboarding no longer tells the operator that Wolfram is the second "
            "falsifier and is never required"
        )


class TestTheScriptStillRuns:
    def test_dry_run_exits_zero(self):
        """ANTI-VACUITY: the structural assertions above would all pass on a file
        that crashes on import."""
        r = subprocess.run([sys.executable, str(ONBOARD), "--dry-run"],
                           cwd=ROOT, capture_output=True, text=True, timeout=180)
        assert r.returncode == 0, r.stdout[-400:] + r.stderr[-400:]
