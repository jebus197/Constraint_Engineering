"""Arm 4 has a prose target that actually exercises A19, and its defects are real.

WHY THIS EXISTS. Arm 4 is the arm that COMMISSIONS A19 — the founder's design
point of 2026-09-10, that a purely prose input should be marked inadmissible
*while still solving any computationally reducible elements within that prose*.
The programme of study records that `sk_score_prose_listings=True` is set and
INERT, because `--target` defaults to `bench/dm/_memory.py` and `_gateable_source`
returns Python unchanged. A flag that is set while nothing exercises it reports
"enabled" and proves nothing.

AND THE FOUNDER'S OWN SUGGESTION CANNOT SERVE. He proposed `PAPER.md`:
*"We don't have a prose heavy target that I can readily think of. But how about
the project's own White Paper? That contains many computable elements?"* Measured
2026-10-14: PAPER.md carries 11 fenced blocks and **0 of them contain Python** —
they hold directive text, shorthand lists and mathematical notation such as
`R_k(i) = R_det . (1 - nu_k) + nu_k`. So `_gateable_source` returns None, "target
carries no code", and S_k reaches NO_SCORE. Tagging those fences `python` would
be a falsehood, so tagging is not a repair. cc2's attack on that item succeeds.

WHAT THIS TARGET IS. A short technical note in the house style of
`control_two_distinct_defects.md`: prose claims, each numbered, with 2 carrying a
fenced Python listing that implements them and 1 carrying none. The 2 listings
are DEFECTIVE and their defects are computationally reducible; the third claim is
about presentation and is not. That is precisely the discrimination A19 exists to
make, so the arm can fail in the interesting direction.

THE PLANTED DEFECTS WERE VERIFIED BEFORE BEING PLANTED, each with 2 independent
tools, so the arm cannot be measuring a non-defect:

  PL-01  divides by n while claiming an unbiased variance. SymPy: the bias is
         -sigma2/n for n and exactly 0 for n-1. NumPy over 200,000 draws of 5:
         mean 3.188535 against 3.985669, true sigma2 = 4.0.
  PL-02  uses z**2/n as the Wilson centre instead of z**2/(2n). statsmodels and
         mpmath at 40 dps agree the upper bound is 0.31949990 for 7 of 40; the
         listing returns 0.36331070, an error of 0.04381080.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TARGET = REPO / "bench" / "cdsfl_registry" / "targets" / "prose_with_computable_listings.md"
RUNNER = REPO / "bench" / "reference_runner_v3.py"


def _live_fence_pattern():
    """The runner's OWN pattern, not a copy of it.

    `execute-do-not-grep`: a second regex here would be a producer and a
    consumer that drift, and this project has paid for that 4 times. The
    pattern is lifted out of the live source and compiled.
    """
    src = RUNNER.read_text(encoding="utf-8")
    i = src.index("_MD_PY_FENCE_ANY = re.compile")
    j = src.index("\n\n", i)
    ns: dict = {}
    exec(compile("import re\n" + src[i:j], "<live>", "exec"), ns)
    return ns["_MD_PY_FENCE_ANY"]


@pytest.fixture(scope="module")
def text():
    if not TARGET.is_file():
        pytest.fail(f"arm 4's prose target is missing: {TARGET}")
    return TARGET.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def listings(text):
    return [m.group("body") for m in _live_fence_pattern().finditer(text)]


def test_the_target_is_not_a_python_module(text):
    """It must classify as PROSE, or the prose path is never taken."""
    assert TARGET.suffix == ".md", TARGET.suffix


def test_the_live_extractor_sees_exactly_two_listings(listings):
    assert len(listings) == 2, f"{len(listings)} listing(s) recognised"


def test_both_listings_parse_as_python(listings):
    for i, body in enumerate(listings, 1):
        ast.parse(body)          # raises SyntaxError and fails the test


def test_the_target_also_carries_a_claim_with_no_listing(text):
    """A19's point is the DISCRIMINATION, so an unscoreable claim must be there."""
    claims = re.findall(r"\*\*Claim (PL-\d+)\.\*\*", text)
    assert len(claims) >= 3, claims
    assert "PL-03" in claims
    # PL-03's section must contain no fence.
    seg = text[text.index("PL-03"):]
    seg = seg[:seg.index("## 3.")] if "## 3." in seg else seg
    assert "```" not in seg, "PL-03 must carry no listing"


def test_defect_PL01_is_real(listings):
    """The variance listing must be BIASED, confirmed symbolically and numerically."""
    sympy = pytest.importorskip("sympy")
    np = pytest.importorskip("numpy")
    body = next(b for b in listings if "round_dispersion" in b)
    ns: dict = {}
    exec(compile(body, "<pl01>", "exec"), ns)
    f = ns["round_dispersion"]
    n, s2 = sympy.symbols("n sigma2", positive=True)
    assert sympy.simplify((n - 1) * s2 / n - s2) != 0           # /n is biased
    assert sympy.simplify((n - 1) * s2 / (n - 1) - s2) == 0     # /(n-1) is not
    rng = np.random.default_rng(20261014)
    draws = rng.normal(0.0, 2.0, size=(60000, 5))
    got = np.array([f(list(r)) for r in draws]).mean()
    unbiased = draws.var(axis=1, ddof=1).mean()
    assert got < unbiased - 0.3, (got, unbiased)
    assert abs(got / unbiased - 4 / 5) < 0.02, (got, unbiased)


def test_defect_PL02_is_real(listings):
    """The interval listing must DISAGREE with the reference implementation."""
    sm = pytest.importorskip("statsmodels.stats.proportion")
    mp = pytest.importorskip("mpmath")
    body = next(b for b in listings if "wilson_interval" in b)
    ns: dict = {}
    exec(compile(body, "<pl02>", "exec"), ns)
    f = ns["wilson_interval"]
    k, n = 7, 40
    ref = sm.proportion_confint(k, n, 0.05, method="wilson")
    got = f(k, n)
    assert abs(got[1] - ref[1]) > 1e-3, (got, ref)
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    N, p = mp.mpf(n), mp.mpf(k) / n
    c = p + z ** 2 / (2 * N)
    h = z * mp.sqrt(p * (1 - p) / N + z ** 2 / (4 * N ** 2))
    d = 1 + z ** 2 / N
    assert abs(float((c + h) / d) - ref[1]) < 1e-12      # 2 tools agree on truth
    assert abs(float((c + h) / d) - got[1]) > 1e-3       # and the listing differs


def test_a_correct_listing_would_fail_these_defect_tests(listings):
    """MUTATION-GRADE. If someone silently REPAIRS the target, these tests must
    stop passing -- otherwise the arm would run against a defect-free target and
    report a clean convergence that measured nothing."""
    body = next(b for b in listings if "round_dispersion" in b)
    # ★ THE REPAIR MUST TOUCH ONLY THE RETURN LINE. A first version of this test
    # replaced every "/ n" and so also rewrote `mean = sum(values) / n`, giving
    # 4.0557 against 3.9933 and failing for a reason that had nothing to do with
    # the target. The instrument was wrong, not the thing measured.
    divisor_line = "    return sum((v - mean) ** 2 for v in values) / n"
    assert divisor_line in body, "the defect is not where this test thinks it is"
    repaired = body.replace(divisor_line, divisor_line[:-1] + "(n - 1)")
    assert repaired != body
    ns: dict = {}
    exec(compile(repaired, "<repaired>", "exec"), ns)
    np = pytest.importorskip("numpy")
    rng = np.random.default_rng(7)
    draws = rng.normal(0.0, 2.0, size=(40000, 5))
    got = np.array([ns["round_dispersion"](list(r)) for r in draws]).mean()
    unbiased = draws.var(axis=1, ddof=1).mean()
    assert abs(got - unbiased) < 1e-9, "the repaired listing should be unbiased"


# ─────────── THE TARGET IS WIRED, NOT MERELY PRESENT ───────────
#
# `additive-standard`: "every new flag, gate, subcommand or entry point must be
# wired to a caller and executed by a test". A target file nothing names is an
# unwired addition, and this project's own record counts 11 confirmed defects of
# exactly that shape. These 2 tests are the wiring.

def test_the_simulated_run_names_this_target():
    """The launcher must NAME it, so the operator need not remember which file."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_sim_run", REPO / "bench" / "tools" / "run_simulated_experiment.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "PROSE_TARGET"), \
        "run_simulated_experiment.py must name the prose target"
    assert (REPO / mod.PROSE_TARGET).is_file(), mod.PROSE_TARGET
    assert mod.PROSE_TARGET == str(TARGET.relative_to(REPO)), mod.PROSE_TARGET
    # EXECUTED, not grepped: the parser is built and run on a real argv.
    ns = mod.build_parser().parse_args(["--target", mod.PROSE_TARGET])
    assert ns.target == mod.PROSE_TARGET
    # and the default is still the Python target, so arms 1-3 are untouched
    assert mod.build_parser().parse_args([]).target.endswith(".py")


def test_the_prose_path_engages_on_this_target_and_not_on_the_default():
    """The discriminating property, executed against the LIVE classifier.

    This is the difference the record calls out: a flag being SET versus a
    capability being EXERCISED. On the default .py target `_gateable_source`
    returns the source unchanged; on this target it must extract listings.
    """
    src = RUNNER.read_text(encoding="utf-8")
    i = src.index("def _gateable_source")
    j = src.index("\ndef _gateable_hunks")
    helpers = []
    for name in ("_MD_PY_FENCE_ANY = re.compile", "def _strip_listing_prefix"):
        a = src.index(name)
        b = src.index("\n\n\n", a) if "\n\n\n" in src[a:a + 4000] else src.index("\n\n", a)
        helpers.append(src[a:b])
    ns: dict = {}
    exec(compile("import re\nfrom typing import Optional, Tuple, List\n"
                 + "\n\n".join(helpers) + "\n\n" + src[i:j], "<live>", "exec"), ns)
    gate = ns["_gateable_source"]
    prose_src, prose_reason = gate(TARGET.read_text(encoding="utf-8"), str(TARGET))
    assert prose_src is not None, prose_reason
    assert "listing" in prose_reason, prose_reason
    py = REPO / "bench" / "dm" / "_memory.py"
    if py.is_file():
        py_src, py_reason = gate(py.read_text(encoding="utf-8"), str(py))
        assert py_reason == "python target", py_reason
