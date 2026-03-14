# Domain-Specific Constraint Directives

## The "Box" Metaphor

Each domain directory contains **constraint boxes** — curated sets of known,
fixed constraints that apply to common project types within that engineering
domain.  They encode the physics, standards, safety requirements, and
established practice that a domain expert would check by reflex.

These boxes are **starting points, not complete constraint sets.**  They
provide the framework within which domain experts add their own
project-specific constraints.  Think of them as the walls of the testing
enclosure — the expert fills in the contents.

## How Layering Works

Directives compose in layers, mirroring how Claude Code's CLAUDE.md works:

```
┌─────────────────────────────────────┐
│  Universal CDSFL directives         │  ← always present (cdsfl_core.txt)
│  (falsification loop, constraint    │
│   classification, epistemic flags)  │
├─────────────────────────────────────┤
│  Domain-specific directives         │  ← loaded per task domain
│  (physics, standards, safety for    │
│   the specific engineering field)   │
├─────────────────────────────────────┤
│  Project-specific constraints       │  ← added by the expert
│  (their own variables, limits,      │
│   acceptance criteria)              │
└─────────────────────────────────────┘
```

The benchmark runner composes layers 1 and 2 automatically.  Layer 3 is
what the expert brings.

## Usage

```bash
# Default: universal directives only (existing behaviour)
python3 run_benchmark.py --dry-run

# Universal + domain-specific (loads first variant per domain)
python3 run_benchmark.py --dry-run \
  --domain-directives bench/directives/ \
  --condition universal+domain

# Specific variant per domain
python3 run_benchmark.py --dry-run \
  --domain-directives bench/directives/ \
  --condition universal+domain \
  --variant building

# Domain-specific only (ablation study — no universal layer)
python3 run_benchmark.py --dry-run \
  --domain-directives bench/directives/ \
  --condition domain-only
```

## Directory Structure

```
directives/
  universal/
    cdsfl_core.txt            ← extracted universal directives
    cdsfl_core_formal.md      ← dual prose + mathematical representation
  hardware/
    hardware_embedded.txt     ← IoT / embedded systems
    hardware_rf.txt           ← RF and high-speed PCB
    hardware_power.txt        ← power electronics
  software/
    software_distributed.txt  ← distributed systems
    software_security.txt     ← security-critical
    software_realtime.txt     ← real-time / embedded software
  chemistry/
    chemistry_process.txt     ← process chemistry / scale-up
    chemistry_pharma.txt      ← pharmaceutical synthesis
    chemistry_analytical.txt  ← analytical methods
  logistics/
    logistics_maritime.txt    ← maritime / shipping
    logistics_supply_chain.txt ← supply chain / warehousing
    logistics_cold_chain.txt  ← temperature-controlled
  biomedical/
    biomedical_device.txt     ← medical devices (ISO 13485)
    biomedical_pharma.txt     ← pharmaceutical formulation
    biomedical_clinical.txt   ← clinical trial design
  industrial/
    industrial_injection.txt  ← injection moulding
    industrial_cnc.txt        ← CNC machining
    industrial_welding.txt    ← welded fabrication
  structural/
    structural_building.txt   ← building design
    structural_bridge.txt     ← bridge design
    structural_temporary.txt  ← temporary works
  product-engineering/
    product_consumer.txt      ← consumer products (CE/UL)
    product_automotive.txt    ← automotive components
    product_industrial_eq.txt ← industrial equipment
  cross-domain/
    cross_thermal_electrical.txt     ← thermal-electrical interface
    cross_software_hardware.txt      ← software-hardware interface
    cross_mechanical_electrical.txt  ← mechanical-electrical interface
```

## Directive File Format

Each `.txt` file follows this structure:

```
# Domain: <domain name>
# Variant: <project type>
# Version: 1.0
# Layers-on: universal/cdsfl_core.txt
#
# STARTING POINT — not a complete constraint set.
# Domain expertise and project-specific knowledge still required.

[HARD constraints — non-negotiable]
...

[SOFT constraints — negotiable]
...

[Verification procedures]
...

[Limitations — what this box does NOT cover]
...
```

## Mathematical Formalisation

Where constraints have genuine mathematical structure, they include inline
formal notation alongside prose:

```
Deflection limit (floor beams, brittle finishes):
  δ_max ≤ L / 360
  where δ = 5wL⁴ / (384EI) for simply supported uniform load
```

Not every constraint is formalisable.  Behavioural directives ("check that
the load path is complete") stay prose-only.  The classification summary
in `cdsfl_core_formal.md` documents which universal directives are
formalisable and which are not.

## Creating Custom Domain Directives

1. Copy an existing directive file as a template
2. Replace the constraints with those specific to your domain/project type
3. Classify each constraint as HARD or SOFT
4. Add mathematical notation where it adds genuine precision
5. Include a Limitations section — state what the box does NOT cover
6. Place the file in the appropriate domain directory (or create a new one)

## Limitations

These directive sets:

- Are **starting points**, not exhaustive constraint catalogues
- Require **domain expertise** to evaluate, extend, and apply correctly
- Reference standards and codes that **may be superseded** — always verify
  against the current edition [VERIFY:current]
- Cannot substitute for **project-specific engineering judgment**
- Are only as useful as the model's ability to **follow directives** — user
  vigilance against model breakout (escape from the constraint box) remains
  essential
