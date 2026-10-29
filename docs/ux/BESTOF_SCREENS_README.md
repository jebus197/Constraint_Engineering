# CDSFL UX — Best-of mockup pack (2026-10-23)

## Why this pack exists

Later rebuild passes sometimes **stubbed** screens (Discourse, Findings, etc.). Earlier versions had **fuller** renders of those same tabs. This pack **does not invent new pixels** — it selects the **most complete surviving screenshot** for each surface from v3 / v5 / v6 / light, and keeps **alternates** where two versions are both strong but differ.

**Authoritative behaviour spec** remains:
`docs/CDSFL_UX_Design_Brief_AUTHORITATIVE_for_Orchestrator.md`

Screens are **illustrative**. Where a primary screen is missing a later agreed control (e.g. “Help for more details”), prefer the **spec** over the older pixel layout.

---

## Primary screens (recommended starting set)

| File | Source | Why chosen |
|------|--------|------------|
| `01_orchestrator_v6.png` | v6 | Load experiment · Generate/View findings report · Help for more details |
| `02_findings_v5.png` | v5 | Full findings table + status chips |
| `03_evidence_v5.png` | v5 | Full evidence panel |
| `04_explorer_v6_RetrospectivePredictive.png` | v6 | Correct mode names (Retrospective / Predictive), named experiment, chart-primary intent |
| `05_discourse_v3_full.png` | v3 | Richest STEM categories + thread cards (later v6 Discourse was stubbed blank) |
| `06_recipes_v5.png` | v5 | Full recipe / new-experiment surface |
| `07_hil_v5_full.png` | v5 | Full HIL detail, equations area, comments, View in registry |
| `08_advanced_v5.png` | v5 | Advanced settings surface |
| `09_view_registry_v5.png` | v5 | Registry view |
| `10_registry_finding_detail_v5.png` | v5 | Unfiltered finding record |
| `11_settings_models_v6.png` | v6 | Models & roles · search · Orchestrator role |
| `12_add_model_peer_v6.png` | v6 | Peer aggregate counts · expand · instance stats |
| `13_peer_donation_v6.png` | v6 | Donation ≠ roster · model seats |
| `14_help_orchestrator_tour_v6.png` | v6 | Numbered Help graphic + legend (Orchestrator) |
| `15_help_explorer_tour_v6.png` | v6 | Numbered Help graphic + legend (Explorer) |

## Alternates (choose if you prefer)

| File | Notes |
|------|--------|
| `01_orchestrator_v5.png` | Earlier orchestrator chrome; may lack Generate findings report wording |
| `04_explorer_v5_fullerCharts.png` | Denser Stage-5 controls / charts; mode labels still “Before/After running” (superseded naming) |
| `05_discourse_v5.png` | Slightly tighter Discourse; still full categories |
| `05_discussions_light.png` | Early light-theme discussions |
| `02_findings_v3.png` / `03_evidence_v3.png` / `06_recipes_v3.png` | Earlier complete variants |
| `07_hil_v3.png` / `07_hil_light.png` | Earlier HIL variants |

## Known gaps vs full agreed spec

No single historical PNG has **every** later agreement at once. When combining:

1. **Help for more details** + Help tab tours → use v6 Help / Orchestrator / Explorer primaries.  
2. **Full Discourse** → use v3 primary (not v6 stub).  
3. **Retrospective / Predictive** naming → use v6 Explorer primary; borrow chart density from v5 alternate if useful.  
4. **HIL comments + registry** → use v5 HIL primary.  
5. **Peer catalogue / donation / Orchestrator role** → use v6 settings primaries.  

Orchestrator implementers should merge **layout richness from primaries** with **behaviour from the authoritative brief**.

## html_sources/

Raw HTML from v3, v5, v6 for reconstruction. Prefer screenshot + brief over HTML if they conflict on later naming (modes, Help pattern).

---

*Assembled 2026-10-23 from surviving artifact trees only.*

## Update 2026-10-24

- **`13_peer_donation_v6.png`** replaced with the **full** donation settings (toggles, model seats table, caps, grant status). Previous primary was a stub.
- **`11_settings_models_v6.png`** and **`12_add_model_peer_v6.png`** re-rendered with fuller roster / peer catalogue detail.
- Other primaries (Findings, Evidence, Discourse, HIL, Recipes, Registry, Advanced) were already taken from complete **v3/v5** renders and did not need fill-in.

## Update 2026-10-24 (evening)

- Orchestrator: single contained chat vessel; compose bar includes **+** for file select/upload.
- Donation settings primary is the full controls version.
- Settings / Add model peer catalogue refreshed earlier same day.
