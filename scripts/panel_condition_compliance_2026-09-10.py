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
                                    disagreement section with a body, judged by
                                    `carries_disagreement`, the 1 definition the
                                    Section P guard also calls

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
#: The tracked mirror of the ignored log directory.
MIRROR = REPO / "experimental_notes" / "evidence"
#: The date Section P made a panel review a precondition on closing any entry.
RULING = "2026-09-09"

#: Cache and build artefacts are not deliverables.
CACHE = re.compile(r"__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.pyc$|\.db$")
#: A round is one directory holding at least 1 seat reply.
#: `ge` and `kimi` ADDED 2026-09-20, and their absence was a real blind spot
#: rather than a tidy-up.
#:
#: This list is the population every Section-P condition is measured over. It
#: read ("cc2", "fable", "cx", "cgpt", "ds"): the Gemini seat was missing from
#: the day this script was written, and the Kimi seat from the day it joined the
#: roster on 2026-09-20. So the compliance script counted 49 replies where the
#: guard, which globs the directory instead of consulting a list, counted 55 --
#: and `TestP5TheGuardIsNotVacuous` exists precisely to notice that the 2 are no
#: longer measuring the same thing. It fired correctly.
#:
#: THE SHARPER HALF IS BELOW: `PAID_SEATS` omitted the same 2, and BOTH of them
#: cost money -- `ge` rides OpenRouter and `kimi` is billed to the founder's
#: Moonshot credits. That list is the fallback the money guard uses when a reply
#: records no route at all, so for any such reply the guard could not see a
#: Gemini or Kimi dispatch. A money constraint the founder reserves to himself
#: was blind to 2 of the 5 paid seats.
#:
#: This is the "addition that nothing reaches" half of the additive standard,
#: in its most expensive form: the roster was extended to 7 seats and the
#: instrument that audits the roster still knew 5.
SEATS = ("cc2", "fable", "cx", "cgpt", "ds", "ge", "kimi")

#: Seats that cost money, per this project's own routing table: `cx` and `cgpt`
#: ride OpenRouter and `ds` is DeepSeek direct. Used ONLY as the fallback when a
#: reply records no route, never in place of a route the file actually carries.
#: `ge` and `kimi` ADDED 2026-09-20. `ge` is Gemini on OpenRouter and has been
#: paid since 2026-05-10, when the seat moved off the direct Google API; `kimi`
#: is billed to the founder's own Moonshot credits. Both were absent, so this
#: fallback -- the thing the money guard consults when a reply carries no route
#: field, which 20 of 30 paid-named files in the archive do not -- could not see
#: a Gemini or a Kimi dispatch at all.
PAID_SEATS = ("cx", "cgpt", "ds", "ge", "kimi")


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

    AND IT READ `bench/logs/` ONLY, which a clone does not have (2026-09-17,
    tasks P1, P3, P4, P5). In a clone this printed "paid seat replies AFTER
    2026-09-05: 0 across 0 directories" followed by "every round since is
    free-seat" -- a conclusion over an empty population. The population is now
    `archive_rounds()`: the live directory where it exists, the tracked mirror
    `experimental_notes/evidence/panel_records_*` everywhere else.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.archive_rounds()


def _round_date(d: pathlib.Path) -> str | None:
    """DELEGATED to the 1 module that decides. See `rounds()` for why."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.round_date(d.name)


#: The per-seat delivery layout introduced by A20's per-seat sandboxes.
SEAT_COPY_SUFFIX = ".as-the-seat-wrote-it.txt"


def source_files(d: pathlib.Path) -> list[str]:
    """Files a round DELIVERED, in either layout it has used.

    READ ONLY `seat_proposals.diff`, AND SO PRINTED A FALSE ZERO FOR ROUND 15
    (2026-09-17, task P4). Since per-seat sandboxes, a round can deliver as
    `<round>/seat_proposals/<name>.as-the-seat-wrote-it.txt`, 1 file per seat
    file, and `panel_round15_2026-09-11` did exactly that: its tracked mirror
    holds 4 such files and no diff, and this function returned 0 for it. The
    per-seat copies are read from the round directory itself AND from the
    tracked mirror of the same round, deduplicated by name. A `README.md` in
    that directory is the harvester's own note, not a seat's fix, and is not
    counted; a round whose only artefact is that README delivered nothing.
    """
    out: list[str] = []
    p = d / "seat_proposals.diff"
    if p.is_file():
        paths = [ln[4:].strip() for ln in p.read_text(errors="replace").splitlines()
                 if ln.startswith("### ")]
        out += [x for x in paths if not CACHE.search(x)]
    seat_dirs = [d / "seat_proposals"]
    seat_dirs += sorted(MIRROR.glob(f"panel_records_*/{d.name}/seat_proposals"))
    seen: set[str] = set()
    for sd in seat_dirs:
        if not sd.is_dir():
            continue
        for f in sorted(sd.iterdir()):
            if not f.is_file() or not f.name.endswith(SEAT_COPY_SUFFIX):
                continue
            name = f.name[:-len(SEAT_COPY_SUFFIX)]
            if name.lower() == "readme.md" or CACHE.search(name) or name in seen:
                continue
            seen.add(name)
            out.append(f"seat_proposals/{name}")
    return out


#: A reply preserves disagreement if it carries a section ABOUT disagreeing --
#: not if it contains one particular phrase.
#:
#: ONE DEFINITION, MOVED HERE 2026-09-17 (task P5). The Section P guard carried
#: this pattern and this script carried a private `_DISAGREE` matching only
#: `strongest[_ ]disagreement|where i disagree`. Under the ruling the guard
#: matched replies this script missed: `panel_roster_fix_2026-09-09` (cc2 and
#: fable) and
#: `panel_round16_2026-09-17` cc2, whose section is labelled `**disagreement**:`.
#: The guard now imports this object, so there is 1 rule and 2 callers.
#:
#: The history of the wording, kept from the guard: this matched
#: `strongest[_ ]disagreement` only, the wording of the round-4 output shape;
#: the round-8 brief asked for the same field as "WHERE I DISAGREE WITH THE
#: OTHER SEAT OR WITH CC1", both seats supplied it, and a literal-phrase guard
#: reported both as misses.
#: WIDENED 2026-09-20, AND IT WAS A PARSING DEFECT, NOT A MISSING RULE.
#:
#: The heading alternative read `disagreement\b`. The trailing `\b` CANNOT match
#: the plural: in "Disagreements" the character after "disagreement" is `s`,
#: a word character, so there is no boundary there and the alternative simply
#: fails. Every seat that titled its section "Disagreements" was recorded as
#: having preserved none. The pattern also had no room for a numbered heading,
#: so "## 7) Disagreements preserved" and "## 8. Disagreements preserved" missed
#: on a second, independent count.
#:
#: MEASURED against the 2026-09-20 rounds, whose replies were read in full and
#: DO carry the section: 4 false negatives -- ds r2 "## Disagreements",
#: cgpt r3 "## 8. Disagreements preserved", cx r3 "## 7) Disagreements
#: preserved", fable r3 "## Disagreements, preserved". Each was reported as a
#: round that "lost its disagreement" when the text was plainly there.
#:
#: This is the same shape as the 2 other parsing defects found the same day: a
#: producer and a consumer that disagree about a string, where each is
#: individually correct and neither can see the other. The rule was never
#: "singular only"; the brief asks for a disagreement section and does not
#: dictate its heading.
DISAGREEMENT_RE = re.compile(
    r"strongest[_ ]disagreements?"
    r"|where\s+i\s+disagree"
    r"|(?:^|\n)\s*#{0,4}\s*\**\s*(?:\d+[.)]\s*)?disagreements?\b"
    r"|i\s+disagree\s+with",
    re.I)

#: A body that DECLARES ABSENCE rather than stating a disagreement.
_NULL_BODY = re.compile(r"(?:none|nothing|n/?a|nil|no\s+disagreements?)", re.I)
_MARKUP = " \t*_`>#:|-—–"


def _is_label_line(line: str) -> bool:
    """A markdown heading, or a line that is only a bold label."""
    s = line.strip()
    return s.startswith("#") or (s.startswith("**") and s.rstrip(":").endswith("**"))


def _introduced_body(text: str, m: re.Match) -> str:
    """What a disagreement match introduces: its inline value, or the section body.

    An inline label (`strongest_disagreement: none`, `I disagree with nothing.`)
    is answered by the rest of its own line. A heading or bold label on a line
    of its own is answered by the next non-empty line, and an empty section --
    the next non-empty line is itself a heading, or there is none -- is empty.
    """
    line_start = text.rfind("\n", 0, m.end()) + 1
    eol = text.find("\n", m.end())
    eol = len(text) if eol < 0 else eol
    rest = text[m.end():eol]
    # A value after a colon or dash is the answer even on a heading line:
    # `## strongest_disagreement: none` declares absence, and
    # `## Disagreement - the brief is wrong` states one.
    after = re.match(r"^[\s*_`]*[:—–-][\s*_`]*(.*)$", rest)
    if after and after.group(1).strip(_MARKUP):
        return after.group(1).strip(_MARKUP)
    inline = rest.strip(_MARKUP)
    if inline and not _is_label_line(text[line_start:eol]):
        return inline
    # A SUB-HEADING IS STRUCTURE, NOT AN EMPTY SECTION (fixed 2026-09-20).
    #
    # This read `if ln.lstrip().startswith("#"): return ""` -- ANY following
    # heading made the body empty. The 2026-09-17 tightening that added it was
    # aimed at a genuinely empty section, where the next heading starts the NEXT
    # section at the same level. But a seat that writes
    #
    #     ## Disagreements
    #     ### With CC1
    #     None that survive verification. CC1's five results all hold...
    #     ### With the revision package
    #     ...
    #
    # has written a structured disagreement section, and this returned "" for it.
    # Measured on bench/logs/maths_panel_2026-09-20_r2/ds.json, whose section runs
    # to several hundred words under sub-headings and was recorded as a round
    # that "lost its disagreement".
    #
    # So the level decides: a heading DEEPER than the matched one is this
    # section's own content and we descend past it; a heading at the SAME or a
    # SHALLOWER level ends the section, and an end reached with no prose is the
    # empty section the tightening exists to catch.
    head = re.match(r"^\s*(#{1,6})\s", text[line_start:eol])
    level = len(head.group(1)) if head else 0
    for ln in text[eol + 1:].split("\n"):
        if not ln.strip():
            continue
        sub = re.match(r"^\s*(#{1,6})\s", ln)
        if sub:
            if level and len(sub.group(1)) > level:
                continue          # a sub-heading of this section: keep looking
            return ""             # the next section began: this one is empty
        return ln.strip(_MARKUP)
    return ""


def carries_disagreement(response: str) -> bool:
    """True iff the reply carries a disagreement section WITH A BODY.

    TIGHTENED 2026-09-17 (task P5). The bare pattern matched
    "strongest_disagreement: none", "I disagree with nothing." and a
    `## Disagreement` heading followed by "None." -- each a declared ABSENCE of
    disagreement, counted as disagreement preserved. A match now counts only if
    what it introduces is not empty and not a null word (none, nothing, n/a,
    nil, no disagreement).
    """
    for m in DISAGREEMENT_RE.finditer(response or ""):
        body = _introduced_body(response, m).strip(_MARKUP + ".!;,")
        if body and not _NULL_BODY.fullmatch(body):
            return True
    return False


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
        row = seat_row(d)
        n, calls, dis = row["n"], row["calls"], row["dis"]
        tool_ok += row["tool_ok"]
        disagree_ok += dis
        paid += row["paid"]
        paid_unknown_route += row["paid_unknown_route"]
        seatn += n
        src = source_files(d)
        if src:
            delivered.append((d.name, src))
        print(f"  {d.name:38s} {n:5d} {calls:11d} {len(src):10d} {dis:9d}")

    print("\nP3 — seats USED the harness (recorded tool calls > 0):")
    rep("seat replies with at least 1 recorded tool call", tool_ok, seatn)
    # THE BEFORE-AND-AFTER SPLIT THAT P3 QUOTES, PRINTED BY THE SCRIPT WHOSE
    # POPULATION IT IS (2026-09-17). Entry P3 cited 28 of 28 against 8 of 134,
    # Fisher p = 1.495245e-24, and no committed script printed any of it.
    for label, kw in (("live archive", {}),
                      ("AS RECORDED IN P3, rounds to 2026-09-11 without round 15",
                       P3_RECORDED)):
        ku, nu, kp, np_, p = p3_split(rs, **kw)
        print(f"\n  P3 split at the ruling {RULING}, {label}:")
        rep("under the ruling, replies with at least 1 tool call", ku, nu)
        rep("before the ruling, replies with at least 1 tool call", kp, np_)
        rep("overall", ku + kp, nu + np_)
        if nu and np_:
            p_mp = fisher_two_sided_mpmath(ku, nu - ku, kp, np_ - kp)
            print(f"      Fisher exact 2-sided p = {p:.6e} scipy | {p_mp:.6e} mpmath | "
                  f"agree rel 1e-6: {abs(p - p_mp) <= 1e-6 * max(p, p_mp)}")
            chi = sps.chi2_contingency([[ku, nu - ku], [kp, np_ - kp]], correction=True)
            print(f"      chi-square with Yates correction p = {chi.pvalue:.6e} scipy")
    print("\nP5 — no compelled convergence (each seat returns its own disagreement):")
    rep("seat replies carrying a disagreement section with a body", disagree_ok, seatn)
    under = [d for d in rs if (_round_date(d) or "") >= RULING]
    rep(f"of which under the ruling ({RULING} on)",
        sum(seat_row(d)["dis"] for d in under), sum(seat_row(d)["n"] for d in under))
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
    # THE INTERVAL P1 QUOTES, PRINTED BESIDE ITS COUNT (2026-09-17). P1 paired
    # "0 of the 24 directories" with the Wilson interval for 0 of 29; the
    # interval now comes from the same line as the denominator it belongs to.
    rep(f"directories dated after {_RULING_CUT} holding a paid seat file",
        sum(1 for d in after if any((d / f"{x}.json").is_file() for x in PAID_SEATS)),
        len(after))
    return 0


def seat_row(d: pathlib.Path) -> dict:
    """1 round's per-seat measurement. The table in `main()` prints exactly this.

    EXTRACTED FROM `main()` 2026-09-17 so a test can CALL the counting path the
    printed figures come from, rather than re-deriving them beside it: the P5
    guard compares this function's disagreement count against its own walk of
    the replies, and the 2 disagreed on named replies while each lived in its own
    loop. The body is the loop `main()` carried, unchanged except that the
    disagreement test is `carries_disagreement`.
    """
    row = {"n": 0, "calls": 0, "tool_ok": 0, "dis": 0,
           "paid": 0, "paid_unknown_route": 0}
    for s in SEATS:
        f = d / f"{s}.json"
        if not f.is_file():
            continue
        try:
            j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        row["n"] += 1
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
                row["paid"] += 1
        elif s in PAID_SEATS:
            row["paid_unknown_route"] += 1
        c = int(j.get("n_tool_calls") or 0)
        row["calls"] += c
        row["tool_ok"] += c > 0
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
        #
        # RETIRED 2026-09-17: the private
        # `_DISAGREE = r"strongest[_ ]disagreement|where i disagree"` that
        # lived here. It was a second definition beside the guard's, and the
        # 2 disagreed on named replies under the ruling. Replaced by
        # `carries_disagreement`, the 1 definition both now call; see
        # `DISAGREEMENT_RE` for the measurement.
        if carries_disagreement(j.get("response", "")):
            row["dis"] += 1
    return row


#: The population entry P3's before-and-after figures were measured over: every
#: round dated on or before 2026-09-11 except round 15, which did not exist yet.
#: Round 15 is NAMED because it shares 2026-09-11 with rounds 11 to 14, so no
#: date cut alone reproduces the recorded population; the date cut keeps every
#: later round -- 16, and any round run after it -- out of the recorded figure.
P3_RECORDED = {"as_of": "2026-09-11", "exclude": ("panel_round15_2026-09-11",)}


def p3_split(rs=None, ruling: str = RULING, exclude=(), as_of=None) -> tuple:
    """(k_under, n_under, k_pre, n_pre, fisher_p) over THIS script's population.

    ADDED 2026-09-17 (task P3). `k` counts per-seat replies (`SEATS` files, the
    same files `seat_row` counts) recording at least 1 tool call; `under` is a
    round dated on or after `ruling`, `pre` is everything else, undated
    directories included, which is how `main()` has always split them. `as_of`
    drops rounds dated after it, and `exclude` drops rounds by name.
    `fisher_p` is scipy's 2-sided Fisher exact test on
    [[k_under, n_under - k_under], [k_pre, n_pre - k_pre]], or None when either
    side is empty.
    """
    from scipy.stats import fisher_exact
    rs = rounds() if rs is None else rs
    ku = nu = kp = np_ = 0
    for d in rs:
        if d.name in exclude:
            continue
        if as_of is not None and (_round_date(d) or "") > as_of:
            continue
        row = seat_row(d)
        if (_round_date(d) or "") >= ruling:
            ku, nu = ku + row["tool_ok"], nu + row["n"]
        else:
            kp, np_ = kp + row["tool_ok"], np_ + row["n"]
    p = (float(fisher_exact([[ku, nu - ku], [kp, np_ - kp]]).pvalue)
         if nu and np_ else None)
    return ku, nu, kp, np_, p


def fisher_two_sided_mpmath(a: int, b: int, c: int, d: int) -> float:
    """Fisher's exact 2-sided p by direct hypergeometric summation, in mpmath.

    The cross-check for scipy's value. Sums the probability of every table with
    the observed margins whose probability does not exceed the observed one,
    with the same relative tolerance scipy applies (1 + 1e-7).
    """
    import mpmath as mp
    mp.mp.dps = 60
    r1, c1, n = a + b, a + c, a + b + c + d

    def prob(x):
        return mp.binomial(r1, x) * mp.binomial(n - r1, c1 - x) / mp.binomial(n, c1)

    obs = prob(a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    return float(mp.fsum(prob(x) for x in range(lo, hi + 1)
                         if prob(x) <= obs * (1 + mp.mpf("1e-7"))))


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    raise SystemExit(main())
