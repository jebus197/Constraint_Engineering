#!/usr/bin/env python3
"""HOW MANY MASTER-TASK-LIST ENTRIES DID HE EXPLICITLY ASK FOR? -- 2026-11-09

HIS TEST, verbatim, 2026-11-09:
  "you should only count additions to your master task list (including those we
   have agreed above) where the entry is preceded by an explicit instruction
   from me to 'add the item/s to your master task list', while discounting the
   rest."

THIS IS THE PRELIMINARY HALF ONLY. It counts HIS INSTRUCTIONS, not the entries
they attach to. Tying each instruction to the entries added after it is the
full inventory, which he directed be run LAST.

TWO SURFACES, because an instruction of his reaches me by 2 routes and a count
over 1 of them is a count of the route, not of him:
  (a) his annotated TTS response files, read with the FORMAT-AWARE reader
      (scripts/read_founder_responses_2026-10-11.py) -- never by grep, because
      221 of 691 annotations are invisible to a naive read.
  (b) this session's chat transcript, user-role text blocks only, with hook
      and system-reminder text excluded by marker.

NARROW vs WIDE is reported as 2 separate rates with their own denominators,
because a single number here would hide which reading produced it.
"""
import json, re, subprocess, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
TRANSCRIPT = pathlib.Path(
    "/Users/georgejackson/.claude/projects/"
    "-Users-georgejackson-Developer-Projects/"
    "a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl")

# NARROW: an adding verb and the LIST named in the same sentence.
NARROW = re.compile(
    r'\b(add|added|adding|put|place|append|stick|log)\b[^.?!]{0,80}?'
    r'\b(master\s+task\s+list|task\s+list|master\s+list)\b', re.I)
# WIDE: also catches "to the list" / "on the list" after an adding verb.
WIDE = re.compile(
    r'\b(add|added|adding|put|place|append|stick|log)\b[^.?!]{0,80}?'
    r'\b(master\s+task\s+list|task\s+list|master\s+list|the\s+list|your\s+list)\b', re.I)

HOOK_MARKERS = ('<system-reminder>', 'Stop hook feedback', '[mc]', '[clock]',
                '[tasks]', '<task-notification>', '<local-command',
                'Primary Request', 'Current Work:', 'command hook')


def _iv(k, n):
    """Wilson then Clopper-Pearson, each on 2 independent routes.

    CANONICAL BODY, lifted byte-exact (sha256 of the function source begins
    5c0ff108ca6d5966) -- see B21's note on why a local re-implementation here
    returned Wilson twice and refused a commit.
    """
    import math
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as _beta
    import mpmath as mp
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    p = k / n
    z = 1.959963984540054
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    w_closed = (max(0.0, cen - hw), min(1.0, cen + hw))
    w_sm = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    cp_lo = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    cp_hi = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))
    cp_lo2 = 0.0 if k == 0 else float(mp.findroot(
        lambda q: mp.betainc(k, n - k + 1, 0, q, regularized=True) - mp.mpf('0.025'),
        mp.mpf(cp_lo) if cp_lo > 0 else mp.mpf('0.001')))
    cp_hi2 = 1.0 if k == n else float(1 - mp.mpf('0.025') ** mp.mpf(1) * 0) if False else (
        1.0 if k == n else float(mp.findroot(
            lambda q: mp.betainc(k + 1, n - k, 0, q, regularized=True) - mp.mpf('0.975'),
            mp.mpf(cp_hi))))
    gap = max(abs(w_closed[0] - w_sm[0]), abs(w_closed[1] - w_sm[1]),
              abs(cp_lo - cp_lo2), abs(cp_hi - cp_hi2))
    return w_closed, (cp_lo, cp_hi), gap


def his_annotations():
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "read_founder_responses_2026-10-11.py"),
         "--json"], capture_output=True, text=True, cwd=str(REPO))
    if out.returncode != 0:
        raise SystemExit(f"reader exited {out.returncode}: {out.stderr[:400]}")
    return json.loads(out.stdout)["annotations"]


def his_chat():
    msgs = []
    if not TRANSCRIPT.exists():
        return msgs
    for line in TRANSCRIPT.open(errors="replace"):
        if '"role":"user"' not in line and '"role": "user"' not in line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        m = r.get("message") or {}
        if m.get("role") != "user":
            continue
        c = m.get("content")
        texts = [c] if isinstance(c, str) else [
            b.get("text", "") for b in (c or [])
            if isinstance(b, dict) and b.get("type") == "text"]
        for t in texts:
            if not t.strip():
                continue
            if any(h in t for h in HOOK_MARKERS):
                continue
            msgs.append((r.get("timestamp", ""), t))
    seen, uniq = set(), []
    for ts, t in msgs:
        k = t[:300]
        if k in seen:
            continue
        seen.add(k)
        uniq.append((ts, t))
    return uniq


def main():
    print("=" * 78)
    print("HOW MANY MASTER-TASK-LIST ENTRIES DID HE EXPLICITLY ASK FOR?")
    print("PRELIMINARY: this counts HIS INSTRUCTIONS, not the entries they produced.")
    print("=" * 78)

    anns = his_annotations()
    chat = his_chat()
    print(f"\nSURFACE A -- annotated response files : {len(anns)} annotations")
    print(f"SURFACE B -- this session's chat      : {len(chat)} distinct messages of his")

    a_narrow = [a for a in anns if NARROW.search(a["text"])]
    a_wide = [a for a in anns if WIDE.search(a["text"])]
    c_narrow = [(ts, t) for ts, t in chat if NARROW.search(t)]
    c_wide = [(ts, t) for ts, t in chat if WIDE.search(t)]

    for lbl, k, n in (("annotations NARROW", len(a_narrow), len(anns)),
                      ("annotations WIDE  ", len(a_wide), len(anns)),
                      ("chat NARROW       ", len(c_narrow), len(chat)),
                      ("chat WIDE         ", len(c_wide), len(chat))):
        w, cp, gap = _iv(k, n)
        print(f"  {lbl}: {k} of {n} = {k/n if n else 0:.6f}"
              f"  Wilson [{w[0]:.6f}, {w[1]:.6f}]"
              f"  CP [{cp[0]:.6f}, {cp[1]:.6f}]  2-route gap {gap:.3e}")

    tot_narrow = len(a_narrow) + len(c_narrow)
    tot_wide = len(a_wide) + len(c_wide)
    print(f"\nTOTAL explicit add-to-the-list instructions of his:")
    print(f"  NARROW (adding verb + the list named) : {tot_narrow}")
    print(f"  WIDE   (also 'the list' / 'your list'): {tot_wide}")

    print("\n-- EVERY NARROW HIT FROM HIS ANNOTATIONS --")
    for a in a_narrow:
        print(f"  [{a['date']}] {a['file']} line {a['line_index']}")
        print(f"      {a['text'][:330]}")
    print("\n-- EVERY NARROW HIT FROM CHAT --")
    for ts, t in c_narrow:
        m = NARROW.search(t)
        print(f"  [{ts[:10]}] ...{t[max(0,m.start()-110):m.end()+200]}...")

    print("\nWHAT THIS DOES NOT SAY. It does not say how many ENTRIES each")
    print("instruction produced -- several of his instructions name a batch.")
    print("Tying instructions to entries is the full inventory, run last on his order.")


if __name__ == "__main__":
    main()
