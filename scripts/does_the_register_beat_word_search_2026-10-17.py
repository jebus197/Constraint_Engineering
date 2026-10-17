#!/usr/bin/env python3
"""Does the hashed register actually beat a word search at spotting known work?

HIS REQUIREMENT, 2026-10-17, verbatim: *"One small but useful refinement would
probably be to give each issue and each resolution its own unique hashed
value/ID and then to store these in a searchable registry within the Bugzilla
framework, and arrange it so that you must search for these hashed values before
you do, or suggest any new work. You should arrange it so that this is much more
useful to you as a way of listing, proposing, searching, applying and
remembering which fixes have and have not been done or applied that just relying
on semantic searches/vocabulary/word searches on their own. You will need to set
this up and test it and ensure that it does work better than other methods for
this purpose and so that it doesn't risk simply becoming decoration that does
nothing useful."*

So the register owes a demonstration, not an assertion. This is it.

THE DECISION UNDER TEST. Before proposing work, decide: is this already known?
That is the decision a rediscovery gets wrong, and the one the register exists to
make.

GROUND TRUTH FROM THE RECORD, NOT FROM A MODEL. The task list is under version
control, so its own history supplies labels that nobody invented:

  * STATE: the list as it stood at an earlier commit.
  * POSITIVES: entries that EXISTED at that commit. Querying with their CURRENT
    text is exactly the rediscovery case -- same item, wording moved on.
  * NEGATIVES: entries added AFTER that commit. They genuinely were not known at
    that point, so a method claiming otherwise is making a real error.

No sentence-embedding model is used anywhere, which is the honest limit the
sibling script `similarity_operating_characteristic.py` had to state about its
own labels. Here the labels are facts about the repository.

THE QUERY CARRIES NO IDENTIFIER, deliberately. A rediscovery happens when work
is described, not when it is cited: if the query carried "B14" the register would
win trivially on an exact reference lookup and the comparison would be
worthless. The leading identifier is stripped and NO task reference is passed,
so the register must earn the answer from content, its normalised digest, and
the code subjects it extracted.

BOTH METHODS GET THEIR BEST OPERATING POINT. The word search is swept across
every threshold and reported at the one that maximises its accuracy, because
beating a deliberately crippled baseline would prove nothing.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

LIST_REL = "experimental_notes/CDSFL_MASTER_TASK_LIST.md"
MARKER = re.compile(r"<!--\s*task:\s*(\S+)")

#: Words too common in this project to carry information. Without this the word
#: search matches everything on "the", "fix", "test" and scores far worse than
#: it deserves, which would flatter the register.
STOP = set("""a an the and or but if then than that this these those is are was
were be been being have has had do does did of to in on at by for with from as
it its so not no any all each per via use used using new now also only one two
three more most some such into over under about after before while when where
which who whom what why how same other another must should would could may might
can will shall do done fix fixed fixes test tested tests run runs ran work works
worked task entry list item note notes claim claims found find founder his he
him measured measure figure number count rate every both still again already
because against between during through within without above below out up down
off very much many few less least first last next
""".split())


def _words(text: str) -> set:
    return {w for w in re.findall(r"[a-z_][a-z0-9_]{2,}", text.lower())
            if w not in STOP}


def _entries_at(sha: str) -> dict:
    """{ident: block_text} for the list as it stood at `sha`."""
    txt = subprocess.run(["git", "show", f"{sha}:{LIST_REL}"],
                         cwd=REPO, capture_output=True, text=True).stdout
    if not txt:
        return {}
    out, lines = {}, txt.splitlines()
    prev = 0
    for i, line in enumerate(lines):
        m = MARKER.match(line.strip())
        if m:
            out[m.group(1)] = "\n".join(lines[prev:i])
            prev = i + 1
    return out


def _query_for(ident: str, block: str) -> str:
    """The description a rediscovery would be phrased as: no identifier."""
    body = re.sub(r"\*+", "", block.strip())
    body = re.sub(r"^(?:★\s*)?" + re.escape(ident) + r"[.)]?\s*", "", body)
    body = re.sub(r"^(?:DONE|WITHDRAWN|CLOSED|PARTIAL|BLOCKED)\b[^.]*\.\s*", "",
                  body, flags=re.IGNORECASE)
    return " ".join(body.split())[:400]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--at", default="60d0d536",
                    help="the commit whose list state is searched")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    old = _entries_at(a.at)
    new = _entries_at("HEAD")
    if not old or not new:
        print(f"FATAL: could not read the list at {a.at} or at HEAD.")
        return 2

    positives = [i for i in new if i in old]
    negatives = [i for i in new if i not in old]
    print(f"list at {a.at}: {len(old)} entries   at HEAD: {len(new)} entries")
    print(f"  POSITIVES (existed then, queried with today's wording): {len(positives)}")
    print(f"  NEGATIVES (added after, so genuinely unknown then)    : {len(negatives)}")
    if not negatives:
        print("FATAL: no negatives, so specificity cannot be measured.")
        return 2

    queries = ([( _query_for(i, new[i]), True) for i in positives]
               + [(_query_for(i, new[i]), False) for i in negatives])
    queries = [(q, lab) for q, lab in queries if len(q) > 20]

    # ---------------------------------------------------------- METHOD A
    from bench.ticket_store import TicketStore
    with tempfile.TemporaryDirectory() as td:
        store = TicketStore(pathlib.Path(td) / "seed.jsonl")
        sys.path.insert(0, str(REPO / "scripts"))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "h_cmp", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
        H = importlib.util.module_from_spec(spec)
        sys.modules["h_cmp"] = H
        spec.loader.exec_module(H)
        for ident, block in old.items():
            q = _query_for(ident, block)
            if len(q) < 10:
                continue
            store.propose("pf", q[:120], q, "task_list", task_ref=ident,
                          subjects=H.subjects_in(block), status="OPEN")
        a_tp = a_fp = a_tn = a_fn = 0
        a_said = []
        for q, known in queries:
            _, outcome = store.propose("pf", q[:120], q, "probe", status="OPEN")
            said_known = outcome != "created"
            a_said.append(said_known)
            if known and said_known: a_tp += 1
            elif known and not said_known: a_fn += 1
            elif not known and said_known: a_fp += 1
            else: a_tn += 1

    # ---------------------------------------------------------- METHOD B
    old_text = "\n".join(old.values())
    old_words = _words(old_text)
    best = None
    for thr in [i / 100 for i in range(5, 100, 5)]:
        tp = fp = tn = fn = 0
        for q, known in queries:
            qw = _words(q)
            share = (len(qw & old_words) / len(qw)) if qw else 0.0
            said_known = share >= thr
            if known and said_known: tp += 1
            elif known and not said_known: fn += 1
            elif not known and said_known: fp += 1
            else: tn += 1
        acc = (tp + tn) / max(1, tp + tn + fp + fn)
        if best is None or acc > best[0]:
            best = (acc, thr, tp, fp, tn, fn)
    # the per-query verdicts at the BEST threshold, for the combination rules
    b_said = []
    for q, known in queries:
        qw = _words(q)
        share = (len(qw & old_words) / len(qw)) if qw else 0.0
        b_said.append(share >= best[1])

    def report(name, tp, fp, tn, fn, extra=""):
        n = tp + fp + tn + fn
        acc = (tp + tn) / max(1, n)
        tpr = tp / max(1, tp + fn)
        tnr = tn / max(1, tn + fp)
        print(f"\n{name}{extra}")
        print(f"  recognised a KNOWN item      : {tp} of {tp+fn} = {100*tpr:.4f}%")
        print(f"  correctly called a NEW item new: {tn} of {tn+fp} = {100*tnr:.4f}%")
        print(f"  accuracy                     : {tp+tn} of {n} = {100*acc:.4f}%")
        try:
            from statsmodels.stats.proportion import proportion_confint
            for k, d, what in ((tp, tp+fn, "recall"), (tn, tn+fp, "specificity")):
                lo, hi = proportion_confint(k, max(1, d), method="wilson")
                print(f"    {what:<12} Wilson [{lo*100:.4f}%, {hi*100:.4f}%]")
        except ImportError as exc:
            #: NAMED AND REPORTED, not swallowed. `except Exception: pass`
            #: here meant a missing statsmodels silently dropped every
            #: confidence interval while the point estimates still printed --
            #: a proportion quoted with no interval, which this project's own
            #: rule forbids. The figure is still printed; what changes is that
            #: its missing interval is now visible.
            print(f"    INTERVALS UNAVAILABLE: {exc}. The percentages above "
                  f"are point estimates with no interval, so they must not be "
                  f"quoted as measurements until this is installed.")
        return acc, tpr, tnr

    print("=" * 74)
    print("THE COMPARISON")
    print("=" * 74)
    print(f"queries: {len(queries)}  "
          f"({sum(1 for _, k in queries if k)} known, "
          f"{sum(1 for _, k in queries if not k)} new)")
    a_acc, a_tpr, a_tnr = report("METHOD A -- the hashed register (3 tiers)",
                                 a_tp, a_fp, a_tn, a_fn)
    acc, thr, tp, fp, tn, fn = best
    b_acc, b_tpr, b_tnr = report("METHOD B -- distinctive-word overlap",
                                 tp, fp, tn, fn,
                                 f", at its BEST threshold {thr:.2f} of 19 swept")

    # ------------------------------------------------- THE COMBINATION RULES
    #
    # HIS INSTRUCTION, 2026-10-17: *"The registry search can contain both a word
    # and hashed ID search, so it can contain the best of both approaches."*
    # That is right, but NOT by a simple AND or OR, and the bounds say why
    # before any measurement is taken: a UNION says "known" whenever either
    # method does, so its specificity cannot exceed the WORSE of the two; an
    # INTERSECTION requires both, so its recall cannot exceed the worse of the
    # two. Neither can give the best of both -- that is arithmetic, not an
    # empirical question.
    #
    # THE TIERED RULE IS THE ONE HIS OWN DUPE DEFINITION IMPLIES. He requires a
    # duplicate to be the same issue AND the same proposed fix AND now the same
    # hash, which is a judgement rather than a string match. So the word layer
    # SURFACES candidates and the hash tiers DECIDE: recall is measured on
    # whether the true match is SURFACED at all, and specificity on whether a
    # genuinely new item is wrongly MERGED. Nothing the word layer finds is
    # auto-merged, so it cannot cost specificity, and it can only add recall.
    def _rates(said, label):
        tp = sum(1 for (q, k), s in zip(queries, said) if k and s)
        fn = sum(1 for (q, k), s in zip(queries, said) if k and not s)
        fp = sum(1 for (q, k), s in zip(queries, said) if not k and s)
        tn = sum(1 for (q, k), s in zip(queries, said) if not k and not s)
        return report(label, tp, fp, tn, fn)

    union = [x or y for x, y in zip(a_said, b_said)]
    inter = [x and y for x, y in zip(a_said, b_said)]
    u_acc, u_tpr, u_tnr = _rates(union, "METHOD D -- UNION (either says known)")
    i_acc, i_tpr, i_tnr = _rates(inter, "METHOD E -- INTERSECTION (both must)")

    # METHOD C: surfaced by either, DECIDED by the register alone.
    c_surfaced_tp = sum(1 for (q, k), u in zip(queries, union) if k and u)
    c_surfaced_fn = sum(1 for (q, k), u in zip(queries, union) if k and not u)
    n_pos = c_surfaced_tp + c_surfaced_fn
    print("\nMETHOD C -- TIERED: the word layer SURFACES, the register DECIDES")
    print(f"  a known item is SURFACED      : {c_surfaced_tp} of {n_pos} = "
          f"{100*c_surfaced_tp/max(1,n_pos):.4f}%")
    from statsmodels.stats.proportion import proportion_confint as _pc
    lo, hi = _pc(c_surfaced_tp, max(1, n_pos), method="wilson")
    print(f"    surfacing recall Wilson [{lo*100:.4f}%, {hi*100:.4f}%]")
    print(f"  a new item is wrongly MERGED  : {a_fp} of {a_fp + a_tn} = "
          f"{100*a_fp/max(1, a_fp + a_tn):.4f}%   (the register decides, so this"
          f" is unchanged from METHOD A)")
    print(f"  so specificity               : {100*a_tnr:.4f}%  == METHOD A")

    print("\n" + "=" * 74)
    print("VERDICT")
    print("=" * 74)
    wins = []
    if a_tnr > b_tnr: wins.append(f"specificity ({100*a_tnr:.4f}% vs {100*b_tnr:.4f}%)")
    if a_tpr > b_tpr: wins.append(f"recall ({100*a_tpr:.4f}% vs {100*b_tpr:.4f}%)")
    if a_acc > b_acc: wins.append(f"accuracy ({100*a_acc:.4f}% vs {100*b_acc:.4f}%)")
    if wins:
        print(f"the register is better on: {', '.join(wins)}")
    losses = []
    if b_tnr > a_tnr: losses.append("specificity")
    if b_tpr > a_tpr: losses.append("recall")
    if b_acc > a_acc: losses.append("accuracy")
    if losses:
        print(f"the WORD SEARCH is better on: {', '.join(losses)}")
    if not wins:
        print("THE REGISTER DOES NOT BEAT THE WORD SEARCH on any measure here.")
        print("His condition -- that it must not become decoration -- is NOT met,")
        print("and saying so is the point of running this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
