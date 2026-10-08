# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f830f3e35fb3fb559325e661f8cfa06daf4a0c7ac79ca8e062ce30df11225d81
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Falsifier for bench/model_identity.py. Imports the real module.

FAILS iff: identical configurations split, differing ones merge, a vendor
release inherits a record, cosmetic fields split a key, or pooling fails to
beat split records on the measured cold-start price.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.model_identity import capability_key, instance_id  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FALSIFIED'}: {name} {detail}")
    if not cond:
        fails.append(name)


base = {"provider": "openrouter", "model_version": "openai/gpt-5.5-2026-08-01",
        "temperature": 0.2, "top_p": 1.0, "max_tokens": 8192,
        "system_prompt": "You are a falsifier writer.",
        "tool_set": ["execute_python", "read_file"], "quantisation": None}

# 1. two genuinely identical configurations are NOT split
check("identical configs merge", capability_key(base) == capability_key(dict(base)))
# ... even when the tool list order differs (same set)
reordered = dict(base, tool_set=["read_file", "execute_python"])
check("tool order does not split", capability_key(base) == capability_key(reordered))
# ... and even when a cosmetic field differs
cosmetic = dict(base, display_name="Codex", billing_tag="exp56")
check("cosmetic fields do not split", capability_key(base) == capability_key(cosmetic))

# 2. one configuration is not merged with a different one
for f, v in [("temperature", 0.7), ("model_version", "openai/gpt-5.5-2026-11-01"),
             ("system_prompt", "You are a reviewer."), ("provider", "claude_cli")]:
    check(f"{f} change splits", capability_key(dict(base, **{f: v})) != capability_key(base))

# 3. a vendor release gets a NEW key at 0 attempts, by construction
release = dict(base, model_version="openai/gpt-6.0-2026-12-01")
check("vendor release -> new key", capability_key(release) != capability_key(base))

# 4. random instance ids are dispatch-only and DO split -- which is the defect
#    random capability keys would have: demonstrate the pooling advantage.
check("instance ids differ per call (dispatch-only)", instance_id() != instance_id())
Z = 1.959963984540054
def wilson(k, n):
    if n == 0: return (0.0, 0.0)
    p, d = k / n, 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = (Z / d) * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))
def rounds_to_separate(p_hi, p_lo, instances):
    """Rounds of 1 attempt per instance until pooled hi-LB clears pooled lo-UB."""
    for r in range(2, 4001):
        n = r * instances
        if wilson(round(p_hi * n), n)[0] > wilson(round(p_lo * n), n)[1]:
            return r
    return None
pooled, split = rounds_to_separate(0.8, 0.4, 2), rounds_to_separate(0.8, 0.4, 1)
print(f"  rounds to separate 0.8 from 0.4: pooled(2 instances)={pooled}, split={split}")
check("pooling beats split records on cold-start rounds", pooled < split,
      f"({pooled} < {split})")

# 5. the live defect this replaces: model_id collides in the orchestrator
src = (Path(__file__).resolve().parents[1] / "bench" /
       "experiment_11_orchestrator.py").read_text()
import re
vals = re.findall(r'(?:secondary_)?model_id="([^"]+)"', src)
dups = {v for v in vals if vals.count(v) > 1}
print(f"  orchestrator model_id values: {len(vals)} occurrences, "
      f"{len(set(vals))} distinct, duplicated: {sorted(dups)}")
check("the collision the digest replaces is real",
      len(vals) == 12 and len(set(vals)) == 10 and dups == {"opus", "gpt-5.5"})

print()
if fails:
    print("FALSIFIED:", fails)
    raise AssertionError(fails)
print("ALL CHECKS PASS -- digest merges the identical, splits the different, "
      "and a vendor release starts at 0 attempts by construction.")
