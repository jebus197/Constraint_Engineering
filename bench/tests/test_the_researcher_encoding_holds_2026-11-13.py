"""Layer 3 exists, its 3 files are separate for a measured reason, and the
currency check can actually refuse.

B185 and B188. The directives README declares 3 layers and the runner composes
2. Layer 3 -- "what the expert brings" -- had never existed as a file, and the
template built for it had 0 instances.

★ THE 3-FILE SPLIT IS NOT TIDINESS AND THIS FILE PINS THE REASON. The 3 hold
things that change at radically different rates: standards about 0.976190 times
a year, confirmations about 1370 times a year at a measured 3.75 session starts
a day. In 1 file a content hash would change 1370.66 times a year of which
0.9762 are real -- a tamper-alert precision of 0.00071220, so 99.93 per cent of
alerts would be benign. Split, the standards file changes only when a standard
does: precision 1.0, a 1404.0952x improvement on a named property. Merging them
would silently destroy the tamper signal while every test about CONTENT still
passed, which is why the separation is asserted here rather than assumed.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tomllib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = REPO / "bench" / "directives" / "researchers"
PROD = REPO / "scripts" / "researcher_encoding_currency_2026-11-13.py"


@pytest.fixture(scope="module")
def cur():
    spec = importlib.util.spec_from_file_location("_cur", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_cur"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def test_layer_three_has_at_least_one_instance(cur):
    """★ THE WHOLE POINT. An architecture declaring a layer that has never been
    instantiated is a promise, not a mechanism."""
    names = cur.researchers()
    assert names, (
        "layer 3 has 0 instances. The directives README declares it and the "
        "runner composes layers 1 and 2 around it.")


def test_the_three_files_are_separate(cur):
    """★ MERGING THEM DESTROYS THE TAMPER SIGNAL. A single file would still
    pass every content test while the hash became useless."""
    for name in cur.researchers():
        d = ROOT / name
        for f in ("standards.toml", "preferences.toml", "confirmations.toml"):
            assert (d / f).is_file(), f"{name} is missing {f}"
        a = tomllib.loads((d / "standards.toml").read_text())
        c = tomllib.loads((d / "confirmations.toml").read_text())
        assert "confirmed" not in a, (
            f"{name}: confirmations have leaked into standards.toml. That file "
            f"must change only when a standard does, or its hash stops being a "
            f"usable tamper signal -- 0.00071220 precision against 1.0.")
        assert "domains" not in c, (
            f"{name}: the standards declaration has leaked into "
            f"confirmations.toml, which is rewritten on every session start")


def test_the_encoding_points_rather_than_restates(cur):
    """A researcher encoding NAMES the domain encodings that apply. Restating
    their content goes stale the moment a domain file changes."""
    for name in cur.researchers():
        std = tomllib.loads((ROOT / name / "standards.toml").read_text())
        doms = std.get("domains") or {}
        assert doms.get("primary"), f"{name} names no primary domains"
        for dom in doms["primary"]:
            block = doms.get(dom)
            assert isinstance(block, dict), f"{name}: {dom} has no block"
            enc = block.get("encoding")
            assert enc, f"{name}: {dom} names no encoding file"
            assert (REPO / enc).is_file(), (
                f"{name}: {dom} points at {enc}, which does not exist")


def test_the_public_instance_carries_no_private_detail(cur):
    """★ HIS STANDING POSITION. The repository instance is the worked example
    others copy, and carries no health, neurotype or identifying detail."""
    BANNED = ("autism", "adhd", "dyslex", "diagnos", "medication",
              "@", "phone", "address")
    for name in cur.researchers():
        prefs_p = ROOT / name / "preferences.toml"
        prefs = tomllib.loads(prefs_p.read_text())
        if prefs.get("instance") != "public":
            continue
        body = prefs_p.read_text().lower()
        hits = [w for w in BANNED if w in body]
        assert not hits, (
            f"{name}/preferences.toml is marked public and contains {hits}. "
            f"A requirement may travel into the repository; the private reason "
            f"for it may not.")


def test_the_cadence_is_derived_not_typed(cur):
    """The backstop must follow from the exposure law, not from a constant."""
    for ceiling in (0.005, 0.01, 0.02):
        for lam in cur.LAMBDA.values():
            T = cur.backstop_for(ceiling, lam)
            assert abs(cur.exposure(lam, T) - ceiling) < 1e-12, (
                "backstop_for and exposure disagree, so the 2 halves of the "
                "cadence are not inverses of each other")
    # the fastest feed must give the tightest backstop
    worst = max(cur.LAMBDA, key=lambda k: cur.LAMBDA[k])
    bs = {k: cur.backstop_for(0.01, v) for k, v in cur.LAMBDA.items()}
    assert bs[worst] == min(bs.values())


def test_the_check_can_actually_refuse(cur, tmp_path, monkeypatch):
    """★ NON-VACUITY. A currency check that cannot report an overdue standard
    is a check that always says yes."""
    import datetime as dt
    name = cur.researchers()[0]
    # drive it 10 years forward: everything cited must then be overdue
    far = dt.date.today() + dt.timedelta(days=3650)
    r = cur.check(name, today=far)
    assert r["due"], (
        "10 years after its last confirmation the check reports nothing due, "
        "so it cannot refuse and its OK verdict means nothing")
    # ...and today it must NOT be crying wolf
    r_now = cur.check(name)
    assert not r_now["unconfirmed"], (
        f"a cited standard has no confirmation date at all: "
        f"{r_now['unconfirmed']}")


def test_a_domain_with_no_scale_is_never_reported_overdue(cur):
    """A domain declaring no consequence scale has nothing to go stale, and
    reporting it as overdue would train the reader to ignore the alarm."""
    import datetime as dt
    far = dt.date.today() + dt.timedelta(days=3650)
    for name in cur.researchers():
        r = cur.check(name, today=far)
        exempt = {d for d, _ in r["exempt"]}
        overdue = {d for d, _, _, _ in r["due"]} | {d for d, _ in r["unconfirmed"]}
        assert not (exempt & overdue), (
            f"{name}: {exempt & overdue} declare no scale yet are reported "
            f"as needing confirmation")
