# CDSFL UX Vision Sketch, 28 March 2026

**Preserved into the repository 2026-08-06 02:15 .** Early UX vision sketch. Historical; retained because it is the only record of the interface intent behind later decisions.

**Provenance.** This is the plain-text text-to-speech document from `~/Desktop/CDSFL_tts/CDSFL_UX_Vision_Sketch_2026-03-28.txt`,
preserved VERBATIM below rather than rewritten. It is a record, and rewriting a record is a fault in
this project. It was cited by name in `RECOVERY.md`
while existing on one machine's Desktop only — and `resources/RECOVERY.md` opens by promising a reader
can rebuild everything from the repository alone. That promise now holds for this document.

---

CDSFL UX Vision Sketch, 28 March 2026

This is an interim architectural sketch for the CDSFL user experience layer. It captures the design intent before compaction can lose it. The UX will be built after Experiment 11 completes. Nothing here is final. Everything here is falsifiable.


What the UX is for

CDSFL is a methodology that makes AI assisted technical work more reliable by coupling generation with iterative falsification. The distributed compute protocol extends this by running multiple models independently and synthesising their findings. The UX makes both of these accessible to users who are not building from the command line.

The UX is the runnable proof of concept. It is the thing that turns a research methodology and a collection of Python scripts into something a practitioner can actually use. The user picks their models, assigns roles, provides their API keys or uses a CLI subscription, selects their domain constraints, and runs the protocol. They watch it progress. They review the outputs. They get a verified result.

This is not a chatbot interface. It is an orchestration and policy management interface with structured, observable, auditable outputs.


The three UX surfaces

The UX has three main surfaces. They are distinct but share the same backend.

Surface 1 is the Orchestration Console. This is where the user configures and runs a distributed compute session. It covers model selection, role assignment, phase progression, output display, and convergence tracking. Everything that Experiment 11 does manually, this surface does through a graphical interface.

Surface 2 is the Registry and Group Policy Editor. This is where the user manages the hierarchical constraint system. It covers the five layer policy hierarchy, from universal constraints down through domain, task, model, and runtime layers. It includes monotonicity enforcement, which means lower layers can tighten constraints but never weaken the hard constraints set above them. This surface replaces manual TOML editing with a structured interface.

Surface 3 is the Domain Configuration Manager. This is where domain expert configurations are created, tested, and shared. It covers the three layer config structure of methodology plus domain directives plus personalisation. Practitioners can build and share domain boxes, which are the constraint packages for specific fields like structural engineering, distributed software, pharmaceutical chemistry, and so on.


Surface 1, the Orchestration Console

The Orchestration Console maps directly to the distributed compute protocol. Every operation described in the Experiment 11 execution plan has a corresponding interface element.

Model Selection. The user sees a list of available models with their API requirements. Each model shows its vendor, its model ID, and what authentication it needs. The user can add models by providing an API key for that vendor, or by connecting a CLI subscription like Codex. The backend reads this from a configuration dataclass, not from hardcoded values. The model list is extensible. When a new model becomes available, the user adds it. No code change required.

Role Assignment. Once models are selected, the user assigns roles. The available roles are collator, player manager, and participant. There must be exactly one collator and one player manager. Everything else is a participant. The interface enforces these constraints. The user drags models into role slots or selects from dropdowns. Role assignment is parameterised in the backend, which means the same model could be collator in one session and participant in another.

System Prompt Configuration. For each model, the user sees what system prompt it will receive. Bare metal models receive only the CDSFL core formal prompt. Factory configured models like Codex show that they carry a vendor prompt plus CDSFL elevated directives. The user can inspect but not edit the CDSFL system prompt. They can choose which domain layer to add on top. This is the link between Surface 1 and Surface 2.

Phase Progression. The console shows the current phase with a progress indicator. Preflight verification, Phase 0 through Phase 6. Each phase shows which models have been dispatched, which have responded, and whether any circuit breaker conditions have triggered. The user sees a live status for each model during dispatch. Green means response received. Yellow means waiting. Red means error or halt.

Circuit Breaker Display. If any halt condition triggers, the console shows what happened, which model, what phase, and what was received. The user decides whether to fix and resume, re-run the phase, or proceed without the failed model. This maps directly to the three resume options in the execution plan.

Output Viewer. Each model's response is displayed in a structured format showing the CDSFL fields, verdict, evidence, constraint class, confidence, strongest objection, and response. The synthesis documents from the player manager are displayed separately. The user can compare outputs side by side. All outputs are persisted via the verification chain, which means they are tamper evident and auditable.

Convergence Dashboard. After each round, the console shows the convergence state as reported by the player manager. Agreements at three out of five or better. Disagreements. Unique findings. The diminishing returns calculation. Whether the stop condition has been met. This is purely observational for the user. The player manager makes the convergence decision under CDSFL.

Cost Tracker. The console tracks cumulative API spend across all models and all phases. It shows the budget threshold and current expenditure. If the threshold is approached, it warns the user. If exceeded, it halts automatically.


Surface 2, the Registry and Group Policy Editor

The registry already exists as a four layer TOML based policy engine in bench cdsfl_registry. The UX surface makes this accessible without manual file editing.

Layer View. The editor shows the five layers as a cascading hierarchy. Universal at the top, then domain, task, model, and runtime. Each layer shows its constraints with their classifications. Hard constraints are visually distinct from soft constraints. The user can expand any layer to see all its settings.

Universal Layer. This is read only for normal users. It shows the foundational hard constraints: anti deference, falsification required, hard soft classification, fail closed on unassessed findings, JSON schema required, SymPy auto verify. These cannot be weakened by any layer below. The interface makes this visually clear, perhaps with a lock icon or a different background colour. The universal layer can only be edited through the project's governance process, not through the UX.

Domain Layer. The user selects a domain from the available set. Currently there are ten domains: structural, hardware, chemistry, software, logistics, biomedical, industrial, product engineering, cross domain, and mathematics. Each domain has variants. For example, structural has bridge, building, and temporary. The user picks a domain and variant. The editor shows the domain specific constraints that will be layered on top of universal. The user can create new domain configs, which are saved as new TOML files in the registry.

Task Layer. This is not yet implemented in the registry. The editor will show a placeholder indicating that task specific constraints can be added here. When implemented, the user will be able to define constraints that apply to a specific task within a domain. For example, a seismic analysis task within the structural domain might add specific constraints about dynamic loading that do not apply to all structural tasks.

Model Layer. The editor shows model specific tuning for each model in the session. Currently these are small files adjusting timeouts, reasoning effort, and structured output capability. The user can view and adjust these. The monotonicity rule applies, so the user cannot use model tuning to weaken a hard constraint from a higher layer. The editor prevents this and explains why.

Runtime Layer. This covers session level settings like maximum rounds, stop rule configuration, blind first enforcement, and peer support minimum families. These are currently in universal.toml but conceptually belong to a runtime context that can be adjusted per session without changing the permanent universal config.

Monotonicity Enforcement. The editor enforces monotonicity visually. If the user tries to set a domain layer value that would weaken a universal hard constraint, the editor shows an error explaining the conflict. The user cannot save a policy that violates monotonicity. This is already implemented in the registry's Python code via PolicyViolationError. The UX surfaces this as a clear user facing message rather than a stack trace.

Policy Validation. The user can run a validation check that tests all their configured layers for consistency. This calls validate_all_policies from the registry module. The results are displayed as a pass fail report with specific conflicts highlighted.


Surface 3, the Domain Configuration Manager

Domain configurations are the portable, shareable packages that encode domain expertise. The configs directory already has a three layer template: methodology, domain directives, and personalisation.

Config Builder. The user starts from the methodology layer, which is always included. They add domain specific directives by selecting hard and soft constraints relevant to their field. They add verification methods that describe how claims in that domain should be checked. They add limitations that describe what the domain box does not cover. They can add a personalisation layer for their own workflow preferences.

Config Testing. The user can test a domain config against a sample task to see how it affects model output. This runs a single dispatch with the composed directives and shows the structured result. It does not run a full distributed compute session. It is a quick check that the config produces the intended constraint behaviour.

Config Sharing. Domain configs are TOML and markdown files. They can be exported, shared, and imported. A structural engineer builds a structural domain box. A pharmaceutical chemist builds a pharma domain box. Each is portable. The user imports a shared config and it appears in their domain list for Surface 2.


API Key and Authentication Integration

The UX supports multiple authentication paths because different users have different access patterns.

API Key Entry. The user provides API keys for each vendor they want to use. The keys are stored locally, never transmitted to our servers, never logged. The UX validates each key by making a lightweight API call before allowing model selection. Keys can be entered per vendor: OpenRouter, Google, DeepSeek, OpenAI, Anthropic.

CLI Subscription. For models available via CLI subscription, like Codex via codex exec or Claude via the Anthropic CLI, the user authenticates through the CLI's own auth flow. The UX detects available CLI tools and their auth status. If Codex is installed and authenticated, it appears as an available model. If Claude CLI is installed, it appears with a note about which model tier the subscription provides.

Mixed Authentication. The user can combine API keys and CLI subscriptions in the same session. For example, Claude via CLI subscription as collator, Codex via CLI as participant, ChatGPT via OpenRouter API key, Gemini via Google API key, DeepSeek via DeepSeek API key. The orchestration backend accepts any combination because API key handling supports multiple sources by design.

Cost Visibility. For API key users, the estimated cost per model per phase is shown before the session starts. The user sees the total estimated cost for the full protocol. This uses token estimates and published pricing. The actual cost is tracked during execution via the cost tracker in Surface 1.


What exists now versus what needs building

The following already exists and is functional.

The CDSFL core formal system prompt, 290 lines, dual mathematical and textual representation. This is the methodology layer that every model receives.

The registry and policy engine, 391 lines of Python with monotonicity enforcement, four layer hierarchy, deep merge, and policy validation. Five domain configs, five model configs, one universal config.

Domain directives, 28 files across 10 domains with up to 3 variants each. Each is a structured constraint package with hard constraints, soft constraints, verification procedures, and limitations.

The benchmark runner, which implements correct per model system prompt delivery for all five current models. This includes the composition logic for layering universal plus domain directives.

The evaluation engine with three layer fault detection, per pass accumulation, and corroboration curve fitting.

The verification chain for tamper evident record keeping. 790 lines, 97 tests, RFC 9162 Merkle trees.

The distributed compute protocol document and the Experiment 11 execution plan with circuit breaker, preflight verification, and all infrastructure configuration.

The following does not yet exist and needs building.

Task layer in the registry. The registry supports it architecturally but no task specific TOML files exist and the loading code has not been connected.

Runtime layer as a distinct concept. Currently runtime settings live in universal.toml. They need to be separated so that session level adjustments do not require editing the universal config.

The orchestration module. This is the programmatic backend that the Experiment 11 execution plan describes. It does not yet exist as callable code. Experiment 11 will be run manually, with me dispatching API calls. Phase 6 of the experiment produces an implementation. The UX readiness design constraint in the plan ensures that implementation is architected for future UX integration.

The UX itself. No web framework, no frontend, no API server. This is all to be built after Experiment 11.

The OpenRouter calling function for bare metal CC2 and ChatGPT. Needed for Experiment 11 and will become part of the orchestration module.


Platform and model agnosticism

CDSFL is platform agnostic and model agnostic by design. The methodology works with any model that can follow structured instructions. The system prompt is plain text. The structured output format is six fields. Any model that can produce these fields can participate.

The UX must preserve this agnosticism completely. The model selection interface must not privilege any vendor. Adding a new model means adding a configuration entry, not modifying code. The policy engine already handles this through its model layer configs. The orchestration backend must accept any model that conforms to the dispatch interface: receive a system prompt and a user prompt, return structured text.

This is what makes the UX a genuine proof of concept for CDSFL as a whole. It demonstrates that the methodology is not tied to any specific model, vendor, or infrastructure. A user with only DeepSeek API access can run a single model CDSFL session. A user with five different vendor keys can run a full distributed compute protocol. The methodology scales with available resources.


Relationship to the Registry and Group Policy

The Registry and Group Policy Editor in Surface 2 is the constraint governance interface. It is where organisational policy meets individual practice.

In an organisational context, a team lead or safety officer sets the universal and domain layers. These propagate to all practitioners. Individual practitioners can add task and model layers but cannot weaken the constraints set above them. This is the group policy pattern familiar from enterprise IT, applied to engineering methodology.

In an individual context, a solo practitioner manages all layers themselves. They are their own policy authority. The monotonicity enforcement still applies because it protects against accidental self contradiction, not just against subordinate override.

The registry's existing architecture already supports this. The four layer hierarchy with monotonicity enforcement is the technical implementation of group policy. The UX surfaces it. The missing piece is the task layer, which needs to be connected, and the runtime layer, which needs to be separated from universal.


What happens next

Experiment 11 runs first. It produces the dynamic management and load balancing formalisation plus a working orchestration implementation with UX ready architecture.

After Experiment 11, we build the UX. Surface 1 wraps the orchestration module. Surface 2 wraps the registry. Surface 3 wraps the domain config system. The implementation from Experiment 11 provides the backend. The existing registry provides the policy engine. The existing domain directives provide the content.

The task layer and runtime layer gaps in the registry need to be addressed. These can be done as part of the UX build or as a preparatory step. The fundamental architecture supports them. The implementation work is connecting the loading code and creating the initial task configs.

The result is a runnable proof of concept where anyone with API access to at least one model can use CDSFL structured methodology, and anyone with access to multiple models can run the full distributed compute protocol, all governed by a hierarchical constraint system that enforces methodological discipline without requiring the user to understand the underlying mathematics.
