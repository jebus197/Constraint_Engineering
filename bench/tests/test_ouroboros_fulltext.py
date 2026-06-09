"""Full-text resolver: Unpaywall (legal) first, Sci-Hub (configurable, off-by-default)
last; the cited source is ALWAYS the original DOI, never Sci-Hub."""
import pytest
from bench.ouroboros_cell import OuroborosCell


def test_normalise_doi():
    c = OuroborosCell(shadow=True)
    assert c._normalise_doi("https://doi.org/10.1/x") == "10.1/x"
    assert c._normalise_doi("doi:10.2/y") == "10.2/y"
    assert c._normalise_doi("10.3/z") == "10.3/z"
    assert c._normalise_doi("not-a-doi") == ""
    assert c._normalise_doi("") == ""


def test_scihub_off_by_default(monkeypatch):
    c = OuroborosCell(shadow=True)
    monkeypatch.setattr(c, "_unpaywall_oa_pdf", lambda doi, email: "")  # no OA copy
    r = c.full_text_for_doi("10.1/paywalled")
    assert r["via"] == "none" and r["url"] == ""
    assert r["doi"] == "10.1/paywalled"   # original DOI preserved as the cited source


def test_scihub_on_returns_mirror_but_cites_original(monkeypatch):
    c = OuroborosCell(shadow=True, enable_scihub_fallback=True,
                      scihub_mirror="https://sci-hub.test")
    monkeypatch.setattr(c, "_unpaywall_oa_pdf", lambda doi, email: "")
    r = c.full_text_for_doi("https://doi.org/10.1/paywalled")
    assert r["via"] == "scihub"
    assert r["url"] == "https://sci-hub.test/10.1/paywalled"
    assert r["doi"] == "10.1/paywalled"   # cite the original, NEVER sci-hub


def test_unpaywall_preferred_over_scihub(monkeypatch):
    c = OuroborosCell(shadow=True, enable_scihub_fallback=True)
    monkeypatch.setattr(c, "_unpaywall_oa_pdf", lambda doi, email: "https://oa.example/x.pdf")
    r = c.full_text_for_doi("10.1/has-oa")
    assert r["via"] == "unpaywall" and r["url"] == "https://oa.example/x.pdf"


def test_non_doi_returns_empty():
    c = OuroborosCell(shadow=True)
    assert c.full_text_for_doi("arxiv.org/abs/1234")["url"] == ""
