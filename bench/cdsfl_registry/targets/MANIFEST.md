# Review targets — provenance only

> **★ RE-MEASURED 2026-08-24 00:25 BST. THE PUBLIC EXPOSURE BELOW IS CLOSED, AND THE
> ARTICLES ARE NOT LOST. Read this before the 2026-08-08 correction, which is now
> stale in both directions.**
>
> **The material survives.** All three unrun articles are recoverable from local
> history at `ddd74bde^`, and their hashes reproduce this file's published table
> exactly: `exp50_physics.md` 29,378 bytes `92a6424d…`, `exp51_biology.md` 27,931
> bytes `67c35e37…`, `exp52_factorial.md` 23,740 bytes `8ff5f06b…`. All five answer
> keys are at `eecdb0f^`, 42-83 KB each. Nothing needs re-authoring.
>
> **The public leak is closed.** `git ls-remote origin` returns exactly one head:
> `refs/heads/main`. Both `exp39-experimental` and `exp38-experimental` are gone from
> GitHub, and neither `ddd74bde^` nor `eecdb0f^` is an ancestor of `origin/main`. The
> route the correction below describes — `git show` against a public branch — no
> longer exists.
>
> **What that does NOT settle, and a founder ruling is still owed on it.** The branch
> was public for a period. Anyone who cloned during that window holds the articles and
> the keys, and no deletion reaches them. So the live route is shut and the historical
> exposure cannot be undone. Whether Exp 50/51/52 may still be reported as blind exams
> is a scientific judgement about that window, not a technical question, and it is the
> ruling the 2026-08-08 correction asked for and never received.
>
> **The staged copies are a separate matter and are simply absent.**
> `~/CDSFL_review_targets/current/` holds one file, `SW-21-REF-04.md`. The staging
> names (`PX-12-REF-05.md`, `BX-14-REF-04.md`, `SW-14-REF-01.md`) that the exp50-52
> configs point at do not exist there and were never committed under those names in
> any branch's history. Staging them from `ddd74bde^` is a copy, not a rebuild — but
> the configs and the repo disagree about what the articles are called, and that
> disagreement is what made them look lost.

> **[Correction 2026-08-08 00:50 BST. Read this before the rest of the file.]**
> The claim below — that the exam documents are not in this repository — is FALSE
> for three of the six. `exp48_chemistry.md`, `exp49_engineering.md` and
> `exp53_zone_controller.md` are each recoverable byte-for-byte from committed run
> records under `bench/logs/`, and each recovered copy hashes to the SHA-256
> published in this file. The mechanism is that a run record stores the prompt as
> sent, and the prompt embeds the whole article; the records were then committed and
> pushed to the public `origin/exp39-experimental`. Both revisions of the control are
> present, so the difference between them is recoverable by subtraction.
>
> Three consequences follow, and none of them is optional. **Those three documents
> are no longer held-out material** — any later result on them has to be read as
> potentially contaminated from this repository, whatever the access rules below say.
> **[CORRECTION 2026-08-08, and it reverses the sentence that stood here.]** The
> claim that `exp50_physics.md`, `exp51_biology.md` and `exp52_factorial.md` "are
> still intact" was FALSE, and it was false in the most damaging direction: a
> document whose whole purpose is honesty about exposure asserted a protection that
> a two-line command refutes. Never having been RUN does not make a document
> unexposed, because the second route is not `bench/logs/` at all — it is `git show`.
> All three were committed to this tree before being moved out of it, and deletion
> does not remove a file from history. Measured 2026-08-08:
>
> | article | recovered from | sha256 of recovered copy | vs published |
> |---|---|---|---|
> | `exp52_factorial.md` | `ddd74bde^` | `8ff5f06b1441906f…` | **EXACT MATCH — fully exposed** |
> | `exp50_physics.md`   | `ddd74bde^` | `92a6424d25856918…` | earlier revision, substantial content exposure |
> | `exp51_biology.md`   | `ddd74bde^` | `67c35e37d72b26ee…` | earlier revision, substantial content exposure |
>
> **All five answer keys are likewise recoverable**, from `eecdb0f^`, including
> `exp52_factorial_answer_key.json` — 48 claims with their planted-false counts.
> Commit `eecdb0f` was written specifically to close answer-key exposure and did
> close it in the working tree; it did not and could not close it in history, and it
> flagged that residual at the time.
>
> So the honest position is that **no exam article in this manifest is held-out
> material against a reader with clone access**, and Exp 52 — the capstone 2×2
> factorial — is exposed byte-for-byte along with its key. **The leak is live, not
> historical**: the next exam run publishes its article the same way unless the
> record is redacted first.
>
> Withholding a document while committing a verbatim copy of it is the failure this
> file was written to prevent, and the published hash is what proves it happened.
> Remediation — history rewrite, redaction going forward, or accepting the exposure
> and retiring the three as held-out targets — **needs a founder ruling** and is not
> taken here.

The exam documents are NOT in this repository, and that is deliberate — **and for
three of the six that sentence is now false; see the correction above.** What follows
is the reasoning for withholding them, not a statement of where they currently stand.
It is left in place because the reasoning is still sound; the outcome is not.

A target kept under version control leaks itself. Any repair to a seeded claim
touches only the claims that are wrong, and the claims that are wrong are the
seeded ones — so `git diff` on the target returns the planted set at precision
1.000, with no answer key, no similarity measure and nothing for a detector to
catch. Measured on 2026-07-29: six of eleven for physics, three of nine for
biology, Fisher p = 1.3e-05. Superseded revisions leak in the same way, by
matching the old seeded text into the current document.

That is not a defect that can be patched. It is a property of storing the test
article beside the code, so the article now lives with the scoring keys,
outside this tree and sealed while any run is in flight.

What remains here is the hash of each document, so a result can be tied to the
exact article that produced it. A hash proves provenance without disclosing
content, a count, or which claims were changed.

```json
{
  "exp48_chemistry.md": {
    "sha256": "9fbaca3ec1a11478ce7a032be90f69596576af3cd4480eb9e43563e4c5b504b9",
    "bytes": 20290
  },
  "exp49_engineering.md": {
    "sha256": "170d16d3c852138d62438b0b14a690d19be1b29a3382abaa52153953a8c65398",
    "bytes": 24542
  },
  "exp50_physics.md": {
    "sha256": "e0748e4cb708b1f69ddf97eabb93976eac8dda6c9ba7ec051b5af9d36f1c784d",
    "bytes": 29815
  },
  "exp51_biology.md": {
    "sha256": "18b6ea0f43db05731d9d92f0b3de29fe705082e57c81b76b8c3f2a094d97f2b7",
    "bytes": 27988
  },
  "exp52_factorial.md": {
    "sha256": "8ff5f06b1441906fa115a7a7e27cc568424324ab9ad738a29adf6eeafd0fb564",
    "bytes": 23740
  },
  "exp53_zone_controller.md": {
    "sha256": "da27c16ef24fceae94d0cf7eb6cb45989b392fac2662af84ce8df80948381766",
    "bytes": 24135
  }
}
```

Anyone holding the store regenerates this block with `shasum -a 256 *.md` for the
hashes and `wc -c *.md` for the byte counts, both run over the directory named by
`CDSFL_TARGETS` in the off-repo scoring config that `bench/stage_targets.sh` reads.
Both fields are needed: `shasum` alone reproduces half the block. Confirmed
2026-08-08 — all six entries regenerate exactly as published, byte counts included.
This line previously read "Generated by
bench/stage_targets.sh --manifest", and that command does not exist: the script
takes module filenames only, and `--manifest` would be resolved against the store as
a filename and fail. The one document whose job is to prove provenance was
misstating its own.

> **Recomputed 2026-08-04 00:05 BST.** The control's fingerprint was stale: it
> recorded the document as it stood before the seven claim repairs of 1 August, so a
> result could have been tied to the wrong revision — the exact failure this file
> exists to prevent. All six recomputed from the store; five were unchanged.

---

## Requesting a document

A hash settles which article produced a result. It does not let anyone check the
article, and a target nobody outside the project can read is a target nobody outside
the project can dispute. Documents are therefore released on request, under the
arrangement controlled-access scientific data has used for years — dbGaP and UK
Biobank at one end of the scale, a held-out benchmark set released to reviewers at
the other. A named custodian, a stated purpose, conditions of use, and an embargo.

**Custodian.** The repository maintainer, via the issue tracker at
`github.com/jebus197/Constraint_Engineering`. Requesting in the open means the
request record is public while the document is not, which suits a project whose
subject is provenance; a private channel can be substituted without changing
anything else here.

**What a request states.** Who is asking and in what capacity; which document, by
the filename in the hash block above; and what it is for, in a paragraph rather than a
form. Reproducing a published run, auditing the seeding, and building a competing
scorer are all ordinary reasons. The purpose matters because it sets the embargo.

**Conditions of release.** The recipient does not redistribute the document or any
part of it. The recipient does not place it in training, fine-tuning or evaluation
corpora, and does not paste it into a hosted model whose operator retains inputs —
one such paste ends the document's usefulness to everyone, including the recipient.
Results are reported against the SHA-256 published above, so a reader can tell which
revision was used. The embargo runs until the experiment the document supports is
published, or twelve months from release if that comes first, and exists to stop a
document reaching the panel through a back channel before it has been sat.

**Only three documents can be released on these terms.** `exp50_physics.md`,
`exp51_biology.md` and `exp52_factorial.md` are still held out. The other three are
already public through the run records, as the correction at the head of this file
records; releasing them under an embargo would be theatre.

**Why not a submission server.** The other recognised pattern for held-out data is to
keep the answers behind an evaluation server and let entrants submit predictions —
blind scoring, no disclosure, a leaderboard. It buys a real property, and the price
is standing infrastructure and continuous maintenance. Against six documents, scored
by a five-model panel, on a project funded personally, that price is out of
proportion to what it buys, and an evaluation server that quietly stops working is
one more thing that fails while reporting success. Recorded here so the choice is
visible rather than assumed.

---

## Contamination canary

Held-out material leaks into training corpora eventually, and a set that has leaked
looks exactly like a set that has not — the scores simply improve. BIG-bench's answer
is a canary: a unique GUID carried inside each held-out document, published so that
anyone can later search a corpus, or a model's output, for a string that has no
reason to exist anywhere else. A hit is contamination. It is the only cheap way to
tell a genuine result from a recital.

**Mechanism.** One UUIDv4 per document, generated once and never reused across
documents, so a hit names which document leaked. It lives in the header block the
articles already carry, on its own line beside `**Document ID:**`, where it reads as
ordinary revision metadata. That placement is deliberate: an explicit "do not train on
this document" notice, which is BIG-bench's own wording, would tell the panel it is
sitting an exam, and this project already treats framing as a documented confound. A
bare identifier in a metadata block tells it nothing.

**The GUID is committed by hash, not published in clear.** BIG-bench publishes its
canary openly because BIG-bench's data is open; publishing this one openly would put
it in a public repository that already republishes these articles verbatim, and a
canary that has been crawled from its own repository reports contamination that the
repository caused. So this file will carry `sha256(guid)` per document. The GUID
itself goes to whoever is running a contamination search, at the time they run it,
and they verify it against the published commitment afterwards. That is the same
commit-then-reveal arrangement the article hashes above already use.

**Not yet in place, and here is what it depends on.** No article carries a canary
today. The articles are sealed and outside this tree and are not edited from here; a
canary is added when a document is next revised for its own reasons. Three
preconditions, in order, and the order is load-bearing:

1. **Redact the run records first.** While the runner commits the prompt verbatim, a
   canary embedded in an article is published by that article's next run — the
   defect above, wearing a new hat. A canary added before this is fixed is worse than
   no canary, because it manufactures the hit it is meant to detect.
2. **Embed, then recompute the hash, in one operation.** Adding the line changes the
   file, which invalidates the SHA-256 published above. A canary landing without the
   manifest being regenerated leaves this file asserting a fingerprint no copy of the
   document matches — and the fingerprint is what the access terms tell recipients to
   report against.
3. **Only where it can still do work.** `exp48`, `exp49` and `exp53` are already
   public. Canarying them would detect leakage that has certainly already happened
   and attribute it to whoever is holding the corpus. The three unrun documents are
   where a canary buys something.

**Absence of a hit is not evidence of a clean corpus** until a canary exists, is
embedded, and predates the corpus. Until all three hold, no contamination search
performed against these documents means anything, and none should be reported as
though it does.
