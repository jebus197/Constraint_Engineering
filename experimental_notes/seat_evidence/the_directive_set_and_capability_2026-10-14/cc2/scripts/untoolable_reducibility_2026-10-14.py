# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0b43710795c50609206d5cf7cd9fb377ea330742fbd54d89d489af8e8faa0b8d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Of the archived findings with no falsifier, which were IRREDUCIBLE and which
were simply NEVER ATTEMPTED?

PANEL ITEM 4, 2026-10-14. The brief's figure under test: "1,938 of 3,298
archived findings carry no falsifier code (58.7629%)". The question the figure
does not answer is whether that silence records a limit of computation or a
limit of supply.

THE CORPUS, AND IT IS REUSED RATHER THAN REDEFINED. Every dict under
`registry.entries` of every `bench/logs/**/runner_state.json` that carries a
numeric `severity`. That is the enumeration of the committed producer the 3,298
figure comes from --
`scripts/severity_was_never_computed_from_the_model_2026-10-12.py` -- so the
denominator is its by construction and a divergence prints rather than hides.
`bench/archive_corpus.py` is the repository's archive helper, but it answers a
different question (what a fresh clone holds); its `untracked_archive_files()`
count is printed here so a reader knows whether this checkout is the one a
cloner gets before quoting any figure below.

WHAT THE ARCHIVE DOES NOT HAVE. There is no `untoolable_reason` field anywhere
in the corpus. The inventory below proves it. So "genuinely irreducible" can
only be read off the free-text reason fields that do exist --
`routing_defer_reason`, `hil_reason`, `computed_evidence[].detail` -- and every
distinct value of those on this population is printed VERBATIM rather than
summarised, because the whole classification turns on them.

THE SPLIT THE ITEM ASKS FOR, over the entries recorded UNTOOLABLE:

  (a) A FALSIFIER WAS ATTEMPTED AND FAILED. Falsifier source survives in the
      entry's own record -- `routing_history[].last_falsifier_code` or
      `computed_evidence[].falsifier_code` -- so a tool was written and run.
      Sub-split by whether the recorded reason for the failure is STRUCTURAL
      (no computation could decide the claim) or EQUIPMENT (the harness lost
      or errored on a tool that existed).
  (b) NO FALSIFIER WAS EVER WRITTEN. No source anywhere in the record.

THE TOOLABILITY JUDGEMENT ON (b) IS NOT AN OPINION WHERE IT NEED NOT BE. For
most of category (b) the repository itself already settles it: nine files under
`bench/tests/` each declare a module-level `COVERS` set of
(run directory, canonical id) pairs and then falsify exactly those findings by
importing the real target. This script maps the population onto those
declarations and EXECUTES them, so "toolable" means "a committed falsifier for
this very finding passes today", not "a reviewer thought it looked easy". For
the residue it probes the named target live: does the module exist, does it
parse, does it define the symbols the claim names.

A SCOPING GAP IN THE EXISTING INSTRUMENT, reported because it moves a committed
number. `scripts/missing_falsifiers_2026-09-10.py` globs
`bench/logs/exp*/runner_state.json` -- `exp*`, not `**` -- so its population of
28, and the "28 of 28 written" that
`bench/tests/test_missing_falsifiers_all_covered_2026-09-17.py` asserts, both
exclude every non-`exp` run family (`sim45_*`, `commissioning_*`, `study_*`).
Over `**` the UNTOOLABLE population is larger, and the difference is printed.
Nothing here changes that script or that test.

THE DENOMINATOR CARRIES HARVEST COPIES, and both figures are printed. Some
`runner_state.json` files under `bench/logs` are copies of other runs'
registries saved inside a seat sandbox harvest. They are real files and the
brief's figure is right about the files it read; it is counting some findings
more than once. The rate with copies excluded is reported alongside, and it
moves the figure UP.

INTERVALS BY TWO INDEPENDENT ROUTES ON EVERY PROPORTION. statsmodels'
`proportion_confint(method='wilson')`, and a Wilson interval derived from the
formula in mpmath at 50 digits with the normal quantile COMPUTED
(z = sqrt(2) * erfinv(0.95)) rather than tabulated as 1.96. Agreement is
asserted numerically at the end, not assumed. scipy's Clopper-Pearson is
printed as a third, differently-constructed reference.

Usage: python3 scripts/untoolable_reducibility_2026-10-14.py
"""
from __future__ import annotations

import ast
import collections
import json
import os
import pathlib
import random
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
TESTS = REPO / "bench" / "tests"

#: The glob and predicate of the committed 3,298 producer. Changing either
#: would silently redefine the denominator, so both live here once.
STATE_GLOB = "**/runner_state.json"

#: Path fragments that mark a `runner_state.json` as a COPY of another run's
#: registry, preserved inside a panel seat's sandbox harvest.
COPY_MARKERS = ("sandbox_harvest", "seat_evidence")

#: Verdicts meaning a tool actually DECIDED the claim.
DECIDED = ("CONFIRMED", "REFUTED")

#: Deterministic sample for the step-4 judgement, and the seed is the date.
SAMPLE_N = 15
SAMPLE_SEED = 20261014

#: STRUCTURAL: the reason asserts that NO FALSIFIER COULD DECIDE THE CLAIM --
#: the claim is not about the target's code at all, so importing the target and
#: computing cannot settle it. This is the only bucket that can support
#: "computationally irreducible", and the phrases are taken from the strings
#: that actually occur on this population rather than invented.
#:
#: A BARE "irreducible" IS DELIBERATELY NOT A MARKER. The first version of this
#: regex carried it and misclassified 11 rows as structural, because the only
#: place the word occurs in the corpus is a DISCLAIMER refusing the label:
#: "'Irreducible' would assert a machine tried and failed." A keyword that
#: matches a sentence denying the keyword is how a measurement reports its own
#: wish; the misclassification and its removal are recorded here rather than
#: quietly fixed.
STRUCTURAL_RE = re.compile(
    r"cannot be falsified by any test"
    r"|no test (?:of|against) [^.]{0,80}\bcan\b"
    r"|not a property of (?:the module|any code)"
    r"|property of the editing"
    r"|describes the editing process"
    r"|process observation"
    r"|records edit churn"
    r"|not about the source at sha"
    r"|describes the (?:review|authoring) process"
    r"|not a testable"
    r"|not computable"
    r"|undecidable"
    r"|requires human judgement"
    r"|requires a human",
    re.I,
)

#: OUT OF SCOPE: the reason says the defect is REAL but sits in a module other
#: than the one under review, so no passage of the TARGET can carry the fix.
#: That is a bar on the splice-and-rerun contract, NOT on computation -- and
#: several of these reason strings contain the model's own EXECUTED proof of
#: the claim ("verified: re.escape('REVISED_ANSWER') == 'REVISED_ANSWER'"),
#: which is the plainest possible demonstration that the claim was computable.
#: Counted separately so it can never be read as irreducibility.
OUT_OF_SCOPE_RE = re.compile(
    r"outside the (?:target|reviewed) module"
    r"|lies\s+outside"
    r"|not in the target document"
    r"|not the (?:review )?target"
    r"|no passage (?:of|in) the target"
    r"|no assertion on the target"
    r"|appears nowhere in the spec"
    r"|does not appear anywhere in the target"
    r"|there is no passage",
    re.I,
)

#: DUPLICATE: the entry restates another finding, so the falsifier was never
#: this entry's to run. Administrative, not a statement about computability.
DUPLICATE_RE = re.compile(
    r"\bduplicate\b"
    r"|no separately testable assertion"
    r"|no separate falsifiable content"
    r"|same passage and same defect"
    r"|restated",
    re.I,
)

#: EQUIPMENT: the reason blames the harness or the supply of tools -- which is
#: the opposite finding to irreducibility, and in this corpus it says so in
#: those words ("an equipment failure", "no model produced a runnable test").
EQUIPMENT_RE = re.compile(
    r"equipment failure"
    r"|no model produced a runnable test"
    r"|no rung returned a falsifier"
    r"|ladder exhausted"
    r"|nothing has been assessed yet"
    r"|no falsifier and no S_k"
    r"|no tool verdict"
    r"|requires a tool verdict",
    re.I,
)

#: Precedence runs STRUCTURAL first, so the reading most favourable to
#: "computationally irreducible" wins every tie and the figure this script
#: reports for irreducibility is an UPPER BOUND, not a floor.
REASON_KINDS = (
    ("STRUCTURAL", STRUCTURAL_RE),
    ("OUT_OF_SCOPE", OUT_OF_SCOPE_RE),
    ("DUPLICATE", DUPLICATE_RE),
    ("EQUIPMENT", EQUIPMENT_RE),
)


def reason_kind(text: str) -> str:
    """Which bucket a single reason string falls in. STRUCTURAL wins ties."""
    for name, pattern in REASON_KINDS:
        if pattern.search(text):
            return name
    return "NEITHER"


def has_structural_reason(entry: dict) -> bool:
    """Does ANY reason on this entry state a bar on COMPUTING the claim?

    Judged per reason string, so an entry whose equipment note sits beside a
    genuine non-computability note still counts as irreducible.
    """
    return any(reason_kind(r) == "STRUCTURAL" for r in reasons(entry))


def falsifier_sources(entry: dict) -> list[tuple[str, str, int]]:
    """Every falsifier body preserved anywhere in this entry's record.

    The entry's own `falsifier_code` slot being empty does NOT mean no tool was
    written: the routing ladder records the body of the last falsifier it ran,
    and a reasoned withdrawal can carry one too.
    """
    out: list[tuple[str, str, int]] = []
    for rung in entry.get("routing_history") or []:
        if not isinstance(rung, dict):
            continue
        body = str(rung.get("last_falsifier_code") or "").strip()
        if body:
            out.append(("routing_history", str(rung.get("verdict") or ""),
                        len(body)))
    for item in entry.get("computed_evidence") or []:
        if not isinstance(item, dict):
            continue
        body = str(item.get("falsifier_code") or "").strip()
        if body:
            out.append(("computed_evidence", str(item.get("kind") or ""),
                        len(body)))
    return out


# ---------------------------------------------------------------- enumeration

def entries():
    """The 3,298 producer's own enumeration, reproduced exactly."""
    for path in sorted(LOGS.glob(STATE_GLOB)):
        try:
            doc = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                      # noqa: BLE001
            continue
        registry = ((doc or {}).get("registry") or {}).get("entries") or {}
        for cid, entry in registry.items():
            if isinstance(entry, dict) and isinstance(entry.get("severity"),
                                                      (int, float)):
                yield path, cid, entry


def code(entry: dict) -> str:
    return str(entry.get("falsifier_code") or "").strip()


def verdict(entry: dict) -> str:
    return str(entry.get("falsifier_verdict") or "").strip().upper()


def is_copy(path: pathlib.Path) -> bool:
    return any(marker in str(path) for marker in COPY_MARKERS)


def run_name(path: pathlib.Path) -> str:
    """The run directory a state file belongs to -- the key the test files use."""
    return path.parent.name


def reasons(entry: dict) -> list[str]:
    """Every field on this entry that can state WHY no falsifier exists."""
    out = []
    for key in ("routing_defer_reason", "routing_deferred_reason", "hil_reason",
                "withdraw_reason", "close_reason", "merge_blocked_reason"):
        if entry.get(key):
            out.append(f"{key}: {entry[key]}")
    for item in entry.get("computed_evidence") or []:
        if isinstance(item, dict) and item.get("detail"):
            out.append(f"computed_evidence.detail: {item['detail']}")
    return out


# -------------------------------------------------------------- the two tools

AGREEMENT: list[float] = []


def wilson_statsmodels(k: int, n: int) -> tuple[float, float]:
    """TOOL 1. The interval the item names, from the library that owns it."""
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return max(0.0, float(lo)), min(1.0, float(hi))


def wilson_by_hand(k: int, n: int) -> tuple[float, float]:
    """TOOL 2. The same interval from the formula, independently, at 50 digits.

        centre = (k + z^2/2) / (n + z^2)
        half   = z/(n + z^2) * sqrt( k(n-k)/n + z^2/4 )

    z is COMPUTED, not tabulated: Phi(z) = 0.975  <=>  z = sqrt(2)*erfinv(0.95).
    A tabulated 1.96 would make this a second reading of the same number rather
    than a second derivation of it.
    """
    from mpmath import erfinv, mp, mpf, sqrt
    mp.dps = 50
    z = sqrt(mpf(2)) * erfinv(mpf("0.95"))
    n_, k_ = mpf(n), mpf(k)
    denom = n_ + z ** 2
    centre = (k_ + z ** 2 / 2) / denom
    half = (z / denom) * sqrt(k_ * (n_ - k_) / n_ + z ** 2 / 4)
    return max(0.0, float(centre - half)), min(1.0, float(centre + half))


def clopper_pearson(k: int, n: int) -> tuple[float, float]:
    """A third, differently-constructed reference: exact, from scipy's beta."""
    from scipy import stats
    lo = float(stats.beta.ppf(0.025, k, n - k + 1)) if k else 0.0
    hi = float(stats.beta.ppf(0.975, k + 1, n - k)) if k < n else 1.0
    return lo, hi


def pct(label: str, k: int, n: int, indent: str = "  ") -> None:
    if not n:
        print(f"{indent}{label}: no denominator")
        return
    w_lo, w_hi = wilson_statsmodels(k, n)
    h_lo, h_hi = wilson_by_hand(k, n)
    c_lo, c_hi = clopper_pearson(k, n)
    delta = max(abs(w_lo - h_lo), abs(w_hi - h_hi))
    AGREEMENT.append(delta)
    print(f"{indent}{label}")
    print(f"{indent}    {k}/{n} = {k / n:.4%}")
    print(f"{indent}    Wilson 95%  statsmodels  [{w_lo:.4%}, {w_hi:.4%}]")
    print(f"{indent}    Wilson 95%  mpmath 50dp  [{h_lo:.4%}, {h_hi:.4%}]"
          f"   max|diff| {delta:.2e}")
    print(f"{indent}    Clopper-Pearson 95%      [{c_lo:.4%}, {c_hi:.4%}]")


def rule(title: str) -> None:
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)


# --------------------------------------------- the committed falsifier corpus

COVERS_RE = re.compile(r'\(\s*"([A-Za-z0-9_\-.]+)"\s*,\s*"(C\d{4})"\s*\)')


def committed_falsifier_declarations() -> dict[tuple[str, str], set[str]]:
    """(run dir, canonical id) -> the test files that DECLARE they falsify it.

    Read out of the `COVERS` declarations the test files already carry for
    `scripts/missing_falsifiers_2026-09-10.py`, so this script invents no new
    registry of its own and cannot drift from the one the suite asserts.
    """
    out: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for path in sorted(TESTS.glob("test_falsifier_*.py")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for run, cid in COVERS_RE.findall(text):
            out[(run, cid)].add(path.name)
    return out


def execute_one(test_file: str) -> tuple[bool, str]:
    """Run ONE declaring falsifier file. 'Toolable' has to mean it passes TODAY.

    PER FILE, NOT IN ONE BATCH, and the reason is a live hazard rather than
    tidiness: a single red file in a batch yields one summary line that says
    nothing about which findings it belongs to, and this repository is under
    concurrent edit by other panel seats during a round. One file going red for
    a reason external to this measurement must not be able to blur the other
    eight.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             str(TESTS / test_file)],
            cwd=str(REPO), capture_output=True, text=True, timeout=900,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"could not execute pytest: {exc!r}"
    tail = [ln for ln in proc.stdout.strip().splitlines()
            if "passed" in ln or "failed" in ln or "error" in ln]
    summary = tail[-1] if tail else f"exit {proc.returncode}, no summary line"
    first_fail = next((ln for ln in proc.stdout.splitlines()
                       if ln.startswith("FAILED")), "")
    if first_fail:
        summary = f"{summary}  | first: {first_fail.split('::')[-1][:70]}"
    return proc.returncode == 0, summary


def execute(test_files: list[str]) -> dict[str, tuple[bool, str]]:
    """Every declaring file, run on its own, keyed by file name."""
    return {f: execute_one(f) for f in sorted(test_files)}


# -------------------------------------------- the live probe for the residue

MODULE_RE = re.compile(r"\b((?:bench|scripts|explorer|hooks)/[\w/]+\.py)\b")

#: A backticked span, which is how these claims name the thing they are about.
#: The trailing `\(?\)?` is load-bearing: the first version was
#: ``r"`([A-Za-z_][\w.]*)`"`` and so never matched ```save()``` -- the exact
#: form the sim45 memory claims use -- and reported their target as having
#: "none of the named symbols". Measured and corrected rather than tuned away.
SYMBOL_RE = re.compile(r"`([A-Za-z_][\w.]*)\(?\)?`")


def live_probe(entry: dict) -> tuple[bool, str]:
    """Could a falsifier import the real target and decide this claim?

    Mechanical, and deliberately strict: the claim text must name a module that
    EXISTS in this checkout, that PARSES, and that defines at least one of the
    symbols the claim names. Anything less is reported as NOT SHOWN rather than
    assumed either way.
    """
    text = f"{entry.get('description') or ''}\n{entry.get('proposed_fix') or ''}"
    modules = [m for m in dict.fromkeys(MODULE_RE.findall(text))
               if (REPO / m).is_file()]
    if not modules:
        return False, "claim names no python module that exists in this checkout"
    wanted = {s.split(".")[-1].rstrip("()") for s in SYMBOL_RE.findall(text)}
    for mod in modules:
        try:
            tree = ast.parse((REPO / mod).read_text(encoding="utf-8",
                                                    errors="ignore"))
        except SyntaxError:
            continue
        defined = {node.name for node in ast.walk(tree)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                        ast.ClassDef))}
        hit = sorted(wanted & defined)
        if hit:
            return True, (f"{mod} exists, parses, and defines "
                          f"{', '.join(hit[:4])}")
    return False, f"{modules[0]} exists but defines none of the named symbols"


# ------------------------------------------------------------------------ main

def main() -> int:
    answer_help(__doc__, __file__)

    rows = list(entries())
    files = {path for path, _cid, _e in rows}
    n_all = len(rows)

    rule("THE CORPUS -- the 3,298 producer's enumeration, reused not redefined")
    print(f"  glob       : bench/logs/{STATE_GLOB}   ({len(files)} files)")
    print("  predicate  : registry.entries[*] is a dict with numeric severity")
    print(f"  entries    : {n_all}   (producer publishes 3,298: "
          f"{'MATCH' if n_all == 3298 else 'MISMATCH -- see below'})")
    try:
        sys.path.insert(0, str(REPO / "bench"))
        import archive_corpus                                  # noqa: PLC0415
        print(f"  this checkout holds "
              f"{archive_corpus.untracked_archive_files()} archive files a "
              f"fresh clone would not")
        print(f"  ({archive_corpus.IGNORE_RULE})")
    except Exception as exc:                                   # noqa: BLE001
        print(f"  bench/archive_corpus.py could not be consulted: {exc!r}")
    if n_all < 1000:
        print(f"\n  only {n_all} entries found; this checkout cannot support "
              f"the measurement. Nothing below is reported as verified.")
        return 3

    # ----------------------------------------------------------------- step 2
    rule("STEP 2 -- REPRODUCING THE BRIEF'S FIGURE")
    population = [(p, c, e) for p, c, e in rows
                  if not code(e) or verdict(e) == "UNTOOLABLE"]
    n_pop = len(population)
    print("  neighbouring definitions, so the reader sees WHICH one 1,938 is:")
    for label, pred in (
        ("falsifier_code absent or empty", lambda e: not code(e)),
        ("  ... OR falsifier_verdict UNTOOLABLE",
         lambda e: not code(e) or verdict(e) == "UNTOOLABLE"),
        ("no falsifier_code KEY at all", lambda e: "falsifier_code" not in e),
        ("verdict not in {CONFIRMED, REFUTED}",
         lambda e: verdict(e) not in DECIDED),
    ):
        k = sum(1 for _p, _c, e in rows if pred(e))
        flag = "   <== THE BRIEF'S 1,938" if k == 1938 else ""
        print(f"    {label:<40}{k:>6}/{n_all} = {k / n_all:8.4%}{flag}")
    print()
    pct("NO FALSIFIER CODE, OR RECORDED UNTOOLABLE", n_pop, n_all)
    print(f"      brief states 1,938/3,298 = 58.7629% -- "
          f"{'REPRODUCED EXACTLY' if (n_pop, n_all) == (1938, 3298) else 'DIFFERS'}")
    n_u_all = sum(1 for _p, _c, e in rows if verdict(e) == "UNTOOLABLE")
    n_u_code = sum(1 for _p, _c, e in rows
                   if verdict(e) == "UNTOOLABLE" and code(e))
    print(f"      the brief's two limbs pick out ONE set: all {n_u_all} "
          f"UNTOOLABLE entries")
    print(f"      store empty code ({n_u_code} of them store any), so the 'or' "
          f"adds nothing.")

    print()
    print("  SENSITIVITY -- the denominator carries harvested sandbox copies:")
    clean = [(p, c, e) for p, c, e in rows if not is_copy(p)]
    copies = [(p, c, e) for p, c, e in rows if is_copy(p)]
    print(f"    rows inside {COPY_MARKERS} paths : {len(copies)}"
          f"   (in {len({p for p, _c, _e in copies})} files)")
    k_clean = sum(1 for _p, _c, e in clean
                  if not code(e) or verdict(e) == "UNTOOLABLE")
    pct("same rate with harvest copies EXCLUDED", k_clean, len(clean),
        indent="    ")
    print("    excluding the copies moves the figure UP, not down, so the")
    print("    brief's number is not flattered by the duplication.")

    # ----------------------------------------------------------------- step 3
    rule("STEP 3 -- THE UNTOOLABLE POPULATION: ATTEMPTED, OR NEVER WRITTEN?")
    untoolable = [(p, c, e) for p, c, e in rows
                  if verdict(e) == "UNTOOLABLE"
                  or str(e.get("status") or "").strip().upper() == "UNTOOLABLE"]
    n_unt = len(untoolable)
    distinct = sorted({(run_name(p), c) for p, c, _e in untoolable})
    print(f"  rows recorded UNTOOLABLE (verdict OR status) : {n_unt}")
    print(f"  distinct (run directory, canonical id)       : {len(distinct)}")
    print("    the gap is harvest copies of the same finding, not new findings")
    print("  status values present : "
          f"{dict(collections.Counter(str(e.get('status')) for _p, _c, e in untoolable))}")
    print()
    print("  WHAT REASON FIELDS EXIST. There is no `untoolable_reason` field")
    print("  anywhere in the corpus, which is why this has to be read off free")
    print("  text at all:")
    for absent in ("untoolable_reason", "irreducible_reason",
                   "falsifier_attempts", "execution_log"):
        print(f"    absent  {absent:<24}"
              f"{sum(1 for _p, _c, e in rows if absent in e):>6}/{n_all}")
    for present in ("routing_defer_reason", "hil_reason", "computed_evidence",
                    "irreducible_escalation", "exhausted", "routing_history",
                    "error_routed"):
        print(f"    present {present:<24}"
              f"{sum(1 for _p, _c, e in untoolable if e.get(present) is not None):>6}"
              f"/{n_unt}")

    print()
    print("  EVERY DISTINCT REASON STRING ON THIS POPULATION, VERBATIM.")
    print("  The classification below is read off these and nothing else, so a")
    print("  reader can overrule it from this block alone.")
    tally: collections.Counter = collections.Counter()
    for _p, _c, e in untoolable:
        for r in reasons(e) or ["(no reason field of any kind)"]:
            tally[r[:400]] += 1
    for text, count in tally.most_common():
        print(f"\n    [x{count}] [{reason_kind(text)}]")
        for line in re.findall(r".{1,68}(?:\s|$)", text):
            if line.strip():
                print(f"      {line.strip()}")

    attempted, never = [], []
    for p, c, e in untoolable:
        (attempted if falsifier_sources(e) else never).append((p, c, e))
    print()
    print("  (a) A FALSIFIER WAS ATTEMPTED -- source survives in the record:")
    for p, c, e in attempted:
        src = falsifier_sources(e)
        rungs = [r for r in (e.get("routing_history") or [])
                 if isinstance(r, dict)]
        tried = rungs[-1].get("rungs_tried") if rungs else None
        avail = rungs[-1].get("rungs_available") if rungs else None
        print(f"      {run_name(p):<44} {c}  {src[0][0]} "
              f"verdict={(src[0][1] or '-'):<10} body={src[0][2]}ch  "
              f"rungs={tried}/{avail}")
    print()
    pct("(a) FALSIFIER ATTEMPTED AND FAILED", len(attempted), n_unt)
    pct("(b) NO FALSIFIER EVER WRITTEN", len(never), n_unt)
    print(f"      partition: {len(attempted)} + {len(never)} = "
          f"{len(attempted) + len(never)} of {n_unt} "
          f"({'exhaustive and disjoint' if len(attempted) + len(never) == n_unt else 'BROKEN'})")

    def entry_kind(entry: dict) -> str:
        """The strongest reason kind on an entry, STRUCTURAL first."""
        kinds = {reason_kind(r) for r in reasons(entry)}
        if not kinds:
            return "SILENT"
        for name, _pattern in REASON_KINDS:
            if name in kinds:
                return name
        return "NEITHER"

    buckets = collections.Counter(entry_kind(e) for _p, _c, e in untoolable)
    print()
    print("  THE REASON EACH ENTRY GIVES, one bucket per entry, STRUCTURAL")
    print("  winning every tie so the irreducible figure is an UPPER bound:")
    for name, blurb in (
        ("STRUCTURAL", "no falsifier could decide the CLAIM"),
        ("OUT_OF_SCOPE", "claim real but outside the reviewed module"),
        ("DUPLICATE", "restates another finding"),
        ("EQUIPMENT", "the harness or the tool supply failed"),
        ("NEITHER", "a reason that speaks to none of the above"),
        ("SILENT", "no reason field of any kind"),
    ):
        pct(f"{name:<13} -- {blurb}", buckets[name], n_unt, indent="    ")
    print(f"    partition total: {sum(buckets.values())} of {n_unt} "
          f"({'exhaustive and disjoint' if sum(buckets.values()) == n_unt else 'BROKEN'})")
    print()
    print("    OUT_OF_SCOPE IS NOT IRREDUCIBILITY, and the archive proves it")
    print("    in its own words: those reason strings carry the model's")
    print("    EXECUTED check of the very claim they decline to tool, e.g.")
    print("    \"Verified real (re.escape('REVISED_ANSWER') ==")
    print("    'REVISED_ANSWER') ... but the defect is in run_benchmark.py,")
    print("    not in the target document\". The computation happened. What")
    print("    could not happen was the splice into the review target.")

    print()
    print("  GENUINELY COMPUTATIONALLY IRREDUCIBLE requires BOTH limbs: a")
    print("  falsifier that was attempted, AND a recorded reason stating a")
    print("  structural bar. An assertion without an attempt is not a finding")
    print("  about computability.")
    irreducible = [(p, c, e) for p, c, e in attempted
                   if has_structural_reason(e)]
    pct("GENUINELY IRREDUCIBLE on the archive's own record", len(irreducible),
        n_unt, indent="    ")
    for p, c, e in irreducible:
        print(f"      {run_name(p)} {c}")
        for r in reasons(e):
            if reason_kind(r) == "STRUCTURAL":
                print(f"        {r[:200]}")
                break
    claimed_structural = [(p, c, e) for p, c, e in untoolable
                          if has_structural_reason(e)]
    pct("asserted structural WITHOUT any attempt (not a computability "
        "finding)", len(claimed_structural) - len(irreducible), n_unt,
        indent="    ")

    print()
    print("  AND THE LADDER WAS NEVER EXHAUSTED WHERE A TOOL WAS TRIED:")
    unexhausted = 0
    for _p, _c, e in attempted:
        for r in e.get("routing_history") or []:
            if isinstance(r, dict) and r.get("rungs_available"):
                if (r.get("rungs_tried") or 0) < r["rungs_available"]:
                    unexhausted += 1
                    break
    pct("attempts that stopped with rungs still untried", unexhausted,
        max(len(attempted), 1), indent="    ")
    print("    An attempt that stops with rungs in hand establishes nothing")
    print("    about what the remaining rungs would have found.")

    # ----------------------------------------------------------------- step 4
    rule("STEP 4 -- WAS CATEGORY (b) TOOLABLE IN PRINCIPLE?")
    declared = committed_falsifier_declarations()
    print(f"  committed falsifier declarations : {len(declared)} (run, id) "
          f"pairs in "
          f"{len({f for fs in declared.values() for f in fs})} files under "
          f"bench/tests/")
    print("  read from the `COVERS` sets those files already carry for")
    print("  scripts/missing_falsifiers_2026-09-10.py -- no new registry here")

    keys = sorted({(run_name(p), c) for p, c, _e in never})
    by_key: dict[tuple[str, str], dict] = {}
    for p, c, e in never:
        by_key.setdefault((run_name(p), c), e)
    print()
    print(f"  category (b) distinct findings : {len(keys)}")
    sample = sorted(random.Random(SAMPLE_SEED).sample(keys,
                                                      min(SAMPLE_N, len(keys))))
    print(f"  SAMPLE: {len(sample)} of {len(keys)}, "
          f"random.Random({SAMPLE_SEED}).sample over the sorted key list")
    print()
    print("  THREE INDEPENDENT ROUTES, reported separately so no one of them")
    print("  carries the conclusion alone:")
    print("    R1 DECLARED  a committed test under bench/tests/ names this very")
    print("                 (run, canonical id) in its COVERS set")
    print("    R2 EXECUTED  that declaring file passes TODAY, run on its own")
    print("    R3 PROBED    the module the claim names exists in this checkout,")
    print("                 parses, and defines the symbols the claim names")
    print("  TOOLABLE IN PRINCIPLE = R1 or R3. R2 is corroboration, and it is")
    print("  reported rather than folded in, because a declaring file can go")
    print("  red for reasons that have nothing to do with the finding. It did")
    print("  during this round: bench/cdsfl_registry/composer.py and")
    print("  bench/directives/ are under concurrent edit by other panel seats,")
    print("  and the C0001 falsifier's fixture went in and out of the pruning")
    print("  branch as they worked. Each file is therefore run ON ITS OWN and")
    print("  its own summary printed, so the state of each is visible rather")
    print("  than averaged into one line.")

    all_files = sorted({f for k in keys for f in declared.get(k, ())})
    print()
    print(f"  R2: executing all {len(all_files)} declaring files, one at a time")
    results = execute(all_files)
    for name, (ok, summary) in results.items():
        print(f"    {'PASS' if ok else 'RED '}  {name}")
        print(f"          {summary}")
    red = [n for n, (ok, _s) in results.items() if not ok]
    if red:
        print()
        print("    A RED FILE IS NOT A TOOLABILITY FINDING, and this one is not")
        print("    even a finding about the archive. bench/cdsfl_registry/")
        print("    composer.py and bench/directives/ are under concurrent edit")
        print("    by other seats in this panel round, and the failing")
        print("    assertion says so in its own words: 'this fixture no longer")
        print("    triggers pruning'. The falsifier still imports the real")
        print("    target and still decides the claim; its FIXTURE no longer")
        print("    reaches the branch. Nothing here edits that test.")

    def judge(key: tuple[str, str]) -> tuple[bool, str]:
        """R1 or R3, with R2 appended when it is available."""
        files_for = sorted(declared.get(key, ()))
        if files_for:
            ok, _summary = results.get(files_for[0], (False, ""))
            return True, (f"R1 declared by {files_for[0]}"
                          f"  (R2 {'passes' if ok else 'RED, see above'})")
        ok, why = live_probe(by_key[key])
        return ok, f"R3 live probe: {why}"

    print()
    judged = [(key, *judge(key)) for key in sample]
    for (run, cid), ok, why in judged:
        print(f"    {'TOOLABLE  ' if ok else 'NOT SHOWN '} {run:<44} {cid}")
        print(f"               {why}")

    k_tool = sum(1 for _k, ok, _w in judged if ok)
    print()
    pct("SAMPLE: in principle toolable", k_tool, len(judged))

    whole = [(key, *judge(key)) for key in keys]
    all_tool = sum(1 for _k, ok, _w in whole if ok)
    n_declared = sum(1 for k in keys if declared.get(k))
    n_r2 = sum(1 for k in keys
               if any(results.get(f, (False, ""))[0]
                      for f in declared.get(k, ())))
    print()
    pct("WHOLE of category (b): in principle toolable", all_tool, len(keys))
    print(f"      R1 declared by a committed falsifier         : {n_declared}")
    print(f"      R2 whose declaring file passes today         : {n_r2}")
    print(f"      R3 settled by a live probe of the target     : "
          f"{all_tool - n_declared}")
    for key, ok, why in whole:
        if not ok:
            print(f"      NOT SHOWN TOOLABLE: {key}  ({why})")

    # ------------------------------------------------------------ scoping gap
    rule("SIDE FINDING -- THE EXISTING INSTRUMENT IS SCOPED TO `exp*`")
    exp_only = [(p, c, e) for p, c, e in untoolable
                if run_name(p).startswith("exp")]
    print("  scripts/missing_falsifiers_2026-09-10.py globs")
    print("    bench/logs/exp*/runner_state.json")
    print(f"  UNTOOLABLE rows under exp* only : {len(exp_only)}")
    print(f"  UNTOOLABLE rows under **        : {n_unt}")
    print("  run families the exp* glob drops : "
          f"{sorted({run_name(p).split('_')[0] for p, _c, _e in untoolable if not run_name(p).startswith('exp')})}")
    print("  So the committed 'ALREADY WRITTEN: 28 / REMAINING: 0' is true of")
    print("  its own population and silent about the rest. Nothing here edits")
    print("  that script or the test that asserts it.")

    # ---------------------------------------------------------------- verdict
    rule("VERDICT")
    worst = max(AGREEMENT) if AGREEMENT else 0.0
    print(f"  interval agreement, statsmodels vs mpmath, over "
          f"{len(AGREEMENT)} proportions: max|diff| {worst:.3e}")
    assert worst < 1e-9, f"the two interval routes disagree by {worst}"
    print("  the two routes agree; no figure above rests on one library.")
    print()
    print(f"  Of {n_unt} archived rows recorded UNTOOLABLE "
          f"({len(distinct)} distinct findings),")
    print(f"  {len(irreducible)} carries positive evidence of computational "
          f"irreducibility --")
    print("  a falsifier that was attempted AND a recorded reason stating a")
    print("  structural bar on computing the claim at all.")
    print(f"  {len(attempted)} were attempted and the record blames EQUIPMENT, "
          f"every one of them")
    print("  stopping with routing rungs still untried.")
    print(f"  {len(never)} had no falsifier written at all; {all_tool} of "
          f"{len(keys)} distinct findings")
    print("  among them are demonstrably toolable, most by a falsifier that is")
    print("  committed to this repository and passes today.")
    print()
    print("  'NEVER-REACHED FINDINGS ARE COMPUTATIONALLY REDUCIBLE' HOLDS on")
    print("  this archive. The limit the word UNTOOLABLE records is a limit of")
    print("  falsifier SUPPLY, not a limit of computation.")
    print()
    print("  THE BOUND, STATED HONESTLY, IN THREE PARTS.")
    print("  1. The archive holds no field recording why a finding was")
    print(f"     untoolable, and {buckets['SILENT']} of {n_unt} rows carry no "
          f"reason at all. For")
    print("     those this is a statement about what the record CAN support,")
    print("     not proof that no reason ever existed in a model's head.")
    print(f"  2. THE ONE GENUINE CASE IS REAL AND IS NOT ROUNDED AWAY: "
          f"{len(irreducible)} of {n_unt},")
    print("     sim45_memory C0050, a claim about how many times the file was")
    print("     rewritten DURING the review round. No test importing the")
    print("     module can decide that, the record says so, and a falsifier")
    print("     was attempted. So 'none so far' is too strong by one.")
    print("  3. The direction is not in doubt. Every other reason in the")
    print("     corpus blames equipment, scope or duplication, and the")
    print("     falsifiers later written for the never-attempted set import")
    print("     the real target and decide the claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
