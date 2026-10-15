#!/bin/bash
# The 2 FREE simulated runs of 2026-10-15, launched one at a time under full `cy`.
#
# FOUNDER'S INSTRUCTION, 2026-10-15: *"Do two free runs then instead of just
# one, and gather your data as required. Apply any outstanding fixes you have
# identified first, including any as yet unbuilt/unapplied machinery, before you
# begin the runs ... continue all your work to full completion under full cy as
# specified."*
#
# COST: NONE. `bench/tools/sim_dispatch_shim.py` patches `_dispatch_single_model`
# -- the only place a paid model is called -- and substitutes Claude subagents on
# the founder's own plan. Seats carry the mandatory `-SIM` suffix AT SOURCE.
# `budget_limit=0.0`.
#
# WHY 2 RUNS AND WHY THEY DIFFER BY EXACTLY 1 FLAG. Run 1 measures the directive
# repair -- the project's own specification delivered whole for the first time.
# Run 2 adds the section 7.7 severity promotion. Same target, same seats, same
# round budget, so run 2 minus run 1 is attributable to the promotion alone.
# Enabling both at once would make neither attributable, which is the error the
# programme already rejects for per-fix attribution.
#
# FLAGS THAT ARE NOT DEFAULTS, AND WHY EACH IS PASSED EXPLICITLY:
#   --seat-models ladder   ALREADY THE DEFAULT, and passed anyway. An earlier
#                          version of this comment said the launcher defaults to
#                          `uniform` and that this flag overrides it; every
#                          clause of that was WRONG. The default changed to
#                          `ladder` at commit e228a214 on 2026-10-07, confirmed
#                          by `git log -L 286,288` and by `parse_args([])`
#                          returning `ladder`. It is passed EXPLICITLY so the run
#                          record is self-describing rather than dependent on a
#                          default that has already changed once.
#                          AND THE OLD "2 BACKING MODELS" CAVEAT IS ALSO GONE:
#                          POST at 2026-10-15 03:19 reports the ladder climbing
#                          with a DISTINCT rung sequence per seat across the
#                          pinned models, not 2 behaviours.
#   --routing-max-rungs 0  0 MEANS EXHAUST since 2026-10-06. His ruling of
#                          2026-10-08 made EXHAUST the default intent; the
#                          dataclass default stays 2 for parity with 49 real
#                          configs, so it is passed here.
#   --target PROSE         `bench/cdsfl_registry/targets/prose_with_computable_listings.md`,
#                          which COMMISSIONS TASK A19: a .py target leaves
#                          `sk_score_prose_listings` inert, so a prose target
#                          carrying fenced computable listings is the only way
#                          the admissibility flag is exercised at all. Its 2
#                          planted defects were each verified with 2 independent
#                          tools before planting, and
#                          `bench/tests/test_the_prose_target_is_fit_for_arm4_2026-10-14.py`
#                          keeps them real.
#   --domain mathematics   AND IT IS NOT THE OBVIOUS NAME, FOR A MEASURED
#                          REASON. The tracker's own resume command named the
#                          statistics domain, and there is no such directory
#                          under bench/directives, so `_load_domain_directive`
#                          returned None and every such run composed NO DOMAIN
#                          LAYER AT ALL while the manifest still recorded the
#                          name. Measured 2026-10-15 by
#                          `scripts/a_domain_name_that_matches_nothing_2026-10-15.py`:
#                          16 of 47 domain references in shipped configs
#                          resolve to nothing, 34.0426%, Wilson [22.1674%,
#                          48.3291%], and 6 of the 9 distinct names match
#                          nothing, 66.6667%, Wilson [35.4202%, 87.9416%].
#                          `mathematics` resolves, at 2,803 characters, and
#                          covers the planted defects, which are a variance
#                          bias and a Wilson interval centre. The loader now
#                          WARNS on a name that matches nothing; it does not
#                          refuse, because refusing would break 16 of 47
#                          shipped references and renaming them is his call.
set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

WHICH="${1:-}"
if [ "$WHICH" != "1" ] && [ "$WHICH" != "2" ]; then
  echo "usage: $0 <1|2>" >&2
  echo "  1 = directive repair, severity specification RECORDED only" >&2
  echo "  2 = directive repair + severity specification DECIDING" >&2
  exit 2
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="bench/cdsfl_registry/targets/prose_with_computable_listings.md"
COMMON=(--target "$TARGET" --rounds 10 --domain mathematics
        --seat-models ladder --routing-max-rungs 0)

if [ "$WHICH" = "1" ]; then
  NAME="free_run1_directive_whole_${STAMP}"
  EXTRA=()
else
  NAME="free_run2_severity_spec_${STAMP}"
  EXTRA=(--severity-spec)
fi

LOG="bench/logs/${NAME}.log"
mkdir -p bench/logs
echo "$NAME" > /tmp/cdsfl_current_free_run.name
echo "$LOG"  > /tmp/cdsfl_current_free_run.log

echo "launching $NAME"
echo "  target : $TARGET"
echo "  log    : $LOG"
# ★ `${EXTRA[@]+...}` IS NOT DECORATION. This machine runs GNU bash 3.2.57,
# where `set -u` treats an EMPTY ARRAY as an unbound variable: `"${EXTRA[@]}"`
# aborts with "EXTRA[@]: unbound variable" on run 1, whose EXTRA is empty by
# design. Measured 2026-10-15 07:10 -- run 1 did NOT launch, and the script had
# already printed its log path and PID, so it LOOKED launched.
#
# `${EXTRA[@]+"${EXTRA[@]}"}` expands to nothing when the array is empty and to
# the quoted elements otherwise, on both bash 3.2 and 5.x.
nohup python3 bench/tools/run_simulated_experiment.py \
      "${COMMON[@]}" ${EXTRA[@]+"${EXTRA[@]}"} --name "$NAME" > "$LOG" 2>&1 &
PID=$!
disown

# ★ AND THE PID IS WRITTEN ONLY ONCE THE PROCESS IS PROVEN ALIVE. The first
# version wrote it unconditionally, so a launch that died instantly left a PID
# file naming a dead process -- and `cy_watch_free_run` reads that file to decide
# the run has ended. A stale PID would have made the watchdog report a completed
# run that never started, which is the precise failure the watchdog exists to
# prevent: silence that looks like success.
sleep 2
if ! ps -p "$PID" >/dev/null 2>&1; then
  echo "  FAILED : the run exited within 2s. No PID file written." >&2
  echo "  log tail:" >&2
  tail -20 "$LOG" >&2 2>/dev/null || true
  exit 1
fi
echo "$PID" > "${LOG%.log}.pid"
echo "  pid    : $PID (alive after 2s; written to ${LOG%.log}.pid)"
