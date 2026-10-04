# Why the parser kept guessing, and what it now reads instead — 2026-10-04 03:53 BST

Plain-English companion to `experimental_notes/Field_Envelope_2026-10-04.md`, which carries the file paths, line numbers and producing scripts. The reading copy for text-to-speech is `experimental_notes/Field_Envelope_2026-10-04.txt`, and it belongs at `~/Desktop/CDSFL_tts/Field_Envelope_2026-10-04.txt`.

## The question that was asked

Parsing defects have recurred through this project's whole life. The task set on 2026-10-04 was not to patch another one but to decide whether a particular repair would close the class, and then to build it if the answer was yes. The proposed repair: take the unmistakable markers already used for one job — the triple-angle-bracket sentinels that wrap a corrected passage — and extend them to every field of every finding.

## The answer, and the correction inside it

The repair is right. The reason given for it was not, and the difference changed the design.

The proposal rested on a claim that the sentinel markers are "unambiguous by construction". Run against 12 different ways of writing the same corrected passage, the existing sentinel reader refuses 6 of them. It refuses a blank line between the label and the marker. It refuses bold formatting around the marker — the exact formatting that once defeated the pattern reading finding identifiers. It refuses a passage that starts on the marker's own line.

The marker itself is fine. Nothing in ordinary prose contains `<<<CDSFL_ORIGINAL>>>` by accident. What fails is the *grammar built around* it: that reader requires an ordinary text label, `CORRECTED_COPY:` followed by an identifier, to sit immediately above the marker with nothing but spaces between. So the one piece of information that says which finding the passage belongs to lives *outside* the marker, in exactly the free prose the diagnosis blamed.

So the property that matters turns out to be two properties, and the old form has only one of them. First, the delimiter must be made of characters the content cannot produce by accident. Second — and this is the one that was missing — the delimiter must be findable on its own, with everything load-bearing written *inside* it. Nothing about the surrounding text, the indentation, the formatting, the order of lines or the position in the reply should be read at all.

## What a field now looks like

```
<<<CDSFL_FIELD field=SEVERITY id=F001>>>0.9<<<CDSFL_FIELD_END>>>
```

The field's name and the finding it belongs to are both inside the opening marker. A model may wrap any field this way, and a field that arrives wrapped is read exactly as written. A model may also ignore the whole thing, and then its reply is read precisely as it is today.

That last point is a requirement, not a courtesy. The project's standing rule is that work must add and never subtract, so a model that does not adopt the new form cannot be allowed to lose anything. Measured over every archived model reply the repository holds — 5,445 of them, 57 MB of text, 17,127 findings between them, and not one containing a single one of the new markers — all 5,445 parse identically with the new reader in place.

The first version of that measurement used only a quarter of the corpus. The repository keeps model replies in two places: the panel records, where models review the project, and the run logs, where models produce findings against a target. The second is the population these parsers actually serve, and it is more than 16 times the size of the first. A green result over the smaller and less relevant half would have been exactly the kind of flattering board this project has a standing rule against.

## Where it earns its place

The sharpest case is the proof block each finding carries, the one stating how much residual risk the model believes is left. Reading it has always meant deciding whether the word "corroboration" is a section heading, a word in a sentence, or a key inside a data structure. The oldest of the three readers decides wrong: in one run it reported 335 proof sections where only 109 were real, so 226 were phantoms. A newer reader, written on 2026-10-03, refuses the phantoms but still has to guess *whose* proof it has found, by looking backwards for the nearest finding identifier.

Over 8 ways a model actually writes a proof block, that newer reader recovers the owner in 4. The marked form recovers it in all 8. The 4 it loses are a bullet point, a table row, a proof written before its identifier is declared, and a proof inside a block of structured data — and the last of those matters most, because one of the models on the panel writes its findings as structured data and the parser has a whole branch dedicated to reading it.

When the owner is lost, the runner falls back to matching proofs to findings by their order on the page. A test built for this repair shows what that costs. Two findings, one with a sound proof and one with a broken one, written in an order that confuses the fallback: without the markers the two verdicts come back **exactly inverted** — the sound proof recorded as failing, the broken one recorded as passing. With the markers, both are right, and shuffling the markers changes nothing.

## The trap that was avoided

A model cannot use a format it has never been shown, so the new form had to go into the prompts. But a format shown to a model is a format the model may copy back verbatim, and this project has measured that happening: a permissive earlier pattern accepted 8 of 12 deliberately awkward constructions, all of the kind a model produces when it simply echoes the instructions.

The existing prompts already have this exposure — a model echoing two lines of the current output format files a phantom finding at severity zero. Rather than open a second door to the same room, the example in the new instructions uses an identifier, `EXAMPLE_ONLY`, which the reader refuses by name, and the instruction text says so plainly. Copying the template unchanged files nothing. Replacing one word files a real finding.

## How the claim was tested

68 tests, all of which *run* both the old and the new reader on the same text rather than inspecting either one's source. That distinction is a standing project rule, earned the hard way: four defects here were found by executing two forms against each other where reading found none.

14 separate mutations were then applied, each undoing one part of the repair, and every one turned the tests red — from 1 failing assertion for the smallest to 9 for the largest.

Two things had to be fixed because of that exercise, and both are the point of doing it. One assertion could not fail: it had been checking a flag that was being set for an unrelated reason, so it would have passed with the repair removed. And one small guard had no test reaching it at all, which is this project's single most common defect shape — 11 confirmed instances in the record — so two assertions were written for it. A test that cannot fail, and a safeguard nothing exercises, are the two things this work exists to avoid.

Four separate measurements back the figures, each with a confidence interval computed twice by independent code. The 2 computations agree to within 1.1e-16, which is machine precision. The producing script is committed beside the numbers, because a number that exists only as prose is a claim about evidence rather than evidence.

## What is still open

Nothing here has run against a live model. Adoption is zero by construction until a dispatch happens with the new prompts, so every figure is over archived text and constructed grids. The run report now carries 2 figures the first live run will fill in: the share of replies containing at least 1 marker, and the share of markers the reader accepted. If models can see the format but not write it cleanly, acceptance will sit below 0.9 while adoption sits above 0, and the answer then is to loosen how the attributes are read rather than to loosen the marker.

Three of the four defect classes named in the original diagnosis are closed. The fourth — a 12-character minimum that once refused a genuine correction — is a judgement about how short a quoted passage may be, not a delimiting failure, and no marker changes it. That is said here so the claim is three of four and not four of four.

The regression sweep covered the 226 test files that touch any of the changed modules: 4,261 passed, 6 failed. Five of those six fail identically with every change reverted — they read raw model replies the repository deliberately does not keep, so no clone can satisfy them. The sixth was genuinely mine, and the way it was caught is worth recording: one document cites a line number in the main runner, and the test that guards that citation does not trust a frozen number — it recomputes the line from the source every run, a design adopted after the document and its own generator once agreed on the same wrong number and so checked each other rather than the code. Adding lines moved the line; the citation was re-pointed. After that, nothing failing is attributable to this work.

One housekeeping consequence: adding lines to the main runner moved 24 line-number citations scattered across 12 documents. The repository's own commit guard found and repaired all 24, which is its job, and then correctly refused to update the copies on the Desktop, because this work happened in a secondary checkout and a secondary checkout must not overwrite the primary one's files. One command run from the main checkout settles it.

---

Written under CDSFL note standard v1.7 (26 August 2026).
