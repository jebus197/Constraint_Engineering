"""Measure the 'unresolved' evasion hole and the resolver that closes it.

Walks every transcript in the live corpus through `scan`'s OWN `on_tool` hook -- not a
second copy of the loop -- and compares `classify_path` (which drops a path carrying a
shell variable, so it can neither accuse nor excuse) against `classify_write` (which
RESOLVES the variable from the same command's bindings, then the environment, before
classifying). Prints the per-class before/after table and the recovery breakdown quoted
in `classify_write`'s docstring, so that figure is reproducible rather than asserted.

Takes no arguments. Reads only transcripts; writes nothing.
"""
import collections
import pathlib
import sys

for _cand in (pathlib.Path(__file__).resolve().parent, *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand)); break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "hooks"))
import ffafp_audit as fa  # noqa: E402

CORPUS = pathlib.Path.home() / ".claude" / "projects" / "-Users-georgejackson-Developer-Projects"


def measure(corpus: pathlib.Path):
    before, after, recovered = collections.Counter(), collections.Counter(), collections.Counter()
    examples = []

    def on_tool(name, inp):
        if name in fa._EDIT_TOOLS:
            muts, cmd = [str(inp.get(fa._EDIT_TOOLS[name]) or "")], ""
        elif name == "Bash":
            cmd = str(inp.get("command") or ""); muts = fa.bash_mutations(cmd)
        else:
            return
        for path in muts:
            old = fa.classify_path(path); before[old] += 1
            new = fa.classify_write(path, cmd); after[new] += 1
            if old == "unresolved" and new != "unresolved":
                recovered[new] += 1
                if new != "transient" and len(examples) < 12:
                    examples.append((new, path))

    files = sorted(corpus.glob("*.jsonl"))
    for f in files:
        state = {"offset": 0, "open": None, "seq": 0, "reads": {},
                 "last_work": None, "reported": None, "history": []}
        with open(f, errors="replace") as fh:
            fa.scan(fh, state, on_close=lambda v: None, on_tool=on_tool)
    return files, before, after, recovered, examples


def main():
    if not CORPUS.is_dir():
        print(f"corpus not present on this machine: {CORPUS}")
        print("Nothing measured. This is an ABSENT MEASUREMENT, not a clean result.")
        return 1
    files, before, after, recovered, examples = measure(CORPUS)
    total = sum(before.values())
    mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"corpus: {len(files)} transcripts, {mb:.1f} MB, {total} mutations\n")
    print(f"{'class':<12}{'classify_path':>16}{'classify_write':>16}")
    for k in ("code", "doc", "other", "transient", "unresolved"):
        print(f"  {k:<10}{before[k]:>16}{after[k]:>16}")
    u = before["unresolved"]
    n = sum(recovered.values())
    print(f"\nRECOVERED from the evasion: {n} of {u} ({100 * n / u:.1f}%)" if u else "\nno unresolved paths")
    for k, v in sorted(recovered.items(), key=lambda x: -x[1]):
        print(f"  -> {k:<10}{v:>5}")
    work = sum(v for k, v in recovered.items() if k != "transient")
    print(f"\n{work} real writes previously dropped in SILENCE are now counted as work.")
    print(f"{recovered['transient']} more are ignored for the RIGHT reason rather than by accident;")
    print(f"counting them instead -- the count-everything alternative -- would be "
          f"{100 * recovered['transient'] / u:.1f}% false refusals on this class.")
    print(f"{after['unresolved']} remain tier-3 residue: leading variable, directory unknowable.")
    print("\nsample real writes recovered:")
    for k, p in examples:
        print(f"  {k:<6}{p[:74]}")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
