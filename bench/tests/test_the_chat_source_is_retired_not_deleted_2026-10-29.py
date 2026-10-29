"""His ruling retired the chat source. It must be OUT of the default and STILL reachable.

HIS RULING, 2026-10-28, verbatim: *"My verdict is to scrap it if it will add to
inefficiency. When I went to sleep last night I noted you were very busy trying
to make it work. This is not a good use of your time, or mine. We will continue
in the previously agreed way. If I have a question, I will mark it as 'qs' in my
tts responses."*

THE RULING IS CONDITIONAL AND THE CONDITION WAS NOT EVALUABLE WHEN HE GAVE IT.
At that point the chat half was broken: its prefilter was not a superset of its
own decision, so "captures nothing useful" and "captures nothing at all" could
not be told apart. The free panel of 2026-10-28 fixed the prefilter -- both
seats delivered a randomised falsifier and both pass -- and with the filter
CORRECT the chat half still returns 0 rows for every window back to 2026-08-01,
at about 15 s per invocation. The 0 is a property of the corpus: of 249,664
transcript lines the number whose text RAISES a marker is 0, and every marker
that appears is a citation, a harness echo or a quotation, which the filters
correctly reject. So his condition HOLDS.

WHY RETIRED AND NOT DELETED, which is the property this file pins. A removal
needs a committed measurement that the replacement dominates; the replacement is
his annotation path, which has supplied 318 annotations against the chat half's
0. But `from_chat` is ALSO the subject of the measurement that justifies
retiring it, and `measured-rate-travels-with-its-script` means that evidence has
to stay reproducible. So the default no longer names `chat` and `--sources chat`
still reaches it.

Producer: `scripts/the_chat_half_was_blind_2026-10-28.py`, whose
`retirement_check` re-tests his condition on every run and says so in its output
if the condition ever stops holding.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HARVESTER = REPO / "scripts" / "harvest_tickets_2026-10-17.py"
PRODUCER = REPO / "scripts" / "the_chat_half_was_blind_2026-10-28.py"


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def test_the_default_does_not_name_chat():
    """The reversion target: putting `chat` back in the default restores a cost
    with a measured 0 yield, against his ruling."""
    r = subprocess.run([sys.executable, str(HARVESTER), "--help"],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[:400]
    blob = r.stdout
    assert "task_list,responses" in blob.replace(" ", ""), (
        "the --sources default no longer reads task_list,responses; if `chat` "
        "has returned to it, his 2026-10-28 ruling has been reversed silently")
    assert "default: task_list,responses,chat" not in blob.replace("'", ""), (
        "`chat` is back in the default")


def test_chat_is_still_REACHABLE_because_it_is_the_evidence():
    """Deleting it would destroy the measurement that justifies retiring it."""
    h = _load(HARVESTER, "_harv_retired")
    assert hasattr(h, "from_chat"), (
        "`from_chat` is gone. It is the SUBJECT of the measurement that "
        "justifies its own retirement, and a figure whose producer cannot run "
        "is a claim about evidence rather than evidence")
    assert callable(h.from_chat)
    assert hasattr(h, "CANDIDATE_LINE") and hasattr(h, "raises_a_marker")


def test_the_prefilter_repair_survived_the_retirement():
    """A retired facility must not quietly lose the panel's fix to it."""
    h = _load(HARVESTER, "_harv_retired2")
    assert h.CANDIDATE_LINE.pattern == r"(?:fr|pf|qs|wr)\b", (
        f"the prefilter is {h.CANDIDATE_LINE.pattern!r}; the panel's repair has "
        f"been lost along with the source's retirement")


def test_the_producer_still_tests_his_condition():
    """The condition is CONDITIONAL, so it is re-tested rather than recorded."""
    m = _load(PRODUCER, "_chat_blind_producer")
    assert hasattr(m, "retirement_check"), (
        "the producer no longer re-tests his condition, so a change that made "
        "the chat half useful again would leave the retirement standing on a "
        "stale measurement")
    h = _load(HARVESTER, "_harv_retired3")
    out = m.retirement_check(h)
    assert "TOTAL captured across every window: 0" in out, (
        "the chat half now captures something, so HIS CONDITION NO LONGER "
        "HOLDS and the retirement must be put back to him rather than left "
        "standing:\n" + out)
    assert "his condition HOLDS" in out
