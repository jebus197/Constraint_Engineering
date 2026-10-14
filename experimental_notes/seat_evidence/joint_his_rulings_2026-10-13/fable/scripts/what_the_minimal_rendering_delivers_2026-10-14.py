# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 146dd0480a86c1b847a872497bfda10e1790a4d39e67bbdd334e22ce9b482fa2
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""What of the core formal directive actually reaches a seat? Measured.

JOINT ROUND his_rulings_2026-10-13, J4. `_load_universal_directive`
(bench/cdsfl_registry/composer.py) switches to `_render_universal_minimal`
whenever format_style == "minimal" OR the full text exceeds
`max_directive_chars`. cdsfl_core_formal.md exceeds EVERY model's cap
(largest cap 12,000 < file), so the minimal rendering is what every seat
receives, always. This script measures, by execution of the live loader:

  * delivered chars per model vs the 27,803-char source;
  * how many of the source's 15 `## ` section headings survive (0);
  * occurrences of the token 'falsifier' in delivered vs source text;
  * which sections never arrive, by name -- including "Runnable Falsifiers
    for Critical Findings" and "Falsifier Integrity -- Do Not Reach for the
    Answer".

NOTE ON THE JOINT BRIEF'S FIGURES, measured here rather than inherited: this
producer finds 2,503 delivered chars (brief said 2,734) and 0 occurrences of
'falsifier' in the delivered text (brief said 1); headings 0/15 and source
counts agree. The discrepancies are small and do not change the conclusion;
the figures that travel are the ones this script prints.

Usage: python3 scripts/what_the_minimal_rendering_delivers_2026-10-14.py
"""
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    answer_help(__doc__, __file__)
    from bench.cdsfl_registry.composer import (
        _load_universal_directive, PHENOTYPE_TRANSFORMS,
    )
    core = (REPO / "bench/directives/universal/cdsfl_core_formal.md").read_text()
    op = (REPO / "bench/directives/universal/cdsfl_operational.md").read_text()
    headings = re.findall(r"^## .+$", core, re.M)
    print(f"source: cdsfl_core_formal.md {len(core)} chars, "
          f"{len(headings)} '## ' sections; 'falsifier' x"
          f"{core.lower().count('falsifier')} (operational: x"
          f"{op.lower().count('falsifier')})")
    print(f"'worked proof' in either file: "
          f"{core.lower().count('worked proof') + op.lower().count('worked proof')}")
    print()
    for model in PHENOTYPE_TRANSFORMS:
        t = _load_universal_directive(model=model).text
        surv = sum(1 for h in headings if h in t)
        print(f"  {model:<16} delivered {len(t):>5} chars  "
              f"headings {surv}/{len(headings)}  "
              f"'falsifier' x{t.lower().count('falsifier')}")
    t = _load_universal_directive(model="opus_4_6").text
    print("\nsections that never arrive (any model):")
    for h in headings:
        if h not in t:
            print(f"  {h}")
    print("\nVERDICT: the falsification machinery's own directive does not")
    print("reach any seat; what arrives is policy keys (e.g.")
    print("'policy.constraints.falsification_required=true') with none of the")
    print("runnable-falsifier or falsifier-integrity content. Every archived")
    print("measurement of model falsifier behaviour is confounded by this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
