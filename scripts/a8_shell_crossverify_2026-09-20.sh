#!/bin/bash
# A8 CROSS-VERIFICATION, 2026-09-20, panel Section P.
# An INDEPENDENT classifier for the 575 cited paths, written with `test -f`,
# `test -d` and `ls` only -- it shares no code with
# scripts/orphan_citation_era_2026-09-17.py. It reproduces disposition()'s
# order exactly: tracked -> file -> dir -> template -> prefix -> missing.
#
#   usage: a8_shell_crossverify_2026-09-20.sh <repo_root> <tracked_list> <manifest.json>
# It prints one `path<TAB>state` line per cited path, then a disagreement count
# against the manifest. Exit 1 on ANY disagreement.
set -u
ROOT="$1"; TRACKED="$2"; MANIFEST="$3"
PATHS=$(python3 -c 'import json,sys;print("\n".join(json.load(open(sys.argv[1]))["rows"]))' "$MANIFEST")
OUT=$(mktemp)
while IFS= read -r path; do
  [ -z "$path" ] && continue
  if grep -Fxq -- "$path" "$TRACKED"; then st=tracked
  elif [ -f "$ROOT/$path" ]; then st=local_only
  elif [ -d "$ROOT/$path" ]; then st=directory
  elif printf '%s' "$path" | grep -Eq 'XX|\.\.\.|\*|<|\{'; then st=template
  else
    bare=${path%"${path##*[!/]}"}          # strip trailing slashes
    stem=${bare##*/}; parent=${bare%/*}
    st=missing
    if [ -n "$stem" ] && [ -d "$ROOT/$parent" ]; then
      if ls -A -- "$ROOT/$parent" | cut -c"1-${#stem}" | grep -Fxq -- "$stem"; then st=prefix; fi
    fi
  fi
  printf '%s\t%s\n' "$path" "$st" >> "$OUT"
done <<< "$PATHS"
echo "--- shell classifier counts ---"
cut -f2 "$OUT" | sort | uniq -c | sort -rn
echo "--- total: $(wc -l < "$OUT") ---"
python3 - "$MANIFEST" "$OUT" <<'PY'
import json,sys
man=json.load(open(sys.argv[1]))["rows"]
sh=dict(l.rstrip("\n").split("\t",1) for l in open(sys.argv[2]) if "\t" in l)
assert set(sh)==set(man), ("path set differs", len(sh), len(man))
bad=[(p,man[p]["state"],sh[p]) for p in man if man[p]["state"]!=sh[p]]
print(f"DISAGREEMENTS: {len(bad)} of {len(man)}")
for p,a,b in bad[:20]: print(f"  {p}\n     manifest={a}  shell={b}")
sys.exit(1 if bad else 0)
PY
