#!/usr/bin/env python3
"""An entry asking for a ruling he has ALREADY given costs him the decision twice.

WHY THIS EXISTS. On 2026-10-30 entry B47 read `state: OPEN`, `status: PROPOSED`,
no `ruled` date, and closed with *"NEEDS HIS RULING."* He had ruled on it on
2026-10-29 in words a commit message quotes verbatim -- *"Build and implement
option 1. fr"* -- and the work shipped the same day in `b7cf1566` with 14 passing
tests and a mechanism that is demonstrably LIVE: `unclean_sv_commits` returns a
sha today, and the resolved memory baseline differs with and without it.

So a decision he had made was queued back to him. That is the `already ruled`
failure this project's record already names twice -- 11 of 45 on one measurement,
recurring on 2026-10-17 -- and it is the most expensive kind of staleness here,
because every other kind wastes MY time and this one wastes HIS.

HOW IT DETECTS, AND WHY THE EVIDENCE IS A COMMIT MESSAGE. The task list's own
`ruled:` field is the thing that is wrong, so it cannot be the detector. The
independent record is the commit: when a ruling of his is built, the commit
message names the entry and quotes him. So for every OPEN entry this searches
the full history for a commit message that names that entry AND carries a
double-quoted string on the same line or the next, and reports the pair for
reading.

IT REPORTS SUSPECTS, NOT VERDICTS, AND THAT BOUNDARY IS DELIBERATE. A quotation
beside an entry id is strong evidence that he spoke on it and NOT proof of what
he decided -- he may have rejected it, or ruled on a neighbouring question.
Closing an entry remains a recorded act with evidence attached, never an
inference from this script. What it removes is the need to re-read 186 entries by
hand to find the ones worth checking.

THE CONTROL IS BUILT IN: entries whose `ruled:` field already matches a commit
of the same vintage must NOT be flagged, or the detector is simply reporting
every entry that was ever discussed.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.task_list_markers import parse_entries  # noqa: E402

#: A line that names an entry and quotes him. The quote must be non-trivial:
#: a 2-word fragment is as likely to be a file name as a ruling.
_QUOTED = re.compile(r'[""„"](?P<q>[^""„"]{12,400})[""„"]')


#: HIS VOICE, NOT MINE: A VERDICT ENDS WITH AN MC MARKER.
#:
#: The loose harvest below finds any quotation beside an entry id, and most of
#: what it finds is MY OWN prose quoted back in my own commit messages. Measured
#: 2026-10-30 over the 7 open entries: 19 quotations harvested, of which 1 is his.
#:
#: 2 DISCRIMINATORS WERE TRIED AND THE FIRST FAILED. Matching an MC marker
#: ANYWHERE in the quote gave 4 of 19, and 3 of those 4 were the bare English
#: article "a" matching the `a` command mid-prose -- "answering it once would
#: retire a class", "on a STILL tree", "a local-first general-purpose STEM
#: calculator". Requiring the marker to TRAIL the quotation gives 1 of 19, which
#: is exactly the true positive, and excludes all 3 article matches. It works
#: because his verdicts put the marker last: "Build and implement option 1. fr".
#:
#: `a` is deliberately absent from the set even though it is a real command. A
#: discriminator that fires on the commonest word in English is not a
#: discriminator, and the cost of dropping it is that a verdict reading only
#: "a" would be missed -- which the guard records as a known limit rather than
#: hiding.
_HIS_VOICE = re.compile(
    r"(?:^|[\s.,;:!?])(fr|pf|qs|cy|rt|sv|pr|re|rs|sq|rg|ag|sy|y|d|e|f|p|t|x)"
    r"[\s.!?]*$", re.I)


def is_his_voice(quote: str) -> str | None:
    """The trailing MC marker if this reads as his verdict, else None."""
    m = _HIS_VOICE.search(quote or "")
    return m.group(1).lower() if m else None


def _commits_naming(ident: str) -> list[dict]:
    """Commits whose message names this entry, newest first.

    * THE FIRST VERSION OF THIS FUNCTION WAS BLIND, and it reported 0 suspects
    while B47 -- a true positive read by hand minutes earlier -- sat in the
    history. 2 predicate errors, both mine, in a producer written to catch
    exactly this shape of error:

      1. It split git's output on NEWLINES and required the `%x1f` field
         separators on every line. A commit body is multi-line, so only its
         FIRST body line was ever examined, and B47's quotation is further down.
         Fixed by terminating each record with `%x1e` and splitting on that, so
         a record survives however many newlines its body contains.
      2. It passed `--grep=\\bB47\\b` with `-E`. `\\b` is a GNU extension that
         git's POSIX ERE does not honour, so the pattern matched nothing
         reliably. Fixed by grepping LOOSELY in git and applying the word
         boundary in Python, where the semantics are known.

    A 0 from a blind detector is indistinguishable from a real 0, which is why
    the guard for this script asserts B47 is FOUND rather than asserting a count.
    """
    r = subprocess.run(
        ["git", "log", "--all", "--format=%H%x1f%cI%x1f%s%x1f%b%x1e",
         f"--grep={ident}", "-n", "40"],
        capture_output=True, text=True, cwd=str(REPO))
    out = []
    for record in (r.stdout or "").split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        parts = record.split("\x1f")
        if len(parts) < 3:
            continue
        sha, iso, subject = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else ""
        if not re.search(rf"(?<![A-Za-z0-9]){re.escape(ident)}(?![A-Za-z0-9])",
                         subject + "\n" + body):
            continue
        out.append({"sha": sha[:8], "when": iso[:10], "subject": subject,
                    "body": body})
    return out


def _quotes_beside(ident: str, text: str) -> list[str]:
    """Double-quoted strings on a line that names the entry, or the line after."""
    lines = text.split("\n")
    found: list[str] = []
    for i, line in enumerate(lines):
        if not re.search(rf"\b{re.escape(ident)}\b", line):
            continue
        window = " ".join(lines[i:i + 3])
        for m in _QUOTED.finditer(window):
            q = m.group("q").strip()
            if q and q not in found:
                found.append(q)
    return found


def is_suspect(asks_for_a_ruling: bool,
               ruled_field: str | None,
               newest_his_voice: str | None) -> bool:
    """THE DECISION, as a pure function of 3 inputs.

    * EXTRACTED 2026-10-30, because the guard that pinned this script's finding
    FIRED ON ITS OWN SUCCESS. It asserted that B47 and C1 are reported as
    suspects; acting on the finding -- closing B47 and advancing C1's `ruled`
    field to the date of the ruling -- correctly emptied the suspect list and
    turned that assertion red. The identical defect is recorded in
    `bench/tests/test_admission_counts_announced_apart_from_silent_2026-10-18.py`,
    whose own note reads *"IT FIRED ON SUCCESS ... The commit was refused by a
    guard celebrating its own obsolescence."*

    Pulling the decision out as a pure function lets the guard exercise it on
    SYNTHETIC inputs, which no repair to the task list can erase, while the
    live scan keeps reporting whatever the tree currently holds.

    An entry is a suspect when it asks for a ruling, a commit quotes HIM naming
    it, and the entry's own `ruled` field is absent or predates that commit.
    """
    if not asks_for_a_ruling or not newest_his_voice:
        return False
    if ruled_field is None:
        return True
    return ruled_field < newest_his_voice



#: THE SECOND SOURCE, ADDED 2026-11-03 ON HIS CHALLENGE. He asked whether all
#: the decisions put to him were new issues he had never ruled on. This script
#: answered 0 of 12 suspects -- and it was looking in the wrong place. It reads
#: COMMIT MESSAGES only, while the surface that actually records his verdicts
#: beside a decision is the report's own detail file, whose `ruled` and
#: `his_words` fields held 3 of the 14 presented decisions: B21, B71 and B84,
#: 0.214286, Wilson 95% [0.075714, 0.475892].
#:
#: ALL 3 TURNED OUT TO BE HANDLED CORRECTLY, which is why the predicate here is
#: NOT "his words exist". Each of those entries tells him in the text he reads
#: that his earlier ruling stands and names the distinct question that remains.
#: The failure that would cost him a decision twice is narrower and is what this
#: detects: HIS RULING IS ON RECORD AND THE TEXT HE READS DOES NOT SAY SO.
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"

#: Phrases that acknowledge a prior verdict of his. A DATE ALONE IS NOT ENOUGH
#: and matching one would have produced a false positive here: B71's section
#: says "You ruled on 1 November" where its field holds 2026-11-01, so a
#: date-string test would have accused a compliant entry.
_ACKNOWLEDGES = re.compile(
    r"you ruled|already ruled|ruling stands|is not reopened|you have settled|"
    r"you settled|you authorised|you authorized|permission is granted|"
    r"I accept your recommendation|you accepted", re.I)


def detail_rulings() -> dict:
    """ident -> {ruled, his_words, acknowledged} from the file HE is shown.

    `acknowledged` asks whether the `title` and `what` fields -- which are what
    the report renders to him verbatim -- say that he already ruled. If his
    verdict is on record and that text does not say so, the entry reads to him
    as a fresh question he has already answered.
    """
    try:
        obj = json.loads(DETAIL.read_text(encoding="utf-8"))
    except Exception:                                        # noqa: BLE001
        return {}
    out = {}
    for key, rec in obj.items():
        if not key.startswith("task:") or not isinstance(rec, dict):
            continue
        ruled = str(rec.get("ruled") or "").strip()
        words = str(rec.get("his_words") or "").strip()
        if not (ruled or words):
            continue
        ident = key.split(":", 1)[1]
        out[ident] = {"ruled": ruled, "his_words": words}
    report = _rendered_report()
    presented = _presented_idents(report)
    for ident, rec in out.items():
        rec["acknowledged"] = _acknowledged_in_report(ident, report)
        rec["presented"] = ident in presented
    return out



def _rendered_report() -> str:
    """The report AS GENERATED. Read, never guessed.

    THE FIRST VERSION OF THIS GUESSED and was wrong on its first run, which is
    the 3rd proxy-predicate error of 2026-11-03. It inferred "presented as a
    decision" from the PRESENCE of an `options` field, and C0001 carries
    options yet is not rendered as a numbered decision at all -- the report puts
    it under outstanding work with the words "YOU RULED THIS ON 2026-11-01; the
    work is outstanding", which is a fuller acknowledgement than the predicate
    was looking for. A proxy for what a generator renders is not what it
    renders; run it and read it.
    """
    try:
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "morning_report_build_2026-10-12.py")],
            capture_output=True, text=True, cwd=str(REPO), timeout=180)
        return r.stdout or ""
    except Exception:                                        # noqa: BLE001
        return ""


def _presented_idents(report: str) -> set:
    """Entries the report renders as NUMBERED decisions, from its own headings."""
    return set(re.findall(r"^### \d+\.\s+([A-Za-z]+\d+)", report, re.M))


def _acknowledged_in_report(ident: str, report: str) -> bool:
    """Does the text he reads say he already ruled on this entry?

    Scoped to the entry's own rendered section where it has one, and otherwise
    to any line naming it -- because an entry can be acknowledged outside the
    decisions list, as C0001 is.
    """
    m = re.search(rf"^### \d+\.\s+{re.escape(ident)}\b.*?(?=^### |\Z)",
                  report, re.S | re.M)
    scope = m.group(0) if m else "\n".join(
        ln for ln in report.splitlines() if ident in ln)
    return bool(_ACKNOWLEDGES.search(scope))


def analyse() -> dict:
    rows = []
    for e in parse_entries():
        if e.state != "OPEN":
            continue
        asks = bool(re.search(r"NEEDS (YOUR|HIS) RULING", e.text, re.I))
        quotes: list[dict] = []
        for c in _commits_naming(e.ident):
            qs = _quotes_beside(e.ident, c["subject"] + "\n" + c["body"])
            if qs:
                marked = [{"text": q, "marker": is_his_voice(q)} for q in qs]
                quotes.append({"sha": c["sha"], "when": c["when"],
                               "quotes": qs[:3], "marked": marked,
                               "his_voice": any(m["marker"] for m in marked)})
        his = [q for q in quotes if q.get("his_voice")]
        newest = his[0]["when"] if his else None
        # SUSPECT: it asks for a ruling, and a commit quotes HIM naming it, and
        # the entry's own `ruled` field is absent or older than that commit.
        # Keyed on HIS voice, not on any quotation: 18 of the 19 quotations
        # harvested on 2026-10-30 were my own prose quoted back at me.
        stale = is_suspect(asks, e.ruled, newest)
        rows.append({"ident": e.ident, "asks_for_a_ruling": asks,
                     "ruled_field": e.ruled, "newest_quote": newest,
                     "quoting_commits": quotes[:3],
                     "his_voice_commits": his[:3], "suspect_stale": stale})
    # THE 2 CHANNELS ARE REPORTED APART, NOT SUMMED. They answer different
    # questions -- one asks whether a commit quotes him naming the entry, the
    # other whether the text he is shown admits a verdict already on record --
    # and a single opaque count would hide which surface was blind.
    det = detail_rulings()
    unacknowledged = sorted(i for i, v in det.items() if not v["acknowledged"])
    return {"rows": rows,
            "n_open": len(rows),
            "n_asking": sum(1 for r in rows if r["asks_for_a_ruling"]),
            "suspects": [r["ident"] for r in rows if r["suspect_stale"]],
            "detail_rulings": det,
            "n_with_his_words": len(det),
            "unacknowledged": unacknowledged}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    a = analyse()

    if args.json:
        print(json.dumps(a, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    for r in a["rows"]:
        mark = "SUSPECT " if r["suspect_stale"] else ("asks    "
                                                     if r["asks_for_a_ruling"]
                                                     else "        ")
        print(f"  {mark} {r['ident']:4s} ruled:{str(r['ruled_field']):10s} "
              f"newest quoting commit: {r['newest_quote'] or '-'}")
        for c in r["quoting_commits"]:
            print(f"           {c['sha']} {c['when']}")
            for q in c["quotes"]:
                print(f"             “{q[:110]}”")
    k, n = len(a["suspects"]), a["n_asking"]
    lo, hi = wilson(k, max(n, 1))
    try:
        from statsmodels.stats.proportion import proportion_confint
        slo, shi = proportion_confint(k, max(n, 1), method="wilson")
        agree = abs(slo - lo) < 1e-12 and abs(shi - hi) < 1e-12
    except Exception:                                          # pragma: no cover
        slo = shi = float("nan")
        agree = False
    print()
    print(f"OPEN entries: {a['n_open']}   asking for a ruling: {n}")
    print(f"SUSPECT ALREADY-RULED: {k} of {n} -> {a['suspects']}")
    print(f"    Wilson 95% (closed form) [{lo:.6f}, {hi:.6f}]")
    print(f"    Wilson 95% (statsmodels) [{slo:.6f}, {shi:.6f}]  agree={agree}")
    print()
    det = a.get("detail_rulings", {})
    print()
    print("SECOND SOURCE -- the detail file he is actually shown:")
    print(f"  decisions whose record holds a ruling of his : {a['n_with_his_words']}")
    for i, v in sorted(det.items()):
        mark = "OK " if v["acknowledged"] else "!! "
        print(f"    {mark}{i:5s} ruled={v['ruled'] or '-':11s} "
              f"presented_as_a_decision={str(v.get('presented')):5s} "
              f"acknowledged_in_what_he_reads={v['acknowledged']}")
        if v["his_words"]:
            print(f"          his words: {v['his_words'][:72]}")
    bad = a.get("unacknowledged", [])
    bad_shown = [i for i in bad if det.get(i, {}).get("presented")]
    bad_hidden = [i for i in bad if not det.get(i, {}).get("presented")]
    n_shown = sum(1 for v in det.values() if v.get("presented"))
    print(f"  HIS RULING ON RECORD, NOT ACKNOWLEDGED IN HIS TEXT: "
          f"{len(bad)} of {a['n_with_his_words']}")
    print(f"    ...among entries PRESENTED to him as decisions : "
          f"{len(bad_shown)} of {n_shown} -> {bad_shown}")
    if n_shown:
        lo3, hi3 = wilson(len(bad_shown), n_shown)
        print(f"      Wilson 95% [{lo3:.6f}, {hi3:.6f}]")
    print(f"    ...among entries NOT presented                 : "
          f"{len(bad_hidden)} of {a['n_with_his_words'] - n_shown} -> {bad_hidden}")
    if a["n_with_his_words"] - n_shown:
        lo4, hi4 = wilson(len(bad_hidden), a["n_with_his_words"] - n_shown)
        print(f"      Wilson 95% [{lo4:.6f}, {hi4:.6f}]")
    print("    THE SPLIT IS THE POINT. A decision PUT TO HIM that hides his own")
    print("    prior ruling costs him the decision twice. One merely RECORDED and")
    print("    never shown costs him nothing today and is a documentation gap.")
    print("    Summing the 2 would read as `your decision queue is wrong`, which")
    print("    the measurement does not support.")
    print()
    print("These are SUSPECTS for reading, never verdicts. A quotation beside an")
    print("entry id shows he SPOKE on it, not what he decided, and closing an")
    print("entry stays a recorded act with evidence attached.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
