# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_proof_and_weight_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 348bf0e39c6f2df2c445dada58486bea8abc00cd96afafb180073bb27926bc63
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Guards for the joint round `severity_proof_and_weight_2026-11-14`.

Each test pins a fact the two blind seats DISAGREED about, so that the
resolution is executed rather than remembered. Every one reads the live
modules; none re-types a formula under test.
"""
import inspect

import pytest

import bench.audit_closing_window as acw
import bench.convergence_location as cl
import bench.evidence as ev
from bench.reference_runner_v3 import (
    CRITICAL_SEVERITY_THRESHOLD,
    SEV_F_W,
    _is_demotion_eligible,
    compute_sev_f,
)

REPO_TOML = "bench/cdsfl_registry/domain_manifest.toml"


def _spellings():
    """Every spelling of the frozen cut OUTSIDE the canonical constant.

    Read by IMPORT and `inspect.signature`, never by text search: a parameter
    DEFAULT is invisible to a search for an assignment, which is how the
    round's brief came to say four when there are six.
    """
    out = [("bench/evidence.py::LEDGER_CRITICAL_SEVERITY",
            ev.LEDGER_CRITICAL_SEVERITY),
           ("bench/audit_closing_window.py::CRITICAL_SEVERITY_THRESHOLD",
            acw.CRITICAL_SEVERITY_THRESHOLD)]
    for name, fn in sorted(inspect.getmembers(cl, inspect.isfunction)):
        p = inspect.signature(fn).parameters.get("critical_threshold")
        if p is not None and p.default is not inspect.Parameter.empty:
            out.append(("bench/convergence_location.py::%s" % name, p.default))
    return out


def test_every_spelling_of_the_critical_cut_matches_the_runner():
    """No duplicate spelling of the cut may drift from the canonical constant.

    Enumerated rather than listed, so a spelling added later is caught without
    editing this test.
    """
    drifted = [(n, v) for n, v in _spellings()
               if v != CRITICAL_SEVERITY_THRESHOLD]
    assert not drifted, (
        "these spellings of the critical cut have drifted from "
        "reference_runner_v3.CRITICAL_SEVERITY_THRESHOLD=%r: %r"
        % (CRITICAL_SEVERITY_THRESHOLD, drifted))


def test_there_are_six_spellings_not_four():
    """The round's brief says four. Measured by import, there are six.

    `convergence_location` carries `critical_threshold=0.7` on FOUR functions,
    not two. This is a floor, not an equality: a NEW spelling should make the
    count rise and should be pinned by the test above, not forbidden here.
    """
    assert len(_spellings()) >= 6, (
        "expected at least the six known spellings, found %d: %r"
        % (len(_spellings()), _spellings()))


def test_the_three_proof_call_sites_do_not_share_one_population():
    """`severity_is_proven`'s call sites split the registry, they do not share it.

    Sites A (A4 release door) and B (reasoned withdrawal) are each conjoined
    with `severity < CRITICAL_SEVERITY_THRESHOLD`. Site C (calibration
    demotion) runs only where `_is_demotion_eligible` holds, and that predicate
    REQUIRES `severity >= CRITICAL_SEVERITY_THRESHOLD`. The two populations are
    therefore disjoint and complementary, which is why no single percentage is
    "the door-relevant figure".
    """
    base = {"falsifier_verdict": "CONFIRMED", "latent": True,
            "finding_category": "performance"}
    below = dict(base, severity=CRITICAL_SEVERITY_THRESHOLD - 0.01)
    at_or_above = dict(base, severity=CRITICAL_SEVERITY_THRESHOLD)

    assert not _is_demotion_eligible(below), (
        "site C must not reach an entry below the cut -- if it does, the "
        "populations overlap and the two-figure report is wrong")
    assert _is_demotion_eligible(at_or_above), (
        "site C must reach an entry at or above the cut")


def test_the_credence_coordinate_is_not_a_function_of_the_evidence_alone():
    """RECORDED DEFECT, not a desired property.

    Appendix section 7.7.1 defines `severity_d(f) = ( c_d(f) , credence(f) )`
    with `credence(f)` being section 7.7's product, `W(class) * confidence *
    Ver`. `W` is keyed on CONSTRAINT CLASS -- the core directives' section 1
    CONSEQUENCE partition. So two findings with identical evidence receive
    different "credence" solely because one concerns a safety constraint.

    ★ WHEN `W` LEAVES THE CREDENCE COORDINATE, THIS TEST MUST BE INVERTED, NOT
    DELETED: change the assertion to `hard == soft` and keep it. It exists to
    make the repair visible in the diff, and deleting it would hide exactly the
    change it was written to expose.
    """
    assert set(SEV_F_W) == {"HARD", "SOFT"}, (
        "this guard is written against the two-weight table; re-derive it if "
        "the table changes")
    differing = [(c, v) for c in (0.9, 0.6, 0.3)
                 for v in ("CONFIRMED", "UNTOOLABLE")
                 if compute_sev_f("HARD", c, v) != compute_sev_f("SOFT", c, v)]
    assert len(differing) == 6, (
        "expected all six (confidence, verdict) cells to show the credence "
        "coordinate varying with CONSEQUENCE class; got %r" % (differing,))


def test_a_third_weight_changes_a_lexicographic_pair_ordering():
    """Refutes "a 3rd weight decides nothing the pair gate reads".

    A pair is compared lexicographically. When `c_d` TIES, the comparison falls
    through to `credence`, which contains `W`. So a third weight does change
    pair orderings, and R2 is not jobless under R3 -- it refines a term that
    should not be in that coordinate at all.
    """
    a_conf, b_conf, ver = 0.9, 0.8, 1.0
    # Two weights: "MEDIUM" is unrecognised, so compute_sev_f defaults to HARD.
    two_a = compute_sev_f("MEDIUM", a_conf, "CONFIRMED")
    two_b = compute_sev_f("HARD", b_conf, "CONFIRMED")
    # Three weights, as R2 proposes: a value strictly inside (1/2, 1).
    w3 = {"HARD": 1.0, "MEDIUM": 0.8, "SOFT": 0.5}
    three_a, three_b = w3["MEDIUM"] * a_conf * ver, w3["HARD"] * b_conf * ver

    assert two_a > two_b, "under two weights A must outrank B"
    assert three_a < three_b, "under three weights B must outrank A"
    assert (two_a > two_b) != (three_a > three_b), (
        "the third weight must flip the tie-break; if it does not, the claim "
        "that R2 is live under R3 falls")


def test_a_per_domain_critical_level_cannot_reach_the_numeric_gate():
    """The gate compares with `>=` against a float; declared levels are strings.

    The probe entry is asserted to SURVIVE `_gate_population` first. Two
    earlier versions of this probe passed without demonstrating anything: one
    omitted a required argument and caught a signature `TypeError`, the other
    used `round_opened` instead of `open_since_round`, so the entry was
    filtered out and the comparison was never reached.
    """
    entries = [{"canonical_id": "X1", "severity": 0.9,
                "open_since_round": 0, "status": "OPEN"}]
    assert len(cl._gate_population(entries)) == 1, (
        "probe entry must survive the gate population filter")
    assert cl._criticals(entries, 1, CRITICAL_SEVERITY_THRESHOLD), (
        "probe entry must be counted critical at the numeric cut, else a "
        "clean run below would prove nothing")

    with pytest.raises(TypeError, match="'>=' not supported"):
        cl.hierarchical_novelty_series(entries, 1, ["s"],
                                       critical_threshold="High")


def test_the_manifest_declares_five_none_and_one_composed():
    """Refutes "the 6 severity_scale='none' domains inherit the application level".

    Measured: FIVE declare `none`. The sixth is `cross_domain`, which declares
    `composed` -- and by the manifest's own rule a composed domain carries two
    or more scales and inherits NO single application level.
    """
    try:
        import tomllib
    except ImportError:                                        # pragma: no cover
        import tomli as tomllib
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    man = tomllib.loads((root / REPO_TOML).read_text(encoding="utf-8"))
    none_d = [k for k, v in man.items()
              if isinstance(v, dict) and v.get("severity_scale") == "none"]
    composed = [k for k, v in man.items()
                if isinstance(v, dict) and v.get("severity_scale") == "composed"]
    assert len(none_d) == 5, "expected five 'none' domains, got %r" % (none_d,)
    assert composed == ["cross_domain"], (
        "expected cross_domain to be the only 'composed' domain, got %r"
        % (composed,))
