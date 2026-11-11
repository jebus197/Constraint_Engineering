#!/usr/bin/env python3
"""A run that names no suite gets NO suite, and the admissible basis is both texts.

★ FOUNDER RULING 2026-11-11, B88, option 1 of 4: *"Make the launcher refuse to
substitute a default suite for a target whose run named no suite at all."* He
declined option 2 (a discrimination control inside the gate, a 3rd suite run per
candidate, measured at 209 s per run on his machine) and option 3 (both), the
latter because `composability-requires-a-measurement` had none to offer.

★ AND HIS SEPARATE RULING THE SAME DAY, on which text is the admissible basis:
*"Keep both the claim prose, and the proposed fix."*

WHAT THE SUBSTITUTED DEFAULT DID. `bench/tools/run_simulated_experiment.py`
defaulted `--test-cmd` to the IMMUNE-MEMORY suite, tied to `bench/dm/_memory.py`
and unrelated to any other target. A run omitting the flag inherited it, so on a
prose target `e2_regression` RAN AND COULD NOT SEE ITS SUBJECT: the document with
real bytes and with its bytes destroyed both returned 0.9454545454545454. Already
recorded at `reference_runner_v3.py:15908`; the arm4 half was repaired on
2026-09-30 and the argparse default was not.

★ THIS GUARD IS BEHAVIOURAL ON PURPOSE. The seat's rescued falsifier
`scripts/falsify_e2_inherits_default_2026-09-30.py` establishes the same fact by
SLICING THE LAUNCHER'S SOURCE TEXT, and a parenthesised help string broke that
slice into a SyntaxError on 2026-11-11. Its header asserts byte-identity with
the seat's output so it may not be edited; this file stands beside it and
asserts the same property by BUILDING THE PARSER AND READING IT, per
`execute-do-not-grep`.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "bench" / "tools" / "run_simulated_experiment.py"
sys.path.insert(0, str(ROOT / "bench"))


def _launcher():
    spec = importlib.util.spec_from_file_location("_rse_guard", LAUNCHER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rse_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheLauncherSubstitutesNothing:
    def test_the_parser_defaults_the_suite_to_none(self):
        """★ BUILT AND READ, not grepped."""
        assert LAUNCHER.is_file(), f"{LAUNCHER} is missing"
        mod = _launcher()
        build = getattr(mod, "build_parser", None) or getattr(mod, "_parser", None)
        if build is None:
            pytest.skip("the launcher exposes no parser builder to call")
        got = build().parse_args([]).test_cmd
        assert got is None, (
            f"a run naming no suite inherits {got!r}. That is the substituted "
            f"default his B88 ruling refuses: the gate then runs against an "
            f"artefact it cannot see and reports a constant.")

    def test_no_suite_is_named_in_the_declaration_text(self):
        """A cheap second route, so the property holds even if the parser
        builder is ever renamed and the test above skips."""
        src = LAUNCHER.read_text(encoding="utf-8")
        i = src.index('ap.add_argument("--test-cmd"')
        decl = src[i:i + 600]
        for suite in ("test_immune_memory_consumption",
                      "test_immune_memory_evaluation"):
            assert suite not in decl, (
                f"the --test-cmd declaration still names {suite}, so a run "
                f"that names no suite inherits one")

    def test_the_seats_rescued_falsifier_still_parses_this_file(self):
        """★ THE SLICE THE SEAT'S EVIDENCE DEPENDS ON. Its header asserts
        byte-identity with the seat's output, so it cannot be repaired; this
        asserts the launcher stays parseable BY it instead."""
        src = LAUNCHER.read_text(encoding="utf-8")
        start = src.index('ap.add_argument("--test-cmd"')
        end = src.index("help=", start)
        end = src.index(")", src.index('"', end + 6) + 1) + 1
        snippet = src[start:end]
        import argparse
        ap = argparse.ArgumentParser()
        exec(snippet, {"ap": ap})          # noqa: S102 - the project's own decl
        assert ap.parse_args([]).test_cmd is None


class TestTheGateStillRefusesWithoutASuite:
    def test_an_absent_suite_excludes_the_gate_rather_than_faking_it(self):
        import bench.reference_runner_v3 as rr                 # noqa: PLC0415
        ok, why = rr._apply_back_gate("x", "thing.py", "", finding=None, domain="")
        assert ok is False
        assert "test_cmd" in why, why


class TestBothTextsAreTheAdmissibleBasis:
    """His 2026-11-11 ruling, asserted on the live function."""

    class _F:
        def __init__(self, d, fix=""):
            self.description = d
            self.proposed_fix = fix

    CLAIM = "the molecule 'CCO' has formula C2H6O"

    def test_claim_alone_no_longer_admits(self):
        import domain_immune as di                             # noqa: PLC0415
        r = di.domain_verification_set(
            "chemistry", self._F(self.CLAIM, "delete the retry loop"))
        assert r["admits"] is False, (
            "a true sub-claim again admits a fix the tools never examined")
        assert r["claim_admits"] is True, "the probe no longer isolates the hole"

    def test_both_verifying_still_admits(self):
        """★ ANTI-INERTIA. A refusal bought by disabling the route is not a fix."""
        import domain_immune as di                             # noqa: PLC0415
        r = di.domain_verification_set(
            "chemistry", self._F(self.CLAIM, f"correct it to: {self.CLAIM}"))
        assert r["admits"] is True, (
            f"a fix the tools DO verify is refused, so the route is inert: "
            f"{r['detail']}")

    def test_an_absent_fix_fails_closed(self):
        import domain_immune as di                             # noqa: PLC0415
        r = di.domain_verification_set("chemistry", self._F(self.CLAIM, ""))
        assert r["admits"] is False
