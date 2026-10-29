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

HIS TWO SECTIONS, 2026-10-17, WITH ONE MARKER CHANGED AND THE REASON RECORDED.
`fr` is a feature request, a new proposal, which is OPEN until it is implemented,
merged or rejected, exactly as a Firefox Bugzilla feature request behaves. The
second section is `pf`, a proposed fix against an observed defect.

HE PROPOSED `pr` FOR THAT SECOND MARKER, AND `pr` IS ALREADY TAKEN. His own
command list at ~/Desktop/keyboard_shortcuts.txt reads "pr = Full panel review.
cc2, cx, ge, cgpt, ds, sy, sth, f, e, d", and he uses it often to order a panel
round. Measured before the change: 4 of 4 of his real panel-review usages --
a bare `pr` on its own line, `pr` after a command list, `pr:` with a sentence,
and `pr` at the end of a sentence -- were harvested by the marker as proposed
fixes. So registering `pr` would have turned every panel order into a ticket and
left the panel command ambiguous. `pf` is unused in all 3 command lists and
collides with nothing. The substance of his design is unchanged: 2 sections, 2
markers, extracted from chat and from his replies alike. HE MAY OVERRULE THIS
NAMING; the collision is the reason, not a preference.

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
def _subjects_in(text: str) -> list[str]:
    """The code subjects a proposal names, through the harvester's own parser.

    Imported lazily so the store does not depend on `scripts/` at import time;
    returns an empty list if the harvester is unavailable, because surfacing by
    subject is an ADDITION to the hashed tiers and its absence must not stop a
    proposal being registered.
    """
    try:
        import importlib.util
        import pathlib as _pl
        import sys as _sys
        path = (_pl.Path(__file__).resolve().parents[1] / "scripts"
                / "harvest_tickets_2026-10-17.py")
        if not path.is_file():
            return []
        if "ticket_harvester" not in _sys.modules:
            spec = importlib.util.spec_from_file_location(
                "ticket_harvester", path)
            mod = importlib.util.module_from_spec(spec)
            _sys.modules["ticket_harvester"] = mod
            spec.loader.exec_module(mod)
        return list(_sys.modules["ticket_harvester"].subjects_in(text))
    except Exception:                                              # noqa: BLE001
        return []


TERMINAL = frozenset({"CLOSED", "CONFIRMED", "DUPLICATE", "MERGED", "REFUTED", "INVALID", "DEPRECATED"})
LIVE = frozenset({"OPEN", "REOPENED", "UNCONFIRMED", "CONTESTED",
                  "CORROBORATED", "UNDECIDED",
                  #: ★ LEGACY, READ-ONLY. The store is APPEND-ONLY, so the 5
                  #: historical rows that carry WITHHELD must still load. It is
                  #: kept in the set for that reason alone and is never written
                  #: again -- `_LEGACY_STATUSES` below is what refuses it on a
                  #: write. His question of 2026-10-23 is why it was renamed:
                  #: "Why would something be 'withheld', and from whom?" The
                  #: answer was that it withholds a MERGE and not information,
                  #: which the word did not say. UNDECIDED does.
                  #:
                  #: THE RUNNER'S FINDING VOCABULARY KEEPS WITHHELD. These are 2
                  #: different universes -- tickets and findings -- and the store
                  #: only borrowed the word. `bench/ux_backend_2026-10-20.py`
                  #: names WITHHELD for FINDINGS and must not be changed.
                  "WITHHELD"})

#: Statuses that may be READ from the log but never WRITTEN again.
_LEGACY_STATUSES = frozenset({"WITHHELD"})

#: How identical 2 repairs must be before his condition (b) is satisfied. 0.95
#: rather than 1.0 because a repair carries whitespace and path prefixes that
#: differ without the repair differing; the measurement normalises whitespace
#: first. Measured on the archive, 21 of 84 comparable merged pairs clear this
#: floor and 63 do not, so it separates the 2 cases rather than admitting all.
DUPLICATE_REPAIR_FLOOR = 0.95

#: ★ STEP 2, HIS APPROVAL 2026-10-24: INVALID, the one genuine gap the Bugzilla
#: comparison found. Mozilla's meaning is "intended behaviour -- not a bug", and
#: nothing in either of our vocabularies said that. REFUTED is NOT the same: its
#: own definition is "a falsifier was executed and did not fire", which conflates
#: "the claim was wrong" with "the instrument was wrong". A correct finding with a
#: bad falsifier and a non-finding with a sound falsifier both landed in REFUTED.
#: Measured: `finding_category` is empty for 3,102 of 3,237 findings, 95.8295%,
#: Wilson [95.0847%, 96.4656%], so no field recorded it either.
#: REJECTED is added for the feature-request half: a proposal he declines is not
#: a refuted finding, and conflating the 2 would lose the distinction he drew.
REJECTED = "REJECTED"
STATUSES = TERMINAL | LIVE | {REJECTED}

#: THE 4 KINDS. `wr` WAS ADDED 2026-10-20 ON HIS INSTRUCTION: "wr is a valid
#: section in the Bugzilla registry, and you should use it to track all remaining
#: outstanding work, and refer back to this before risking constantly referring
#: back to me and requesting my verdict". It is NOT a proposal and NOT a repair:
#: it is settled work whose execution is deferred, so it must never surface as
#: something awaiting his decision. R1, the zero-plant control, is the type case:
#: ruled 2026-08-07 and again 2026-09-06, and carried 66 days as an open question
#: because no kind fitted it.
#: `fr` a feature request, `pf` a proposed fix against an observed
#: defect, and `qs` A QUESTION -- his instruction of 2026-10-19: *"From now on qs
#: = Question. Questions should be given their own unique hashed ID in the
#: registry, like the other categories, like 'fr' feature request, and 'pf',
#: proposed fix, so they can be tied directly to the problems they address and so
#: that in future you can't lose them, or forget which issues they address."*
#:
#: WHY A QUESTION NEEDS ITS OWN KIND RATHER THAN A STATUS. A question is not a
#: smaller proposal: its resolution is an ANSWER, not a build, and the 2 travel in
#: opposite directions. 72 of his 318 annotations are questions owed back to him,
#: and until now they sat as `pf` rows the gate reported as work, which is how a
#: question gets read as a task and then dropped when the task turns out not to
#: exist. `tid_of` already digests the kind, so the same sentence recorded as a
#: question and as a proposed fix takes 2 distinct identities, which is correct:
#: answering the question does not build the fix.
#:
#: HOW IT IS TIED TO WHAT IT ASKS ABOUT, using the fields that already exist
#: rather than a new one. `task_ref` names the master-task-list entry, `subjects`
#: the exact code identifiers, and `anchor` the file and ordinal of his
#: annotation. Those 3 are the same ties every other kind uses and they already
#: survive rewording, so no schema change is needed to satisfy his requirement.
KINDS = ("fr", "pf", "qs", "wr")

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


def tid_of(kind: str, verbatim: str, task_ref: str = "", anchor: str = "") -> str:
    """Exact identity digest: kind, text, and any explicit task reference.

    THE TASK REFERENCE IS PART OF THE IDENTITY, and leaving it out was a defect
    worse than the one it was meant to fix. Found 2026-10-17 by this module's own
    test: 2 task entries about the same mechanism, worded identically, produced
    the SAME digest. So creating a separate ticket for the second overwrote the
    first in the index -- and the first was CLOSED, so a closed record was
    destroyed by a later open one. Over-merging hides work; this DELETED it.

    A caller that names no reference still gets pure content addressing, which is
    what makes deduplication work for chat and for his replies.

    WHERE A REFERENCE EXISTS IT IS THE WHOLE IDENTITY, and the text is excluded.
    CORRECTED 2026-10-17 after the first form was measured and found unstable.
    Digesting the text as well means the identity moves whenever the entry is
    reworded -- and the entry is reworded every time an addendum is written. The
    consequences were both observed, not predicted:

      * 5 references -- R10, 3.2, 6.2, B15 and B20 -- already carried 2 tickets
        each, because an addendum recording a NEIGHBOUR as built sat above the
        entry in a shared block and changed the text the digest read.
      * Improving the extraction rule itself re-minted 114 of 141 identities in
        one step, which would have duplicated the entire register and orphaned
        every hashed identifier already cited.

    A reference is unique within the list -- 141 entries, 141 distinct
    references, verified -- so excluding the text cannot cause the collision the
    reference was added to prevent. Two identically-worded entries still get
    different identities, because they have different references. What it buys
    is that the identifier a reader cites survives every subsequent edit to the
    entry's prose, which is what the founder's ruling of 2026-10-17 requires of
    a register that must be searched before any work is proposed.
    AND AN `anchor` SERVES THE SAME PURPOSE WHERE NO REFERENCE EXISTS, added
    2026-10-17. His annotations carry no task reference, so they were addressed
    purely by content -- and his shortest rulings are his most repeated words.
    Measured: "Do it." appears 3 times and "Fix it." twice among the annotations
    of October 2026, each on a DIFFERENT subject. Content addressing collapses
    those 3 rulings into 1 ticket, which loses 2 of them silently. The anchor is
    the annotation's own `file:line`, which is unique and stable, so each ruling
    becomes its own ticket while 2 harvests of the SAME line still agree.

    PRECEDENCE: a task reference wins, then an anchor, then the content. Content
    addressing survives untouched for any caller that supplies neither, which is
    what makes deduplication work for chat.
    """
    h = hashlib.sha256()
    h.update(kind.encode())
    h.update(b"\x00")
    if task_ref:
        h.update(str(task_ref).encode())
    elif anchor:
        h.update(str(anchor).encode())
    else:
        h.update(" ".join(str(verbatim).split()).encode())
    return h.hexdigest()[:12]


def nid_of(verbatim: str) -> str:
    """Normalised digest: catches a REWORDED restatement of the same thing."""
    h = hashlib.sha256()
    h.update(" ".join(_norm_tokens(verbatim)).encode())
    return h.hexdigest()[:12]


def norm_title(title: str) -> str:
    """THE ONE normalisation of a ticket's search label.

    WRITTEN ONCE BECAUSE 2 EXPRESSIONS OF IT CAUSED UNBOUNDED CHURN. Measured
    2026-10-17: `propose` and `retitle` each normalised whitespace and then
    truncated to 160, while the harvester compared the stored label against
    its OWN untruncated computation. Truncating a normalised string at 160 can
    leave a TRAILING SPACE, which `" ".join(split())` then strips, so the
    stored label was 159 characters where the caller held 160. The comparison
    could never succeed: 18 of 141 rows re-wrote an identical record on every
    single run, appending to a file that is append-only by design.

    This is the same shape the note linter records in `paragraphs()`, where 2
    expressions of one paragraph rule drifted apart and silently broke an
    exemption set. So the rule lives here, callers compare against this
    function rather than against their own spelling of it, and the strip comes
    AFTER the truncation rather than before.
    """
    return " ".join(str(title).split())[:160].strip()


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
    kind: str                      # fr | pf | qs
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
    #: THE STABLE IDENTITY OF AN ANNOTATION, where no task reference exists:
    #: `<file>#<ordinal among identical texts in that file>`. His shortest
    #: rulings repeat verbatim -- "Do it." 3 times across October 2026, twice in
    #: one file -- so content addressing collapsed separate rulings into one
    #: ticket. The ordinal is used rather than a line number because he
    #: RE-ANNOTATES files, which shifts every line below the insertion and would
    #: re-mint every identity in that file.
    anchor: str = ""
    #: The MECHANISMS this ticket concerns, as exact code identifiers. This is
    #: the tier that survives rewording, and the one that would have caught the
    #: routing-ladder rediscovery of 2026-10-17.
    subjects: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    #: ★ DEFERRED AND BLOCKER, added 2026-10-24 on his ruling. His words, which
    #: are the whole specification: *"If a blocker is a true blocker, that would
    #: mean that no other work could proceed until that blocker was cleared. Is
    #: that not what a 'blocker' is? If it doesn't block work from continuing and
    #: can be addressed without detriment at the end of a task list, then record
    #: it and present it clearly once all other tasks that can be completed are
    #: completed."*
    #:
    #: THEY ARE FIELDS AND NOT STATUSES, deliberately. Adding 2 members to
    #: `STATUSES` would reach the harvester, the summary, and every guard that
    #: asserts on the vocabulary; a field is read by the one gate that needs it
    #: and is invisible to everything else. They are also fields and not notes,
    #: because `notes` is prose and a gate that parses prose to decide state is
    #: the shape this project keeps finding wrong.
    #:
    #: `deferred` holds the date it was set aside to the END of the list; it is
    #: still live work and is PRESENTED when nothing workable remains.
    #: `blocker` holds the reason nothing else can proceed, and `declare_blocker`
    #: REFUSES to set it while any workable ticket exists, because by his
    #: definition that would not be a blocker.
    deferred: str = ""
    deferred_reason: str = ""
    blocker: str = ""
    #: ★ HIS DEFINITION OF A DUPLICATE, 2026-10-16, which the harness did not
    #: implement: *"a duplicate can only be called a duplicate, if a) it finds the
    #: same fault and b) if the proposed repair is in fact identical."* Condition
    #: (b) had no representation anywhere, so `duplicate_of` records WHICH ticket
    #: and `repair_identity` records the measured similarity of the 2 repairs.
    duplicate_of: str = ""
    repair_identity: str = ""
    #: ★ DEPRECATED, his design of 2026-10-24: *"where two fixes are aimed at the
    #: same target/issue, and one fix is clearly better ... then that better fix
    #: can replace an existing fix and the existing fix can be marked as
    #: 'deprecated'."* `superseded_by` names the winning ticket and
    #: `supersession_evidence` carries the MEASUREMENT that it dominates -- his
    #: standard is "demonstrably does the job better", so an assertion is refused.
    superseded_by: str = ""
    supersession_evidence: str = ""

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
        #: THE IDENTITY A TICKET'S OWN FIELDS IMPLY -> the tid it is STORED at.
        #: Empty for every ticket raised normally, because `tid_of` over its own
        #: fields reproduces its tid exactly. It carries exactly one entry per
        #: ticket repaired by `adopt_identity`, which fills in a missing
        #: `task_ref` or `anchor` WITHOUT re-keying the record. Without this
        #: bridge, `exact()` would compute the newly-implied digest and miss the
        #: ticket -- a producer and a consumer that each describe themselves
        #: correctly and disagree with each other, which is the defect shape
        #: `execute-do-not-grep` names and the one this project has measured most.
        self._by_identity: dict[str, str] = {}
        #: token -> tids, built lazily, dropped on any mutation.
        self._word_index: tuple | None = None
        self.load()

    # ---------------------------------------------------------------- loading
    def load(self) -> None:
        self._by_tid.clear(); self._by_nid.clear(); self._by_subject.clear()
        self._by_identity.clear()
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
            self._index_identity(t)
        #: A RELOAD INVALIDATES THE INDEX AS SURELY AS AN APPEND. Placed after
        #: the loop, at method level: the first attempt put it inside the loop
        #: body at the wrong indent and would have rebuilt the index once per
        #: line of a 1,925-line log. It raised IndentationError immediately,
        #: which is the cheap kind of mistake; the expensive kind is the one
        #: that parses.
        self._word_index = None

    def _append(self, t: Ticket) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(t.to_json() + "\n")
        #: EVERY MUTATION FUNNELS THROUGH HERE -- 10 call sites, verified by
        #: grep over `_append(` -- so this plus `load` are the only 2 places the
        #: word index can go stale. A stale index is the dangerous failure: a
        #: newly raised ticket would be INVISIBLE to word search, which is the
        #: duplicate the register exists to catch.
        self._word_index = None
        self._by_tid[t.tid] = t
        self._by_nid.setdefault(t.nid, [])
        if t.tid not in self._by_nid[t.nid]:
            self._by_nid[t.nid].append(t.tid)
        for sub in t.subjects:
            self._by_subject.setdefault(sub, [])
            if t.tid not in self._by_subject[sub]:
                self._by_subject[sub].append(t.tid)
        self._index_identity(t)

    def _index_identity(self, t: Ticket) -> None:
        """Register an alias ONLY where a ticket's fields imply a digest that is
        not the one it is stored at. For every ticket raised normally the 2 agree,
        so this adds nothing and the index stays the size of the repair set."""
        implied = tid_of(t.kind, t.verbatim, t.task_ref, t.anchor)
        if implied != t.tid:
            self._by_identity[implied] = t.tid

    # ----------------------------------------------------------------- search
    def get(self, tid: str) -> Optional[Ticket]:
        return self._by_tid.get(tid)

    def exact(self, kind: str, verbatim: str, task_ref: str = "",
              anchor: str = "") -> Optional[Ticket]:
        """The ticket at this exact identity, following an adoption alias.

        THE STORED TID IS TRIED FIRST and the alias only as a fallback, so a
        ticket raised normally is reached by exactly the path it always was.
        The fallback exists because `adopt_identity` fills in a missing
        `task_ref` or `anchor` without re-keying the record: after it runs, the
        digest the ticket's own fields imply is no longer the key it sits under,
        and a caller supplying that reference would otherwise raise a duplicate.
        """
        digest = tid_of(kind, verbatim, task_ref, anchor)
        hit = self._by_tid.get(digest)
        if hit is not None:
            return hit
        aliased = self._by_identity.get(digest)
        return self._by_tid.get(aliased) if aliased else None

    def similar(self, verbatim: str) -> list[Ticket]:
        """Tickets whose NORMALISED digest matches. Catches a rewording."""
        return [self._by_tid[i] for i in self._by_nid.get(nid_of(verbatim), [])]

    #: How much of a proposal's distinctive vocabulary must already appear in a
    #: ticket for that ticket to be SURFACED as a candidate. Swept over 19
    #: thresholds on 150 queries by
    #: `scripts/does_the_register_beat_word_search_2026-10-17.py`; 0.95 was the
    #: most accurate single point and is used here. It governs SURFACING only.
    WORD_OVERLAP_SURFACE = 0.95

    def similar_by_words(self, verbatim: str,
                         threshold: float | None = None,
                         include_notes: bool = False) -> list[Ticket]:
        """Tickets sharing most of this proposal's distinctive vocabulary.

        HIS INSTRUCTION, 2026-10-17: *"The registry search can contain both a
        word and hashed ID search, so it can contain the best of both
        approaches."*

        HE IS RIGHT, AND NOT BY A UNION, WHICH IS WHY THIS LAYER ONLY SURFACES.
        Measured on 150 queries over 106 known and 44 genuinely new items:

          * the hashed tiers        recall 95.2830%, specificity 95.4545%
          * distinctive-word overlap recall 98.1132%, specificity 86.3636%
          * UNION, either says known recall 98.1132%, specificity 81.8182%
          * INTERSECTION, both must  recall 95.2830%, specificity 100.0000%

        A UNION IS WORSE ON SPECIFICITY THAN EITHER METHOD ALONE, and that is
        arithmetic rather than an accident: saying "known" whenever either
        method does cannot be more specific than the less specific of the two.
        So the word layer is NOT allowed to decide. It surfaces candidates --
        98.1132% of known items are surfaced, Wilson [93.3801%, 99.4810%] --
        and `propose` still decides by the hashed tiers, holding specificity at
        95.4545%.

        THE ASYMMETRY SETTLES THE DESIGN. A wrong merge BURIES a finding under a
        closed ticket; a missed match merely creates a duplicate ticket that can
        be merged later. The costs are not comparable, so the stricter rule
        wins, which is also what his own duplicate test requires: the same
        issue AND the same proposed fix AND, since 2026-10-17, the same hash.

        Returns candidates ranked by overlap, most similar first.
        """
        share = self.WORD_OVERLAP_SURFACE if threshold is None else threshold
        wanted = set(_norm_tokens(verbatim))
        if not wanted:
            return []
        if include_notes:
            #: OPT-IN, AND OFF BY DEFAULT ON PURPOSE. The measured operating
            #: characteristic above -- 98.1132% recall at 86.3636%
            #: specificity -- was derived over ticket TEXT, so folding notes
            #: into the default would invalidate it and every figure quoted
            #: from it. The reason the option exists is that an absorbed
            #: proposal's words are kept as a note, and a record nobody can
            #: search for is barely better than a discarded one.
            #:
            #: It routes through the scan rather than the index because the
            #: postings index is built over text only. Adding a second index
            #: for an opt-in path would be a second thing to keep in step for
            #: no measured gain.
            return self._similar_by_words_scan(wanted, share, notes=True)
        if share <= 0:
            # AT A THRESHOLD OF 0 EVERY TICKET QUALIFIES, including those
            # sharing no token at all, and such a ticket appears in NO postings
            # list. The superset argument below fails there, so the scan is
            # used. Measured rather than assumed: the index and the scan are
            # compared on every call in the guard, and a 0 threshold is one of
            # the cases it compares.
            return self._similar_by_words_scan(wanted, share)
        return self._similar_by_words_indexed(wanted, share)

    def _similar_by_words_scan(self, wanted: set, share: float,
                               notes: bool = False) -> list[Ticket]:
        """THE REFERENCE IMPLEMENTATION. Linear, obvious, and kept.

        It is not dead code: it is what the indexed path is CHECKED AGAINST,
        by a guard that calls both and compares their ordered output. The
        project's own rule is that a test asserting on the source text of two
        forms proves only that each describes itself consistently -- so both
        forms stay live and the guard executes them.
        """
        scored: list[tuple[float, Ticket]] = []
        for ticket in self._by_tid.values():
            text = ticket.verbatim or ticket.title or ""
            if notes and ticket.notes:
                text = text + " " + " ".join(ticket.notes)
            have = set(_norm_tokens(text))
            if not have:
                continue
            overlap = len(wanted & have) / len(wanted)
            if overlap >= share:
                scored.append((overlap, ticket))
        scored.sort(key=lambda pair: (-pair[0], pair[1].tid))
        return [ticket for _, ticket in scored]

    def _build_word_index(self) -> tuple[dict, dict]:
        """token -> set of tids, plus each ticket's token count.

        Built lazily and thrown away on any mutation. Measured on the live
        902-ticket store: 21.58 ms to build, 1,905 distinct tokens.
        """
        postings: dict[str, set] = {}
        sizes: dict[str, int] = {}
        for ticket in self._by_tid.values():
            toks = set(_norm_tokens(ticket.verbatim or ticket.title or ""))
            sizes[ticket.tid] = len(toks)
            for tok in toks:
                postings.setdefault(tok, set()).add(ticket.tid)
        return postings, sizes

    def _similar_by_words_indexed(self, wanted: set, share: float) -> list[Ticket]:
        """The same answer as the scan, without touching every ticket.

        WHY THIS IS EXACT AND NOT AN APPROXIMATION. A ticket scoring
        `shared / len(wanted) >= share` with `share > 0` must share at least 1
        of the query's tokens, so it appears in the postings list of at least 1
        of them. The union of those lists is therefore a SUPERSET of the
        answer, and scoring inside it reproduces the scan's ranking exactly --
        measured at 200 of 200 identical ordered results, Wilson [98.1155%,
        100.0000%], at 203.44x the speed (20.6045 ms to 0.1013 ms on the mean).

        PRODUCED BY scripts/what_would_partitioning_the_register_buy_2026-10-17.py
        AND THE FIRST VERSION WAS FAST AND WRONG: it agreed with the scan on 2
        of 200, because it used `min(len(query), len(ticket))` as the
        denominator, excluded the query's own ticket, and indexed `verbatim`
        without the title fallback. The speed-up was already 200x then. A
        speed-up is not evidence of correctness.

        THE IDEA IS GEMINI WEB'S, from the design brief of 2026-10-17, which
        proposed SQLite FTS5. The mechanism here is a plain dict because the
        store already loads wholly into memory, so FTS5 would add a second copy
        on disk that can drift from the append-only log for no measured gain.
        """
        if self._word_index is None:
            self._word_index = self._build_word_index()
        postings, sizes = self._word_index
        counts: dict[str, int] = {}
        for tok in wanted:
            for tid in postings.get(tok, ()):
                counts[tid] = counts.get(tid, 0) + 1
        scored: list[tuple[float, Ticket]] = []
        for tid, shared in counts.items():
            if not sizes.get(tid):
                continue
            overlap = shared / len(wanted)
            if overlap >= share:
                scored.append((overlap, self._by_tid[tid]))
        scored.sort(key=lambda pair: (-pair[0], pair[1].tid))
        return [ticket for _, ticket in scored]

    def candidates(self, kind: str, verbatim: str, task_ref: str = "",
                   anchor: str = "") -> dict:
        """Everything the register can surface about a proposal, DECIDING nothing.

        The one place a caller should look before raising a ticket, and the
        reason the register is a register rather than a log: it answers "has this
        been raised, fixed, refused or merged before?" across all 3 hashed tiers
        AND the word layer, and leaves the merge decision to `propose` and to his
        duplicate test.
        """
        exact = self.exact(kind, verbatim, task_ref=task_ref, anchor=anchor)
        return {
            "exact": [exact] if exact else [],
            "reworded": self.similar(verbatim),
            # THE SUBJECT EXTRACTOR LIVES IN THE HARVESTER, not here, and this
            # calls it rather than carrying a second copy. `subjects_of` was
            # written into this method first and does not exist -- an invented
            # name that would have raised on the first call, which is why this
            # method is executed by its guard rather than only read.
            "by_subject": [t for s in _subjects_in(verbatim)
                           for t in self.by_subject(s)],
            "by_words": self.similar_by_words(verbatim),
        }

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
        """Work that is actually OPEN. Excludes UNCONFIRMED, which means only
        that something was harvested and its state has not yet been established.

        THE DISTINCTION MATTERS AND WAS FOUND BY MEASUREMENT on 2026-10-17: a
        first harvest created 281 tickets from his annotations and called them
        all OPEN, so the store reported 306 open items when most were long
        handled. A store that overstates open work is as useless as one that
        understates it, and both make it decoration.
        """
        return [t for t in self._by_tid.values() if t.status == "OPEN"]

    def unconfirmed(self) -> list[Ticket]:
        """Harvested, state not yet established. These need triage, not work."""
        return [t for t in self._by_tid.values() if t.status == "UNCONFIRMED"]

    def live(self) -> list[Ticket]:
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
    def propose_from_chat(self, kind: str, title: str, verbatim: str,
                          when: str, **kw) -> tuple["Ticket", str]:
        """Raise a ticket from chat with an anchor DERIVED, never remembered.

        WHY THIS EXISTS RATHER THAN A NOTE TELLING ME TO PASS AN ANCHOR. On
        2026-10-27 I raised 5 questions by hand and all 5 carry neither a
        `task_ref` nor an anchor, so 4 of them were decided by the subject tier
        on a single shared identifier and had to be re-raised with invented
        subjects. The escape hatch `_distinct` provides was designed, documented
        and simply not used. A mechanism that depends on my remembering it is
        the thing this project's record says fails.

        `when` is the clock reading for the message, which is what makes the
        anchor identify WHERE in the record the item came from. The shape
        matches `from_chat`'s exactly -- `chat#<timestamp>#<8 hex of the text>`
        -- so an item raised by hand and the same item harvested later collide
        on purpose rather than duplicating.
        """
        import hashlib as _hl
        digest = _hl.sha256(str(verbatim).encode()).hexdigest()[:8]
        kw.setdefault("anchor", f"chat#{when}#{digest}")
        kw.setdefault("source", "founder-chat")
        return self.propose(kind, title, verbatim, kw.pop("source"), **kw)

    def propose(self, kind: str, title: str, verbatim: str, source: str,
                source_ref: str = "", ruled: str = "", created: str = "",
                task_ref: str = "", subjects: Iterable[str] = (),
                status: str = "OPEN", anchor: str = "") -> tuple[Ticket, str]:
        """Create or return a ticket. Returns (ticket, outcome).

        outcome is one of: created, exists, settled-already, reworded-match,
        subject-settled.
        A caller that receives anything other than `created` MUST NOT treat the
        item as new work. This is the step that stops a rediscovery.
        """
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}, not {kind!r}")
        want = tid_of(kind, verbatim, task_ref, anchor)
        self.record_search(verbatim, [t.tid for t in self.similar(verbatim)])

        def _distinct(hit: "Ticket") -> bool:
            """A caller naming a DIFFERENT explicit identity is a different item.

            AN ANCHOR COUNTS, added 2026-10-17. Without it the alias tiers
            absorbed every annotation into whichever content-matching ticket
            already existed: a harvest of all 318 annotations created only 16
            tickets and reported 302 `reworded-match`, so his 3 separate "Do
            it." rulings stayed collapsed into 1. An anchor is as explicit as a
            task reference and is treated the same way.
            """
            if task_ref and hit.task_ref != task_ref:
                return True
            return bool(anchor) and hit.anchor != anchor
        #: ★ THE ALIAS IS FOLLOWED HERE TOO, AND IT WAS NOT AT FIRST.
        #: `exact()` was given the adoption bridge on 2026-10-29 and `propose`
        #: computes `want` itself rather than calling it, so the bridge did not
        #: reach the one path where a miss MATTERS: a proposal naming an adopted
        #: anchor would have found nothing at this tier and created a second
        #: ticket. FOUND BY TRACING THE CALLERS of `exact()` after the change --
        #: it has exactly 1 production caller, `candidates()`, which decides
        #: nothing. The guard test appeared to cover it and did not: it passed
        #: on the REWORDED tier, because the 2 proposals shared their normalised
        #: text, so it was green for a reason unrelated to the bridge.
        hit = self._by_tid.get(want)
        if hit is None:
            _aliased = self._by_identity.get(want)
            if _aliased:
                hit = self._by_tid.get(_aliased)
        if hit is not None and not _distinct(hit):
            self._note_alias(hit, task_ref, subjects)
            if hit.status in TERMINAL or hit.status == REJECTED:
                return hit, "settled-already"
            return hit, "exists"
        # AN EXPLICIT IDENTIFIER BEATS AN INFERRED SIMILARITY.
        #
        # MEASURED 2026-10-17, and it is the dangerous direction of a matching
        # error. Over-merging hides the open item behind the closed one, which is
        # worse than the rediscovery this store exists to prevent. An integrity
        # check over the seeded store found 3 settled tickets concealing 5 OPEN
        # task entries: a ticket owned by 3.1a hid B14 and C12, one owned by A12
        # hid A19 and C17, and one owned by V8 hid B11.
        #
        # A `task_ref` is a human-assigned identifier for a distinct item. Text
        # and subject similarity are inferences ABOUT items. So when the caller
        # names a task reference that the matched ticket does not own, the match
        # is recorded as a relation and a SEPARATE ticket is created. Two entries
        # about the same mechanism are still 2 entries.
        for sub in subjects:
            # THE SUBJECT TIER NOW RESPECTS `kind`, AS EVERY OTHER TIER IN THIS
            # FUNCTION ALREADY DID -- repair of 2026-10-28, his instruction, and
            # raised as pf:b705bdbab3a9.
            #
            # HIS RULING OF 2026-10-19 IS WHAT MAKES THIS A CORRECTION RATHER
            # THAN A PREFERENCE: a question and a proposed fix are different
            # items whose resolutions travel in OPPOSITE directions -- he answers
            # mine, I answer his -- which is exactly why `tid_of` digests the
            # kind. A settled `pf` therefore has no standing to say that a new
            # `qs` is already settled. The `reworded-match` tier below has always
            # filtered on `t.kind == kind`; this loop was the only one that did
            # not, and the asymmetry was unintended rather than designed.
            #
            # ★ THE FIGURE THAT ORIGINALLY JUSTIFIED THIS IS WITHDRAWN, and the
            # justification is REPLACED rather than merely removed. The free
            # panel of 2026-10-28 showed the cross-kind blocked SHARE -- around
            # 0.74 on the live store, whatever its exact value on the day -- to
            # be 0.740299 HYPOTHETICAL: of the 1,340 (kind, subject) pairs it
            # counts, only 348 are pairs for which a ticket of that kind
            # actually EXISTS. A share computed over pairs that do not exist
            # cannot measure a defect that does. It was a judgement dressed as a
            # measurement and it is not cited here any longer.
            #
            # WHAT JUSTIFIES THE FILTER INSTEAD is an executed 3-variant table
            # over the DOCUMENTED case families, delivered by the fable seat as
            # bench/tests/test_the_kind_filter_three_variants_measured_2026-10-28.py:
            #   A  settled pf vs a NEW qs          LIVE   kind-ignorant FAILS,
            #                                             this form PASSES
            #   B  settled pf vs a GENUINELY NEW
            #      fr                              LIVE   kind-ignorant FAILS,
            #                                             this form PASSES,
            #                                             a qs-only narrowing
            #                                             FAILS
            #   C  settled pf vs the SAME item
            #      reworded as fr                  0 live occurrences
            # This form is the UNIQUE variant correct on both LIVE cases. The
            # only realised cross-kind suppression in 2,879 tickets is `qs`
            # blocked by `pf` -- his exact pair -- measured by the cc2 seat,
            # which also showed a qs-only narrowing recovers an IDENTICAL set on
            # an anchorless replay (4 of 31 each, set difference EMPTY). Parity
            # on recovery is not dominance, and the narrowing LOSES case B, so
            # reverting to it is a removal `additive-standard` refuses.
            #
            # B AND C ARE INSEPARABLE BY KIND ALONE and text-similarity repairs
            # were already tried against this exact problem and refused twice as
            # circular, so the choice is which error to prefer. The live record
            # decides it: B occurred, C has not.
            #
            # IT DOES NOT WEAKEN DEDUPLICATION, and the suite is the evidence:
            # both anti-vacuity guards -- `test_a_settled_subject_blocks_
            # regardless_of_wording` and `test_dedup_still_works_when_no_task_
            # reference_is_named` -- are SAME-KIND cases and are untouched. The
            # one guard whose expectation changes is the one whose own docstring
            # calls the behaviour "THE DEFECT": a genuinely new `fr` absorbed by
            # a settled `pf` over the single shared identifier `area_of`.
            #
            # 2 TUNED REPAIRS WERE TRIED BEFORE AND BOTH WERE REFUSED, recorded
            # below in this same comment block. This one adds no constant at all.
            blocked = [b for b in self.settled_on_subject(sub) if b.kind == kind]
            if blocked:
                if _distinct(blocked[0]):
                    break                 # related, not the same item
                #: THE SUBJECT TIER STILL DECIDES, AND THE PROPOSAL'S TEXT
                #: IS NO LONGER LOST. Both halves were established on
                #: 2026-10-17 and the second was found by the register
                #: refusing my own work: a genuinely new feature request --
                #: namespace paths, from the design brief he attached -- was
                #: NOT CREATED, because it shares exactly 1 identifier,
                #: `area_of`, with the ticket for the new command-line entry
                #: point, closed minutes earlier. The text went nowhere.
                #:
                #: THE FIRST REPAIR TRIED WAS WRONG AND THE SUITE PROVED IT.
                #: Requiring the word layer to corroborate a subject match is
                #: CIRCULAR: the subject tier exists precisely to catch
                #: rewordings the word layer misses, so demanding its agreement
                #: destroys the tier's whole value. Measured: the store fell
                #: from 4 of 4 to 1 of 4 on the known rediscovery cases.
                #:
                #: A PARTIAL-OVERLAP THRESHOLD WAS MEASURED AND REFUSED AS
                #: OVERFITTING. The 3 true rediscoveries score 0.1429 to
                #: 0.2500 on shared vocabulary and the 2 genuinely-new items
                #: score 0.0000 to 0.1111, so any threshold in (0.1111,
                #: 0.1429) separates them -- a margin of 0.0318 fitted to 5
                #: data points. That is a tuned constant pretending to be a
                #: finding, and this project has retired one of those before.
                #:
                #: SO THE DECISION IS UNCHANGED and the loss is fixed instead.
                #: `_distinct` already provides the designed escape hatch: a
                #: caller naming a `task_ref` or an `anchor` that the matched
                #: ticket does not own gets a SEPARATE ticket. My call simply
                #: omitted one. What was not acceptable is that omitting it
                #: discarded his words, so the proposal's own text is now
                #: recorded on the settled ticket, where a word search will
                #: find it and a reader can split the two by hand.
                #:
                #: 291 of 907 tickets, 32.0838% Wilson [29.1269%, 35.1918%],
                #: carry neither a task_ref nor an anchor, so this path is
                #: reached often rather than rarely, and the historical
                #: backfill will reach it for every item it raises.
                #: Measured by
                #: scripts/can_a_shared_mechanism_hide_a_new_item_2026-10-17.py
                self._note_proposal_text(blocked[0], title, verbatim, sub)
                self._note_alias(blocked[0], task_ref, subjects)
                return blocked[0], "subject-settled"
        near = [t for t in self.similar(verbatim)
                if t.kind == kind and not _distinct(t)]
        if near:
            settled = [t for t in near if t.status in TERMINAL or t.status == REJECTED]
            chosen = settled[0] if settled else near[0]
            self._note_alias(chosen, task_ref, subjects)
            return chosen, "reworded-match"
        if status not in LIVE:
            raise ValueError(
                f"a new ticket must start in a LIVE status, not {status!r}. A "
                "terminal status is tool-only and is reached through close(), "
                "reject() or merge(), never by creation.")
        t = Ticket(tid=want, nid=nid_of(verbatim), kind=kind, status=status,
                   title=norm_title(title),
                   verbatim=" ".join(str(verbatim).split()),
                   source=source, source_ref=source_ref, ruled=ruled,
                   created=created, task_ref=task_ref, anchor=anchor,
                   subjects=sorted(set(subjects)))
        self._append(t)
        return t, "created"

    def _note_proposal_text(self, hit: Ticket, title: str, verbatim: str,
                            subject: str) -> None:
        """Keep a proposal's own words when a subject match absorbs it.

        WITHOUT THIS THE TEXT IS GONE. `propose` returns the settled ticket and
        the caller's wording is discarded, so nothing can later ask what was
        proposed or notice that it was a different item. On 2026-10-17 that
        swallowed a genuinely new feature request whole.

        POINT, NEVER PRUNE. The note is appended to the settled ticket rather
        than used to create a second one, because creating one would change the
        tier's decision -- which the known-rediscovery cases show is right 4
        times out of 4 when it fires on a reworded repeat. Recording the text
        changes nothing about the decision and makes it reviewable.
        """
        folded = " ".join(str(verbatim).split())
        note = (f"absorbed over subject {subject!r}: proposed as "
                f"{norm_title(title)!r} -- {folded}")
        if note in hit.notes:
            return
        nt = Ticket(**{**asdict(hit), "notes": list(hit.notes) + [note]})
        self._append(nt)

    def _note_alias(self, hit: Ticket, task_ref: str,
                    subjects: Iterable[str] = ()) -> None:
        """Record a task reference that resolved to an EXISTING ticket.

        WITHOUT THIS THE LINK IS LOST, measured 2026-10-17: task B18 matched an
        existing ticket, `propose` returned that ticket, and B18's own identifier
        went nowhere -- so a search for "the ticket for B18" found nothing while
        the work was in fact tracked under another id. A store that silently
        drops the caller's reference cannot be searched by that reference, which
        defeats the point of the reference.
        """
        note = f"also tracked as {task_ref}" if task_ref else ""
        new_subs = [s for s in subjects if s and s not in hit.subjects]
        if not note and not new_subs:
            return
        if note and note in hit.notes:
            note = ""
        if not note and not new_subs:
            return
        nt = Ticket(**{**asdict(hit),
                       "notes": list(hit.notes) + ([note] if note else []),
                       "subjects": sorted(set(list(hit.subjects) + new_subs))})
        self._append(nt)

    def by_task_ref(self, task_ref: str) -> list[Ticket]:
        """Tickets whose own reference matches, OR which record it as an alias."""
        needle = f"also tracked as {task_ref}"
        return [t for t in self._by_tid.values()
                if t.task_ref == task_ref or needle in t.notes]

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

    def restate(self, tid: str, verbatim: str, verification: str) -> Ticket:
        """Track an entry's CURRENT wording without moving its identity.

        WHY THIS IS SAFE NOW AND WAS NOT BEFORE. While identity digested the
        text, any restatement minted a new ticket -- which is how 5 references
        came to hold 2 tickets each. Identity is now the reference, so the text
        can be brought up to date and the hashed identifier a reader has cited
        still resolves to the same record. The guard below asserts that rather
        than assuming it.

        WHY IT IS WORTH DOING. The reworded-match tier is what catches the same
        issue arriving in different words, and it reads `nid`, which is derived
        from the stored text. A stale record therefore weakens exactly the tier
        that stops a rediscovery. 22 of 141 entries held a stub of the form
        `task A1: A1. DONE ...` because a status stamp defeated the first-
        sentence rule, and a stub matches nothing.

        WHAT IT REFUSES. The status is carried across untouched, so this is not
        a route to reopening settled work: a CLOSED ticket stays closed, and
        the resolution and verification that closed it are preserved.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if not str(verification).strip():
            raise ValueError("a restatement must name what authorised it")
        clean = " ".join(str(verbatim).split())
        if not clean:
            raise ValueError("refusing to blank a ticket's text")
        if clean == t.verbatim:
            return t
        # RECOMPUTE, DO NOT COMPARE A COPIED FIELD. Found 2026-10-17 by
        # mutation: the first form asserted `nt.tid != t.tid`, and `tid` is a
        # STORED field that `asdict` copies across, so the comparison could
        # never fail whatever `tid_of` did. Deleting the assertion entirely
        # left all 19 guards green, which is how a vacuous gate announces
        # itself. Digesting the NEW text and comparing that to the stored
        # identity is the real question: it fires the moment identity starts
        # depending on the text again, which is the regression that minted 5
        # duplicate tickets.
        if tid_of(t.kind, clean, t.task_ref) != t.tid:
            raise AssertionError(
                "restating this text would move the hashed identity, so identity "
                "is digesting the text again. Refusing to write it.")
        nt = Ticket(**{**asdict(t), "verbatim": clean, "nid": nid_of(clean)})
        self._append(nt)
        return nt

    def migrate_identity(self, old_tid: str, new_tid: str,
                         verification: str) -> tuple[Ticket, Ticket]:
        """Move a ticket to a new identity, preserving status and substance.

        WHY A NAMED PATH AND NOT A REWRITE. The identity rule changed on
        2026-10-17: where an entry carries a reference, the reference alone is
        the identity, because digesting the text as well moved the identity
        every time the entry was reworded. 56 of 141 references were left at
        their old text-derived identity, so a lookup by reference found
        nothing and the register under-reported.

        Rewriting those records in place would be the easy fix and the wrong
        one: an identifier already cited in a note or a commit message would
        silently stop resolving. So the OLD record is kept and marked MERGED,
        naming its successor, and a NEW record is written at the new identity
        carrying the status, resolution and verification across unchanged. A
        reader following either identifier arrives at the same place.

        The status is carried, not re-derived. A CLOSED ticket stays closed
        through the migration -- 113 of the 146 task-list tickets were settled,
        and a migration that re-opened them would resurrect every one, which is
        the precise failure this register exists to prevent.
        """
        old = self._by_tid.get(old_tid)
        if old is None:
            raise KeyError(f"no ticket {old_tid}")
        if not str(verification).strip():
            raise ValueError("an identity migration must name what authorised it")
        if new_tid == old_tid:
            raise ValueError("migrate_identity called with identical identities")
        if new_tid in self._by_tid:
            raise ValueError(
                f"{new_tid} already exists; merge into it rather than migrating")
        # NO GUARD HERE, DELIBERATELY. The status and the text are carried by
        # the `asdict` copy, so a guard comparing them to the original could
        # never fail -- the vacuous shape that mutation testing exposed in
        # `restate` on 2026-10-17. The property is held BY CONSTRUCTION and is
        # verified behaviourally by
        # `test_a_migration_carries_a_closure_across`, which closes a ticket,
        # migrates it, and fails if the closure is lost. An unreachable gate
        # would be an addition nothing reaches, which the additive standard
        # forbids in the same breath as a removal.
        moved = Ticket(**{**asdict(old), "tid": new_tid})
        self._append(moved)
        retired = Ticket(**{**asdict(old), "status": "MERGED",
                            "resolution": f"identity migrated to {new_tid}",
                            "rid": rid_of(old_tid, f"identity migrated to {new_tid}"),
                            "verification": " ".join(str(verification).split())})
        self._append(retired)
        return moved, retired

    def adopt_identity(self, tid: str, verification: str, *,
                       task_ref: str = "", anchor: str = "") -> Ticket:
        """Give an identityless ticket the identity it should have carried.

        WHY THIS EXISTS, AND WHAT IT CORRECTS IN MY OWN REPORT TO HIM. Entry B49
        told the founder that the count of tickets carrying neither a `task_ref`
        nor an `anchor` *"cannot be brought back down"*, and the measurement
        offered for that was `migrate_identity`: raising a bare ticket takes the
        count from 320 to 321, migrating it to 322, because the migration leaves
        the old record behind as a MERGED marker and that marker is itself
        without an identity. **That measurement is sound and the conclusion drawn
        from it was not.** It establishes that MIGRATION cannot walk the count
        back; it says nothing about whether any operation can, and no operation
        that filled in the missing field existed to be measured. His ruling of
        2026-10-29 -- *"Do the re-baseline and implement your fix as you
        suggest."* -- was given on the premise of irreversibility, so building
        this first is what tests that premise rather than ratcheting a guard
        looser on the strength of it.

        WHY IT DOES NOT RE-KEY THE RECORD, which is the whole difference from
        `migrate_identity`. Re-keying is what forces a marker to be left behind,
        because an identifier already cited in a note or a commit message must
        keep resolving. So the record stays at the identity it was created
        under, the missing field is filled in, and `_by_identity` bridges the
        digest the new fields imply back to that stored key. The count of
        identityless tickets therefore FALLS by exactly 1 per adoption, where a
        migration raised it by 1.

        WHAT IT REFUSES, so it cannot be used as a way round the identity rule:
        a ticket that already carries an identity (that is a migration, not an
        adoption); a call naming neither field; a call with no verification; and
        any adoption whose implied digest is already taken by a different
        ticket, which would make 2 tickets answer to 1 identity -- the exact
        collapse that destroyed a ticket of mine on 2026-10-29.

        THE STATUS IS NOT TOUCHED. An adoption is a provenance repair, and a
        terminal ticket is the common case for one: the 3 tickets this was built
        for are all DUPLICATE, having been superseded by correctly-identified
        re-raises. Repairing the provenance of a settled record is precisely
        what an append-only log is for.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if not str(verification).strip():
            raise ValueError("an identity adoption must name what authorised it")
        task_ref = str(task_ref).strip()
        anchor = str(anchor).strip()
        if not (task_ref or anchor):
            raise ValueError(
                "adopt_identity must supply a task_ref or an anchor; "
                "an adoption that supplies neither changes nothing")
        if t.task_ref or t.anchor:
            raise ValueError(
                f"{tid} already carries an identity "
                f"(task_ref={t.task_ref!r}, anchor={t.anchor!r}); "
                f"use migrate_identity to move it")
        implied = tid_of(t.kind, t.verbatim, task_ref, anchor)
        clash = self._by_tid.get(implied)
        if clash is not None and clash.tid != tid:
            raise ValueError(
                f"the identity implied by that reference is {implied}, which "
                f"already holds {clash.kind}:{clash.tid}; merge into it rather "
                f"than adopting")
        held = self._by_identity.get(implied)
        if held is not None and held != tid:
            raise ValueError(
                f"the identity implied by that reference is already an alias of "
                f"{held}; 2 tickets may not answer to 1 identity")
        #: ★ THE GUARD ITS OWN P-PASS FOUND MISSING, 2026-10-29. The 3 checks
        #: above all reason about the IMPLIED DIGEST, and a digest is blind to an
        #: anchor already in use on a ticket whose identity came from a
        #: `task_ref` instead -- because `tid_of` takes the reference in
        #: preference and never reads the anchor at all. `pf:b0d8ca44a450` was
        #: therefore adopted onto an anchor `pf:2835f264ae18` already carried,
        #: and only the fact that the 2 are records of ONE item kept the result
        #: truthful. An anchor is meant to be a unique stable identity, so a
        #: second holder is refused outright rather than left to luck.
        #: ONLY THE ANCHOR IS CHECKED HERE, and the first draft also checked the
        #: `task_ref`. That branch was UNREACHABLE and its own test proved it: a
        #: same-kind, same-reference adoption always collides on the implied
        #: digest first, because `tid_of` digests the reference alone, so either
        #: the `clash` check or the alias check fires before this loop is
        #: reached. An addition nothing can reach is what the additive standard
        #: forbids in the same breath as a removal, so it was taken out rather
        #: than left in as apparent thoroughness.
        if anchor:
            for other in self._by_tid.values():
                if other.tid != tid and other.anchor == anchor:
                    raise ValueError(
                        f"{other.kind}:{other.tid} already carries anchor "
                        f"{anchor!r}; an anchor identifies 1 ticket")
        note = (f"identity adopted {task_ref or anchor} -> implies {implied}, "
                f"stored key unchanged at {tid}; authorised by: "
                f"{' '.join(str(verification).split())}")
        adopted = Ticket(**{**asdict(t), "task_ref": task_ref or t.task_ref,
                            "anchor": anchor or t.anchor,
                            "notes": list(t.notes) + [note]})
        self._append(adopted)
        return adopted

    def retitle(self, tid: str, title: str) -> Ticket:
        """Correct a ticket's SEARCH LABEL. Substance and identity are untouched.

        WHY THIS EXISTS, AND WHY IT IS NOT A WAY ROUND THE TERMINAL STATUSES.
        The founder's ruling of 2026-10-17 requires this registry to be
        searched before any work is proposed, so a title naming the wrong
        entry is a defect at the point of use: measured 2026-10-17 by
        `scripts/do_the_ticket_titles_name_their_own_entry_2026-10-17.py`, 9
        of 141 titles named a DIFFERENT entry -- 6.3830%, Wilson [3.3941%,
        11.6854%] -- because an addendum recording entry N as built sits
        above entry N+1's heading in a shared block.

        `propose` deliberately returns `exists` without refreshing anything,
        because silently rewriting a stored record is how a settled issue
        comes back wearing new words. So correcting a label needs its own
        named path, and this one can only ever move the label: the new
        record is built field-by-field from the old one with `title` alone
        replaced, so `verbatim`, `status`, `resolution`, `verification` and
        the hashed `tid` itself are carried across unchanged BY CONSTRUCTION
        rather than by promise. The identifier a reader has already cited
        therefore still resolves after a retitle, which is the whole point.

        A CLOSED ticket may be retitled, and that is deliberate: a settled
        record whose label points at the wrong entry is the case most likely
        to cause a rediscovery, since the reader concludes the real issue was
        never filed.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        clean = norm_title(title)
        if not clean:
            raise ValueError("a retitle must supply a title; refusing to blank one")
        if clean == t.title:
            return t
        # RECOMPUTED for the same reason as in `restate`: comparing the copied
        # field could never fail. This asks whether the LABEL has become part
        # of the identity, which is the only way a retitle could move one.
        if tid_of(t.kind, t.verbatim, t.task_ref) != t.tid:
            raise AssertionError(
                "this ticket's stored identity does not match its own content, so "
                "a retitle cannot be shown to be safe. Refusing to write it.")
        nt = Ticket(**{**asdict(t), "title": clean})
        self._append(nt)
        return nt

    # ─────────────── deferral and true blockers, his ruling 2026-10-24 ──────

    def workable(self) -> list["Ticket"]:
        """Open tickets that can be worked NOW: not deferred, not a blocker.

        This is the predicate the Stop gate turns on. `wr` is excluded from
        PRODDING elsewhere but is NOT excluded here, because deferred work is
        marked by the `deferred` field rather than inferred from its kind.
        """
        return [t for t in self.open_tickets() if not t.deferred and not t.blocker]

    def deferred_tickets(self) -> list["Ticket"]:
        """Live work set aside to the END of the list, to be PRESENTED there."""
        return [t for t in self.open_tickets() if t.deferred and not t.blocker]

    def blockers(self) -> list["Ticket"]:
        """Tickets declared to stop all other work. By his definition, rare."""
        return [t for t in self.open_tickets() if t.blocker]

    def defer(self, tid: str, reason: str, when: str) -> Ticket:
        """Set a ticket aside to the end of the list. It stays LIVE.

        HIS RULING, 2026-10-24: *"If it doesn't block work from continuing and can
        be addressed without detriment at the end of a task list, then record it
        and present it clearly once all other tasks that can be completed are
        completed."*

        Deferring does NOT permit a stop by itself. The gate permits a stop only
        when nothing workable remains, and then it PRESENTS everything deferred.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if t.status not in LIVE:
            raise ValueError(
                f"{tid} is {t.status}, which is not live work; there is nothing "
                f"to defer")
        reason = " ".join(str(reason).split())
        if len(reason) < 12:
            raise ValueError(
                "a deferral must say WHY it can wait, in a sentence a reader can "
                "check. Deferral with no stated reason is how an item leaves the "
                "list without being decided.")
        # ★ THE CALLER SUPPLIES THE TIMESTAMP AND THIS MODULE NEVER READS A
        # CLOCK. `created` is passed in for the same reason: the project's rule is
        # that a timestamp is captured from `date` and never typed or inferred, so
        # a store that stamped itself would be the one place that broke it.
        if not str(when).strip():
            raise ValueError(
                "defer() needs the timestamp from `date -Iseconds`; this module "
                "never reads a clock, so it cannot supply one")
        nt = Ticket(**{**asdict(t),
                       "deferred": str(when).strip(),
                       "deferred_reason": reason})
        self._append(nt)
        return nt

    def undefer(self, tid: str, reason: str, when: str) -> Ticket:
        """Clear a deferral, naming WHAT DISCHARGED IT. The symmetric operation.

        WHY IT WAS OWED. `defer` existed and nothing could reverse it, so the
        field was one-way: an item deferred because it waited on his decision
        stayed deferred after he decided. Found 2026-10-29 while building his
        ruling that the register is the single source for deferral -- 3 of the
        register's 7 deferrals were discharged by rulings he gave that same day,
        and there was no operation that could say so. A single source of truth
        that cannot be corrected is worse than 2 that can, because every
        consumer now reads the stale answer with no second opinion to contradict
        it.

        THE REASON IS REQUIRED, exactly as it is for `defer`, and for the same
        stated purpose: an undeferral with no reason is how an item re-enters the
        list without anyone having decided that it should.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        reason = " ".join(str(reason).split())
        if len(reason) < 12:
            raise ValueError(
                "an undeferral must say WHAT DISCHARGED the deferral, in a "
                "sentence a reader can check. Clearing it silently is how an "
                "item re-enters the list without anyone deciding it should.")
        if not str(when).strip():
            raise ValueError(
                "undefer() needs the timestamp from `date -Iseconds`; this "
                "module never reads a clock, so it cannot supply one")
        if not t.deferred:
            raise ValueError(f"{tid} is not deferred; there is nothing to clear")
        note = (f"undeferred {str(when).strip()} (was deferred {t.deferred}): "
                f"{reason}")
        nt = Ticket(**{**asdict(t), "deferred": "", "deferred_reason": "",
                       "notes": list(t.notes) + [note]})
        self._append(nt)
        return nt

    def declare_blocker(self, tid: str, reason: str) -> Ticket:
        """Declare that nothing else can proceed until this is cleared.

        ★ HIS DEFINITION IS ENFORCED HERE AND NOT MERELY QUOTED. His words:
        *"If a blocker is a true blocker, that would mean that no other work could
        proceed until that blocker was cleared. Is that not what a 'blocker' is?"*

        So this REFUSES while any workable ticket remains. A ticket that leaves
        other work possible is not a blocker, and calling it one would let a
        single awkward item stop a list with 30 items still open on it -- which is
        precisely the stop his ruling exists to prevent.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        reason = " ".join(str(reason).split())
        if len(reason) < 12:
            raise ValueError("a blocker must state what it blocks and why")
        others = [x for x in self.workable() if x.tid != tid]
        if others:
            raise ValueError(
                f"{tid} is not a blocker by his definition: {len(others)} other "
                f"ticket(s) can still be worked, the next being {others[0].tid} "
                f"({others[0].kind}) {others[0].title[:70]!r}. A blocker is an "
                f"item that stops ALL other work. Defer this instead, or work the "
                f"others first.")
        nt = Ticket(**{**asdict(t), "blocker": reason})
        self._append(nt)
        return nt

    # ────── his duplicate / supersession taxonomy, ruled 2026-10-16 and -24 ──

    def invalidate(self, tid: str, reason: str, verification: str) -> Ticket:
        """INVALID: this was never a defect. Intended behaviour, or a misread spec.

        THE GAP THIS FILLS, found by comparing against Bugzilla on 2026-10-24.
        Mozilla's INVALID is "intended behaviour -- not a bug". Nothing here said
        that, and REFUTED is not it: REFUTED means "a falsifier was executed and
        did not fire", which conflates THE CLAIM WAS WRONG with THE INSTRUMENT WAS
        WRONG. A correct finding with a bad falsifier and a non-finding with a
        sound falsifier both landed in REFUTED.

        IT IS TERMINAL, SO IT NEEDS A VERIFICATION, exactly as `close()` does: the
        terminal set is tool-only in this vocabulary and a model may not assert a
        terminal status by saying so.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if not str(verification).strip():
            raise ValueError(
                "INVALID is terminal, so it needs the verification that "
                "establishes there was no defect -- the spec section, the "
                "documented behaviour, or the execution that shows it is "
                "intended. An assertion is refused.")
        nt = Ticket(**{**asdict(t), "status": "INVALID",
                       "resolution": " ".join(str(reason).split()),
                       "rid": rid_of(tid, reason),
                       "verification": " ".join(str(verification).split())})
        self._append(nt)
        return nt

    def mark_duplicate(self, tid: str, of_tid: str, repair_identity: float,
                       verification: str) -> Ticket:
        """DUPLICATE: his definition, with condition (b) ENFORCED.

        HIS WORDS, 2026-10-16: *"a duplicate can only be called a duplicate, if a)
        it finds the same fault and b) if the proposed repair is in fact
        identical. Isn't this how dupes normally work in the world of software
        engineering?"*

        ★ CONDITION (b) IS WHY THIS EXISTS. The harness had deprecated DUPLICATE
        and folded it into MERGED, whose criterion is `adjudicate_by_repair`:
        apply A's fix, re-run both falsifiers, and if B's now passes call it the
        SAME defect. That tests (a) ONLY. Measured 2026-10-24 over the archive: of
        84 merged pairs whose repairs are both comparable, 63 -- 75.0000%, Wilson
        [64.7857%, 83.0277%] -- have DIFFERENT repairs, so three quarters of what
        the harness called one item fail his condition (b).

        So this REFUSES below the identity floor. Same fault with different
        repairs is not a duplicate; it is a supersession question, and
        `deprecate()` is where that goes.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if self._by_tid.get(of_tid) is None:
            raise KeyError(f"no ticket {of_tid} to be a duplicate OF")
        if of_tid == tid:
            raise ValueError("a ticket cannot be a duplicate of itself")
        try:
            ident = float(repair_identity)
        except (TypeError, ValueError):
            raise ValueError("repair_identity must be a measured number in [0,1]")
        if not 0.0 <= ident <= 1.0:
            raise ValueError(f"repair_identity {ident} is outside [0,1]")
        if ident < DUPLICATE_REPAIR_FLOOR:
            raise ValueError(
                f"repairs are only {ident:.4f} identical, below the floor of "
                f"{DUPLICATE_REPAIR_FLOOR}. By his definition of 2026-10-16 a "
                f"duplicate needs the SAME FAULT AND AN IDENTICAL REPAIR; this "
                f"pair fails condition (b). It is a supersession question -- "
                f"adjudicate which fix is better and use deprecate().")
        if not str(verification).strip():
            raise ValueError("DUPLICATE is terminal and needs its verification")
        nt = Ticket(**{**asdict(t), "status": "DUPLICATE",
                       "duplicate_of": of_tid,
                       "repair_identity": f"{ident:.4f}",
                       "resolution": f"duplicate of {of_tid}",
                       "rid": rid_of(tid, of_tid),
                       "verification": " ".join(str(verification).split())})
        self._append(nt)
        return nt

    def deprecate(self, tid: str, superseded_by: str, evidence: str) -> Ticket:
        """DEPRECATED: this fix was replaced by a demonstrably better one.

        HIS DESIGN, 2026-10-24: *"where two fixes are aimed at the same
        target/issue, and one fix is clearly better than the other, and does its
        job more efficiently, more effectively and/or at lower resource cost
        (memory/cpu/gpu etc.) and meets our additive, simplest sufficient fix and
        composability standards (where a composition of fixes is demonstrably
        better), then that better fix can replace an existing fix and the existing
        fix can be marked as 'deprecated'."*

        ★ "DEMONSTRABLY" IS THE OPERATIVE WORD, so the evidence is required and a
        judgement is refused. The additive standard says it in the same terms: a
        judgement that something is better is not evidence that it is.

        THE WORD WAS ALREADY IN USE AS A META-COMMENT. `bench/reference_runner_v3`
        carried `"DUPLICATE": {"meaning": "DEPRECATED -- collapse into MERGED"}`,
        so DEPRECATED described a retired STATUS while he had defined it as a
        status for a retired FIX. He spotted the double duty on 2026-10-24.
        """
        t = self._by_tid.get(tid)
        if t is None:
            raise KeyError(f"no ticket {tid}")
        if self._by_tid.get(superseded_by) is None:
            raise KeyError(f"no ticket {superseded_by} to supersede it")
        if superseded_by == tid:
            raise ValueError("a fix cannot supersede itself")
        ev = " ".join(str(evidence).split())
        if len(ev) < 30:
            raise ValueError(
                "deprecating a fix needs the MEASUREMENT showing the replacement "
                "dominates on a named property -- his standard is 'demonstrably "
                "does the job better', and the additive standard refuses a "
                "judgement in place of evidence. Name what was measured, on what, "
                "and which way it came out.")
        nt = Ticket(**{**asdict(t), "status": "DEPRECATED",
                       "superseded_by": superseded_by,
                       "supersession_evidence": ev,
                       "resolution": f"superseded by {superseded_by}",
                       "rid": rid_of(tid, superseded_by),
                       "verification": ev})
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
        """DUPLICATE -> MERGED. His 3 elements: same fault, same repair, same hash.

        HIS DEFINITION, restated and EXTENDED on 2026-10-17: *"if it\'s the same
        issue and the fix/proposed feature etc is the same (and now also if its
        hash value is the same), then it can/should be marked as a dupe. However
        if a new fix/feature request is genuinely new, it should be raised as a
        new ticket."* The first 2 elements are his of 2026-10-16: *"a duplicate
        can only be called a duplicate, if a) it finds the same fault and b) if
        the proposed repair is in fact identical."*

        THE HASH IS A NECESSARY CONDITION, NOT A SUFFICIENT ONE, and the
        distinction is load-bearing. Two proposals sharing a digest are the same
        TEXT, which is strong evidence of the same fault; they are not thereby
        the same REPAIR, because a digest is taken over the finding rather than
        over the fix. So a matching hash admits a merge to consideration and the
        2 substantive elements still have to hold, which is why `verification`
        is mandatory here and names them.

        WHY THE WORD LAYER CANNOT MERGE ANYTHING. `similar_by_words` surfaces
        candidates at 98.1132% recall, and a UNION rule admitting its matches
        would drop specificity to 81.8182% -- worse than either tier alone.
        Measured by `scripts/does_the_register_beat_word_search_2026-10-17.py`.
        A wrong merge BURIES a finding under a closed ticket; a missed match
        only leaves a duplicate to merge later. The costs are not comparable.
        """
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

    def settled_with_open_aliases(self, open_idents) -> list[tuple[Ticket, list[str]]]:
        """Settled tickets whose ALIASED task references are still open.

        WHY THIS EXISTS. Dedup is the store's whole purpose, and over-merging is
        its matching failure in the dangerous direction: collapsing 2 genuinely
        distinct items hides the open one behind the closed one, which is worse
        than the rediscovery it was built to prevent.

        OBSERVED 2026-10-17, benignly. Tasks 7.1, V2 and B10 all concern the
        note-lint stamp rule, so they collapsed into 1 ticket; the ticket closed
        when 7.1 seeded from a DONE marker, while B10 was still open. It turned
        out to be the same work and B10 completed the same morning, so nothing
        was lost -- but nothing was CHECKING, and that is the defect.

        Pass the identifiers the task list currently records as open.

        A MERGED RECORD IS A REDIRECT, NOT A CONCEALMENT, and excluding it was
        added 2026-10-17 after this check reported 4 false positives. MERGED
        means "see that other ticket", and the resolution names which one, so a
        reader following it arrives at the live record. Counting a redirect as
        concealment made the check fire on every identity migrated that day --
        and a check that cries wolf is one an operator learns to wave through,
        which is a defect this project has already recorded once in the
        containment alarm.

        What still counts is a record that ENDS the trail: CLOSED, CONFIRMED,
        REFUTED or REJECTED while an aliased reference is open.
        """
        want = set(open_idents)
        #: ★ A REFERENCE WITH A LIVE SIBLING IS NOT CONCEALED, added 2026-10-29,
        #: and it is the same reasoning as the MERGED exclusion above: what
        #: counts is a record that ENDS THE TRAIL. A settled ticket beside a LIVE
        #: ticket on the same reference ends nothing -- a reader searching that
        #: reference still finds open work.
        #:
        #: WHY IT APPEARED NOW. His ruling of 2026-10-19 made `qs` its own kind,
        #: and `tid_of` digests the kind, so a QUESTION about an entry and a
        #: PROPOSED FIX for it take 2 distinct identities by design. Answering
        #: the question settles the question and not the entry. On 2026-10-29
        #: `qs:cea0bd553f52` was closed because he had ruled which term the claim
        #: channel enters, while entry C1's implement half is deliberately
        #: unfinished -- the channel's weight is 0 pending a commissioning run --
        #: and this check reported the answered question as concealing C1.
        #: Measured at that moment: C1 carried 4 tickets, 1 of them OPEN, so
        #: nothing was concealed.
        #:
        #: THIS IS THE SECOND CHECK TONIGHT WITH THE SAME 1-TICKET-PER-REFERENCE
        #: ASSUMPTION. `test_the_closed_count_equals_the_task_lists_own` had it
        #: too and was corrected to count ENTRIES rather than tickets.
        live_refs = set()
        for t in self.all():
            if t.status in TERMINAL or t.status == REJECTED:
                continue
            if t.task_ref:
                live_refs.add(t.task_ref)
            for n in t.notes:
                if n.startswith("also tracked as "):
                    live_refs.add(n.split("also tracked as ", 1)[1])
        out = []
        for t in self.settled():
            if t.status in ("MERGED", "DUPLICATE"):
                continue
            refs = ([t.task_ref] if t.task_ref else []) + [
                n.split("also tracked as ", 1)[1]
                for n in t.notes if n.startswith("also tracked as ")]
            still_open = sorted({r for r in refs
                                 if r in want and r not in live_refs})
            if still_open:
                out.append((t, still_open))
        return out

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
