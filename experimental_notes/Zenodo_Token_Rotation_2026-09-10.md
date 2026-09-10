# Rotating the Zenodo token

**Written 2026-09-10. Task Z1.** A plain-English companion for text-to-speech is at `~/Desktop/CDSFL_tts/Zenodo_Token_Rotation_2026-09-10.txt`.

## Why this exists

On **2026-08-19** the founder asked, verbatim: *"You need to give me clear instructions how to do this!"* They were never supplied. That is **22 days**. This is the file that should have arrived that day.

## The situation, measured before instructing

| | |
|---|---|
| Location | `ZENODO_TOKEN` in `.env` at the repository root |
| Shape | 60 characters, alphanumeric, begins `ievd` |
| Last changed | 2026-08-16 01:03 |
| In version control | **No** — `.gitignore:6` excludes `.env`, so it has never been committed or pushed |
| Files in this repository that read it | **0** — measured across every `.py` under `scripts/` and `bench/` |

**Nothing here uses it**, so rotating it cannot break a running process. There is no downtime to plan and no service to restart.

## The five steps

1. Go to **zenodo.org** and sign in.
2. Your name, top right → **Applications** → **Personal access tokens**.
3. Find the existing token and click **Delete** / **Revoke**. You do not need to know its value. This is what actually retires the old credential.
4. **New token** → name it something recognisable (`CDSFL September 2026`) → tick **`deposit:write`** and **`deposit:actions`** → **Create**. **Zenodo shows the value exactly once.** Copy it now.
5. In `.env`, replace the `ZENODO_TOKEN=` line. No spaces around `=`, no quotes needed.

## Confirming it

```bash
python3 scripts/zenodo_token_check.py --live
```

It reports whether Zenodo accepts the token and **never prints the token** — not in output, not in an error, not in a traceback. Without `--live` it reports only the length and first 4 characters: enough to confirm a paste landed, not enough for anyone reading over a shoulder to use.

## The honest framing

There is **no operational urgency**, because nothing reads the token. The reason to rotate is that a credential unchanged for 25 days, on a machine reachable remotely, is worth replacing on principle. **Nothing has gone wrong.** The task is about 4 minutes.

**FIGURE PROVENANCE.** Every figure above is produced by `scripts/zenodo_token_check.py`, which reads `.env` and scans the repository at run time. No number here is typed.

Written under CDSFL note standard v1.7 (26 August 2026).
