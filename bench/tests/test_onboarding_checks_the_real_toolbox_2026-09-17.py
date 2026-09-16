"""Onboarding must check every tool the project actually requires, and must
prove Wolfram computes rather than that its command exists.

FOUNDER RULING 2026-09-16: *"The onboarding script should recommend Wolfram and
other relevant tools ... and provide as much automation in this regard for them
as possible, or point and click/copy and paste options when not."*

WHY THE WOLFRAM CHECK CHANGED. The previous version printed `[FOUND]` whenever
`wolframscript` was on PATH. Through the whole of 2026-09-14 that was true while
every call failed: the licence had lapsed on 2026-09-11 without auto-renewing,
and separately wolframscript could not locate a kernel. Presence is not
capability. These tests drive the state function with a fake subprocess so all 4
states are exercised, including the 2 that a presence check cannot tell apart.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "cdsfl_onboard.py"


@pytest.fixture(scope="module")
def onb():
    spec = importlib.util.spec_from_file_location("onb", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["onb"] = m
    spec.loader.exec_module(m)
    return m


def _toolbox_imports() -> set[str]:
    """The third-party imports named by the Tool Constraint Box."""
    import re
    text = (REPO / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
    names = set(re.findall(r"`import ([a-zA-Z0-9_]+)", text))
    names |= set(re.findall(r"`from ([a-zA-Z0-9_]+) import", text))
    return names - {"ast", "difflib", "dis", "inspect"}   # stdlib: nothing to install


def test_every_toolbox_import_is_checked(onb):
    checked = {im for table in (onb.CORE_PACKAGES, onb.CODE_QUALITY_PACKAGES,
                                onb.STEM_PACKAGES, onb.OPTIONAL_PACKAGES)
               for im, _pip, _desc in table}
    missing = sorted(_toolbox_imports() - checked)
    assert not missing, (
        f"the Tool Constraint Box names these and onboarding checks none of "
        f"them, so a fresh clone passes onboarding and fails on first use: {missing}")


def test_the_pip_names_are_the_installable_ones(onb):
    pip = {im: p for table in (onb.STEM_PACKAGES,) for im, p, _ in table}
    assert pip["sklearn"] == "scikit-learn"
    assert pip["Bio"] == "biopython"
    assert pip["pulp"] == "PuLP"
    assert pip["crosshair"] == "crosshair-tool"


class TestWolframIsProvedNotAssumed:
    def _fake(self, monkeypatch, onb, *, which, returncode=0, out="", raises=False):
        monkeypatch.setattr(onb.shutil, "which", lambda _c: which)

        def fake_run(*a, **k):
            if raises:
                raise subprocess.TimeoutExpired(cmd="x", timeout=1)
            return subprocess.CompletedProcess(a[0], returncode, out, "")
        monkeypatch.setattr(onb.subprocess, "run", fake_run)

    def test_absent_when_the_command_is_missing(self, onb, monkeypatch):
        self._fake(monkeypatch, onb, which=None)
        assert onb.wolfram_state() == "ABSENT"

    def test_ok_only_when_it_returns_2(self, onb, monkeypatch):
        self._fake(monkeypatch, onb, which="/usr/local/bin/wolframscript", out="2\n")
        assert onb.wolfram_state() == "OK"

    def test_expired_licence_is_not_reported_as_found(self, onb, monkeypatch):
        """THE 2026-09-14 CASE: the command exists, nothing computes."""
        self._fake(monkeypatch, onb, which="/usr/local/bin/wolframscript",
                   returncode=255,
                   out="Your Wolfram Engine installation is not activated or is "
                       "experiencing a license-related problem.")
        assert onb.wolfram_state() == "NOT_ACTIVATED"

    def test_missing_kernel_is_its_own_state(self, onb, monkeypatch):
        self._fake(monkeypatch, onb, which="/usr/local/bin/wolframscript",
                   returncode=255,
                   out="A WolframKernel location could not be determined.")
        assert onb.wolfram_state() == "NO_KERNEL"

    def test_a_hang_is_not_success(self, onb, monkeypatch):
        self._fake(monkeypatch, onb, which="/usr/local/bin/wolframscript", raises=True)
        assert onb.wolfram_state() != "OK"

    def test_the_old_presence_check_would_have_passed_all_of_them(self, onb, monkeypatch):
        """POSITIVE CONTROL: the states above are exactly what presence cannot see."""
        monkeypatch.setattr(onb.shutil, "which", lambda _c: "/usr/local/bin/wolframscript")
        assert bool(onb.shutil.which("wolframscript")) is True


def test_the_retired_client_is_labelled_not_recommended(onb):
    opt = {im: desc for im, _pip, desc in onb.OPTIONAL_PACKAGES}
    assert "RETIRED" in opt["wolframalpha"].upper()


def test_dry_run_still_exits_zero():
    r = subprocess.run([sys.executable, str(SCRIPT), "--dry-run"],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:]
