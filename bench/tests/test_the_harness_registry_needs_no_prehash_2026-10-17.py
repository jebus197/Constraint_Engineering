#!/usr/bin/env python3
"""The harness registry mints duplicates too rarely for a pre-mint lookup to help.

HIS QUESTION, 2026-10-17: *"The full harness already has a registry, but I don't
know if it currently works this way either? But if it doesn't and you do gauge it
to be genuinely useful you should probably apply these principles to the harness
registry too."*

THE ANSWER IS NO ON BOTH HALVES. It does not work that way --
`FindingRegistry.register` assigns `C{next:04d}`, a sequential counter -- and it
should not be made to, which is the opposite of the agreeable answer.

MEASURED across 61 runs and 2,954 described findings using the harness's OWN
`_routing_similarity`, so the judgement is the system's and not the author's: 33
pairs reach the 0.85 threshold the routing ladder actually uses, and only 6 of
the 33 carry substantial descriptions on BOTH sides. 6 are fragments of 8
distinct words or fewer and 21 are mid-length, where word overlap reaches 0.85 on
shared code tokens like `finding_id: str` without the findings being the same
defect. Several of the 6 are findings ABOUT other findings -- "Addresses C0007",
"VERDICT: CONFIRM C0014" -- which are legitimately distinct.

A first version of that measurement reported 33 pairs and 66 of 2,954 findings
involved, 2.2343%, and recommended putting the change to him. That figure is an
inflated upper bound dominated by the artefact, and it is withdrawn.

WHAT THIS GUARDS. Not the recommendation, which is a judgement, but the FACT the
recommendation rests on: that the duplication detectable by description overlap
is dominated by short fragments. If a future archive shows substantial
duplication instead, this fails and the question is genuinely reopened.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402

SCRIPT = REPO / "scripts" / "does_the_harness_registry_mint_duplicates_2026-10-17.py"
LOGS = REPO / "bench" / "logs"
THRESHOLD = 0.85


def _pairs():
    out = []
    if not LOGS.is_dir():
        return out
    for rs in sorted(LOGS.rglob("runner_state.json")):
        if len(rs.relative_to(LOGS).parts) != 2:
            continue
        try:
            ents = (json.loads(rs.read_text(errors="replace"))
                    .get("registry") or {}).get("entries") or {}
        except (OSError, ValueError):
            continue
        rows = [(c, e) for c, e in ents.items()
                if isinstance(e, dict) and (e.get("description") or "").strip()]
        for (ca, ea), (cb, eb) in itertools.combinations(rows, 2):
            if R._routing_similarity(ea, eb) >= THRESHOLD:
                out.append((ca, cb, ea, eb))
    return out


def _distinct_words(e) -> int:
    return len(set((e.get("description") or "").lower().split()))


def test_the_producer_exists_and_answers_help():
    assert SCRIPT.is_file()
    spec = importlib.util.spec_from_file_location("dup_probe", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["dup_probe"] = m
    spec.loader.exec_module(m)          # importable without doing the work


def test_identity_is_still_a_counter_not_a_hash():
    """The factual half of his question, read off the code."""
    import inspect
    src = inspect.getsource(R.FindingRegistry.register)
    assert "_next_id" in src, (
        "registration no longer uses a sequential counter; his question about "
        "whether the harness works like the ticket register has a new answer")
    assert "sha256" not in src and "hashlib" not in src, (
        "registration now hashes, so the measurement behind C32 no longer "
        "describes the code and the recommendation must be revisited")


def test_description_overlap_is_dominated_by_short_fragments():
    """THE FACT THE RECOMMENDATION RESTS ON.

    If substantial duplication ever outweighs the fragment artefact, a pre-mint
    lookup becomes worth considering and this test says so by failing.
    """
    pairs = _pairs()
    if not pairs:
        pytest.skip("no archived pairs reach the threshold in this checkout")
    subst = sum(1 for _, _, ea, eb in pairs
                if min(_distinct_words(ea), _distinct_words(eb)) > 20)
    frag_or_mid = len(pairs) - subst
    assert frag_or_mid > subst, (
        f"of {len(pairs)} pairs at {THRESHOLD}, {subst} are substantial against "
        f"{frag_or_mid} short or mid-length. The artefact no longer dominates, "
        f"so description overlap may now be a signal worth acting on and the "
        f"C32 recommendation needs revisiting.")


def test_the_duplication_rate_stays_low():
    """A pre-mint lookup is only worth its over-merge risk if duplication is real."""
    pairs = _pairs()
    if not pairs:
        pytest.skip("no archived pairs reach the threshold in this checkout")
    subst = sum(1 for _, _, ea, eb in pairs
                if min(_distinct_words(ea), _distinct_words(eb)) > 20)
    assert subst <= 20, (
        f"{subst} substantially-described duplicate pairs now exist. Above a "
        f"couple of dozen the balance against the over-merge hazard changes and "
        f"his question should be put again.")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
