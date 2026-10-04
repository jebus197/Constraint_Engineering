# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_blocker_round1_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 56ae7240a54c645639c447dedd52b6c073faafc0aa95f3e7e369c137686a494a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Census of A4-counted entries across every archived runner_state.json.

Challenges Position A's figures ("65 runs; 22 with >=1 permanently blocked
entry; 150 entries; 107 blocked by the severity clause alone") against the
archive actually present, classifying each A4-counted entry by WHICH valve
guard stops its release:
  sev_only : severity < 0.7 but verdicts present  (Position A's repair alone
             would eventually release it)
  verd_only: verdicts == [] but severity >= 0.7   (evidence/verdict channel
             is the blocker; severity clause is NOT)
  both     : severity < 0.7 AND verdicts == []    (run-1b shape; needs the
             composed fix)
Wilson 95% CIs via statsmodels, cross-verified with an mpmath closed form.
"""
import glob, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import reference_runner_v3 as rv

rows, skipped = [], 0
for sp in sorted(glob.glob('bench/logs/*/runner_state.json')):
    try:
        reg = rv.FindingRegistry.from_dict(json.load(open(sp))['registry'])
        a4 = reg.unverified_critical_count()
    except Exception:
        skipped += 1
        continue
    counted = []
    for cid, e in reg.entries.items():
        if e.get('status') != 'UNCONFIRMED': continue
        if e.get('irreducible_escalation') and not e.get('integrity_unobserved'): continue
        if e.get('exhausted'): continue
        if rv._integrity_violation_excluded(e): continue
        fc = (e.get('falsifier_code') or '').strip()
        fv = (e.get('falsifier_verdict') or '').strip().upper()
        if (not fc) or fv not in rv._FALSIFIER_RESOLVED_VERDICTS:
            counted.append(e)
    assert len(counted) == a4, (sp, len(counted), a4)  # census == real counter
    rows.append((sp, counted))

n_runs = len(rows)
blocked_runs = sum(1 for _, c in rows if c)
entries = [e for _, c in rows for e in c]
sev_only  = sum(1 for e in entries if (e.get('severity') or 0) < 0.7 and e.get('verdicts'))
verd_only = sum(1 for e in entries if not e.get('verdicts') and (e.get('severity') or 0) >= 0.7)
both      = sum(1 for e in entries if not e.get('verdicts') and (e.get('severity') or 0) < 0.7)
neither   = len(entries) - sev_only - verd_only - both
zero_verd = sum(1 for e in entries if not e.get('verdicts'))
has_ce    = sum(1 for e in entries if e.get('computed_evidence'))
fix_rel   = sum(1 for e in entries if e.get('verdicts') or e.get('computed_evidence'))

def wilson_sm(k, n):
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method='wilson')
    return 100*lo, 100*hi

def wilson_mp(k, n):
    import mpmath as mp
    z = mp.sqrt(2) * mp.erfinv(mp.mpf('0.95'))
    p = mp.mpf(k)/n
    den = 1 + z**2/n
    ctr = p + z**2/(2*n)
    rad = z*mp.sqrt(p*(1-p)/n + z**2/(4*n**2))
    return float(100*(ctr-rad)/den), float(100*(ctr+rad)/den)

def show(label, k, n):
    sl, sh = wilson_sm(k, n); ml, mh = wilson_mp(k, n)
    assert abs(sl-ml) < 1e-6 and abs(sh-mh) < 1e-6, (label, sl, ml)
    print(f"{label}: {k}/{n} = {100*k/n:.4f}%  Wilson95 [{sl:.4f}%, {sh:.4f}%] (statsmodels==mpmath to 1e-6)")

print(f"archives readable: {n_runs} (skipped {skipped}) -- the brief said 65")
show("runs with >=1 A4-counted entry", blocked_runs, n_runs)
print(f"A4-counted entries total: {len(entries)} -- the brief said 150")
show("  zero-verdict entries", zero_verd, len(entries))
show("  severity-clause-ALONE blocked (subcrit, verdicts present)", sev_only, len(entries))
show("  verdict-channel-ALONE blocked (critical, zero verdicts)", verd_only, len(entries))
show("  BOTH guards block (run-1b shape)", both, len(entries))
show("  carrying computed_evidence", has_ce, len(entries))
show("  releasable by the composed fix (verdicts OR computed_evidence)", fix_rel, len(entries))
print(f"  blocked by neither valve guard (critical with verdicts; age/threshold holds them): {neither}")
# The brief's own quoted intervals, recomputed:
show("brief's 22/65", 22, 65)
show("brief's 58/86", 58, 86)
