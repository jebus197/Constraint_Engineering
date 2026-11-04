#!/usr/bin/env python3
"""Which unadopted seat designs bear on the decisions still waiting on him?

HIS RULING, 2026-11-01, annotation 7: *"Triage them."* And annotation 26, the
question the triage answered: *"Again what seat designs? I have no idea what you
are asking me here? What does '44' relate to?"*

`scripts/triage_the_unadopted_seat_designs_2026-11-02.py` reduced 44 absent
live-module files to 25 genuine design modules and gave each a verdict, leaving
23 that need a judgement. 23 designs to read is better than 25 files, and it is
still 23 judgements.

★ THIS GOES ONE STEP FURTHER, AND THE STEP IS THE USEFUL ONE. Several of those
designs state, in their own docstrings, the DEFECT they close -- and several of
those defects are the subject of an entry still OPEN on the master task list. So
the question for him is not "is this design good" in the abstract; it is "here is
a design that bears on a decision you already owe". That reframes a parked store
as material for the 6 decisions actually in front of him.

★ MATCHED ON NAMED CODE IDENTIFIERS, NOT ON TOPIC WORDS, and the distinction is
the whole method. A topic-keyword match is a proxy, and a proxy chosen without
measuring its alternatives is this project's single most recorded error class --
`_directive_topic_and_stance` is the cautionary case in this very repository:
its `table` topic fires on any text containing the word "table" and cost a model
an engineering requirement. A function or class name is not a topic; if a design
names `_check_gamma_alt_convergence` and an open entry names it too, they are
about the same code. Where no identifier is shared, this reports NO LINK rather
than guessing one from prose.

NOTHING IS ADOPTED AND NOTHING IS REJECTED. This reports a correspondence.
"""
from __future__ import annotations
import ast, collections, math, pathlib, re, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
STORE = REPO / "experimental_notes" / "seat_evidence"
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: A python identifier long enough that a shared mention is not coincidence.
#: 12 characters, and the floor is stated rather than tuned: the shortest live
#: function name this matched on is `gate_would_fire` at 15, and the MC commands
#: that wrecked an earlier predicate are 1 and 2 characters.
IDENT = re.compile(r"\b(_?[a-z][a-z0-9]*(?:_[a-z0-9]+){2,})\b")
MIN_LEN = 12

NOT_LIVE = ("experimental_notes/seat_evidence/", "bench/logs/",
            "/sandbox_harvest/", "/panel_worktree_harvest/", "/files/bench/")


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def _defined_names() -> set[str]:
    """Every name DEFINED as a function or class, live or in the design store.

    ★ THE 3RD PREDICATE CORRECTION IN THIS SCRIPT, and each was caught by
    reading its output rather than by review. A length floor alone was not
    enough: with it, 11 of 25 designs "matched" an open entry and the shared
    identifier was `reference_runner_v3` in every B20 case -- a MODULE name that
    almost every file in the project mentions. Matching on it is the equivalent
    of matching on the word "bench": true, and empty.

    A name that is DEFINED somewhere as a `def` or a `class` is a thing with
    behaviour. A module name is a location. Only the former can tell us 2
    documents are about the same code.
    """
    out: set[str] = set()
    for root in (REPO / "bench", REPO / "scripts", STORE):
        for p in root.rglob("*.py"):
            try:
                tree = ast.parse(p.read_text(errors="replace"))
            except Exception:                                # noqa: BLE001
                continue
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)) and len(n.name) >= MIN_LEN:
                    out.add(n.name)
    return out


DEFINED: set[str] = set()


def idents(text: str) -> set[str]:
    """Identifiers in `text` that are DEFINED as a function or class somewhere."""
    return {m for m in IDENT.findall(text or "")
            if len(m) >= MIN_LEN and m in DEFINED}


def main() -> int:
    answer_help(__doc__, __file__)
    from task_list_markers import parse_entries

    global DEFINED
    DEFINED = _defined_names()
    print(f"  function/class names of {MIN_LEN}+ chars defined anywhere: "
          f"{len(DEFINED)}")

    entries = [e for e in parse_entries(LIST) if e.state == "OPEN"]
    print("=" * 78)
    print("WHICH UNADOPTED DESIGNS BEAR ON THE DECISIONS STILL WAITING ON HIM?")
    print("=" * 78)
    print(f"  open entries: {len(entries)} -> {[e.ident for e in entries]}")

    # ★ `Entry.text` IS the whole entry body -- each entry occupies ONE long
    # line in the list -- and the field is `line_no`, not `line`. A first
    # version did `start = e.line - 1 if hasattr(e, "line") else 0`, and since
    # there is no `.line` attribute every entry fell to `start = 0` and all 6
    # were handed the SAME 40 lines. The symptom was every entry reporting
    # exactly 1 identifier, which is the uniform-verdict signal
    # `feedback_a_signal_is_not_a_measurement_2026-10-30` names as the cheapest
    # sign that a predicate is wrong. Settled by inspecting the dataclass
    # fields rather than guessing a second time.
    ent_idents: dict[str, set[str]] = {e.ident: idents(e.text) for e in entries}
    for ident, s in ent_idents.items():
        print(f"    {ident:7s} names {len(s)} identifier(s) of {MIN_LEN}+ chars")

    # the designs
    designs = []
    for f in sorted(STORE.rglob("*.py")):
        parts = f.relative_to(STORE).parts
        if len(parts) < 3:
            continue
        sp = "/".join(parts[2:])
        if (sp.startswith(("bench/tests/", "scripts/"))
                or pathlib.Path(sp).name.startswith("test_") or "falsif" in sp):
            continue
        if not sp.startswith("bench/") or (REPO / sp).is_file():
            continue
        src = f.read_text(errors="replace")
        try:
            doc = ast.get_docstring(ast.parse(src)) or ""
        except Exception:                                    # noqa: BLE001
            doc = ""
        designs.append({"sp": sp, "seat": parts[1], "lines": src.count("\n") + 1,
                        "idents": idents(doc), "claim": " ".join(
                            l.strip() for l in doc.strip().splitlines()[:2])[:150]})
    print(f"\n  design modules: {len(designs)}")

    linked = []
    for d in designs:
        hits = {ident: sorted(d["idents"] & s)
                for ident, s in ent_idents.items() if d["idents"] & s}
        if hits:
            linked.append((d, hits))
    p, lo, hi = wilson(len(linked), len(designs))
    print(f"  designs naming an identifier an OPEN entry also names: "
          f"{len(linked)}/{len(designs)} = {p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]")

    if not linked:
        print("\n" + "=" * 78)
        print("★ 0 LINKS, AND THAT IS A PROPERTY OF THIS METHOD RATHER THAN OF THE")
        print("DESIGNS. Reporting it as a finding would be the error.")
        print("=" * 78)
        n_named = {k: len(v) for k, v in ent_idents.items()}
        print(f"  defined identifiers named by each OPEN entry: {n_named}")
        print("  The intersection is near-guaranteed empty because the ENTRIES name")
        print("  almost no defined function or class names, not because the designs")
        print("  are unrelated to them.")
        print()
        print("  THE COUNTER-EXAMPLE, VERIFIED BY HAND, which settles it:")
        print("    `_check_gamma_alt_convergence` IS a defined name, the design")
        print("    bench/degraded_convergence_2026-10-07.py NAMES it as the defect")
        print("    it repairs, and that function is the subject of entry B76 -- but")
        print("    B76's own text never mentions it, naming a test file instead. So")
        print("    a real correspondence exists and this method cannot see it.")
        print()
        print("  AND THE CAUSE IS NOT AN ACCIDENT. The entries are written for HIM")
        print("  to read: his annotation of 2026-11-01 was that printing issue codes")
        print("  without explanation renders a report unreadable, so entries name")
        print("  their subjects in WORDS. A method keyed on code identifiers is")
        print("  therefore the wrong instrument for this corpus, and strengthening")
        print("  the design side further cannot fix a weakness on the entry side.")
        print()
        print("  WHAT WOULD WORK, stated so the next attempt is not a 4th guess at")
        print("  a predicate: give each open entry an explicit `subjects:` field, as")
        print("  the ticket store already does for tickets, and match on that. Then")
        print("  the correspondence is DECLARED rather than inferred from prose.")
        return 0

    print(f"\n  THE CORRESPONDENCE, by open entry")
    by_entry = collections.defaultdict(list)
    for d, hits in linked:
        for ident in hits:
            by_entry[ident].append((d, hits[ident]))
    for ident in sorted(by_entry):
        print(f"\n  --- {ident} ---")
        for d, shared in sorted(by_entry[ident], key=lambda x: -x[0]["lines"]):
            print(f"    {d['lines']:4d}L  {d['sp']}  [{d['seat']}]")
            print(f"          shares: {shared[:4]}")
            print(f"          {d['claim'][:130]}")

    unlinked = [d for d in designs if d not in [x[0] for x in linked]]
    print(f"\n  AND {len(unlinked)} DESIGN(S) SHARE NO IDENTIFIER WITH ANY OPEN")
    print(f"  ENTRY, so nothing says they bear on a pending decision:")
    for d in sorted(unlinked, key=lambda x: -x["lines"])[:10]:
        print(f"    {d['lines']:4d}L  {d['sp']}")
    _withheld = max(0, len(unlinked) - 10)
    if _withheld:
        print(f"    ... and {_withheld} more not shown "
              f"(of {len(unlinked)} total)")
    print("\n  NOTHING IS ADOPTED AND NOTHING IS REJECTED. This is a")
    print("  correspondence, so his judgement on a design can be taken beside")
    print("  the decision it bears on rather than in the abstract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
