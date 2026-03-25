# CDSFL Domain Expert Configurations

A domain expert configuration is a portable, reusable cognitive configuration
that encodes analytical methodology for use with AI systems. It is structured
as a system-level prompt with three layers:

1. **Methodology** (universal) — The CDSFL cognitive framework. Same for
   everyone. P-pass falsification for STEM, fitness review for design,
   precision review for prose. Named directive IDs for machine-addressable
   policy control.

2. **Domain Expert Directives** (domain-specific) — Encodes domain knowledge,
   HARD constraints, verification methods, and terminology specific to a
   field. A structural engineer's config differs from a biochemist's config
   at this layer.

3. **Personalisation** (user-specific) — Workflow shortcuts, accessibility
   needs, communication preferences, project protocols. Personal to the
   practitioner.

## How to Use

Apply the configuration as a **system-level prompt** at session initialisation.
The methodology should be the environment the model operates in, not
instructions received mid-conversation.

- **Claude Code**: Save as `~/.claude/CLAUDE.md` (global) or as a
  project-level `CLAUDE.md` in your repository root.
- **ChatGPT**: Paste the methodology and domain layers into Custom
  Instructions or the system prompt field.
- **Codex CLI**: Save to `~/.codex/instructions.md`.
- **API usage**: Include as the system message in your API call.

## Examples

- `examples/methodology_only.md` — The universal CDSFL methodology layer.
  Use this as the foundation for any domain expert config.
- `examples/software_engineering.md` — Example domain config for software
  engineering, showing how domain-specific directives layer on top of the
  universal methodology.
- `examples/full_config_template.md` — Complete three-layer template with
  placeholder sections for domain and personalisation layers.

## Relationship to the Constraint Editor

These configurations will ultimately be directly manageable via the CDSFL
Constraint Editor (CE) — a hierarchical policy engine that governs how
configurations are composed, validated, and enforced. The CE merges layers
with monotonicity guarantees: lower layers can add constraints but never
weaken higher-layer HARD constraints. See `bench/cdsfl_registry/` for the
current implementation.

## Verification

The effectiveness of a domain expert configuration is empirically verifiable.
Run the CDSFL bench test with and without the configuration applied. Compare
the (D, v-bar, A, C) capability fingerprint — decay rate, verification score,
total findings, and coverage. A configuration that measurably improves these
metrics on domain-relevant tasks has demonstrated value.
