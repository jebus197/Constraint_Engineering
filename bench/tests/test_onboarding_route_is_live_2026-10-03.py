#!/usr/bin/env python3
"""A new reader must be ROUTED to the installer, and no document may re-type its list.

WHAT THIS GUARDS, measured 2026-10-03 by a 6-agent audit that ran in isolated
sandboxes and changed nothing on the host.

`scripts/cdsfl_onboard.py` is a real installer: 1214 lines, added 2026-04-08, 28
Python packages plus 3 system tools, 8 consent prompts each printing the exact
command first. A probe that replaced `subprocess.run` with a recorder caught it
dispatching `pip install sympy z3-solver` and `brew install graphviz`, so it
installs rather than merely checking. It was never the problem.

THE DOCUMENTS WERE. `resources/ONBOARDING.md` named the installer 0 times across
2944 lines; its only install pointer sat at line 2812 of 2944 — 95.5% of the way
through — and pointed elsewhere. `START_HERE.md`, which calls itself the map for a
first-time reader, had 0 of its 124 lines mentioning install, setup, prerequisite or
dependency. So the founder had never been able to test whether ONBOARDING.md could
onboard anyone, because nothing in it said to run the thing that does.

AND THE SECOND COPY DRIFTED, WHICH IS WHY THIS TEST FORBIDS SECOND COPIES.
`docs/REPRODUCING.md` carried a hand-typed `pip install` line naming 18 of the 28
packages, 64.2857%, omitting PuLP, astropy, biopython, crosshair-tool, matplotlib,
networkx, pandas, pint, rdkit and scikit-learn. `bench/tests/test_specialist_shadow_cells.py`
calls `pytest.fail` on an ImportError for pint, astropy and rdkit, so 3 tests
hard-failed for anyone who followed that page while it stated "All tests should
pass". The installer's tables changed 2026-09-17 and the document's list 2026-08-15,
a 33-day drift that a later edit to the document did not close, because nothing
compared the two. `bench/tests/test_researcher_onboarding.py` holds 13 tests and
none of them compared the two either.

THE PACKAGE LIST IS READ BY EXECUTING THE INSTALLER, never by parsing its source.
A source scan would only show that the script describes itself consistently, and
this project has 4 defects found by executing 2 forms against each other where
reading found none.
"""
import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
INSTALLER_REL = "scripts/cdsfl_onboard.py"
INSTALLER = REPO / INSTALLER_REL


def _installer_packages() -> set[str]:
    """The pip names the installer actually offers, by EXECUTING it."""
    spec = importlib.util.spec_from_file_location("_cdsfl_onboard_probe", INSTALLER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_cdsfl_onboard_probe"] = mod
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass  # the module answers --help and exits; its tables are still bound
    names: set[str] = set()
    for table in ("CORE_PACKAGES", "CODE_QUALITY_PACKAGES", "STEM_PACKAGES"):
        rows = getattr(mod, table, None)
        assert rows, f"{table} is missing or empty in {INSTALLER_REL}"
        for row in rows:
            # (import_name, pip_name, description)
            names.add(str(row[1]).strip().lower())
    return names


class TestThePremiseIsAlive:
    def test_the_installer_exists_and_offers_a_real_set(self):
        """If this fails, every other test here is vacuous."""
        assert INSTALLER.is_file(), f"{INSTALLER_REL} is missing"
        pkgs = _installer_packages()
        assert len(pkgs) >= 20, (
            f"the installer offers only {len(pkgs)} packages; this guard was written "
            f"against 28 and a collapse that large means the tables moved"
        )


class TestTheReaderIsRouted:
    @pytest.mark.parametrize("rel,within", [
        ("resources/ONBOARDING.md", 80),
        ("START_HERE.md", None),
    ])
    def test_the_entry_point_names_the_installer(self, rel: str, within):
        """ONBOARDING.md must name it EARLY. A pointer at line 2812 of 2944 is not a
        route; it is a thing a reader finds after they have given up."""
        p = REPO / rel
        if not p.is_file():
            pytest.skip(f"{rel} is absent from this checkout")
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [i + 1 for i, ln in enumerate(lines) if "cdsfl_onboard" in ln]
        assert hits, (
            f"{rel} never names scripts/cdsfl_onboard.py, so a new reader is not "
            f"routed to the installer at all. That was the 2026-10-03 state: 0 "
            f"mentions in 2944 lines."
        )
        if within is not None:
            assert min(hits) <= within, (
                f"{rel} names the installer first at line {min(hits)} of "
                f"{len(lines)}, which is too late to be a route. Put it within the "
                f"first {within} lines."
            )

    def test_start_here_offers_a_setup_step_in_words_a_reader_would_search_for(self):
        p = REPO / "START_HERE.md"
        if not p.is_file():
            pytest.skip("START_HERE.md is absent from this checkout")
        text = p.read_text(encoding="utf-8", errors="replace").lower()
        assert any(w in text for w in ("set this up", "install", "setup")), (
            "START_HERE.md calls itself the map for a first-time reader and offers "
            "no setup step. Measured 2026-10-03: 0 of its 124 lines contained "
            "install, setup, prerequisite or dependency."
        )


class TestNoDocumentReTypesTheList:
    """A second copy of the package list is a second thing to drift."""

    DOCS = ["docs/REPRODUCING.md", "resources/ONBOARDING.md", "START_HERE.md",
            "README.md"]

    @pytest.mark.parametrize("rel", DOCS)
    def test_no_multi_package_pip_line_disagrees_with_the_installer(self, rel: str):
        p = REPO / rel
        if not p.is_file():
            pytest.skip(f"{rel} is absent from this checkout")
        text = p.read_text(encoding="utf-8", errors="replace")
        offered = _installer_packages()

        # every `pip install a b c ...` run of 3+ package-looking tokens
        for m in re.finditer(r'pip\s+install\s+((?:[A-Za-z0-9_.\-]+(?:\s+\\?\s*)?){3,})',
                             text):
            listed = {t.strip().lower() for t in re.split(r'[\s\\]+', m.group(1))
                      if t.strip() and not t.strip().startswith("-")}
            listed &= offered | {t for t in listed if t in offered}
            # only judge lines that are plainly trying to be THE dependency list
            if len(listed & offered) < 3:
                continue
            missing = sorted(offered - listed)
            assert not missing, (
                f"{rel} re-types the dependency list and it DISAGREES with "
                f"{INSTALLER_REL}: it omits {len(missing)} of {len(offered)} "
                f"packages — {', '.join(missing)}. Do not maintain a second copy; "
                f"point the reader at `python3 scripts/cdsfl_onboard.py`, whose "
                f"tables are the maintained source. This is the exact defect "
                f"measured on 2026-10-03, when the omission of pint, astropy and "
                f"rdkit hard-failed 3 tests on the same page that promised "
                f"'All tests should pass'."
            )


class TestTheClaimedGuardIsThisFile:
    def test_reproducing_cites_this_test_by_name(self):
        """docs/REPRODUCING.md's correction note names this file as its guard. If the
        name drifts, the citation becomes a claim about evidence that does not
        exist — the defect class this project calls an unwired addition."""
        p = REPO / "docs/REPRODUCING.md"
        if not p.is_file():
            pytest.skip("docs/REPRODUCING.md is absent from this checkout")
        text = p.read_text(encoding="utf-8", errors="replace")
        me = pathlib.Path(__file__).name
        if "test_onboarding_route_is_live" not in text:
            pytest.skip("REPRODUCING.md does not cite this guard; nothing to hold")
        assert me in text, (
            f"REPRODUCING.md cites a guard whose filename is not {me}; the citation "
            f"points at nothing"
        )
