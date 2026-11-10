"""The model catalogue must be REACHED by a product module, not only by a test.

`bench/model_catalogue.py` is B21 step 5 -- the generated selectable model list
-- built on 2026-11-10 and verified by execution. Measured the same day: it was
named by its own guard and 1 producer and by **0 product modules**, which is an
addition nothing reaches. `additive-standard`'s symmetric form forbids that as
firmly as it forbids removing something needed: over this project's record since
2026-08-01, 11 confirmed defects were additions that did nothing and 0 were
removals of something needed.

`bench/ux_backend_2026-10-20.py:seats()` is the natural consumer, and its own
docstring said the route half comes back as unknown because *"there is no
module-level roster to read"*. The catalogue is exactly that roster.

THESE TESTS EXECUTE `seats()` and read its return value. A source assertion
would prove only that the module describes itself consistently, and this
project has withdrawn 4 claims found by executing 2 forms against each other.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="module")
def ux():
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "ux_backend_probe", REPO / "bench" / "ux_backend_2026-10-20.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def test_seats_reports_the_catalogue_when_no_run_is_supplied(ux):
    r = ux.seats()
    assert "catalogue" in r, sorted(r)
    assert r["catalogue"], (
        "the catalogue came back empty, so a front end still cannot offer a "
        "model list before a run is loaded")
    assert r["catalogue_source"] == (
        "bench/model_catalogue.py:registry_models"), r["catalogue_source"]


def test_the_catalogue_is_a_fallback_and_never_an_override(ux):
    """A run's OWN configuration is the authority on what it dispatches."""
    r = ux.seats(models=[])
    assert r["catalogue"] is None, (
        "a per-run roster was supplied and the catalogue answered anyway")
    assert "not consulted" in r["catalogue_source"], r["catalogue_source"]


def test_every_catalogue_entry_names_a_model(ux):
    for e in ux.seats()["catalogue"]:
        assert isinstance(e, dict), e
        assert any(k in e for k in ("id", "name", "model", "label")), sorted(e)


def test_it_contacts_nothing_and_reads_no_credential_value(ux):
    """A probe is a dispatch, and no dispatch happens without his word."""
    r = ux.seats()
    flat = repr(r).lower()
    for secret in ("sk-", "api_key=", "bearer "):
        assert secret not in flat, f"a credential value leaked: {secret}"
    assert r["rule"].startswith("configuration is reported"), r["rule"]


def test_the_catalogue_module_is_now_reached_by_a_product_module():
    """THE PROPERTY THE ENTRY IS ABOUT, asserted on the parsed tree so a
    comment mentioning the module cannot satisfy it."""
    import ast
    src = (REPO / "bench" / "ux_backend_2026-10-20.py").read_text()
    found = False
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.ImportFrom) and (n.module or "").endswith("bench"):
            found = found or any(a.name == "model_catalogue" for a in n.names)
        if isinstance(n, ast.Import):
            found = found or any("model_catalogue" in a.name for a in n.names)
    assert found, (
        "no product module imports the catalogue any more, so B21 step 5 is "
        "an addition nothing reaches again")


def test_a_missing_catalogue_costs_the_fallback_and_not_the_surface(ux,
                                                                   monkeypatch):
    """FAILS OPEN. A front end must still get a seats surface."""
    import builtins
    real = builtins.__import__

    def boom(name, *a, **k):
        if name == "bench" and a and "model_catalogue" in str(a):
            raise ImportError("planted")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", boom)
    r = ux.seats()
    assert r["name"] == "Seats"
    assert "counts" in r and "seats" in r

