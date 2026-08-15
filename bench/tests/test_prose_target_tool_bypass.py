"""A6: the Python-only code tools are bypassed on a prose target.

THE DEFECT
----------
Five B-Cell specialist verifiers take a file PATH and hand it to a tool that
assumes the path is Python source: mypy, ruff, bandit, dis, crosshair. The
router at `_specialist_b_cell_dispatch` passed `finding.target_file` straight
through with no check on what kind of file it was.

Handed a markdown document none of the five refuse. Three of them ANSWER, and
answer definitively. Measured on this machine, 2026-08-01, and re-measured by
the first three tests below with the guard disabled:

    ruff      declines the non-.py path, exits 0, prints "All checks passed!"
              -> the wrapper counts that line as a violation
              -> CONFIRMED, confidence 0.80
    bandit    cannot parse it, files that under "errors", returns results=[]
              and exits 0 -> SEC_CLEAN -> REJECTED, confidence 0.75
    mypy      parses the prose as source, reports "Leading zeros in decimal
              integer literals" -> TYPE_ERROR -> CONFIRMED, confidence 0.85
    dis       SyntaxError -> UNCERTAIN
    crosshair ModuleNotFoundError -> UNCERTAIN

So on every prose target, every code-quality and every type finding was
silently CONFIRMED by a tool that never read the file, and every security
finding was REJECTED by a tool that returned an empty result set because it
could not parse it. None of that appears anywhere as an error. It appears as
verification.

A SECOND DEFECT, FOUND HERE AND LEFT ALONE
------------------------------------------
The ruff reading above is not really about prose. `_verify_lint_check` treats
every non-blank line of ruff's stdout as a violation, and ruff prints "All
checks passed!" on success — so the wrapper returns CONFIRMED at 0.80 for a
CLEAN Python file as well, and its LINT_CLEAN branch is unreachable. That is
a live defect on the cs_software domain, which is in LIVE_SPECIALIST_DOMAINS
and routes code_structural to lint_check. It is out of scope for A6 and is
reported, not changed here: altering a verifier's verdict on the Python path
is a change to the experiments that already converged.

THE FIX
-------
The target-type check happens BEFORE the tool is invoked, in code, at two
levels — the router and each verifier — and reports NOT_APPLICABLE: a verdict
string that is neither a pass nor a fail, carries zero confidence, and
contributes zero weight to every consensus path in the module.

Not in a config file. The launcher has silently dropped config keys six
times, and a dropped target-type declaration would put mypy straight back on
the markdown.

WHAT THESE TESTS PIN
--------------------
  * the defect is real (guard disabled -> the three false verdicts reappear);
  * with the guard, all five report NOT_APPLICABLE and do not run;
  * the router bypasses them and says so, without disturbing the non-file
    tools or the Python path;
  * NOT_APPLICABLE cannot become a rejection or a confirmation downstream;
  * a file tool added to the manifest in future without a guard fails a test.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import bench.immune_agents as ia  # noqa: E402
from bench.dm._types import Finding  # noqa: E402
from bench.immune_agents import (  # noqa: E402
    NOT_APPLICABLE_VERDICT,
    CellType,
    ClaimType,
    TriagedFinding,
    _PYTHON_ONLY_FILE_TOOLS,
    _specialist_b_cell_dispatch,
    _verify_bytecode_analysis,
    _verify_lint_check,
    _verify_security_scan,
    _verify_symbolic_execution,
    _verify_type_check,
    helper_t_cell_synthesize,
    helper_t_v2,
)

# The shape of an Exp 48-53 target: claims in prose, code in fences. The
# "032" is not decoration — it is the token that makes mypy report a syntax
# error, which is what the wrapper reads as a confirmed type finding.
DOC = """# Reference SW-21-REF-04

**ZC-01.** Offsets are 032 and 0100 in the table; the retry budget is 3.

```python
import subprocess

def run(cmd):
    return subprocess.call(cmd, shell=True)
```
"""

CLAIM = "the retry budget is 3 attempts, not 4"


@pytest.fixture
def prose(tmp_path):
    p = tmp_path / "SW-21-REF-04.md"
    p.write_text(DOC, encoding="utf-8")
    return str(p)


@pytest.fixture
def pysrc(tmp_path):
    p = tmp_path / "target.py"
    p.write_text("def f(a: int) -> int:\n    return a + 1\n", encoding="utf-8")
    return str(p)


def _finding(fid="C0031", target_file="", desc=CLAIM) -> Finding:
    return Finding(
        finding_id=fid, model_id="CC2", round_idx=0, flaw_class=2,
        severity=0.8, abstraction_index=0.5, description=desc,
        target_file=target_file,
    )


def _triaged(target_file, claim_type=ClaimType.CODE_STRUCTURAL, fid="C0031"):
    return TriagedFinding(
        finding=_finding(fid=fid, target_file=target_file),
        claim_type=claim_type,
        extracted_claim=CLAIM,
    )


@pytest.fixture
def guard_disabled(monkeypatch):
    """Reverts A6 in-process, to re-measure what it prevents."""
    monkeypatch.setattr(ia, "is_python_target", lambda _p: True)


# ═══════════════════════════════════════════════════════════════════════════
# 1. The defect is real — the same tests, with the guard reverted
# ═══════════════════════════════════════════════════════════════════════════


class TestTheDefectIsReal:
    """Each of these FAILS to be alarming only because the guard is off.

    If one of them ever stops reproducing, the tool's own behaviour changed
    and the corresponding claim in the source comments is stale — fix the
    comment, do not delete the guard.
    """

    def test_without_the_guard_ruff_decides_a_finding_it_never_read(
            self, prose, guard_disabled):
        """RE-MEASURED 2026-08-01 23:15, exactly as this test instructed.

        It originally asserted CONFIRMED, and named the mechanism: ruff declines
        the .md path and prints "All checks passed!", and the wrapper counted
        that success line as a violation. It carried its own instruction — "if
        this stops holding, _verify_lint_check's stdout parsing was fixed and
        this test should be re-measured, not deleted". The B3 repair
        (immune_agents.py, 2026-08-01) fixed exactly that parsing, so the
        direction has moved: rc==0 now reads as clean, and the verdict is
        REJECTED rather than CONFIRMED.

        That is not a smaller defect, only a differently-signed one. Before, a
        tool that never opened the document voted to CONFIRM the finding and
        inflated its severity. Now it votes to DISMISS it. The property this
        test exists to pin is unchanged and is the one that matters: with the
        A6 guard removed, a tool that did not read the document still returns a
        DEFINITIVE verdict on it, at high confidence.

        The guard is what prevents both signs. It is on in every real run; this
        test removes it deliberately to measure what it is worth.
        """
        v = _verify_lint_check(CLAIM, prose)
        assert v.verdict in ("CONFIRMED", "REJECTED"), (
            "the defect is a DEFINITIVE verdict from a tool that never read the "
            f"document — either sign. Got {v.verdict}: {v.evidence[:200]}")
        assert v.verdict != "UNCERTAIN", (
            "UNCERTAIN would mean the wrapper had noticed it learned nothing; "
            "it has not, and that is the point of the guard")
        assert v.confidence >= 0.7, (
            "and it is not hedged — it is asserted at high confidence")
        assert "LINT_CLEAN" in v.evidence, (
            "post-B3 the verdict is built from ruff's rc==0, which on a .md "
            "path means 'I found no Python files to check', not 'this document "
            "is clean'. If this stops holding, re-measure again — do not "
            "delete the guard")

    def test_without_the_guard_bandit_rejects_a_finding_it_never_read(
            self, prose, guard_disabled):
        v = _verify_security_scan(CLAIM, prose)
        assert v.verdict == "REJECTED", (
            "expected the measured defect: bandit returns results=[] on a file "
            f"it cannot parse. Got {v.verdict}: {v.evidence[:200]}")
        assert v.confidence >= 0.7

    def test_without_the_guard_mypy_confirms_a_finding_from_a_paragraph(
            self, prose, guard_disabled):
        v = _verify_type_check(CLAIM, prose)
        assert v.verdict == "CONFIRMED", (
            "expected the measured defect: mypy parses prose as source and "
            f"reports a syntax error. Got {v.verdict}: {v.evidence[:200]}")
        assert "Leading zeros" in v.evidence or "syntax" in v.evidence.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 2. With the guard: bypassed, and said out loud
# ═══════════════════════════════════════════════════════════════════════════


_FILE_VERIFIERS = [
    ("mypy", _verify_type_check),
    ("ruff", _verify_lint_check),
    ("bandit", _verify_security_scan),
    ("dis", _verify_bytecode_analysis),
    ("crosshair", _verify_symbolic_execution),
]


class TestEachVerifierBypasses:

    @pytest.mark.parametrize("tool,fn", _FILE_VERIFIERS,
                             ids=[t for t, _ in _FILE_VERIFIERS])
    def test_verdict_is_not_applicable(self, tool, fn, prose):
        v = fn(CLAIM, prose)
        assert v.verdict == NOT_APPLICABLE_VERDICT, (
            f"{tool} must report NOT_APPLICABLE on a prose target, not "
            f"{v.verdict}")

    @pytest.mark.parametrize("tool,fn", _FILE_VERIFIERS,
                             ids=[t for t, _ in _FILE_VERIFIERS])
    def test_it_is_neither_a_pass_nor_a_fail(self, tool, fn, prose):
        v = fn(CLAIM, prose)
        assert v.verdict not in ("CONFIRMED", "REJECTED", "DUPLICATE"), (
            f"{tool} produced a decision about a file it cannot read")
        assert v.confidence == 0.0

    @pytest.mark.parametrize("tool,fn", _FILE_VERIFIERS,
                             ids=[t for t, _ in _FILE_VERIFIERS])
    def test_the_tool_did_not_run(self, tool, fn, prose):
        """Bypassed, not invoked-and-second-guessed. crosshair alone costs
        seconds per call; on a 300-finding round that is the whole budget."""
        v = fn(CLAIM, prose)
        assert v.elapsed_s == 0.0
        assert "not_applicable" in v.tool_used

    @pytest.mark.parametrize("tool,fn", _FILE_VERIFIERS,
                             ids=[t for t, _ in _FILE_VERIFIERS])
    def test_it_names_the_target_and_the_reason(self, tool, fn, prose):
        v = fn(CLAIM, prose)
        assert "SW-21-REF-04.md" in v.evidence
        assert "not a Python source file" in v.evidence

    def test_a_missing_path_still_reads_as_uncertain_not_not_applicable(self):
        """Deliberate boundary. 'No target was supplied' is a different
        statement from 'the target is the wrong kind', and the existing
        UNCERTAIN reading of the first one is truthful."""
        v = _verify_lint_check(CLAIM, "")
        assert v.verdict == "UNCERTAIN"
        assert "no valid file_path" in v.evidence

    @pytest.mark.parametrize("tool,fn", _FILE_VERIFIERS,
                             ids=[t for t, _ in _FILE_VERIFIERS])
    def test_a_python_target_is_untouched(self, tool, fn, pysrc):
        v = fn(CLAIM, pysrc)
        assert v.verdict != NOT_APPLICABLE_VERDICT, (
            f"{tool} must still run on real Python — this change must be "
            "invisible to the code experiments")


# ═══════════════════════════════════════════════════════════════════════════
# 3. The router — where A6 is actually specified
# ═══════════════════════════════════════════════════════════════════════════


_CFG_FILE_TOOLS = {
    "immune": {
        "verification_tools": {
            "code_structural": ["type_checker", "lint_check"],
            "code_behavioral": ["security_scan", "symbolic_execution"],
        },
    },
}


class TestRouterBypassesOnProse:

    def test_no_definitive_verdict_survives_a_prose_target(self, prose):
        verdicts = _specialist_b_cell_dispatch([_triaged(prose)], _CFG_FILE_TOOLS)
        assert verdicts, "the bypass must be reported, not swallowed"
        for v in verdicts:
            assert v.verdict == NOT_APPLICABLE_VERDICT, (
                f"router let {v.tool_used} decide on a prose target: "
                f"{v.verdict}")

    def test_every_configured_file_tool_is_accounted_for(self, prose):
        verdicts = _specialist_b_cell_dispatch([_triaged(prose)], _CFG_FILE_TOOLS)
        tools = {v.tool_used for v in verdicts}
        assert tools == {"mypy:not_applicable", "ruff:not_applicable"}, (
            "each bypassed tool gets its own record, so the report shows what "
            f"was not done. Got {tools}")

    def test_the_records_carry_the_finding_id(self, prose):
        verdicts = _specialist_b_cell_dispatch([_triaged(prose)], _CFG_FILE_TOOLS)
        assert all(v.finding_id == "C0031" for v in verdicts)
        assert all(v.cell_type == CellType.B_CELL for v in verdicts)

    def test_a_python_target_still_gets_its_tools_run(self, pysrc):
        verdicts = _specialist_b_cell_dispatch([_triaged(pysrc)], _CFG_FILE_TOOLS)
        assert verdicts
        assert not any(v.verdict == NOT_APPLICABLE_VERDICT for v in verdicts), (
            "the Python path must be untouched by A6")

    def test_non_file_tools_are_unaffected_by_a_prose_target(self, prose):
        """sympy does not read the target file, so a .md target is irrelevant
        to it. Bypassing on target type must not disable the tools that can
        still decide a prose claim — those are the ones Exp 48 and 49
        converged on."""
        tf = TriagedFinding(
            finding=_finding(fid="M1", target_file=prose, desc="sqrt(4) = 3"),
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="sqrt(4) = 3",
        )
        cfg = {"immune": {"verification_tools": {"mathematical": ["sympy"]}}}
        verdicts = _specialist_b_cell_dispatch([tf], cfg)
        assert verdicts
        assert verdicts[0].verdict in ("CONFIRMED", "REJECTED", "UNCERTAIN")
        assert verdicts[0].verdict != NOT_APPLICABLE_VERDICT

    def test_a_substantive_verdict_still_comes_first(self, prose):
        """Existing callers read verdicts[0]. A bypass record must not
        displace the tool that actually looked."""
        cfg = {"immune": {"verification_tools": {
            "mathematical": ["sympy", "type_checker"]}}}
        tf = TriagedFinding(
            finding=_finding(fid="M2", target_file=prose, desc="2 + 2 = 4"),
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="2 + 2 = 4",
        )
        verdicts = _specialist_b_cell_dispatch([tf], cfg)
        assert verdicts[0].verdict != NOT_APPLICABLE_VERDICT


# ═══════════════════════════════════════════════════════════════════════════
# 4. NOT_APPLICABLE cannot turn into a decision downstream
# ═══════════════════════════════════════════════════════════════════════════


class TestItCannotBecomeAVerdict:

    def test_helper_t_v1_leaves_such_a_finding_uncertain(self, prose):
        tf = _triaged(prose)
        verdicts = _specialist_b_cell_dispatch([tf], _CFG_FILE_TOOLS)
        final, conf = helper_t_cell_synthesize([tf], verdicts)
        assert final["C0031"] == "UNCERTAIN", (
            "a finding whose only verdicts are 'the tool could not read this' "
            f"must stay undecided, got {final['C0031']}")
        assert conf["C0031"] == 0.0

    def test_helper_t_v2_leaves_such_a_finding_uncertain(self, prose):
        tf = _triaged(prose)
        verdicts = _specialist_b_cell_dispatch([tf], _CFG_FILE_TOOLS)
        final, _ = helper_t_v2([tf], verdicts)
        assert final["C0031"] == "UNCERTAIN"

    def test_it_cannot_outweigh_a_tool_that_did_look(self, prose):
        """Zero confidence, so a real reading always wins the aggregation."""
        tf = _triaged(prose)
        na = _specialist_b_cell_dispatch([tf], _CFG_FILE_TOOLS)
        real = ia.CellVerdict(
            cell_type=CellType.CYTOTOXIC_T, finding_id="C0031", verdict="CONFIRMED",
            confidence=0.8, evidence="falsifier: computed value differs",
            tool_used="falsifier", elapsed_s=1.0,
        )
        final, _ = helper_t_cell_synthesize([tf], na + [real])
        assert final["C0031"] == "CONFIRMED"


# ═══════════════════════════════════════════════════════════════════════════
# 5. A future file tool cannot be added without a guard
# ═══════════════════════════════════════════════════════════════════════════


class TestTheGuardCoversTheWholeManifest:

    def test_every_file_based_tool_is_listed_as_python_only(self):
        manifest = ia._load_tool_manifest()
        assert manifest, "tool manifest must load"
        needs_file = {n for n, e in manifest.items() if e.get("needs_file")}
        missing = needs_file - set(_PYTHON_ONLY_FILE_TOOLS)
        assert not missing, (
            f"file-based tools absent from _PYTHON_ONLY_FILE_TOOLS: {missing}. "
            "Every tool that takes a path must declare whether it can read "
            "anything other than Python.")

    def test_every_file_based_verifier_checks_the_target_type(self):
        manifest = ia._load_tool_manifest()
        unguarded = []
        for name, entry in manifest.items():
            if not entry.get("needs_file"):
                continue
            fn = getattr(ia, entry["verifier"], None)
            assert fn is not None, f"{name}: verifier {entry['verifier']} missing"
            if "is_python_target" not in inspect.getsource(fn):
                unguarded.append(f"{name} -> {entry['verifier']}")
        assert not unguarded, (
            "file-based verifiers with no target-type guard: "
            f"{unguarded}. The router guard alone is not enough — these are "
            "called directly elsewhere.")

    def test_the_router_guards_before_it_dispatches(self):
        src = inspect.getsource(_specialist_b_cell_dispatch)
        i = src.index('if entry.get("needs_file"):')
        j = src.index("v = verifier_fn(tf.extracted_claim, target_file)", i)
        assert "is_python_target" in src[i:j], (
            "the target-type check must sit between the needs_file branch and "
            "the call, so the tool is never invoked on a target it cannot read")
