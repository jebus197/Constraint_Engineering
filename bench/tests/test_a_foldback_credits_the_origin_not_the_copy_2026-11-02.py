"""A folded-back file must credit where a design CAME FROM, not which copy it took.

WHAT WENT WRONG, 2026-11-02. `bench/proof_verify.py` was folded back on his ruling
and its docstring read "Written by panel seat `fable` in the joint round of
2026-10-31". The byte-identical body was preserved **56 minutes earlier** under
seat `cc2`, from cc2's OWN sandbox in the BLIND round of 2026-10-30 -- and a blind
round is one in which a seat cannot see its co-seat's work. Both PROVENANCE records
carry the same sha256. So cc2 authored it, fable's copy is a joint-round return,
and the fold-back credited the copy it was drawn from rather than the origin.

WHY THAT IS NOT A TIDINESS POINT. The project's own standing directive on simulated
panels states the principle: a result attributed to a model that never produced it
is indistinguishable, downstream, from a fabricated result. And
`public-model-marking` requires a major model contribution to be marked where
relevant, which only works if the mark names the right model.

★ THE PROPERTY GUARDED IS SATISFIABLE BY NAMING BOTH, which is what the repair did.
It is NOT "never name the later seat" -- naming the copy you took is useful
provenance. It is: if a live file credits a seat, and a byte-identical preserved
body exists under an EARLIER seat, the file must name that earlier seat too. So a
correct file passes and a file crediting only the copy fails.

★ IT DOES NOT NEED A LIVE DEFECT. The dual-attributed bodies are historical facts
in the archive, so the check has subjects whether or not any live file is currently
wrong -- the property `feedback_a_regression_guard_must_not_need_a_live_defect_2026-10-31`
asks for. If the archive ever holds 0 such bodies the test says so and skips rather
than passing vacuously.
"""
from __future__ import annotations

import collections
import hashlib
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HDR = re.compile(r"^#\s*PRESERVED SEAT EVIDENCE\. Written by seat '([^']+)' "
                 r"during panel round '([^']+)'")
SEAT = re.compile(r"\b(cc2|fable|gemini|codex|chatgpt|deepseek)\b", re.I)

#: An AUTHORSHIP CLAIM, not any mention of a seat. The distinction is the whole
#: predicate and the first version of this file got it wrong in exactly the way my
#: own manual check had: it flagged
#: `bench/tests/test_spawn_blob_tokens_2026-10-03.py`, whose text reads "First
#: reported by cc2 (blind round 2, 2026-10-02)" -- a credit for FINDING THE DEFECT,
#: a different act from authoring the file, and correct as written.
#:
#: THE PHRASINGS ARE DERIVED FROM THE CORPUS RATHER THAN GUESSED. Across bench/,
#: scripts/ and experimental_notes/, authorship is claimed 332 times as "Written
#: by" and twice as "Taken from the copy preserved under", the latter being the
#: 2026-11-02 repair. "First reported by", "independently reproduced" and bare
#: mentions are NOT authorship claims and are deliberately out of scope.
#: CASE-INSENSITIVE, because this project writes a correction in capitals and the
#: first version of this pattern matched "Authored by" while missing "AUTHORED BY"
#: -- so it flagged the very file that had just been repaired.
AUTHORSHIP = re.compile(
    r"(written by|taken from the copy[^.]{0,40}?under|authored by)"
    r"[^.]{0,80}?\b(cc2|fable|gemini|codex|chatgpt|deepseek)\b", re.I)


def _authorship_credits(head: str) -> set[str]:
    """Seats this text CLAIMS AS AUTHOR, lowercased. Mentions do not count."""
    return {m.group(2).lower() for m in AUTHORSHIP.finditer(head)}


def _preserved() -> list[dict]:
    root = REPO / "experimental_notes" / "seat_evidence"
    out = []
    if not root.is_dir():
        return out
    for p in root.rglob("*.py"):
        try:
            lines = p.read_text(errors="replace").splitlines(keepends=True)
        except OSError:
            continue
        if not lines:
            continue
        m = HDR.match(lines[0])
        if not m:
            continue
        body = "".join(lines[1:])
        out.append({
            "path": p, "seat": m.group(1), "round": m.group(2),
            "sha": hashlib.sha256(body.encode()).hexdigest(),
            "mtime": p.stat().st_mtime, "name": p.name,
        })
    return out


def _dual_attributed() -> dict[str, list[dict]]:
    """Bodies preserved identically under 2 or more DIFFERENT seats."""
    by_sha: dict[str, list[dict]] = collections.defaultdict(list)
    for r in _preserved():
        by_sha[r["sha"]].append(r)
    return {s: v for s, v in by_sha.items()
            if len({x["seat"] for x in v}) > 1}


def _live_files() -> list[pathlib.Path]:
    out = []
    for root in (REPO / "bench", REPO / "scripts"):
        if not root.is_dir():
            continue
        for p in root.rglob("*.py"):
            s = str(p)
            if "/logs/" in s or "seat_evidence" in s:
                continue
            out.append(p)
    return out


class TestTheCheckHasSubjects:
    """Not vacuous: say so if the archive holds no dual attributions."""

    def test_the_archive_holds_dual_attributed_bodies(self):
        dual = _dual_attributed()
        if not dual:
            pytest.skip("no dual-attributed preserved bodies; nothing to guard")
        assert len(dual) >= 1
        # every case must have a strictly earliest seat, or "origin" is undefined
        for sha, v in dual.items():
            times = sorted(x["mtime"] for x in v)
            assert times[0] < times[-1], (
                f"body {sha[:12]} has no strictly earliest copy, so which seat is "
                f"the origin cannot be read off the archive")


class TestALiveFileNamesTheOrigin:
    """The property. Satisfiable by naming BOTH seats."""

    def test_no_live_file_credits_only_a_later_copy(self):
        dual = _dual_attributed()
        if not dual:
            pytest.skip("no dual-attributed bodies")
        problems = []
        live = _live_files()
        for sha, v in dual.items():
            earliest = min(v, key=lambda x: x["mtime"])
            later = {x["seat"] for x in v if x["seat"] != earliest["seat"]}
            names = {x["name"] for x in v}
            for lp in live:
                if lp.name not in names:
                    continue
                head = "\n".join(lp.read_text(errors="replace").splitlines()[:60])
                credited = _authorship_credits(head)
                if not credited:
                    continue      # claims no author; a bare mention is not a claim
                # if it credits a LATER seat it must also name the EARLIEST
                if (credited & {s.lower() for s in later}
                        and earliest["seat"].lower() not in credited):
                    problems.append(
                        f"{lp.relative_to(REPO)} credits {sorted(credited)} but the "
                        f"identical body was preserved earlier under "
                        f"{earliest['seat']!r} in round {earliest['round']!r}; name "
                        f"the origin as well as the copy")
        assert not problems, "\n".join(problems)

    def test_the_check_would_catch_the_defect_it_was_written_for(self, tmp_path):
        """The control, on a synthetic file, so the repair is not what makes it pass.

        Without this, a check that never fires would pass the test above.
        """
        dual = _dual_attributed()
        if not dual:
            pytest.skip("no dual-attributed bodies")
        sha, v = next(iter(dual.items()))
        earliest = min(v, key=lambda x: x["mtime"])
        later = [x for x in v if x["seat"] != earliest["seat"]][0]

        head = f'"""Written by panel seat `{later["seat"]}`, and nobody else."""\n'
        credited = _authorship_credits(head)
        assert later["seat"].lower() in credited, "the control's own text is wrong"
        assert earliest["seat"].lower() not in credited, (
            "the control names the origin, so it does not exercise the failure")
        # this is exactly the condition the test above flags
        assert (credited & {later["seat"].lower()}
                and earliest["seat"].lower() not in credited)

    def test_naming_both_seats_satisfies_it(self):
        """The repair's shape passes, so the property is satisfiable rather than
        a prohibition on crediting the copy at all."""
        dual = _dual_attributed()
        if not dual:
            pytest.skip("no dual-attributed bodies")
        sha, v = next(iter(dual.items()))
        earliest = min(v, key=lambda x: x["mtime"])
        later = [x for x in v if x["seat"] != earliest["seat"]][0]
        head = (f'"""Taken from the copy preserved under seat `{later["seat"]}`. '
                f'Authored by `{earliest["seat"]}`."""\n')
        credited = _authorship_credits(head)
        assert earliest["seat"].lower() in credited
        assert later["seat"].lower() in credited


class TestTheKnownCaseIsRecorded:
    """The specific repair, pinned to the PROPERTY and not to the wording."""

    def test_the_proof_verifier_names_both_seats_or_is_absent(self):
        f = REPO / "bench" / "proof_verify.py"
        if not f.is_file():
            pytest.skip("bench/proof_verify.py is not in this tree")
        head = "\n".join(f.read_text(errors="replace").splitlines()[:60])
        credited = _authorship_credits(head) | {
            m.group(1).lower() for m in SEAT.finditer(head)}
        assert "cc2" in credited and "fable" in credited, (
            f"credits {sorted(credited)}; the design is cc2's from the blind round "
            f"and the copy folded back was fable's from the joint round, so both "
            f"belong in the provenance")


class TestTheNarrowingIsItselfGuarded:
    """A mention is not a claim, pinned so the predicate cannot widen back."""

    def test_first_reported_by_is_not_an_authorship_claim(self):
        head = "First reported by cc2 (blind round 2, 2026-10-02); reproduced"
        assert _authorship_credits(head) == set(), (
            "'First reported by' is a credit for finding a defect, not for "
            "authoring a file; counting it reintroduces the false positive this "
            "file was corrected for")

    def test_written_by_is_an_authorship_claim(self):
        """The control, or the test above would pass on a predicate matching nothing."""
        assert _authorship_credits("Written by seat 'cc2' during panel round 'x'") \
            == {"cc2"}

    def test_the_real_file_that_caused_the_false_positive_is_not_flagged(self):
        f = REPO / "bench" / "tests" / "test_spawn_blob_tokens_2026-10-03.py"
        if not f.is_file():
            pytest.skip("that file is not in this tree")
        head = "\n".join(f.read_text(errors="replace").splitlines()[:60])
        assert _authorship_credits(head) == set(), (
            "this file credits cc2 with REPORTING the defect and claims no "
            "author; flagging it is the false positive, not a finding")
