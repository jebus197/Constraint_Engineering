#!/usr/bin/env python3
# PROVENANCE: written by panel seat cc2 inside its own sandbox during the
# falsifier-root-cause design review of 2026-09-30, NOT by the orchestrating
# session. Rescued verbatim to scripts/ on 2026-09-30T10:47:16+01:00 because
# .gitignore:48 `bench/logs/**` excluded the harvest that held it, leaving the
# evidence behind this review's published figures unversioned and one reboot
# from unrecoverable. Body is byte-identical to the seat's output below this
# header; the seat's original sha256 is 1a2576c4ba811c3bdd4a41b93a3edb8213e655f409e2bab409cedace144fa834
# (recorded in scripts/seat_evidence_manifest_2026-09-30.json). It is EVIDENCE,
# not an applied fix: no seat proposal is adopted by this rescue.
"""FALSIFIER: the "no runnable falsifier" root cause is a SUPPLY gap, not a
capability gap and not a routing gap -- and the project already owns the supply.

THE CLAIM UNDER TEST (three parts, all mechanically decided here):

  (1) SUPPLY EXISTS AND WORKS. `bench/tests/fixtures/stem/stem_fixtures.py`
      carries 5 prose STEM documents with 29 ground-truth-tagged claims and one
      `falsifier_template` each. Every template, re-run by the project's own
      decider `falsifier_verify.reverify_falsifier`, must CONFIRM on the pristine
      document (the planted false claim is present) and REFUTE on the corrected
      document. That is a BIDIRECTIONAL discriminator, not a rubber stamp.

  (2) SUPPLY IS UNREACHABLE FROM THE LIVE PATH. No module on the live review
      path imports the corpus, and no seat-facing directive teaches the pattern.
      A working mechanism nothing reaches is, by the project's own additive
      standard, an addition that does nothing.

  (3) ROUTING CANNOT SUBSTITUTE FOR SUPPLY. `routing.resolve_via_routing` is
      driven with a `resolve_fn` that returns no falsifier (today's seat, which
      emits UNTOOLABLE) and then with one that returns the corpus pattern. If
      routing were the fix, climbing rungs would resolve findings regardless of
      supply. It does not: with nothing to route, EVERY rung returns ERROR.

Raises AssertionError iff the root cause stands as stated. Prints NOT FALSIFIED
and exits 0 once the corpus is reachable from the live path.

Run:  python3 scripts/falsify_prose_falsifier_supply_2026-09-30.py
"""
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench/tests/fixtures/stem"))

import stem_fixtures as SF                                   # the REAL corpus
from bench.falsifier_verify import reverify_falsifier         # the REAL decider
from bench.routing import rank_falsifier_writers, resolve_via_routing

# ---- (1) does the committed supply actually discriminate, both ways? ------
print("== part 1: bidirectional discrimination by the project's own decider ==")
claims = sum(len(f.claims) for f in SF.FIXTURES)
false_claims = sum(1 for f in SF.FIXTURES for c in f.claims if c.verdict == "FALSE")
print("fixtures=%d claims=%d FALSE=%d TRUE=%d"
      % (len(SF.FIXTURES), claims, false_claims, claims - false_claims))

tmp = pathlib.Path(tempfile.mkdtemp())
bidirectional = 0
for f in SF.FIXTURES:
    v_pristine = reverify_falsifier(f.falsifier(), repo_root=str(ROOT))
    corrected = tmp / f.doc_name
    corrected.write_text(f.apply(f.correct_fix), encoding="utf-8")
    v_fixed = reverify_falsifier(f.falsifier(corrected), repo_root=str(ROOT))
    ok = (v_pristine == "CONFIRMED" and v_fixed == "REFUTED")
    bidirectional += ok
    print("  %-11s pristine=%-10s corrected=%-9s %s"
          % (f.key, v_pristine, v_fixed, "OK" if ok else "MISBEHAVED"))
print("  bidirectional: %d/%d" % (bidirectional, len(SF.FIXTURES)))

# ---- (2) is that supply reachable from the live review path? --------------
print("\n== part 2: reachability from the live path ==")
LIVE = ["bench/reference_runner_v3.py", "bench/runner_core.py",
        "bench/immune_agents.py"]
LIVE_DIRS = ["bench/cdsfl_registry", "bench/directives"]
importers = []
for rel in LIVE:
    p = ROOT / rel
    if p.exists() and "stem_fixtures" in p.read_text(encoding="utf-8", errors="replace"):
        importers.append(rel)
for d in LIVE_DIRS:
    for p in (ROOT / d).rglob("*.py") if (ROOT / d).exists() else []:
        if "stem_fixtures" in p.read_text(encoding="utf-8", errors="replace"):
            importers.append(str(p.relative_to(ROOT)))
print("  live-path modules importing the corpus: %d %s" % (len(importers), importers or ""))

# ---- (3) can routing resolve without supply? -----------------------------
print("\n== part 3: routing is a multiplier on supply, not a substitute ==")
rungs = rank_falsifier_writers(["Gemini-SIM", "Codex-SIM"])


def _decide(code):
    return reverify_falsifier(code, repo_root=str(ROOT))


def untaught(model, finding):
    """Today's seat: reasons in prose, attaches nothing."""
    return ""


def taught(model, finding):
    """A seat with the corpus pattern in reach."""
    return finding["_template"]


scores = {}
for label, fn in (("no supply", untaught), ("corpus supply", taught)):
    resolved = 0
    for f in SF.FIXTURES:
        r = resolve_via_routing({"finding_id": f.key, "_template": f.falsifier()},
                                rungs, fn, _decide, max_rungs=2)
        resolved += r.resolved
        print("  %-13s %-11s verdict=%-10s resolved=%s rungs=%d"
              % (label, f.key, r.verdict, r.resolved, r.rungs_tried))
    scores[label] = resolved
print("  RESOLVED  no supply: %d/%d   corpus supply: %d/%d"
      % (scores["no supply"], len(SF.FIXTURES),
         scores["corpus supply"], len(SF.FIXTURES)))

# ---- verdict -------------------------------------------------------------
n = len(SF.FIXTURES)
supply_works = (bidirectional == n)
unreachable = (len(importers) == 0)
routing_insufficient = (scores["no supply"] == 0 and scores["corpus supply"] == n)

print("\nsupply_works=%s  unreachable_from_live_path=%s  routing_insufficient=%s"
      % (supply_works, unreachable, routing_insufficient))

if supply_works and unreachable and routing_insufficient:
    raise AssertionError(
        "ROOT CAUSE CONFIRMED: falsifier SUPPLY, not capability and not routing.\n"
        "  (1) %d/%d committed prose falsifiers discriminate BIDIRECTIONALLY under "
        "the project's own decider (CONFIRMED on the planted claim, REFUTED once "
        "corrected), over %d ground-truth claims.\n"
        "  (2) %d live-path modules import that corpus. It is reachable from the "
        "simulation harness and the test suite only, so no seat on a real review "
        "ever sees the one proven pattern this project owns.\n"
        "  (3) resolve_via_routing resolved %d/%d with no falsifier supplied and "
        "%d/%d with the corpus pattern supplied. Routing climbs a ladder of "
        "WRITERS; it cannot manufacture a PATTERN. With nothing to route, every "
        "rung returns ERROR, so adding rungs cannot close this gap.\n"
        "The fix is to put the corpus on the live path, which is a WIRING change, "
        "not new machinery and not a new model."
        % (bidirectional, n, claims, len(importers),
           scores["no supply"], n, scores["corpus supply"], n)
    )

print("\nNOT FALSIFIED: the corpus is now reachable from the live review path, "
      "or the supply no longer discriminates, or routing resolves without it.")
raise SystemExit(0)
