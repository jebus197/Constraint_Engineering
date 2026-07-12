"""Ouroboros shadow real-work loop (added 2026-07-12): resolve OA full text ->
download -> extract -> read -> brief. Proves the cell fetches, parses, and briefs a
REAL paper end-to-end (was a placeholder before). The read step uses the deterministic
extractive fallback (reader_backend="none") so CI does not hard-depend on an LLM
backend being reachable. The download+parse tests are network-marked.

SHADOW isolation is preserved: briefs are logged, never injected into a model prompt,
and never touch c_ext / nu_k / gamma. See the build note for the full argument.
"""
import pytest
from bench.ouroboros_cell import OuroborosCell


def test_arxiv_pdf_url_mapping():
    """Offline: the arXiv abs/pdf URL -> direct PDF URL mapping (no network)."""
    c = OuroborosCell(shadow=True)
    assert c._arxiv_pdf_url("http://arxiv.org/abs/1706.03762v5") == \
        "https://arxiv.org/pdf/1706.03762v5"
    assert c._arxiv_pdf_url("https://arxiv.org/abs/1811.01933") == \
        "https://arxiv.org/pdf/1811.01933"
    assert c._arxiv_pdf_url("https://example.com/x") == ""


def test_extractive_brief_is_real_offline():
    """Offline: the no-LLM fallback distils real overlap, never a placeholder."""
    c = OuroborosCell(shadow=True, reader_backend="none")
    rel, brief = c._extractive_brief(
        "self-attention transformer architecture",
        "The Transformer uses self-attention. Self-attention relates positions "
        "of a single sequence. The architecture dispenses with recurrence.")
    assert rel in ("HIGH", "MEDIUM", "LOW")
    assert "attention" in brief.lower()
    assert "Shadow candidate for target" not in brief   # old placeholder is gone


def test_bad_scheme_download_never_raises():
    """Offline: a non-http URL degrades to an error field, never an exception."""
    c = OuroborosCell(shadow=True)
    out = c._download_and_extract("ftp://example.com/x.pdf")
    assert out["error"] == "bad-scheme" and out["chars"] == 0


@pytest.mark.network
def test_real_paper_fetched_read_and_briefed():
    """Network: fetch a stable fully-OA arXiv paper, parse its PDF, brief it."""
    c = OuroborosCell(shadow=True, reader_backend="none", enable_fulltext=True)
    paper = {"title": "Attention Is All You Need",
             "url": "http://arxiv.org/abs/1706.03762v5", "abstract": ""}

    res = c.resolve_fulltext_url(paper)
    # arXiv serves the PDF at arxiv.org/pdf/<id> (no ".pdf" suffix in the modern scheme)
    assert res["via"] == "arxiv" and "/pdf/1706.03762" in res["url"]

    dl = c._download_and_extract(res["url"])
    assert dl["chars"] > 2000, f"expected real parsed text, got {dl}"
    assert "attention" in dl["text"].lower()

    briefs = c._read_and_brief(
        [{"target": "self-attention transformer architecture",
          "source_ref": paper["url"]}],
        [{"papers": [paper]}])
    assert len(briefs) == 1
    b = briefs[0]
    assert b["fulltext_chars"] > 2000        # full text really parsed
    assert b["via"] == "arxiv"
    assert b["source_hash"]                   # content was hashed
    assert b["relevance"] in ("HIGH", "MEDIUM", "LOW", "NONE")
    assert b["brief"]                         # a real brief exists


@pytest.mark.network
def test_shadow_log_captures_briefs():
    """Network: the shadow log serialises real briefs for post-hoc study, and the
    candidate description is a real brief (never the old placeholder string)."""
    c = OuroborosCell(shadow=True, reader_backend="none")
    log = c.run_between_rounds(round_idx=0, anomalies=["transformer attention"],
                               immune_response=None, round_findings=None)
    d = log.to_dict()
    assert "briefs" in d                      # briefs are serialised
    for cand in d["candidate_claims"]:
        assert "Shadow candidate for target" not in cand["description"]
