#!/usr/bin/env python3
"""Rule 32 is enforced on delivered DOCUMENTS and not on CHAT, so he has had to
ask twice for a descriptor beside every entry code.

HIS INSTRUCTION, 2026-11-10, verbatim: *"I can't always tell when you print
identifiers like B102 or C0003 (for example), if these are the same issues you
may have been discussing a few lines ago. I don't have access to your ticket
store, or any of the other resources you have to store these issues. Nor do I
have your ability to quickly look them up. I already asked you when you print
these labels, to include a short descriptor, so I can know what you are talking
about."*

WHY A PROMISE IS WORTH NOTHING HERE, IN HIS OWN PRECEDENT. His `no-word-numbers`
ruling records the identical shape: *"The failure was never the absence of a rule
or a checker; it was never running the checker."* Rule 32 of the note standard
already states this rule and already has a working predicate in
`scripts/note_vagueness_lint.py`. Its SCOPE is the gap: it is *"scoped to
delivered documents"*, because unscoped it fires on 412 of 1,187 notes. Chat was
never in scope, so the rule has never once been applied to the surface he
actually reads.

WHAT THIS MEASURES. Every assistant TEXT block in the session transcripts is
read, split into sentences, and run through the SAME predicate the note lint
uses -- `entry_subjects()` for the title words of each entry, `_subject_words()`
for the sentence, and a violation when an identifier known to the task list
appears in a sentence sharing none of its title's content words.

IT REUSES THE EXISTING INSTRUMENT RATHER THAN WRITING A SECOND ONE. A second
predicate would be 2 descriptions of 1 rule with no comparator, which is the
shape `execute-do-not-grep` names and which this project has withdrawn claims
over 4 times.

BOUNDS, STATED. An identifier the task list does not carry is SKIPPED, so a
mutation label like M3 or a probe label like P1 is never counted. A code inside
a quotation of HIS words is still counted, because this measures what HE reads,
not who typed it -- and that direction is the conservative one.

Run: python3 scripts/a_bare_entry_code_in_chat_2026-11-10.py [--limit N]
Exit 0 always: this reports a state.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


def _repo() -> pathlib.Path:
    for cand in (pathlib.Path(__file__).resolve().parent,
                 *pathlib.Path(__file__).resolve().parents):
        if (cand / "bench" / "domain_immune.py").is_file():
            return cand
    raise SystemExit("cannot locate the repository")


REPO = _repo()
SESSIONS = (pathlib.Path.home() / ".claude" / "projects"
            / "-Users-georgejackson-Developer-Projects")


def _iv(k: int, n: int):
    """((wilson_lo, wilson_hi), (cp_lo, cp_hi), cross_check) -- the RESERVED
    project contract, implemented here to it rather than shadowed by a
    formatter of the same name."""
    import numpy as np
    import mpmath as mp
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint
    mp.mp.dps = 40
    sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp = proportion_confint(k, n, alpha=0.05, method="beta")
    z = st.norm.ppf(0.975)
    p = k / n if n else 0.0
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    w2 = (max(0.0, cen - hw), min(1.0, cen + hw))

    #: SECOND ROUTE VIA THE EXACT BINOMIAL TAIL, NOT THE BETA QUANTILE.
    #: mpmath's `betainc` is the obvious mirror of `scipy.stats.beta.ppf` and it
    #: FAILED here -- `hypsum() failed to converge to the requested 166 bits`
    #: at these parameters, because the hypergeometric series behind the
    #: incomplete beta diverges for large a and b. The Clopper-Pearson bounds
    #: are DEFINED by the binomial tails, so computing those directly is both a
    #: genuinely independent route and numerically stable: the lower bound
    #: solves P(X >= k | p) = 0.025 and the upper solves P(X <= k | p) = 0.025.
    def _tail_ge(q, kk):
        return mp.fsum([mp.binomial(n, i) * q**i * (1 - q)**(n - i)
                        for i in range(kk, n + 1)])

    def _tail_le(q, kk):
        return mp.fsum([mp.binomial(n, i) * q**i * (1 - q)**(n - i)
                        for i in range(0, kk + 1)])

    def _bisect(fn, target):
        lo, hi = mp.mpf(0), mp.mpf(1)
        for _ in range(240):
            mid = (lo + hi) / 2
            if fn(mid) < target:
                lo = mid
            else:
                hi = mid
        return float((lo + hi) / 2)

    cp2 = (0.0 if k == 0 else _bisect(lambda q: _tail_ge(q, k), mp.mpf("0.025")),
           1.0 if k == n else _bisect(lambda q: -_tail_le(q, k),
                                      -mp.mpf("0.025")))
    cross = max(abs(sm[0] - w2[0]), abs(sm[1] - w2[1]),
                abs((cp[0] or 0.0) - cp2[0]), abs(cp[1] - cp2[1]))
    return ((sm[0], sm[1]), ((cp[0] or 0.0), cp[1]), cross)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--limit", type=int, default=0,
                    help="examine only the N most recent transcripts")
    ns = ap.parse_args(argv)

    sys.path.insert(0, str(REPO / "scripts"))
    import note_vagueness_lint as nvl             # the EXISTING predicate

    subjects = nvl.entry_subjects()
    if not subjects:
        print("FAIL: the task list yielded 0 entry subjects, so the predicate "
              "would accuse nothing and a 0 here would be a false 0")
        return 1

    files = sorted(SESSIONS.glob("*.jsonl"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    if ns.limit:
        files = files[:ns.limit]

    sent_re = re.compile(r"[^.!?\n]+[.!?]?")
    total = bare = 0
    offenders: dict[str, int] = {}
    examples: list[tuple[str, str]] = []

    for f in files:
        try:
            raw = f.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in raw:
            if '"type":"assistant"' not in line and '"type": "assistant"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:                       # noqa: BLE001
                continue
            for blk in (d.get("message", {}).get("content") or []):
                if not isinstance(blk, dict) or blk.get("type") != "text":
                    continue
                for s in sent_re.findall(blk.get("text", "") or ""):
                    for im in nvl._ENTRY_IDENT.finditer(s):
                        subj = subjects.get(im.group(1))
                        if not subj:
                            continue                # unknown code: never counted
                        total += 1
                        if not (subj & nvl._subject_words(s)):
                            bare += 1
                            offenders[im.group(1)] = offenders.get(
                                im.group(1), 0) + 1
                            if len(examples) < 6:
                                examples.append((im.group(1),
                                                 s.strip()[:118]))

    print("=" * 76)
    print("RULE 32 APPLIED TO CHAT FOR THE FIRST TIME")
    print("=" * 76)
    print(f"  transcripts read           : {len(files)}")
    print(f"  known entry codes printed  : {total}")
    print(f"  printed with NO descriptor : {bare}")
    if total:
        (wlo, whi), (clo, chi), cross = _iv(bare, total)
        print(f"\n  {bare} of {total} = {bare / total:.6f}")
        print(f"    Wilson          [{wlo:.6f}, {whi:.6f}]")
        print(f"    Clopper-Pearson [{clo:.6f}, {chi:.6f}]")
        print(f"    2 routes per interval agree to {cross:.3e}")
    print("\n  worst offenders:")
    _ranked = sorted(offenders.items(), key=lambda kv: -kv[1])
    for ident, k in _ranked[:10]:
        _w = sorted(subjects.get(ident, ()))
        words = _w[:4]
        tail = f" +{len(_w) - 4} more" if len(_w) > 4 else ""
        print(f"    {ident:6s} {k:4d} bare   (its subject words: "
              f"{', '.join(words)}{tail})")
    if len(_ranked) > 10:
        print(f"    ... and {len(_ranked) - 10} further identifier(s) "
              f"withheld, accounting for "
              f"{sum(v for _i, v in _ranked[10:])} of the {bare} bare uses")
    print("\n  examples, verbatim:")
    for ident, s in examples:
        print(f"    [{ident}] {s}")
    print("\n" + "=" * 76)
    print("  THE FIX IS NOT A PROMISE. The descriptor has to be AVAILABLE at the")
    print("  moment of writing, which is why it is injected into the turn")
    print("  context beside the open-entry list rather than looked up.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
