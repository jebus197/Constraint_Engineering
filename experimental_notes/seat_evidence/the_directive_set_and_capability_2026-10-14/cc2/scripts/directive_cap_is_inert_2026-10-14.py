# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1ec969f59aff9c23fb7d382ed305d90f0977fb11eb9c8a172886381faa78c6b1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""`max_directive_chars` is INERT over its whole configured range. Measured, not argued.

Run from the repository root:

    python3 scripts/directive_cap_is_inert_2026-10-14.py

WHY THIS SCRIPT EXISTS
----------------------
The founder proposed removing `max_directive_chars` outright. The additive
standard forbids a removal without "a COMMITTED MEASUREMENT showing the
replacement dominates on a named property". No such measurement existed, and
none *could* exist, because nothing in the repository reports what a seat
actually receives. This script is that instrument. It is written BEFORE the
removal, so the removal can be evidenced rather than judged.

WHAT IS MEASURED, by calling the live composer
----------------------------------------------
1. DELIVERY PER SEAT. `_load_universal_directive(label)` is called for every
   label the live tables carry plus roster labels that have no entry. Delivered
   characters and a SHA are reported, so identical renders show as identical.

2. THE CAP'S TRANSFER FUNCTION. `max_directive_chars` is swept across
   [500, 50000] with everything else held fixed. The output is a step function
   with exactly ONE step, and the step is NOT at any configured cap value:

       deliver(c) = ValueError          for c <  2503   (len of minimal render)
       deliver(c) = 2503                for 2503 <= c < 27803
       deliver(c) = 27803               for c >= 27803  (len of the source)

   The four configured values -- 4000, 6000, 8000, 12000 -- all lie strictly
   inside the flat middle interval. So d(deliver)/d(cap) = 0 at every value the
   project actually uses: the parameter cannot change any output it is set to.
   This is stronger than "the caps differentiate nothing": they do not even
   select between the two branches differently from one another.

3. THE CRASH REGION. For any cap below the minimal render's own length,
   `_render_universal_minimal` raises ValueError. 2000 is an entirely plausible
   cap for a genuinely small-context model -- precisely the case the parameter
   exists to serve. So the parameter is inert where it is used and raises where
   it would matter. That asymmetry is the finding, not the cap values.

4. SILENT DEFAULTING. Labels absent from `PHENOTYPE_TRANSFORMS` inherit the
   8000 default with no diagnostic. Same failure shape as the realised
   2026-08-30 incident recorded in `bench/reference_runner_v3.py` ("Fable had
   no COMPOSER_MODEL_MAP entry and no .toml, so it composed to
   FileNotFoundError -> 0 chars") -- a seat ran on an empty system prompt and
   nothing said so.

Every number printed is computed here from live code. Nothing is hardcoded
except the interval endpoints of the sweep.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry.composer import (  # noqa: E402
    DIRECTIVES_DIR,
    PHENOTYPE_TRANSFORMS,
    PhenotypeTransform,
    _load_universal_directive,
    _render_universal_minimal,
)

#: Labels carrying a PHENOTYPE_TRANSFORMS entry, plus live roster labels that do
#: not. `None` is the no-model default path.
PROBE_LABELS: tuple[object, ...] = (
    "opus_4_6", "chatgpt_5_4", "codex_5_3", "gemini_3_1_pro", "deepseek_v3",
    "fable", "Fable", "cc2", None,
)

#: Cap values to sweep. Chosen to bracket both discontinuities and to include
#: every configured value, so the flat region is visible rather than asserted.
SWEEP_CAPS: tuple[int, ...] = (
    500, 1000, 2000, 2502, 2503, 2504, 3000,
    4000, 6000, 8000, 12000, 20000, 27802, 27803, 27804, 30000, 50000,
)

_SWEEP_KEY = "__cap_sweep_probe__"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _headings(text: str) -> list[str]:
    return re.findall(r"^#{1,6} +(.*)$", text, flags=re.MULTILINE)


def deliver_at_cap(cap: int) -> int | str:
    """Deliver the universal directive with `max_directive_chars` set to `cap`.

    Everything else is held fixed at a non-"minimal" format_style, so the only
    live variable is the cap. Returns the delivered character count, or the
    exception rendering if composition raised.
    """
    PHENOTYPE_TRANSFORMS[_SWEEP_KEY] = PhenotypeTransform(
        max_directive_chars=cap, format_style="concise"
    )
    try:
        return len(_load_universal_directive(_SWEEP_KEY).text)
    except Exception as exc:                  # noqa: BLE001 - reported, not swallowed
        return f"{type(exc).__name__}: {exc}"
    finally:
        PHENOTYPE_TRANSFORMS.pop(_SWEEP_KEY, None)


def measure() -> dict:
    core_path = DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md"
    oper_path = DIRECTIVES_DIR / "universal" / "cdsfl_operational.md"
    core = core_path.read_text(encoding="utf-8")
    oper = oper_path.read_text(encoding="utf-8") if oper_path.exists() else ""

    minimal = _render_universal_minimal()

    per_seat = []
    for label in PROBE_LABELS:
        transform = PHENOTYPE_TRANSFORMS.get(label or "", PhenotypeTransform())
        has_entry = (label or "") in PHENOTYPE_TRANSFORMS
        text = _load_universal_directive(label).text
        per_seat.append({
            "label": "None (no-model default)" if label is None else label,
            "has_transform_entry": has_entry,
            "cap": transform.max_directive_chars,
            "delivered_chars": len(text),
            "sha12": _sha(text),
            "headings_delivered": len(_headings(text)),
        })

    sweep = [{"cap": c, "delivered": deliver_at_cap(c)} for c in SWEEP_CAPS]

    configured = sorted({t.max_directive_chars for t in PHENOTYPE_TRANSFORMS.values()}
                        | {PhenotypeTransform().max_directive_chars})
    delivered_at_configured = {c: deliver_at_cap(c) for c in configured}

    return {
        "core_chars": len(core),
        "core_headings": len(_headings(core)),
        "oper_chars": len(oper),
        "minimal_chars": len(minimal),
        "minimal_headings": len(_headings(minimal)),
        "per_seat": per_seat,
        "sweep": sweep,
        "configured_caps": configured,
        "delivered_at_configured": delivered_at_configured,
        "distinct_renders": len({s["sha12"] for s in per_seat}),
        "seats_without_entry": [s["label"] for s in per_seat
                                if not s["has_transform_entry"]],
    }


def report(m: dict) -> None:
    print("=" * 74)
    print("max_directive_chars: TRANSFER FUNCTION AND INERTNESS")
    print("=" * 74)
    print(f"\ncdsfl_core_formal.md  : {m['core_chars']:,} chars, "
          f"{m['core_headings']} headings")
    print(f"cdsfl_operational.md  : {m['oper_chars']:,} chars")
    print(f"minimal render        : {m['minimal_chars']:,} chars, "
          f"{m['minimal_headings']} headings")

    print("\n-- 1. DELIVERY PER SEAT (live composer call) " + "-" * 29)
    print(f"{'label':26s} {'entry':>6s} {'cap':>7s} {'delivered':>10s} "
          f"{'sha12':>14s} {'hdgs':>5s}")
    for s in m["per_seat"]:
        print(f"{s['label']:26s} {str(s['has_transform_entry']):>6s} "
              f"{s['cap']:>7d} {s['delivered_chars']:>10d} "
              f"{s['sha12']:>14s} {s['headings_delivered']:>5d}")
    print(f"\n  distinct renders across {len(m['per_seat'])} seats: "
          f"{m['distinct_renders']}")
    print(f"  seats silently inheriting the default: {m['seats_without_entry']}")

    print("\n-- 2. CAP SWEEP: delivered chars as a function of the cap " + "-" * 16)
    for row in m["sweep"]:
        print(f"  cap={row['cap']:>7} -> {row['delivered']}")

    print("\n-- 3. THE PARAMETER AT ITS CONFIGURED VALUES " + "-" * 29)
    for cap, delivered in sorted(m["delivered_at_configured"].items()):
        print(f"  cap={cap:>7} -> {delivered}")
    values = list(m["delivered_at_configured"].values())
    inert = len(set(values)) == 1
    print(f"\n  configured values: {m['configured_caps']}")
    print(f"  distinct outputs over configured values: {len(set(values))}")
    print(f"  VERDICT: parameter is {'INERT' if inert else 'LIVE'} over its "
          f"configured range")

    print("\n-- 4. DERIVED STEP FUNCTION " + "-" * 46)
    lo, hi = m["minimal_chars"], m["core_chars"]
    print(f"  deliver(c) = ValueError   for c <  {lo}")
    print(f"  deliver(c) = {lo}         for {lo} <= c < {hi}")
    print(f"  deliver(c) = {hi}        for c >= {hi}")
    print(f"  All configured caps lie in [{lo}, {hi}) -> d(deliver)/d(cap) = 0")

    print("\n" + "=" * 74)
    if inert:
        print("CONCLUSION: `max_directive_chars` carries 4 distinct configured")
        print("values and 1 distinct behaviour. It is an addition nothing")
        print("reaches, in the sense the additive standard names. A removal is")
        print("EVIDENCED by this measurement rather than judged -- but see")
        print("bench/tests/test_falsifier_directive_cap_inert_2026-10-14.py for")
        print("the property that must hold AFTER any removal.")
    else:
        print("CONCLUSION: the parameter is live; the inertness claim is REFUTED.")
    print("=" * 74)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Measure whether max_directive_chars affects any output.",
    )
    ap.add_argument("--json", action="store_true", help="emit raw JSON instead")
    args = ap.parse_args(argv)
    m = measure()
    if args.json:
        import json
        print(json.dumps(m, indent=2, default=str))
    else:
        report(m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
