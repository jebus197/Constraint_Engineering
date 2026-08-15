#!/bin/bash
# CDSFL one-shot arc sequencer (founder directive 2026-07-29: the arc must
# advance without depending on any attention window).
#
# Runs the remaining legs back-to-back, detached from any host process, and
# STOPS THE CHAIN on the founder's ratified pause conditions: a leg that does
# not reach CONVERGED, a crash, a missing or unstaged target, an uncleared
# module, or evidence that a panel reached the scoring key. It never
# auto-advances past a failure.
#
# ORDER (founder ruling, 2026-07-29 evening): 53 zero-plant control FIRST, then
# 50 physics, then 51 biology. The control leads because it is the only instrument
# built that measures behaviour with NO ground truth available — which is Bench
# Run 2's regime — and because it measures the stopping decision directly, which
# is the quantity the Exp 48 contamination destroyed. On calibration grounds it is
# worth more than either remaining subject exam.
#
# The factorial is NOT in this chain. Its target is an open founder question (the
# historical candidate, the runner itself, is 7,536 lines against a largest-ever
# convergence of 929), and it has no clearance file, so require_cleared halts here
# by design rather than by omission.
set -u
REPO=/Users/georgejackson/Developer_Projects/Constraint_Engineering
cd "$REPO"
STATUS=/tmp/arc_sequencer_status.txt
# Location is read from a file OUTSIDE the repository. Naming the key store in a
# tracked file is what leaked it during Exp 48: the note recording where the keys
# had moved to was committed inside the tree the panel could read. One indirection
# is defence in depth, not a boundary — the boundary is panel confinement plus
# detection of any climb out of the staged directory.
CONF="${CDSFL_SCORING_CONF:-$HOME/.config/cdsfl/scoring.env}"
[ -r "$CONF" ] || { echo "missing scoring config: $CONF" >&2; exit 1; }
# shellcheck source=/dev/null
. "$CONF"
: "${CDSFL_STORE:?scoring config did not define CDSFL_STORE}"
: "${CDSFL_VAULT:?scoring config did not define CDSFL_VAULT}"
: "${CDSFL_TARGETS:?scoring config did not define CDSFL_TARGETS}"
KEY_DIR="$CDSFL_STORE"
VAULT_FILE="$CDSFL_VAULT"
stamp() { date "+%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(stamp)] $*" | tee -a "$STATUS"; }
halt() { log "STOP: $*"; exit 1; }

# ── Pre-flight: the conditions that make a recall measurement mean anything ──

# 1. No plaintext scoring key anywhere on disk for the duration of the arc.
#    Confining the panel's working directory stops discovery by proximity; it
#    does not stop an absolute-path read or a home-directory search. During
#    Exp 48 a routed model read the key by absolute path.
if ! bash bench/vault_keys.sh status | grep -q '^VAULTED'; then
  halt "scoring keys are unvaulted — run 'bash bench/vault_keys.sh vault' before the arc"
fi
log "pre-flight: keys vaulted"

# 2. Each leg's module must be cleared by the tell-audit. A module whose seeded
#    claims can be located without doing the verification work produces a
#    worthless measurement. The gate file is written by the audit/repair step,
#    never by this script.
require_cleared() {
  [ -f "$REPO/bench/cdsfl_registry/targets/.cleared_exp$1" ] \
    || halt "Exp $1 module not cleared by tell-audit"
}

# 3. The panel's working directory must exist and hold exactly one file — the
#    document under review. A shared staging directory let a single `ls`
#    enumerate the whole exam series, including papers not yet sat.
check_staging() {
  CFG=$1
  PCWD=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('panel_cwd',''))" "$CFG")
  TGT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['test_article'])" "$CFG")
  [ -n "$PCWD" ] || halt "$(basename "$CFG"): panel_cwd unset — panel would run in the repo"
  [ -d "$PCWD" ] || halt "$(basename "$CFG"): panel_cwd does not exist ($PCWD) — run bench/stage_targets.sh"
  [ -f "$TGT" ]  || halt "$(basename "$CFG"): target missing ($TGT) — run bench/stage_targets.sh"
  N=$(find "$PCWD" -maxdepth 1 -type f | wc -l | tr -d ' ')
  [ "$N" = "1" ] || halt "$(basename "$CFG"): panel_cwd holds $N files, expected exactly 1"
  case "$PCWD" in "$REPO"*) halt "$(basename "$CFG"): panel_cwd is inside the repository" ;; esac

  # 3b. The STAGED copy must match the module it was staged from. Existence is
  #     not currency. Found 2026-08-01: the control's staged copy dated from the
  #     halted 29 July launch and predated that evening's repair of seven
  #     ambiguous claims. Every check above passed on it. The leg would have run
  #     the unrepaired document and halted on the same ambiguities that stopped
  #     it the first time — with nothing anywhere saying why.
  # run_leg moves the target store to "$CDSFL_TARGETS.away" BEFORE calling this,
  # so the leg cannot read a sibling module. Look in both places, or this check
  # finds nothing and silently passes — which is how it behaved when first
  # written (2026-08-01), i.e. exactly the failure it exists to prevent.
  SRCDIR=""
  for cand in "${CDSFL_TARGETS:-}" "${CDSFL_TARGETS:-}.away"; do
    [ -n "$cand" ] && [ -d "$cand" ] && { SRCDIR="$cand"; break; }
  done
  if [ -n "$SRCDIR" ]; then
    DOCID=$(basename "$TGT" .md)
    SRCFILE=$(grep -rl "^\*\*Document ID:\*\*[[:space:]]*$DOCID" "$SRCDIR" 2>/dev/null | head -1)
    [ -n "$SRCFILE" ] \
      || halt "$(basename "$CFG"): no module in $SRCDIR declares Document ID $DOCID"
    cmp -s "$TGT" "$SRCFILE" \
      || halt "$(basename "$CFG"): STAGED COPY IS STALE — $TGT differs from $SRCFILE; re-run bench/stage_targets.sh"
  fi
}


# 4. CC2 LIVENESS, PROVED BEFORE ANY MONEY IS SPENT.
#    CC2 is the routing resolver and wrote the resolving falsifier in every prior
#    experiment, so a 4-of-5 panel is a methodological deviation, not a degraded
#    run. On the first launch of the control it died on "this workspace has not
#    been trusted" — a consequence of confinement that no test covered, discovered
#    one round in. The runner's own fallback then quietly carried on with the other
#    four, which is exactly the silent degradation to avoid.
#
#    This probe exercises the two things a leg actually needs: that the CLI RUNS in
#    the staged directory at all, and that it can execute python3 through Bash,
#    which is what every falsifier demonstration depends on. Both from the panel's
#    real working directory, with the real flags. Costs no API credit.
cc2_probe() {
  PCWD=$1
  # The trust flag is attached to this exact path, so the probe needs it to exist
  # even before the first leg stages into it.
  [ -d "$PCWD" ] || mkdir -p "$PCWD"
  OUT=$(cd "$PCWD" && printf '%s' 'Run this and reply with only its output: python3 -c "print(7*6)"' \
        | env -u ANTHROPIC_BASE_URL -u MallocNanoZone -u MallocStackLogging \
          claude -p --model opus --output-format text \
          --no-session-persistence --allowedTools Bash Read Grep Glob 2>&1)
  case "$OUT" in
    *"not been trusted"*)
      halt "CC2 cannot run in $PCWD — workspace not trusted. Accept it once with:
       cd $PCWD && claude" ;;
    *"Not logged in"*|*"/login"*)
      halt "CC2 is not authenticated. Re-login with: claude  then /login" ;;
    *42*)
      log "pre-flight: CC2 runs in the panel directory and can execute python3" ;;
    *)
      halt "CC2 probe returned neither the expected result nor a known failure.
       A 4-of-5 panel is a deviation, so this is refused rather than degraded.
       Output: $(printf '%s' "$OUT" | head -c 400)" ;;
  esac
}

# ── Legs ──────────────────────────────────────────────────────────────────────

run_leg() {
  LABEL=$1; CFG=$2; MODULE=$3
  [ -f "$CFG" ] || halt "$LABEL config missing ($CFG)"
  # Stage THIS leg's document and nothing else. Every target previously sat in one
  # shared parent, so `ls ..` from inside the confined directory enumerated the
  # whole series and `cat ../*/*.md` read every sibling exam — including papers not
  # yet sat. Staging per leg means the parent holds one document for the duration.
  # Stage from the target store, then put the store out of reach for the run.
  # The store holds ALL SIX papers in plaintext. That is not the answer key, but a
  # panel that reads a sibling exam gets the cross-target count prior the audit
  # flagged — the mechanism the whole redesign exists to remove. Staging needs the
  # store; the run does not. So it is present for the copy and absent for the leg.
  # `mv A B` puts A INSIDE B when B already exists. If both the live store and
  # the stowed one are present — which happens whenever a previous leg was halted
  # mid-run and a later one recreated the store — this silently nests one inside
  # the other, and the leg then stages whichever copy happens to sit on top.
  # Reproduced 2026-08-01: the repaired control module ended up one level down
  # while the superseded 29 July copy sat at the top, and staging took the old
  # one. Refuse rather than merge; the two must be reconciled deliberately.
  if [ -d "$CDSFL_TARGETS.away" ]; then
    if [ -d "$CDSFL_TARGETS" ]; then
      halt "both $CDSFL_TARGETS and $CDSFL_TARGETS.away exist — a previous leg was
  interrupted before restoring the store. Reconcile them by hand (the .away copy is
  the one a halted leg stowed) and remove one, then re-run. Merging them by mv would
  nest one inside the other and stage the wrong module."
    fi
    mv "$CDSFL_TARGETS.away" "$CDSFL_TARGETS"
  fi
  bash bench/stage_targets.sh "$MODULE" >/dev/null || halt "$LABEL staging failed ($MODULE)"
  mv "$CDSFL_TARGETS" "$CDSFL_TARGETS.away" \
    || halt "$LABEL: could not put the target store out of reach"
  check_staging "$CFG"
  SIBS=$(find ~/CDSFL_review_targets -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d " ")
  [ "$SIBS" = "1" ] || halt "$LABEL: $SIBS documents staged; the leg must not be able to read a sibling"
  LOG=/tmp/${LABEL}_launch.log
  # Truncate. The log is grepped for "CONVERGED at round" with no run scoping, and
  # re-running the sequencer after a halt is the intended operating mode — so an
  # appended log lets a leg pass on a PREVIOUS run's verdict. Keep the old one.
  [ -s "$LOG" ] && mv "$LOG" "${LOG%.log}.$(date +%Y%m%dT%H%M%S).log"
  : > "$LOG"
  log "launching $LABEL"
  env -u ANTHROPIC_BASE_URL -u MallocNanoZone -u MallocStackLogging \
    python3 bench/launch_exp42.py --config "$CFG" >> "$LOG" 2>&1
  RC=$?
  [ $RC -eq 0 ] || halt "$LABEL exited rc=$RC"
  grep -q "CONVERGED at round" "$LOG" || halt "$LABEL did not converge — founder review"

  # Post-run integrity: did the panel reach the key? A contaminated recall
  # figure is worse than none, because it reads as a measurement. Halting here
  # costs one leg; not halting costs every leg after it.
  EXP_NAME=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['experiment_name'])" "$CFG")
  # -type d: errata sidecars are FILES beside the run directories and sort newer,
  # and handing one to the scanner exits 2 (usage), which `if !` would escalate as
  # a key-access incident that never happened.
  RUN_DIR=$(find "$REPO/bench/logs" -maxdepth 1 -type d -name "*${EXP_NAME}*" 2>/dev/null \
            | sort -r | head -1)
  if [ -n "$RUN_DIR" ]; then
    # The key location is passed in, never hardcoded in the scanner — the panel
    # can read the scanner. Both the plaintext store and the vault archive are
    # named: the vault sits under ~/Library, which the scanner otherwise treats
    # as benign home noise, so without this the vault and the detector would
    # have quietly cancelled each other out.
    if ! CDSFL_KEY_DIR="$KEY_DIR:$VAULT_FILE" \
         python3 bench/key_access_forensics.py "$RUN_DIR" >>"$LOG" 2>&1; then
      halt "$LABEL: KEY-ACCESS EVIDENCE in $RUN_DIR — measurement compromised, chain halted"
    fi
    log "$LABEL forensics clean"
  else
    halt "$LABEL: run directory not found — forensics could NOT run, so the leg is unverified. Not treated as clean."
  fi
  log "$LABEL CONVERGED"
}

cc2_probe "$HOME/CDSFL_review_targets/current"

require_cleared 53; run_leg exp53 "$REPO/bench/exp53_configs/53_control_zero_live.json" exp53_zone_controller.md
require_cleared 50; run_leg exp50 "$REPO/bench/exp50_configs/50_physics_exam_live.json" exp50_physics.md
require_cleared 51; run_leg exp51 "$REPO/bench/exp51_configs/51_biology_exam_live.json" exp51_biology.md

[ -d "$CDSFL_TARGETS.away" ] && mv "$CDSFL_TARGETS.away" "$CDSFL_TARGETS"
log "THREE LEGS COMPLETE: zero-plant control, physics, biology."
log "STOPPING HERE. The factorial (Exp 52) is an open founder question — target"
log "  choice and whether to reseed — and carries no clearance file. Scoring needs"
log "  the key store unsealed, which only the founder can do."
