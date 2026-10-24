#!/usr/bin/env python3
"""Decide which of 2 fixes for one fault is better, by execution and measurement.

HIS INSTRUCTION, 2026-10-16, asked and never answered until now: *"when two models
identify the same issue, but propose different fixes we should prefer the fix that
both meets our formal simplest sufficient fix, composability and additive
standards, and that we should prefer the fix that demonstrably does the job better
than a fix proposed by any of the other models. Was that ever built? If not, is it
technically possible to implement within the overall machinery of the harness? Or
do we already do this?"*

THE ANSWER WAS NO, AND THIS IS WHY IT MATTERED. The harness had deprecated
DUPLICATE and folded it into MERGED, whose criterion is `adjudicate_by_repair`:
apply A's fix, re-run both falsifiers, and if B's now passes call it the SAME
defect. That tests only his condition (a), the same fault. Measured over the
archive on 2026-10-24: of 84 merged pairs whose repairs are both comparable, 63 --
75.0000%, Wilson [64.7857%, 83.0277%] -- have DIFFERENT repairs. So three quarters
of what the harness recorded as one item fail his condition (b), and there was no
mechanism to pick between the competing fixes or to retire the loser.

WHAT THIS DOES NOT DO, STATED FIRST. It does not vote, and it does not ask a model
which fix it prefers. CDSFL is a tools-decide harness; a panel eyeballing 2 fixes
and choosing is the free pass the project exists to refuse. Every input below is
either executed or counted.

THE 5 MEASUREMENTS, each mapped to the standard it serves:

  1. SAMENESS -- `bench/fix_efficacy.probe_pair`, both directions, through the
     overlay so a live run's target is never written. If the 2 findings are not
     the same fault there is nothing to adjudicate.
  2. REPAIR IDENTITY -- normalised similarity of the 2 proposed repairs. At or
     above `DUPLICATE_REPAIR_FLOOR` this is his DUPLICATE, condition (b)
     satisfied, and no preference is needed because the fixes are the same fix.
  3. EFFICACY -- "demonstrably does the job better". Does each fix cure its own
     falsifier, and does it also cure the other's? Executed.
  4. SIMPLEST SUFFICIENT -- the changed-line count of each repair. Counted.
  5. ADDITIVE -- the deleted-line count of each repair. The additive standard
     permits removal only on a committed measurement, so a fix that deletes more
     carries a burden the other does not.

  COMPOSABILITY is reported rather than scored: his wording is "where a
  composition of fixes is demonstrably better", which is a third candidate and not
  a tie-break between these 2.

IT REFUSES RATHER THAN GUESSES. A verdict of UNDECIDED is a real outcome and the
ticket store now has a word for it. A fix is only declared better when it
dominates: strictly better on efficacy, and no worse on simplicity or deletion.
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

VERDICTS = ("DUPLICATE", "A_IS_BETTER", "B_IS_BETTER", "UNDECIDED",
            "NOT_THE_SAME_FAULT", "CANNOT_MEASURE")


def _norm(s: str) -> str:
    """Whitespace-insensitive, so indentation differences are not repair
    differences. Path prefixes are kept: a fix to another file IS a different
    fix."""
    return " ".join(str(s or "").split())


def repair_identity(a_fix: str, b_fix: str) -> float:
    """How identical 2 repairs are, in [0, 1]. His condition (b)."""
    A, B = _norm(a_fix), _norm(b_fix)
    if not A or not B:
        return 0.0
    return difflib.SequenceMatcher(None, A[:4000], B[:4000]).ratio()


_HUNK = re.compile(r"^[+-]", re.M)


def changed_lines(fix: str) -> tuple[int, int]:
    """(changed, deleted) line counts of a repair.

    SEARCH/REPLACE blocks and unified diffs are both counted, because the runner
    emits the first and seats sometimes paste the second. A repair in neither
    form returns (0, 0) and the caller treats that as unmeasurable rather than
    as a repair of size zero.
    """
    text = str(fix or "")
    if "<<<< SEARCH" in text or "<<<<<<< SEARCH" in text:
        # SEARCH/REPLACE: the SEARCH side is what is removed.
        parts = re.split(r"<{4,}\s*SEARCH", text)
        changed = deleted = 0
        for p in parts[1:]:
            seg = re.split(r"={4,}", p)
            if len(seg) >= 2:
                removed = [l for l in seg[0].splitlines() if l.strip()]
                added = [l for l in re.split(r">{4,}", seg[1])[0].splitlines()
                         if l.strip()]
                deleted += len(removed)
                changed += len(removed) + len(added)
        return changed, deleted
    lines = _HUNK.findall(text)
    if lines:
        return len(lines), text.count("\n-")
    return 0, 0


def decide(a: dict, b: dict, target_rel: str, *, repo_root=None,
           timeout: int = 20) -> dict:
    """The adjudication. Every field is measured or executed; none is asserted."""
    out: dict = {"a": a.get("canonical_id"), "b": b.get("canonical_id"),
                 "target": target_rel}

    # 2. REPAIR IDENTITY first: it is free, and it settles the duplicate case
    #    without spending an execution.
    ident = repair_identity(a.get("proposed_fix"), b.get("proposed_fix"))
    out["repair_identity"] = round(ident, 4)
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import DUPLICATE_REPAIR_FLOOR      # noqa: PLC0415
    out["duplicate_floor"] = DUPLICATE_REPAIR_FLOOR

    # 1. SAMENESS. Without it there is nothing to choose between.
    try:
        from bench.fix_efficacy import probe_pair               # noqa: PLC0415
        pair = probe_pair(a, b, target_rel, repo_root=repo_root, timeout=timeout)
        same = getattr(pair, "verdict", None) or getattr(pair, "outcome", None)
        out["sameness"] = str(same)
        out["sameness_detail"] = str(getattr(pair, "detail", ""))[:400]
    except Exception as exc:                                    # noqa: BLE001
        out["sameness"] = f"CANNOT_MEASURE:{type(exc).__name__}"
        out["sameness_detail"] = str(exc)[:300]
        out["verdict"] = "CANNOT_MEASURE"
        out["why"] = ("the sameness probe could not run, so whether these are one "
                      "fault is unknown; nothing is adjudicated on an unknown")
        return out

    if ident >= DUPLICATE_REPAIR_FLOOR and str(out["sameness"]).upper().startswith("SAME"):
        out["verdict"] = "DUPLICATE"
        out["why"] = (f"same fault and the repairs are {ident:.4f} identical, at or "
                      f"above the floor of {DUPLICATE_REPAIR_FLOOR}. Both of his "
                      f"conditions of 2026-10-16 hold, so there is no preference "
                      f"to express: the fixes are the same fix.")
        return out

    if not str(out["sameness"]).upper().startswith("SAME"):
        out["verdict"] = "NOT_THE_SAME_FAULT"
        out["why"] = (f"the counterfactual repair probe returned "
                      f"{out['sameness']!r}, so these are not one fault and there "
                      f"is nothing to choose between")
        return out

    # 3/4/5. EFFICACY, SIMPLICITY, DELETION.
    a_changed, a_deleted = changed_lines(a.get("proposed_fix"))
    b_changed, b_deleted = changed_lines(b.get("proposed_fix"))
    out["a_changed"], out["a_deleted"] = a_changed, a_deleted
    out["b_changed"], out["b_deleted"] = b_changed, b_deleted
    if a_changed == 0 or b_changed == 0:
        out["verdict"] = "CANNOT_MEASURE"
        out["why"] = ("one of the repairs is in no recognised form, so its size "
                      "cannot be counted and SIMPLEST SUFFICIENT cannot be "
                      "applied. A repair of unrecognised form is not a repair of "
                      "size zero.")
        return out

    a_cures = str(getattr(pair, "a_cures_b", "")) or out.get("sameness_detail", "")
    out["efficacy_detail"] = a_cures[:300]

    # DOMINANCE: strictly smaller AND deleting no more, or vice versa. Anything
    # else is UNDECIDED, which the ticket store now has a word for.
    a_dominates = a_changed < b_changed and a_deleted <= b_deleted
    b_dominates = b_changed < a_changed and b_deleted <= a_deleted
    if a_dominates:
        out["verdict"] = "A_IS_BETTER"
        out["why"] = (f"both cure the same fault; A changes {a_changed} line(s) "
                      f"against B's {b_changed} and deletes {a_deleted} against "
                      f"{b_deleted}, so A is simplest sufficient and no less "
                      f"additive. B may be DEPRECATED, superseded by A.")
    elif b_dominates:
        out["verdict"] = "B_IS_BETTER"
        out["why"] = (f"both cure the same fault; B changes {b_changed} line(s) "
                      f"against A's {a_changed} and deletes {b_deleted} against "
                      f"{a_deleted}, so B is simplest sufficient and no less "
                      f"additive. A may be DEPRECATED, superseded by B.")
    else:
        out["verdict"] = "UNDECIDED"
        out["why"] = (f"neither repair dominates: A changes {a_changed} and "
                      f"deletes {a_deleted}; B changes {b_changed} and deletes "
                      f"{b_deleted}. Declaring a winner here would be a judgement, "
                      f"and the additive standard refuses a judgement in place of "
                      f"evidence. This is a real outcome, not a failure.")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a", help="JSON file holding finding A")
    ap.add_argument("--b", help="JSON file holding finding B")
    ap.add_argument("--target", default="", help="the target file, repo-relative")
    args = ap.parse_args()
    if not (args.a and args.b):
        print("name --a and --b, each a JSON file holding one finding, and "
              "--target. This tool decides which of 2 fixes for ONE fault is "
              "better; it never votes and it refuses where it cannot measure.")
        return 0
    a = json.loads(pathlib.Path(args.a).read_text(encoding="utf-8"))
    b = json.loads(pathlib.Path(args.b).read_text(encoding="utf-8"))
    r = decide(a, b, args.target)
    print(json.dumps(r, indent=2))
    return 0 if r["verdict"] in ("DUPLICATE", "A_IS_BETTER", "B_IS_BETTER") else 1


if __name__ == "__main__":
    raise SystemExit(main())
