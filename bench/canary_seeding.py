"""Canary seeding: turn convergence from an absence of signal into a demonstration.

WHAT THIS IS FOR
================
The two-sided gate certifies convergence when critical novelty has flattened AND
K consecutive rounds add no new critical findings. Both halves read the same
evidence: what the reviewers said. Neither can distinguish

    "the panel went quiet because the document is clean"          (converged)
    "the panel went quiet because the panel stopped looking"      (exhausted)

Canary seeding supplies the missing discriminator. A canary is a defect of known
type and known location, seeded into the review target. If the panel is still
detecting, it kills its canaries. Silence PLUS killed canaries is affirmative
evidence of credible exhaustion; silence plus MISSED canaries is a dead panel.

Method is mutation testing (DeMillo, Lipton and Sayward 1978) pointed at
reviewers rather than at a test suite: p_hat = catches / k, per model, per domain.

    Proposed by the fable reviewer, Note 5 route B, 2026-08-27.
    Founder ruling 2026-08-27: "Build it, test it, implement it in its own
    independent 3 model panel review ... give it its own panel/build process."

THE CATALOGUE IS ANSWER-KEY MATERIAL
====================================
A canary catalogue names defects that reviewers are about to be scored on
finding. That is scoring-key material under the project's standing rule: keys
and planted defects live OUTSIDE the repository, and unencrypted study copies may
be published only AFTER the experiment has run. `load_catalogue` therefore
REFUSES a path inside any git work tree.

WHAT exp48 ACTUALLY WAS, because the first draft of this docstring got it wrong
and the correct version indicts this design rather than excusing it. exp48 was
not a path-handling slip. A MODEL wrote a falsifier that opened the scoring key,
and the runner re-ran it. The model's own recorded reason was that editing the
file would destroy "a seeded fault the panel is scored on". **Seeding created the
motive.** That is the closest thing to a base rate this design has, and it says
that a module whose entire purpose is seeding faults raises the very pressure
that produced the project's one excluded run. Corrected 2026-08-28 after the
build panel checked the claim against resources/RECOVERY.md:133 and
bench/tests/test_falsifier_cannot_read_the_key.py.

THE SEEDED DOCUMENT IS ITSELF AN ANSWER KEY, and a worse one than the catalogue.
bench/cdsfl_registry/targets/MANIFEST.md records the measurement: a target kept
under version control leaks itself, because `git diff` returns the planted set at
precision 1.000 with no key needed. `seed()` therefore refuses to seed a target
that lives inside a git work tree.

WHAT IS DELIBERATELY NOT HERE
=============================
No scoring of a live run, and no wiring into the gate. This module measures; it
does not yet decide anything. Whether a missed canary should BLOCK convergence is
a founder ruling, not a default, because it is a new way for a run to fail.
"""
from __future__ import annotations

import dataclasses
import hashlib
import os
import json
import pathlib
import re
from typing import Iterable, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Split names. p_hat is reported on HELD_OUT only -- see `detection_rate`.
CALIBRATION = "calibration"
HELD_OUT = "held_out"
_SPLITS = (CALIBRATION, HELD_OUT)


class CanaryIntegrityError(RuntimeError):
    """A canary operation would have leaked, or rested on, answer-key material."""


@dataclasses.dataclass(frozen=True)
class Canary:
    """One seeded defect with known ground truth.

    `generator` is load-bearing for the Goodhart guard: a catalogue whose canaries
    all come from one generator measures whether reviewers have learned that
    generator, not whether they can still detect. `detection_rate` refuses to
    report on a single-generator held-out set.
    """
    id: str
    domain: str
    defect_class: str
    generator: str
    split: str
    find: str                 # exact text to replace in the target
    replace: str              # the seeded (defective) text
    summary: str              # ground truth, never shown to a reviewer

    def __post_init__(self) -> None:
        if self.split not in _SPLITS:
            raise ValueError(f"{self.id}: split must be one of {_SPLITS}, got {self.split!r}")
        if not self.find:
            raise ValueError(f"{self.id}: `find` is empty, so the canary cannot be seeded")
        if self.find == self.replace:
            raise ValueError(f"{self.id}: find == replace, so nothing would be seeded")
        for field in ("id", "domain", "defect_class", "generator"):
            if not str(getattr(self, field)).strip():
                raise ValueError(
                    f"{self.id!r}: {field} is empty. An empty generator name counted as "
                    "a second generator and defeated the multi-generator guard.")


# --------------------------------------------------------------------------- #
# Loading                                                                      #
# --------------------------------------------------------------------------- #
def _in_a_git_worktree(path: pathlib.Path) -> pathlib.Path | None:
    """Return the work-tree root containing `path`, or None.

    Two defects the build panel found, both fixed here.

    `REPO_ROOT` is `parents[1]` of THIS FILE, so the old check protected the tree
    containing this copy of the module. Panels are dispatched into throwaway git
    worktrees, so a harness copy running in one would happily read a catalogue
    sitting in the canonical tracked tree -- the exp48 shape through the front
    door. Containment is now decided by walking for a `.git` entry, so ANY work
    tree is protected, including the canonical one and this module's own.

    And `Path.resolve()` does not case-normalise on macOS. `relative_to` is a
    string comparison, so a path whose ROOT components differ in case resolved to
    "outside" and the catalogue was read. Verified 2026-08-28: mangling a
    component BELOW the root was correctly refused (which is what one reviewer
    tested), while mangling a component OF the root read the key (which is what
    the other tested). Both reported accurately; they ran different things.
    `os.path.normcase` closes it on case-insensitive volumes.
    """
    resolved = pathlib.Path(os.path.normcase(os.path.realpath(path)))
    for parent in [resolved, *resolved.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def _is_inside_repo(path: pathlib.Path) -> bool:
    return _in_a_git_worktree(path) is not None


def load_catalogue(path: str | pathlib.Path) -> list[Canary]:
    """Load a canary catalogue from OUTSIDE the repository.

    Refuses an in-repo path. The refusal is the point: a catalogue committed to
    the repository is a published answer key, and the publication is silent.
    """
    p = pathlib.Path(path).expanduser()
    if _is_inside_repo(p):
        raise CanaryIntegrityError(
            f"catalogue path is inside the repository: {p}\n"
            "A canary catalogue is scoring-key material. It belongs in the key "
            "store outside the repository (see bench/vault_keys.sh), never in a "
            "tracked tree. Refusing to read it."
        )
    if not p.is_file():
        raise FileNotFoundError(f"canary catalogue not found: {p}")
    # A hardlink is a second name for the same inode, and resolve() cannot see
    # through one, so a link made outside a tracked tree reads the tracked bytes.
    # Both build reviewers demonstrated it; verified here.
    if p.stat().st_nlink > 1:
        raise CanaryIntegrityError(
            f"catalogue has {p.stat().st_nlink} hard links: {p}\n"
            "A hardlink is a second name for the same bytes, which may be a "
            "tracked file. Refusing to read a multiply-linked catalogue.")
    raw = json.loads(p.read_text(encoding="utf-8"))
    cans = [Canary(**c) for c in raw["canaries"]]
    # Catalogue-wide id uniqueness. seed() checked only within one call, so an id
    # present in BOTH splits let a CALIBRATION kill score as held-out detection --
    # precisely the Goodhart failure the split exists to prevent.
    seen: dict[str, str] = {}
    for c in cans:
        if c.id in seen:
            raise CanaryIntegrityError(
                f"duplicate canary id {c.id!r} (splits {seen[c.id]!r} and {c.split!r}). "
                "An id in both splits lets a calibration kill count as held-out detection.")
        seen[c.id] = c.split
    return cans


# --------------------------------------------------------------------------- #
# Seeding                                                                      #
# --------------------------------------------------------------------------- #
def seed(target_text: str, canaries: Sequence[Canary],
         *, target_path: str | pathlib.Path | None = None) -> tuple[str, dict]:
    """Seed `canaries` into `target_text`. Returns (seeded_text, manifest).

    The manifest records what was seeded and where. It is answer-key material and
    is returned rather than written, so the caller decides where it goes -- which
    must be the key store.

    Blinding is checked on what the edit INTRODUCED -- no canary id, split name,
    generator name or ground-truth summary, and none of the words canary/seeded/
    mutant. A word blacklist is a tripwire and not a proof; it catches the obvious
    tell and nothing subtler.

    It also refuses to seed a target inside a git work tree, because `git diff`
    returns the planted set at precision 1.000 and needs no key to read it.
    """
    if not canaries:
        raise ValueError("no canaries supplied; seeding nothing is not a measurement")
    if target_path is not None:
        wt = _in_a_git_worktree(pathlib.Path(target_path))
        if wt is not None:
            raise CanaryIntegrityError(
                f"target is inside a git work tree ({wt}). The SEEDED DOCUMENT is "
                "itself an answer key and a worse one than the catalogue: "
                "MANIFEST.md records that `git diff` returns the planted set at "
                "precision 1.000, no key required. Seed a copy with no history.")
    seen_ids: set[str] = set()
    out = target_text
    placed = []
    for c in canaries:
        if c.id in seen_ids:
            raise ValueError(f"duplicate canary id {c.id!r}")
        seen_ids.add(c.id)
        n = out.count(c.find)
        if n == 0:
            raise ValueError(f"{c.id}: `find` text is not present in the target, so it cannot be seeded")
        if n > 1:
            raise ValueError(
                f"{c.id}: `find` text occurs {n} times, so the seeded location is ambiguous. "
                "Widen `find` until it is unique.")
        out = out.replace(c.find, c.replace, 1)
        placed.append({"id": c.id, "domain": c.domain, "defect_class": c.defect_class,
                       "generator": c.generator, "split": c.split, "summary": c.summary})

    _assert_blind(target_text, out, canaries)
    manifest = {
        "canaries": placed,
        "seeded_sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
        "clean_sha256": hashlib.sha256(target_text.encode("utf-8")).hexdigest(),
    }
    return out, manifest


#: Words that would announce the exercise. Plurals and possessives included --
#: `\bmutant\b` does not match "mutants", demonstrated by the build panel.
_TELLS = re.compile(r"\bcanar(?:y|ies)\b|\bseed(?:ed|ing|s)?\b|\bmutants?\b", re.I)


def _assert_blind(clean: str, seeded: str, canaries: Iterable[Canary]) -> None:
    """The SEEDED EDIT must not announce itself.

    Counts tokens in the seeded text against the clean text and flags only what
    the edit INTRODUCED. Scanning the whole document instead produced a confirmed
    false refusal that would have bitten the real corpus: a legitimate target
    containing "a seeded random number generator" was rejected outright, and any
    biology document containing "mutant" would be too -- and there is a biology
    domain. Found by the build panel, 2026-08-28.
    """
    def _added(pattern: str) -> bool:
        n_clean = len(re.findall(pattern, clean, re.I))
        n_seed = len(re.findall(pattern, seeded, re.I))
        return n_seed > n_clean

    for c in canaries:
        for token, what in ((c.id, "id"), (c.generator, "generator name"),
                            (c.split, "split name"), (c.summary, "ground-truth summary")):
            if token and _added(re.escape(token)):
                raise CanaryIntegrityError(
                    f"the seeded edit introduced the canary {what} {token!r} ({c.id}). "
                    "A reviewer could read off the answer, so this is not a measurement.")
    if len(_TELLS.findall(seeded)) > len(_TELLS.findall(clean)):
        raise CanaryIntegrityError(
            "the seeded edit introduced a word that announces the exercise "
            "(canary, seeded or mutant, including plurals). Blinding is broken.")


# --------------------------------------------------------------------------- #
# Scoring                                                                      #
# --------------------------------------------------------------------------- #
def catches(findings: Sequence[dict], canaries: Sequence[Canary],
            *, verifier=None) -> dict[str, list[str]]:
    """Which canaries did each model kill? Returns {model: [canary_id, ...]}.

    A finding kills a canary when its falsifier DEMONSTRATES the defect on the
    seeded text and does NOT demonstrate it on the clean text. That is the
    project's own counterfactual method, and it is the only evidence accepted
    here: matching a finding's prose against the ground-truth summary would score
    the reviewer on wording rather than on detection.

    `verifier(finding, canary) -> bool` is injected so this function can be tested
    without running model code. Passing None means no evidence is available, and
    the honest result is that nothing is scored as caught.
    """
    out: dict[str, list[str]] = {}
    if verifier is None:
        return out
    by_id = {c.id: c for c in canaries}
    for f in findings:
        model = f.get("model") or "(unattributed)"
        for cid, c in by_id.items():
            if cid in out.get(model, []):
                continue
            if verifier(f, c):
                out.setdefault(model, []).append(cid)
    return out


def detection_rate(caught: dict[str, list[str]], canaries: Sequence[Canary],
                   *, models: Sequence[str], seeded_ids: Iterable[str],
                   domain: str | None = None) -> dict[str, float]:
    """p_hat = catches / k per model, over HELD-OUT canaries only.

    Held-out only, because a canary the panel has already been scored on is a
    canary it can have learned. Calibration canaries set the threshold; held-out
    canaries measure. Reporting both together is the Goodhart failure this design
    exists to avoid.

    `models` is the roster of reviewers actually dispatched, and it is REQUIRED.
    An earlier version derived the result from `caught` alone, so a model that
    detected NOTHING was simply absent from the output rather than scoring 0.0 --
    and a reviewer that has stopped detecting altogether is the exact thing this
    instrument exists to find. Silent omission in the reassuring direction, in the
    module written to catch silent omission in the reassuring direction.

    KNOWN LIMIT, not fixable here: blinding covers the CONTENT of the seeded
    document. It cannot survive a reviewer that can read the target's version
    history, where the seeded edit is one `git diff` away. Seeding must therefore
    happen on a copy with no history, and that is a property of how the target is
    presented, not of this module.
    """
    pool = [c for c in canaries if c.split == HELD_OUT and (domain is None or c.domain == domain)]
    if not pool:
        raise CanaryIntegrityError(
            f"no held-out canaries{f' in domain {domain!r}' if domain else ''}. "
            "p_hat over calibration canaries measures memorisation, not detection.")
    generators = {c.generator.strip().lower() for c in pool}
    if len(generators) < 2:
        raise CanaryIntegrityError(
            f"held-out set uses a single generator ({generators.pop()!r}). p_hat would "
            "measure whether reviewers have learned that generator. Use at least two.")
    if not models:
        raise CanaryIntegrityError(
            "no model roster supplied. p_hat derived from the catch list alone "
            "omits any reviewer that caught nothing, which is the one result that "
            "must never go missing.")
    # The denominator must be what was ACTUALLY SEEDED, not what the catalogue
    # holds. A canary that was never seeded is unkillable by construction and
    # silently deflates every model's score. `seed()` returns the manifest that
    # supplies this; passing the catalogue's own ids is not a substitute.
    seeded = set(seeded_ids)
    if not seeded:
        raise CanaryIntegrityError(
            "no seeded ids supplied. Scoring against canaries that were never "
            "seeded deflates every model by an amount nobody can see.")
    ids = {c.id for c in pool} & seeded
    if not ids:
        raise CanaryIntegrityError(
            "no held-out canary was actually seeded, so there is nothing to score.")
    unknown = seeded - {c.id for c in canaries}
    if unknown:
        raise CanaryIntegrityError(f"seeded ids not present in the catalogue: {sorted(unknown)}")
    for m, hits in caught.items():
        stray = set(hits) - {c.id for c in canaries}
        if stray:
            raise CanaryIntegrityError(
                f"model {m!r} credited with ids that are in no catalogue: {sorted(stray)}. "
                "Silently intersecting these away would hide an id-drift defect upstream.")
    k = len(ids)
    return {m: len(set(caught.get(m, ())) & ids) / k for m in models}
