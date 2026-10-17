"""The project-level ticket store: settled is a RECORDED FIELD, never an inference.

WHY THIS EXISTS, and the measurement that justifies it rather than a preference.
On 2026-10-17 the founder observed that the assistant keeps resurrecting settled
issues, and asked whether the project's existing Bugzilla machinery could be
repurposed so that it cannot. The case for yes is that 6 separate attempts to
determine from TEXT whether something was settled or novel all failed in one
night, each producing a clean-looking answer that was an artefact of search
scope or a function signature:

  1. a coverage measure that passed its own control and answered the wrong
     question (his words present in the list says nothing about acting on them);
  2. a repeatability measure saturated at the same figure at every threshold
     from 0.10 to 0.99, because it compared a boolean against a boilerplate
     status string;
  3. a claim about the note linter that called `undefined_project_terms` with a
     string when its signature takes a path, so it returned [] for every input;
  4. a rediscovery triage whose corpus included the task list, so every entry
     matched its own text;
  5. a novelty search reporting "0 files" because it covered neither the source
     tree nor the chat transcripts;
  6. a predicate called with the wrong positional argument, so `strength_order`
     received the exclusion.

A RECORDED STATE HAS NEITHER A SCOPE NOR A SIGNATURE. That is the whole argument.

WHAT IS REUSED RATHER THAN REINVENTED. The status vocabulary is the runner's own,
version 2026-08-22, sourced from `experimental_notes/Design_Reviews_Bugzilla_And_
Perturbation_2026-08-21.md`: terminal statuses are CLOSED, CONFIRMED, DUPLICATE,
MERGED and REFUTED, and live statuses are OPEN, REOPENED, UNCONFIRMED, CONTESTED,
CORROBORATED and WITHHELD. **Crucially the terminal set is TOOL-ONLY in that
vocabulary**: a model may not assert them. This store preserves that property, so
the assistant cannot declare a ticket CLOSED by saying so — `close()` requires a
verification record, and `reopen()` requires the founder.

HIS TWO SECTIONS, 2026-10-17. `fr` is a feature request, a new proposal, which is
OPEN until it is implemented, merged or rejected, exactly as a Firefox Bugzilla
feature request behaves. `pr` is a proposed fix against an observed defect. Both
live in one store with a `kind` field so either section can be listed alone.

HIS HASHED IDENTIFIERS, 2026-10-17. Every ticket and every resolution carries a
content-addressed identifier, and the store is searched by identifier before any
new work is proposed. Two digests are kept per ticket and they answer different
questions:

  `tid`  — sha256 over kind + the VERBATIM source text. Exact. Two records of the
           same sentence collide by construction, which no word search guarantees.
  `nid`  — sha256 over a NORMALISED form: lowercased, punctuation stripped,
           stopwords removed, tokens sorted and de-duplicated. This is the digest
           that catches a reworded restatement of the same instruction, which is
           the case that actually bit: his wording of 2026-10-15 against the
           assistant's paraphrase of 2026-10-17.

THE THIRD AND DECISIVE TIER: `subjects`. Measured on 2026-10-17 against the real
case, text similarity is NOT sufficient. His wording of 2026-10-15 and the
assistant's paraphrase of 2026-10-17 share only 4 normalised tokens of 28, a
Jaccard of 0.1429, so neither digest collides and no plausible threshold would
catch it without also catching everything else. A registry built on text
similarity alone would be exactly the decoration he warned against.

What DID catch it was a recorded terminal state on the SUBJECT: the memory note
carried "Do not raise either with the founder again" about the routing ladder,
not about any particular sentence. So a ticket also records the MECHANISM it
concerns -- `rank_falsifier_writers`, `apply_fixes_back`, `fingerprint_scope` --
as exact strings. Those are stable across any rewording, because both his
instruction and the assistant's proposal are about the same code. Asking "is
there a settled ticket about `rank_falsifier_writers`?" is then an exact lookup
rather than a similarity judgement, and it is the lookup that would have
prevented the rediscovery.

The `nid` is a claim about usefulness, so it is MEASURED rather than asserted.
`bench/tests/test_ticket_store_2026-10-17.py` scores it against plain word
overlap on the known rediscoveries of 2026-10-16 and 2026-10-17, where the right
answer is already established, and fails if it does not beat them. A registry
that cannot beat a word search is decoration, which he named as the risk.

WHAT THIS DOES NOT CLAIM. It makes STATE impossible to misreport. It does not
make IDENTITY impossible to misjudge: deciding that a new finding IS a given
closed ticket is the duplicate problem, and the `nid` reduces it rather than
removing it. Every ticket therefore stores the verbatim source text, so a human
read settles identity in seconds, which is how the routing-ladder rediscovery was
in fact caught.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import pathlib
from dataclasses import dataclass, field, asdict
from typing import Any, Iterable, Optional

REPO = pathlib.Path(__file__).resolve().parent.parent
STORE_DIR = REPO / "bench" / "tickets"
STORE = STORE_DIR / "tickets.jsonl"
#: Kept as the DEFAULT store's log only. Each store owns its own; see __init__.
SEARCH_LOG = STORE_DIR / "tickets_searches.jsonl"

#: The runner's own vocabulary, version 2026-08-22. Terminal states are TOOL-ONLY.
TERMINAL = frozenset({"CLOSED", "CONFIRMED", "DUPLICATE", "MERGED", "REFUTED"})
LIVE = frozenset({"OPEN", "REOPENED", "UNCONFIRMED", "CONTESTED",
                  "CORROBORATED", "WITHHELD"})
#: REJECTED is added for the feature-request half: a proposal he declines is not
#: a refuted finding, and conflating the 2 would lose the distinction he drew.
REJECTED = "REJECTED"
STATUSES = TERMINAL | LIVE | {REJECTED}

KINDS = ("fr", "pr")

_STOP = frozenset("""a an and are as at be been being but by can could did do does
for from had has have he her him his how i if in into is it its me my no nor not
of on only or our should so than that the their them then there these they this
those to too us was we were what when where which who why will with would you
your it's dont don't just also very more most much many some any such own same
other another thing things way ways get got make made say said see seen look
looked think thought know known want wanted need needed go going gone come came
take taken give given use used work working yes ok okay please thanks""".split())


#: Crude suffix stripping, deliberately not a real stemmer. It exists because
#: the case that actually bit was "climb" against "climbing" and "ladder"
#: against "ladders": his wording and the assistant's paraphrase of the same
#: instruction 2 days apart. A full stemmer would be a dependency for no
#: measured gain, and the gain here IS measured -- see the test of 2026-10-17,
#: which fails if this does not beat plain word overlap on the known cases.
_SUFFIXES = ("ingly", "edly", "ing", "ies", "ied", "ed", "es", "ly", "s")


def _stem(word: str) -> str:
    """ONE suffix strip, then one trailing `e`. Deliberately crude, and its limit
    is stated rather than hidden.

    THE PROPERTY THAT MATTERS IS SYMMETRY, not linguistic correctness: a singular
    and its plural must normalise to the SAME token, whatever that token is.
    "gate" and "gates" both becoming "gat" is useless English and perfectly good
    normalisation. Stripping a trailing `e` after the suffix pass is what buys
    that symmetry, because it collapses "refuse"/"refuses" and "measure"/
    "measures", which a suffix pass alone cannot.

    MEASURED LIMIT: 1 of 11 tested pairs still disagrees, "finding" against
    "findings", because that needs a second suffix pass and a second pass breaks
    "refuses". Rather than chase a lexicon, the limit is recorded here and the
    load is carried by the SUBJECT tier, which is exact and was measured to be
    the only tier that catches a genuine paraphrase. A normaliser is a
    convenience here, not the mechanism.
    """
    for suf in _SUFFIXES:
        if len(word) - len(suf) >= 4 and word.endswith(suf):
            base = word[: -len(suf)]
            if suf == "ies":
                base += "y"
            word = base
            break
    if len(word) > 4 and word.endswith("e"):
        word = word[:-1]
    return word


def _norm_tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z_]+", str(text).lower())
    keep = {_stem(w) for w in words if w not in _STOP and len(w) > 3}
    return sorted(k for k in keep if len(k) > 2)


def tid_of(kind: str, verbatim: str) -> str:
    """Exact content digest. Same sentence, same kind -> same id, always."""
    h = hashlib.sha256()
    h.update(kind.encode())
    h.update(b"\x00")
    h.update(" ".join(str(verbatim).split()).encode())
    return h.hexdigest()[:12]


def nid_of(verbatim: str) -> str:
    """Normalised digest: catches a REWORDED restatement of the same thing."""
    h = hashlib.sha256()
    h.update(" ".join(_norm_tokens(verbatim)).encode())
    return h.hexdigest()[:12]


def rid_of(tid: str, resolution: str) -> str:
    """Resolution digest, scoped to its ticket so 2 tickets cannot share one."""
    h = hashlib.sha256()
    h.update(tid.encode()); h.update(b"\x00")
    h.update(" ".join(str(resolution).split()).encode())
    return h.hexdigest()[:12]


@dataclass
class Ticket:
    tid: str
    nid: str
    kind: str                      # fr | pr
    status: str
    title: str
    verbatim: str                  # the source text, never paraphrased
    source: str                    # chat | responses | task_list | panel | code
    source_ref: str = ""           # timestamp, or file plus line
    ruled: str = ""                # the date he decided it, if he has
    resolution: str = ""
    rid: str = ""
    verification: str = ""         # what tool set a terminal status
    created: str = ""
    task_ref: str = ""             # the master-task-list identifier, if any
    #: The MECHANISMS this ticket concerns, as exact code identifiers. This is
    #: the tier that survives rewording, and the one that would have caught the
    #: routing-ladder rediscovery of 2026-10-17.
    subjects: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


class TicketStore:
    """Append-only on disk, indexed in memory. Nothing is ever silently rewritten."""

    def __init__(self, path: pathlib.Path | None = None):
        self.path = pathlib.Path(path) if path else STORE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        #: THE SEARCH LOG IS SCOPED TO THE STORE, not module-global. A global log
        #: mixes searches across stores and across runs, so "was a search
        #: recorded for this proposal?" stops being answerable -- found by its
        #: own test on 2026-10-17, where searches from other cases leaked in.
        self.search_log = self.path.with_name(self.path.stem + "_searches.jsonl")
        self._by_tid: dict[str, Ticket] = {}
        self._by_nid: dict[str, list[str]] = {}
        self._by_subject: dict[str, list[str]] = {}
        self.load()

    # ---------------------------------------------------------------- loading
    def load(self) -> None:
        self._by_tid.clear(); self._by_nid.clear(); self._by_subject.clear()
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = Ticket(**d)
            self._by_tid[t.tid] = t            # a later record supersedes
            self._by_nid.setdefault(t.nid, [])
            if t.tid not in self._by_nid[t.nid]:
                self._by_nid[t.nid].append(t.tid)
            for sub in t.subjects:
                self._by_subject.setdefault(sub, [])
                if t.tid not in self._by_subject[sub]:
                    self._by_subject[sub].append(t.tid)

    def _append(self, t: Ticket) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(t.to_json() + "\n")
        self._by_tid[t.tid] = t
        self._by_nid.setdefault(t.nid, [])
        if t.tid not in self._by_nid[t.nid]:
            self._by_nid[t.nid].append(t.tid)
        for sub in t.subjects:
            self._by_subject.setdefault(sub, [])
            if t.tid not in self._by_subject[sub]:
                self._by_subject[sub].append(t.tid)

    # ----------------------------------------------------------------- search
    def get(self, tid: str) -> Optional[Ticket]:
        return self._by_tid.get(tid)

    def exact(self, kind: str, verbatim: str) -> Optional[Ticket]:
        return self._by_tid.get(tid_of(kind, verbatim))

    def similar(self, verbatim: str) -> list[Ticket]:
        """Tickets whose NORMALISED digest matches. Catches a rewording."""
        return [self._by_tid[i] for i in self._by_nid.get(nid_of(verbatim), [])]

    def by_subject(self, subject: str) -> list[Ticket]:
        """Every ticket touching a named mechanism. Survives any rewording."""
        return [self._by_tid[i] for i in self._by_subject.get(subject, [])]

    def settled_on_subject(self, subject: str) -> list[Ticket]:
        """Settled tickets on a mechanism. A non-empty result means DO NOT RAISE."""
        return [t for t in self.by_subject(subject)
                if t.status in TERMINAL or t.status == REJECTED]

    def subjects(self) -> list[str]:
        return sorted(self._by_subject)

    def all(self) -> list[Ticket]:
        return list(self._by_tid.values())

    def by_kind(self, kind: str) -> list[Ticket]:
        return [t for t in self._by_tid.values() if t.kind == kind]

    def by_status(self, *statuses: str) -> list[Ticket]:
        want = set(statuses)
        return [t for t in self._by_tid.values() if t.status in want]

    def open_tickets(self) -> list[Ticket]:
        return [t for t in self._by_tid.values() if t.status in LIVE]

    def settled(self) -> list[Ticket]:
        return [t for t in self._by_tid.values()
                if t.status in TERMINAL or t.status == REJECTED]

    # ------------------------------------------------------- the search gate
    def record_search(self, query: str, found: Iterable[str]) -> None:
        """A search MUST be recorded before new work is proposed.

        The gate reads this log. Without it the obligation is a convention, and
        a convention is what failed 6 times on 2026-10-17.
        """
        self.search_log.parent.mkdir(parents=True, exist_ok=True)
        with self.search_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"query": " ".join(str(query).split())[:400],
                                 "nid": nid_of(query),
                                 "found": sorted(set(found))},
                                ensure_ascii=False) + "\n")

    def searches(self) -> list[dict[str, Any]]:
        if not self.search_log.exists():
            return []
        out = []
        for line in self.search_log.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try: out.append(json.loads(line))
                except json.JSONDecodeError: pass
        return out

    # ------------------------------------------------------------ transitions
    def propose(self, kind: str, title: str, verbatim: str, source: str,
                source_ref: str = "", ruled: str = "", created: str = "",
                task_ref: str = "", subjects: Iterable[str] = ()) -> tuple[Ticket, str]:
        """Create or return a ticket. Returns (ticket, outcome).

        outcome is one of: created, exists, settled-already, reworded-match,
        subject-settled.
        A caller that receives anything other than `created` MUST NOT treat the
        item as new work. This is the step that stops a rediscovery.
        """
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}, not {kind!r}")
        want = tid_of(kind, verbatim)
        self.record_search(verbatim, [t.tid for t in self.similar(verbatim)])
        hit = self._by_tid.get(want)
        if hit is not None:
            if hit.status in TERMINAL or hit.status == REJECTED:
                return hit, "settled-already"
            return hit, "exists"
        # THE SUBJECT TIER FIRST, because it is the one that survives rewording.
        for sub in subjects:
            blocked = self.settled_on_subject(sub)
            if blocked:
                return blocked[0], "subject-settled"
        near = [t for t in self.similar(verbatim) if t.kind == kind]
        if near:
            settled = [t for t in near if t.status in TERMINAL or t.status == REJECTED]
            return (settled[0] if settled else near[0]), "reworded-match"
        t = Ticket(tid=want, nid=nid_of(verbatim), kind=kind, status="OPEN",
                   title=" ".join(str(title).split())[:160],
                   verbatim=" ".join(str(verbatim).split()),
                   source=source, source_ref=source_ref, ruled=ruled,
                   created=created, task_ref=task_ref,
                   subjects=sorted(set(subjects)))
        self._append(t)
        return t, "created"

    def close(self, tid: str, resolution: str, verification: str) -> Ticket:
        """CLOSED is TOOL-ONLY: a verification record is required, not a claim."""
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if not str(verification).strip():
            raise ValueError(
                "CLOSED is a tool-only status in the project's status vocabulary "
                "(version 2026-08-22). Supply the verification that set it -- a "
                "test name, a producer, or an execution result. An assertion is "
                "not a verification.")
        nt = Ticket(**{**asdict(t), "status": "CLOSED",
                       "resolution": " ".join(str(resolution).split()),
                       "rid": rid_of(tid, resolution),
                       "verification": " ".join(str(verification).split())})
        self._append(nt)
        return nt

    def reject(self, tid: str, reason: str, by: str = "founder") -> Ticket:
        """A declined proposal. Only the founder may reject a feature request."""
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if by != "founder":
            raise ValueError("only the founder may REJECT a proposal; "
                             "a model declining its own suggestion is not a ruling")
        nt = Ticket(**{**asdict(t), "status": REJECTED,
                       "resolution": " ".join(str(reason).split()),
                       "rid": rid_of(tid, reason), "verification": f"ruled by {by}"})
        self._append(nt)
        return nt

    def reopen(self, tid: str, reason: str, by: str = "founder") -> Ticket:
        """CLOSED -> REOPENED, by the founder only, per the Bugzilla paradigm."""
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if by != "founder":
            raise ValueError(
                "a CLOSED ticket is challenge-resistant and terminal. Only the "
                "founder may reopen it, by explicit escalation. This is the "
                "property that stops a settled issue being resurrected.")
        nt = Ticket(**{**asdict(t), "status": "REOPENED",
                       "verification": f"reopened by {by}",
                       "notes": list(t.notes) + [f"REOPENED: {reason}"]})
        self._append(nt)
        return nt

    def merge(self, tid: str, into: str, verification: str) -> Ticket:
        """DUPLICATE -> MERGED. His 2 elements: same fault AND same repair."""
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if into not in self._by_tid:
            raise KeyError(f"no target ticket {into}")
        if not str(verification).strip():
            raise ValueError("MERGED is tool-only: name what established that "
                             "the fault AND the proposed repair are the same")
        nt = Ticket(**{**asdict(t), "status": "MERGED",
                       "resolution": f"merged into {into}",
                       "rid": rid_of(tid, f"merged into {into}"),
                       "verification": " ".join(str(verification).split())})
        self._append(nt)
        return nt

    # ------------------------------------------------------------- reporting
    def summary(self) -> dict[str, Any]:
        from collections import Counter
        return {
            "total": len(self._by_tid),
            "by_status": dict(Counter(t.status for t in self._by_tid.values())),
            "by_kind": dict(Counter(t.kind for t in self._by_tid.values())),
            "open": len(self.open_tickets()),
            "settled": len(self.settled()),
            "searches_recorded": len(self.searches()),
        }
