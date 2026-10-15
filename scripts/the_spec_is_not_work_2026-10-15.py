#!/usr/bin/env python3
"""The 4 defects that stop the project's own specification reaching a model, measured.

WHY THIS EXISTS. The founder's ruling of 2026-10-14, verbatim: *"7000 or so words
for a system prompt is hardly excessive for any modern model? Why should we need
to cut it at all? The whole point of measuring what our models can do and then
giving them exactly the kind of work they are best suited to, is that no resource
and no model's capabilities are wasted ... Where does cutting core system
directives come into that picture at all?"* And: *"as far as any caps have ever
existed, their intention was to never feed any model more work than they were
demonstrably able to handle ... There was never an intent as far as I recall to
applying this same reasoning to the core operational directives themselves."*

THE DISTINCTION HE DRAWS IS THE FIX. A cap on WORK is measured machinery serving
the routing ladder. A cap on SPECIFICATION is a silent spec loss. The 4 figures
below are the 4 places the code does not draw that line.

EVERY FIGURE HERE IS PRODUCED BY THIS SCRIPT, cross-verified by 2 tools where it
is computable, and every proportion carries a 95% interval.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import sympy as sp                                                 # noqa: E402
import z3                                                          # noqa: E402
import mpmath as mp                                                # noqa: E402
from scipy.stats import beta as scipy_beta                         # noqa: E402
from statsmodels.stats.proportion import proportion_confint         # noqa: E402

from bench.cdsfl_registry import composer as C                     # noqa: E402

CORE = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
OPER = REPO / "bench" / "directives" / "universal" / "cdsfl_operational.md"

DECOMPOSE_HARD_FLOOR_CHARS = 80_000          # reference_runner_v3.DECOMPOSE_HARD_FLOOR_CHARS


def interval(k: int, n: int) -> str:
    """Wilson by statsmodels and Clopper-Pearson by scipy — 2 tools, 1 claim."""
    if n == 0:
        return "n=0, no interval"
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_cp = 0.0 if k == 0 else float(scipy_beta.ppf(0.025, k, n - k + 1))
    hi_cp = 1.0 if k == n else float(scipy_beta.ppf(0.975, k + 1, n - k))
    return (f"{100.0 * k / n:.4f}%  Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%]"
            f"  Clopper-Pearson [{100*lo_cp:.4f}%, {100*hi_cp:.4f}%]")


def section_1_what_the_spec_is() -> dict:
    core = CORE.read_text(encoding="utf-8")
    oper = OPER.read_text(encoding="utf-8")
    core_blocks = C._split_packet_directives(core)
    hard_blocks = [b for b in core_blocks if C._block_is_hard(b)]
    print("=" * 78)
    print("1. WHAT THE SPECIFICATION IS, AND WHAT THE CAPS ARE MEASURED AGAINST")
    print("=" * 78)
    print(f"  core formal   {len(core):>7} chars  {len(core.split()):>6} words"
          f"  {len(core_blocks):>4} blocks  {len(hard_blocks):>3} HARD by the project's own predicate")
    print(f"  operational   {len(oper):>7} chars  {len(oper.split()):>6} words"
          f"  {len(C._split_packet_directives(oper)):>4} blocks")
    print(f"  TOGETHER      {len(core)+len(oper):>7} chars  {len(core.split())+len(oper.split()):>6} words")
    caps = {m: t.max_directive_chars for m, t in C.PHENOTYPE_TRANSFORMS.items()}
    print(f"\n  per-model max_directive_chars: {caps}")
    biggest = max(caps.values())
    over = sum(1 for c in caps.values() if len(core) > c)
    print(f"  models whose cap is below the core spec: {over} of {len(caps)} — {interval(over, len(caps))}")
    print(f"  the most generous cap is {biggest}; the spec is {len(core)}, "
          f"a factor of {len(core)/biggest:.4f}")
    return {"core": core, "oper": oper, "core_blocks": core_blocks,
            "hard_blocks": hard_blocks, "caps": caps}


def _pre_repair_minimal(core: str) -> str:
    """Reconstruct the PRE-REPAIR reduced form: policy keys + behavioural bullets.

    ★ IT IS RECONSTRUCTED, NOT READ FROM THE LIVE FUNCTION, AND THAT MATTERS.
    `_render_universal_minimal` has been repaired, so calling it returns the
    8,367-character faithful render and every "before" figure in this script
    would silently become a "after" figure. Measured when that happened: the
    reported system prompt "today" moved from 48,877 to 54,741 and the headroom
    loss from 25,300 to 19,436 characters -- a producer quietly ceasing to
    reproduce the numbers it was committed beside, which is the exact failure
    `measured-rate-travels-with-its-script` exists to prevent.

    The reconstruction is the pre-repair body verbatim: the flattened
    `universal.toml` policy, then the bullets of `## Non-Formalisable
    Directives`. It yields 2,503 characters, which is the figure the record
    carries.
    """
    policy = C._load_toml(C.REGISTRY_DIR / "universal.toml")
    lines = ["CDSFL CORE MINIMAL"]
    lines.extend(C._flatten_policy_items(policy, "policy"))
    for i, directive in enumerate(
        C._extract_hard_behavioural_directives(core), 1
    ):
        lines.append(f"behaviour.{i}={directive}")
    return "\n".join(lines)


def section_2_minimal_render_drops_hard(ctx: dict) -> None:
    print()
    print("=" * 78)
    print("2. DEFECT 1 — THE MINIMAL RENDER CLAIMS TO PRESERVE EVERY HARD CONSTRAINT")
    print("=" * 78)
    hard = ctx["hard_blocks"]
    before = _pre_repair_minimal(ctx["core"])
    after = C._render_universal_minimal()

    # VERBATIM CONTAINMENT, which is the only instrument that works here. A
    # first-8-words probe space-joins across newlines and cannot match a
    # multi-line block, and 9 of the 22 HARD blocks are multi-line: it reported
    # 1 of 22 for the pre-repair render where the honest figure is 0 of 22, and
    # 13 of 22 for the repaired one where the honest figure is 22 of 22.
    carried_before = sum(1 for b in hard if b in before)
    carried_after = sum(1 for b in hard if b in after)
    probe_after = sum(
        1 for b in hard
        if " ".join(b.split()[:8]).strip("#*-| ").lower() in after.lower()
    )

    print(f"  PRE-REPAIR reduced form (reconstructed): {len(before)} chars")
    print(f"    HARD blocks carried: {carried_before} of {len(hard)} — "
          f"{interval(carried_before, len(hard))}")
    print(f"  POST-REPAIR reduced form (live code):    {len(after)} chars")
    print(f"    HARD blocks carried: {carried_after} of {len(hard)} — "
          f"{interval(carried_after, len(hard))}")
    print(f"    the withdrawn first-8-words probe would say: {probe_after} of "
          f"{len(hard)} — understating by {carried_after - probe_after}")
    missing = [b.split("\n")[0][:84] for b in hard if b not in before]
    if missing:
        print("  EVERY HARD BLOCK THE PRE-REPAIR FORM DROPPED, UNFILTERED:")
        for m in missing:
            print(f"    - {m!r}")


def _pre_repair_resolve(packets):
    """The resolver as it stood BEFORE 2026-10-15, reconstructed.

    ★ RECONSTRUCTED FOR THE SAME REASON THE REDUCED FORM IS. The 2 guards added
    on 2026-10-15 -- a packet may not resolve against itself, and a HARD
    directive is recorded rather than deleted -- are UNCONDITIONAL, so the
    pre-repair behaviour is not reachable by any flag and the "40 of 42" figure
    cannot be reproduced from live code. Reconstructing it here keeps the figure
    producible, which is what `measured-rate-travels-with-its-script` requires
    of a number the record carries.

    This is the pre-repair body verbatim: priority sort, first-match conflict,
    delete the loser, no same-packet guard and no HARD exemption.
    """
    entries = []
    for pi, packet in enumerate(packets):
        for di, text in enumerate(C._split_packet_directives(packet.text)):
            hard = (packet.constraint_class == "HARD"
                    or C._block_is_hard(text))
            entries.append({
                "id": f"{packet.layer}:{packet.name}:{di}",
                "packet_index": pi, "packet": packet, "text": text,
                "hard": hard,
                "priority": (1 if hard else 0,
                             C._LAYER_PRIORITY.get(packet.layer, 0),
                             C._specificity_score(packet), -pi, -di),
            })
    entries.sort(key=lambda e: e["priority"], reverse=True)
    kept, conflicts = [], []
    for entry in entries:
        topic, stance = C._directive_topic_and_stance(entry["text"])
        if topic is None:
            kept.append(entry)
            continue
        losing = False
        for winner in kept:
            wt, ws = C._directive_topic_and_stance(winner["text"])
            if wt == topic and ws != stance:
                conflicts.append({
                    "topic": topic,
                    "winner_layer": winner["packet"].layer,
                    "winner_packet": winner["packet"].name,
                    "loser_layer": entry["packet"].layer,
                    "loser_packet": entry["packet"].name,
                    "loser_text": entry["text"],
                    "loser_hard": entry["hard"],
                })
                losing = True
                break
        if not losing:
            kept.append(entry)
    return conflicts


def section_3_resolver(ctx: dict) -> None:
    print()
    print("=" * 78)
    print("3. DEFECT 2 — THE RESOLVER RESOLVES THE SPECIFICATION AGAINST ITSELF")
    print("=" * 78)
    import collections
    domains = sorted(p.name for p in (REPO / "bench" / "directives").iterdir()
                     if p.is_dir() and p.name != "universal")
    cls = collections.Counter()
    hard_deleted = []
    post = {"conflicts": 0, "hard_deleted": 0, "packets_altered": 0}
    for domain in domains:
        packets = [C.DirectivePacket(layer="universal", name="cdsfl_core",
                                     text=ctx["core"], constraint_class="HARD", tags=set())]
        dp = C._load_domain_directive(domain, variant=None)
        if dp:
            packets.append(dp)
        packets.append(C._build_situation_packet(
            review_target="t.py", code_extracts="x = 1\n", verified_facts="",
            explicit_unknowns="", adversarial_brief="b", interaction_surface=""))
        prelim = C.ComposedDirectiveSet(
            packets=packets, rendered_text=C._render_directive_text(packets),
            policy={}, cid="probe", constraint_count=1, token_estimate=1,
            constraint_density=0.0, coherence_budget=0.02, pruned_soft=[],
            manifest={"model": "probe", "domain": domain})
        # PRE-REPAIR, reconstructed — the 2 guards are unconditional in live
        # code, so this is the only way the figure stays producible.
        for c in _pre_repair_resolve(packets):
            same_pkt = (c["winner_layer"] == c["loser_layer"]
                        and c["winner_packet"] == c["loser_packet"])
            cls["SAME-PACKET" if same_pkt else
                ("SAME-LAYER" if c["winner_layer"] == c["loser_layer"]
                 else "CROSS-LAYER")] += 1
            if c["loser_hard"]:
                hard_deleted.append((domain, c["loser_layer"], c["topic"],
                                     c["loser_text"].split("\n")[0][:76]))
        # POST-REPAIR, live code, same packets.
        _after, live = C.resolve_layer_conflicts(prelim)
        post["conflicts"] += len(live)
        post["hard_deleted"] += sum(
            1 for c in live if c.deleted and C._block_is_hard(c.loser_text))
        by_layer = {q.layer: q.text for q in _after.packets}
        post["packets_altered"] += sum(
            1 for q in packets if by_layer.get(q.layer) != q.text)
    total = sum(cls.values())
    print(f"  domains probed: {len(domains)}   conflicts recorded: {total}")
    for k in ("SAME-PACKET", "SAME-LAYER", "CROSS-LAYER"):
        print(f"    {k:<12} {cls[k]:>4}  {interval(cls[k], total)}")
    print(f"\n  the function's own docstring says it resolves conflicts "
          f'"between directives from different layers"')
    print(f"  so SAME-PACKET conflicts are outside its own stated contract: "
          f"{cls['SAME-PACKET']} of {total}")
    print(f"\n  DELETIONS WHOSE LOSER IS HARD BY THE PROJECT'S OWN PREDICATE: {len(hard_deleted)}")
    for row in hard_deleted:
        print(f"    {row[0]:<22}{row[1]:<10}topic={row[2]:<10}{row[3]!r}")
    print("\n  AFTER THE REPAIR, live code over the same packets:")
    print(f"    conflicts recorded : {post['conflicts']}")
    print(f"    HARD deletions     : {post['hard_deleted']}")
    print(f"    packets altered    : {post['packets_altered']}")


def section_4_decomposition(ctx: dict) -> None:
    print()
    print("=" * 78)
    print("4. DEFECT 3 — THE DECOMPOSITION DECISION COUNTS A PAYLOAD IT CANNOT SPLIT")
    print("=" * 78)
    # PRE-REPAIR, reconstructed — see `_pre_repair_minimal`. Calling the live
    # function here would report the repaired render as the baseline and this
    # whole section would silently measure nothing.
    spec_now = len(_pre_repair_minimal(ctx["core"])) + len(ctx["oper"])
    spec_full = len(ctx["core"]) + len(ctx["oper"])
    print(f"  system prompt BEFORE (reduced core + operational): {spec_now} chars")
    print(f"  system prompt AFTER  (spec delivered whole):       {spec_full} chars")
    print(f"  added by the repair:                               {spec_full - spec_now} chars")
    head_now = DECOMPOSE_HARD_FLOOR_CHARS - spec_now
    head_new = DECOMPOSE_HARD_FLOOR_CHARS - spec_full
    print(f"\n  work headroom before the {DECOMPOSE_HARD_FLOOR_CHARS} hard floor:")
    print(f"    before           {head_now:>7} chars")
    print(f"    after the repair {head_new:>7} chars")
    print(f"    lost             {head_now - head_new:>7} chars"
          f"  ({100.0*(head_now-head_new)/head_now:.4f}% of today's headroom)")

    # z3: is a 20,000-char work payload below the floor, before and after?
    W = z3.Int("W")
    s_now, s_new = z3.IntVal(spec_now), z3.IntVal(spec_full)
    for name, S in (("today", s_now), ("after the repair", s_new)):
        solver = z3.Solver()
        solver.add(W == 20_000, S + W > DECOMPOSE_HARD_FLOOR_CHARS)
        print(f"    z3: a 20,000-char work payload force-decomposes {name}? "
              f"{solver.check()}")

    # SymPy + z3: decomposition RE-SENDS the system prompt per chunk, so counting
    # the system prompt triggers a mechanism that multiplies it.
    S, Wsym, n = sp.symbols("S W n", positive=True, integer=True)
    monolithic = S + Wsym
    decomposed = (n + 1) * S + Wsym          # n chunk turns + 1 synthesis turn
    delta = sp.simplify(decomposed - monolithic)
    print(f"\n  SymPy: total bytes decomposed minus monolithic = {delta}")
    print(f"         positive for every n >= 1 and S > 0: "
          f"{sp.simplify(delta.subs({n: 1})) > 0}")
    sv, wv, nv = z3.Ints("Sv Wv nv")
    s2 = z3.Solver()
    s2.add(sv > 0, wv > 0, nv >= 1, (nv + 1) * sv + wv <= sv + wv)
    print(f"  z3:    'decomposing sends no more system-prompt bytes' is {s2.check()}")
    # mpmath third check on the concrete case
    mp.mp.dps = 30
    conc = mp.mpf((2 + 1) * spec_full + 20_000) - mp.mpf(spec_full + 20_000)
    print(f"  mpmath: at n=2 and the repaired spec, decomposing adds "
          f"{int(conc)} system-prompt chars ({2 * spec_full} expected)")


def main() -> int:
    ctx = section_1_what_the_spec_is()
    section_2_minimal_render_drops_hard(ctx)
    section_3_resolver(ctx)
    section_4_decomposition(ctx)
    print()
    print("=" * 78)
    print("NOTHING IS CHANGED BY THIS SCRIPT. It reads the live composer and reports.")
    print("=" * 78)
    return 0


def _answer_help_without_measuring(doc: str) -> None:
    """A `--help` MUST NEVER COST ANYTHING, and that is a founder-standing rule:
    15 of 17 runners once billed a live dispatch on any unrecognised argument.
    This script's measurement is free, but the rule is about the SHAPE: a flag
    that silently runs the whole measurement is indistinguishable from a flag
    that silently spends. Guarded by
    `bench/tests/test_help_is_answered_2026-09-11.py`.
    """
    import argparse
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=(doc or "").strip().splitlines()[0] if doc else None,
        epilog="Takes no arguments: run it with none to produce the measurement.",
    )
    ap.parse_args()


if __name__ == "__main__":
    _answer_help_without_measuring(__doc__)
    raise SystemExit(main())
