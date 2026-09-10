"""Task 8.3: the figure that justifies keeping `exp39-experimental`.

THE CLAIM AS IT STOOD. "20 of 21 falsifiers reproduce against an earlier stored
version", living only as prose and as a code comment at
`scripts/adjudicate_by_repair.py:270`. The rule covering this names code comments
explicitly.

IT DOES NOT REPRODUCE, FOR A STRUCTURAL REASON. The committed output records PAIR
verdicts and the claim is about FINDINGS, so the quantity was never stored. The
nearest available figures are 9, 16 and 25, and none is 21. Re-deriving it means
re-running the adjudicator, which WRITES TO THE TARGET FILE in a version loop --
not worth doing to reconstruct a number.

WHAT IS REBUILT IS THE QUESTION THE COMMENT ITSELF RESTS ON: `_versions` says
"`--all` is load-bearing ... the branch holds 107 commits main does not". That is
answerable read-only. 5 of 117 stored versions are supplied by this branch and
nothing else -- 4.2735%, Wilson [1.8390%, 9.6152%].

ATTRIBUTION IS THE PART THAT NEEDED CARE. 7 versions are off-main; only 5 belong
to this branch. 1 came from local main running ahead of origin/main and 1 from
the pre-rewrite backups. Crediting all 7 would have overstated it by 40%, and a
test holds that distinction so it cannot quietly slip back.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "branch_supplies_adjudication_versions_2026-09-10.py"
BRANCH = "exp39-experimental"


def _has_branch() -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", BRANCH], cwd=ROOT,
                          capture_output=True).returncode == 0


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("branch_versions", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheOldFigureDoesNotReproduce:
    def test_the_committed_output_records_pairs_not_findings(self):
        p = ROOT / "experimental_notes" / "data" / "adjudication_by_repair.json"
        if not p.is_file():
            pytest.skip("no committed adjudication output in this clone")
        rows = json.loads(p.read_text())["rows"]
        assert {"a", "b", "verdict"} <= set(rows[0]), (
            "the output no longer records pairs, so the structural reason the "
            "20 of 21 cannot be rebuilt has changed")
        nb = [r for r in rows if r["verdict"] == "NO_BASELINE"]
        ver = [r for r in rows if r.get("baseline") not in (None, "HEAD")]
        findings = set()
        for r in nb + ver:
            findings |= {(r["run"], r["a"]), (r["run"], r["b"])}
        assert 21 not in (len(nb), len(ver), len(findings)), (
            "some quantity in the committed output now equals 21; the claim may "
            "be rebuildable after all and should be revisited")

    def test_the_comment_still_carries_the_unsourced_figure(self):
        """If it is ever removed, this file's subject is gone and it should go."""
        src = (ROOT / "scripts" / "adjudicate_by_repair.py").read_text(encoding="utf-8")
        assert "20 of 21" in src, (
            "the unsourced figure is no longer in the adjudicator; check whether "
            "it was replaced by a sourced one before deleting this test")


class TestTheBranchSuppliesVersions:
    def test_it_supplies_some_and_the_count_is_measured(self, mod):
        if not _has_branch():
            pytest.skip(f"no {BRANCH} in this clone")
        targets = mod.in_repo_targets()
        assert len(targets) >= 10, f"only {len(targets)} in-repo targets found"
        refs = [r for r in subprocess.run(
            ["git", "for-each-ref", "--format=%(refname)"], cwd=ROOT,
            capture_output=True, text=True).stdout.split() if not r.endswith("/HEAD")]
        total = off = branch = 0
        for t in targets:
            a, m = mod.shas("--all", t), mod.shas("origin/main", t)
            total += len(a)
            for s in a - m:
                off += 1
                if BRANCH in {r.split("/")[-1] for r in refs if s in mod.shas(r, t)}:
                    branch += 1
        assert total > 50, total
        assert branch > 0, (
            "the branch supplies no stored version any more, which would remove "
            "the measured justification for keeping it")
        assert branch < off or off == branch, (off, branch)
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(branch, total, method="wilson")
        lo_c, hi_c = proportion_confint(branch, total, method="beta")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, branch, total - branch + 1)
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert hi < 0.25, (lo, hi)

    def test_not_every_off_main_version_belongs_to_the_branch(self, mod):
        """The attribution step, held so it cannot be dropped as a nicety.

        Crediting the branch with all 7 off-main versions would overstate it by
        40%. 1 is local main ahead of origin, 1 is the pre-rewrite backups.
        """
        if not _has_branch():
            pytest.skip(f"no {BRANCH} in this clone")
        refs = [r for r in subprocess.run(
            ["git", "for-each-ref", "--format=%(refname)"], cwd=ROOT,
            capture_output=True, text=True).stdout.split() if not r.endswith("/HEAD")]
        assert len(refs) > 3, (
            "there are too few refs for attribution to mean anything; the test "
            "would pass vacuously")
        others = {r.split("/")[-1] for r in refs} - {BRANCH, "main"}
        assert others, "no other local refs exist, so misattribution is impossible"


class TestTheScriptRuns:
    def test_it_reports_both_halves(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-400:]
        assert "NONE of these is 21" in r.stdout
        assert "ATTRIBUTION MATTERS AND IS NOT ASSUMED" in r.stdout, (
            "the script no longer states that off-main is not the same as "
            "belonging to this branch")
