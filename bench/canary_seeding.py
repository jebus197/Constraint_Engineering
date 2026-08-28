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
REFUSES a path inside the repository. This is not advisory -- exp48 is the run
that had to be excluded because the harness read the key it exists to protect,
and that happened through a path that looked innocuous at the call site.

WHAT IS DELIBERATELY NOT HERE
=============================
No scoring of a live run, and no wiring into the gate. This module measures; it
does not yet decide anything. Whether a missed canary should BLOCK convergence is
a founder ruling, not a default, because it is a new way for a run to fail.
"""
from __future__ import annotations

import dataclasses
import hashlib
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


# --------------------------------------------------------------------------- #
# Loading                                                                      #
# --------------------------------------------------------------------------- #
def _is_inside_repo(path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


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
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [Canary(**c) for c in raw["canaries"]]


# --------------------------------------------------------------------------- #
# Seeding                                                                      #
# --------------------------------------------------------------------------- #
def seed(target_text: str, canaries: Sequence[Canary]) -> tuple[str, dict]:
    """Seed `canaries` into `target_text`. Returns (seeded_text, manifest).

    The manifest records what was seeded and where. It is answer-key material and
    is returned rather than written, so the caller decides where it goes -- which
    must be the key store.

    Blinding is checked, not hoped for: the seeded text is verified to contain no
    canary id, no split name and no generator name before it is returned. A
    reviewer that can see which passage is seeded is not being measured.
    """
    if not canaries:
        raise ValueError("no canaries supplied; seeding nothing is not a measurement")
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

    _assert_blind(out, canaries)
    manifest = {
        "canaries": placed,
        "seeded_sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
        "clean_sha256": hashlib.sha256(target_text.encode("utf-8")).hexdigest(),
    }
    return out, manifest


def _assert_blind(seeded: str, canaries: Iterable[Canary]) -> None:
    """The seeded document must not announce its own canaries."""
    low = seeded.lower()
    for c in canaries:
        for token, what in ((c.id, "id"), (c.generator, "generator name"), (c.summary, "ground-truth summary")):
            if token and token.lower() in low:
                raise CanaryIntegrityError(
                    f"seeded target contains the canary {what} {token!r} ({c.id}). "
                    "A reviewer could read off the answer, so this is not a measurement.")
    if re.search(r"\bcanary\b|\bseeded\b|\bmutant\b", low):
        raise CanaryIntegrityError(
            "seeded target contains a word that announces the exercise "
            "('canary', 'seeded' or 'mutant'). Blinding is broken.")


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
                   *, models: Sequence[str], domain: str | None = None) -> dict[str, float]:
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
    generators = {c.generator for c in pool}
    if len(generators) < 2:
        raise CanaryIntegrityError(
            f"held-out set uses a single generator ({generators.pop()!r}). p_hat would "
            "measure whether reviewers have learned that generator. Use at least two.")
    if not models:
        raise CanaryIntegrityError(
            "no model roster supplied. p_hat derived from the catch list alone "
            "omits any reviewer that caught nothing, which is the one result that "
            "must never go missing.")
    ids = {c.id for c in pool}
    k = len(ids)
    return {m: len(set(caught.get(m, ())) & ids) / k for m in models}
