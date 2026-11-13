# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'standards_currency_r2_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 162b2a6e5e606d52b964e5e082de8033ca68f68051cadfa596b78bb5fb4e171b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""D1, settled by arithmetic over the shape cc2 proposes, not by opinion.

cc2's proposed bound, read from `scripts/cdsfl_sv.py` lines 615-723:

    bound(k) = max(FLOOR, HEADROOM * max(observed[k-N+1 .. k]))

with FLOOR = 300, HEADROOM = 4, N = COMMIT_TIMEOUT_LEDGER_ROWS = 10.

fable's objection: a bound DERIVED from the record RATCHETS -- the record grows,
the bound grows with it, and it never binds. Decidable by execution: drive the
bound with growing series and count refusals.

A bound BINDS at step k iff observed[k] > bound(k-1).
"""
import sys

FLOOR, HEADROOM, N = 300, 4, 10


def bound(window):
    return max(FLOOR, HEADROOM * max(window)) if window else FLOOR


def drive(series, label):
    """Return (refusals, final bound, max admitted) driving the bound online."""
    obs, refusals = [], 0
    for s in series:
        b = bound(obs[-N:])
        if s > b:
            refusals += 1
        obs.append(s)
    return label, refusals, bound(obs[-N:]), max(obs)


def main() -> int:
    print("=" * 78)
    print("D1  DOES max-of-last-N x HEADROOM RATCHET?")
    print("=" * 78)
    print(f"  FLOOR={FLOOR}  HEADROOM={HEADROOM}  N={N}  (read from scripts/cdsfl_sv.py)")
    print()
    cases = [
        ("flat at 100",                 [100] * 200),
        ("linear +10/step",             [100 + 10 * i for i in range(200)]),
        ("geometric x1.5/step",         [100 * 1.5 ** i for i in range(60)]),
        ("geometric x3/step",           [100 * 3.0 ** i for i in range(40)]),
        ("geometric x4/step (= H)",     [100 * 4.0 ** i for i in range(30)]),
        ("geometric x4.1/step (> H)",   [100 * 4.1 ** i for i in range(30)]),
        ("one 100x spike at step 50",   [100] * 50 + [10000] + [100] * 50),
    ]
    rows = [drive(s, l) for l, s in cases]
    print(f"    {'series':28} {'refusals':>9} {'final bound':>16} {'max admitted':>16}")
    for l, r, b, m in rows:
        print(f"    {l:28} {r:>9} {b:>16.4g} {m:>16.4g}")
    print()

    # THE DECISIVE ARITHMETIC, not the table. Under monotone growth with a
    # per-step ratio r, max(last N) == observed[k-1], so the bound at step k is
    # HEADROOM * observed[k-1] and the next entry is observed[k-1] * r. The bound
    # binds iff r > HEADROOM. It is INDEPENDENT of how large the entries have got.
    ratios = [1.0, 2.0, 3.0, 3.9, 4.0, 4.1, 8.0]
    print("  The binding condition under geometric growth at ratio r:")
    print(f"    {'r':>6} {'binds?':>8} {'refusals in 30 steps':>22}")
    for r in ratios:
        _, nref, _, _ = drive([100 * r ** i for i in range(30)], "")
        print(f"    {r:>6.1f} {str(r > HEADROOM):>8} {nref:>22}")
    print()
    print("  => The bound binds on the RATIO of consecutive entries and NEVER on")
    print("     their SIZE. Growth at any ratio <= HEADROOM is admitted without")
    print("     limit, and the bound grows to meet it. That is a ratchet.")

    # And the quantity the ratchet is WRONG for is named by its failure direction.
    print()
    print("  WHY IT IS CORRECT FOR cdsfl_sv AND INVERTED FOR A CURATION BOUND:")
    print("    commit timeout      -- the derived quantity is a TOLERANCE. A bound")
    print("                           that is too SMALL aborts a healthy commit, so")
    print("                           the conservative direction is UP, and a bound")
    print("                           that grows with the record fails SAFE.")
    print("    curation/size bound -- the derived quantity is a LIMIT ON HUMAN")
    print("                           REVIEW LOAD. A bound that is too LARGE admits")
    print("                           unreviewed content, so the conservative")
    print("                           direction is DOWN, and a bound that grows with")
    print("                           the record fails UNSAFE.")
    print("    The SHAPE transfers; the DIRECTION does not. max-of-last-N is")
    print("    monotone non-decreasing in the record by construction, so it can only")
    print("    ever be conservative upward.")

    flat = [r for l, r, _, _ in rows if l == "flat at 100"][0]
    lin = [r for l, r, _, _ in rows if l == "linear +10/step"][0]
    g15 = [r for l, r, _, _ in rows if l == "geometric x1.5/step"][0]
    g41 = [r for l, r, _, _ in rows if l == "geometric x4.1/step (> H)"][0]
    assert flat == 0 and lin == 0 and g15 == 0, "a sub-headroom ramp must be admitted"
    assert g41 > 0, "growth above HEADROOM must bind, or the bound is vacuous"
    print()
    print("  RATCHET CONFIRMED: unbounded growth admitted with 0 refusals at every")
    print("  ratio <= HEADROOM; the bound binds only above it.")
    print("  ratchets_under_sub_headroom_growth = True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
