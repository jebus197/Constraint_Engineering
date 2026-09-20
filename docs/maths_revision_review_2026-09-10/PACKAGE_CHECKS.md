# Package checks

Release: CDSFL_Mathematical_Review_Suite_2026-09-10. Proposal version 1.1. These are packaging and reproducibility checks, not empirical validation of CDSFL.

| Check | Recorded result |
|---|---|
| Scientific-file preservation | All 29 entries in the preserved final scientific manifest match their recorded lengths and SHA-256 hashes. |
| Reading copies | Six current documents included in PDF and offline HTML; editable Markdown retained. |
| PDF structure and appearance | 34 pages rendered and visually inspected. No detected clipping, invalid internal page destinations, or text outside the checked page margins. |
| Mathematical rendering | All 182 mathematical markup occurrences match the PDF-rendering inventory. The PDF uses high-resolution equation images; formulas remain editable in Markdown and HTML. |
| Text retention | 665 ordinary text chunks longer than 30 characters checked against extracted PDF text, excluding page footers; none missing. This supplements, rather than replaces, visual inspection. |
| Package audit | A separate read-only audit found no release-blocking content issue. Its record is under work/package-audit/. |
| Archive structure | One top-level directory, relative member paths, no symbolic links, caches, or absolute archive paths. ZIP CRC check passed. |
| Fresh extraction | All included files matched PACKAGE_MANIFEST.json; VERIFY_PACKAGE.py completed successfully. |
| Original counterexamples | All exact-arithmetic checks passed from the extracted package. |
| Revised-model checks | 5,600 conditional cases; 650 impossible observations rejected; 2,000 branch-policy expectations; 125 sequential-repair cases; 125 reduction/expectation cases; eight deliberately incorrect alternatives rejected. |
| Severe-test checks | 450 constructed bound cases passed; three deliberately incorrect alternatives rejected. |
| Recorded-result reproduction | Both generated JSON reports matched the preserved reports, including source hashes. |

The executable checks were run with Python 3.12.14 using the standard library. They require no model access or network connection. Repeat executions of these constructed cases do not constitute additional independent experiments or establish empirical calibration.

The final ZIP was reopened and extracted for verification after its contents and manifest were assembled. An external verification report and ZIP checksum were retained alongside the delivered archive. The package manifest excludes itself to avoid a self-referential digest. Integrity checks do not independently authenticate authorship or certify the mathematics.

Original repository documents are preserved unchanged; some of their links refer to material in the full repository. The revised-document and guide links point to included files or cited external sources.
