# resources/configs/ — Domain Expert Encoding Templates

Template material for third-party authors writing CDSFL domain expert
encodings. A domain expert encoding is a portable, reusable cognitive
configuration that any CDSFL-compliant model can load to operate at
expert level in a given domain.

## Contents

- **[example_domain_expert_config.md](example_domain_expert_config.md)** —
  Structural template showing the three-layer schema: universal
  methodology, domain-specific directives, individual personalisation.
  Copy and adapt.

- **[methodology_reference.md](methodology_reference.md)** — The
  universal methodology layer. Copied verbatim into new encodings; do
  not modify without a documented reason.

## Populated Examples

The templates above are deliberately abstract. For working examples of
the same artefact class, populated with real domain directives and used
in CDSFL bench experiments, see
**[bench/exp39_configs/](../../bench/exp39_configs/)**. These cover
mathematics, physics, chemistry, biology, computer science, information
science, engineering, statistics, composition, cross-domain reasoning,
and several cell-specific encodings.

## Intent

Domain expert encodings are envisaged as a tradable, conservable
cognitive asset. A qualified domain expert writes the encoding once; it
can then be swapped, shared, iterated upon, or offered on an open
marketplace, and be trivially loaded within the CDSFL schema so that
expert knowledge is treated as a fungible asset across domains of human
endeavour. The templates in this folder are the starting point; the
populated examples in `bench/exp39_configs/` demonstrate the
fully-developed form.
