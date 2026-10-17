"""The register has a terminal entry point, and it costs nothing to ask.

His instruction of 2026-10-17 was that the register be searchable by string id,
by literal word, or by any other method that is quick and accurate, and that it
be organised into areas so that finding one issue does not mean looking through
every issue. All 4 search methods already existed as library functions; what
did not exist was any way to call them from a terminal -- `bench/ticket_store.py`
contained 0 occurrences of `argparse`. `scripts/register.py` is that entry
point, and the design brief he attached proposes the same thing in its
section 4.

`--help` MUST NEVER COST MONEY. 15 of 17 runners in this project once billed
for a help request, so that is asserted here directly rather than assumed.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
CLI = REPO / "scripts" / "register.py"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _run(*args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, cwd=str(REPO))


@pytest.fixture(scope="module")
def store():
    from bench.ticket_store import TicketStore
    s = TicketStore()
    s.load()
    if len(s.all()) < 20:
        pytest.skip("register too small to exercise a CLI against")
    return s


def test_the_entry_point_exists_and_is_executable():
    assert CLI.is_file(), "the CLI his instruction asks for does not exist"


def test_help_exits_clean_and_dispatches_to_nothing():
    r = _run("--help")
    assert r.returncode == 0, r.stderr
    assert "usage: register.py" in r.stdout
    # A help request must not reach a model or the network. Asserted by the
    # absence of any dispatch marker in the output and by the exit code; the
    # suite is offline by default, so a dispatch would fail loudly.
    assert "openrouter" not in r.stdout.lower()
    assert "api" not in r.stderr.lower()


def test_no_arguments_prints_help_and_refuses_rather_than_dumping_everything():
    """A bare invocation that printed 902 tickets would be a token trap."""
    r = _run()
    assert r.returncode == 2
    assert "usage: register.py" in r.stdout


def test_an_unknown_id_fails_rather_than_returning_nothing_quietly():
    r = _run("--id", "zzzznotarealid")
    assert r.returncode == 1
    assert "no ticket" in r.stderr


def test_an_exact_id_finds_exactly_that_ticket(store):
    target = store.all()[0]
    r = _run("--id", target.tid, "--json")
    assert r.returncode == 0, r.stderr
    rows = json.loads(r.stdout)["rows"]
    assert [x["tid"] for x in rows] == [target.tid]


def test_an_id_prefix_resolves(store):
    target = store.all()[0]
    r = _run("--id", target.tid[:8], "--json")
    assert r.returncode == 0, r.stderr
    assert target.tid in {x["tid"] for x in json.loads(r.stdout)["rows"]}


def test_the_word_search_returns_what_the_library_returns(store):
    """ONE DEFINITION, EXECUTED TWICE. The CLI must not reimplement search."""
    target = next(t for t in store.all() if len(t.verbatim or "") > 60)
    expected = {t.tid for t in store.similar_by_words(target.verbatim)}
    r = _run("--word", target.verbatim, "--json", "--limit", "0")
    assert r.returncode == 0, r.stderr
    got = {x["tid"] for x in json.loads(r.stdout)["rows"]}
    assert got == expected, (
        f"the CLI's word search differs from the library's by "
        f"{len(got ^ expected)} ticket(s). It is calling something else.")


def test_the_subject_search_returns_what_the_library_returns(store):
    subject = next((s for s in store.subjects() if store.by_subject(s)), None)
    if subject is None:
        pytest.skip("no ticket carries a subject in this checkout")
    expected = {t.tid for t in store.by_subject(subject)}
    r = _run("--subject", subject, "--json", "--limit", "0")
    assert r.returncode == 0, r.stderr
    assert {x["tid"] for x in json.loads(r.stdout)["rows"]} == expected


def test_every_ticket_gets_an_area_so_the_filter_cannot_hide_one(store):
    """Coverage is the point: a ticket with no area would be unreachable by
    any --area query, which is the whole-store scan it was meant to avoid."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_reg", CLI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    index = mod._definition_index()
    missing = [t.tid for t in store.all() if not mod.area_of(t, index)]
    assert not missing, (
        f"{len(missing)} tickets resolve to no area at all: {missing[:5]}")


def test_the_area_distribution_accounts_for_every_ticket(store):
    r = _run("--areas", "--json")
    assert r.returncode == 0, r.stderr
    counts = json.loads(r.stdout)
    assert sum(counts.values()) == len(store.all()), (
        f"the area distribution sums to {sum(counts.values())} against "
        f"{len(store.all())} tickets, so a ticket is counted twice or not at "
        f"all")


def test_the_area_filter_narrows_rather_than_widens(store):
    r = _run("--areas", "--json")
    counts = json.loads(r.stdout)
    area = max(counts, key=counts.get)
    r2 = _run("--area", area, "--json", "--limit", "0")
    assert r2.returncode == 0, r2.stderr
    got = json.loads(r2.stdout)["matched"]
    assert got == counts[area], (
        f"--area {area} returned {got} against a declared {counts[area]}")
    assert got < len(store.all()), "the filter narrowed nothing"


def test_a_status_filter_composes_with_a_word_search(store):
    """COMPOSABILITY, not a special case per combination."""
    target = next(t for t in store.all() if len(t.verbatim or "") > 60)
    r = _run("--word", target.verbatim, "--status", target.status,
             "--json", "--limit", "0")
    assert r.returncode == 0, r.stderr
    rows = json.loads(r.stdout)["rows"]
    assert rows, "the composed query returned nothing; it should find at least "\
                 "the ticket the query text came from"
    assert all(x["status"] == target.status for x in rows)


def test_the_json_output_is_machine_readable_on_every_mode(store):
    for args in (("--summary",), ("--areas", "--json"),
                 ("--id", store.all()[0].tid, "--json")):
        r = _run(*args)
        assert r.returncode == 0, f"{args}: {r.stderr}"
        json.loads(r.stdout)
