#!/usr/bin/env python3
"""B22's remaining half, measured: the harness is domain-general in PROMPT TEXT
and almost never in its DECISIONS.

HIS QUESTION, verbatim: *"CDSFL has been envisaged from the outset as a general
purpose STEM calculator, operating on strict Popperian falsification principles.
But in order for that to be true the entire harness has to be as equally useful
against a wide range of STEM related topics, as it currently is for code."* He
directed it to a free panel *"not only asking if we are there already or not, but
if any improvements or modifications may be required"*.

WHY A MEASUREMENT RATHER THAN A PANEL ANSWER. 2 panel rounds already ran on the
adjacent question of what a PROOF means outside code, and a 3rd was nearly
dispatched on an answered question. What those rounds did NOT answer is the
*there yet* half, and that half is countable rather than deliberative: either
the live path changes what it does on the domain, or it does not.

THE DISTINCTION THIS SCRIPT DRAWS, and it is the whole measurement. A module
that MENTIONS a domain may only be passing a label into a prompt. A module with
a BRANCH whose test involves the domain is making a DECISION on it. B22's own
evidence already records that the policy merge returns 10 distinct merged
policies for 10 domains -- so the prompt side is real. This counts the other
side.

WHAT IT FOUND, 2026-11-10, and the headline is the runner. The canonical
runner `bench/reference_runner_v3.py` carried **0** domain-conditioned branches
at HEAD. Tonight's B88 route -- his ruling that the verification set comes from
the STEM topic -- is the FIRST domain-conditioned decision in it.

THE HONEST READING. "Not yet", with a number attached instead of an impression,
and the number is small enough that the prompt/decision gap is the finding
rather than a quibble. It does not say the harness cannot review non-code STEM:
B22's own record has it converging on `domain=mathematics` 3 times. It says the
machinery's DECISIONS are still overwhelmingly domain-blind.

Run: python3 scripts/is_the_harness_domain_general_in_its_decisions_2026-11-10.py
Exit 0 always; this reports a state rather than asserting a pass condition.
"""
from __future__ import annotations

import ast
import pathlib
import re
import subprocess


def _find_repo() -> pathlib.Path:
    for start in (pathlib.Path(__file__).resolve().parent,
                  pathlib.Path.cwd().resolve()):
        for cand in (start, *start.parents):
            if (cand / "bench" / "reference_runner_v3.py").is_file():
                return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
RUNNER = "bench/reference_runner_v3.py"


def live_modules() -> list[pathlib.Path]:
    """Product modules only: no archived sandboxes, no tests, no scripts."""
    out = []
    for sub in ("bench", "bench/cdsfl_registry"):
        for p in sorted((REPO / sub).glob("*.py")):
            if "logs" in p.parts or "seat_evidence" in p.parts:
                continue
            out.append(p)
    return out


def domain_branches(src: str) -> list[tuple[int, str]]:
    """Branches whose TEST involves a domain — a decision, not a label."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)):
            try:
                t = ast.unparse(node.test)
            except Exception:
                continue
            if re.search(r"\bdomain", t):
                out.append((getattr(node, "lineno", 0), t[:88]))
    return out


#: NOT the canonical `_iv`. Renamed 2026-11-10 because `_iv` is a
#: RESERVED NAME in this tree: 50 scripts define it with one contract --
#: `_iv(k, n) -> ((wilson_lo, wilson_hi), (cp_lo, cp_hi), cross_check)` --
#: and `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`
#: LOADS every `def _iv` under `scripts/` and requires them all to agree
#: to 12 decimals. This helper returns formatted output instead, so
#: taking that name made 11 assertions fail on a contract it never
#: claimed to implement. A name collision, not a contract dispute.
def _iv_line(k: int, n: int) -> str:
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint
    sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = st.norm.ppf(0.975)
    p = k / n
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (f"{k} of {n} = {p:.6f}  Wilson statsmodels "
            f"[{sm[0]:.6f}, {sm[1]:.6f}]  scipy+numpy "
            f"[{max(0.0, cen - hw):.6f}, {min(1.0, cen + hw):.6f}]")


def main(argv=None) -> int:
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran. The description is taken
    #: from the module docstring so the usage text cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    mods = live_modules()
    mentions, deciders = [], []
    for p in mods:
        try:
            src = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(r"\bdomain\b", src):
            mentions.append(p)
        b = domain_branches(src)
        if b:
            deciders.append((p, len(b)))

    print("=" * 76)
    print("IS THE HARNESS DOMAIN-GENERAL IN ITS DECISIONS, OR ONLY IN ITS PROMPTS?")
    print("=" * 76)
    print(f"\n  live product modules scanned: {len(mods)}")
    print(f"  MENTION a domain:    {_iv_line(len(mentions), len(mods))}")
    print(f"  DECIDE on a domain:  {_iv_line(len(deciders), len(mods))}")

    print("\n  the modules that decide, most first:")
    for p, n in sorted(deciders, key=lambda t: -t[1]):
        print(f"    {str(p.relative_to(REPO)):46s} {n:3d} branch(es)")

    # The headline: the canonical runner, then against HEAD.
    live = (REPO / RUNNER).read_text(encoding="utf-8", errors="ignore")
    head = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{RUNNER}"],
                          capture_output=True, text=True).stdout
    lb, hb = domain_branches(live), domain_branches(head) if head else []
    print(f"\n  THE CANONICAL RUNNER, {RUNNER}")
    print(f"    at HEAD: {len(hb)} domain-conditioned branch(es)")
    print(f"    now    : {len(lb)}")
    for ln, t in lb:
        print(f"      line {ln}: {t}")
    if head and len(lb) > len(hb):
        print("\n    => the B88 route is the FIRST domain-conditioned decision")
        print("       in the canonical runner.")

    print("\n" + "=" * 76)
    print("  THE READING: domain-general in PROMPT COMPOSITION, which B22's own")
    print("  evidence establishes (10 distinct merged policies for 10 domains),")
    print("  and almost entirely domain-BLIND in its decisions. That is the")
    print("  'there yet' half of his question, with a number instead of an")
    print("  impression. It does NOT say the harness cannot review non-code")
    print("  STEM -- the record has it converging on domain=mathematics 3 times.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
