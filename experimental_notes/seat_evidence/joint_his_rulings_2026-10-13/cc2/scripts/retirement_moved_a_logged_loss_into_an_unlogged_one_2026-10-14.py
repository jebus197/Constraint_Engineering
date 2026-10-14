# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: bedd2c0961c2b277a8f193ddd47980576fa3b8618a9ba16a0654d2129b977104
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""J1 producer, 2026-10-14 joint round: the composition-level interaction.

WHAT THIS MEASURES, AND WHY IT IS NOT THE RETIREMENT MEASUREMENT

`scripts/retiring_the_pruner_dominates_2026-10-13.py` measured ONE loss mode:
a domain directive deleted outright by `_prune_for_coherence` (10 of 50
compositions with the flag on, 0 of 50 with it off). That figure is reproduced
here and is not disputed.

This script measures a SECOND loss mode the retirement figure cannot see,
because it is not a lost packet -- it is a lost SUFFIX of a kept packet:

  bench/cdsfl_registry/composer.py:1439-1443
      if len(rendered) > transform.max_directive_chars:
          rendered = rendered[: transform.max_directive_chars] + "...truncated..."

That cap applies to the FINAL rendered text, AFTER pruning. Packet order in
`compose` is universal, domain, situation (composer.py:1333-1384), so the cap
cuts from the TAIL -- the situation layer, which carries `review_target`,
`code_extracts` and `adversarial_brief`: the per-dispatch payload.

The interaction, as a causal chain:
  1. `coherence_pruning=False` (retired default, composer.py:1306) keeps every
     SOFT packet, so `rendered` is strictly LONGER than with the pruner on.
  2. A longer `rendered` crosses `max_directive_chars` on more compositions, so
     the cap at :1439 drops more characters.
  3. `_prune_for_coherence`'s deletions were RECORDED in `pruned_soft` and
     carried into `manifest["pruned_soft"]` (composer.py:1465). The cap's
     deletion is recorded NOWHERE in the manifest: `pruned_soft` is [], and no
     field states how many characters the cap removed.

So the retirement is right on its own named property AND moves a logged loss
into an unlogged one -- a sec.10 category-4 exposure (silent evidence loss)
arising only from the COMPOSITION of two individually-correct changes.

Two independent tools on every number: the live `compose()` on the real
directive tree is the PRODUCER; a recomputation from the returned
`manifest["packets"]` char counts is the independent CONSUMER, and the script
reports whether they agree on whether the cap fired. Every proportion carries a
95% Wilson interval computed twice (statsmodels, and a hand-derived Wilson in
mpmath).

Run:  python3 scripts/retirement_moved_a_logged_loss_into_an_unlogged_one_2026-10-14.py
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

TRUNC_MARKER = "[... truncated for model capacity]"

# A situation packet of realistic size. A real dispatch carries the review
# target plus code extracts plus an adversarial brief; this is a deliberately
# MODEST stand-in (40 lines), so these figures are a LOWER bound.
CODE_EXTRACT = "\n".join(
    "    line_%03d = compute_residual(entry_%d, budget=0.0%d)" % (i, i, i % 9 + 1)
    for i in range(40)
)


def wilson_statsmodels(k, n):
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return float(lo), float(hi)


def wilson_mpmath(k, n):
    """Hand-derived Wilson score interval, independent of statsmodels."""
    import mpmath as mp
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    n_ = mp.mpf(n)
    p = mp.mpf(k) / n_
    denom = 1 + z**2 / n_
    centre = (p + z**2 / (2 * n_)) / denom
    half = (z * mp.sqrt(p * (1 - p) / n_ + z**2 / (4 * n_**2))) / denom
    return float(centre - half), float(centre + half)


def main():
    ap = argparse.ArgumentParser(
        description=("J1: measure what the final max_directive_chars cap removes "
                     "under coherence_pruning ON vs OFF, and whether it is logged."))
    ap.parse_args()

    from bench.cdsfl_registry import composer as C
    from bench.cdsfl_registry.composer import PHENOTYPE_TRANSFORMS, compose
    from bench.cdsfl_registry.registry import DOMAIN_MAP

    models = list(PHENOTYPE_TRANSFORMS)
    domains = sorted(DOMAIN_MAP) if DOMAIN_MAP else ["software"]

    print("=" * 78)
    print("J1 -- THE RETIREMENT x TRANSPORT-CAP INTERACTION")
    print("=" * 78)
    print("models  : %s" % models)
    print("domains : %s" % domains)
    print("situation code-extract payload: %d chars" % len(CODE_EXTRACT))
    print()

    uni = (C.DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md").read_text(
        encoding="utf-8")
    print("cdsfl_core_formal.md on disk : %d chars" % len(uni))
    for m in models:
        t = PHENOTYPE_TRANSFORMS[m]
        u = C._load_universal_directive(model=m)
        print("  %-16s cap=%6d universal_delivered=%5d room_for_rest=%6d"
              % (m, t.max_directive_chars, len(u.text),
                 t.max_directive_chars - len(u.text)))
    print()

    rows = []
    for m in models:
        for d in domains:
            rec = {"model": m, "domain": d}
            for arm, flag in (("on", True), ("off", False)):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    cs = compose(
                        task_domain=d, model=m,
                        review_target="bench/dm/_convergence.py",
                        code_extracts=CODE_EXTRACT,
                        adversarial_brief=("Assume the convergence predicate is "
                                           "wrong and find the input proving it."),
                        coherence_pruning=flag)
                rendered = cs.rendered_text
                cap_fired_producer = rendered.endswith(TRUNC_MARKER)
                pkt_chars = sum(p["chars"] for p in cs.manifest["packets"])
                cap = PHENOTYPE_TRANSFORMS[m].max_directive_chars
                cap_fired_consumer = pkt_chars > cap
                payload_tail = CODE_EXTRACT.strip().splitlines()[-1].strip()
                rec[arm] = {
                    "chars": len(rendered),
                    "cap_fired": cap_fired_producer,
                    "cap_fired_consumer": cap_fired_consumer,
                    "agree": cap_fired_producer == cap_fired_consumer,
                    "pruned_soft": list(cs.pruned_soft),
                    "cap_dropped_lb": max(pkt_chars - cap, 0),
                    "situation_present": any(
                        p["layer"] == "situation" for p in cs.manifest["packets"]),
                    "domain_present": any(
                        p["layer"] == "domain" for p in cs.manifest["packets"]),
                    "payload_intact": payload_tail in rendered,
                }
            rows.append(rec)

    print("-" * 78)
    print("PER-COMPOSITION, BOTH ARMS")
    print("-" * 78)
    print("%-16s %-12s | %8s %3s %6s %3s | %9s %3s %6s %3s"
          % ("model", "domain", "ONchars", "cap", "logged", "pay",
             "OFFchars", "cap", "logged", "pay"))
    for r in rows:
        on, off = r["on"], r["off"]
        print("%-16s %-12s | %8d %3s %6d %3s | %9d %3s %6d %3s"
              % (r["model"], r["domain"],
                 on["chars"], "Y" if on["cap_fired"] else "n",
                 len(on["pruned_soft"]), "Y" if on["payload_intact"] else "N",
                 off["chars"], "Y" if off["cap_fired"] else "n",
                 len(off["pruned_soft"]), "Y" if off["payload_intact"] else "N"))
    print()
    print("cap    = cap at composer.py:1439 fired (rendered ends in the marker)")
    print("logged = len(manifest['pruned_soft']): the ONLY record of lost text")
    print("pay    = last line of the dispatch code extract survived")
    print()
    disagree = [r for r in rows if not r["on"]["agree"] or not r["off"]["agree"]]
    print("PRODUCER vs CONSUMER on 'did the cap fire': %d/%d rows disagree"
          % (len(disagree), len(rows)))
    for r in disagree[:6]:
        print("   %s/%s on=%s/%s off=%s/%s"
              % (r["model"], r["domain"], r["on"]["cap_fired"],
                 r["on"]["cap_fired_consumer"], r["off"]["cap_fired"],
                 r["off"]["cap_fired_consumer"]))
    print("   (the consumer counts packet chars only; the producer counts the")
    print("    rendered text including separators, so the consumer is a LOWER")
    print("    bound -- a disagreement is expected only where the margin is")
    print("    smaller than the separator overhead.)")
    print()

    n = len(rows)

    def report(label, k, nn):
        sm = wilson_statsmodels(k, nn)
        mpv = wilson_mpmath(k, nn)
        agree = abs(sm[0] - mpv[0]) < 1e-9 and abs(sm[1] - mpv[1]) < 1e-9
        print("%-50s %3d/%3d = %8.4f%%  Wilson95 [%7.4f%%, %7.4f%%]"
              % (label, k, nn, 100.0 * k / nn, 100 * sm[0], 100 * sm[1]))
        print("%-50s                      mpmath   [%7.4f%%, %7.4f%%] agree=%s"
              % ("", 100 * mpv[0], 100 * mpv[1], agree))

    print("-" * 78)
    print("THE FIGURES")
    print("-" * 78)
    for arm in ("on", "off"):
        tag = ("pruning ON (pre-retirement)" if arm == "on"
               else "pruning OFF (retired default)")
        print("[%s]" % tag)
        report("  cap at :1439 fired",
               sum(1 for r in rows if r[arm]["cap_fired"]), n)
        report("  dispatch payload tail LOST",
               sum(1 for r in rows if not r[arm]["payload_intact"]), n)
        # HONESTY CORRECTION (made in place, 2026-10-14): "domain packet
        # absent" conflates TWO causes -- the domain has no directive file at
        # all (`_load_domain_directive` returns None, composer.py:611-617), and
        # the pruner deleted it. Only the second is a loss. The baseline is the
        # OFF arm, where nothing can delete a packet.
        no_domain_file = sum(1 for r in rows if not r["off"]["domain_present"])
        print("%-50s %3d/%3d  (no domain directive file exists; NOT a loss)"
              % ("  domain packet absent at baseline", no_domain_file, n))
        report("  domain packet DELETED by the pruner (vs baseline)",
               sum(1 for r in rows
                   if r["off"]["domain_present"] and not r[arm]["domain_present"]), n)
        report("  situation packet DELETED by the pruner (vs baseline)",
               sum(1 for r in rows
                   if r["off"]["situation_present"] and not r[arm]["situation_present"]), n)
        report("  text lost with NOTHING in pruned_soft",
               sum(1 for r in rows
                   if (r[arm]["cap_fired"] or not r[arm]["payload_intact"])
                   and not r[arm]["pruned_soft"]), n)
        print()

    on_unlogged = sum(1 for r in rows
                      if (r["on"]["cap_fired"] or not r["on"]["payload_intact"])
                      and not r["on"]["pruned_soft"])
    off_unlogged = sum(1 for r in rows
                       if (r["off"]["cap_fired"] or not r["off"]["payload_intact"])
                       and not r["off"]["pruned_soft"])
    on_chars = sum(r["on"]["chars"] for r in rows)
    off_chars = sum(r["off"]["chars"] for r in rows)
    on_dropped = sum(r["on"]["cap_dropped_lb"] for r in rows)
    off_dropped = sum(r["off"]["cap_dropped_lb"] for r in rows)
    print("-" * 78)
    print("INTERACTION SUMMARY")
    print("-" * 78)
    print("total rendered chars, pruning ON  : %d" % on_chars)
    print("total rendered chars, pruning OFF : %d" % off_chars)
    print("  retirement delivers %+d chars of directive text" % (off_chars - on_chars))
    print("chars dropped by the :1439 cap (lower bound, from manifest):")
    print("  pruning ON  : %d" % on_dropped)
    print("  pruning OFF : %d" % off_dropped)
    print("compositions losing text with an EMPTY pruned_soft record:")
    print("  pruning ON  : %d/%d" % (on_unlogged, n))
    print("  pruning OFF : %d/%d" % (off_unlogged, n))
    print()
    if off_unlogged > on_unlogged or off_dropped > on_dropped:
        print("VERDICT: the retirement INCREASES unlogged text loss. The loss mode")
        print("moved from pruned_soft (recorded) to the :1439 cap (unrecorded).")
    elif off_unlogged == on_unlogged == 0 and off_dropped == on_dropped == 0:
        print("VERDICT: no loss in either arm on this payload. No interaction.")
    else:
        print("VERDICT: unlogged loss not increased by the retirement here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
