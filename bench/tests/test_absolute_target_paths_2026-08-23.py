"""Models are given the FULL path to their target, never a relative fragment.

FOUNDER RULING, 2026-08-23: "Models should never be fed just relative names. They
should always be fed the full direct path and file name to the target under
consideration... Leave nothing open to the models for either interpretation, or
potential hallucination."

WHAT WENT WRONG WITHOUT THIS. Every falsifier runs in the sandbox's throwaway
working directory, which is empty by design so a falsifier cannot write into the
real tree. A falsifier told to open its target by a repo-relative name therefore
resolved against an empty folder and died on FileNotFoundError; the gate recorded
ERROR and routed the finding away. A DETACHED falsifier -- one that opens nothing
and restates the document's numbers from memory -- does not care where it runs, so
it executed cleanly and was recorded CONFIRMED.

The gate was therefore selecting FOR the falsifiers that ignore the document, which
is precisely the pathology the discrimination control exists to catch. Measured on
Exp 55 (2026-08-23): 6 relative-path falsifiers ERRORed, the 2 detached ones
CONFIRMED, six criticals locked irreducible against a bound of two, and the run
halted at round 0 -- twice, 1152 s and 1178 s of paid dispatch each time.

Nothing anywhere in the suite pinned this. That is what these tests are for.
"""
from __future__ import annotations

import os
import pathlib

import pytest

from bench import reference_runner_v2 as rr

REL = "bench/cdsfl_registry/targets/control_two_distinct_defects.md"


class TestModelsAreGivenAbsolutePaths:
    def test_helper_absolutises(self):
        out = rr._absolute_target(REL)
        assert os.path.isabs(out), f"model would be handed a relative fragment: {out!r}"
        assert out.endswith(REL)

    def test_helper_passes_an_absolute_path_through_unchanged(self):
        already = "/somewhere/else/target.md"
        assert rr._absolute_target(already) == already

    def test_helper_is_empty_safe(self):
        assert rr._absolute_target("") == ""
        assert rr._absolute_target(None) == ""

    @pytest.mark.parametrize("suffix,label", [(".md", "prose"), (".py", "module")])
    def test_sweep_prompt_names_the_full_path(self, suffix, label):
        rel = f"bench/cdsfl_registry/targets/probe{suffix}"
        residual = {"C0001": {"description": "d", "severity": 0.9, "status": "OPEN"}}
        prompt = rr._sweep_prompt(residual, rel, "body text")
        want = rr._absolute_target(rel)
        assert want in prompt, f"{label} sweep prompt lacks the absolute path"
        # and it must not offer the bare relative form as an alternative to read
        assert f"({rel})" not in prompt, f"{label} sweep prompt still shows the relative fragment"

    def test_routing_prompt_names_the_full_path(self):
        rel = "bench/cdsfl_registry/targets/probe.md"
        prompt = rr._routing_resolve_prompt(
            {"description": "d"}, rel, "body text", rr.TARGET_KIND_PROSE)
        assert rr._absolute_target(rel) in prompt
        assert f"TARGET DOCUMENT: {rel}\n" not in prompt


class TestTheAbsolutePathIsTheFormTheMachineryCanHandle:
    """The point of the ruling: relative was the ONE form neither layer supports."""

    def test_retargeter_can_redirect_an_absolute_path(self, tmp_path):
        code = f'open("{rr.REPO_ROOT}/{REL}").read()'
        out, nsub = rr._retarget_falsifier(code, rr.REPO_ROOT, tmp_path)
        assert nsub == 1, "the discrimination control could not redirect this falsifier"
        assert str(tmp_path) in out

    def test_retargeter_CANNOT_redirect_a_relative_path(self, tmp_path):
        """The defect, pinned. Kept as a test so the reason is never re-litigated."""
        code = f'open("{REL}").read()'
        _out, nsub = rr._retarget_falsifier(code, rr.REPO_ROOT, tmp_path)
        assert nsub == 0, (
            "if this now substitutes, the retargeter handles relative paths and this "
            "test should be replaced rather than deleted")

    def test_overlay_builder_still_requires_the_relative_form(self):
        """The internal canonical form stays relative; only prompts go absolute."""
        with pytest.raises(ValueError, match="repo-relative"):
            rr._build_discrimination_overlay(rr.REPO_ROOT, rr._absolute_target(REL), "x")

    def test_fix_block_header_resolves_whether_absolute_or_relative(self):
        class _B:
            def __init__(self, fp): self.file_path = fp
        assert rr._fix_block_targets(_B(REL), REL)
        assert rr._fix_block_targets(_B(rr._absolute_target(REL)), REL), (
            "a model answering with the absolute path must still have its fix matched")


@pytest.mark.skipif(not (rr.REPO_ROOT / REL).is_file(),
                    reason="control target absent from this checkout")
class TestEndToEndThroughTheRealGate:
    """The measurement that the halt was made of, executed rather than described."""

    def _verdict(self, code):
        from bench.falsifier_verify import reverify_falsifier
        return reverify_falsifier(code, repo_root=str(rr.REPO_ROOT))

    FALSIFIER = (
        'import re, pathlib\n'
        'T = pathlib.Path("{path}").read_text()\n'
        'if re.search(r"exceeds `?f_max", T):\n'
        '    print("FALSIFIED")\n'
    )

    def test_a_relative_path_falsifier_still_ERRORs_at_the_gate(self):
        v = self._verdict(self.FALSIFIER.format(path=REL))
        assert v == "ERROR", (
            f"expected the documented failure, got {v}. If the sandbox now populates "
            "its working directory, update this test rather than deleting it.")

    def test_an_ABSOLUTE_path_falsifier_reaches_CONFIRMED_at_the_gate(self):
        v = self._verdict(self.FALSIFIER.format(path=rr._absolute_target(REL)))
        assert v == "CONFIRMED", (
            f"THE REGRESSION THIS FILE EXISTS FOR: got {v}. A falsifier that opens the "
            "real target and finds the planted defect must reach CONFIRMED through the "
            "gate. If this fails, prose runs will halt at round 0 again.")
