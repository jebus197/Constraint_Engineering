# Interaction specification for the human in the loop — DRAFT for his correction

**2026-10-29.** Answers his instruction of 2026-10-19, registered as `fr:3599a74cc1aa`.

**His words:** *"Perhaps therefore, as well as drawing up a specification for the HIL, you should draw up an interaction specification or me, and use this in your experiments that involve the new orchestrator?"* (*or me* is *for me*.)

**It is marked DRAFT deliberately and that is not hedging.** This describes how *he* works. Everything below is either a verbatim lift from his own instruction or a figure measured from his own annotations, but a specification of someone's behaviour can only be confirmed by that person. Where it is wrong he should strike it, as he has struck 3 rules of mine that acquired his name without his words behind them.

## 1. His own worked example, verbatim, which is the core of this

From the same 2026-10-19 annotation:

> *"you will simply tell the orchestrator model to run Onboarding.md first (while skipping tools that are already installed on my local machine), then explain the purpose of the experiment to the orchestrator, which target to use (the experiment to run), and in cases where no existing target is present, explain to the orchestrator the nature of the experiment you wish to conduct. Indeed, more or less exactly the way I interact with you now."*

That is the interaction, in his words, and the specification below is an attempt to state it precisely enough to run an experiment against — nothing more.

**And his reason for routing it through CC1 first, also verbatim:** *"these experiments are simulated runs (or they should be). They are tests, just to see if everything will work as expected. If they do, then the bounded orchestrator may well eventually become the primary means by which I interact with the harness too."*

## 2. The 4 moves

| # | move | what the orchestrator must do |
|---|---|---|
| 1 | **Bring the environment up** | Run onboarding, **skipping anything already installed locally**. Report what it skipped and why, so a skip is never silent. |
| 2 | **State the purpose** | Accept a purpose in plain prose. It is not a parameter list; it is what the experiment is for. |
| 3 | **Name the target** | Accept an existing target by name, or — where none exists — accept a description of the experiment to be conducted and say plainly that no target exists yet. |
| 4 | **Run and report** | Run, then produce the findings report. Nothing in moves 1 to 3 settles a claim. |

**Move 1 is the one most likely to be got wrong**, because *skipping what is installed* is a decision, and a skip reported as nothing is the silent-default failure this project has recorded 8 times. The specification is therefore that every skip is named.

## 3. The shape of his instructions, measured

From his 752 annotations, by `scripts/how_does_he_actually_interact_2026-10-29.py`:

- **median length 127 characters**, mean 244.5, shortest 6, longest 3,788;
- **198 of 752 are under 60 characters** — 0.263298, Wilson [0.233080, 0.295922], exact [0.232135, 0.296330];
- **137 of 752 are over 400 characters** — 0.182181, Wilson [0.156231, 0.211361], exact [0.155218, 0.211662].

**So the interface must accept both a 6-character verdict and a 3,788-character specification, and must not assume either.** A quarter of his instructions are shorter than a sentence; a sixth are longer than a paragraph. Anything that demands a form in between will be wrong a large fraction of the time.

## 4. What the corpus can and cannot say about his commands

**It can say this.** Every MC command appearing in a command position across all 752 annotations is a **ticket marker**: `fr` 7 times, `qs` 3, `pf` 3. 13 of 752 annotations carry at least 1 marker — 0.017287, Wilson [0.010130, 0.029351].

**It cannot say how often he issues steering commands**, because those reach a session through chat rather than through annotations. No such frequency is estimated here.

**And the measurement that would have said otherwise was wrong**, which is recorded because it bears on how any future version of this is built. Counting by word boundary returns `a` **612** times in 752 annotations and matches `t` inside *"don't"*: a single-letter command cannot be told from English that way. In a command position — a line, or a trailing run, whose every token is a command, which is how he writes them (*"a, d"*, *"a, f, sy"*) — the count falls from 612 to 13.

## 5. What the orchestrator must never require of him

Derived from his rulings rather than proposed:

- **It must not require him to repeat himself.** His annotations are the record; an item he has already ruled on must not be presented as a decision again. That failure has a name in this project and he caught it: *"Then if I already ruled. Why are you presenting it as a decision required from me again?"*
- **It must not require a form.** A 6-character verdict is a complete instruction.
- **It must not require him to authorise what it can establish itself.** His 2026-10-29 challenge on the 63 adjudications settled this: work that is computationally reducible is not his to do, and 0 of those items were ever shown to need him.
- **It must not interrupt him for a non-blocking item.** His criterion, verbatim: *"Does it prevent further progress on the task list? If so, then yes, it's a blocker. If not, then append to the closing/final report."*
- **It must not spend money, touch a git ref or open the sealed key store** without his express word on the occasion.

## 6. What it must give him unprompted

- **A findings report in plain technical English**, not markdown noise, with equations rendered.
- **The decisions he owes, each with its options** and where it lives, so a decision never arrives without the alternatives.
- **A TTS companion**, because he is dyslexic and long output is a struggle to read; that is not a preference but an accessibility requirement, and a document delivered without a TTS companion is delivered to nobody.
- **The clock on any temporal claim**, never an estimate.

## 7. Acceptance checks

- [ ] Onboarding runs and every skipped tool is named with its reason
- [ ] A purpose in plain prose is accepted with no parameter list
- [ ] An absent target is reported as absent rather than defaulted
- [ ] A 6-character instruction and a 3,788-character instruction are both accepted
- [ ] An item he has already ruled on cannot be re-presented as a decision
- [ ] A non-blocking item reaches the closing report and never interrupts him
- [ ] A reserved action refuses without his word on that occasion
- [ ] Every delivered document has a TTS companion

## 8. What this does not cover

It does not cover the interface — that is his authoritative brief. It does not estimate his command frequencies, for the reason in section 4. And it does not claim to be right: it is a draft of his own behaviour, and his correction governs.

Written under CDSFL note standard v1.8 (17 October 2026).
