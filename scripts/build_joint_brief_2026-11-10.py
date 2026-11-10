#!/usr/bin/env python3
"""Build the JOINT half of any blind panel round, from the round's own replies.

HIS RULING, 2026-11-10: a joint round is run IMMEDIATELY after the blind round
it belongs to, and that has been the project's practice since its inception.
The instruction came after a blind round of mine was dispatched with the
topology gate overridden, which was the wrong call.

WHY THIS IS PARAMETERISED AND THE 2 PRECEDENTS ARE NOT. The project has written
1 brief builder PER ROUND -- `build_severity_joint_brief_2026-10-31.py` and
`build_period_joint_brief_2026-11-04.py` -- so the same lifting, quoting and
refusal logic exists twice and would have existed 4 times by the end of tonight.
This takes the round name as an argument. Neither precedent is removed: each
carries round-specific framing text this cannot reproduce, and under
`additive-standard` removal needs a committed measurement showing the
replacement dominates, which has not been taken.

THE ONE PROPERTY THAT MATTERS, and the gate in
`bench/confer_maths_panel_2026-09-05.py` enforces it rather than trusting the
declaration: a joint brief must QUOTE the parent round's landed replies, with a
240-character contiguous span of each surviving into the brief. Pointing a seat
at a sibling directory is not exposure -- nothing checks that the seat read it,
and measured on 2026-10-14 a brief pointed at directories that did not exist.
This builder embeds each reply IN FULL and then verifies the span condition
itself, refusing to write if it fails, so the failure arrives here rather than
at dispatch.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

for _c in (pathlib.Path(__file__).resolve().parent, pathlib.Path.cwd().resolve()):
    for _x in (_c, *_c.parents):
        if (_x / "bench" / "confer_maths_panel_2026-09-05.py").is_file():
            REPO = _x
            break
    else:
        continue
    break
else:
    raise SystemExit("cannot locate the repository")

LOGS = REPO / "bench" / "logs"
SPAN = 240


def _reply(path: pathlib.Path) -> str:
    j = json.loads(path.read_text(encoding="utf-8"))
    for k in ("response", "reply", "text", "output", "content"):
        v = j.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def build(parent: str, question: str, out_round: str) -> int:
    pdir = LOGS / parent
    if not pdir.is_dir():
        print(f"REFUSED: {parent} is not a round directory under bench/logs")
        return 2
    replies = {}
    for f in sorted(pdir.glob("*.json")):
        if f.name.endswith((".tools.attempt1.json", "topology.json")):
            continue
        if f.stem in ("topology", "completion_barrier", "sandbox_manifest",
                      "canonical_attribution", "canonical_touched",
                      "control_plane_touched"):
            continue
        body = _reply(f)
        if len(body) >= SPAN:
            replies[f.stem] = body
    if len(replies) < 2:
        print(f"REFUSED: {parent} has {len(replies)} reply/replies of at least "
              f"{SPAN} characters; a joint round needs 2 seats to expose to "
              f"each other")
        return 3

    odir = LOGS / out_round
    odir.mkdir(parents=True, exist_ok=True)
    seats = sorted(replies)

    L = [f"# PANEL BRIEF — JOINT ROUND on `{parent}`", "",
         f"This is the JOINT half of the blind round `{parent}`. In the blind "
         f"half each of the {len(seats)} seats answered WITHOUT seeing the "
         f"others. Both replies are reproduced BELOW IN FULL, verbatim. Read "
         f"the other seat's actual words before you answer.", "",
         "**Disagreement is INFORMATION and is preserved. There is no "
         "compelled convergence: do NOT move toward the other seat to be "
         "agreeable. Change your position only where its EVIDENCE moves you, "
         "and say which evidence did. Where you still disagree, say so and "
         "say what would settle it.**", "",
         "## THE PROJECT, ITS AIMS, AND ITS SPECIFICATIONS — read before answering",
         "",
         "CDSFL is a falsification harness. Its aim is the democratisation of "
         "science for every kind of intelligence, so a mechanism that only "
         "works on code, or only on this machine, is a mechanism that misses "
         "the point. The 3 formal standards below are exacting and are not "
         "loose English.", "",
         "1. **ADDITIVE** — work adds to reliability, functionality, accuracy, "
         "robustness and the project's stated aims. A feature is never "
         "disabled or removed; removal only where a COMMITTED MEASUREMENT "
         "shows the replacement dominates on a NAMED property. Symmetrically, "
         "an addition nothing reaches is not additive either: every new flag, "
         "gate or entry point must be wired to a caller and executed by a test.",
         "2. **SIMPLEST SUFFICIENT** — the smallest change addressing the ROOT "
         "CAUSE and the downstream consequences traced before the fix.",
         "3. **COMPOSABILITY** — the founder, verbatim, 2026-10-02: "
         "\"Composability doesn't mean composing two solutions just because "
         "they can be composed. It means this principle should be applied "
         "where two composed solutions demonstrably provide a better, more "
         "robust and/or more efficient solution than either fix in isolation. "
         "Where a single fix out performs a composed one, that fix should "
         "continue to be preferred. In all cases any fix should also take the "
         "first two conditions fully into consideration also.\" So a composed "
         "fix needs a MEASUREMENT showing it dominates either part alone. "
         "\"They do not conflict\" is the weak sense his wording excludes.", "",
         "Work under `a` (analyse dispassionately), `f` (FFAFP: Find, Follow, "
         "Analyse with tools, Fix, P-pass) and `sy` (use the STEM tools; every "
         "computational claim cross-verified by 2 independent tools; every "
         "proportion carries a confidence interval). The tool output IS the "
         "evidence. **Findings are confirmed programmatically or by the "
         "founder — there is no model voting.**", "",
         "## REQUIRED SECTION 1 — The question", "", question, "",
         "## REQUIRED SECTION 2 — Use the harness", "",
         "Read and RUN the code. Do not reason from the brief alone. Do not "
         "invoke pytest across the whole tree: the heavy-process budget on "
         "this machine is 1, and a full board is already cached. Targeted test "
         "files are fine.", "",
         "## REQUIRED SECTION 3 — Produce a fix, and test it", "",
         "Where you find a defect, deliver the fix and the executed evidence "
         "that it works, including what you tried that did NOT work. **WRITE "
         "YOUR FIX INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH.** A fix "
         "left in prose, or written to scratch space, is destroyed when the "
         "sandbox is torn down and has not been delivered. Supply a runnable "
         "falsifier, EXECUTE it, and quote its output.", "",
         "## REQUIRED SECTION 4 — What would refute you", "",
         "State, for each position you hold, the observation that would "
         "overturn it. A position with no falsifier is not a finding.", "",
         "## REQUIRED SECTION 5 — Output shape", "",
         "`verdict`, `composability`, `reasoning`, `falsifier`, "
         "`falsifier_result`, `strongest_disagreement`, `aims_check`. In "
         "`strongest_disagreement` name the specific claim of the OTHER SEAT "
         "you reject, and why, with evidence.", "",
         "## REQUIRED SECTION 6 — Termination", "",
         "Stop when a pass produces no new above-threshold finding. State how "
         "many passes you ran.", "",
         "---", "",
         f"# THE BLIND HALF — all {len(seats)} replies, verbatim and in full", ""]

    for seat in seats:
        L += [f"## SEAT `{seat}` — its blind reply, verbatim", "",
              "<!-- verbatim-begin -->", "", replies[seat], "",
              "<!-- verbatim-end -->", ""]

    text = "\n".join(L)

    # ★ VERIFY THE GATE'S OWN CONDITION HERE, so a failure arrives at build
    # time rather than at dispatch. A 240-character contiguous span of EACH
    # reply must survive into the brief.
    missing = [s for s in seats if replies[s][:SPAN] not in text]
    if missing:
        print(f"REFUSED: no {SPAN}-character span of these seats' replies "
              f"survives into the brief: {missing}")
        return 4

    (odir / "BRIEF.md").write_text(text, encoding="utf-8")
    print(f"wrote {odir / 'BRIEF.md'}  ({len(text)} chars)")
    print(f"  parent        : {parent}")
    print(f"  seats quoted  : {seats}")
    for s in seats:
        print(f"    {s:8s} {len(replies[s]):>7d} chars embedded verbatim")
    print(f"  {SPAN}-char span of each reply present: True")
    #: ★ THE ROUND NAME IS A POSITIONAL ARGUMENT, NOT AN ENV VAR. The first
    #: version of this line printed `PANEL_ROUND=<name>`, which does not
    #: exist: the dispatcher reads `sys.argv[1]` and refuses with its usage
    #: line in under 1 second. Both joint rounds were dispatched from that
    #: wrong instruction and both exited 2 immediately. Verified against the
    #: dispatcher's own argument handling rather than from memory.
    print(f"\nDispatch with:")
    print(f"  PANEL_JOINT_OF={parent} PANEL_ONLY={','.join(seats)} \\")
    print(f"    python3 bench/confer_maths_panel_2026-09-05.py {out_round}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("parent", nargs="?", help="the blind round to pair")
    ap.add_argument("--question", default="",
                    help="REQUIRED SECTION 1 text; defaults to a generic re-ask")
    ap.add_argument("--out", default="",
                    help="the new round name (default: <parent>_joint)")
    a = ap.parse_args(argv)
    if not a.parent:
        ap.error("a parent round is required")
    q = a.question or (
        "Re-answer the question you were given in the blind half, having now "
        "read the other seat's reply in full. Where it found something you "
        "missed, say so and verify it yourself rather than accepting it. "
        "Where it is wrong, refute it by execution.")
    return build(a.parent, q, a.out or f"{a.parent}_joint")


if __name__ == "__main__":
    raise SystemExit(main())
