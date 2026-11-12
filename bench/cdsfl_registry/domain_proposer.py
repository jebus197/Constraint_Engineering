#!/usr/bin/env python3
"""PROPOSE a (domain, subdomain) from a task's own text, and say when it cannot.

★ WHY THIS EXISTS. Measured 2026-11-11 by syntax tree over the reference runner:
**1** command-line domain argument carrying a hardcoded default, **0** functions
that classify a domain from task content, and **0 of 67** archived run states
recording which domain the run used. So a run's domain was whatever the operator
typed, and nothing could propose it or check it afterwards.

★ IT PROPOSES; IT NEVER DECIDES. That is the founder's 2-sided steering design:
an explicit selection first, this proposer as a PROPOSAL the researcher confirms
or overrides in 1 action, and a conversation only where the proposal is
ambiguous. A classifier that decided would reproduce the fault it exists to
remove -- for 7 months every proof-based mathematics task received a box that
explicitly disclaimed it, because a default was taken from the alphabetically
first file in a directory.

★ THE VOCABULARY IS NOT INVENTED HERE. The score is the overlap between the
task's content words and the DISTINCTIVE terms of each subdomain's own expert
encoding, read through `domain_vocabulary`. Hand-written keyword lists would be
a second source of truth about what a domain is, and would drift from the
manifest the moment a subdomain was re-pathed. A term is DISTINCTIVE when it
appears in few encodings: a word in every box separates nothing.

★ AMBIGUITY IS A FIRST-CLASS OUTCOME, not a low score. `propose` returns
`ambiguous=True` when the top 2 candidates are not separated by `MARGIN`. The
acceptance condition for the steering surface is not that a conversation is
possible but that an ambiguous case ESCALATES instead of guessing -- a simulation
in which every case resolves cleanly has not tested the escalation path at all.

Costs nothing: reads local files, dispatches to no model.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import domain_vocabulary as V  # noqa: E402

#: The top 2 candidates must be separated by at least this share of the leader's
#: score, or the proposal is AMBIGUOUS and the surface must ask rather than guess.
#: A judgement, not a measurement: no figure here relates a margin to an outcome.
MARGIN = 0.15
#: A term in more than this share of encodings separates nothing, so it is
#: dropped from the vocabulary. Derived from the corpus at load time.
TOO_COMMON = 0.5
_WORD = re.compile(r"[a-z][a-z_-]{3,}")
#: Structural words that appear in every encoding by FORMAT rather than subject.
_FORMAT = frozenset("""
hard soft constraints verification procedures diagnostic heuristics known
failure modes exception catalogue tool limitations domain scope version tier
severity scale sources must never always should where when with that this
there their been have been being also than then only must_not
""".split())


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower())
            if w not in _FORMAT and len(w) > 3}


def vocabulary() -> dict[tuple[str, str], set[str]]:
    """Distinctive terms per (domain, subdomain), from the encodings themselves."""
    raw: dict[tuple[str, str], set[str]] = {}
    for dom in sorted(V.domains()):
        for sub in sorted(V.subdomains(dom)):
            try:
                p = REPO / V.encoding_path(dom, sub)
            except Exception:                                  # noqa: BLE001
                continue
            if not p.is_file():
                continue
            raw[(dom, sub)] = _tokens(p.read_text(encoding="utf-8", errors="replace"))
    if not raw:
        return {}
    n = len(raw)
    freq: dict[str, int] = {}
    for toks in raw.values():
        for t in toks:
            freq[t] = freq.get(t, 0) + 1
    #: A term in more than TOO_COMMON of the boxes is format or shared project
    #: vocabulary, not subject matter, so it cannot discriminate.
    return {k: {t for t in toks if freq[t] / n <= TOO_COMMON}
            for k, toks in raw.items()}


def score(task: str, vocab: dict | None = None) -> list[tuple[float, str, str]]:
    """Every candidate scored against the task, highest first."""
    vocab = vocabulary() if vocab is None else vocab
    want = _tokens(task)
    if not want or not vocab:
        return []
    out = []
    for (dom, sub), toks in vocab.items():
        hit = want & toks
        if not toks:
            continue
        #: Overlap normalised by the SQUARE ROOT of the box's vocabulary size, so
        #: a long encoding cannot win on length alone -- the defect a raw count
        #: would have, since the 22 new boxes run 109 to 142 lines against a mean
        #: of 65.2 for the 28 older ones.
        out.append((len(hit) / math.sqrt(len(toks)), dom, sub))
    out.sort(key=lambda r: (-r[0], r[1], r[2]))
    return out


def propose(task: str, vocab: dict | None = None) -> dict:
    """The proposal, with ambiguity as a first-class outcome."""
    ranked = score(task, vocab)
    if not ranked:
        return {"domain": None, "subdomain": None, "ambiguous": True,
                "reason": "no candidate matched any distinctive term",
                "top": [], "margin": None}
    best = ranked[0]
    if len(ranked) == 1 or best[0] <= 0:
        amb = best[0] <= 0
        return {"domain": best[1], "subdomain": best[2], "ambiguous": amb,
                "reason": "only 1 candidate scored" if not amb else "no term matched",
                "top": [(round(s, 6), d, u) for s, d, u in ranked[:3]],
                "margin": None}
    #: ★ AMBIGUITY IS MEASURED AT DOMAIN LEVEL, NOT SUBDOMAIN LEVEL. Corrected
    #: 2026-11-12 after the first run of the 4 steering cases got the DOMAIN right
    #: 4 times out of 4 and the ambiguity signal right only 2 times out of 4.
    #:
    #: THE REASON IS WHAT THE SURFACE IS FOR, not a threshold that fits the
    #: cases. The consequence scale, the critical level and the encoding are all
    #: properties of the DOMAIN. 2 subdomains of ONE domain share all 3, so a
    #: close call between them changes nothing a researcher needs to confirm --
    #: it is not a steering ambiguity. A close call between 2 DOMAINS changes
    #: which scale a finding is judged on, which is exactly what must be asked
    #: about.
    #:
    #: MEASURED ON THE FIRST RUN: a proof-theory task scored mathematics/proof
    #: then mathematics/applied, which the subdomain rule would have escalated
    #: for no gain; a clinical task scored biology/zoology then
    #: cross_domain/general, which is a genuine 2-domain contest and SHOULD ask.
    second_other = next((r for r in ranked[1:] if r[1] != best[1]), None)
    if second_other is None:
        return {"domain": best[1], "subdomain": best[2], "ambiguous": False,
                "reason": "every scoring candidate is in 1 domain, so the scale "
                          "is settled and only the subdomain is a preference",
                "top": [(round(s, 6), d, u) for s, d, u in ranked[:3]],
                "margin": None}
    margin = (best[0] - second_other[0]) / best[0] if best[0] else 0.0
    amb = margin < MARGIN
    return {
        "domain": best[1], "subdomain": best[2],
        "ambiguous": amb,
        "reason": (f"the nearest OTHER DOMAIN ({second_other[1]}) is within "
                   f"{margin:.4f}, under the {MARGIN} margin, so the scale is not "
                   f"settled and the surface must ASK rather than guess"
                   if amb else
                   f"clear of the nearest other domain ({second_other[1]}) by "
                   f"{margin:.4f}, so the scale is settled"),
        "top": [(round(s, 6), d, u) for s, d, u in ranked[:3]],
        "margin": round(margin, 6),
        "nearest_other_domain": second_other[1],
    }


#: ★ THE RECOVERY PATH, ENTRY B161, AND IT IS HIS DESIGN RATHER THAN MINE.
#: Added 2026-11-12. The 4 simulated steering chats exercised selecting a domain
#: and escalating to a dialogue, and never the case where the researcher simply
#: says the proposal is wrong. His words: the classifier *"can be told to say
#: some thing like 'Oh sorry about that. What category of problem would you like
#: to discuss today. Would you like me to search again for you, or would you
#: like to specify one exactly?' There can be a few allowed variations of this,
#: so the response doesn't always seem too mechanical."*
#:
#: 3 SEPARABLE PIECES AND THEY ARE DELIBERATELY NOT 1 FUNCTION: the repair turn,
#: a profile that survives a restart, and the test deciding when a query falls
#: outside the loaded profile. Only the 3rd has a measurable criterion today,
#: because the 4 simulated chats left a labelled set of 5 domain calls and 5
#: subdomain calls; the phrasings are a user-experience choice with no
#: falsifiable criterion, so they get a fitness review and not a falsification.
#:
#: THE VARIANTS ARE SELECTED BY INDEX, NEVER AT RANDOM. A random phrasing cannot
#: be reproduced in a test or in a transcript, and this project's whole record
#: is that an unreproducible behaviour is one nobody can check.
REPAIR_PHRASINGS = (
    "Sorry about that. What category of problem would you like to discuss "
    "today? I can search again, or you can name the category exactly.",
    "My mistake. Which area does this belong to? I can have another look, or "
    "you can tell me outright.",
    "Apologies, I had that wrong. What kind of problem are we working on? "
    "Happy to search again, or you can specify it.",
    "Sorry, let me try again. Which field is this in? I can look once more, or "
    "you can name it directly.",
)

#: Why the question is asked at all, offered only if the researcher queries it.
#: His words: *"the model can offer a short explainer that it just wants to be
#: sure it can load the correct profile for the researcher."*
EXPLAINER = ("I ask because the category decides which expert constraints get "
             "loaded for you, and which severity scale a finding is judged on. "
             "Getting it right once means I can keep the same profile loaded "
             "from here on.")


def repair_turn(attempt: int = 0) -> str:
    """What to say when the researcher rejects the proposed category.

    `attempt` selects a variant so a repeated repair does not read as a script.
    It is taken modulo the number of phrasings, so any integer is safe and the
    choice is REPRODUCIBLE -- a random pick could not be pinned by a test.
    """
    return REPAIR_PHRASINGS[int(attempt) % len(REPAIR_PHRASINGS)]


def explainer() -> str:
    """The short answer to 'why do you need to know?'."""
    return EXPLAINER


def profile_mismatch(task: str, profile: dict | None,
                     vocab: dict | None = None) -> dict:
    """Does `task` fall outside the profile already loaded for this researcher?

    REUSES `propose` rather than deciding again. A second predicate for "which
    domain is this" would be a second steering surface, and this project spent
    2026-11-11 removing exactly that: 2 domain vocabularies that agreed on 3
    names of 17, with every routing decision depending on which one a caller
    happened to read.

    AN AMBIGUOUS PROPOSAL ASKS; IT DOES NOT SILENTLY KEEP THE PROFILE. Keeping
    it would judge a finding on a scale nobody chose, which is the same silent
    default `consequence_domain` was written to remove.
    """
    loaded = list((profile or {}).get("domains") or [])
    pr = propose(task, vocab)
    if pr.get("ambiguous"):
        return {"mismatch": True, "resteer": True, "proposed": pr.get("domain"),
                "loaded": loaded, "proposal": pr,
                "why": (f"the proposal is ambiguous ({pr.get('reason')}), so the "
                        f"loaded profile cannot be assumed to cover it")}
    if not loaded:
        return {"mismatch": True, "resteer": True, "proposed": pr.get("domain"),
                "loaded": loaded, "proposal": pr,
                "why": "no profile is loaded yet, so the first steering chat is owed"}
    if pr.get("domain") in loaded:
        return {"mismatch": False, "resteer": False, "proposed": pr.get("domain"),
                "loaded": loaded, "proposal": pr,
                "why": (f"{pr.get('domain')} is already in the loaded profile, so "
                        f"no steering chat is needed")}
    return {"mismatch": True, "resteer": True, "proposed": pr.get("domain"),
            "loaded": loaded, "proposal": pr,
            "why": (f"{pr.get('domain')} is not in the loaded profile {loaded}, so "
                    f"an additional encoding has to be chosen")}


def accept(profile: dict | None, domain: str) -> dict:
    """Add a domain to the loaded profile, without dropping what is there.

    ADDITIVE BY CONSTRUCTION, and that is his design rather than a convenience:
    *"the new (or additional) profile/encoding can be loaded"*. A researcher who
    moves between 2 fields keeps both, so the 2nd steering chat does not undo
    the 1st.
    """
    doms = list((profile or {}).get("domains") or [])
    d = V.resolve(domain)   # the ONE vocabulary, never a second resolver
    if d not in doms:
        doms.append(d)
    out = dict(profile or {})
    out["domains"] = doms
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Propose a (domain, subdomain) for a task's text. Proposes "
                    "only; never decides. Reads local files, dispatches to no model.")
    ap.add_argument("task", nargs="?", help="the task text")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--vocab-size", action="store_true",
                    help="report the distinctive vocabulary per candidate and exit")
    a = ap.parse_args()
    if a.vocab_size:
        v = vocabulary()
        print(f"{len(v)} candidate(s) with a distinctive vocabulary")
        for (d, s), t in sorted(v.items()):
            print(f"  {d}/{s}: {len(t)} distinctive term(s)")
        return 0
    if not a.task:
        ap.error("a task text is required unless --vocab-size is given")
    r = propose(a.task)
    if a.json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"PROPOSAL: {r['domain']}/{r['subdomain']}")
    print(f"  ambiguous: {r['ambiguous']}")
    print(f"  reason   : {r['reason']}")
    for s, d, u in r["top"]:
        print(f"    {s:.6f}  {d}/{u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
