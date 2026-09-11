#!/usr/bin/env python3
"""Section P: do the panel rounds actually meet the founder's conditions?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE CONDITIONS ARE HIS, verbatim, 2026-09-09: *"In all cases and with all fixes
always check them with Fable and CC2 in full CDSFL panel review format (so not
just some simple open ended prompt), they must use whatever aspects of the
harness are currently working, including our mathematical model and all relevant
mechanics in the formation of their answers/fixes, as should you."*

Section P restates that as P1 to P7. Entries P1, P3, P4 and P5 have sat at
PROPOSED since, with no measurement of whether the rounds actually satisfy them.
This measures it from the archived seat records rather than asserting it.

WHAT EACH CLAUSE IS CHECKED BY, and none of it is a word search of the brief.

  P1  full CDSFL format          -- the dispatcher carries the formal schema, and
                                    the brief passed the validator before dispatch
  P3  seats USE the harness      -- recorded tool calls per seat, from the tool
                                    logs the dispatcher writes, not from claims
  P4  seats PRODUCE and TEST     -- source files the seat left in the sandbox,
                                    which is the only delivery the harness keeps
  P5  no compelled convergence   -- each seat returning its own verdict AND a
                                    strongest_disagreement section

P4 IS THE HARD ONE AND IT IS WHY THIS EXISTS. A seat can describe a fix at any
length. Only a file it leaves behind is a delivered fix, because
`panel_sandbox.teardown` destroys everything else.
"""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Cache and build artefacts are not deliverables.
CACHE = re.compile(r"__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.pyc$|\.db$")
#: A round is one directory holding at least 1 seat reply.
SEATS = ("cc2", "fable", "cx", "cgpt", "ds")

#: Seats that cost money, per this project's own routing table: `cx` and `cgpt`
#: ride OpenRouter and `ds` is DeepSeek direct. Used ONLY as the fallback when a
#: reply records no route, never in place of a route the file actually carries.
PAID_SEATS = ("cx", "cgpt", "ds")


def rounds() -> list[pathlib.Path]:
    """Every directory holding review output, selected by CONTENT.

    IT GLOBBED `panel_*` AND CALLED THE RESULT "every round", and the figure
    that carried was a COST one. Measured 2026-09-11: `panel_*` matches 46
    directories; 78 hold a seat reply or a BRIEF.md. The other 32 are the
    `confer_*`, `severity_*`, `track_record_*`, `bugzilla_*`, `independent_*`,
    `perturbation_*`, `canary_*`, `convergence_*`, `repair_loop_*` and `pr_*`
    reviews -- and 12 of them hold PAID replies. So the line
    "paid seat replies across every round: 10" was a statement about 46 of 78
    directories, and the archive-wide figure is **30 across 16 directories**.
    The CONCLUSION is unchanged -- the latest is 2026-09-05 and 0 of the 29
    directories dated after it hold one -- but a cost-control number quoted as
    covering everything while covering 59% of it is the class this project
    refuses, and cost is the category the founder reserves to himself.

    The predicate is IMPORTED rather than reimplemented: 2 definitions of
    "a review record" is the shape `execute-do-not-grep` names, and this file
    and the mirror would drift apart the moment a new naming convention landed.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(d for d in LOGS.iterdir() if mod.holds_review_output(d))


_D_DASH = re.compile(r"(20\d\d-\d\d-\d\d)")
_D_COMPACT = re.compile(r"(20\d{6})T\d{6}Z")


def _round_date(d: pathlib.Path) -> str | None:
    """The run's date from its own directory name, both conventions."""
    m = _D_DASH.search(d.name)
    if m:
        return m.group(1)
    c = _D_COMPACT.search(d.name)
    if c:
        g = c.group(1)
        return f"{g[0:4]}-{g[4:6]}-{g[6:8]}"
    return None


def source_files(d: pathlib.Path) -> list[str]:
    p = d / "seat_proposals.diff"
    if not p.is_file():
        return []
    paths = [ln[4:].strip() for ln in p.read_text(errors="replace").splitlines()
             if ln.startswith("### ")]
    return [x for x in paths if not CACHE.search(x)]


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sps
    import mpmath as mp

    def rep(label, k, n):
        if not n:
            print(f"  {label}: no denominator")
            return
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        mp.mp.dps = 30
        z = mp.mpf(str(sps.norm.ppf(0.975)))
        p, N = mp.mpf(k) / n, mp.mpf(n)
        cc = (p + z**2 / (2 * N)) / (1 + z**2 / N)
        h = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
        agree = abs(w[0] - float(cc - h)) < 1e-9
        print(f"  {label}: {k} of {n} = {k / n:.4%}")
        print(f"      Wilson [{w[0]:.4%}, {w[1]:.4%}] statsmodels | "
              f"[{float(cc - h):.4%}, {float(cc + h):.4%}] mpmath | agree 1e-9: {agree}")
        print(f"      Clopper-Pearson [{c[0]:.4%}, {c[1]:.4%}]")

    rs = rounds()
    print(f"panel rounds with at least 1 seat reply: {len(rs)}\n")
    print(f"  {'round':38s} {'seats':>5} {'tool calls':>11} {'src files':>10} {'disagree':>9}")
    tool_ok = disagree_ok = seatn = 0
    delivered = []
    paid = 0
    paid_unknown_route = 0
    for d in rs:
        calls = 0
        n = 0
        dis = 0
        for s in SEATS:
            f = d / f"{s}.json"
            if not f.is_file():
                continue
            try:
                j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            n += 1
            # AN ABSENT ROUTE IS UNKNOWN, NOT FREE.
            #
            # This read `j.get("route") and j["route"] != "claude_cli"`, so a
            # reply with no route field counted as free. Measured 2026-09-11
            # over every paid-named seat file in the archive: **20 of 30 record
            # no route at all -- 66.6667%, Wilson [48.7801%, 80.7695%],
            # Clopper-Pearson [47.1880%, 82.7126%]** -- every one of them a
            # `confer_*` or `track_record_pr_*` run from the older harness,
            # which did not write the field. They are paid: this project's own
            # routing table makes `cx` and `cgpt` OpenRouter and `ds` DeepSeek
            # direct. So the cost figure read 10 where the archive holds 30.
            #
            # A missing field read as the SAFE value is a false zero pointing
            # the wrong way, and the wrong way here is spending. Task A5 already
            # settled the principle for the containment alarm: an unrecognised
            # case counts as the dangerous one, because under-reporting is worse
            # than over-reporting. Seat identity is the fallback, and the 2
            # populations are reported separately so neither hides the other.
            if j.get("route"):
                if j["route"] != "claude_cli":
                    paid += 1
            elif s in PAID_SEATS:
                paid_unknown_route += 1
            c = int(j.get("n_tool_calls") or 0)
            calls += c
            tool_ok += c > 0
            # BOTH FIELD NAMES, AND MATCHING ONLY THE FIRST WAS A FALSE ZERO
            # IN A FOUNDER-CONDITION COMPLIANCE FIGURE.
            #
            # The brief asked for `strongest_disagreement` up to round 7 and for
            # "WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1" from round 8.
            # Measured 2026-09-11 across the 28 seat replies dispatched under the
            # ruling: 12 carry the old name, 14 the new, 2 neither -- and the 2
            # are `panel_roster_fix_2026-09-09`, which the task list already
            # identifies as the only round dispatched before the field existed at
            # all. 28 of 28 discuss disagreement in prose.
            #
            # So a scan for the old name alone reports 12 of 28 = 42.8571% and
            # FALLING, when the truth is 26 of 28 = 92.8571% and the decline is a
            # RENAME. P5 is a founder condition -- no compelled convergence --
            # and an instrument that reads a renamed field as non-compliance
            # would have had the panel appearing to abandon it.
            _DISAGREE = r"strongest[_ ]disagreement|where i disagree"
            if re.search(_DISAGREE, j.get("response", ""), re.I):
                dis += 1
                disagree_ok += 1
        seatn += n
        src = source_files(d)
        if src:
            delivered.append((d.name, src))
        print(f"  {d.name:38s} {n:5d} {calls:11d} {len(src):10d} {dis:9d}")

    print("\nP3 — seats USED the harness (recorded tool calls > 0):")
    rep("seat replies with at least 1 recorded tool call", tool_ok, seatn)
    print("\nP5 — no compelled convergence (each seat returns its own disagreement):")
    rep("seat replies carrying a strongest_disagreement", disagree_ok, seatn)
    print("\nP4 — seats DELIVERED a fix as a file, not as prose:")
    rep("rounds that returned at least 1 source file", len(delivered), len(rs))
    _SHOW = 6
    for name, src in delivered:
        print(f"      {name}: {len(src)} file(s)")
        for x in src[:_SHOW]:
            print(f"          {x}")
        if len(src) > _SHOW:
            # Naming the remainder, because a capped listing that stays silent
            # reads as the whole set.
            print(f"          ... {len(src) - _SHOW} more not shown")

    # BOTH FIGURES, SO NEITHER CAN BE QUOTED ALONE. The archive-wide count is
    # the honest total; the post-ruling count is what the ruling is about. The
    # first version printed only a total, over a population that was not "every
    # round", and called it "across every round".
    _RULING_CUT = "2026-09-05"
    after = [d for d in rs if (_round_date(d) or "") > _RULING_CUT]
    paid_after = sum(
        1 for d in after for x in PAID_SEATS if (d / f"{x}.json").is_file())
    total_paid = paid + paid_unknown_route
    print(f"\nCOST CONTROL — paid seat replies, WHOLE ARCHIVE: {total_paid} "
          f"across {len(rs)} review directories")
    print(f"               of which the reply itself records a paid route: {paid}")
    print(f"               and {paid_unknown_route} record NO route and are "
          f"counted paid by seat identity")
    print(f"COST CONTROL — paid seat replies AFTER {_RULING_CUT}: {paid_after} "
          f"across {len(after)} directories")
    if not paid_after:
        print("               (the latest paid dispatch is on or before "
              f"{_RULING_CUT}; every round since is free-seat)")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    raise SystemExit(main())
