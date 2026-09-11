"""Task A18: two of the three "unwired" config fields are wired, and I can say why.

THE ENTRY SAYS THREE exp56 OFF-SWITCHES ARE "read by none of the 210 runner
modules under `bench/`, resolved by AST, not by grep". Two of the three are read:

  merge_arbitration_enabled   reference_runner_v3.py:12638
                              `if getattr(cfg, "merge_arbitration_enabled", False)`
  immune_memory_enabled       reference_runner_v3.py:14984, same form
  _ouroboros.max_papers_per_round
                              genuinely unread -- and its SIBLING in the same
                              block, `api_access`, IS read at
                              reference_runner_v3.py:9423, so the block reaches
                              the runner and exactly 1 of its 2 keys is consulted

WHY THE SWEEP MISSED THEM, and it is this project's recurring shape in a new
place. An AST scan for attribute access resolves `cfg.field` and reports ZERO for
`getattr(cfg, "field", False)` -- which is the same read, written as a string.
The sweep chose AST over grep for good reasons and then looked for one of the two
forms the language offers. Substring-versus-token, attribute-versus-getattr:
the same mistake wearing a different hat.

AND THE ARM IS NOT LYING TO ITS READER, which is what the entry was worried
about. `max_papers_per_round = 0` is REDUNDANT rather than inert: the arm's
stated intent is "External literature retrieval OFF", and `api_access: []`
achieves it through the key that IS read. A reader who believed the capability
was disabled for the experiment was right -- for a different reason than they
would have guessed.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "config_fields_are_read_2026-09-11.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("cfgread", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cfgread"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestBothAccessFormsAreResolved:
    def test_a_getattr_read_is_found(self, m):
        """The form the original sweep could not see."""
        sites = m.readers_of("merge_arbitration_enabled")
        assert sites, "the getattr form is invisible again"
        assert any("reference_runner_v3.py" in s for s in sites), sites

    def test_the_second_one_too(self, m):
        sites = m.readers_of("immune_memory_enabled")
        assert any("reference_runner_v3.py" in s and "getattr" in s
                   for s in sites), sites

    def test_a_plain_attribute_read_is_found(self, m):
        """ANTI-VACUITY for the widening: the ORIGINAL form must still resolve,
        or the resolver has swapped one blind spot for another."""
        sites = m.readers_of("immune_memory_path")
        assert sites, "cfg.attribute reads are no longer resolved at all"

    def test_a_field_nothing_reads_comes_back_empty(self, m):
        assert m.readers_of("a_field_name_that_appears_nowhere_at_all") == []


class TestTheOneGenuinelyUnreadField:
    def test_max_papers_per_round_is_read_by_nothing(self, m):
        assert m.readers_of("max_papers_per_round") == []

    def test_its_sibling_in_the_same_block_is_read(self, m):
        """This is what makes it REDUNDANT rather than a broken config: the
        `_ouroboros` block does reach the runner, and the arm's intent is
        achieved by the key beside it."""
        sites = m.readers_of("api_access")
        assert any("reference_runner_v3.py" in s for s in sites), sites

    def test_the_arm_really_does_declare_retrieval_off(self):
        """ANTI-VACUITY. If api_access were non-empty, "redundant" would be the
        wrong word and the entry's worry would stand."""
        import json
        arms = sorted((ROOT / "bench" / "exp56_configs").glob("*.json"))
        assert arms, "the exp56 configs are gone"
        checked = 0
        for f in arms:
            cfg = json.loads(f.read_text(encoding="utf-8"))
            o = cfg.get("_ouroboros")
            if not o:
                continue
            checked += 1
            assert o.get("api_access") == [], (
                f"{f.name} no longer declares retrieval off through the key "
                f"that is actually read; max_papers_per_round being ignored "
                f"stops being redundant and starts being a hole")
        assert checked >= 1, "no arm carries an _ouroboros block any more"


class TestTheScriptRuns:
    def test_it_reports_and_states_the_lesson(self):
        import subprocess
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--field", "merge_arbitration_enabled",
             "--field", "max_papers_per_round"],
            cwd=ROOT, capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-400:]
        assert "READ BY NOTHING" in r.stdout
        assert "BOTH ACCESS FORMS ARE RESOLVED" in r.stdout, (
            "the script no longer states why the original sweep was wrong")
