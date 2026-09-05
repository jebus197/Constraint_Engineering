"""Duplicate matching by EXECUTION, not by text (item D8, founder-approved 2026-09-05).

WHAT THIS IS
------------
Two findings are the same defect if the same executable settles both. Not if
their prose reads alike -- if a repair applied to the target flips both
falsifiers, or flips one and leaves the other firing. The falsifier is the
instrument; running it is the evidence; the text is a proxy for the evidence.

This is `execute-do-not-grep` one level up. The founder ruling that phrase comes
from was about TESTS asserting on source text instead of calling the code. The
same defect exists in the duplicate matcher: it compares two DESCRIPTIONS of two
defects and never once runs either defect's falsifier against the other's
repair.

WHAT IS WRONG WITH THE TEXT MATCHER, MEASURED
---------------------------------------------
The live matcher is `bench/dm/_similarity.finding_similarity` at
`tau_sim = 0.50` (`bench/immune_agents.py:4331`), embedding backend
all-MiniLM-L6-v2 with a flaw-class bonus. Measured by `--survey` below over the
4 archived code-target runs (exp44, exp45, exp46, exp47), on the 4,511 pairs
whose BOTH members carry a falsifier: it calls 643 of them duplicates, 14.25%.

Measured by `--compare exp44`, on the 15 exp44 pairs the counterfactual repair
adjudicator (`scripts/adjudicate_by_repair.py`) decided SAME or DIFFERENT: this
module decides 12 of them, and the text matcher disagrees with the execution
verdict on 7 of those 12. All 7 are FALSE MERGES -- text says duplicate,
execution says two different defects that survive each other's repair -- and 0
run the other way. That is the costly direction: a false merge deletes a real
second defect from the count and the gate can close on it.

The same run reproduces the method against the stored adjudication: 12 of 15
agree, and all 3 disagreements are rows whose own stored `detail` string
records an ERROR leg (see EQUIPMENT FAILURE below).

THE METHOD, AND WHERE IT COMES FROM
-----------------------------------
Counterfactual repair, which this project already names as its ground-truth
method for "same defect or two?" and which `scripts/adjudicate_by_repair.py`
applied ONCE, offline, over an archived pair list, deciding 133 pairs.

What is new here is not the idea. It is that the method is (1) an importable
module a runner can call, (2) computed as a PROFILE -- one execution pass over
N findings and up to N+1 target states, then O(N^2) pair verdicts with no
further execution, where the pairwise script re-ran falsifiers per pair -- and
(3) built so it can be run BESIDE the text matcher and the two compared, which
is what `compare_matchers` is for. This is a behavioural change to how findings
are matched, so it must be measurable before anyone switches over, and it is
DEFAULT OFF until someone does.

  ExecutionBasedMatcher(..., enabled=False)   <- the default; runs nothing

THE DECISION RULE
-----------------
For each candidate a probe state is built: the target with that candidate's own
proposed fix applied. Every falsifier is run against every state. For a pair
(A, B) the decision reads ONLY the columns that belong to the pair -- the
pristine baseline, A's fix state, B's fix state:

  * either baseline verdict is not CONFIRMED      -> UNDECIDED / no_baseline
  * any verdict in those columns is not CONFIRMED
    and not REFUTED                               -> UNDECIDED / equipment_failure
  * neither fix produced a state                  -> UNDECIDED / no_applicable_fix
  * the two vectors differ                        -> DIFFERENT
  * they agree and some state flipped BOTH        -> SAME
  * they agree and nothing flipped either         -> UNDECIDED / no_witness

PAIR-SCOPED COLUMNS ARE NOT AN OPTIMISATION, THEY ARE THE FIX FOR A DEFECT THIS
FILE HAD. The first version compared the FULL vectors across all states. On
exp44 one finding's fix (C0026) makes the file raise on import, so its column is
ERROR for everybody -- and a full-vector rule refuses every pair in the run on
one unrelated broken fix. Measured: 2 of 15 pairs decided under full-vector,
12 of 15 under pair-scoped columns. The full vectors are still RECORDED on the
profile, because a state that discriminates a pair it does not belong to is
real information; it is simply not allowed to decide.

THE WITNESS REQUIREMENT IS THE VACUITY GUARD, AND IT IS NOT OPTIONAL. Two
falsifiers that CONFIRM on every state have identical vectors and have
demonstrated nothing about each other. Without the witness clause this module
would call every unrepairable pair SAME -- a matcher that returns a constant.
This project shipped exactly that once: `boundary_band_sensitivity` was an
unconditional constant, vacuous in 41 of 41 archived reports, and the test
guarding it asserted on source text instead of calling it.

EQUIPMENT FAILURE IS NOT A VERDICT. An ERROR, UNTOOLABLE or INTEGRITY_VIOLATION
leg means the instrument did not run, so it says nothing in either direction.
`scripts/adjudicate_by_repair.py` learned this the expensive way: SAME used to
be its fall-through, so an ERRORed leg PRODUCED a verdict rather than merely
contaminating one -- 40 of 178 leg-bearing directions across 34 of 133 pairs.
The stored `experimental_notes/data/adjudication_by_repair.json` predates that
fix and still carries the contaminated rows; see `--compare exp44`, where all 3
of this module's disagreements with that file are rows whose own `detail` string
records an ERROR leg.

THE REPOSITORY IS NEVER WRITTEN TO
----------------------------------
Every probe state is materialised as a throwaway overlay -- a temp root of
symlinks to the real repo with the ONE target file replaced -- via the runner's
own `_build_discrimination_overlay`, and falsifiers are re-run with
`repo_root` pointed at the overlay. `scripts/adjudicate_by_repair.py` instead
writes the patched file into the real tree and restores it in a `finally`. That
is safe alone and NOT safe here: this module is meant to be callable during a
run, and other agents work in this repository at the same time. `profile()`
additionally hashes the target before and after and raises if it moved, because
a guarantee nobody measures is a hope.

Usage
-----
    python3 -m bench.execution_based_matcher --survey
    python3 -m bench.execution_based_matcher --compare exp44
"""
from __future__ import annotations

import hashlib
import itertools
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Constants

#: DEFAULT OFF. This changes how findings are matched, which is behavioural, so
#: it is off until someone measures the two matchers against each other and
#: decides. `ExecutionBasedMatcher(enabled=False)` runs NO subprocesses at all --
#: not "runs them and ignores the result". Verified by
#: `test_disabled_runs_no_falsifier_at_all`.
ENABLED_BY_DEFAULT: bool = False

#: The two verdicts that carry information about the CLAIM. Everything else
#: (ERROR, UNTOOLABLE, INTEGRITY_VIOLATION) is a statement about the INSTRUMENT
#: and must not resolve a pair in either direction.
CLEAN_VERDICTS = frozenset({"CONFIRMED", "REFUTED"})

#: The name of the pristine column. Every pair's decision starts here and both
#: members must CONFIRM on it: a falsifier that does not fire against the state
#: it was raised against is not evidence about anything.
BASELINE_STATE = "pristine"

SAME = "SAME"
DIFFERENT = "DIFFERENT"
UNDECIDED = "UNDECIDED"

#: Threshold the live text matcher uses. Hardcoded at `bench/immune_agents.py`
#: :4331 (`tau_sim: float = 0.50`) for the NK-cell dedup that actually runs, so
#: the comparison harness defaults to the same number rather than to the config
#: default, which the immune pipeline does not read.
TEXT_TAU_SIM: float = 0.50

#: Per-falsifier wall clock. Below `falsifier_verify.DEFAULT_TIMEOUT` (30) on
#: purpose: a profile runs (states x findings) executions, so the tail matters
#: more here than in the gate. Measured on exp44, 9 findings x 9 states = 81
#: executions in 6.8 s, about 0.08 s each.
DEFAULT_TIMEOUT: int = 20


# ─────────────────────────────────────────────────────────────────────────────
# Inputs and outputs


@dataclass(frozen=True)
class Candidate:
    """One finding, as the execution matcher needs to see it.

    `description` and `flaw_class` are carried ONLY so the same object can be
    handed to the text matcher for comparison. Nothing in the execution
    decision reads them -- if it did, this would be the text matcher wearing a
    hat.
    """

    finding_id: str
    falsifier_code: str = ""
    proposed_fix: str = ""
    description: str = ""
    flaw_class: int = 0
    severity: float = 0.0
    model_id: str = ""

    @classmethod
    def from_registry_entry(cls, canonical_id: str, entry: dict) -> "Candidate":
        """Build from a `FindingRegistry` entry dict (or an archived report's)."""
        return cls(
            finding_id=canonical_id,
            falsifier_code=entry.get("falsifier_code") or "",
            proposed_fix=entry.get("proposed_fix") or "",
            description=entry.get("description") or "",
            flaw_class=int(entry.get("flaw_class") or 0),
            severity=float(entry.get("severity") or 0.0),
            model_id=entry.get("source_model") or "",
        )


@dataclass(frozen=True)
class ProbeState:
    """One version of the target the falsifiers are run against.

    `origin` names the candidate whose proposed fix produced this state, or ""
    for the pristine baseline. The pair-scoped decision selects its columns by
    `origin`, so this field is load-bearing, not documentation.
    """

    name: str
    source: str
    origin: str = ""


@dataclass(frozen=True)
class ExecutionProfile:
    """What every falsifier did on every state. The expensive part, computed once.

    `verdicts[finding_id]` is a tuple aligned with `states`. `match` slices it;
    it never re-executes.
    """

    target_rel: str
    states: Tuple[ProbeState, ...] = ()
    verdicts: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)
    executions: int = 0
    enabled: bool = True

    def column(self, origin: str) -> Optional[int]:
        """Index of the state produced by `origin`'s fix, or None."""
        for i, s in enumerate(self.states):
            if s.origin == origin:
                return i
        return None

    def baseline_column(self) -> Optional[int]:
        for i, s in enumerate(self.states):
            if not s.origin:
                return i
        return None


@dataclass(frozen=True)
class MatchVerdict:
    """One pair's answer, with the evidence that produced it attached.

    `columns` and the two vectors are kept so a disagreement with the text
    matcher can be READ rather than re-derived. A verdict whose evidence has to
    be recomputed to be understood is a claim about evidence.
    """

    a: str
    b: str
    verdict: str
    reason: str
    witness: Tuple[str, ...] = ()
    columns: Tuple[str, ...] = ()
    vector_a: Tuple[str, ...] = ()
    vector_b: Tuple[str, ...] = ()

    @property
    def decided(self) -> bool:
        return self.verdict in (SAME, DIFFERENT)


# ─────────────────────────────────────────────────────────────────────────────
# The matcher


class ExecutionBasedMatcher:
    """Match findings by what their falsifiers DO under each other's repairs.

    Constructed disabled. `enabled=False` is not a flag the decision consults
    at the end -- it short-circuits `profile()` before a single subprocess
    starts, so an accidental live construction costs nothing.
    """

    def __init__(
        self,
        repo_root,
        target_rel: str,
        *,
        enabled: bool = ENABLED_BY_DEFAULT,
        timeout: int = DEFAULT_TIMEOUT,
        apply_fix: Optional[Callable[[str, str], Optional[str]]] = None,
        reverify: Optional[Callable[..., str]] = None,
    ):
        self.repo_root = Path(repo_root).resolve()
        self.target_rel = str(target_rel)
        self.enabled = bool(enabled)
        self.timeout = int(timeout)
        # INJECTED, NOT IMPORTED AT MODULE LEVEL. Two reasons, both real.
        # `_apply_fix_to_source` lives in `bench.endocrine` and
        # `reverify_falsifier` in `bench.falsifier_verify`; importing the first
        # eagerly drags the endocrine module into every importer of this one,
        # and the seam is what lets a test drive a DELIBERATELY WRONG
        # implementation past this class and see the verdict change. A matcher
        # that cannot be shown to fail has not been shown to work.
        self._apply_fix = apply_fix
        self._reverify = reverify
        # Keyed (state source digest, falsifier digest). The same falsifier
        # against the same bytes cannot answer differently, and a profile runs
        # the same falsifier once per state -- so this also makes a pair's two
        # vectors comparable, which they would not be if each cell were an
        # independent sample of a flaky test.
        self._cache: Dict[Tuple[str, str], str] = {}
        self.executions = 0

    # ── plumbing ────────────────────────────────────────────────────────────

    def _fix_fn(self) -> Callable[[str, str], Optional[str]]:
        if self._apply_fix is None:
            from bench.endocrine import _apply_fix_to_source
            self._apply_fix = _apply_fix_to_source
        return self._apply_fix

    def _reverify_fn(self) -> Callable[..., str]:
        if self._reverify is None:
            from bench.falsifier_verify import reverify_falsifier
            self._reverify = reverify_falsifier
        return self._reverify

    def _run(self, code: str, source: str, overlay_root: Path) -> str:
        if not (code or "").strip():
            return "UNTOOLABLE"
        key = (
            hashlib.sha256(source.encode("utf-8", "replace")).hexdigest(),
            hashlib.sha256(code.encode("utf-8", "replace")).hexdigest(),
        )
        if key in self._cache:
            return self._cache[key]
        # A prose falsifier reaches its target by ABSOLUTE path, which
        # PYTHONPATH cannot redirect. The runner already owns that substitution
        # and measures whether it was load-bearing; re-deriving it here would be
        # a second implementation of a rule, which is a second rule.
        from bench.reference_runner_v3 import _retarget_falsifier
        retargeted, _ = _retarget_falsifier(code, self.repo_root, overlay_root)
        try:
            verdict = self._reverify_fn()(
                retargeted, repo_root=str(overlay_root), timeout=self.timeout
            )
        except Exception as exc:                       # noqa: BLE001
            # Named, not swallowed. A harness failure that reads as REFUTED
            # would turn a dead instrument into a SAME verdict.
            verdict = f"HARNESS_ERROR:{type(exc).__name__}"
        self.executions += 1
        self._cache[key] = verdict
        return verdict

    # ── the expensive pass ──────────────────────────────────────────────────

    def build_states(
        self, candidates: Sequence[Candidate], baseline_source: str
    ) -> Tuple[List[ProbeState], Dict[str, str]]:
        """Pristine plus one state per candidate whose fix actually applies.

        A fix that does not parse, does not locate, or leaves the file
        byte-identical produces NO state. That is recorded rather than guessed
        at: `_apply_fix_to_source` refuses ambiguity by returning None, and a
        wrongly-placed repair would yield a confident and false SAME.
        """
        states = [ProbeState(BASELINE_STATE, baseline_source, "")]
        skipped: Dict[str, str] = {}
        fix = self._fix_fn()
        for c in candidates:
            if not (c.proposed_fix or "").strip():
                skipped[c.finding_id] = "no_proposed_fix"
                continue
            try:
                patched = fix(baseline_source, c.proposed_fix)
            except Exception as exc:                   # noqa: BLE001
                skipped[c.finding_id] = f"fix_raised:{type(exc).__name__}"
                continue
            if not patched or patched == baseline_source:
                skipped[c.finding_id] = "fix_did_not_apply"
                continue
            states.append(ProbeState(f"fix:{c.finding_id}", patched, c.finding_id))
        return states, skipped

    def profile(
        self, candidates: Sequence[Candidate], baseline_source: str
    ) -> ExecutionProfile:
        """Run every falsifier against every state. Returns the verdict matrix.

        Cost is (states x candidates) executions minus cache hits, once -- not
        once per pair. `scripts/adjudicate_by_repair.py` re-ran per pair and
        needed its own cache to survive it.
        """
        if not self.enabled:
            # DEFAULT OFF MEANS NOTHING RUNS. Not "runs and is discarded".
            return ExecutionProfile(self.target_rel, (), {}, {}, 0, enabled=False)

        target = self.repo_root / self.target_rel
        before = self._target_digest(target)

        states, skipped = self.build_states(candidates, baseline_source)
        verdicts: Dict[str, List[str]] = {c.finding_id: [] for c in candidates}
        try:
            for state in states:
                overlay = self._overlay(state.source)
                try:
                    for c in candidates:
                        verdicts[c.finding_id].append(
                            self._run(c.falsifier_code, state.source, overlay)
                        )
                finally:
                    shutil.rmtree(overlay, ignore_errors=True)
        finally:
            after = self._target_digest(target)
            if before != after:
                # LOUD. The whole safety claim of this module is that it never
                # writes to the repository; a silent breach would let a run
                # corrupt a file other agents are editing.
                raise RuntimeError(
                    f"execution matcher mutated the repository target "
                    f"{self.target_rel!r} ({before} -> {after})"
                )

        return ExecutionProfile(
            target_rel=self.target_rel,
            states=tuple(states),
            verdicts={k: tuple(v) for k, v in verdicts.items()},
            skipped=skipped,
            executions=self.executions,
            enabled=True,
        )

    def _target_digest(self, target: Path) -> str:
        try:
            return hashlib.sha256(target.read_bytes()).hexdigest()
        except OSError:
            return "<absent>"

    def _overlay(self, content: str) -> Path:
        from bench.reference_runner_v3 import _build_discrimination_overlay
        return _build_discrimination_overlay(
            self.repo_root, self.target_rel, content
        )

    # ── the cheap pass ──────────────────────────────────────────────────────

    def match(self, profile: ExecutionProfile, a: str, b: str) -> MatchVerdict:
        """Decide one pair from the profile. No execution happens here."""
        if not profile.enabled:
            return MatchVerdict(a, b, UNDECIDED, "disabled")
        va_all = profile.verdicts.get(a)
        vb_all = profile.verdicts.get(b)
        if va_all is None or vb_all is None:
            return MatchVerdict(a, b, UNDECIDED, "not_profiled")

        base = profile.baseline_column()
        if base is None:
            return MatchVerdict(a, b, UNDECIDED, "no_baseline_state")

        cols = [base]
        for origin in (a, b):
            i = profile.column(origin)
            if i is not None and i not in cols:
                cols.append(i)
        names = tuple(profile.states[i].name for i in cols)
        va = tuple(va_all[i] for i in cols)
        vb = tuple(vb_all[i] for i in cols)

        def out(verdict: str, reason: str, witness: Tuple[str, ...] = ()) -> MatchVerdict:
            return MatchVerdict(a, b, verdict, reason, witness, names, va, vb)

        if va[0] != "CONFIRMED" or vb[0] != "CONFIRMED":
            # A falsifier that does not fire on the pristine target has not
            # reproduced its own defect, so it cannot speak about another's.
            return out(UNDECIDED, "no_baseline")
        if any(v not in CLEAN_VERDICTS for v in va + vb):
            return out(UNDECIDED, "equipment_failure")
        if len(cols) == 1:
            return out(UNDECIDED, "no_applicable_fix")
        if va != vb:
            witness = tuple(n for n, x, y in zip(names, va, vb) if x != y)
            return out(DIFFERENT, "surviving_repair", witness)
        # Vectors agree. They must agree about SOMETHING: a state where both
        # flipped away from the baseline is a repair that settled both, which is
        # the whole claim. Agreement with nothing flipping is agreement that
        # neither was repaired, which is not evidence of identity.
        witness = tuple(
            n for n, x in zip(names[1:], va[1:]) if x != va[0]
        )
        if not witness:
            return out(UNDECIDED, "no_witness")
        return out(SAME, "shared_repair", witness)

    def match_all(self, profile: ExecutionProfile) -> List[MatchVerdict]:
        ids = list(profile.verdicts)
        return [self.match(profile, a, b) for a, b in itertools.combinations(ids, 2)]


# ─────────────────────────────────────────────────────────────────────────────
# The text matcher, CALLED not re-implemented


def text_similarity(a: Candidate, b: Candidate) -> float:
    """The live text matcher's score for this pair.

    CALLS `bench.dm._similarity.finding_similarity` -- the same function
    `bench/immune_agents.py:4360` calls -- rather than restating its formula.
    A comparison harness that re-implemented the incumbent would be comparing
    against a description of the incumbent, and could not see it change.
    """
    from bench.dm._similarity import finding_similarity
    from bench.dm._types import Finding

    def _f(c: Candidate) -> Finding:
        return Finding(
            finding_id=c.finding_id, model_id=c.model_id, round_idx=0,
            flaw_class=c.flaw_class, severity=c.severity, abstraction_index=0.0,
            description=c.description, proposed_fix=c.proposed_fix,
            falsifier_code=c.falsifier_code,
        )

    return float(finding_similarity(_f(a), _f(b)))


def text_verdict(a: Candidate, b: Candidate, tau_sim: float = TEXT_TAU_SIM) -> str:
    """SAME / DIFFERENT under the incumbent rule. It never returns UNDECIDED --
    which is itself the point of comparison: the text matcher must answer every
    pair, and this one may decline."""
    return SAME if text_similarity(a, b) >= tau_sim else DIFFERENT


# ─────────────────────────────────────────────────────────────────────────────
# Running the two side by side


@dataclass(frozen=True)
class ComparisonRow:
    a: str
    b: str
    execution: str
    execution_reason: str
    text: str
    similarity: float

    @property
    def comparable(self) -> bool:
        return self.execution in (SAME, DIFFERENT)

    @property
    def agree(self) -> bool:
        return self.comparable and self.execution == self.text


@dataclass(frozen=True)
class ComparisonReport:
    rows: Tuple[ComparisonRow, ...] = ()
    tau_sim: float = TEXT_TAU_SIM

    @property
    def decided(self) -> Tuple[ComparisonRow, ...]:
        return tuple(r for r in self.rows if r.comparable)

    def counts(self) -> Dict[str, int]:
        d = self.decided
        agree = sum(1 for r in d if r.agree)
        # Named by DIRECTION, because the two errors are not equally costly. A
        # false merge deletes a real second defect from the count and lets the
        # gate close on it; a false split costs a duplicate line in a report.
        false_merge = sum(
            1 for r in d if r.execution == DIFFERENT and r.text == SAME)
        false_split = sum(
            1 for r in d if r.execution == SAME and r.text == DIFFERENT)
        return {
            "pairs": len(self.rows),
            "execution_decided": len(d),
            "agree": agree,
            "disagree": len(d) - agree,
            "text_merges_what_execution_separates": false_merge,
            "text_separates_what_execution_merges": false_split,
        }


def compare_matchers(
    matcher: ExecutionBasedMatcher,
    profile: ExecutionProfile,
    candidates: Sequence[Candidate],
    *,
    pairs: Optional[Iterable[Tuple[str, str]]] = None,
    tau_sim: float = TEXT_TAU_SIM,
) -> ComparisonReport:
    """Run BOTH matchers over the same pairs and report where they part.

    This exists because D8 is a BEHAVIOURAL change. Agreement is not the
    interesting output -- the disagreements are, and they must be countable
    before anyone changes which matcher decides.
    """
    by_id = {c.finding_id: c for c in candidates}
    if pairs is None:
        pairs = itertools.combinations(sorted(by_id), 2)
    rows: List[ComparisonRow] = []
    for a, b in pairs:
        ca, cb = by_id.get(a), by_id.get(b)
        if ca is None or cb is None:
            continue
        mv = matcher.match(profile, a, b)
        sim = text_similarity(ca, cb)
        rows.append(ComparisonRow(
            a=a, b=b, execution=mv.verdict, execution_reason=mv.reason,
            text=(SAME if sim >= tau_sim else DIFFERENT), similarity=round(sim, 4),
        ))
    return ComparisonReport(tuple(rows), tau_sim)


# ─────────────────────────────────────────────────────────────────────────────
# Reproducing the numbers in this file's docstring.
#
# `measured-rate-travels-with-its-script`: every figure quoted above is produced
# by one of the two entry points below, over files committed in this repository.

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The archived runs whose target is Python and still on disk. Mirrors
#: `scripts/adjudicate_by_repair.py:TARGETS` deliberately -- both read the same
#: four runs, and a drift between them would make the two sets of numbers
#: incomparable.
ARCHIVE_RUNS = {
    "exp44": ("exp44_evidence_locationkey_live", "bench/evidence.py"),
    "exp45": ("exp45_memory_statistics_live", "bench/dm/_memory.py"),
    "exp46": ("exp46_stage6_locationkey_live", "bench/dm/_shadow_stage6.py"),
    "exp47": ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py"),
}

REPAIR_ADJUDICATION = (
    REPO_ROOT / "experimental_notes" / "data" / "adjudication_by_repair.json"
)


def load_archive(run: str) -> Tuple[List[Candidate], str, str]:
    """Candidates carrying a falsifier, plus the target path and its source."""
    stem, target_rel = ARCHIVE_RUNS[run]
    hits = [
        p for p in (REPO_ROOT / "bench" / "logs").glob(f"{stem}_*/{stem}_report.json")
        if ".errata" not in str(p)
    ]
    if not hits:
        raise FileNotFoundError(f"archived run not present: {stem}")
    entries = json.loads(hits[0].read_text(encoding="utf-8"))["registry"]["entries"]
    cands = [
        Candidate.from_registry_entry(cid, e)
        for cid, e in sorted(entries.items())
        if (e.get("falsifier_code") or "").strip()
    ]
    return cands, target_rel, (REPO_ROOT / target_rel).read_text(encoding="utf-8")


def survey() -> Dict[str, dict]:
    """What the TEXT matcher does on the archive. No execution, so it is cheap.

    Reproduces: 4,511 falsifier-bearing pairs across the 4 code-target runs,
    643 called duplicate at tau_sim = 0.50, 14.25%.
    """
    out: Dict[str, dict] = {}
    tot_pairs = tot_dup = 0
    for run in ARCHIVE_RUNS:
        cands, _, _ = load_archive(run)
        pairs = list(itertools.combinations(cands, 2))
        dup = sum(1 for a, b in pairs if text_similarity(a, b) >= TEXT_TAU_SIM)
        out[run] = {"findings": len(cands), "pairs": len(pairs), "text_duplicate": dup}
        tot_pairs += len(pairs)
        tot_dup += dup
    out["TOTAL"] = {
        "pairs": tot_pairs, "text_duplicate": tot_dup,
        "rate": round(tot_dup / tot_pairs, 6) if tot_pairs else 0.0,
    }
    return out


def compare_against_repair_adjudication(run: str = "exp44") -> dict:
    """Both matchers, plus the archived counterfactual-repair verdicts.

    Restricted to the findings the stored adjudication decided SAME or
    DIFFERENT, so the three-way comparison is like for like.
    """
    stored = json.loads(REPAIR_ADJUDICATION.read_text(encoding="utf-8"))["rows"]
    decided = [r for r in stored
               if r["run"] == run and r["verdict"] in (SAME, DIFFERENT)]
    wanted = {c for r in decided for c in (r["a"], r["b"])}

    cands, target_rel, source = load_archive(run)
    cands = [c for c in cands if c.finding_id in wanted]
    matcher = ExecutionBasedMatcher(REPO_ROOT, target_rel, enabled=True)
    prof = matcher.profile(cands, source)
    report = compare_matchers(
        matcher, prof, cands, pairs=[(r["a"], r["b"]) for r in decided])

    by_pair = {(r.a, r.b): r for r in report.rows}
    three_way = []
    for r in decided:
        row = by_pair.get((r["a"], r["b"]))
        if row is None:
            continue
        three_way.append({
            "a": r["a"], "b": r["b"], "stored_repair": r["verdict"],
            "execution": row.execution, "execution_reason": row.execution_reason,
            "text": row.text, "similarity": row.similarity,
            "stored_detail": r.get("detail", ""),
        })
    agree_stored = sum(1 for t in three_way if t["execution"] == t["stored_repair"])
    # Every disagreement with the STORED file should be a row the stored file
    # produced from an ERROR leg -- rows the 2026-08-28 equipment-failure fix in
    # `scripts/adjudicate_by_repair.py` would no longer decide, and which were
    # never recomputed into the JSON. Counted, not asserted in prose.
    stale = sum(1 for t in three_way
                if t["execution"] != t["stored_repair"] and "ERROR" in t["stored_detail"])
    return {
        "run": run,
        "executions": prof.executions,
        "states": len(prof.states),
        "counts": report.counts(),
        "vs_stored_repair_adjudication": {
            "pairs": len(three_way),
            "agree": agree_stored,
            "disagree": len(three_way) - agree_stored,
            "disagreements_whose_stored_row_has_an_ERROR_leg": stale,
        },
        "rows": three_way,
    }


def _main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--survey", action="store_true",
                    help="text-matcher duplicate rate over the archive (no execution)")
    ap.add_argument("--compare", metavar="RUN", nargs="?", const="exp44",
                    choices=sorted(ARCHIVE_RUNS),
                    help="run BOTH matchers on an archived run and report disagreement")
    args = ap.parse_args(argv)
    # A bare invocation must never start executing falsifiers by accident. The
    # project rule is that `--help` must never cost money; the same reasoning
    # applies to compute.
    if not (args.survey or args.compare):
        ap.print_help()
        return 0
    if args.survey:
        print(json.dumps(survey(), indent=1))
    if args.compare:
        print(json.dumps(compare_against_repair_adjudication(args.compare), indent=1))
    return 0


if __name__ == "__main__":                                  # pragma: no cover
    raise SystemExit(_main())
