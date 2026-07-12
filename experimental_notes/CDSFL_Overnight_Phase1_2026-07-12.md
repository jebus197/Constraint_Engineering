# CDSFL Phase 1 — Overnight Execution Report (technical)

2026-07-12, 02:10 BST.

## Summary

Phase 1 (the pre-Experiment-43 work agreed on 8 July) executed autonomously overnight: a
guarded directive-pruning panel (A1), an ouroboros shadow real-work build (A2), and the
routing rename (A3, formerly `take_up_slack`). §10 (A4) was confirmed already inert. An
isolated adversarial verification pass over A2 and A3 surfaced five confirmed defects,
including one genuine A3 regression bearing on the Experiment 43 = Experiment 42 identity
constraint; all five are fixed. The Claude command-line dispatch route (CC2) is currently
blocked by an expired subscription OAuth session; the fix is a founder-side re-login. No
experiment was launched — the run pauses here for founder review, per instruction.

Commits on `exp39-experimental` (local; pushed at the `sv` accompanying this note):
`df18201` A2, `ef1fe7b` A1, `349951f` A3, `b656549` adversarial-pass fixes.

## A1 — directive-pruning panel review (recommendation only)

A five-model panel (`pr`) reviewed the 43,667-character operational directive for prunable
exposition (history, motivation, narration) without touching the falsification core. Three
prompt guards protected the core, held the mathematics (gamma) out of scope, and framed the
output as hypothesis-not-authority (every cut to be validated by a lean-versus-full ablation).
Four of five models responded (the fifth, CC2 via the command-line route, failed on the OAuth
issue below). Verdict on the pruning method: unanimous SOUND-WITH-CAVEATS. Three of the four
independently named section 18 (the divergence / compelled-convergence exposition) as the
highest-value prune — the same machinery the founder already retired. Convergent compression
targets: sections 18, 17, 16, 7.1 (estimated 7,000–14,000 characters saved by compression
alone, no core touched). Preserved disagreements (not smoothed): section 8 gamma/rho exposition
(Gemini KEEP as mathematics vs DeepSeek COMPRESS as duplicative — this sits on the gamma-guard
boundary and needs founder scrutiny); section 13 (ChatGPT CUT vs DeepSeek KEEP). Not implemented
pre-Experiment-43. Full model responses saved under `bench/logs/confer_directive_pruning_pr_2026-07-12/`.

## A2 — ouroboros shadow real-work (built, proven, shadow-isolated)

The ouroboros cell previously fetched 500-character abstracts and discarded them, emitting a
placeholder candidate string. It now resolves an open-access full-text URL (arXiv-direct, then
Unpaywall, then Sci-Hub only if explicitly enabled), downloads and extracts the text (pypdf,
then pdfplumber; BeautifulSoup for HTML), dispatches a cheap-reader librarian pass (Haiku, then
DeepSeek, then a deterministic no-model extractive fallback), and produces a real distilled
brief that becomes the candidate description. No new dependency was required. Proven live: arXiv
paper 1706.03762 fetched, 24,000 characters parsed and hashed, a real brief produced, the old
placeholder gone. The change is strictly shadow: briefs are logged only, never injected into a
model prompt, never fed to the external-content or novelty channels, and cannot move the
convergence gate. Note (surfaced by the adversarial pass, see below): the frozen Experiment 43
config has no `_ouroboros` block, so the cell does not run in Experiment 43 at all — enabling it
there would be a pre-registration amendment requiring founder sign-off, not done here.

## A3 — routing rename (code-only, behaviour byte-identical)

`take_up_slack` was renamed to `routing` throughout: module, functions (`route`,
`resolve_via_routing`), the `RoutingResult` type, the `_apply_routing` runner helper, the
`routing_enabled` config field, the persisted entry keys, and the log string. All Experiment 42
and 43 config files were left unchanged; a back-compat alias maps the legacy config key
`take_up_slack_enabled` to the new field so behaviour is byte-identical regardless of launch
path. The frozen Experiment 43 pre-registration prose (which names the legacy key) is untouched.
The Experiment 43 config-key rename that the rename plan had suggested was deliberately NOT done,
to protect byte-identity and the frozen pre-registration; it is an optional post-Experiment-43
tidy for founder decision.

## A4 — section 10 (compelled convergence): already inert

Confirmed in prior verification and unchanged here: the `section_10_compelled_convergence` flag
is never passed into the runner config and no compelled-convergence text reaches the dispatched
directive. There is nothing operative to retire. Consequently Experiment 43 is fully
directive-identical to Experiment 42 — a cleaner position than the earlier plan (which framed
"run without section 10" as a deliberate deviation) anticipated. The documentation-only flag
removal is deferred to post-Experiment-43 so the instrument is untouched before the run.

## Adversarial verification pass (14 agents, 5 confirmed, all fixed)

An isolated adversarial pass (four review lenses, each finding then verified by an independent
skeptic instructed to refute it) ran over the A2 and A3 commits. Five findings were confirmed
(five others refuted). One verifier additionally caught a fabricated commit citation inside a
finding and upheld only the substance — the refute-by-default discipline working as intended.
All five confirmed defects are fixed in `b656549`:

1. MEDIUM (genuine A3 regression). `RunnerConfig.from_dict` / `from_json` — the runner's own
   `--config` command-line entry point — lacked the legacy-key alias, which had been added only
   to `launcher_core`. So `RunnerConfig.from_json(exp43_config).routing_enabled` returned False
   (routing silently off) while the launcher path returned True. Launching Experiment 43 via the
   runner command-line, rather than `launch_exp42.py`, would have run with capability-aware
   routing off — diverging from the Experiment 42 landmark, a direct hit on the "identical to
   Experiment 42" constraint. The earlier A3 verification exercised only the launcher path and
   missed this. Fix: the same alias is mirrored in `from_dict`; both ingestion paths now yield
   `routing_enabled=True` for the Experiment 42 and 43 configs. Regression test added.
2. LOW. `_download_and_extract` re-raised on a network exception despite a "Never raises"
   docstring (the timeout wrapper re-raises worker exceptions; the call site was unguarded),
   which discarded a whole round's briefs instead of degrading per paper. Fix: the call is
   guarded to an error field, and the per-paper loop is wrapped so one paper's failure cannot
   lose the round. Regression tests added.
3. LOW. The 20-megabyte download cap was bypassable when a server omits `Content-Length`
   (`r.content` buffers the entire body before the size slice). Fix: streamed download with a
   running byte cap.
4. LOW. Test-adequacy: the real fetch/read/brief loop was covered only by network-marked tests
   (excluded from the offline gate), and one online assertion passed vacuously on an empty
   candidate list. Fix: three new offline tests (a monkeypatched shadow loop proving a real
   brief plus provenance; a never-raises regression; a per-paper-isolation regression) and a
   non-vacuous network assertion.
5. (Grouped with 2/4 above — same underlying non-raising defect, same fix.)

All four LOW findings are in the shadow ouroboros code, which does not run in Experiment 43
(no `_ouroboros` block), so none could confound the experiment; they are real defects in
newly-authored code and were fixed on that basis. Gamma and the shadow-isolation boundary are
untouched by every fix.

## Claude command-line (CC2) dispatch — expired OAuth, founder re-login required

The Claude command-line route returned a generic 401 from subprocess dispatch. Diagnosis: the
harness environment exports `ANTHROPIC_BASE_URL`, which the child `claude` process inherits and
authenticates against instead of the subscription; stripping it reveals the true cause —
"OAuth session expired and could not be refreshed." The macOS Keychain token has aged out, and
`claude -p` (non-interactive) cannot perform an interactive refresh. The workspace also still
reads as not-trusted in `~/.claude.json`. This blocked CC2 in the A1 panel and is why two
command-line-dispatching integration tests time out. It is a routine re-login, not a
re-registration. Founder action: force a real command-line re-login, then verify with
`claude -p --model opus "PONG"` in a plain terminal. Confirmed separately: the command-line
route uses `--system-prompt` to fully replace Claude's system prompt with the CDSFL directive —
a capability the subagent route cannot match — so fixing the command-line route is the correct
choice, and for Experiment 43 it keeps the model panel byte-identical to Experiment 42. Once the
token is refreshed, dispatch launches with `ANTHROPIC_BASE_URL` stripped and no code change.

## Test state and one pre-existing defect

Full non-network suite: 1,595 passed, 3 failed. Two failures are the command-line OAuth timeouts
above. The third, `test_both_phase1_paths_use_the_constant`, is a pre-existing stale test:
`decomposed_dispatch.py` was refactored off the `_PHASE1_MAX_TOKENS` constant in commit `fbafff8`
before this session, and the test was not updated. It is unrelated to Phase 1 and flagged for a
separate fix.

## State and next step

Experiment 43 (`43_macrophage_locationkey_live.json`) is unlaunched and its instrument is
unchanged; the configuration carries every Experiment 42 landmark flag identically. The run is
paused here for founder review. Next: founder refreshes the command-line login and reviews this
report; then Experiment 43 launches under full monitoring, with the ouroboros studying in shadow.

Written under CDSFL note standard v1.2 (14 May 2026).
