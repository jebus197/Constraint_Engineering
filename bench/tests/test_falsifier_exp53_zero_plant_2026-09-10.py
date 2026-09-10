"""Task 2.2: the 11 exp53 falsifiers, and the false-positive measurement they are.

EXP 53 IS THE ZERO-PLANT CONTROL, and its pre-registration says what these
findings are for, verbatim: "FALSE-POSITIVE RATE = findings raised against true
claims divided by 44, the only clean estimate available anywhere in the
programme". The document `SW-21-REF-04.md` carries 44 numbered claims, ZC-01
through ZC-44, and nothing planted in it.

11 critical findings were raised against it and every one was recorded
`UNTOOLABLE` with an empty `falsifier_code`. Writing their falsifiers IS the
measurement the control exists to produce, so this file adjudicates each against
the document rather than against the models.

THE VERDICT, AND IT IS ONE MECHANISM REPEATED. Every claim in that document names
the scope it is asserted over -- "under single-threaded use", "with non-negative
costs", "unit-cost requests" -- and the findings are raised by stepping outside
it. The claims are TRUE AS STATED. The code behaviours the findings describe are
REAL. Both of those hold at once, and neither cancels the other.

PER FINDING:

* C0003 (ChatGPT 0.86) and C0031 (Codex 0.80): "Listing A mutates shared state
  without a lock". ZC-26 says exactly this, at length, with its own instrumented
  demonstration. C0003's own text concedes it -- "The document itself later
  states this in ZC-26". A finding that restates a claim the document makes.
* C0001 (Codex 0.78 and 0.85): negative and fractional costs break the token
  invariant. ZC-14 is scoped "with non-negative costs" and ZC-12 to "unit-cost
  requests". The behaviour is real -- allow(-5.0) on a drained 1-token bucket
  returns True and leaves tokens at 5.0 -- and it contradicts neither claim.
* C0005 (ChatGPT 0.78): "ZC-20 incorrectly states that the retry schedule never
  shortens". ZC-20 SAYS THE OPPOSITE: "the sampled delays are not ordered, since
  each is drawn uniformly below its own cap". The phrase "never shortens" does
  not occur in it. A finding against a claim the document does not make.
* C0004, C0012, C0032 (0.78 to 0.85): topo_order returns a partial order on a
  cyclic graph instead of raising. ZC-19 documents that postcondition precisely.
  Preferring an exception is a design view, not a contradiction.
* C0007 (Gemini 0.80): locate should use bisect_left rather than bisect_right.
  A real convention point with NO measured effect: the 2 functions disagree on 0
  of 262,144 keys, Wilson [0.00000000%, 0.00146538%]. ZC-17's actual claim is
  that the subscript stays in range, and it does.
* C0014 (ChatGPT 0.72) and C0023 (CC2 0.74): input validation on backoff_delay,
  and dict-keyed collapse in topo_order. Same shape -- behaviour outside the
  stated scope.

WHAT THIS IS NOT. It is not a finding that the panel performed badly. Every one
of these describes real code behaviour, and several would be worth fixing in
production software. What the control measures is the STOPPING DECISION, and on
a document where every claim is true the panel kept producing critical findings
by widening the scope of the claims until something failed.
"""
from __future__ import annotations

import bisect
import hashlib
import pathlib
import random
import time

import pytest

TARGET = pathlib.Path(
    "/Users/georgejackson/CDSFL_review_targets/current/SW-21-REF-04.md")

#: The pre-registration's denominator: the document's numbered claims.
DECLARED_CLAIMS = 44

#: The 11 critical findings with no falsifier, and what each turned out to be.
ADJUDICATION = {
    "C0003": "restates ZC-26", "C0031": "restates ZC-26",
    "C0001a": "outside ZC-14's non-negative scope",
    "C0001b": "outside ZC-14's non-negative scope",
    "C0005": "misquotes ZC-20",
    "C0004": "ZC-19 documents it", "C0012": "ZC-19 documents it",
    "C0032": "ZC-19 documents it",
    "C0007": "convention, 0 keys affected",
    "C0014": "outside ZC-20's postcondition",
    "C0023": "outside ZC-18's scope",
}


@pytest.fixture(scope="module")
def doc():
    if not TARGET.is_file():
        pytest.skip("the exp53 zero-plant target is not on this machine")
    return TARGET.read_text(encoding="utf-8")


class TokenBucket:
    """Listing A, copied verbatim from the target so the test executes IT."""

    def __init__(self, capacity, refill_per_sec):
        self.capacity = float(capacity)
        self.rate = float(refill_per_sec)
        self.tokens = float(capacity)
        self.last = time.monotonic()

    def allow(self, cost=1.0):
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class TestTheDocumentIsWhatTheFindingsAttack:
    def test_it_carries_the_declared_number_of_claims(self, doc):
        n = doc.count("**ZC-")
        assert n == DECLARED_CLAIMS, (
            f"the document now carries {n} claims, not the {DECLARED_CLAIMS} the "
            f"pre-registration uses as the false-positive denominator")

    def test_the_claims_name_their_own_scope(self, doc):
        """The mechanism behind every one of these findings."""
        for phrase in ("Under single-threaded use", "with non-negative costs",
                       "unit-cost requests"):
            assert phrase in doc, (
                f"{phrase!r} is gone; the claims no longer name their scope and "
                f"the adjudication below would have to be redone")


class TestZC14IsTrueAsStated:
    def test_no_violation_within_the_scope_it_names(self):
        """ZC-14's own evidence, reproduced: 120,000 calls, no violation."""
        random.seed(7)
        b = TokenBucket(240, 60)
        n, viol = 120_000, 0
        for _ in range(n):
            b.allow(random.choice([0.0, 0.5, 1.0, 2.0, 7.5]))   # non-negative
            if not (-1e-9 <= b.tokens <= b.capacity + 1e-9):
                viol += 1
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(viol, n, method="wilson")
        assert viol == 0, f"ZC-14 is violated {viol} times in its own scope"
        assert hi < 1e-4, (lo, hi)

    def test_the_findings_case_is_real_AND_out_of_scope(self):
        """Both halves. Denying either would be the dishonest report."""
        b = TokenBucket(1, 0)
        assert b.allow(1.0) is True
        assert b.tokens == 0.0
        assert b.allow(-5.0) is True, "negative cost no longer admits"
        assert b.tokens > b.capacity, (
            "the negative-cost path no longer pushes tokens above capacity, so "
            "the finding's behaviour claim is stale")


class TestC0005MisquotesTheClaimItAttacks:
    def test_zc20_does_not_say_what_the_finding_says_it_says(self, doc):
        i = doc.find("**ZC-20.**")
        assert i > 0, "ZC-20 is gone from the document"
        zc20 = doc[i:doc.find("\n", i)]
        assert "never shortens" not in zc20, (
            "ZC-20 now contains the phrase the finding quotes, so C0005 would be "
            "a fair reading after all")
        assert "not ordered" in zc20, (
            "ZC-20 no longer states that the sampled delays are unordered")


class TestC0007HasNoMeasuredEffect:
    def test_the_two_bisects_agree_on_every_key_in_the_fleet(self):
        pts = sorted((int.from_bytes(hashlib.blake2b(
            f"dist-{i:02d}#{j}".encode(), digest_size=8).digest(), "big"),
            f"dist-{i:02d}") for i in range(24) for j in range(128))
        keys = [p[0] for p in pts]
        assert len(pts) == 3072, "the ring size no longer matches ZC-03"
        n, diff = 262_144, 0
        for k in range(n):
            h = int.from_bytes(hashlib.blake2b(
                f"node-{k:06d}".encode(), digest_size=8).digest(), "big")
            if bisect.bisect_right(keys, h) != bisect.bisect_left(keys, h):
                diff += 1
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(diff, n, method="wilson")
        assert diff == 0, (
            f"the 2 bisects now disagree on {diff} keys, so C0007 has a "
            f"measurable effect and its verdict should be revisited")
        assert hi < 1e-4, (lo, hi)


class TestTheRateIsReportedWithItsScope:
    def test_every_finding_is_adjudicated(self):
        assert len(ADJUDICATION) == 11, (
            f"{len(ADJUDICATION)} findings adjudicated, not 11; the population "
            f"changed and the rate below is over the wrong denominator")

    def test_the_rate_carries_an_interval(self):
        """11 of 44 claims drew a critical finding that contradicts none of them."""
        from statsmodels.stats.proportion import proportion_confint
        k, n = len(ADJUDICATION), DECLARED_CLAIMS
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, k, n - k + 1)
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert 0.1 < k / n < 0.5, k / n
        assert lo > 0.1 and hi < 0.5, (lo, hi)
