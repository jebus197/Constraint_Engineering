# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4c53bfcffdc72762e8c87293f89263afc7bf90a200e4acd8e505def32d8ceca1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Q2: reach of the proof-polarity inversion across the archive.

Counts, over every archived registry in bench/logs/**: entries carrying
cc2's `verification_polarity` field (producer count), non-critical entries
whose FINAL status is REFUTED (the silent-retire channel's ceiling), and
critical entries with falsifier_verdict REFUTED (the CONFIRM-only HIL class).
Also reports which runs recorded severity_spec_enabled true.
"""
import json, os, glob

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench", "logs")
reports = []
for pat in ("*/*report.json", "*/*.json"):
    reports.extend(glob.glob(os.path.join(ROOT, pat)))
reports = sorted(set(r for r in reports if "sandbox_harvest" not in r))

runs = 0; entries_total = 0; pol_field = 0
noncrit_refuted = 0; crit_verdict_refuted = 0; crit_confirmed = 0
spec_on_runs = []
seen_registry_files = 0
for rp in reports:
    try:
        with open(rp) as f: d = json.load(f)
    except Exception:
        continue
    if not isinstance(d, dict): continue
    reg = d.get("registry") or {}
    ent = reg.get("entries") if isinstance(reg, dict) else None
    cfg = d.get("config") or {}
    if isinstance(cfg, dict) and cfg.get("severity_spec_enabled"):
        spec_on_runs.append(os.path.basename(rp))
    if not isinstance(ent, dict) or not ent: continue
    seen_registry_files += 1
    runs += 1
    for cid, e in ent.items():
        if not isinstance(e, dict): continue
        entries_total += 1
        if "verification_polarity" in e: pol_field += 1
        sev = float(e.get("severity") or 0.0)
        fv = str(e.get("falsifier_verdict") or "").strip().upper()
        st = str(e.get("status") or "").strip().upper()
        if sev < 0.7 and st == "REFUTED": noncrit_refuted += 1
        if sev >= 0.7 and fv == "REFUTED": crit_verdict_refuted += 1
        if sev >= 0.7 and fv == "CONFIRMED": crit_confirmed += 1

print(f"report files scanned      : {len(reports)}")
print(f"files with registry        : {seen_registry_files}")
print(f"entries total              : {entries_total}")
print(f"entries with verification_polarity field : {pol_field}")
print(f"non-critical, status REFUTED             : {noncrit_refuted}")
print(f"critical, falsifier_verdict REFUTED      : {crit_verdict_refuted}")
print(f"critical, falsifier_verdict CONFIRMED    : {crit_confirmed}")
print(f"runs recording severity_spec_enabled=True: {len(spec_on_runs)} {spec_on_runs[:5]}")
