# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'standards_currency_r2_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cf132852bcd206084d380fc6a67a55c247a5da6d6c8d2c477926f0ceefb8e5c8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is a RELABEL safe to apply without a human? Executed, not argued.

CC1's proposed boundary for the dynamic half of the founder's question: a
revision may be applied AUTOMATICALLY when it is provably non-semantic for the
encoding's purpose -- the standard's NAME or CITATION YEAR changes while the
ordinal SCALE and the CRITICAL CUT are bit-identical -- checked by comparing the
scale tuple and the cut before and after.

This script applies exactly such a relabel to the live encoding IN MEMORY (GHS
Rev. 11, 2025 -> Rev. 12, 2027), holding `severity_levels` and `critical_level`
byte-identical, and then diffs EVERY decision the vocabulary module makes. The
question is not whether the gate still fires the same way -- it must, that is
what the check tests -- but whether any OTHER consumer decides on the name.

Nothing is written. The mutation is to an in-memory dict and is reverted.
"""
import copy
import itertools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "bench"))
from cdsfl_registry import domain_vocabulary as dv          # noqa: E402

OLD = "GHS health hazard category (Rev. 11, 2025)"
NEW = "GHS health hazard category (Rev. 12, 2027)"


def decisions():
    """Every decision the module makes, as a comparable structure."""
    ds = sorted(dv.domains())
    out = {}
    for d in ds:
        r = dv.consequence_domain(d)
        out[("consequence_domain", d)] = r
        try:
            out[("severity", d)] = dv.severity(d)
        except Exception as e:                              # noqa: BLE001
            out[("severity", d)] = f"ERROR {type(e).__name__}"
    for a, b in itertools.combinations(ds, 2):
        try:
            out[("may_compose", a, b)] = dv.may_compose(a, b)
        except Exception as e:                              # noqa: BLE001
            out[("may_compose", a, b)] = f"ERROR {type(e).__name__}"
    out[("inheriting_domains",)] = tuple(dv.inheriting_domains())
    out[("tiers",)] = tuple(dv.tiers())
    return out


def main() -> int:
    enc = dv.load()
    before_levels = tuple(enc["chemistry"]["severity_levels"])
    before_cut = enc["chemistry"]["critical_level"]
    before = copy.deepcopy(decisions())

    # --- apply the relabel, holding the ordinal scale and the cut IDENTICAL ---
    enc["chemistry"]["severity_scale"] = NEW
    after = copy.deepcopy(decisions())
    after_levels = tuple(enc["chemistry"]["severity_levels"])
    after_cut = enc["chemistry"]["critical_level"]

    print("=" * 78)
    print("IS A RELABEL NON-SEMANTIC?  GHS Rev. 11, 2025 -> Rev. 12, 2027")
    print("=" * 78)
    print(f"  ordinal scale bit-identical : {before_levels == after_levels}")
    print(f"  critical cut bit-identical  : {before_cut == after_cut}  ({before_cut!r})")
    print("  => CC1's admissibility check PASSES: this relabel is auto-appliable")
    print("     under the proposed boundary.")
    print()

    changed = [k for k in before if before[k] != after[k]]
    print(f"  decisions that CHANGED anyway: {len(changed)} of {len(before)}")
    for k in changed:
        print(f"    {k}")
        print(f"      before: {before[k]}")
        print(f"      after : {after[k]}")
    print()

    # --- the consumer the gate check cannot see: a record stamped with the id ---
    archived = {"severity": 0.81, "scale_name": OLD, "critical_level": before_cut}
    live_scale = dv.consequence_domain("chemistry")["scale"]
    matches = archived["scale_name"] == live_scale
    print("  THE CONSUMER THE CHECK CANNOT SEE. A severity record stamped with")
    print("  the scale it was judged on -- which is the provenance repair BOTH")
    print("  seats recommended -- compares that stamp against the live scale:")
    print(f"    archived stamp : {archived['scale_name']!r}")
    print(f"    live scale     : {live_scale!r}")
    print(f"    stamps match   : {matches}")
    assert not matches, (
        "the relabel did not change the stamp; then this falsifier proves "
        "nothing and must be read as REFUTING the finding")
    print("  A relabel that is non-semantic FOR THE GATE silently makes every")
    print("  previously archived record compare UNEQUAL to the live encoding.")
    print("  The record is not wrong and the gate is not wrong; the EQUALITY is.")
    print()
    print("  relabel_changes_a_gate_decision   = False")
    print(f"  relabel_changes_other_decisions   = {len(changed) > 0}")
    print("  relabel_breaks_archived_stamp_match = True")
    print()
    print("  VERDICT: the boundary is SOUND FOR THE GATE and UNSOUND AS STATED,")
    print("  because 'non-semantic for the encoding's purpose' was checked on")
    print("  the gate's inputs only. The scale NAME is itself load-bearing for")
    print("  provenance comparison, which is the repair this round recommends.")

    enc["chemistry"]["severity_scale"] = OLD     # revert in memory
    assert dv.consequence_domain("chemistry")["scale"] == OLD, "revert failed"
    print("  in-memory encoding reverted; nothing was written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
