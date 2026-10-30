#!/usr/bin/env python3
"""Does `ds` as a ticket kind collide with `ds` the DeepSeek seat, and what
else does the harvester's hand-written kind allow-list already drop?

FOUNDER RULING 2026-10-30, verbatim from his annotation of
`Decisions_Awaiting_You_2026-10-30.txt` line 187:

    "If a comment I make has no marker, and does not end with a question
    mark, then treat it as a ds. fr"

`ds` IS ALREADY TAKEN. It is the DeepSeek V4 Pro seat in the panel dispatch
table of `.claude/CLAUDE.md`. That is the identical situation which forced
`pf` over his proposed `pr` on 2026-10-17, so it is measured the same way
rather than argued: the `pr` collision was REALISED -- 4 of 4 of his real
panel-review usages were harvested as proposed fixes before the rename.

THREE SEPARATE QUESTIONS, because conflating them is how the `pr` decision
nearly went the other way:

  Q1 Does the collision bite in his ANNOTATIONS, which is where a marker is
     written? A seat name appears there as prose, not as a marker.
  Q2 Does it bite in CHAT, which the harvester also reads and which is where
     a dispatch instruction ("cx ge ds") is actually typed?
  Q3 Independently of `ds`: the harvester tests his marker against a
     HAND-WRITTEN tuple ("fr", "pf", "qs") while the vocabulary itself is
     `ticket_store.KINDS`, which has carried `wr` since 2026-10-19. A
     duplicate of a vocabulary is a vocabulary that can disagree with itself.

Q3 is the root cause and `ds` is only the occasion for finding it. The fix is
to test against KINDS, so a kind added once reaches every reader.

Cross-verification per the 21 Apr 2026 rule: every proportion carries a
Wilson interval from statsmodels AND a hand-derived Wilson from the closed
form, and the exact binomial tail from scipy AND mpmath.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import subprocess
import sys

import mpmath
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
RESPONSES = pathlib.Path("/Users/georgejackson/Developer_Projects/Responses")
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"

#: The seats, from the dispatch table in `.claude/CLAUDE.md`. `ds` is one.
SEATS = ("cc2", "cx", "ge", "cgpt", "ds", "fable")

#: `ds` as a standalone token. Deliberately the same shape as the harvester's
#: own MARKER: a boundary on the left, punctuation or whitespace on the right.
DS_TOKEN = re.compile(r"(?:(?<=^)|(?<=[\s(\[“'\"]))ds(?:[:\]\),.;'\"”]|\s|$)", re.M)

#: A seat USE, not a mention of the word: `ds` with another seat beside it, or
#: a dispatch verb within 60 characters. One seat alone is ambiguous; two are
#: a panel.
OTHER_SEATS = re.compile(r"\b(cc2|cx|ge|cgpt|fable)\b")
DISPATCH_VERB = re.compile(r"\b(confer|dispatch|panel|seat|run it (?:by|past)|ask)\b", re.I)


def wilson_two_ways(k: int, n: int) -> tuple[tuple[float, float], tuple[float, float]]:
    """Wilson 95% from statsmodels and from the closed form, to agree."""
    if n == 0:
        return (float("nan"), float("nan")), (float("nan"), float("nan"))
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (float(lo_sm), float(hi_sm)), ((c - h) / d, (c + h) / d)


def binom_tail_two_ways(k: int, n: int, p0: float) -> tuple[float, float]:
    """P(X <= k) under Binomial(n, p0), from scipy and from mpmath exactly."""
    sp = float(stats.binom.cdf(k, n, p0))
    with mpmath.workdps(60):
        mp = mpmath.nsum(
            lambda i: mpmath.binomial(n, int(i)) * mpmath.mpf(p0) ** int(i)
            * (1 - mpmath.mpf(p0)) ** (n - int(i)),
            [0, k],
        )
    return sp, float(mp)


def annotations() -> list[dict]:
    out = subprocess.run(
        [sys.executable, str(READER), "--since", "2026-01-01", "--json"],
        capture_output=True, text=True, cwd=str(REPO), check=True,
    )
    return json.loads(out.stdout)["annotations"]


def classify_ds(text: str) -> str:
    """MARKER, SEAT or MENTION for a text containing `ds` as a token."""
    m = DS_TOKEN.search(text)
    if m is None:
        return "ABSENT"
    window = text[max(0, m.start() - 80):m.end() + 40]
    # His marker convention: the token sits at the very END of the annotation,
    # after the full stop, alone or beside another marker.
    tail = text.rstrip().rstrip(".")
    if re.search(r"(?:^|[\s,])ds\.?$", tail):
        return "MARKER"
    if OTHER_SEATS.search(window) or DISPATCH_VERB.search(window):
        return "SEAT"
    return "MENTION"


def q1_annotations(anns: list[dict]) -> dict:
    hit = [a for a in anns if DS_TOKEN.search(a["text"])]
    tally = collections.Counter(classify_ds(a["text"]) for a in hit)
    n = len(anns)
    k = tally.get("SEAT", 0)
    sm, closed = wilson_two_ways(k, n)
    return {"annotations": n, "ds_token": len(hit), "tally": dict(tally),
            "seat_uses": k, "wilson_statsmodels": sm, "wilson_closed_form": closed,
            "examples": [{"file": a["file"], "line_index": a["line_index"],
                          "class": classify_ds(a["text"]),
                          "tail": a["text"].rstrip()[-70:]} for a in hit]}


def q2_chat() -> dict:
    """His own messages across every session transcript."""
    root = pathlib.Path.home() / ".claude" / "projects"
    seat_uses = marker_uses = total = 0
    examples: list[str] = []
    for p in sorted(root.rglob("*.jsonl")):
        try:
            with p.open(errors="replace") as fh:
                for line in fh:
                    if '"type":"user"' not in line and '"type": "user"' not in line:
                        continue
                    if "ds" not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    msg = rec.get("message") or {}
                    content = msg.get("content")
                    if isinstance(content, list):
                        txt = " ".join(c.get("text", "") for c in content
                                       if isinstance(c, dict))
                    else:
                        txt = str(content or "")
                    if not txt or not DS_TOKEN.search(txt):
                        continue
                    total += 1
                    cls = classify_ds(txt)
                    if cls == "SEAT":
                        seat_uses += 1
                        if len(examples) < 8:
                            examples.append(txt.strip()[:120])
                    elif cls == "MARKER":
                        marker_uses += 1
        except OSError:
            continue
    sm, closed = wilson_two_ways(seat_uses, total) if total else ((float("nan"),) * 2,) * 2
    return {"his_messages_with_ds_token": total, "seat_uses": seat_uses,
            "marker_uses": marker_uses, "wilson_statsmodels": sm,
            "wilson_closed_form": closed, "examples": examples}


def q3_allowlist(anns: list[dict]) -> dict:
    """What the hand-written tuple drops that KINDS would not."""
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import KINDS

    hand = ("fr", "pf", "qs")
    dropped = tuple(k for k in KINDS if k not in hand)
    # Execute the two forms against his real markers rather than read them.
    def kind_hand(marker: str) -> str:
        mk = marker.split(",")[0].strip().lower()
        return (mk if mk in hand else "") or "pf"

    def kind_kinds(marker: str) -> str:
        mk = marker.split(",")[0].strip().lower()
        return (mk if mk in KINDS else "") or "pf"

    disagree = []
    for a in anns:
        mk = str(a.get("marker") or "")
        if not mk:
            continue
        h, k = kind_hand(mk), kind_kinds(mk)
        if h != k:
            disagree.append({"file": a["file"], "line_index": a["line_index"],
                             "marker": mk, "hand": h, "kinds": k})
    return {"KINDS": list(KINDS), "hand_written": list(hand),
            "dropped_by_hand_list": list(dropped),
            "his_marked_annotations": sum(1 for a in anns if a.get("marker")),
            "disagreements": disagree, "disagreement_count": len(disagree)}


def q4_question_mark(anns: list[dict]) -> dict:
    """Reach of the two halves of his default rule, over unmarked annotations."""
    unmarked = [a for a in anns if not (a.get("marker") or "").strip()]
    ends_q = [a for a in unmarked if a["text"].rstrip().endswith("?")]
    n, k = len(unmarked), len(ends_q)
    sm, closed = wilson_two_ways(k, n)
    sp, mp = binom_tail_two_ways(k, n, 0.5)
    return {"unmarked": n, "ends_with_question_mark": k,
            "would_become_qs": k, "would_become_ds": n - k,
            "share_qs": k / n if n else float("nan"),
            "wilson_statsmodels": sm, "wilson_closed_form": closed,
            "binom_cdf_scipy": sp, "binom_cdf_mpmath": mp}


def main() -> int:
    anns = annotations()
    report = {"q1_his_annotations": q1_annotations(anns),
              "q2_his_chat": q2_chat(),
              "q3_allowlist": q3_allowlist(anns),
              "q4_default_rule_reach": q4_question_mark(anns)}
    print(json.dumps(report, indent=2, default=str))
    q1, q2, q3, q4 = (report["q1_his_annotations"], report["q2_his_chat"],
                      report["q3_allowlist"], report["q4_default_rule_reach"])
    print("\n--- SUMMARY ---")
    print(f"Q1 annotations: {q1['seat_uses']} of {q1['annotations']} use `ds` as a SEAT; "
          f"Wilson {q1['wilson_statsmodels'][0]:.6f} to {q1['wilson_statsmodels'][1]:.6f}")
    print(f"Q2 chat: {q2['seat_uses']} of {q2['his_messages_with_ds_token']} "
          f"messages carrying the token use it as a SEAT")
    print(f"Q3 allow-list drops {q3['dropped_by_hand_list']}; "
          f"{q3['disagreement_count']} of his {q3['his_marked_annotations']} "
          f"marked annotations are misfiled by the hand-written tuple")
    print(f"Q4 default rule: {q4['ends_with_question_mark']} of {q4['unmarked']} "
          f"unmarked become qs, {q4['would_become_ds']} become ds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
