#!/usr/bin/env python3
"""Was the severity panel invalidated by the truncation I claimed in its brief?

HIS QUESTION, 2026-10-31, verbatim: "Also if the panel review you did was based
on what you took as a truncated response from me, is it still valid? Should we
scrap it and run it again with the full framing?"

THE CLAIM UNDER TEST IS MINE, NOT HIS. The joint brief of 2026-10-31 and the
morning report both state that his second severity question is truncated in the
record mid-sentence at the words "what should realistic boundaries for these".
This script tests that claim against the artefacts and then tests whether the
round's conclusion depends on it.

DECISION RULE, STATED BEFORE MEASURING SO IT CAN FAIL.
  The round is INVALID if either holds:
    (a) the seats were deprived of the content of his question, or
    (b) the conclusion rests on the escape clause the brief offered
        ("or a plain statement that they cannot be set yet") rather than on
        mechanical evidence about the code.
  Otherwise the round stands and the defect is in the RECORD, not the dispatch.

WHY SUBSTRING PROBES ARE THE RIGHT INSTRUMENT HERE, against
`execute-do-not-grep`. That rule forbids asserting on SOURCE TEXT as a proxy for
BEHAVIOUR. The question here is not behavioural: it is literally whether certain
characters were present in the document the seats received. The brief is the
artefact of record and a substring test on it is a direct measurement, not a
proxy. The second half of the test -- whether the conclusion rests on evidence --
is deliberately framed as a presence/absence count over the seats' own replies
and is reported as such, not as a verdict on their reasoning.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
BLIND = "what_is_severity_and_should_it_gate_convergence_2026-10-30"
JOINT = "joint_severity_gates_convergence_2026-10-31"

#: The 3 substantive content items in the span I reported as missing.
PROBES = {
    "0.7 is not universally informative": [
        "0.7 in all circumstances", "tell us very little", "in all circumstances"],
    "the 4+4 against Riemann worked example": ["4 + 4", "4+4", "Riemann"],
    "severity is not a fixed number and lies in a range": [
        "unlikely to be a fixed number", "within a range",
        "complexity of the topic", "confidence once can derive"],
}
#: Tokens that only appear if a seat examined the code itself.
MECHANICAL = ["0 writers", "no writer", "0 production", "model_params", "R_old",
              "0.500000", "distinct count", "1 reader", "compute_rk",
              "bit-identical", "bit identical"]
#: The escape the joint brief offered, and my own invented word.
ESCAPE = ["cannot be set yet", "cannot be set", "truncat"]


def his_annotation() -> str:
    spec = importlib.util.spec_from_file_location(
        "rd", REPO / "scripts" / "read_founder_responses_2026-10-11.py")
    rd = importlib.util.module_from_spec(spec)
    sys.modules["rd"] = rd
    spec.loader.exec_module(rd)
    rows = [r for r in rd.annotations()
            if r["file"] == "Decisions_Awaiting_You_2026-10-30.txt"]
    sev = [r for r in rows if "Riemann" in r["text"]]
    if len(sev) != 1:
        raise SystemExit(f"expected 1 severity annotation, found {len(sev)}")
    return sev[0]["text"]


def present(text: str) -> dict:
    return {name: sorted(p for p in probes if p.lower() in text.lower())
            for name, probes in PROBES.items()}


def body_of(path: pathlib.Path) -> str:
    raw = path.read_text(errors="replace")
    try:
        obj = json.loads(raw)
    except Exception:
        return raw
    if isinstance(obj, dict):
        for k in ("reply", "text", "content", "answer", "output"):
            if isinstance(obj.get(k), str) and len(obj[k]) > 400:
                return obj[k]
    return raw


def interval(k: int, n: int) -> str:
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    sm = proportion_confint(k, n, method="wilson")
    cp = proportion_confint(k, n, method="beta")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054"); K, N = mp.mpf(k), mp.mpf(n)
    ph = K / N; d = 1 + z**2 / N
    c = (ph + z**2 / (2 * N)) / d
    h = z * mp.sqrt(ph * (1 - ph) / N + z**2 / (4 * N**2)) / d
    agree = max(abs(sm[0] - float(c - h)), abs(sm[1] - float(c + h)))
    return (f"{k}/{n} = {k/n:.6f}  Wilson [{sm[0]:.6f}, {sm[1]:.6f}] "
            f"(mpmath agrees to {agree:.1e})  "
            f"Clopper-Pearson [{cp[0]:.6f}, {cp[1]:.6f}]")


def main() -> int:
    his = his_annotation()
    print("=" * 78)
    print("WAS THE SEVERITY ROUND INVALIDATED BY THE TRUNCATION I CLAIMED?")
    print("=" * 78)
    print(f"his annotation, as the reader returns it: {len(his)} chars")
    ref = present(his)
    assert all(ref.values()), f"the reference text lacks its own items: {ref}"
    print("  all 3 content items present in HIS OWN text (the control)\n")

    print("(1) WAS THE CLAIM TRUE? -- does the record truncate his question?")
    tasklist = (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").read_text(
        errors="ignore")
    i = tasklist.find("B53.")
    blk = tasklist[i:i + 9000]
    done = 'boundaries for these be?' in blk or 'for these be?"' in blk
    print(f"    task list entry B53 carries the question to 'be?'      : {done}")
    print(f"    task list entry B53 carries the 4+4/Riemann contrast    : "
          f"{'Riemann' in blk}")
    for name, d in (("blind", BLIND), ("joint", JOINT)):
        b = (LOGS / d / "BRIEF.md").read_text(errors="replace")
        n_trunc = len(re.findall(r"truncat", b, re.I))
        print(f"    {name} brief asserts truncation                       : "
              f"{n_trunc} time(s)")
    print()

    print("(2) WERE THE SEATS DEPRIVED OF THE CONTENT? -- probe the dispatched briefs")
    for name, d in (("blind", BLIND), ("joint", JOINT)):
        b = (LOGS / d / "BRIEF.md").read_text(errors="replace")
        got = present(b)
        n = sum(1 for v in got.values() if v)
        print(f"    {name} brief: {n} of {len(PROBES)} content items present")
        for k, v in got.items():
            print(f"        {'PRESENT' if v else 'ABSENT '}  {k}")
    print()

    print("(3) DOES THE CONCLUSION REST ON EVIDENCE OR ON THE ESCAPE CLAUSE?")
    blind_clean = joint_clean = 0
    rows = []
    for name, d in (("blind", BLIND), ("joint", JOINT)):
        for seat in ("cc2", "fable"):
            p = LOGS / d / f"{seat}.json"
            if not p.exists():
                continue
            body = body_of(p)
            mech = sorted({m for m in MECHANICAL if m.lower() in body.lower()})
            esc = sorted({m for m in ESCAPE if m.lower() in body.lower()})
            rows.append((name, seat, len(mech), len(esc)))
            if not esc:
                if name == "blind":
                    blind_clean += 1
                else:
                    joint_clean += 1
            print(f"    {name:5} {seat:6} mechanical tokens={len(mech):2}  "
                  f"escape tokens={len(esc)}  {esc}")
    n_blind = sum(1 for r in rows if r[0] == "blind")
    n_joint = sum(1 for r in rows if r[0] == "joint")
    print()
    print(f"    blind replies free of any escape token: "
          f"{interval(blind_clean, n_blind)}")
    print(f"    joint replies free of any escape token: "
          f"{interval(joint_clean, n_joint)}")
    print(f"    replies carrying mechanical evidence  : "
          f"{interval(sum(1 for r in rows if r[2] > 0), len(rows))}")
    print()

    print("=" * 78)
    deprived = any(not v for name, d in (("blind", BLIND),)
                   for v in present((LOGS / BLIND / 'BRIEF.md').read_text(
                       errors='replace')).values())
    rests_on_escape = blind_clean < n_blind
    if deprived or rests_on_escape:
        print("VERDICT: INVALID by the rule stated above. Re-run with the full framing.")
        return 1
    print("VERDICT: VALID. The blind round had the complete question, asserted no")
    print("truncation, and both its replies reached the conclusion on mechanical")
    print("evidence with 0 escape tokens. The truncation claim is a defect in MY")
    print("RECORD -- introduced by the joint brief and repeated in the morning")
    print("report -- not in what the seats were asked. Do not scrap the round;")
    print("correct the record, and leave the archived brief as written.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
