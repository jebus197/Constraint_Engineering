# examples/ — Ready-to-Use Configuration Templates

Plain-text, copy-and-adapt templates for getting started with CDSFL in
an everyday tooling setup. These complement the abstract template
material under [`resources/configs/`](../resources/configs/) and the
populated experimental configurations under
[`bench/exp39_configs/`](../bench/exp39_configs/).

## Contents

- **[CLAUDE.md.example](CLAUDE.md.example)** — a working `CLAUDE.md`
  implementing the CDSFL methodology (P-pass, Extended P-pass,
  constraint classification, verification flags, behavioural
  constraints). Copy to `~/.claude/CLAUDE.md` for global application or
  to your project root for project-specific behaviour, then adapt.
  Derived from a production configuration with personal preferences
  removed.

- **[structural_building.txt.example](structural_building.txt.example)** —
  a concrete domain expert encoding for structural engineering (steel
  and concrete multi-storey buildings, Eurocode + AISC). Shows the
  HARD / SOFT constraint format with real code-referenced capacity
  equations, load combinations, deflection limits, buckling curves,
  connection rules, and limitation boundaries. Copy as a starting
  model when writing a new domain encoding in the plain-text style.

## Conventions

The `.example` suffix is deliberate: copy the file, rename to drop the
suffix, then adapt. Keeping the originals unmodified preserves them as
reference templates that survive git pulls without conflict.

## Where to look next

- Abstract template structure: [`resources/configs/`](../resources/configs/)
- Populated CDSFL bench configurations (JSON): [`bench/exp39_configs/`](../bench/exp39_configs/)
- Full methodology reference: [`docs/REPRODUCING.md`](../docs/REPRODUCING.md)
