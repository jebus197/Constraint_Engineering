"""B94 decision 1: `v_bar` counts a model's own claim, and that is MEASURED.

B94's own text says the `verified` flag *"can be set either by an execution or
by the model writing `"VERIFIED": true` in its own reply"*. Measured 2026-11-10
by walking syntax trees over `bench/` and `scripts/`: of the 8
`Finding(..., verified=...)` construction sites -- the object `v_bar` reads by
attribute -- **7 take their value from the model's reply and the 8th is a
literal `False`**, 0.875000, Wilson [0.529112, 0.977583], Clopper-Pearson
[0.473490, 0.996840]. The execution path exists as **18** dict assignments to
`entry['verified']` on registry entries, which `v_bar` never reads. So the 2
quantities already exist in 2 places and are simply not joined.

THESE TESTS EXECUTE the producer's own scanner and the live dataclass. Nothing
asserts on source text: 8 of the first 16 grep hits for this flag were
COMMENTS, which is why the producer walks trees.

★ 2 DEFECTS IN THE PRODUCER ARE PINNED HERE, both found by running it.
Its first version walked only constructor calls and attribute assignments and
concluded the project never verifies by execution -- it had not looked in 3 of
the 5 routes, and the subscript route holds 18. Its second version classified
`verified=False` as a parsed reply because the ENCLOSING FUNCTION mentions
`verified_raw`, and its literal tally then read 0 because it compared against a
value expression it had already annotated.

WHICH quantity the fingerprint should read is HIS under B94 and is not decided
by anything here.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
PROD = REPO / "scripts" / "what_v_bar_actually_counts_2026-11-10.py"


@pytest.fixture(scope="module")
def prod():
    spec = importlib.util.spec_from_file_location("vbar_prod", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def scanned(prod):
    return prod.scan()


# ── what v_bar reads, established on the live object ───────────────────────

def test_v_bar_reads_a_dataclass_attribute_not_a_dict_key():
    sys.path.insert(0, str(REPO / "bench"))
    from dm._types import Finding                      # noqa: PLC0415
    assert dataclasses.is_dataclass(Finding)
    names = {f.name for f in dataclasses.fields(Finding)}
    assert "verified" in names, (
        "the field `v_bar` reads was renamed or removed; v_bar would then "
        "count nothing and report 0.0 rather than failing")


def test_the_manager_still_computes_v_bar_from_that_attribute():
    """EXECUTED on the real source tree, by parsing it -- the only honest way
    to tie the metric to the field without running a whole experiment."""
    import ast                                          # noqa: PLC0415
    src = (REPO / "bench" / "dm" / "_manager.py").read_text()
    found = False
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Attribute) and n.attr == "verified":
            found = True
            break
    assert found, (
        "`bench/dm/_manager.py` no longer reads `.verified` anywhere; v_bar's "
        "source has moved and this entry's measurement is stale")


# ── the producer's scanner, driven ─────────────────────────────────────────

def test_both_populations_are_found(scanned):
    """ANTI-VACUITY in both directions: a 0 on either side would make every
    proportion below meaningless."""
    ctor, subscript, repl, setat = scanned
    assert len(ctor) >= 5, f"only {len(ctor)} construction sites found"
    assert len(subscript) >= 5, (
        f"only {len(subscript)} registry dict assignments found; the execution "
        f"path is what the first version of the producer missed entirely")


def test_every_true_capable_construction_site_is_a_model_claim(scanned, prod):
    ctor, _sub, _r, _s = scanned
    literal = [c for c in ctor
               if c[3].split("   [<-")[0].strip() in ("False", "True")]
    claims = [c for c in ctor
              if any(mk in c[3] for mk in prod.CLAIM_MARKERS)
              or "[<- parsed reply]" in c[3]]
    unexplained = [c for c in ctor if c not in literal and c not in claims]
    assert not unexplained, (
        f"these construction sites take `verified` from something that is "
        f"neither a literal nor a parsed reply, so B94's factual answer no "
        f"longer holds: {unexplained}")


def test_a_literal_is_never_classed_as_a_parsed_reply(scanned):
    """★ THE PRODUCER'S OWN SECOND DEFECT. It classified by the ENCLOSING
    FUNCTION, so `verified=False` was labelled a parsed reply because
    `verified_raw` appears elsewhere in the same function."""
    ctor, _sub, _r, _s = scanned
    for fp, ln, _f, val in ctor:
        raw = val.split("   [<-")[0].strip()
        if raw in ("False", "True"):
            assert "[<- parsed reply]" not in val, (
                f"{fp}:{ln} is the literal {raw} and was annotated as a "
                f"parsed reply")


@pytest.mark.parametrize("label,snippet,bucket", [
    ("constructor", "f = Finding(finding_id='x', verified=True)\n", 0),
    ("dict subscript", "entry = {}\nentry['verified'] = True\n", 1),
    ("dataclasses.replace",
     "import dataclasses\nx = dataclasses.replace(f, verified=True)\n", 2),
    ("setattr", "setattr(f, 'verified', True)\n", 3),
])
def test_the_scanner_finds_each_route_on_a_planted_site(
        prod, tmp_path, label, snippet, bucket):
    """★ A PLANTED SITE PER ROUTE, because an assertion that a route is ABSENT
    cannot tell a clean tree from a blind scanner.

    The mutation board proved it: disabling the `setattr` branch left the guard
    GREEN, since the live tree holds 0 setattr sites and `assert not setat`
    stays true either way. Its predecessor checked for the word "setattr" in
    the producer's SOURCE, which the mutation left in place elsewhere -- a
    source assertion passing on a module that describes itself consistently,
    which is the failure `execute-do-not-grep` names.
    """
    (tmp_path / "bench").mkdir()
    (tmp_path / "bench" / "planted.py").write_text(snippet)
    found = prod.scan(roots=("bench",), base=tmp_path)
    assert found[bucket], (
        f"the scanner is blind to the {label} route: a planted site at "
        f"bench/planted.py was not found")
    assert sum(len(x) for x in found) == len(found[bucket]), (
        f"the planted {label} site was counted in more than 1 bucket")


def test_no_setattr_or_replace_route_has_appeared(scanned):
    """A RATCHET. If either appears, the producer's conclusion needs redoing
    and this test says so rather than the figure drifting silently."""
    _c, _sub, repl, setat = scanned
    assert not repl, f"dataclasses.replace(verified=...) appeared: {repl}"
    assert not setat, f"setattr(..., 'verified', ...) appeared: {setat}"


# ── the reserved interval contract ─────────────────────────────────────────

def test_the_interval_helper_honours_the_reserved_contract(prod):
    (wlo, whi), (clo, chi), cross = prod._iv(7, 8)
    assert 0.0 <= wlo < whi <= 1.0, (wlo, whi)
    assert 0.0 <= clo < chi <= 1.0, (clo, chi)
    assert cross < 1e-9, f"the 2 interval routes disagree by {cross}"
    assert clo < wlo, "Clopper-Pearson must be the wider interval here"


def test_the_interval_helper_survives_the_edges(prod):
    for k, n in ((0, 8), (8, 8), (1, 2)):
        (wlo, whi), (clo, chi), cross = prod._iv(k, n)
        assert 0.0 <= wlo <= whi <= 1.0, (k, n, wlo, whi)
        assert 0.0 <= clo <= chi <= 1.0, (k, n, clo, chi)
        assert cross < 1e-9, (k, n, cross)


# ── the producer runs, and cheaply ─────────────────────────────────────────

def test_the_producer_exits_zero():
    r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, r.stdout[-1200:] + r.stderr[-600:]
    assert "construction sites" in r.stdout
    assert "DICT assignments" in r.stdout


def test_the_producers_help_is_free():
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, str(PROD), "--help"],
                       capture_output=True, text=True, timeout=30,
                       cwd=str(REPO))
    assert r.returncode == 0, r.stderr
    assert time.monotonic() - t0 < 5.0, "a --help must never cost minutes"


def test_the_producer_states_that_the_decision_is_his():
    """B94's 2 halves are HIS. A producer that read as a recommendation would
    be taking a decision that changes a number driving the experiment.

    ★ ASSERTED ON THE OUTPUT, NOT THE SOURCE. The first version accepted
    `"stays HIS under B94" in src or "his decision" in src`, and the phrase
    "his decision" appears in the module docstring -- so removing the printed
    line left this GREEN. The mutation board caught it.
    """
    r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-600:]
    assert "stays HIS under B94" in r.stdout, (
        "the producer's output no longer says the decision is his")
