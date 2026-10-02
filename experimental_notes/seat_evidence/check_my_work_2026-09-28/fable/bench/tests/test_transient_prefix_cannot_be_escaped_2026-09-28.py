# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b009a0833304a8a1789998a333d7df78e9c322937e70746ccf7963ae379bd71a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A write that lands in the repository must not classify "transient".

PANEL FINDING (seat B), 2026-09-28, against the literal-leading-prefix rule
added to `hooks/ffafp_audit.py:classify_path` on 2026-09-24. That rule decides
transience by where a path STARTS, and the start does not bind where the write
LANDS:

  /tmp/../<anything>/hooks/evil.py       -- a literal `..` segment
  /tmp/${V:-../../repo}/hooks/evil.py    -- a default-value expansion the
                                            assignment parser cannot see but
                                            the real shell honours
  /tmp/$V/hooks/evil.py                  -- V knowable from neither the command
                                            nor the hook's environment

All three classified "transient" before this fix -- the one verdict that
EXCUSES a write -- while the actual write can land inside the repository.
Demonstrated by executing bash: `mkdir -p t/repo/hooks && cd t &&
echo x > /tmp/${V:-<abs-of-t>/repo}/hooks/evil.py` creates the file under
t/repo/. After the fix a dynamic remainder under a transient head returns
"unresolved" (neither accuses nor excuses) and a literal traversal is
classified by its extension (accuses honestly).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def fa():
    spec = importlib.util.spec_from_file_location(
        "ffafp_audit_escape_ut", ROOT / "hooks" / "ffafp_audit.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ffafp_audit_escape_ut"] = m
    spec.loader.exec_module(m)
    return m


class TestTheEscapesAreClosed:
    def test_literal_traversal_is_classified_by_its_extension(self, fa):
        assert fa.classify_path("/tmp/../repo/hooks/evil.py") == "code"
        assert fa.classify_path("/var/folders/x/../../repo/notes.md") == "doc"

    def test_a_dynamic_remainder_under_a_transient_head_is_unresolved(self, fa):
        assert fa.classify_path("/tmp/$V/hooks/evil.py") == "unresolved"
        assert fa.classify_path("/tmp/${V:-../../repo}/hooks/evil.py") == "unresolved"
        # command substitution is dynamic too, and the old variable regex
        # never matched `$(`:
        assert fa.classify_path("/tmp/$(echo ..)/repo/evil.py") == "unresolved"

    def test_classify_write_resolves_before_judging_so_known_vars_still_work(self, fa):
        # A variable ASSIGNED IN THE COMMAND resolves to a genuinely transient
        # path and must still classify transient -- the 2026-09-24 bounce fix.
        got = fa.classify_write("$SP/gate_in.json", 'SP=/tmp/scratch; echo x > $SP/gate_in.json')
        assert got == "transient"


class TestNothingLegitimateIsReclassified:
    """ANTI-VACUITY: the ordinary transient shapes keep their verdict."""

    def test_plain_tmp_writes_stay_transient(self, fa):
        assert fa.classify_path("/tmp/run.log") == "transient"
        assert fa.classify_path("/private/tmp/x/out.json") == "transient"
        assert fa.classify_path("/var/folders/ab/cd/T/scratch.txt") == "transient"
        assert fa.classify_path("/dev/null") == "transient"

    def test_the_2026_09_24_head_and_extension_rule_is_unchanged(self, fa):
        assert fa.classify_path("bench/targets/exp$n.py") == "code"
        assert fa.classify_path("bench/logs/run_$STAMP/BRIEF.md") == "doc"
        assert fa.classify_path("$WORK/x.py") == "unresolved"


def test_the_escape_is_real_not_theoretical(fa, tmp_path):
    """EXECUTED: the shell expansion the classifier cannot see lands the write
    inside a repository tree."""
    import subprocess
    (tmp_path / "repo" / "hooks").mkdir(parents=True)
    target_dir = str(tmp_path / "repo")
    # On macOS /tmp resolves to /private/tmp, so /tmp/.. is /private; step up
    # enough levels that the traversal reaches / and re-enter the target:
    ups = "../" * 8
    cmd = 'echo x > /tmp/' + ups + target_dir.lstrip("/") + '/hooks/evil.py'
    subprocess.run(["bash", "-c", cmd], check=True)
    assert (tmp_path / "repo" / "hooks" / "evil.py").is_file(), (
        "premise gone: the traversal write no longer lands; re-examine"
    )
    assert fa.classify_path(cmd.split("> ", 1)[1]) == "code"
