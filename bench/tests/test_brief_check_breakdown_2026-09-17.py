"""The per-check brief breakdown that replaces an unproduced "47 of 49" (task P4).

Entry P4 said the founder's point about fixes "is still true of 47 of 49 briefs",
and no committed script printed 47. `scripts/brief_archive_refusal_rate_2026-09-10.py`
now prints, per shape check and split at the 2026-09-09 ruling, how many archived
briefs the committed validator finds meeting each check. These tests CALL
`per_check()`; none reads the script's text.

It also carries the evidence for the delivery check added to
`scripts/panel_brief_validate.py` the same day: that check is only worth enabling
if it separates the post-ruling briefs that carried the delivery rule from those
that did not.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bench import archive_corpus as corpus  # noqa: E402

SCRIPT = ROOT / "scripts" / "brief_archive_refusal_rate_2026-09-10.py"
FIX = "requires a fix, not only a finding"
TESTED = "requires the fix to be TESTED"
DELIVERED = "requires the fix to be DELIVERED as a file"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("brief_breakdown", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def archive(mod):
    return [(name, b.read_text(encoding="utf-8", errors="replace"))
            for name, b in mod.briefs()]


COMPLIANT = """# Does the intake parser drop falsifier blocks?

The artefact under review is `bench/runner_core.py`.

## Use the harness
You must RUN the parser against the archived replies. Use S_k and gamma to say
whether a recovered block would have changed the verdict.

## Produce a fix and test it
A finding without a fix is half an answer. Write a runnable falsifier, EXECUTE it,
and report the command and its output. Write the fix INTO the sandbox repository
tree at its real path.

## What would refute you
State what evidence would overturn your own conclusion.

## Output
Return: verdict, reasoning, the falsifier and its executed result.

## Termination
Stop when a further pass produces no new above-threshold findings.
"""


class TestTheBreakdownCountsWhatTheValidatorSays:
    def test_synthetic_briefs_are_counted_exactly(self, mod):
        untested = COMPLIANT.replace("falsifier", "result")
        undelivered = COMPLIANT.replace(
            " Write the fix INTO the sandbox repository\ntree at its real path.", "")
        assert untested != COMPLIANT and undelivered != COMPLIANT, "fixtures must change"
        items = [("panel_round90_2026-09-12", COMPLIANT),
                 ("panel_round91_2026-09-12", untested),
                 ("panel_round92_2026-09-12", undelivered),
                 ("panel_old_20260901T000000Z", "# q\n\nWhat do you think?\n")]
        s = mod.per_check(items)
        assert s["pre"]["n"] == 1 and s["pre"]["refused"] == 1
        assert s["pre"]["meets"][FIX] == 0 and s["pre"]["fix_and_tested"] == 0
        post = s["post"]
        assert post["n"] == 3
        assert post["refused"] == 2, post
        assert post["meets"][FIX] == 3, post
        assert post["meets"][TESTED] == 2, post
        assert post["meets"][DELIVERED] == 2, post
        assert post["fix_and_tested"] == 2, post

    def test_it_agrees_with_validate_called_directly_on_the_archive(self, mod, archive):
        """2 FORMS: the aggregate, and validate() called brief by brief."""
        reason = corpus.shortfall(len(archive), 49, "archived panel briefs")
        if reason:
            pytest.skip(reason)
        pbv_spec = importlib.util.spec_from_file_location(
            "pbv_direct", ROOT / "scripts" / "panel_brief_validate.py")
        pbv = importlib.util.module_from_spec(pbv_spec)
        pbv_spec.loader.exec_module(pbv)
        s = mod.per_check(archive)
        for label, _, _ in pbv.CHECKS:
            direct = sum(1 for _, text in archive
                         if not any(p.startswith(label + ":") for p in pbv.validate(text)))
            assert s["pre"]["meets"][label] + s["post"]["meets"][label] == direct, label


class TestTheArchiveFigures:
    def test_the_pre_ruling_breakdown(self, mod, archive):
        """The 49 briefs before the ruling are closed, so these are fixed values.

        24 of 49 lack 1 or both of the fix and tested checks. That is the
        committed validator's LEXICAL reading and is not the reading behind the
        "47 of 49" P4 quoted, which no script produced.
        """
        s = mod.per_check(archive)["pre"]
        reason = corpus.shortfall(s["n"], 49, "pre-ruling panel briefs")
        if reason:
            pytest.skip(reason)
        assert s["n"] == 49
        assert s["refused"] == 49
        assert s["meets"][FIX] == 43
        assert s["meets"][TESTED] == 27
        assert s["fix_and_tested"] == 25
        assert s["meets"][DELIVERED] == 0

    def test_the_delivery_check_separates_the_post_ruling_briefs(self, mod, archive):
        """Enabled only because it discriminates: rounds 5 and 6, which returned
        0 source files, fail it; round 7, whose brief introduced the rule, passes."""
        mirror = mod._load("mirror_records",
                           ROOT / "scripts" / "mirror_panel_records_2026-09-11.py")
        post = [(n, t) for n, t in archive if (mirror.round_date(n) or "") >= mod.RULING]
        reason = corpus.shortfall(len(post), 10, "post-ruling panel briefs")
        if reason:
            pytest.skip(reason)
        by_name = {n: mod.per_check([(n, t)])["post"]["meets"][DELIVERED] for n, t in post}
        assert by_name.get("panel_round5_2026-09-10") == 0
        assert by_name.get("panel_round6_2026-09-10") == 0
        assert by_name.get("panel_round7_2026-09-10") == 1
        met = sum(by_name.values())
        assert 0 < met < len(by_name), f"{met} of {len(by_name)} meet it; it does not discriminate"
