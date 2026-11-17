#!/usr/bin/env python3
"""Did the free panel's recommendations match mine, on the 19 he owes?

★ HIS QUESTION, 2026-11-16, verbatim: *"What do they recommend and (without
telling them) does their recommendation match yours?"*

★ THE COMPARISON IS NOT TRIVIAL, BECAUSE THE BRIEF SHUFFLED THE OPTIONS. My
recommendation is option 1 in 17 of 19 entries, so presenting the options in
their recorded order would have told a seat the answer by position alone. The
brief therefore shuffles each item's options under a fixed seed, and a seat's
"option B" is NOT the record's option 2. This script reproduces that shuffle and
VERIFIES the reproduction against the brief's own text before using it: if the
replayed order does not reproduce the delivered letters byte for byte, it
refuses rather than reporting a comparison built on a guess.

★ IT CLASSIFIES, IT DOES NOT ADJUDICATE. Whether a seat is RIGHT is the
founder's call. What is reported is agreement and disagreement, preserved as
information, with no compelled convergence anywhere in it.

Reads the round directory and the pinned blind record. Writes nothing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import random
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
BLIND = REPO / "experimental_notes" / "evidence" / "cc1_blind_recommendations_2026-11-17.json"
BUILDER = REPO / "scripts" / "build_the_nineteen_panel_brief_2026-11-17.py"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"


def _builder():
    spec = importlib.util.spec_from_file_location("brief_builder", BUILDER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["brief_builder"] = m
    spec.loader.exec_module(m)
    return m


def shuffle_map(bb) -> dict:
    """entry -> list mapping brief position (0=A) to the record's 1-based index.

    Replays the builder's own generator in the builder's own order. Verified
    against the delivered brief by `verify_map` before any use.
    """
    d = json.loads(DETAIL.read_text(encoding="utf-8"))
    rng = random.Random(bb.SEED)
    out = {}
    for e in bb.OWED:
        opts = list((d.get(f"task:{e}", {}) or {}).get("options") or [])
        cleaned = [bb.strip_leaks(o) for o in opts]
        order = list(range(len(cleaned)))
        paired = list(zip(cleaned, order))
        # The builder shuffles the TEXT list; replay by shuffling an index list
        # with an identical-length sequence so the generator advances the same way.
        rng.shuffle(paired)
        out[e] = [i + 1 for _, i in paired]
    return out


#: ★ THE ARTEFACT IS THE GROUND TRUTH, NOT A REBUILD. ADDED 2026-11-17 AFTER
#: THIS SCRIPT CORRECTLY REFUSED TO SCORE ITS OWN ROUND.
#: `shuffle_map` replays the builder over the LIVE decisions file. That is sound
#: only while the live file still holds what the seats were shown, and it stopped
#: holding it the same night: 3 recommendations were corrected after the round
#: was scored, so the replay no longer reproduced the delivered letters and the
#: script refused -- rightly, because reporting different numbers silently would
#: be worse. But a refusal means the delivered figures could no longer be
#: REPRODUCED, which is `measured-rate-travels-with-its-script` broken at the
#: point it matters: the producer existed and no longer produced.
#: So the letter a seat chose is now read from the FROZEN brief that was actually
#: delivered, matched to the FROZEN record of CC1's own picks. Both artefacts are
#: immutable: the brief sits in the round directory, and the recommendations file
#: pins its source commit and a blob sha256.
#: Matching is on the BOLD LEAD-IN rather than the whole sentence, because the
#: builder strips recommendation markers out of the delivered text by design, so
#: the delivered option and the recorded option differ in their tails on exactly
#: the items that carried a marker.
#: The replay is NOT removed. It detects a builder-side shuffle bug that the
#: artefact route cannot see, while the artefact route detects drift the replay
#: cannot; they fail differently rather than one dominating, so both are kept
#: and the replay now REPORTS instead of refusing.
FROZEN_RECS = (REPO / "experimental_notes" / "evidence"
               / "cc1_blind_recommendations_2026-11-17.json")

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)


def _lead_in(text: str) -> str:
    """The option's bold lead-in, which survives marker stripping."""
    m = _BOLD.search(text or "")
    return (m.group(1) if m else (text or "")[:60]).strip().rstrip(".,").lower()


def delivered_options(brief: pathlib.Path) -> dict:
    """entry -> [(letter, delivered_text)], read from the brief as sent."""
    text = brief.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^### ITEM \d+\. (B\d{2,4}) — .*?$(.*?)(?=^### ITEM |\Z)",
                         text, re.M | re.S):
        out[m.group(1)] = re.findall(r"^([A-Z])\. (.+)$", m.group(2), re.M)
    return out


def letter_brief_for(round_dir: pathlib.Path) -> pathlib.Path:
    """The brief whose LETTERS a round's answers refer to.

    A joint round is not a letter-choice round. Its brief heads items
    `### B77  ★ YOU DIFFER` and carries 0 lettered option lines, because it puts
    each seat's own blind answer in front of it and asks it to reconsider. The
    letters a seat names there are therefore the BLIND round's letters, and
    looking for them in the joint brief is what produced `item not found in the
    brief` on all 19 items. The parent is the same directory without the suffix.
    """
    if round_dir.name.endswith("_joint"):
        parent = round_dir.with_name(round_dir.name[: -len("_joint")])
        if (parent / "BRIEF.md").is_file():
            return parent / "BRIEF.md"
    return round_dir / "BRIEF.md"


def my_letter_from_artefacts(brief: pathlib.Path) -> dict:
    """entry -> the LETTER that carried CC1's own recommendation in the brief.

    Reads only frozen artefacts, so it keeps reproducing after the live
    decisions file moves. Returns None for an entry whose lead-in cannot be
    matched, because a wrong letter is worse than no letter.
    """
    recs = json.loads(FROZEN_RECS.read_text(encoding="utf-8"))["recommendations"]
    delivered = delivered_options(brief)
    out = {}
    for entry, rec in recs.items():
        opts = delivered.get(entry) or []
        want = _lead_in(rec.get("option_text", ""))
        hit = [L for L, got in opts if _lead_in(got) == want]
        #: A WHOLE-LEAD-IN MATCH IS TOO STRICT WHERE THE MARKER SAT INSIDE THE
        #: BOLD SPAN. On B160 the recorded option reads "...change nothing. this
        #: is the recommendation" and the delivered one "...change nothing. it
        #: errs toward...", because `strip_leaks` removed the marker from WITHIN
        #: the bold text rather than after it. So fall back to the longest
        #: common prefix and accept it only when it picks out exactly 1 option:
        #: a prefix that matches 2 options is no evidence at all, and a wrong
        #: letter is worse than none.
        if len(hit) != 1:
            for width in (60, 40, 24):
                pre = want[:width]
                if len(pre) < width:
                    continue
                cand = [L for L, got in opts if _lead_in(got).startswith(pre)]
                if len(cand) == 1:
                    hit = cand
                    break
        out[entry] = hit[0] if len(hit) == 1 else None
    return out


def verify_map(bb, mapping: dict, brief: pathlib.Path) -> list:
    """Refuse unless the replayed order reproduces the brief's own letters."""
    d = json.loads(DETAIL.read_text(encoding="utf-8"))
    text = brief.read_text(encoding="utf-8")
    bad = []
    for e in bb.OWED:
        m = re.search(rf"^### ITEM \d+\. {e} — .*?$(.*?)(?=^### ITEM |\Z)",
                      text, re.M | re.S)
        if not m:
            bad.append((e, "item not found in the brief"))
            continue
        delivered = re.findall(r"^([A-Z])\. (.+)$", m.group(1), re.M)
        opts = [bb.strip_leaks(o) for o in (d[f"task:{e}"]["options"])]
        if len(delivered) != len(opts):
            bad.append((e, f"{len(delivered)} letters against {len(opts)} options"))
            continue
        for pos, (letter, got) in enumerate(delivered):
            want = opts[mapping[e][pos] - 1]
            if got.strip() != want.strip():
                bad.append((e, f"letter {letter} does not match replayed position {pos}"))
                break
    return bad


#: ★ 2 SEATS, 2 REPLY SHAPES, AND A PARSER TUNED TO EACH RATHER THAN 1 THAT
#: FITS NEITHER. Read off the 2026-11-17 replies before writing this:
#:   fable  `**ITEM 1 — B77 \`pf:...\` — Better option (A, as ratification...)**`
#:   cc2    `B77 — \`pf:...\` · convergence gate` then `**My option: C, ...**`
#: A single loose pattern over either shape picked up the first capital letter
#: in the following prose, which on fable's reply returned the wrong letter on
#: 12 of 19 items. A parser that silently returns a wrong letter is worse than
#: one that returns nothing, so `seat_picks` records NONE where it cannot read
#: a letter, and the caller prints that as unparsed rather than as agreement.
#: ★ KEYED ON WHAT BOTH REPLY SHAPES SHARE, NOT ON EITHER ONE'S MARKDOWN.
#: Measured on the 2026-11-17 replies, the 2 seats head their items differently:
#:   cc2    `## ITEM 1. B77 — \`pf:4f09b9135a60\` · convergence gate`
#:   fable  `**ITEM 1 — B77 \`pf:4f09b9135a60\` — Better option (A, ...)**`
#: A parser written to either shape returns 0 of 19 on the other, and the first
#: version of this one did exactly that -- it reported cc2 as having produced no
#: verdicts when cc2 had produced all 19. What the 2 share is the ITEM CODE
#: followed closely by its BACKTICKED HASH, which is a heading in both and
#: appears nowhere else in either reply. That is the anchor.
HEAD_ANY = re.compile(r"(B\d{2,4})\s*[—–-]?\s*`((?:pf|qs|fr|frx|stm|disc|wr):"
                      r"[0-9a-f]{12})`")
#: The seat's own statement of its choice, in either shape.
CHOICE = re.compile(r"(?:\*\*My option:|Better option[:\s(]|^\s*\*\*[A-F]\b|"
                    r"[—–-]\s*)(.{0,170})", re.M)
LETTER = re.compile(r"(?:^|[\s(*])(?:option\s+)?([A-F])(?=[\s,.):;]|$)")
OWN = re.compile(r"\bNONE\b|\bnone of\b|better option(?!\s*[:(]\s*[A-F])"
                 r"|wrong question|as framed", re.I)


def _letter(text: str):
    """(kind, letter). kind is LETTER, OWN where the seat proposed its own, or None."""
    own = bool(OWN.search(text))
    m = LETTER.search(text)
    if own:
        return ("OWN", m.group(1).upper() if m else None)
    return ("LETTER", m.group(1).upper()) if m else (None, None)


def seat_picks(reply: str, owed: list) -> dict:
    """entry -> (kind, letter), read from the seat's own words."""
    heads = list(HEAD_ANY.finditer(reply))
    picks = {}
    for i, h in enumerate(heads):
        code = h.group(1)
        end = heads[i + 1].start() if i + 1 < len(heads) else len(reply)
        seg = reply[h.end():end]
        mo = re.search(r"\*\*My option:\s*(.{0,170})", seg, re.I)
        if mo:
            picks[code] = _letter(mo.group(1))
            continue
        # fable states the choice in the heading itself, after the hash
        tail = seg[:190]
        picks[code] = _letter(tail)
    return {e: picks.get(e, (None, None)) for e in owed}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--round", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args([] if argv is None else argv)

    rd = REPO / "bench" / "logs" / a.round
    bb = _builder()

    #: PRIMARY: the frozen brief that was dispatched, and the frozen record of
    #: CC1's own picks. Neither can drift, so the figures keep reproducing.
    letter_brief = letter_brief_for(rd)
    my_letters = my_letter_from_artefacts(letter_brief)
    recovered = sum(1 for v in my_letters.values() if v)
    print(f"  letters read from the DELIVERED brief "
          f"({letter_brief.parent.name}): {recovered} of {len(my_letters)}")
    if recovered == 0:
        print("  REFUSED: no letter could be read from the delivered brief, so a "
              "seat's choice cannot be translated back to an option at all.")
        return 2

    #: SECONDARY, AND IT NO LONGER BLOCKS. The replay catches a builder-side
    #: shuffle bug that the artefact route cannot see; the artefact route catches
    #: drift in the live decisions file that the replay cannot. They fail
    #: differently, so both are kept -- but a replay mismatch now means the LIVE
    #: file has moved since dispatch, which is expected and is not a reason to
    #: refuse to score an already-delivered round.
    try:
        mapping = shuffle_map(bb)
        bad = verify_map(bb, mapping, rd / "BRIEF.md")
    except Exception as exc:                               # noqa: BLE001
        mapping, bad = {}, [("replay", f"{type(exc).__name__}: {exc}")]
    if bad:
        print(f"  cross-check: the replay no longer reproduces the brief "
              f"({len(bad)} item(s)); the live decisions file has moved since "
              f"dispatch. Scoring proceeds from the frozen artefacts.")
        #: STATE THE REMAINDER. A list cut to N under a heading that reads as
        #: complete is a silent falsehood, and this line was 1 of 6 offenders
        #: `test_operational_scripts.py` names -- the only 1 of them written
        #: on 2026-11-17, by me, in the same session that quoted the rule.
        SHOWN = 3
        for e, why in bad[:SHOWN]:
            print(f"    {e}: {why}")
        if len(bad) > SHOWN:
            print(f"    ... and {len(bad) - SHOWN} more item(s) not shown "
                  f"({len(bad)} in total)")
    else:
        print("  cross-check: the replay still reproduces the delivered brief")

    blind = json.loads(BLIND.read_text(encoding="utf-8"))["recommendations"]
    seats = {}
    for name in ("cc2", "fable"):
        f = rd / f"{name}.json"
        if not f.is_file():
            print(f"  {name}: no reply yet")
            continue
        #: ★ THE REPLY TEXT, NOT THE JSON AROUND IT. The first version passed
        #: `json.dumps(body)` to the parser, which escapes every newline into a
        #: literal backslash-n -- so every `^`-anchored pattern matched nothing
        #: and all 19 items on both seats read as UNPARSED. An instrument that
        #: returns "no verdict" for a reply full of verdicts reports silence as
        #: a finding about the seats when it is a finding about itself.
        try:
            body = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            body = {"response": f.read_text(encoding="utf-8", errors="replace")}
        txt = body.get("response", "") if isinstance(body, dict) else str(body)
        if not txt.strip():
            print(f"  {name}: reply is empty; refusing to report it as silence")
            continue
        seats[name] = seat_picks(txt, bb.OWED)

    if not seats:
        print("  no seat replies on disk yet; nothing to compare")
        return 1

    rows = []
    for e in bb.OWED:
        #: LETTERS, NOT INDICES. Comparing indices required translating a
        #: seat's letter back through a replayed shuffle. Both sides are
        #: letters in the delivered brief, so comparing them directly removes
        #: the translation and the only thing that could drift with it.
        mine = my_letters.get(e)
        row = {"entry": e, "mine": mine, "n": blind[e]["n_options"]}
        for name, picks in seats.items():
            kind, letter = picks.get(e, (None, None))
            row[name + "_kind"] = kind
            row[name] = letter
            row[name + "_letter"] = letter
        rows.append(row)

    if a.json:
        print(json.dumps({"my_letters": my_letters, "rows": rows}, indent=2))
        return 0

    names = sorted(seats)
    print()
    hdr = f"  {'entry':<7}{'mine':>6}" + "".join(f"{n:>9}" for n in names) + "   verdict"
    print(hdr)
    agree_all = agree_any = decided = 0
    for r in rows:
        line = f"  {r['entry']:<7}{r['mine']:>6}"
        vals = []
        for n in names:
            v = r.get(n)
            vals.append(v)
            line += f"{(str(v) if v else '-'):>9}"
        got = [v for v in vals if v]
        if got:
            decided += 1
            if all(v == r["mine"] for v in got) and len(got) == len(names):
                agree_all += 1
                line += "   ALL AGREE with me"
            elif any(v == r["mine"] for v in got):
                agree_any += 1
                line += "   SPLIT"
            else:
                line += "   ALL DIFFER from me"
        else:
            line += "   (no seat verdict parsed)"
        print(line)
    print()
    if decided:
        from statsmodels.stats.proportion import proportion_confint
        import mpmath as mp
        mp.mp.dps = 40
        for lbl, k in (("items where every seat agreed with me", agree_all),
                       ("items where at least 1 seat agreed", agree_all + agree_any)):
            lo, hi = proportion_confint(k, decided, alpha=0.05, method="wilson")
            cl, ch = proportion_confint(k, decided, alpha=0.05, method="beta")
            z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
            p = mp.mpf(k) / decided
            dd = 1 + z**2 / decided
            c = p + z**2 / (2 * decided)
            hh = z*mp.sqrt(p*(1-p)/decided + z**2/(4*decided**2))
            agree = max(abs(float((c-hh)/dd)-lo), abs(float((c+hh)/dd)-hi))
            print(f"  {lbl}: {k} of {decided} = {k/decided:.6f}")
            print(f"      Wilson [{lo:.6f}, {hi:.6f}] (mpmath agrees to {agree:.2e})"
                  f"  Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
    print()
    print("  DISAGREEMENT IS INFORMATION. A seat differing from me is not a seat "
          "being wrong;")
    print("  every one of the 19 is the founder's to rule, and the split is "
          "reported to him as a split.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
