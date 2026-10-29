# CDSFL UX — Authoritative Design Brief for the Orchestrator

**Date:** 2026-10-21  
**Status:** Single source of truth for product shell behaviour  
**Audience:** Orchestrator / build model and human implementers  

**Note on mockup PNGs:** Iterative HTML screenshot packs were partially degraded in later turns (some tabs reduced to stubs). **Do not treat incomplete screenshots as the spec.** This document and the live repo (registry, explorer, experimental notes) are authoritative. Rebuild UI from this brief + codebase.

---

## 1. Product identity

CDSFL is a **local-first general-purpose STEM calculator and experiment instrument**, not a multi-tenant chat website and not a configuration console for its own internals.

**Primary metaphor:** science journal + calculator  
**Primary surface:** Orchestrator  
**Primary path:** Load or start experiment → run → read findings → optional human decisions → optional risk-dynamics explorer  

**Default language:** plain formal English accessible to informed novices and experts. Schema key names (`stop_rule`, `hard_veto`, `fail_closed_unassessed`, …) belong in **docs** and **Settings → Advanced**, not on first-open chrome or footers.

---

## 2. Non-negotiable behavioural rules

1. Claims are **not** cleared by chat, Discourse, or comments. Only mechanical checks and explicit human residual acceptance settle outcomes.
2. The **Orchestrator** seat is bound by the same experimental rules as other seats. Binding is behaviour; the tab is simply named **Orchestrator**.
3. The Explorer models residual-risk **dynamics**; it does not forecast live runs and does not settle claims.
4. **Solo / local use is complete.** Peer capacity is optional, default **off**.
5. **Defaults first.** Deep tunables live under Settings → Advanced.
6. Accuracy over speed remains an acceptable trade.

---

## 3. Top-level information architecture

**Tabs (left → right):**  
Orchestrator · Findings · Evidence · Explorer · Discourse · Recipes · HIL · Settings · **Help**

| Tab | Purpose |
|-----|---------|
| **Orchestrator** | Main work: load experiment, instruct run, generate/view findings report |
| **Findings** | Claim list and status (tools / open / needs human decision) |
| **Evidence** | Mechanical evidence for one finding |
| **Explorer** | Stage-5 risk-dynamics calculator (chart-primary) |
| **Discourse** | STEM discussion, help, apply to join experiments (does not clear claims) |
| **Recipes** | High-level new experiment / domain / mode / max passes |
| **HIL** | Human review queue: plain detail, comments, view in registry |
| **Settings** | Models & roles, paths, peer master switch; **Advanced** sub-area |
| **Help** | Searchable guided help; numbered graphic + legend per topic |

**Platform:** local-first desktop shell (window chrome), light theme, solid outer edge, rounded corners. Not pure browser-SaaS chrome as the product identity.

---

## 4. Global Help (agreed pattern)

- **No** scattered circular blue `?` help icons in the chrome.
- On every primary tab **except Help**: a consistent control labelled **“Help for more details”** (same place in the top chrome).
- Click → switch to **Help** tab and **jump** to the article for the tab (or control) you came from.
- **Help tab** is highlighted **only when active** (never permanently highlighted on other tabs).
- Help article layout:
  - **Majority of width:** annotated graphic / HTML mock of that tab with **numbered callouts** on elements.
  - **Right column:** vertical legend — number → plain explanation of what that element does.
  - **Search field** over the **entire** Help library.
- Full multi-domain Explorer essay: `docs/Explorer_Meta_Tooltip_for_Orchestrator.md` (linked from Explorer Help article / Read more). Parameter micro-copy may stay minimal on sliders; long explanation lives in Help.

---

## 5. Orchestrator tab

- Title: **Orchestrator** (not “Bounded orchestrator”).
- **Load experiment**.
- Instruction / chat stream with the bound orchestrator.
- **Generate findings report** (preferred label over “Print findings”).
- **View findings report** — enabled only after a report exists for this run.
- Report pipeline: plain technical English from experimental notes; if missing, generate unfiltered experimental note **and** plain report; optional save path from Settings.
- Run context: experiment id, status, open items, peer on/off in plain language.
- Footer (all default tabs): e.g. *Evidence settles claims · discussion does not · human decisions when checks cannot finish* — **no** internal protocol key names.

---

## 6. Findings, Evidence, HIL

**Findings:** table of claims with plain status vocabulary and a one-line legend:
- Confirmed by tools  
- Still open  
- Needs human decision  

**Evidence:** claim text, mechanical path, re-run control, residual in plain language.

**HIL:**
- Queue of escalated items.
- Detail panel: **full plain technical English** (from experimental notes style); equations rendered; **no** heavy markdown noise.
- **Add comments** (instruct models; comments **do not** clear residual risk).
- **Approve / Reject / Request evidence**.
- **View in registry** → unfiltered technical record.

---

## 7. Explorer (Risk dynamics explorer)

**Naming in UI:** prefer **Risk dynamics explorer** (or “Risk dynamics”) over software-only “residual risk calculator.”

### Modes
- **Retrospective Mode (default):** bind to **last run**, **name the experiment**, show residual-risk and marginal-yield for that run; **Select a different experiment**. Only mode that refers to past runs.
- **Predictive Mode:** **fully predictive**; researcher-set parameters only; **no** last-run name, binder, or select-experiment control; not a forecast of live outcomes.

### Layout (non-negotiable)
- **Charts primary** (large residual-risk + marginal-yield) — at-a-glance is the point.
- **Parameters secondary** (side column): π, p, η, σ, ν, θ, perturbation; trust view; naive baseline; presets (healthy / ideal / leaky / futile).
- Do not demote the graphic to a tiny corner.

### Caveat (always visible, plain language)
Models residual-risk dynamics under stated assumptions. Retrospective interprets a named experiment’s record. Predictive explores parameters you set. Does **not** settle claims. Live stop behaviour depends on the experiment’s checks and human decisions when escalated.

### Why it exists (Help / docs)
Not only “bugs left after n code passes.” Stage-5 loop: detection → resolution → re-injection. Same shape in physics/instrumentation, chemistry/process, biology/assay, engineering control. Full domain tables and can/cannot text: `Explorer_Meta_Tooltip_for_Orchestrator.md`. Read more → technical note → Mathematical Appendix Stage 5.

---

## 8. Discourse (must not be blank)

Full STEM discussion surface, not an empty placeholder.

- Banner: **Discussion does not settle experimental claims.**
- Category list aligned with registry domains, e.g.: Mathematics & formal methods; Physics & dimensional analysis; Chemistry & materials; Biology & life sciences; Software & computer science; Engineering & systems; Statistics & uncertainty; Information science; Cross-domain; Experiments & collaboration.
- Actions: New discussion; Apply to an experiment; optional share outcomes.
- Thread list with title, subject area, status/reply counts.
- **Sample content for implementers:** at least one **non-software** thread that discusses explorer output for a named experiment (interpretation only).
- One expanded category view is enough to define the list pattern; other categories reuse it.
- Peer **admission** may mint a **scoped experiment grant** (capability token / API key: experiment id, role, resource class, expiry). Discourse does not schedule jobs or clear science.

---

## 9. Recipes

High-level only: target path, domain, Live vs Simulated, max passes (default 5), peer off/on (approved grants only), recipe presets (e.g. standard multi-model, math-heavy, simulated shakedown). Deep switches stay in Advanced.

---

## 10. Settings — Models & roles

- **Search** across Local, OpenRouter, Peer (peer only if enabled and grants exist).
- **Add model** from: Local (detect/browse) · OpenRouter (catalogue search) · Peer (grant-scoped).
- **Roles:** **Orchestrator** (usually exactly one in presets) · Worker · Researcher · Classifier.
- Recommended presets match current harness practice.
- Roster table: model, source, role, change control.

### Peer catalogue (fundamentals before mass auto-dispatch)
1. Aggregate by vendor + model version (e.g. Opus 5.5, Gemini 3.1) with **count available**.
2. Expand → instances sorted by **lowest latency / strongest free resources**.
3. Instance details: latency, uptime, location (if known), CPU/GPU class, memory, storage, **available / busy**.
4. User **adds N seats** explicitly (small tasks may need only a few models).

### Paths & reports
Experimental notes directory; plain report save path.

### Peer master switch
Default **off**. Link to donation settings.

---

## 11. Settings — Peer donation (separate from roster)

What this machine **offers** (not what the current experiment uses):

- Spare CPU/GPU cycles; headless worker; temporary storage; full local runner (**elevated**).
- **Installed models as seats** — per-model toggle, allowed roles, max concurrent — **distinct from full harness donation**.
- Caps (max concurrent jobs, daily time).
- Grant status panel.

**Deferred:** automated fair allocation of raw cycles/storage across many researchers. Seat selection + grants first.

---

## 12. Settings → Advanced

- Full registry-tunable surface; **HARD** items not user-weakenable in UI.
- Schema default vs experiment default where schema `0.0` means *off* (e.g. churn): show operational recommendation for real multi-round runs, not a nonsense zero.
- Donation matrix may also be reachable here.
- Not required for a default solo experiment.

---

## 13. Peer-to-peer product rules

1. Default off; solo path complete.  
2. Donation = offer, not obligation.  
3. Model-seat donation ≠ full runner.  
4. Peer models in Add only with scoped grant.  
5. Owner’s checks and HIL still own residual risk.  
6. Remote work returns signed execution receipts into owner provenance.  
7. Trust/participation (Genesis-aligned) affects **admission**, not claim clearance.  
8. Massively distributed auto-dispatch is a later phase.

---

## 14. First-run tutorial (dismissible)

1. Welcome — local STEM instrument; evidence settles claims.  
2. Orchestrator — load, run, findings report.  
3. Findings / Evidence / HIL.  
4. Explorer — chart-primary; modes; open Help for more details once.  
5. Discourse — does not clear claims.  
6. Settings — models including Orchestrator role; peer off; Advanced optional.  
7. Where **Help for more details** lives.  

“Show tutorial again” under Settings.

---

## 15. Implementation order

1. Orchestrator + Load experiment + Generate/View findings report  
2. Findings / Evidence / HIL (plain detail, comments, registry)  
3. Explorer Retrospective default + Predictive + chart-primary layout  
4. Recipes + Settings models/roles (**Orchestrator** role, search, Add)  
5. Help system (button, tab, search, numbered graphic + legend per tab)  
6. Discourse full categories + non-software sample thread  
7. Peer donation + peer catalogue aggregates (grant-gated)  
8. Advanced = registry surface  
9. Tutorial  

Scientific integrity of the local instrument precedes network features.

---

## 16. Acceptance checks

- [ ] All top tabs present including Help (Help only highlighted when active)  
- [ ] “Help for more details” on every tab except Help  
- [ ] Help = searchable + numbered graphic + right legend for at least Orchestrator and Explorer  
- [ ] Orchestrator: Load experiment, Generate/View findings report state machine  
- [ ] Findings legend in plain language  
- [ ] HIL: plain detail, comments, view in registry  
- [ ] Explorer: Retrospective default with named last run + select different experiment; Predictive fully predictive; charts primary  
- [ ] Discourse: categories, banner, non-empty thread UI (not a blank stub)  
- [ ] Models: search, Add Local/OpenRouter/Peer, Orchestrator role  
- [ ] Peer: aggregates, expand, instance stats; donation ≠ roster  
- [ ] Default surfaces free of schema key-name clutter  
- [ ] Full Explorer multi-domain note available via Help / docs  

---

## 17. Supporting docs in this package

| File | Role |
|------|------|
| `Explorer_Meta_Tooltip_for_Orchestrator.md` | Full multi-domain Explorer explanation (physics, chemistry, biology) |
| `Explorer_Read_More_Technical_Note_Outline.md` | Layer-3 maths path outline |
| `README_HELP_PATTERN.md` | Short Help pattern reminder |

Live repo remains source for registry keys, explorer Stage-5 controls, and experimental note tone for HIL copy.

---

*End of authoritative brief.*
