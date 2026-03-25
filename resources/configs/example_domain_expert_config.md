## CDSFL Domain Expert Configuration — Example Template

This file demonstrates the structure of a CDSFL domain expert configuration.
It is a portable, reusable cognitive configuration designed to be injected as
a system-level prompt at session initialisation.

Three layers. Methodology is universal. Domain directives are specialist.
Personalisation is individual. Replace the placeholder content with your own.

---

### Methodology (Universal — same for all configurations)

Copy the full methodology layer from the reference implementation at:
`resources/configs/methodology_reference.md`

This includes: Core Directives, P-Pass Logic, Non-STEM Rigour Methods,
Verification Rules, Selection Rules, Failure Tracking, Execution Discipline,
Documentation Integrity, Public Attribution, and Style Preservation.

Do not modify the methodology layer unless you have a specific, documented
reason. Changes to methodology should be tested via bench runs before adoption.

---

### Domain Expert Directives (Specialist — varies by domain)

Replace this section with directives specific to your domain of expertise.
These encode WHAT to check and HOW to check it in your field.

Example for structural engineering:

```
`domain-load-path-priority`: In structural review, check load paths first.
All other checks depend on load path integrity.

`domain-safety-factor-verify`: Verify safety factors against the applicable
code (Eurocode, AISC, local jurisdiction). Do not assume a default factor.

`domain-material-fatigue`: For any component subject to cyclic loading,
check fatigue life. Static analysis alone is insufficient.

`domain-connection-detail`: Connections fail more often than members.
Review connection details with at least the same rigour as member sizing.

`domain-boundary-conditions`: Verify that boundary conditions in any
computational model match the physical reality. Fixed vs pinned vs roller
assumptions propagate through every result.
```

These directives are the tradeable asset under the CDSFL schema.
They encode domain expertise in a format that any capable model can apply.

---

### Personalisation (Individual — varies by user)

Replace this section with your personal workflow preferences.

Example:

```
Shorthand: y = yes, d = discuss, p = P-pass, t = continue

Accessibility: [your requirements here]

Communication style: [your preferences here]

Project protocols: [your workflow shortcuts here]

Recovery: [your context recovery procedures here]
```

The personalisation layer is private by default. Share it only if you choose to.

---

### Usage

1. Copy this template.
2. Include the full methodology layer from the reference.
3. Write your domain expert directives.
4. Add your personalisation.
5. Inject the complete file as a system prompt at session start.
6. Verify effectiveness by running CDSFL bench tasks in your domain
   and comparing decay curves with and without the configuration.

The configuration is effective if it produces measurably better analytical
results (higher D, higher v-bar) than the model's default behaviour.

### Future: Constraint Editor Integration

Domain expert configurations will ultimately be directly configurable via
the CDSFL Constraint Editor (CE) — a hierarchical policy engine that manages
universal, domain, task, and model-level configurations. When the CE is
available, this file format will be importable as a policy layer.
