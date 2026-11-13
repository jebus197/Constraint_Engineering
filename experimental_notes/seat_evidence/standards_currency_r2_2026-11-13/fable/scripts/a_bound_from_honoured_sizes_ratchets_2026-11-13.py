# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'standards_currency_r2_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 39472fe4d84aa50cb5e9954bab8e9c1a340ea465f655d0c7cd80fc96517d1e48
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""D1 of the standards-currency joint round: a bound derived from HONOURED sizes
ratchets, and the commit-timeout precedent does not, and the difference is
causal direction -- settled by execution on 2026-11-13.

THE QUESTION (joint brief D1). cc2 proposed bounding a preference block by the
shape of `scripts/cdsfl_sv.py`'s commit timeout: max(FLOOR, HEADROOM * max of
the last N recorded values). fable claimed any size bound derived from the
record RATCHETS: blocks grow, the derived bound grows, and it never binds.

THE ANSWER, BY CONSTRUCTION AND BY RUN. After any honoured size s_k the next
bound is at least HEADROOM * s_k, so every sequence with s_{k+1} <= HEADROOM *
s_k is honoured forever: with HEADROOM = 4 a block may QUADRUPLE per revision,
unboundedly. The bound binds on jumps greater than HEADROOM, never on drift.
Whether that is self-defeating depends on the recorded quantity's causal
relation to the bound:

  - a preference-block SIZE enters the record by PASSING the bound, so the
    record is downstream of the allowance and expands to fill it -> ratchet;
  - a COMMIT DURATION is driven by the repository and the machine, not by the
    timeout, so the record is (approximately) exogenous -> no ratchet, which is
    why the `cdsfl_sv.py` shape is sound where it stands.

So the derived quantity for preference currency must come from a record that is
NOT downstream of the bound -- fable's per-entry review timestamps qualify;
honoured sizes do not.
"""
from __future__ import annotations

FLOOR, HEADROOM, N = 50, 4, 10


def drive(sizes, floor=FLOOR, headroom=HEADROOM, n=N):
    """Run a series of proposed sizes through the max-of-last-N bound.

    Returns (honoured sizes, number of times the bound bound).
    """
    honoured, binds = [], 0
    for s in sizes:
        rec = honoured[-n:]
        bound = max(floor, headroom * max(rec)) if rec else floor
        if s <= bound:
            honoured.append(s)
        else:
            binds += 1
    return honoured, binds


def main() -> int:
    g = [20 * 1.1 ** k for k in range(100)]
    h, b = drive(g)
    print(f"gradual 10 per cent growth: honoured {len(h)}/100, binds {b}, "
          f"final size {h[-1]:.0f} from 20")
    for r in (1.5, 2.0, 4.0, 4.1):
        h, b = drive([20 * r ** k for k in range(30)])
        print(f"growth ratio {r}: honoured {len(h)}/30, binds {b}")
    print("so the bound binds on jumps > HEADROOM per step and never on drift;")
    print("a quantity recorded by passing the bound cannot also bound itself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
