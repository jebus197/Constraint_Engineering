#!/usr/bin/env python3
"""Did he ever ask what `v_bar` is? HE DID. This script's first answer was WRONG.

★★★ THE ORIGINAL CLAIM IS WITHDRAWN, 2026-11-03 EVENING, UNDER
`failure-later-refutation-protocol`. Recorded in full because the shape of the
error is more valuable than the answer.

  WHAT WAS CLAIMED. That the compaction summary of 06:19:48 UTC INVENTED a
  question of his asking what `v_bar` is, and that the question appears in
  nothing he wrote. The headline figure was 0 hits in 1,719 of his typed
  messages and 0 in 839 of his annotations.

  WHAT THE ORIGINAL PASS ASSESSED, AND IT WAS NOT CARELESS. It partitioned the
  corpus 3 ways and made a 2-SIDED prediction so a broken search could not
  produce the answer; it refused to report a negative unless the summary
  partition was non-zero; it pinned its own regex both ways; and it checked that
  its prefilter was lossless against an exhaustive decode. All of that held.

  WHAT REFUTED IT. He asked it directly at 2026-11-03T03:56:55 --
  *"What is v-bar? I have never heard of it before? Is it part of the
  mathematical model?"* -- typed WHILE A TURN WAS RUNNING. The harness stores
  such a message on an entry of type `queue-operation` with the text in a
  top-level `content` key, no `message` dict, and no `promptSource` field. So
  `_text_of` returned "" for it and `_partition` could not classify it as his.
  The corpus the measurement was certain about was missing 206 of his 1,421
  distinct messages, 0.144968, Wilson 95% [0.127620, 0.164231].

  WHAT IT IMPLIES, AND THIS IS THE PART WORTH KEEPING. Every defence above
  guarded the SEARCH. None guarded the CORPUS. A 2-sided prediction, a pinned
  regex and a lossless prefilter are all checks that the instrument reads what
  it was pointed at; not one of them asks whether it was pointed at everything.
  The anti-vacuity control worked perfectly and was satisfied by summary text,
  so it could never have surfaced this. An instrument written to catch a
  fabricated question of his was itself blind to 14.5 per cent of his words, and
  it then told me he had never asked something he asked 19 hours earlier.

  SCOPE OF THE FAILURE, NOT GENERALISED BEYOND IT. The regex, the partition
  logic, the interval arithmetic and the prefilter check were all correct and
  are unchanged. 1 function could not see 1 record shape.

THE SCRIPT NOW READS BOTH RECORDS through `scripts/his_messages.py`, which is
the single reader for what he typed, and the verdict it prints flips on the
evidence rather than on this docstring.

WHY THIS CLASS OF ERROR IS THE EXPENSIVE ONE. A fabricated question is
indistinguishable, downstream, from a real instruction: it acquires his name, it
gets worked on, and the work is then reported back to him as discharging
something he asked for. The project already carries 2 instances of advice
acquiring his authority without his words behind it -- an invented Wolfram denial
rule and an invented stored-falsifier condition, both retracted. This is the
same shape arriving through a NEW channel: the summary rather than the prose.

★ THE MEASUREMENT IS BUILT SO THAT A BROKEN SEARCH CANNOT PRODUCE THE ANSWER.
A grep returning 0 is worth nothing on its own -- it is equally consistent with
"he never said it" and "the search is broken", and this project has already been
bitten by a verdict that could not see its own subject removed. So the corpus is
PARTITIONED and the prediction is 2-SIDED:

    partition                                   prediction
    ---------------------------------------     -------------------------
    his genuinely typed messages                0 hits   <- the finding
    compaction summaries                      >=1 hits   <- the anti-vacuity
    his annotated response files                0 hits   <- the finding

If the summary partition is ALSO 0, the search is broken and this script exits 1
with the claim UNVERIFIED rather than reporting a negative. The same regex, the
same decoder and the same corpus produce both numbers, so the positive half is a
live control on the negative half.

HIS GENUINE MESSAGES ARE IDENTIFIED STRUCTURALLY, NOT BY KEYWORD. `promptSource
== "sdk"` with `isMeta` and `isCompactSummary` both false. A `role == "user"`
filter is WRONG here and was measured wrong the same day: it returns 1657
entries for this transcript because tool results and injected summaries carry the
user role, against 2 messages he actually typed on 2026-11-03.

THE PREFILTER IS A PROVABLE SUPERSET OF THE DECISION, and the one way it could
fail is CHECKED rather than assumed. The decision runs on decoded text; the
prefilter runs on the raw line, because the big transcript is 760 MB and cannot
be decoded line by line at acceptable cost. Any spelling of the token contains
the literal letters "bar" UNLESS a serialiser escaped an ASCII letter as `\\uXXXX`,
which no mainstream serialiser does. That exception is MEASURED: the count of
lines carrying `\\u0062`, `\\u0061`, `\\u0072` or `\\u0076` is reported, and where it
is 0 the superset is exact for this corpus rather than merely probable.

WHAT THIS DOES NOT CLAIM. `v_bar` is REAL and it matters: it is 1 of the 4
CapabilityFingerprint dimensions, it carries 0.350000 of the orchestrator role
score, and it is open for his ruling as entry B94 -- the dimension whose
self-reporting exposure was derived on 2026-11-03. Nothing here touches that.
The single claim is about the QUESTION'S PROVENANCE: he did not ask it, so no
reply is owed to him for it, and an entry recorded as answering him would have
been answering a summary.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

TRANSCRIPTS = (pathlib.Path.home() / ".claude" / "projects"
               / "-Users-georgejackson-Developer-Projects")
REPO = pathlib.Path(__file__).resolve().parents[1]

#: The decision, run on DECODED text. Covers vbar, v_bar, v-bar, v bar.
#:
#: THE FIRST VERSION WAS `v[-_ ]?bar` AND IT INVERTED THIS SCRIPT'S VERDICT.
#: That form matches ACROSS A WORD BOUNDARY, so "arXiv barely" contains "v bar"
#: and was counted as the founder asking about `v_bar`. The script then printed
#: HE DID WRITE IT about a corpus in which he never had. 2 guards close it: a
#: lookbehind requiring the `v` to begin a token, and a trailing word boundary
#: so "barely", "barrier", "bars" and "balls" cannot match. Pinned by
#: `check_the_regex_itself`, which fails if either guard is loosened.
TOKEN = re.compile(r"(?<![A-Za-z0-9])v[-_ ]?bars?\b", re.IGNORECASE)

#: Forms the decision MUST see, and forms it MUST NOT. The second list is the
#: operative one: every entry is a real false positive of the first version.
MUST_MATCH = ("v_bar", "v-bar", "vbar", "v bar", "What is v-bar?", "v_bars",
              "v_bar=0.90", "(v_bar)", "D_decay=0.10, v_bar=0.90, A=0.85")
MUST_NOT_MATCH = ("arXiv barely", "Wasserstein balls", "v barrier", "nav bar",
                  "env bars", "v barometer", "observ bar", "vocab barrier")

#: The prefilter, run on the RAW line, because the largest transcript is 760 MB
#: and cannot be JSON-decoded line by line at acceptable cost. Every string
#: TOKEN matches contains the literal substring "bar" in DECODED text, so the
#: only way the prefilter can lose a hit is a transcript spelling a letter as a
#: backslash-u-X-X-X-X escape. THAT IS CHECKED BY EXECUTION -- see `prefilter_is_lossless`.
#:
#: IT WAS CHECKED BY A HAND-WRITTEN PATTERN FIRST AND THE PATTERN WAS VACUOUS.
#: The intent was "does this line escape the letter b". What reached disk was
#: the 1-byte literal b'b', so it asked "does this line contain the letter b"
#: and fired on 375,433 of 375,433 lines -- printing a WARNING that made the
#: real finding look WEAKER than it is. 2 lessons, and the second is the
#: general one. The escape sequence did not survive being written to the file,
#: so the code that ran was not the code that was composed -- which is why the
#: sequence is spelled in prose above rather than as characters. And a predicate
#: nobody executed is not a check: running 2 forms against each other is.
PREFILTER = b"bar"

#: A question-shaped hit: the token and a question mark in the same text.
#: Deliberately LOOSE, because a narrow pattern tuned to the summary's exact
#: wording would find it by construction and find nothing else by construction.
QUESTIONISH = re.compile(r"\?")


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes.

    2 library names can be 1 route: `scipy` and `statsmodels` resolve to the
    identical verifier for a proportion test, so the canonical pair bought 0
    cross-checks. What matters is ROUTES PER QUANTITY -- Wilson from statsmodels
    against Wilson written out, and Clopper-Pearson from scipy's beta quantile
    against mpmath's regularized incomplete beta by bisection.

    The 3rd return value is the LARGER of the 2 disagreements, so a drift in
    either quantity surfaces in the single number the caller prints.
    """
    import math

    import mpmath
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        def _f(x):
            return mpmath.betainc(a, b, 0, x, regularized=True) - y
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(240):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if _f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def _text_of(entry: dict) -> str:
    """Flatten an entry's message content to text, whatever shape it carries.

    ★ THE QUEUE RECORD IS READ HERE TOO (2026-11-03 evening), AND NOT READING IT
    IS WHY THIS SCRIPT'S ORIGINAL VERDICT WAS WRONG. A message he types while a
    turn is already running is stored on an entry of type `queue-operation` with
    its text in a TOP-LEVEL `content` key and NO `message` dict at all. This
    function returned "" for every one of them, so the HIS partition could not
    contain them and the measurement reported 0 where the answer was 1.
    """
    if (entry.get("type") == "queue-operation"
            and entry.get("operation") == "enqueue"
            and isinstance(entry.get("content"), str)):
        return entry["content"]
    msg = entry.get("message")
    if isinstance(msg, str):
        return msg
    if not isinstance(msg, dict):
        return ""
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for b in c:
            if isinstance(b, dict):
                if isinstance(b.get("text"), str):
                    out.append(b["text"])
                elif isinstance(b.get("content"), str):
                    out.append(b["content"])
            elif isinstance(b, str):
                out.append(b)
        return "\n".join(out)
    return ""


def _partition(entry: dict) -> str:
    """HIS, SUMMARY or OTHER. The structural filter, not a keyword one.

    ★ THE 2nd RECORD IS ADMITTED TO `HIS` (2026-11-03 evening). `promptSource`
    is a sound marker for a message typed AT THE PROMPT and it is absent from a
    `queue-operation` entry entirely, so a mid-turn message of his fell through
    to OTHER -- counted, but not counted as his. That single omission inverted
    this script's verdict. The queue rule is applied FIRST only after the
    summary test, so a compaction summary can never be reclassified by it.
    """
    if entry.get("isCompactSummary") is True:
        return "SUMMARY"
    if (entry.get("type") == "queue-operation"
            and entry.get("operation") == "enqueue"
            and not entry.get("isMeta")):
        return "HIS"
    if (entry.get("promptSource") == "sdk"
            and not entry.get("isMeta")
            and not entry.get("isCompactSummary")):
        return "HIS"
    return "OTHER"


def check_the_regex_itself() -> dict:
    """Pin the decision regex both ways, so a loosening fails loudly.

    `execute-do-not-grep`: a comment claiming the regex is tight asserts only
    that the comment is consistent with itself. This CALLS it.
    """
    missed = [t for t in MUST_MATCH if not TOKEN.search(t)]
    spurious = [t for t in MUST_NOT_MATCH if TOKEN.search(t)]
    return {"missed": missed, "spurious": spurious,
            "ok": not missed and not spurious}


#: Transcripts at or under this size are decoded in FULL, with no prefilter, so
#: the prefilter can be compared against the thing it approximates.
LOSSLESS_CHECK_MAX_BYTES = 100 * 1024 * 1024


def prefilter_is_lossless() -> dict:
    """Run the scan WITH and WITHOUT the prefilter and compare the hit sets.

    This replaces a hand-written escape pattern that was vacuous. It is a
    strictly stronger statement: rather than counting a proxy for the one way
    the prefilter could fail, it decodes every line of 5 of the 6 transcripts
    and asks whether the prefiltered pass found the same hits as the exhaustive
    one. A disagreement is a REFUSAL, not a warning.
    """
    with_pf: set = set()
    without_pf: set = set()
    n_lines = n_bytes = 0
    for f in sorted(TRANSCRIPTS.glob("*.jsonl")):
        if f.stat().st_size > LOSSLESS_CHECK_MAX_BYTES:
            continue
        n_bytes += f.stat().st_size
        with f.open("rb") as fh:
            for i, raw in enumerate(fh):
                n_lines += 1
                saw_pf = PREFILTER in raw.lower()
                try:
                    e = json.loads(raw)
                except Exception:                            # noqa: BLE001
                    continue
                if not isinstance(e, dict):
                    continue
                txt = _text_of(e)
                if txt and TOKEN.search(txt):
                    without_pf.add((f.name, i))
                    if saw_pf:
                        with_pf.add((f.name, i))
    lost = without_pf - with_pf
    return {"lines": n_lines, "bytes": n_bytes, "files_checked": len(
        [f for f in TRANSCRIPTS.glob("*.jsonl")
         if f.stat().st_size <= LOSSLESS_CHECK_MAX_BYTES]),
        "hits_exhaustive": len(without_pf), "hits_prefiltered": len(with_pf),
        "lost": sorted(lost)[:5], "ok": not lost}


def scan_transcripts() -> dict:
    counts: collections.Counter = collections.Counter()
    hits: dict = {"HIS": [], "SUMMARY": [], "OTHER": []}
    files = sorted(TRANSCRIPTS.glob("*.jsonl"))
    scanned_bytes = 0
    for f in files:
        scanned_bytes += f.stat().st_size
        with f.open("rb") as fh:
            for raw in fh:
                low = raw.lower()
                if PREFILTER not in low:
                    continue
                try:
                    e = json.loads(raw)
                except Exception:                            # noqa: BLE001
                    continue
                if not isinstance(e, dict):
                    continue
                txt = _text_of(e)
                if not txt or not TOKEN.search(txt):
                    continue
                part = _partition(e)
                counts[part] += 1
                m = TOKEN.search(txt)
                lo = max(0, m.start() - 110)
                snip = " ".join(txt[lo:m.end() + 110].split())
                if len(hits[part]) < 6:
                    hits[part].append(
                        {"file": f.name[:8], "q": bool(QUESTIONISH.search(txt)),
                         "snip": snip})
    return {"files": len(files), "bytes": scanned_bytes, "counts": counts,
            "hits": hits}


def count_his_messages() -> int:
    """The DENOMINATOR for the HIS partition: every message he actually typed."""
    #: ★ THE PREFILTER WAS `b'"sdk"'` AND IT WAS A 2nd COPY OF THE SAME BUG.
    #: A prefilter must be provably WEAKER than the decision it approximates. A
    #: `queue-operation` entry contains no `"sdk"` anywhere, so this loop could
    #: not reach the branch `_partition` had just been taught, and the
    #: denominator would have stayed at 1,719 while the numerator moved. Both
    #: markers are admitted now, which is a strict superset of either.
    #: ★ THE DENOMINATOR COMES FROM THE SHARED READER (2026-11-03 evening), and
    #: the first correction here got it wrong in the opposite direction. Teaching
    #: `_partition` the queue record took this count from 1,719 to 5,463, because
    #: a raw row count counts a mid-turn message TWICE -- once queued, once
    #: absorbed -- and admits the task notifications the harness queues to
    #: itself. A denominator inflated by harness noise makes the rate meaningless
    #: in the flattering direction, which is the failure the project records as
    #: "ask what a 0 is a 0 OF".
    #:
    #: `scripts/his_messages.py` is the single reader for this question. It
    #: deduplicates across both records and excludes 7 named harness shapes, so
    #: the denominator is DISTINCT MESSAGES OF HIS: 1,421 as measured.
    import importlib.util                                    # noqa: PLC0415
    spec = importlib.util.spec_from_file_location(
        "_hm", REPO / "scripts" / "his_messages.py")
    hm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hm)
    return len(hm.distinct())


def scan_annotations() -> dict:
    """His annotated response files, read with the project's own reader."""
    sys.path.insert(0, str(REPO / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_rd", REPO / "scripts" / "read_founder_responses_2026-10-11.py")
    rd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rd)
    ann = rd.annotations()
    hits = [a for a in ann if TOKEN.search(str(a.get("text") or ""))]
    return {"n": len(ann), "k": len(hits),
            "sample": [str(a.get("text"))[:90] for a in hits[:4]]}


def main() -> int:
    argparse.ArgumentParser(
        description=("Measure whether the founder ever asked what `v_bar` is, "
                     "with the anti-vacuity control in the same corpus.")
    ).parse_args()

    print("=" * 78)
    print("DID HE EVER ASK WHAT `v_bar` IS? THE SUMMARY SAID SO.")
    print("=" * 78)

    rx = check_the_regex_itself()
    print("\nINSTRUMENT CHECK 1: is the decision regex tight?")
    print(f"  forms it must match, missed   : {rx['missed'] or 'none'}")
    print(f"  forms it must reject, matched : {rx['spurious'] or 'none'}")
    if not rx["ok"]:
        print("  REFUSED. The regex does not hold its own specification, so")
        print("  every count below is meaningless. This is exactly how the")
        print("  first version inverted its verdict on 'arXiv barely'.")
        return 1
    print("  => the regex holds both directions.")

    ll = prefilter_is_lossless()
    print("\nINSTRUMENT CHECK 2: does the raw prefilter lose any hit?")
    print(f"  {ll['files_checked']} transcript(s) decoded in FULL, "
          f"{ll['lines']} line(s), {ll['bytes'] / 1e6:.1f} MB")
    print(f"  hits found WITHOUT the prefilter : {ll['hits_exhaustive']}")
    print(f"  hits found WITH the prefilter    : {ll['hits_prefiltered']}")
    if not ll["ok"]:
        print(f"  REFUSED. The prefilter LOST {len(ll['lost'])} hit(s): "
              f"{ll['lost']}")
        return 1
    print("  => lossless on every line it was run against. Not a count of a")
    print("     proxy for the failure: the 2 forms were executed and agreed.")

    t = scan_transcripts()
    c = t["counts"]
    print(f"\nCORPUS: {t['files']} transcript(s), "
          f"{t['bytes'] / 1e6:.1f} MB scanned line by line.")

    n_his = count_his_messages()
    a = scan_annotations()

    print("\nTHE PARTITION, same regex and same decoder throughout:")
    print(f"  his genuinely typed messages      : {c['HIS']:5d} hit(s) "
          f"of {n_his} message(s)")
    print(f"  compaction summaries              : {c['SUMMARY']:5d} hit(s)"
          f"   <- the anti-vacuity control")
    print(f"  everything else (tools, my prose) : {c['OTHER']:5d} hit(s)")
    print(f"  his annotated response files      : {a['k']:5d} hit(s) "
          f"of {a['n']} annotation(s)")

    for part in ("SUMMARY", "HIS"):
        if t["hits"][part]:
            print(f"\n  sample from {part}:")
            for h in t["hits"][part]:
                print(f"    [{h['file']}] question-shaped={h['q']}")
                print(f"      {h['snip'][:150]}")

    print("\nINTERVALS. 2 denominators, so 2 intervals -- an interval belongs")
    print("to the denominator it was computed from and may not be reused.")
    for label, k, n in (("his typed messages", c["HIS"], n_his),
                        ("his annotations", a["k"], a["n"])):
        (wl, wh), (cl, ch), d = _iv(k, n)
        print(f"  {label:22s} {k} of {n}, {k / n if n else 0:.6f}")
        print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
        print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  "
              f"(2-route |diff| {d:.1e})")

    vacuous = c["SUMMARY"] == 0
    print()
    if vacuous:
        print("  REFUSED. The anti-vacuity control is 0, so the search found")
        print("  the token NOWHERE -- including where it is known to be. The")
        print("  claim is UNVERIFIED, not negative. Fix the search.")
        return 1

    found_in_his = c["HIS"] > 0 or a["k"] > 0
    print("  VERDICT:", "HE DID WRITE IT -- the summary was faithful."
          if found_in_his else
          "HE NEVER WROTE IT. The question is a SUMMARY ARTEFACT.")
    #: ★ THIS LINE USED TO READ "0 in anything he wrote" UNCONDITIONALLY, which
    #: contradicted the verdict printed immediately above it the moment the
    #: verdict flipped. A sentence that cannot change when its subject does is
    #: the stale-comment defect this project has recorded repeatedly, and here
    #: it sat 1 line below the thing it contradicted.
    print(f"  The control proves the search works: {c['SUMMARY']} hit(s) in")
    print(f"  summary-generated text, against {c['HIS']} in his own messages")
    print(f"  and {a['k']} in his annotations. Same regex throughout.")
    print()
    print("  SCOPE. This is about the QUESTION'S PROVENANCE only. `v_bar` is")
    print("  real, carries 0.350000 of the orchestrator role score, and is")
    print("  open for his ruling as entry B94 on the self-reported verified")
    print("  flag. Nothing here revises that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
