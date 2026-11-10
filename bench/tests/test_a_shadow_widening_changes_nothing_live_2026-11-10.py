"""A SHADOW MEASUREMENT MUST NOT TOUCH WHAT IT MEASURES.

B22 asks whether the harness is a general-purpose STEM calculator yet, and
records that 7 of the 29 claims in the project's own STEM corpus reach 0
verification tools. It deliberately proposes NO pattern, because widening
`claim_patterns` changes which claims the LIVE immune pipeline routes to
which tools across 10 domains, and that is the founder's to authorise.

`scripts/what_a_claim_pattern_widening_would_route_2026-11-10.py` produces
the evidence that decision needs WITHOUT taking it: it applies candidate
patterns to in-memory COPIES and reports what would route differently. This
file pins the 3 properties that make such a producer trustworthy.

1. IT CHANGES NOTHING. The domain config files are digested before and after
   and must be byte-identical. "It only edits a copy" is a claim about code;
   this measures it.

2. IT REPORTS THE RISK SIDE, NOT ONLY THE GAIN. A widening has 2 directions.
   The gain is claims that reach no tool and would reach one. The risk is
   claims that route correctly today and would be pulled to a DIFFERENT
   claim type, hence a different tool set. A gain-only measurement cannot see
   the second, and a decision offered on half a measurement is a decision
   made for him.

3. ITS INPUT IS THE CLAIM, NOT THE CLAIM'S REPR. A corpus `Claim` carries
   tag, verdict, summary, anchor and note. A fallback chain ending in
   `str(c)` silently yields the whole dataclass repr, note included, and the
   note is full of operators -- so every claim classifies and the defect
   vanishes. Measured both ways on 2026-11-10: the summary routes 22 of 29,
   the repr routes 29 of 29. That near-miss nearly produced a false
   correction to a committed figure, so the input is pinned here.
"""
import hashlib
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / \
    "what_a_claim_pattern_widening_would_route_2026-11-10.py"
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(scope="module")
def prod():
    spec = importlib.util.spec_from_file_location("_shadow_w", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_shadow_w"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def configs():
    import domain_immune as di
    return di, di.load_all_domain_configs()


class TestItChangesNothingLive:
    def test_the_domain_configs_are_byte_identical_after_a_run(self):
        import domain_immune as di
        d = pathlib.Path(getattr(di, "_DOMAINS_DIR"))
        assert d.is_dir(), "the domain config directory moved; this guard is blind"
        before = {f: hashlib.sha256(f.read_bytes()).hexdigest()
                  for f in sorted(d.rglob("*")) if f.is_file()}
        assert before, "no domain config files found; nothing to protect"
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=str(REPO),
                           timeout=600)
        assert r.returncode == 0, r.stdout[-1500:]
        changed = [str(f) for f, h in before.items()
                   if not f.is_file()
                   or hashlib.sha256(f.read_bytes()).hexdigest() != h]
        assert changed == [], (
            f"a SHADOW measurement rewrote {len(changed)} live config "
            f"file(s): {changed}. It must apply candidates to copies only.")

    def test_the_shadow_helper_does_not_mutate_its_input(self, prod, configs):
        """The property at the function level, so a caller cannot rely on
        luck. `_shadow` deep-copies; this asserts the original is unchanged
        and that the copy genuinely differs."""
        di, cfgs = configs
        cfg = cfgs["cs_software"]
        before = {k: list(v) for k, v in
                  (getattr(cfg, "claim_patterns", None) or {}).items()}
        sh = prod._shadow(cfg, prod.CANDIDATES["cs_software"])
        after = {k: list(v) for k, v in
                 (getattr(cfg, "claim_patterns", None) or {}).items()}
        assert after == before, "_shadow mutated the config it was given"
        assert sh is not cfg
        assert (getattr(sh, "claim_patterns") !=
                getattr(cfg, "claim_patterns")), (
            "the shadow copy is identical to the live config, so the "
            "measurement compares a thing with itself")


class TestItReportsBothDirections:
    def test_the_output_names_the_gain_and_the_risk(self):
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=str(REPO),
                           timeout=600)
        assert r.returncode == 0, r.stdout[-1200:]
        for needed in ("GAINED", "MOVED", "LOST", "the risk side"):
            assert needed in r.stdout, (
                f"the producer no longer reports {needed!r}, so the decision "
                f"would rest on half a measurement")

    def test_it_recommends_nothing(self):
        """B22 holds that the widening is his to authorise. A producer that
        quietly recommended one would be taking the decision from a
        measurement, which is what `p-pass-high-consequence-check` forbids."""
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=str(REPO),
                           timeout=600)
        assert "NOT recommended" in r.stdout, (
            "the producer now carries a recommendation; the claim-pattern "
            "widening changes live routing across 10 domains and is his")


class TestTheInputIsTheClaimNotItsRepr:
    def test_claim_text_reads_the_summary(self, prod):
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "_fx_in", REPO / "bench" / "tests" / "fixtures" / "stem"
            / "stem_fixtures.py")
        fx = ilu.module_from_spec(spec)
        sys.modules["_fx_in"] = fx
        spec.loader.exec_module(fx)
        c = fx.FIXTURES[0].claims[0]
        got = prod.claim_text(c)
        assert got == c.summary, f"claim_text returned {got[:60]!r}"
        #: THE DISCRIMINATING ASSERTION: the repr must NOT be what is read.
        assert "note=" not in got and "verdict=" not in got, (
            "claim_text is returning the dataclass repr, which carries the "
            "note and anchor. The note is full of operators, so every claim "
            "classifies and the routing defect disappears: 29 of 29 instead "
            "of 22 of 29.")

    def test_the_two_inputs_genuinely_differ(self, prod, configs):
        """ANTI-VACUITY for the test above: if summary and repr routed the
        same way, pinning the input would protect nothing."""
        import importlib.util as ilu
        di, cfgs = configs
        spec = ilu.spec_from_file_location(
            "_fx_in2", REPO / "bench" / "tests" / "fixtures" / "stem"
            / "stem_fixtures.py")
        fx = ilu.module_from_spec(spec)
        sys.modules["_fx_in2"] = fx
        spec.loader.exec_module(fx)

        class V:
            def __init__(self, d):
                self.description = d

        counts = []
        for pick in (lambda c: c.summary, lambda c: str(c)):
            routed = 0
            for f in fx.FIXTURES:
                cfg = cfgs[prod.CORPUS_DOMAIN[f.domain]]
                for c in f.claims:
                    k, _ = di.domain_classify_claim(V(pick(c)), cfg)
                    routed += bool(di.domain_b_cell_tools(k, cfg) or [])
            counts.append(routed)
        assert counts[0] < counts[1], (
            f"the summary and the repr route the same number of claims "
            f"({counts}), so the input no longer changes the answer and this "
            f"pin has gone vacuous")
