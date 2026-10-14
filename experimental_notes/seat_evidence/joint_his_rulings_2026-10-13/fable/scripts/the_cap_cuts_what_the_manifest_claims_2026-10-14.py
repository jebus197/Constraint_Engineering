# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c82309925835c5a93b8c861f4dbd36509814c32398b38c1eb998b3e44b7dc75a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The length cap cuts text the manifest claims was delivered. Measured.

JOINT ROUND his_rulings_2026-10-13, J1. The composed system under test: the
severity specification shadow, the single-membership queue, the retired pruner
(`coherence_pruning=False`) and the ablation switch, all live at once. This
script demonstrates the one interaction none of the per-fix tests covered.

THE MECHANISM, by the names in the code. `compose()` applies the global
phenotype length cap at bench/cdsfl_registry/composer.py (the block commented
"Apply global phenotype length cap", keyed on
`PhenotypeTransform.max_directive_chars`) to the FINAL rendered text, AFTER
packet assembly. The retirement measurement -- 0 of 50 compositions lose a
domain directive with pruning off, 10 of 50 with it on, committed in
bench/tests/test_falsifier_C0001_prune_inversion_2026-09-10.py -- counts PACKET
membership (`"domain" not in {p.layer for p in c.packets}`). It therefore
measures the layer ABOVE the cap. With the pruner retired the composition is
LONGER (nothing deletes SOFT packets any more), so the cap bites deeper, and
what it cuts is the TAIL of the render: canonical order universal -> domain ->
situation, so the situation packet -- the per-dispatch review target, code
extracts and adversarial brief -- goes first, then the domain directive.

MEASURED ON THE REAL COMPOSE PATH (this script re-executes it): for
deepseek_v3 (max_directive_chars=4000), pruning OFF, domains software and
mathematics, with a situation packet attached:

  * the DOMAIN directive survives to 1490 of 3049 chars (software) and
    1490 of 2748 (mathematics) -- 48.9% and 54.2% respectively;
  * the SITUATION packet survives to 1 of 282 chars -- effectively absent;
  * the manifest lists all 3 packets at their FULL char counts and
    `pruned_soft=[]`, i.e. the record says everything was delivered.

THE VERDICT THIS SUPPORTS. The retirement itself stands: with pruning ON the
same deepseek compositions lose domain AND situation ENTIRELY (packet deleted),
so partial-by-cap dominates absent-by-pruner on every row, and the other 4
models deliver FULL text with pruning off. But the founder's stated ground for
retirement -- "we have no way of knowing what it feeds" -- is still violated
for deepseek_v3: the provenance manifest misstates what was delivered, and the
0-of-50 figure, measured at packet level, cannot see it. The simplest
sufficient repair is manifest honesty: record the cap event and which packets
lost text. It changes no delivered byte, so replay comparisons survive.

Falsifier: bench/tests/test_the_manifest_records_the_length_cap_cut_2026-10-14.py
(red before the manifest records the cut, green after).

Usage: python3 scripts/the_cap_cuts_what_the_manifest_claims_2026-10-14.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402


SIT = dict(
    review_target="SIM target: a 400-line numerical integrator",
    code_extracts=(
        "def integrate(f,a,b,n):\n    h=(b-a)/n\n"
        "    return sum(f(a+i*h) for i in range(n))*h"
    ),
    adversarial_brief=(
        "SIM adversarial brief: attack the trapezoid-vs-rectangle claim."
    ),
)


def _surviving_prefix(text: str, rendered: str) -> int:
    t = text.strip()
    lo, hi = 0, len(t)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if t[:mid] in rendered:
            lo = mid
        else:
            hi = mid - 1
    return lo


def main() -> int:
    answer_help(__doc__, __file__)
    from bench.cdsfl_registry.composer import compose, PHENOTYPE_TRANSFORMS

    rows_cap_fired = 0
    rows = 0
    manifest_admits = 0
    print(f"{'model':<16}{'domain':<13}{'prune':<7}{'final':<7}{'cap':<7}"
          f"{'domain_text':<14}{'situation_text':<16}manifest_claims")
    for model, tr in PHENOTYPE_TRANSFORMS.items():
        for dom in ("software", "mathematics"):
            for prune in (False, True):
                c = compose(dom, model, coherence_pruning=prune, **SIT)
                rows += 1
                rend = c.rendered_text
                by_layer = {p.layer: p for p in c.packets}

                def frac(layer):
                    p = by_layer.get(layer)
                    if p is None:
                        return "ABSENT-packet"
                    n = _surviving_prefix(p.text, rend)
                    return ("FULL" if n == len(p.text.strip())
                            else f"{n}/{len(p.text.strip())}")

                cap_fired = rend.endswith("[... truncated for model capacity]")
                if cap_fired and not prune:
                    rows_cap_fired += 1
                cap_rec = c.manifest.get("length_cap")
                if isinstance(cap_rec, dict) and cap_rec.get("fired") == cap_fired:
                    manifest_admits += 1
                print(f"{model:<16}{dom:<13}{str(prune):<7}{len(rend):<7}"
                      f"{tr.max_directive_chars:<7}{frac('domain'):<14}"
                      f"{frac('situation'):<16}"
                      f"packets={[p['layer'] for p in c.manifest['packets']]} "
                      f"length_cap_recorded={bool(cap_rec)}")

    print()
    print(f"rows: {rows}; pruning-OFF rows where the cap cut delivered text: "
          f"{rows_cap_fired}")
    print(f"rows whose manifest records the cap truthfully: "
          f"{manifest_admits}/{rows}")
    if manifest_admits < rows:
        print("VERDICT: the manifest claims delivery the cap removed. "
              "The 0-of-50 retirement figure is a PACKET-level measurement "
              "and cannot see this. Repair: record the cap event in the "
              "manifest (no delivered byte changes).")
        return 1
    print("VERDICT: manifest records the cap; knowability holds at the "
          "render layer as well as the packet layer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
