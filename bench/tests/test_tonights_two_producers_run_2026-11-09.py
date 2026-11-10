"""The 2 producers written on 2026-11-09 are EXECUTED by this file.

WHY IT EXISTS. `bench/tests/test_an_unreached_producer_set_cannot_grow_2026-11-08.py`
is a ratchet: a producer nothing runs may not be added. Its own words are
"Either have a test execute them, or -- if one is deliberately exempt -- say
so beside the exemption. Re-pinning to silence this is how a ratchet becomes a
rubber stamp." Neither of these is exempt, so neither is pinned; both are run.

WHAT THEY PRODUCED, AND WHY IT MATTERS THAT THEY KEEP RUNNING. Both answered
questions he asked directly on 2026-11-09, and both corrected a claim of mine:

  how_many_items_actually_remain  -- the exact census, and the demonstration
    that the master task list has been as low as 2 open entries, which refutes
    the "it may never exhaust" framing I had used with him.

  how_many_did_he_actually_ask_for -- 21 explicit add-to-the-list instructions
    of his under the narrow reading, 23 under the wider one, against his own
    recollection of "no greater than 30".

A figure quoted to him whose producer no longer runs is a figure with no
evidence behind it, which is the defect `measured-rate-travels-with-its-script`
names.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
PRODUCERS = {
    "how_many_items_actually_remain_2026-11-09.py": (
        ("total_entries", "states sum to total"),
        600),
    "how_many_did_he_actually_ask_for_2026-11-09.py": (
        ("TOTAL explicit add-to-the-list instructions", "NARROW", "WIDE"),
        600),
}


def _run(name: str, timeout: int) -> subprocess.CompletedProcess:
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    return subprocess.run([sys.executable, str(p)], capture_output=True,
                          text=True, timeout=timeout, cwd=str(REPO))


@pytest.mark.parametrize("name", sorted(PRODUCERS))
def test_the_producer_exits_zero(name):
    """EXECUTED, not inspected. A producer that cannot run is not evidence."""
    r = _run(name, PRODUCERS[name][1])
    assert r.returncode == 0, (
        f"{name} exited {r.returncode}. Its figures were quoted to the founder "
        f"on 2026-11-09, so this is a silent loss of evidence.\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-800:]}")


@pytest.mark.parametrize("name", sorted(PRODUCERS))
def test_the_producer_still_prints_its_headline(name):
    r = _run(name, PRODUCERS[name][1])
    missing = [m for m in PRODUCERS[name][0] if m not in r.stdout]
    assert not missing, (
        f"{name} ran but no longer prints {missing}; the figure quoted to him "
        f"came from these lines")


@pytest.mark.parametrize("name", sorted(PRODUCERS))
def test_every_proportion_it_prints_carries_an_interval(name):
    """His standing rule: a proportion is reported with a confidence interval."""
    r = _run(name, PRODUCERS[name][1])
    bare = []
    for line in r.stdout.splitlines():
        if not re.search(r"\b\d+ of \d+\b", line):
            continue
        if "Wilson" in line or "Clopper" in line:
            continue
        #: ★ THIS GUARD ACCUSED CORRECT CODE ON ITS FIRST RUN. The census
        #: ECHOES entry titles, and one of them -- B79's -- contains the words
        #: "3 of 6 seats", which is a proportion the ENTRY reports and not one
        #: the producer computes. A line that carries the entry-listing columns
        #: is quoted material, so it is skipped. Narrowed rather than deleted:
        #: the rule still binds on every figure the producer itself prints.
        if "status=" in line or "ruled (" in line:
            continue
        # the interval is allowed on the NEXT line, which is the house style
        bare.append(line.strip())
    joined = r.stdout
    for b in list(bare):
        i = joined.find(b)
        after = joined[i:i + 400]
        if "Wilson" in after or "Clopper" in after:
            bare.remove(b)
    assert not bare, (
        f"{name} prints a proportion with no interval near it: {bare[:3]}")


class TestTheCensusAgreesWithTheLiveReader:
    """A producer that disagrees with the engine it reports on is not evidence."""

    def test_the_total_matches_parse_entries(self):
        sys.path.insert(0, str(SCRIPTS))
        import task_list_markers as tlm
        live = len(tlm.parse_entries())
        r = _run("how_many_items_actually_remain_2026-11-09.py", 600)
        m = re.search(r"total_entries:\s*(\d+)", r.stdout)
        assert m, f"the census no longer prints its total:\n{r.stdout[:800]}"
        assert int(m.group(1)) == live, (
            f"the census reports {m.group(1)} entries, the canonical reader "
            f"finds {live}. A producer and its subject disagreeing is the "
            f"shape `execute-do-not-grep` names.")
