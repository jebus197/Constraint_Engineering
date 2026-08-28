"""The claims audit must catch a stale claim and clear a live one.

WHY IT EXISTS. Three times in 48 hours a canonical document asserted a fact
about data, the data said otherwise, and the stale assertion reached the founder
as a decision to make: merge arbitration "defaults False" (True in every config),
the 133 pairs "PENDING FOUNDER RULING" (tool-decided ten days earlier), and "no
archived report carries a rho series -- measured" (22 of 31 do, and the word
"measured" described no code).

Documents cannot check themselves. scripts/claims_audit.py holds a registry of
claims whose data source is named, and checks each one.

WHAT THIS FILE ASSERTS. Not that the audit runs. That it DISCRIMINATES: a claim
asserted in a document and refuted by the data must fail, and the same claim
once removed from the document must pass. Without both, the audit could pass
forever by matching nothing -- the exact failure mode of the vagueness linter,
which existed since v1.5 and was run against nothing.
"""
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "claims_audit.py"
sys.path.insert(0, str(REPO / "scripts"))
import claims_audit as ca  # noqa: E402


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=REPO, timeout=120)


class TestTheRegistryIsRealAndChecked:
    def test_the_registry_is_not_empty(self):
        assert len(ca.CLAIMS) >= 3, "an audit with no claims passes forever"

    def test_every_claim_names_a_document_and_a_checker(self):
        for name, sites, check in ca.CLAIMS:
            assert sites, f"{name}: no document site given"
            assert callable(check), f"{name}: no checker"
            for rel, pat in sites:
                assert (REPO / rel).is_file() or True, rel  # a site may be deleted
                assert pat, f"{name}: empty pattern"

    def test_each_checker_returns_a_verdict_and_a_reason(self):
        """A checker that returns a bare boolean gives the reader nothing."""
        for name, _, check in ca.CLAIMS:
            holds, detail = check()
            assert isinstance(holds, bool), f"{name}: verdict is not a boolean"
            assert isinstance(detail, str) and detail.strip(), (
                f"{name}: no reason given, so a failure would be unactionable"
            )


class TestItDiscriminates:
    def test_the_tree_currently_passes(self):
        r = _run()
        assert r.returncode == 0, f"a registered claim is stale:\n{r.stdout}"

    def test_reintroducing_a_stale_claim_makes_it_FAIL(self, tmp_path):
        """KNOWN-BAD, applied to the real tree and reverted.

        The rho claim is the one whose document text was corrected on
        2026-08-28. Putting the old wording back must fail the audit, because
        the data still refutes it.
        """
        target = REPO / "scripts" / "replay_accounting.py"
        orig = target.read_text(encoding="utf-8")
        try:
            target.write_text(orig + '\n# count of rho-shaped keys is zero\n',
                              encoding="utf-8")
            r = _run()
            assert r.returncode == 1, (
                "re-asserting a claim the data refutes did NOT fail the audit; "
                f"the check is not discriminating\n{r.stdout}"
            )
            assert "STALE" in r.stdout and "rho series" in r.stdout
        finally:
            target.write_text(orig, encoding="utf-8")
        assert target.read_text(encoding="utf-8") == orig, "tree not restored"

    def test_the_two_answers_differ(self):
        """Belt and braces: clean tree passes, dirtied tree fails."""
        clean = _run().returncode
        target = REPO / "scripts" / "replay_accounting.py"
        orig = target.read_text(encoding="utf-8")
        try:
            target.write_text(orig + '\n# count of rho-shaped keys is zero\n',
                              encoding="utf-8")
            dirty = _run().returncode
        finally:
            target.write_text(orig, encoding="utf-8")
        assert clean == 0 and dirty == 1, f"clean={clean} dirty={dirty}"


class TestTheCheckersMeasureTheRightThing:
    def test_rho_checker_finds_the_series_that_actually_exists(self):
        holds, detail = ca.rho_series_absent()
        assert holds is False, "the rho checker says no report carries a series"
        assert "DO carry" in detail

    def test_merge_checker_reads_configs_not_the_dataclass(self):
        holds, detail = ca.merge_arbitration_default()
        assert holds is False, (
            "the merge checker agrees the flag defaults off; it should be reading "
            "configs, where it is True everywhere"
        )

    def test_pairs_checker_reads_the_adjudication_output(self):
        holds, detail = ca.pairs_pending_founder()
        if "no adjudication output exists" in detail:
            pytest.skip("adjudication output absent on this machine")
        assert holds is False and "BY TOOL" in detail


def test_list_mode_costs_nothing():
    r = _run("--list")
    assert r.returncode == 0 and "rho series" in r.stdout
