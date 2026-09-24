#!/usr/bin/env python3
"""Is the FFAFP detector ALIVE, and what is it measuring? A committed answer to both.

WHY THIS EXISTS. On 2026-09-22 the detector was found to have recorded nothing since
2026-09-20 while exiting 0 on every invocation. Its `--survey` mode looked perfectly
healthy throughout, because `survey()` walks a transcript from a FRESH state dict
(`{"offset": 0, "open": None, ...}`) while the hook walks it from the state PERSISTED
on disk. Only the persisted path could carry the poison, so the instrument's own
self-report could not see the instrument's own death. That is the false-negative shape
this project recorded when 16 of 17 panel tool calls errored and were read as results.

WHAT DISTINGUISHES THE TWO SILENCES. "Nothing missing because healthy" and "nothing
missing because dead" are identical in the verdict and differ in exactly one
mechanically checkable fact: a live detector's byte offset ADVANCES as the transcript
grows, and its history gains entries. This script asserts that against the live state
file, and reports the FFAFP trace rates alongside, so no figure in any panel reply has
to be quoted from an uncommitted script.

    python3 scripts/ffafp_liveness_check_2026-09-22.py            # newest session
    python3 scripts/ffafp_liveness_check_2026-09-22.py <session-id>

Exit 0 = alive. Exit 1 = STALE: the detector is not recording and its verdicts, clean
or otherwise, are ABSENT EVIDENCE rather than evidence of absence.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import sys

STATE_DIR = pathlib.Path.home() / ".claude" / ".ffafp_audit"
PROJECTS = pathlib.Path.home() / ".claude" / "projects"

#: Bytes of unconsumed transcript above which the detector is declared STALE. A live
#: hook consumes to EOF on every prompt, so the healthy value is a few kB at most --
#: whatever the harness wrote between the scan and the stat. The frozen detector was
#: 26.0 MB behind when it was found. 1 MB sits far above the former and far below the
#: latter, and the run that found the defect measured 6.40 s to parse 196.4 MB, so a
#: backlog is never explained by the hook being slow.
LAG_LIMIT = 1 << 20


def _ts(entry):
    return (entry or {}).get("ts") or ""


def newest_session():
    best, best_m = None, -1.0
    for p in PROJECTS.glob("*/*.jsonl"):
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if m > best_m:
            best, best_m = p, m
    return best


def transcript_for(sid: str):
    for p in PROJECTS.glob("*/%s.jsonl" % sid):
        return p
    return None


def survey_rates(tpath: pathlib.Path) -> dict:
    """Trace rates, taken from the HOOK'S OWN walk rather than a second copy of it.

    A survey that re-implemented the scan could agree with itself while disagreeing
    with the hook; this project has found 4 defects of exactly that shape.
    """
    import importlib.util
    hook = pathlib.Path.home() / ".claude" / "hooks" / "ffafp_audit.py"
    repo = pathlib.Path(__file__).resolve().parents[1] / "hooks" / "ffafp_audit.py"
    src = repo if repo.is_file() else hook
    spec = importlib.util.spec_from_file_location("ffafp_live", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    st = mod.survey([str(tpath)])
    out = {"source": str(src), "work": st.get("work", 0), "code": st.get("code", 0)}
    # Key names are taken from `survey()` itself. An earlier draft of this script
    # invented them and printed "P-PASS missing: 0 of 168 = 0.0%" against the hook's
    # own 115 of 168, because `st.get(key, 0)` returns 0 for a key that is not there.
    # A silent 0 from a typo'd lookup is the same failure this whole file is about, so
    # the lookup is now strict and a missing key raises.
    for key in ("miss_ppass", "stem", "miss_follow", "miss_analyse"):
        k = st[key]
        n = st["code"] if key == "miss_ppass" else st["work"]
        p, lo, hi = mod.wilson(k, n)
        out[key] = {"k": k, "n": n, "p": p, "lo": lo, "hi": hi,
                    "vacuous": k in (0, n)}
    return out


def main() -> int:
    sid = sys.argv[1] if len(sys.argv) > 1 else None
    tpath = transcript_for(sid) if sid else newest_session()
    if tpath is None:
        print("no transcript found")
        return 1
    sid = tpath.stem
    sf = STATE_DIR / sid
    print("session    : %s" % sid)
    print("transcript : %s (%.1f MB)" % (tpath, tpath.stat().st_size / 1e6))

    if not sf.is_file():
        print("LIVENESS   : STALE -- no state file. The hook has never run for this session.")
        return 1
    st = json.loads(sf.read_text())
    size = tpath.stat().st_size
    lag = size - int(st.get("offset", 0) or 0)
    hist = st.get("history") or []
    last = _ts(hist[-1]) if hist else ""
    print("offset     : %d of %d  (lag %.1f MB)" % (st.get("offset", 0), size, lag / 1e6))
    print("history    : %d entries, last %s" % (len(hist), last or "NEVER"))
    print("open turn  : %s" % (_ts(st.get("open")) or "none"))
    if st.get("last_error"):
        print("last error : %s" % st["last_error"])
    if st.get("recovered"):
        print("recovered  : %d time(s) -- turns before each recovery were FORFEIT"
              % st["recovered"])

    stale = lag > LAG_LIMIT
    print("LIVENESS   : %s" % ("STALE -- verdicts are ABSENT EVIDENCE, not evidence of "
                               "absence" if stale else "ALIVE"))

    r = survey_rates(tpath)
    print("survey via : %s" % r.pop("source"))
    print("work turns : %d   code-touching: %d" % (r.pop("work"), r.pop("code")))
    for key, lab in (("miss_ppass", "P-PASS missing"), ("stem", "STEM tool used"),
                     ("miss_follow", "FOLLOW missing"),
                     ("miss_analyse", "ANALYSE missing")):
        d = r[key]
        print("  %-16s: %d of %d = %.1f%%  95%% Wilson [%.1f%%, %.1f%%]%s"
              % (lab, d["k"], d["n"], 100 * d["p"], 100 * d["lo"], 100 * d["hi"],
                 "  <-- VACUOUS" if d["vacuous"] else ""))
    return 1 if stale else 0


if __name__ == "__main__":
    # WIRED 2026-09-24 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help
    # takes_no_arguments=False: this script TAKES a session id. Wiring it
    # with the default on 2026-09-24 made that argument unreachable -- the
    # SAME defect fixed in panel_harvest_loss_2026-09-22.py an hour earlier,
    # repeated. A help guard must not eat a real argument.
    answer_help(__doc__, __file__, takes_no_arguments=False)
    sys.exit(main())
