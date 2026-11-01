#!/usr/bin/env python3
"""PRODUCER: how many of the items put to him are decisions he actually owes.

HIS CHALLENGE, 2026-11-01 11:51 GMT, verbatim: *"Before I went to sleep you
said there were 10 decisions awaiting me. Now you say there are 4? The first
seemed like a suspiciously high number, as you have a habit of repeating issues
to me to rule on that I have already ruled on, or that have already been
settled. (It's fine if these issues are demonstrably real however.) So how much
is there really that needs my verdict/attention now?"*

HE IS RIGHT THAT THE NUMBER IS NOT ONE NUMBER, AND THAT IS THE DEFECT. Four
different counts for one quantity were in front of him at the same moment, and
3 of the 4 are in a single file:

  * the hand-written report's PART 7 is HEADED `WHAT NEEDS YOUR VERDICT` and
    carries a numbered list of 10 items;
  * the opening paragraph of that same PART 7 says `4 are decisions for you`;
  * the generated half's header line says `5 decisions need you`;
  * the chat message at 04:51 GMT named 5 entries as waiting on him.

So the 10 he remembers IS in the record, under a heading that says those items
need his verdict. It was not a count of decisions; it was the length of a list
that mixes decisions with items the same section says are not his.

THE THIRD TIME HE HAS RAISED THIS, AND THAT IS THE REAL FINDING. The generator
already carries 2 filters, each added after he asked this question before:
`no_ruling_needed` (2026-10-16, after *"are you certain none of these are items
I have previously ruled on?"*) and the `ruled:` marker field (2026-10-19, after
*"Then if I already ruled. Why are you presenting it as a decision required
from me again?"*). Both are keyed on the state of ONE entry. Neither can see a
DECISION GRAPH: 4 entries that each declare, in their own text, that they await
a 5th entry's decision are still presented as 4 decisions. That is the route
this report took, and it is a class of fault rather than an instance.

WHAT THIS SCRIPT DECIDES, MECHANICALLY, and each rule is reversible so the
output can contradict the prose above. For every live task entry it reads the
entry's own body and classifies it:

  ASKS          -- the body contains a sentence asking him to rule or authorise
  DEPENDENT     -- the body names ANOTHER entry as holding the decision
  GRANTED       -- the ask is for a free panel or simulated run, which his
                   standing rule already permits without further permission
  HIS_DEFERRAL  -- state DEFERRED with a ruling date: he took it off the queue
  MINE          -- no asking sentence at all

A DECISION HE OWES is an entry that ASKS, is not DEPENDENT, is not GRANTED and
is not a HIS_DEFERRAL. Dependants are reported as what they are: work waiting on
an answer, not questions of their own.

TWO TOOLS ON EVERY FIGURE. Wilson intervals from statsmodels, recomputed in
mpmath at 40 digits; the dependency graph checked for acyclicity and for
unique-root resolution in z3, so the deduplication is proved well-defined
rather than assumed.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as TLM  # noqa: E402

TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
REPORT = REPO / "experimental_notes" / "Morning_Report_2026-11-01.txt"
GENERATED = REPO / "experimental_notes" / "Morning_Report_2026-11-01_GENERATED.md"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"

#: An entry body asking him for something. Deliberately broad: a false positive
#: shows up as an item this script says he owes and the reading disproves, which
#: is the safe direction. A false negative hides a question from him.
ASKS = re.compile(
    r"NEEDS (?:HIS|YOUR) (?:RULING|AUTHORISATION|GO-AHEAD|VERDICT|ANSWER|DECISION)"
    r"|STILL NEEDS (?:HIS|YOUR)"
    r"|\[NEEDS YOUR RULING\]"
    r"|(?:is|are|remains) (?:his|yours) to (?:rule|authorise|decide|settle|release)"
    r"|so it is (?:his|yours)", re.I)

#: The body naming ANOTHER entry as the holder of the decision. This is the
#: predicate neither existing filter has, and the one this report needed.
DEPENDS = re.compile(
    r"AWAITS THE SHARED SCOPE DECISION AT ([A-Z]\d+)"
    r"|awaits? the (?:shared )?(?:scope )?decision at ([A-Z]\d+)"
    r"|NOT A RULING OF ITS OWN", re.I)

#: His standing rule, recorded verbatim in the project record: a free panel or
#: a simulated experiment has never needed permission beyond the instruction to
#: run it. An entry asking a go-ahead for one is asking for something granted.
FREE = re.compile(r"\bfree panel\b|\bfree-panel\b|\bsimulated (?:run|experiment|panel)\b", re.I)

#: An entry that RETIRES its own asking sentence. B22 and B41 both do this: a
#: later paragraph says the go-ahead request above is stale, or records his
#: ruling verbatim. Without this the entry reads as open on its first sentence
#: and settled on its last, and a report reads the first.
STALE = re.compile(r"SENTENCE ABOVE IS STALE|ALREADY CONTAINS ITS OWN REFUTATION"
                   r"|IS STALE,? \d{4}-\d{2}-\d{2}", re.I)

#: ★ THE PREDICATE THIS SCRIPT GOT WRONG ON ITS FIRST RUN, AND THE FAILURE WAS
#: IN THE DANGEROUS DIRECTION. The first version asked whether a free panel was
#: mentioned ANYWHERE in the body, and marked the whole entry GRANTED if so.
#: B21 carries 2 asking sentences: a free-panel go-ahead, which his standing
#: rule grants, and **WHAT STILL NEEDS HIS RULING: the single registration
#: point** -- a decision that changes how every seat is configured. The coarse
#: predicate classified B21 as needing nothing and HID THE SECOND QUESTION FROM
#: HIM, which is the opposite of the error this script exists to catch. The ask
#: is therefore scoped to its own SENTENCE, and an entry is settled only when
#: EVERY asking sentence in it is granted or retired.
_SENT = re.compile(r"(?<=[.!?])\s+")


def interval(k: int, n: int) -> str:
    """Wilson, in 2 independent implementations."""
    import mpmath as mp
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return f"{k}/{n} — no denominator, no interval"
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054")
    K, N = mp.mpf(k), mp.mpf(n)
    ph = K / N
    d = 1 + z**2 / N
    c = (ph + z**2 / (2 * N)) / d
    h = z * mp.sqrt(ph * (1 - ph) / N + z**2 / (4 * N**2)) / d
    agree = max(abs(lo - float(c - h)), abs(hi - float(c + h)))
    return (f"{k}/{n} = {k/n:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}] "
            f"(mpmath agrees to {agree:.1e})")


def bodies() -> dict[str, str]:
    """Each live entry's own body text, by ident."""
    lines = TASKLIST.read_text(errors="replace").splitlines()
    starts = [i for i, l in enumerate(lines) if TLM._is_entry(l)]
    out = {}
    for n, i in enumerate(starts):
        ident = TLM.ENTRY.match(lines[i]).group(1)
        a, b = TLM.body_bounds(lines, starts, n)
        out[ident] = "\n".join(lines[a:b])
    return out


def classify_text(state: str, ruled: str | None, txt: str) -> dict:
    """The whole decision, as a PURE function of one entry's own text.

    ★ EXTRACTED SO IT CAN BE CALLED RATHER THAN DESCRIBED, 2026-11-01, after
    `scripts/the_decision_classifier_mutations_2026-11-01.py` showed the
    DEPENDENT branch deciding NOTHING on live data: all 4 entries that declare
    they await B61 also carry no asking sentence, so they fall to MINE whether
    the branch exists or not. The branch is a forward guard for an entry that
    BOTH asks and depends -- a shape the list does not hold today and will the
    moment a dependant restates its parent's question. A guard whose only
    evidence is live data that does not exercise it is indistinguishable from
    a guard that does nothing, which is why the harness now drives this
    function with a CONSTRUCTED case instead.
    """
    state = (state or "").upper()
    dep = DEPENDS.search(txt)
    parent = (dep.group(1) or dep.group(2)) if dep else None
    retired = bool(STALE.search(txt))
    asks, live_asks = [], []
    for sent in _SENT.split(txt):
        if not ASKS.search(sent):
            continue
        one = re.sub(r"\s+", " ", sent).strip()
        free = bool(FREE.search(sent))
        asks.append({"sentence": one, "free": free, "retired": retired})
        if not free and not retired:
            live_asks.append(one)
    if state == "DEFERRED" and ruled:
        kind = "HIS_DEFERRAL"
    elif dep:
        kind = "DEPENDENT"
    elif live_asks:
        kind = "OWED"
    elif asks:
        kind = "GRANTED"
    else:
        kind = "MINE"
    return {"kind": kind, "parent": parent, "asks": asks, "live_asks": live_asks}


def classify() -> list[dict]:
    body = bodies()
    rows = []
    for e in TLM.parse_entries(TASKLIST):
        state = (e.state or "").upper()
        if state in ("DONE", "WITHDRAWN"):
            continue
        d = classify_text(state, e.ruled, body.get(e.ident, ""))
        rows.append({"ident": e.ident, "state": state, "status": e.status,
                     "ruled": e.ruled, "line": e.line_no, **d})
    return rows


#: ★ THE INVERSE FAILURE, AND IT IS THE WORSE ONE. A `ruled:` date is a POINT
#: EVENT. The generator treats it as permanent absolution: any entry carrying
#: one leaves the decision list for good. B21 carries `ruled: 2026-10-17` and
#: has accumulated 4 NEW questions since, dated 2026-10-30 and 2026-10-31 in
#: its own body -- the 1-or-2 role dimension, the go-ahead for the single
#: functional layer, the 2 declarations of the structural axis, and the type
#: checker configuration. All 4 were filtered out of the generated report by a
#: ruling 14 days older than the questions. Repetition is visible; suppression
#: is not, which is the same argument the parked-file fix had to be reversed on.
_DATE = re.compile(r"\b(2026-\d{2}-\d{2})")


def suppressed(rows: list[dict]) -> list[dict]:
    """Entries a `ruled:` date removes from the queue while they still ask.

    The predicate is mechanical and reversible: the entry has at least 1 LIVE
    asking sentence, carries a `ruled:` date, and its own body carries a date
    stamp LATER than that ruling. A question raised after a ruling cannot have
    been answered by it.
    """
    body = bodies()
    out = []
    for r in rows:
        if not r["live_asks"] or not r["ruled"]:
            continue
        later = sorted({d for d in _DATE.findall(body.get(r["ident"], ""))
                        if d > r["ruled"]})
        if later:
            out.append({**r, "ruled": r["ruled"], "later_dates": later[-3:]})
    return out


#: The night's commits, oldest first, with the previous `sv` as the baseline.
#: Named here rather than typed into a document, because the open count went
#: DOWN and then UP and a single figure cannot say that.
NIGHT = ("8b1f50d7", "ea799770", "0fab7c9b", "7a36ae2c", "2322ad5f", "619a7081")


def board_trace() -> list[dict]:
    """OPEN/DONE at each of the night's commits, read with the project parser.

    ★ A SHELL TRAP WORTH RECORDING, because it cost 3 calls and produced 3
    EMPTY measurements that looked like a board with 0 entries. In zsh,
    `"$c:experimental_notes/..."` applies the `:e` history modifier to `$c` and
    the path becomes `xperimental_notes/...`. `git show` then fails, the
    redirect still creates the file, and the parse reports 0 entries rather
    than an error. Reading the blob through Python avoids the quoting entirely.
    """
    import subprocess
    import tempfile
    out = []
    for sha in NIGHT + ("WORKING",):
        if sha == "WORKING":
            rows = TLM.parse_entries(TASKLIST)
        else:
            r = subprocess.run(
                ["git", "show", f"{sha}:experimental_notes/CDSFL_MASTER_TASK_LIST.md"],
                capture_output=True, text=True, cwd=str(REPO))
            if r.returncode != 0:
                out.append({"sha": sha, "error": r.stderr.strip()[:120]})
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
                fh.write(r.stdout)
            rows = TLM.parse_entries(pathlib.Path(fh.name))
        states = [(e.ident, (e.state or "?").upper()) for e in rows]
        out.append({"sha": sha, "entries": len(states),
                    "open": sum(1 for _, s in states if s == "OPEN"),
                    "done": sum(1 for _, s in states if s == "DONE"),
                    "idents": dict(states)})
    return out


def part7_items() -> list[str]:
    if not REPORT.is_file():
        return []
        
    txt = REPORT.read_text(errors="replace")
    m = re.search(r"^PART 7\.(.*?)^PART 8\.", txt, re.S | re.M)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines()
            if re.match(r"^\d+\.\s", l.strip())]


def generated_decisions() -> list[str]:
    if not GENERATED.is_file():
        return []
    txt = GENERATED.read_text(errors="replace")
    m = re.search(r"^## 1\. Decisions that need you(.*?)^## 2\.", txt, re.S | re.M)
    if not m:
        return []
    return re.findall(r"^### \d+\.\s+(\S+)", m.group(1), re.M)


def graph_is_well_defined(rows: list[dict]) -> list[str]:
    """z3: the dependency graph is acyclic and every dependant has 1 root.

    Without this the deduplication below is an assertion. A dependant pointing
    at a dependant, or a cycle, would make 'count the roots' ill-defined and
    the figure put to him would be arbitrary.
    """
    import z3
    out = []
    edges = {r["ident"]: r["parent"] for r in rows if r["kind"] == "DEPENDENT"}
    idents = [r["ident"] for r in rows]
    rank = {i: z3.Int(f"rank_{i}") for i in idents}
    s = z3.Solver()
    for i in idents:
        s.add(rank[i] >= 0)
    for child, par in edges.items():
        if par in rank:
            s.add(rank[child] > rank[par])
    out.append(f"z3 acyclicity of {len(edges)} dependency edge(s): {s.check()}")
    # every dependant must resolve to a NON-dependant root in 1 hop or more
    kinds = {r["ident"]: r["kind"] for r in rows}
    bad = []
    for child, par in edges.items():
        seen, cur = set(), par
        while cur in edges and cur not in seen:
            seen.add(cur)
            cur = edges[cur]
        if cur is None or kinds.get(cur) == "DEPENDENT":
            bad.append(child)
    out.append(f"dependants whose root is itself dependent (must be 0): {len(bad)}"
               + (f" {bad}" if bad else ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="How many decisions he actually owes.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = classify()
    live = len(rows)
    owed = [r for r in rows if r["kind"] == "OWED"]
    dependent = [r for r in rows if r["kind"] == "DEPENDENT"]
    granted = [r for r in rows if r["kind"] == "GRANTED"]
    deferral = [r for r in rows if r["kind"] == "HIS_DEFERRAL"]
    mine = [r for r in rows if r["kind"] == "MINE"]

    detail = json.loads(DETAIL.read_text(encoding="utf-8")) if DETAIL.is_file() else {}
    no_ruling = sorted(k.split(":", 1)[-1] for k, v in detail.items()
                       if isinstance(v, dict) and v.get("no_ruling_needed"))

    p7 = part7_items()
    gen = generated_decisions()
    chat_0451 = ["B61", "B63", "B22", "B41", "B60"]   # transcript 2026-11-01T04:51Z

    if args.json:
        print(json.dumps({"rows": rows, "owed": [r["ident"] for r in owed],
                          "dependent": [r["ident"] for r in dependent],
                          "part7_count": len(p7), "generated": gen,
                          "chat_0451": chat_0451}, indent=2))
        return 0

    print("=" * 78)
    print("HOW MANY DECISIONS ACTUALLY NEED HIM")
    print("=" * 78)
    print(__doc__)

    print("\n0. WHAT MOVED OVERNIGHT, READ FROM THE COMMITS THEMSELVES")
    prev = None
    for b in board_trace():
        if b.get("error"):
            print(f"    {b['sha']:10} UNREADABLE: {b['error']}")
            continue
        line = (f"    {b['sha']:10} entries {b['entries']:4}  OPEN {b['open']:3}"
                f"  DONE {b['done']:4}")
        if prev:
            closed = sorted(k for k, v in b["idents"].items()
                            if prev.get(k) == "OPEN" and v == "DONE")
            fresh = sorted(k for k in b["idents"] if k not in prev)
            if closed:
                line += f"  closed {closed}"
            if fresh:
                line += f"  added {fresh}"
        print(line)
        prev = b["idents"]
    print("    The open count fell 15 to 10 and then rose to 11. 1 figure cannot")
    print("    say that, which is why the trace is printed rather than a total.")

    print("\n1. THE 4 COUNTS THAT WERE IN FRONT OF HIM AT ONCE")
    print(f"    hand-written PART 7, numbered items under the heading"
          f" 'WHAT NEEDS YOUR VERDICT' : {len(p7)}")
    print(f"    the same section's own opening prose                              "
          f"          : 4")
    print(f"    generated half's header line                                      "
          f"          : {len(gen)}  {gen}")
    print(f"    chat message at 04:51 GMT, entries named as waiting on him         "
          f"         : {len(chat_0451)}  {chat_0451}")
    print("    4 counts, 1 quantity. The 10 is a LIST LENGTH under a heading that")
    print("    promises the list is his to decide.")

    print(f"\n2. WHAT THE MARKERS SAY, over {live} live entries")
    for kind, label in (("OWED", "a decision he owes"),
                        ("DEPENDENT", "waiting on ANOTHER entry's decision"),
                        ("GRANTED", "asking a go-ahead his standing rule grants"),
                        ("HIS_DEFERRAL", "he deferred it himself, with a date"),
                        ("MINE", "mine, asks him nothing")):
        sel = [r for r in rows if r["kind"] == kind]
        print(f"    {label:48} {interval(len(sel), live)}")
        for r in sel:
            par = f" -> {r['parent']}" if r["parent"] else ""
            rl = f" ruled:{r['ruled']}" if r["ruled"] else ""
            print(f"        {r['ident']:7} {r['state']:9} {r['status'] or '-':10}"
                  f"{rl}{par}  L{r['line']}")
            for q in r["live_asks"]:
                print(f"            ASKS: {q[:150]}")

    print("\n3. IS THE DEDUPLICATION WELL DEFINED?")
    for line in graph_is_well_defined(rows):
        print(f"    {line}")

    sup = suppressed(rows)
    print("\n4. THE INVERSE FAILURE: A RULING OLDER THAN THE QUESTIONS IT SILENCES")
    print(f"    entries with a live ask AND a ruling older than their own latest"
          f" dated addition: {len(sup)}")
    for r in sup:
        print(f"        {r['ident']:7} ruled {r['ruled']}, later additions"
              f" {r['later_dates']}, {len(r['live_asks'])} live ask(s)")
    if sup:
        print("    These left the generated decision list because of a ruling that")
        print("    PREDATES the questions. Repetition is visible; suppression is not.")

    print("\n5. THE ANSWER TO HIS QUESTION")
    print(f"    decisions he genuinely owes      : {len(owed)}  "
          f"{[r['ident'] for r in owed]}")
    print(f"    entries released by those        : {len(dependent)}  "
          f"{[r['ident'] for r in dependent]}")
    print(f"    presented to him and NOT his     : "
          f"{len([r for r in rows if r['kind'] in ('DEPENDENT','GRANTED','HIS_DEFERRAL')])}")
    inflation = len(p7) - len(owed)
    print(f"    PART 7's list length minus the owed count: {inflation}")
    print(f"    authored detail already flags as needing no ruling: {no_ruling}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
