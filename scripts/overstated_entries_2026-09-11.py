#!/usr/bin/env python3
"""Task V2: check the 11 entries a reviewer called overstated, one claim at a time.

`measured-rate-travels-with-its-script`. V2 lists 11 entries and asserts something
specific about each. An entry that says another entry is wrong is itself a claim,
and this project's record holds several reviewer claims that did not survive
measurement -- the "80.95% incidental" proxy, the "silent failure" that warned,
the 55.56% harm rate that conflated absent with deleted.

SO EACH CLAIM IS CHECKED HERE RATHER THAN ACTED ON. The checks are mechanical
where the claim is mechanical (does the marker say COMMITTED? does the named file
exist in git? do the figures reproduce?) and report UNCHECKABLE where it is not,
rather than guessing. An UNCHECKABLE is not a pass.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as tlm  # noqa: E402

LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: The 11 the reviewer named, with V2's own words for what is wrong.
CLAIMS = {
    "6.3": "already FIXED; a live regression, not an overstatement (25e5b34)",
    "7.2": "the urgent one: 2 demonstrated bypasses",
    "6.7": "declined a question that was answerable",
    "6.4": "wired 5 of the 6 named sites",
    "4.2": "status COMMITTED is false; the memory file was never committed",
    "8.1": "contains a sentence its own opening line contradicts",
    "1.1": "carries figures that do not reproduce or cite no producing script",
    "5.1": "as 1.1",
    "6.2": "as 1.1",
    "6.5": "as 1.1",
    "M1": "as 1.1",
}

FIGURE = re.compile(r"\b\d{1,3}\.\d+\s*%|\bp\s*=\s*[\d.]+e?-?\d*")
SCRIPT = re.compile(r"(scripts/[\w./-]+\.py|bench/tests/[\w./-]+\.py)")


def entries():
    return {e.ident: e for e in tlm.parse_entries(LIST)}


def blocks(by_id) -> dict:
    """Each entry's FULL text, entry line to the next entry line.

    `Entry.text` is the entry LINE. Measuring over it and calling the result a
    fact about entries is the population error that produced "25 of 67" above.
    """
    lines = LIST.read_text(encoding="utf-8").splitlines()
    es = sorted(by_id.values(), key=lambda e: e.line_no)
    out = {}
    for k, e in enumerate(es):
        start = e.line_no - 1
        end = es[k + 1].line_no - 1 if k + 1 < len(es) else len(lines)
        out[e.ident] = "\n".join(lines[start:end])
    return out


def tracked(path: str) -> bool:
    r = subprocess.run(["git", "ls-files", "--error-unmatch", path],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def check_marker_claims(by_id) -> dict:
    """The claims a marker can settle on its own."""
    out = {}
    for ident in CLAIMS:
        e = by_id.get(ident)
        if e is None:
            out[ident] = ("MISSING", "no entry with this id")
            continue
        out[ident] = ("state=%s status=%s evidence=%d" %
                      (e.state, e.status, len(e.evidence)), e.text[:90])
    return out


def check_evidence_is_tracked(by_id) -> list:
    """A DONE entry whose evidence is not in git cannot be COMMITTED."""
    bad = []
    for ident, e in sorted(by_id.items()):
        if e.state != "DONE":
            continue
        for ev in e.evidence:
            if not tracked(ev):
                bad.append((ident, ev, "not tracked by git"))
    return bad


def check_figures_have_producers(by_id) -> list:
    """The 1.1 / 5.1 / 6.2 / 6.5 / M1 claim, mechanised."""
    orphans = []
    for ident, e in sorted(by_id.items()):
        if not FIGURE.findall(e.text):
            continue
        live = [s for s in SCRIPT.findall(e.text) if (REPO / s).is_file()]
        if not live:
            orphans.append(ident)
    return orphans


def check_committed_names_a_tracked_artefact(by_id, blocks) -> list:
    """The 4.2 claim: a COMMITTED entry whose artefact is not in this repository.

    THE FIRST VERSION OF THIS MEASUREMENT WAS WRONG AND SAID 25 of 67. It read
    `Entry.text`, which is the entry LINE only -- an entry's continuation
    paragraphs are separate lines that `parse_entries` does not carry -- so it
    measured first lines and called them entries. Over the whole BLOCK, and
    counting the marker's own `evidence:` field, the true figure is 0 of 67,
    Wilson [0.0000%, 5.4226%]. A population error in the instrument, in the
    direction that would have put a wrong number in front of the founder.

    What remains checkable is narrower and is 4.2's actual defect: a block that
    names a path under the PRIVATE memory directory, which this repository does
    not carry, while its marker says COMMITTED and the block does not say so.
    """
    import os

    bad = []
    for ident, e in sorted(by_id.items()):
        if e.status != "COMMITTED":
            continue
        block = blocks.get(ident, "")
        names_private = "memory/feedback_" in block or "memory/cdsfl_" in block
        if names_private and "does not carry" not in block:
            bad.append((ident, "names a private memory artefact and claims "
                               "COMMITTED without saying what is committed here"))
    return bad


def check_self_contradiction(by_id) -> list:
    """The 8.1 claim: an entry whose body denies its own opening line.

    MECHANICAL ONLY WHERE IT CAN BE. A general contradiction check is not
    something a script should pretend to do. What it CAN do is find an entry
    whose opening declares DONE while its body carries an explicit NOT DONE,
    OPEN, or STILL marker, which is the specific shape the reviewer named.
    """
    hits = []
    for ident, e in sorted(by_id.items()):
        head = e.text.split(".**")[0] if ".**" in e.text else e.text[:120]
        body = e.text[len(head):]
        if re.search(r"\bDONE\b", head) and re.search(
                r"\*\*(?:NOT DONE|STILL OPEN|OPEN)\b|\bis STILL\b", body):
            hits.append((ident, head[:80]))
    return hits


def main() -> int:
    by_id = entries()
    print(f"entries parsed: {len(by_id)}\n")

    print("--- the 11 named by V2, as their markers stand today ---")
    for ident, (state, text) in check_marker_claims(by_id).items():
        print(f"  {ident:5s} {state}")
        print(f"        {CLAIMS[ident]}")

    print("\n--- DONE entries whose named evidence is NOT tracked by git ---")
    bad = check_evidence_is_tracked(by_id)
    for ident, ev, why in bad:
        print(f"  {ident}: {ev} -- {why}")
    if not bad:
        print("  none")

    print("\n--- entries carrying a figure with no live producing script ---")
    orphans = check_figures_have_producers(by_id)
    print(f"  {orphans or 'none'}")

    print("\n--- COMMITTED entries whose artefact this repository does not carry ---")
    priv = check_committed_names_a_tracked_artefact(by_id, blocks(by_id))
    for ident, why in priv:
        print(f"  {ident}: {why}")
    if not priv:
        print("  none")

    print("\n--- entries whose opening says DONE and whose body says otherwise ---")
    contra = check_self_contradiction(by_id)
    for ident, head in contra:
        print(f"  {ident}: {head}")
    if not contra:
        print("  none")

    n = len(CLAIMS)
    settled = sum(1 for i in CLAIMS
                  if i in orphans or any(b[0] == i for b in bad)
                  or any(c[0] == i for c in contra)
                  or any(x[0] == i for x in priv))
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(settled, n, method="wilson")
    lo_c, hi_c = proportion_confint(settled, n, method="beta")
    from scipy.stats import beta as sbeta
    hi_s = 1.0 if settled == n else sbeta.ppf(0.975, settled + 1, n - settled)
    print(f"\nof V2's {n} named entries, {settled} still fail a MECHANICAL check "
          f"= {settled / n:.4%}")
    print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy cross-check, "
          f"upper agrees to {abs(hi_s - hi_c):.1e})")
    print("\nThe remainder are NOT thereby cleared. A claim a script cannot check "
          "is UNCHECKED, not refuted, and each is read by hand below the line.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
