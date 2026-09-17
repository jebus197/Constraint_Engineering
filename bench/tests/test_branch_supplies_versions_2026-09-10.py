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
answerable read-only.

REWRITTEN 2026-09-17 (task 8.3 correction, panel round 16). The earlier version of
this file asserted `total > 50`, `branch > 0` and `hi < 0.25`, stayed green while
the figure drifted from 5 of 117 to 5 of 118 and from 7 off-main to 6, carried an
assertion (`branch < off or off == branch`) that cannot fail because `branch`
never exceeds `off` (z3: the negation is unsat), and held the attribution only as a
printed constant. What replaces it:

  * `experimental_notes/data/branch_supplies_versions.json`, written by the
    script's `--write-sidecar`, pins the ref tips measured and every count.
  * The pin is REPLAYED from those recorded tips, so the dated figure is held
    exactly and a later commit to a target file cannot silently change it. Every
    count, every off-main version and its ref set, and both intervals must match,
    and a mismatch names the old and new values.
  * The branch resolution order, the computed attribution sentence and the
    UNAVAILABLE refusal (exit 4, no numbers) are each executed, with controls.
"""
from __future__ import annotations

import importlib.util
import json
import math
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "branch_supplies_adjudication_versions_2026-09-10.py"
SIDECAR = ROOT / "experimental_notes" / "data" / "branch_supplies_versions.json"
BRANCH = "exp39-experimental"
COUNTS = ("n_targets", "total", "off_main", "from_branch", "branch_only", "not_from_branch")
REFRESH = ("if the change is real, re-run `python3 scripts/"
           "branch_supplies_adjudication_versions_2026-09-10.py --write-sidecar` "
           "and re-date the figure quoted in task 8.3")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("branch_versions", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def pin() -> dict:
    return json.loads(SIDECAR.read_text(encoding="utf-8"))


def _object_exists(sha: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT,
                          capture_output=True).returncode == 0


def _replayable_tips(pin: dict) -> dict:
    """The pinned tips this clone can replay, or a skip naming what is missing.

    A tip whose commit is absent (a dropped stash, a deleted worktree branch) is
    dropped ONLY if no pinned off-main version names it, since then it supplied
    nothing the figure counts. If a version names it, the replay cannot be exact
    and the test skips with the ref named, rather than comparing a different figure.
    """
    named = {r for v in pin["versions"] for r in v["refs"]}
    tips, blocking = {}, []
    for ref, sha in pin["tips"].items():
        if _object_exists(sha):
            tips[ref] = sha
        elif ref in named or ref == pin["main_ref"]:
            blocking.append(ref)
    if blocking:
        pytest.skip(f"this clone lacks the commits behind {blocking}, which the "
                    "pinned figure depends on, so it cannot be replayed here")
    return tips


@pytest.fixture(scope="module")
def replay(mod, pin, tmp_path_factory):
    """Run the script's own `main(['--write-sidecar'])` on the pinned tips.

    This executes the `--write-sidecar` path end to end, into a temp file, and the
    record it writes IS the recomputed measurement. The committed sidecar is
    never rewritten by the suite.
    """
    tips = _replayable_tips(pin)
    out = tmp_path_factory.mktemp("replay") / "branch_supplies_versions.json"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(mod, "live_tips", lambda: dict(tips))
        mp.setattr(mod, "SIDECAR", out)
        mp.setattr(mod, "REPO", ROOT)
        rc = mod.main(["--write-sidecar"])
    assert rc == 0, f"the replay exited {rc}"
    assert out.is_file(), "--write-sidecar returned 0 and wrote nothing"
    return json.loads(out.read_text(encoding="utf-8"))


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
    def test_the_targets_are_the_pinned_targets(self, mod, pin):
        live = mod.in_repo_targets()
        assert live == pin["targets"], (
            f"in-repo targets moved: pinned {len(pin['targets'])} "
            f"{sorted(set(pin['targets']) - set(live))} gone, "
            f"{sorted(set(live) - set(pin['targets']))} new, live {len(live)}; {REFRESH}")

    def test_every_count_reproduces_from_the_pinned_tips(self, pin, replay):
        drift = {k: (pin[k], replay[k]) for k in COUNTS if pin[k] != replay[k]}
        assert not drift, (
            "the pinned figure does not reproduce: "
            + ", ".join(f"{k} pinned {a} recomputed {b}" for k, (a, b) in drift.items())
            + f" (pinned at {pin['head'][:7]}); {REFRESH}")
        assert replay["branch_ref"] == pin["branch_ref"]

    def test_every_off_main_version_and_its_refs_reproduce(self, pin, replay):
        def key(vs):
            return [(v["target"], v["sha"], tuple(v["refs"]), v["from_branch"],
                     v["branch_only"]) for v in vs]
        assert key(replay["versions"]) == key(pin["versions"]), (
            f"pinned {key(pin['versions'])}\nrecomputed {key(replay['versions'])}; {REFRESH}")

    def test_the_intervals_reproduce_and_two_tools_agree(self, pin, replay):
        k, n = pin["from_branch"], pin["total"]
        for name in ("wilson", "clopper_pearson"):
            for a, b in zip(pin["intervals"][name], replay["intervals"][name]):
                assert abs(a - b) < 1e-12, (name, pin["intervals"][name],
                                            replay["intervals"][name])
        # Wilson in closed form, sharing no code with statsmodels.
        z = 1.959963984540054
        p = k / n
        centre = (p + z * z / (2 * n)) / (1 + z * z / n)
        half = z / (1 + z * z / n) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
        lo, hi = pin["intervals"]["wilson"]
        assert abs(lo - (centre - half)) < 1e-9 and abs(hi - (centre + half)) < 1e-9
        assert abs(pin["intervals"]["clopper_pearson"][0]
                   - pin["intervals"]["clopper_pearson_lo_scipy"]) < 1e-9, (
            "statsmodels and scipy disagree on the Clopper-Pearson lower bound")

    def test_not_every_off_main_version_belongs_to_the_branch(self, pin, replay):
        """The attribution step, counted rather than asserted.

        The count of off-main versions the branch does NOT reach is recomputed from
        the replayed ref sets and compared with the pin.
        """
        unreached = [v for v in replay["versions"] if not v["from_branch"]]
        assert len(unreached) == replay["not_from_branch"] == pin["not_from_branch"], (
            f"off-main versions not reached by the branch: pinned "
            f"{pin['not_from_branch']}, recomputed {len(unreached)}; {REFRESH}")


class TestBranchResolution:
    def test_the_order_is_heads_then_remotes_then_the_pin_tag(self, mod):
        tag = f"refs/tags/{mod.PIN_TAG}"
        heads = f"refs/heads/{BRANCH}"
        remote = f"refs/remotes/origin/{BRANCH}"
        assert mod.resolve_branch({heads: "a", remote: "b", tag: "c"}) == heads
        assert mod.resolve_branch({remote: "b", tag: "c"}) == remote
        assert mod.resolve_branch({tag: "c"}) == tag
        assert mod.resolve_branch({}) is None

    def test_lookalike_refs_do_not_resolve(self, mod):
        assert mod.resolve_branch({
            f"refs/original/refs/heads/{BRANCH}": "a",
            f"refs/remotes/origin/{BRANCH}-old": "b",
            f"refs/heads/{BRANCH}-2": "c",
            f"refs/tags/{BRANCH}": "d",
        }) is None


class TestTheAttributionIsComputed:
    @staticmethod
    def _m(off_refs: list, branch_ref=f"refs/heads/{BRANCH}"):
        versions = [{"target": f"t{i}", "sha": f"s{i}", "refs": refs,
                     "from_branch": branch_ref in refs,
                     "branch_only": refs == [branch_ref]}
                    for i, refs in enumerate(off_refs)]
        b = sum(v["from_branch"] for v in versions)
        return {"off_main": len(versions), "from_branch": b,
                "branch_only": sum(v["branch_only"] for v in versions),
                "versions": versions, "branch_ref": branch_ref,
                "main_ref": "refs/remotes/origin/main"}

    def test_the_old_night_and_today_give_different_sentences(self, mod):
        br = [f"refs/heads/{BRANCH}"]
        old = self._m([br] * 5 + [["refs/heads/main"], ["refs/tags/pre-rewrite-2026-08-27"]])
        today = self._m([br] * 5 + [["refs/tags/pre-rewrite-2026-08-27"]])
        s_old, s_today = mod.attribution(old), mod.attribution(today)
        assert "overstate its contribution by 40.0000%" in s_old, s_old
        assert "1 reachable only from [refs/heads/main]" in s_old, s_old
        assert "overstate its contribution by 20.0000%" in s_today, s_today
        assert "refs/heads/main" not in s_today, s_today
        assert "5 of the 5 are reached by" in s_today, s_today

    def test_a_pin_tag_beside_the_branch_makes_it_not_branch_only(self, mod):
        both = [f"refs/heads/{BRANCH}", f"refs/tags/{mod.PIN_TAG}"]
        s = mod.attribution(self._m([both] * 5))
        assert "0 of the 5 are reached by" in s, s
        assert "None comes from any other ref" in s, s

    def test_the_pinned_measurement_gives_the_pinned_sentence(self, mod, pin):
        s = mod.attribution(pin)
        off, b = pin["off_main"], pin["from_branch"]
        assert f"{off} stored version(s) are off" in s
        assert f"overstate its contribution by {(off - b) / b:.4%}" in s, s


class TestTheRefusal:
    def test_nothing_resolves_exits_4_with_no_numbers_and_writes_nothing(
            self, mod, monkeypatch, capsys, tmp_path):
        out = tmp_path / "sidecar.json"
        monkeypatch.setattr(mod, "live_tips", lambda: {
            "refs/remotes/origin/main": "0" * 40, "HEAD": "0" * 40})
        monkeypatch.setattr(mod, "SIDECAR", out)
        monkeypatch.setattr(mod, "REPO", ROOT)
        rc = mod.main(["--write-sidecar"])
        text = capsys.readouterr().out
        assert rc == mod.EXIT_UNAVAILABLE == 4, rc
        half = text.split(f"--- what {BRANCH} supplies")[1]
        assert "UNAVAILABLE" in half
        assert not re.search(r"\d+/\d+|overstate|%", half), half
        assert not out.exists(), "--write-sidecar wrote a record for an unavailable measurement"

    def test_a_missing_origin_main_also_refuses(self, mod):
        m = mod.measure(tips={f"refs/heads/{BRANCH}": "0" * 40}, targets=[])
        assert m["available"] is False and m["main_ref_present"] is False

    def test_a_failed_git_log_raises_rather_than_reading_as_zero(self, mod):
        with pytest.raises(RuntimeError):
            mod.shas("0" * 40, "bench/runner_core.py")


class TestTheScriptRuns:
    def test_it_reports_both_halves(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert "NONE of these is 21" in r.stdout
        if r.returncode == 4:
            assert "UNAVAILABLE" in r.stdout and "overstate" not in r.stdout
            pytest.skip("the branch resolves from no ref in this clone (exit 4)")
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-400:]
        out = r.stdout

        def num(label: str) -> int:
            mt = re.search(re.escape(label) + r"\s*:\s*(\d+)", out)
            assert mt, f"the run no longer prints {label!r}"
            return int(mt.group(1))

        total = num("stored versions reachable with --all")
        off = num("reachable from no ref on origin/main")
        b = num(f"of those, supplied by {BRANCH}")
        only = num("of those, supplied by it and no other ref")
        rows = re.findall(r"^\s+([B-]) [0-9a-f]{7}  ", out, flags=re.M)
        assert len(rows) == off and rows.count("B") == b, (off, b, rows)
        assert f"{b}/{total} = " in out
        # The attribution sentence must agree with the numbers this run printed.
        assert f"{off} stored version(s) are off" in out
        if b:
            assert f"overstate its contribution by {(off - b) / b:.4%}" in out
        assert f"{only} of the {b} are reached by" in out
