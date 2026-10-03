#!/usr/bin/env python3
"""WHY does a critical finding end a run without a runnable falsifier?

THE FOUNDER'S QUESTION, 2026-10-02, verbatim from his annotation: "The
falsifier supply issue is a persistent problem for this project. You were asked
to decide if there might be a root cause. You said there might be, but I don't
know if it was ever identified or written? However I wonder if it might be the
case that our falsifier's are sometimes too specific, rather than general? ...
Our primary falsifiers after all are tools, and these tools are already
general?"

His hypothesis has a sharp, testable consequence: if a falsifier is only a
WRAPPER around a general tool, then a new target needs no new falsifier, and
starvation should be rare. If instead falsifiers hand-roll bespoke assertions
against one named target, starvation is structural. This script measures which
is true, and it measures what ACTUALLY stops a critical from being falsified,
because a cause asserted without a decomposition is a guess.

DELIBERATELY NOT A SINGLE RATE. "Supply failed" pools at least 5 distinct
states with different remedies:

    NO BODY        nothing was ever written            -> a supply problem
    ERROR          written, and it broke               -> an execution problem
    INTEGRITY      written, correct, and refused        -> a GATE problem
    UNTOOLABLE     the ladder declined to write one     -> a routing problem
    RESOLVED       written and it decided               -> no problem

Pooling these is how "falsifier supply" became one phrase for several faults.

THE DOUBLE-COUNT IS HANDLED EXPLICITLY. This project records that a run writes
its registry into more than 1 artefact, so every directory-walking archive
count has been doubled before, "in the reassuring direction". Entries are
therefore deduplicated on (cid, sha1(description)) and BOTH the raw and
deduplicated counts are printed, so the correction is visible rather than
asserted.

Cross-verification: every proportion carries a Wilson 95% interval computed by
statsmodels AND by an independent mpmath closed form, with agreement asserted.
No Wolfram result is used.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRITICAL = 0.7

#: A falsifier DELEGATES when it reaches a general instrument. Import or
#: subprocess both count: what matters is that the judgement is the tool's.
TOOL_PATTERNS = {
    "pytest": r"\bpytest\b",
    "ruff": r"\bruff\b",
    "bandit": r"\bbandit\b",
    "ast": r"\bimport ast\b|\bast\.(?:parse|walk|dump)\b",
    "sympy": r"\bsympy\b",
    "z3": r"\bimport z3\b|\bz3\.",
    "scipy": r"\bscipy\b",
    "numpy": r"\bnumpy\b|\bimport numpy\b",
    "mpmath": r"\bmpmath\b",
    "statsmodels": r"\bstatsmodels\b",
    "subprocess": r"\bsubprocess\.(?:run|call|check_output|Popen)\b",
    "importlib": r"\bimportlib\b",
    "compile": r"\bcompile\s*\(",
}
TOOL_RE = re.compile("|".join(f"(?:{p})" for p in TOOL_PATTERNS.values()))

#: A body is TARGET-COUPLED when it names a concrete file. A falsifier that
#: names no file can in principle be pointed at anything.
FILE_RE = re.compile(r"[\w./-]+\.(?:py|md|json|toml|txt|csv|yaml|yml)\b")


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if n == 0:
        return None
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    lo_mp, hi_mp = float((c - h) / d), float((c + h) / d)
    agree = abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9
    return float(lo_sm), float(hi_sm), lo_mp, hi_mp, agree


def pct(k: int, n: int, label: str, indent: str = "    ") -> None:
    if not n:
        print(f"{indent}{label:34s} {k:5d}  (no denominator)")
        return
    w = wilson(k, n)
    print(f"{indent}{label:34s} {k:5d} / {n:5d} = {100*k/n:8.4f}%  "
          f"Wilson [{100*w[0]:7.4f}%, {100*w[1]:7.4f}%]  agree={w[4]}")


def harvest():
    """Every critical finding in the archive, deduplicated, with its state."""
    raw = 0
    seen: dict[tuple[str, str], dict] = {}
    parse_failures = 0
    files = 0
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted((ROOT / "bench" / "logs").glob(f"*/{name}")):
            files += 1
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                parse_failures += 1
                continue
            reg = (data.get("registry") or {}).get("entries") or {}
            for cid, e in reg.items():
                if not isinstance(e, dict):
                    continue
                if (e.get("severity") or 0.0) < CRITICAL:
                    continue
                raw += 1
                desc = (e.get("description") or e.get("title") or "")[:4000]
                key = (cid, hashlib.sha1(desc.encode("utf-8", "replace")).hexdigest())
                prev = seen.get(key)
                # Prefer the record that carries a falsifier body.
                if prev is None or (not _body(prev) and _body(e)):
                    seen[key] = e
    return raw, seen, parse_failures, files


def _body(e: dict) -> str:
    return ((e.get("falsifier_code") or "").strip()
            or (e.get("last_falsifier_code") or "").strip())


def classify(e: dict) -> str:
    """Which of the states a critical's falsifier ended in.

    THE VERDICT IS READ BEFORE THE BODY, AND THE FIRST VERSION HAD IT THE OTHER
    WAY ROUND. It returned "NO BODY WAS EVER WRITTEN" on an empty body before
    looking at any verdict, so a finding the instrument ASSESSED AND DECLINED
    (UNTOOLABLE) or that ERRORED without retaining its source was reported as
    one nobody had written a falsifier for. Measured on the archive: 42 of the
    793 so classified carried a real verdict -- 38 UNTOOLABLE and 4 ERROR --
    5.2963%, Wilson [3.9420%, 7.0817%].

    That is exactly the conflation this file's own docstring says the
    decomposition exists to undo, and it inflated the bucket the conclusion
    rested on. Found by an adversarial pass over this script, not by reading it;
    `test_a_truncated_retained_body_still_counts_as_written` covered only the
    neighbouring case, which is `feedback_verify_the_deciding_layer` again.

    A DECLINATION IS NOT A SUPPLY FAILURE. "The ladder was asked and said no" and
    "nothing ever asked" have opposite remedies, so they get separate buckets.
    """
    body = _body(e)
    hist = e.get("routing_history") or []
    _eff = ((e.get("falsifier_verdict") or "").strip().upper()
            or (e.get("routing_verdict_unreconciled") or "").strip().upper()
            or ((hist[-1].get("verdict") or "").strip().upper() if hist else ""))
    if not body and not _eff:
        return "NOTHING WRITTEN AND NOTHING RECORDED"
    if not body and _eff == "UNTOOLABLE":
        return "ASSESSED AND DECLINED (UNTOOLABLE)"
    if not body and _eff == "ERROR":
        return "WRITTEN, THEN ERRORED"
    if not body:
        return f"NO BODY RETAINED, VERDICT {_eff}"
    v = (e.get("falsifier_verdict") or "").strip().upper()
    ladder = (e.get("routing_verdict_unreconciled") or "").strip().upper()
    hist = e.get("routing_history") or []
    last = (hist[-1].get("verdict") or "").strip().upper() if hist else ""
    eff = v or ladder or last
    if "INTEGRITY" in (v, ladder, last) or "INTEGRITY_VIOLATION" in (v, ladder, last):
        return "WRITTEN, REFUSED BY THE GATE"
    if eff == "CONFIRMED":
        return "WRITTEN AND RESOLVED"
    if eff == "ERROR":
        return "WRITTEN, THEN ERRORED"
    if eff == "UNTOOLABLE":
        return "ASSESSED AND DECLINED (UNTOOLABLE)"
    if eff in ("REFUTED",):
        return "WRITTEN, RETURNED REFUTED"
    return f"WRITTEN, OTHER VERDICT ({eff or 'none recorded'})"


def main() -> int:
    raw, seen, parse_failures, files = harvest()
    print("POPULATION")
    print(f"  archive files read                : {files}")
    print(f"  unreadable (reported, not dropped): {parse_failures}")
    print(f"  critical entries, RAW             : {raw}")
    print(f"  critical entries, DEDUPLICATED    : {len(seen)}")
    if raw:
        print(f"  inflation from re-recorded registries: "
              f"{100*(raw-len(seen))/raw:.4f}% of raw")

    print("\nWHAT ACTUALLY HAPPENS TO A CRITICAL'S FALSIFIER")
    buckets: dict[str, int] = {}
    for e in seen.values():
        buckets[classify(e)] = buckets.get(classify(e), 0) + 1
    n = len(seen)
    for label in sorted(buckets, key=lambda k: -buckets[k]):
        pct(buckets[label], n, label)

    bodies = {}
    for (cid, h), e in seen.items():
        b = _body(e)
        if b:
            bodies.setdefault(b, (cid, h))
    print(f"\nTHE FOUNDER'S HYPOTHESIS, TESTED ON {len(bodies)} DISTINCT BODIES")
    print("  'Our primary falsifiers after all are tools, and these tools are")
    print("   already general?' -- so: does a body DELEGATE to a general tool,")
    print("   or hand-roll its own assertions?")
    # COMMENTS ARE STRIPPED FIRST, and that correction came from this script's
    # own failable check rather than from reading it. A body whose only mention
    # of an instrument is in a `#` comment does not delegate to it; 2 of 70 were
    # of that shape. The raw count is printed beside it as the upper bound,
    # because the error direction matters: it inflates DELEGATION, so it
    # understates the hand-rolled share that carries the finding.
    def _code_only(src: str) -> str:
        return "\n".join(re.sub(r"#.*$", "", ln) for ln in src.splitlines())

    delegating = sum(1 for b in bodies if TOOL_RE.search(_code_only(b)))
    raw_deleg = sum(1 for b in bodies if TOOL_RE.search(b))
    pct(delegating, len(bodies), "DELEGATES to a general tool")
    pct(len(bodies) - delegating, len(bodies), "hand-rolled, no general tool")
    pct(raw_deleg, len(bodies), "  (delegation incl. comment-only, upper bound)")

    per_tool = {k: sum(1 for b in bodies if re.search(p, _code_only(b)))
                for k, p in TOOL_PATTERNS.items()}
    print("\n  which instrument, where one is reached:")
    for k in sorted(per_tool, key=lambda k: -per_tool[k]):
        if per_tool[k]:
            pct(per_tool[k], len(bodies), f"  {k}", indent="    ")

    print("\nTARGET COUPLING (a body naming a concrete file cannot be repointed)")
    named = sum(1 for b in bodies if FILE_RE.search(b))
    pct(named, len(bodies), "names at least 1 concrete file")
    counts = sorted(len(set(FILE_RE.findall(b))) for b in bodies)
    if counts:
        import numpy as np, mpmath as mp
        mean_np = float(np.mean(counts))
        mp.mp.dps = 30
        mean_mp = float(mp.fsum(counts) / len(counts))
        print(f"    distinct files named per body: mean {mean_np:.4f} "
              f"(numpy) / {mean_mp:.4f} (mpmath), agree="
              f"{abs(mean_np-mean_mp) < 1e-9}, median {counts[len(counts)//2]}, "
              f"max {counts[-1]}")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NEVER COST ANYTHING (founder ruling, after 15 of 17
    # runners billed a live dispatch on an unrecognised argument). Without
    # this call the flag is ignored and the whole archive measurement runs
    # in answer to a request to be told what the script does.
    answer_help(__doc__, __file__)
    raise SystemExit(main())
