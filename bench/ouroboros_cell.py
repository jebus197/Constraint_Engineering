"""CDSFL Ouroboros Cell (O1) — External research and self-improvement.

In mythology, the ouroboros is the snake consuming its own tail, representing
cyclical self-reference and self-improvement. In CDSFL, the Ouroboros gathers
external research from sources like arXiv and Semantic Scholar, and can gather
data from other CDSFL-linked network systems. It processes what it finds and
presents candidate claims back to the pipeline for verification by other cells.

Key design decisions (confer 12 April 2026, Gemini 3.1 Pro + Codex 5.3):

1. **Between-round placement**: Ouroboros runs AFTER each round completes,
   not during verification. Stage 2 assumes the batch already exists.
   Inserting a cell that creates new claims during verification is
   architecturally confused. One-round lag is acceptable because the
   Macrophage monitors in real time for emergencies.

2. **Disjoint evidence paths**: If the Ouroboros proposes a finding based
   on a paper, the B-Cell must verify it through a completely different
   method (computation, execution, or a strictly different data source).

3. **Provenance**: All external-origin claims carry explicit provenance
   tags: origin_type, source_ref, retrieval_query, retrieved_at,
   source_hash, source_diversity. Mandatory falsification_debt: high.

CRITICAL: O1 runs in SHADOW mode for Exp 39. It logs what it WOULD have
injected into the pipeline but does NOT actually inject claims. Promotion
to active mode requires explicit HIL approval.

Hard caps for Exp 39: max 3 queries per round, max 2 candidate claims.

Refactored from ouroboros_cell.py: 12 April 2026 (cell type split).
The original ouroboros_cell.py was renamed to macrophage_cell.py (internal
monitor). This file is the NEW external research cell.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cdsfl.ouroboros")


@dataclass
class ProvenancePacket:
    """Provenance metadata for an external-origin claim.

    Every claim the Ouroboros produces must carry a complete provenance
    packet. The Macrophage monitors these for source monoculture and
    missing fields.
    """
    origin_type: str = "external_ouroboros"  # Always external for O1
    source_ref: str = ""       # Paper DOI, URL, or identifier
    retrieval_query: str = ""  # The search query that found this source
    retrieved_at: str = ""     # ISO 8601 timestamp of retrieval
    source_hash: str = ""      # SHA-256 of source content
    source_diversity: float = 0.0  # Diversity metric (0-1)

    def to_dict(self) -> dict:
        return {
            "origin_type": self.origin_type,
            "source_ref": self.source_ref,
            "retrieval_query": self.retrieval_query,
            "retrieved_at": self.retrieved_at,
            "source_hash": self.source_hash,
            "source_diversity": str(self.source_diversity),
        }


@dataclass
class OuroborosCandidateClaim:
    """A candidate claim produced by the Ouroboros for pipeline injection.

    In shadow mode, these are logged but NOT injected. In active mode,
    they enter the normal intake and go through standard triage and
    verification gates like any other finding.
    """
    claim_id: str
    description: str
    provenance: ProvenancePacket
    relevance_score: float = 0.0   # How relevant to observed anomalies (0-1)
    falsification_debt: str = "high"  # External claims always start high
    round_observed: int = 0        # Which round triggered this research
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "description": self.description,
            "provenance": self.provenance.to_dict(),
            "relevance_score": str(self.relevance_score),
            "falsification_debt": self.falsification_debt,
            "round_observed": self.round_observed,
            "timestamp": str(self.timestamp),
        }


@dataclass
class OuroborosShadowLog:
    """Shadow replay log: records what the Ouroboros WOULD have done.

    For Exp 39, the Ouroboros does not inject claims. Instead, it logs
    what it noticed, what it queried, what came back, and what claims
    it would have created. This allows evaluation without pipeline risk.
    """
    round_idx: int
    anomalies_observed: List[str] = field(default_factory=list)
    queries_issued: List[Dict[str, str]] = field(default_factory=list)
    metadata_retrieved: List[Dict[str, Any]] = field(default_factory=list)
    candidate_claims: List[OuroborosCandidateClaim] = field(default_factory=list)
    # Real read+brief records for the shadow full-text loop (added 2026-07-12). Each
    # entry carries: target, source_ref (cited DOI/arXiv id), via, fulltext_chars,
    # source_hash, relevance, brief, reader_model, raw_reader_response, elapsed_s, error.
    briefs: List[Dict[str, Any]] = field(default_factory=list)
    would_have_injected: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "round_idx": self.round_idx,
            "anomalies_observed": self.anomalies_observed,
            "queries_issued": self.queries_issued,
            "metadata_retrieved": self.metadata_retrieved,
            "candidate_claims": [c.to_dict() for c in self.candidate_claims],
            "briefs": self.briefs,
            "would_have_injected": self.would_have_injected,
            "timestamp": str(self.timestamp),
        }


class OuroborosCell:
    """O1 cell: external research and self-improvement engine.

    Runs between rounds. Observes what happened in the completed round,
    queries external sources based on anomalies, and produces candidate
    claims for the next round's normal intake.

    Shadow mode (Exp 39): logs only, no pipeline injection.

    Example::

        o1 = OuroborosCell(shadow=True)
        shadow_log = o1.run_between_rounds(
            round_idx=3,
            anomalies=["verdict_cluster detected"],
            immune_response=response,
        )
        # In shadow mode, shadow_log records what O1 would have done
    """

    # Hard caps for Exp 39
    MAX_QUERIES_PER_ROUND: int = 3
    MAX_CANDIDATE_CLAIMS: int = 2
    # Real-work caps (added 2026-07-12 for the shadow full-text loop). Network+parse
    # and LLM reads are expensive, so both are hard-bounded per round; the reader is
    # handed at most MAX_FULLTEXT_CHARS of extracted text.
    MAX_FULLTEXT_FETCHES_PER_ROUND: int = 2   # network+parse is expensive
    MAX_READER_CALLS_PER_ROUND: int = 2       # one LLM read per fetched paper
    MAX_FULLTEXT_CHARS: int = 24000           # cap text handed to the reader
    MAX_PDF_BYTES: int = 20 * 1024 * 1024     # mirror run_round_robin.py download cap

    def __init__(
        self,
        shadow: bool = True,
        allowed_sources: Optional[List[str]] = None,
        *,
        contact_email: str = "cdsfl-ouroboros@constraint-engineering.local",
        enable_scihub_fallback: bool = False,
        scihub_mirror: str = "",
        reader_backend: str = "haiku",   # "haiku" | "deepseek" | "none"
        reader_model: str = "",          # override; default per backend
        enable_fulltext: bool = True,    # download+parse OA full text before reading
    ) -> None:
        self.shadow = shadow  # MUST be True for Exp 39
        # OpenAlex added (free, no key, domain-general) as the reliable default fallback.
        self.allowed_sources = allowed_sources or ["arxiv", "semantic_scholar", "openalex"]
        # Full-text resolution config (off by default). enable_scihub_fallback flips on the
        # silent last-resort retrieval path; scihub_mirror overrides the mirror (config/env).
        self.contact_email = contact_email
        self.enable_scihub_fallback = enable_scihub_fallback
        self.scihub_mirror = scihub_mirror
        # Cheap-reader (librarian) config for the shadow full-text loop. reader_backend
        # picks the dispatch route; "none" forces the deterministic extractive brief
        # (used by CI so the test never hard-depends on an LLM backend being reachable).
        self.reader_backend = reader_backend
        self.reader_model = reader_model
        self.enable_fulltext = enable_fulltext
        self._claim_counter = 0
        self._round_logs: List[OuroborosShadowLog] = []

    def _next_claim_id(self) -> str:
        self._claim_counter += 1
        return f"o1_claim_{self._claim_counter:04d}"

    def run_between_rounds(
        self,
        round_idx: int,
        anomalies: Optional[List[str]] = None,
        immune_response: Optional[Any] = None,
        round_findings: Optional[List[Any]] = None,
    ) -> OuroborosShadowLog:
        """Execute Ouroboros between-round research cycle.

        This is the main entry point. Called AFTER a round completes.

        Args:
            round_idx: Index of the just-completed round.
            anomalies: Anomaly descriptions from Macrophage observations.
            immune_response: The ImmuneResponse from the completed round.
            round_findings: Findings from the completed round.

        Returns:
            OuroborosShadowLog recording what O1 did (or would have done).
        """
        shadow_log = OuroborosShadowLog(round_idx=round_idx)

        # Step 1: Target selection — identify what to research based on anomalies
        targets = self._select_targets(
            anomalies or [],
            immune_response,
            round_findings,
        )
        shadow_log.anomalies_observed = targets

        if not targets:
            self._round_logs.append(shadow_log)
            return shadow_log

        # Step 2: Structured metadata fetch (mocked in shadow/Exp 39)
        queries = self._build_queries(targets)
        shadow_log.queries_issued = queries[:self.MAX_QUERIES_PER_ROUND]

        metadata = self._fetch_metadata(
            shadow_log.queries_issued,
        )
        shadow_log.metadata_retrieved = metadata

        # Step 2.5 (SHADOW real work): resolve OA full text, download, read, brief.
        # Briefs are logged only — never injected into a model prompt, never touch the
        # maths. Wrapped so any fetch/reader failure degrades to error fields, not a crash.
        try:
            shadow_log.briefs = self._read_and_brief(
                shadow_log.queries_issued, metadata,
            )
        except Exception as exc:  # noqa: BLE001 — shadow work is strictly non-fatal
            logger.warning("Ouroboros read+brief failed (round %d): %s", round_idx, exc)
            shadow_log.briefs = []

        # Step 3: Candidate claim generation — built from the REAL briefs
        candidates = self._generate_candidates(
            targets, metadata, round_idx, shadow_log.briefs,
        )
        shadow_log.candidate_claims = candidates[:self.MAX_CANDIDATE_CLAIMS]
        shadow_log.would_have_injected = len(candidates) > 0

        # In shadow mode, log only — no pipeline injection
        if shadow_log.would_have_injected:
            logger.info(
                "Ouroboros [shadow] round %d: would inject %d candidate claims "
                "(capped at %d). Queries: %d. Targets: %s",
                round_idx, len(candidates),
                self.MAX_CANDIDATE_CLAIMS,
                len(shadow_log.queries_issued),
                targets[:3],
            )

        self._round_logs.append(shadow_log)
        self._last_shadow_log = shadow_log
        return shadow_log

    def _select_targets(
        self,
        anomalies: List[str],
        immune_response: Optional[Any],
        round_findings: Optional[List[Any]],
    ) -> List[str]:
        """Select research targets based on round anomalies and findings.

        Prioritises:
        1. Macrophage-flagged anomalies (direct signal)
        2. Recurring disputed findings (convergence failures)
        3. High-severity unresolved claims
        """
        targets = []

        # Macrophage anomalies are direct research triggers
        for anomaly in anomalies:
            targets.append(anomaly)

        # Check for disputed/uncertain findings — use descriptions, not IDs
        # (HARD FIX: finding IDs like 'Gemini_F002' are unsearchable)
        if immune_response:
            final_verdicts = getattr(immune_response, "final_verdicts", {})

            # Build fid → description lookup from round findings
            fid_to_desc: Dict[str, str] = {}
            if round_findings:
                for f in round_findings:
                    fid = getattr(f, "finding_id", None)
                    desc = getattr(f, "description", "")
                    if fid and desc:
                        fid_to_desc[fid] = desc[:200]

            for fid, verdict in final_verdicts.items():
                if verdict == "UNCERTAIN":
                    desc = fid_to_desc.get(fid, "")
                    if desc:
                        targets.append(f"uncertain_finding:{desc}")
                    else:
                        # Fallback: use fid but prefix for clarity
                        targets.append(f"uncertain_finding:{fid}")

        return targets[:5]  # Cap targets

    def _build_queries(
        self,
        targets: List[str],
    ) -> List[Dict[str, str]]:
        """Build structured search queries from targets."""
        queries = []
        for target in targets[:self.MAX_QUERIES_PER_ROUND]:
            # Round-robin source selection (HARD FIX: was always [0])
            source_idx = len(queries) % len(self.allowed_sources) if self.allowed_sources else 0
            source = self.allowed_sources[source_idx] if self.allowed_sources else "arxiv"

            query = {
                "target": target,
                "source": source,
                "query": self._target_to_query(target),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            queries.append(query)
        return queries

    def _target_to_query(self, target: str) -> str:
        """Convert a target description to a search query.

        Strips statistical noise (percentages, counts, decimals, parenthetical
        details) and extracts the conceptual core suitable for an academic
        search API. Returns a query of at most 10 keywords.

        Examples:
            "92% of verdicts are REJECTED (11/12) — possible systemic bias"
            → "verdicts REJECTED possible systemic bias"

            "Confidence variance very low (0.0002) with mean 0.85 — models over-confident"
            → "Confidence variance very low models over-confident uniformly"
        """
        import re

        # Expand prefixed labels into searchable terms
        # "uncertain_finding:f3" → "uncertain finding"
        # "round_4_anomalies:3" → "round anomalies"
        prefix = ""
        if ":" in target:
            prefix, target = target.split(":", 1)
            # Convert underscored prefix to words, strip trailing digits
            prefix = re.sub(r'_\d+$', '', prefix)
            prefix = prefix.replace("_", " ").strip()

        # Extract quoted names before removing them (e.g. 'b_cell' → b_cell)
        quoted_names = re.findall(r"'([^']*)'", target)
        quoted_terms = ' '.join(n.replace('_', ' ') for n in quoted_names)

        # Remove parenthetical noise: (11/12), (0.0002), (21.7x median 0.40s)
        target = re.sub(r'\([^)]*\)', '', target)

        # Remove numbers with optional units/suffixes: 92%, 8.70s, 3x, 0.85
        target = re.sub(r'\b\d+\.?\d*[%sx]?\s*', '', target)

        # Remove em-dashes/hyphens used as separators
        target = re.sub(r'\s*[\u2014\u2013—]+\s*', ' ', target)

        # Remove quoted stage names (already extracted above)
        target = re.sub(r"'[^']*'", '', target)

        # Combine: prefix + cleaned target + quoted names
        combined = f"{prefix} {target} {quoted_terms}"

        # Collapse whitespace
        combined = re.sub(r'\s+', ' ', combined).strip()

        # Remove common noise words that don't help search
        noise = {'of', 'are', 'is', 'the', 'a', 'an', 'with', 'may', 'be',
                 'from', 'for', 'in', 'to', 'and', 'or', 'took', 'than',
                 'mean', 'median'}
        words = [w for w in combined.split() if w.lower() not in noise]

        # Cap at 10 keywords; fallback if empty
        result = ' '.join(words[:10])
        return result if result else "pipeline anomaly detection"

    def _fetch_metadata(
        self,
        queries: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Fetch structured metadata from arXiv and Semantic Scholar.

        Real API calls (wired 13 April 2026). Results are logged even in
        shadow mode — the ouroboros still does not inject claims into the
        pipeline, but now gathers genuine external evidence for calibration.

        Graceful degradation: if an API call fails (network, rate limit,
        package missing), falls back to shadow_mock for that query.
        """
        results = []
        for query in queries:
            source = query.get("source", "arxiv")
            query_text = query.get("query", "")
            fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            try:
                fetchers = {
                    "arxiv": self._query_arxiv,
                    "semantic_scholar": self._query_semantic_scholar,
                    "openalex": self._query_openalex,
                }
                fetch = fetchers.get(source)
                # Hard-capped primary attempt (libraries' own timeouts are unreliable).
                papers = (self._run_with_timeout(
                    fetch, query_text, timeout_s=20.0, max_results=3) if fetch else [])
                fetched_via = source if papers else None
                # Fallback chain: if the requested source timed out / returned nothing,
                # try a proven-fast source so the cell is never silently empty when an
                # alternate can do the job (OpenAlex: free, no key, domain-general).
                for alt in ("openalex", "arxiv"):
                    if papers or alt == source:
                        continue
                    papers = self._run_with_timeout(
                        fetchers[alt], query_text, timeout_s=20.0, max_results=3)
                    if papers:
                        fetched_via = f"{alt} (fallback from {source})"
                        break

                result = {
                    "query": query_text,
                    "source": source,
                    "fetched_via": fetched_via,
                    "status": "live" if papers else "live_empty",
                    "results_count": len(papers),
                    "papers": papers,
                    "fetched_at": fetched_at,
                }
            except Exception as e:
                logger.warning(
                    "O1 _fetch_metadata failed for %s query %r: %s",
                    source, query_text[:60], e,
                )
                result = {
                    "query": query_text,
                    "source": source,
                    "status": "shadow_mock",
                    "results_count": 0,
                    "papers": [],
                    "fetched_at": fetched_at,
                    "error": f"{type(e).__name__}: {str(e)[:120]}",
                }
            results.append(result)
        return results

    @staticmethod
    def _query_arxiv(query_text: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Query arXiv API. Returns list of {title, authors, abstract, url, published}."""
        import arxiv

        client = arxiv.Client(num_retries=1, page_size=max_results)
        search = arxiv.Search(
            query=query_text,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        papers = []
        for r in client.results(search):
            papers.append({
                "title": r.title,
                "authors": ", ".join(a.name for a in r.authors[:3]),
                "abstract": r.summary[:500] if r.summary else "",
                "url": r.entry_id,
                "published": r.published.isoformat() if r.published else "",
            })
        return papers

    @staticmethod
    def _query_semantic_scholar(
        query_text: str, max_results: int = 3,
    ) -> List[Dict[str, str]]:
        """Query Semantic Scholar API. Returns list of paper metadata.

        Uses SEMANTIC_SCHOLAR_API_KEY (from .env / environment) when present — the
        authenticated key removes the unauthenticated throttling that made this source
        take ~95s (2026-06-09). Unauthenticated still works (slower); the hard-timeout
        wrapper + OpenAlex fallback bound it either way."""
        import os
        from semanticscholar import SemanticScholar

        _s2_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or None
        sch = SemanticScholar(api_key=_s2_key, timeout=15)
        results = sch.search_paper(
            query_text,
            limit=max_results,
            fields=["title", "authors", "abstract", "url", "year",
                     "citationCount"],
        )
        papers = []
        for p in results[:max_results]:
            authors = ", ".join(
                a.get("name", "") if isinstance(a, dict) else str(a)
                for a in (p.authors or [])[:3]
            )
            papers.append({
                "title": p.title or "",
                "authors": authors,
                "abstract": (p.abstract or "")[:500],
                "url": p.url or "",
                "year": str(p.year) if p.year else "",
                "citations": str(p.citationCount) if p.citationCount else "0",
            })
        return papers

    @staticmethod
    def _run_with_timeout(fn, *args, timeout_s: float = 20.0, **kwargs):
        """Hard wall-clock cap on an external call. The source libraries' own
        timeouts are unreliable (Semantic Scholar's ``timeout=15`` was measured at
        95s on 2026-06-09), so this enforces a real ceiling: the call runs in a
        daemon thread; if it overruns, return [] (best-effort) and let the daemon
        die with the process. Never blocks the caller beyond ``timeout_s``."""
        import threading
        box: Dict[str, Any] = {}

        def _w():
            try:
                box["r"] = fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 — surfaced to caller below
                box["e"] = exc

        t = threading.Thread(target=_w, daemon=True)
        t.start()
        t.join(timeout_s)
        if t.is_alive():
            return []  # timed out — best-effort empty
        if "e" in box:
            raise box["e"]
        return box.get("r", [])

    @staticmethod
    def _query_openalex(query_text: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Query OpenAlex (free, NO API key, fast, domain-general — works across
        physics, biology, CS, etc.). The reliable default fallback source.
        Returns the same metadata shape as the other fetchers."""
        import json as _json
        import urllib.parse
        import urllib.request

        url = (
            "https://api.openalex.org/works?search="
            + urllib.parse.quote(query_text)
            + f"&per_page={max_results}&mailto=cdsfl-ouroboros@constraint-engineering.local"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "CDSFL-ouroboros/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 — fixed host
            data = _json.loads(resp.read().decode("utf-8"))
        papers: List[Dict[str, str]] = []
        for w in data.get("results", [])[:max_results]:
            authors = ", ".join(
                ((a.get("author") or {}).get("display_name", ""))
                for a in (w.get("authorships") or [])[:3]
            )
            inv = w.get("abstract_inverted_index")
            abstract = ""
            if inv:
                pos: Dict[int, str] = {}
                for word, idxs in inv.items():
                    for i in idxs:
                        pos[i] = word
                abstract = " ".join(pos[i] for i in sorted(pos))[:500]
            papers.append({
                "title": w.get("title") or w.get("display_name") or "",
                "authors": authors,
                "abstract": abstract,
                "url": w.get("doi") or w.get("id") or "",
                "year": str(w.get("publication_year") or ""),
                "citations": str(w.get("cited_by_count") or 0),
            })
        return papers

    # --- Full-text resolution (for the loop-close: feed real papers to the models) ---
    # Chain: Unpaywall (free, legal open-access) FIRST; Sci-Hub (configurable, OFF by
    # default, best-effort) LAST. The citation/attribution is ALWAYS the original DOI /
    # publisher — Sci-Hub is only ever a retrieval path, never a cited source. Restores
    # the originally-envisaged ouroboros source list (arXiv + Semantic Scholar + Unpaywall
    # + CORE + OpenAlex, planned 14 April 2026) and the founder's silent-Sci-Hub fallback.

    @staticmethod
    def _normalise_doi(url_or_doi: str) -> str:
        """Extract a bare DOI from a DOI URL or raw DOI; '' if not a DOI."""
        s = (url_or_doi or "").strip()
        for pre in ("https://doi.org/", "http://doi.org/", "doi:"):
            if s.lower().startswith(pre):
                s = s[len(pre):]
        return s if s.startswith("10.") else ""

    @staticmethod
    def _unpaywall_oa_pdf(doi: str, email: str, timeout_s: float = 12.0) -> str:
        """Legal open-access PDF URL for a DOI via Unpaywall, or '' if none."""
        import json as _json
        import urllib.parse
        import urllib.request
        url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}"
        req = urllib.request.Request(url, headers={"User-Agent": "CDSFL-ouroboros/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
            data = _json.loads(resp.read().decode("utf-8"))
        if not data.get("is_oa"):
            return ""
        loc = data.get("best_oa_location") or {}
        return loc.get("url_for_pdf") or loc.get("url") or ""

    def full_text_for_doi(self, doi_or_url: str) -> Dict[str, str]:
        """Resolve a full-text URL for a DOI. Returns {url, via, doi}; via is the retrieval
        path ('unpaywall' / 'scihub'), doi is ALWAYS the original (the cited source).
        Unpaywall first (legal OA); Sci-Hub only if ``enable_scihub_fallback`` is on. Empty
        url on failure (best-effort; never blocks > timeout)."""
        doi = self._normalise_doi(doi_or_url)
        if not doi:
            return {"url": "", "via": "", "doi": ""}
        email = getattr(self, "contact_email", "cdsfl-ouroboros@constraint-engineering.local")
        url = self._run_with_timeout(self._unpaywall_oa_pdf, doi, email, timeout_s=15.0)
        if url:
            return {"url": url, "via": "unpaywall", "doi": doi}
        # Configurable, off-by-default, silent last resort. Cite the original DOI only.
        if getattr(self, "enable_scihub_fallback", False):
            mirror = getattr(self, "scihub_mirror", "") or "https://sci-hub.se"
            return {"url": f"{mirror.rstrip('/')}/{doi}", "via": "scihub", "doi": doi}
        return {"url": "", "via": "none", "doi": doi}

    # --- Real full-text loop: resolve OA URL -> download -> extract -> read -> brief ---
    # Added 2026-07-12. Runs SHADOW-only: briefs are logged, never injected into a model
    # prompt and never touch c_ext / nu_k / gamma. Exp 43 stays a clean generalisation test.

    @staticmethod
    def _arxiv_pdf_url(url: str) -> str:
        """arXiv abs/pdf/entry URL -> direct PDF URL; '' if not arXiv.

        arXiv is fully open-access and is the dominant metadata source in live logs,
        so resolving it directly (before Unpaywall) materially raises fetch success.
        """
        raw = (url or "").strip()
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:v\d+)?/?$", raw)
        if not m:
            return ""
        vm = re.search(r"(v\d+)/?$", raw)   # preserve an explicit version if present
        ver = vm.group(1) if vm else ""
        return f"https://arxiv.org/pdf/{m.group(1)}{ver}"

    def resolve_fulltext_url(self, paper: Dict[str, str]) -> Dict[str, str]:
        """Resolve a fetchable full-text URL for a fetched paper.

        Order: arXiv-direct (OA) -> Unpaywall (OA) -> Sci-Hub (only if enabled).
        Returns {url, via, source_ref}; source_ref is the DOI/arXiv id we cite.
        """
        raw = paper.get("url", "") or ""
        ax = self._arxiv_pdf_url(raw)
        if ax:
            return {"url": ax, "via": "arxiv", "source_ref": raw}
        ft = self.full_text_for_doi(raw)          # existing resolver, unchanged
        if ft["url"]:
            return {"url": ft["url"], "via": ft["via"], "source_ref": ft["doi"]}
        return {"url": "", "via": "none", "source_ref": raw}

    def _download_and_extract(self, url: str, timeout_s: float = 20.0) -> Dict[str, Any]:
        """Download an OA URL and extract text. PDF via pypdf(->pdfplumber); HTML via
        BeautifulSoup. Best-effort, hard-capped, http(s)-only. Never raises.

        The URL originates from Unpaywall/arXiv metadata, never from model output, so
        this is not acting on injected instructions (SSRF guard: scheme + size + timeout).
        """
        import io
        out = {"text": "", "chars": 0, "content_type": "", "error": ""}
        if not url or not url.lower().startswith(("http://", "https://")):
            out["error"] = "bad-scheme"
            return out
        try:
            import requests
        except ImportError:
            out["error"] = "requests-missing"
            return out

        def _get():
            r = requests.get(
                url, timeout=timeout_s,
                headers={"User-Agent": "CDSFL-ouroboros/1.0 (research)"},
                stream=True)
            ctype = r.headers.get("Content-Type", "").lower()
            clen = int(r.headers.get("Content-Length", 0) or 0)
            if clen > self.MAX_PDF_BYTES:
                return {"skip": f"too-large:{clen}"}
            body = r.content[: self.MAX_PDF_BYTES + 1]
            return {"ctype": ctype, "body": body, "status": r.status_code}

        got = self._run_with_timeout(_get, timeout_s=timeout_s)   # reused daemon cap
        if not got or "skip" in (got or {}):
            out["error"] = (got or {}).get("skip", "timeout") if isinstance(got, dict) else "timeout"
            return out
        if got["status"] != 200 or len(got["body"]) < 1000:
            out["error"] = f"http-{got['status']}-or-tiny"
            return out

        ctype, body = got["ctype"], got["body"]
        out["content_type"] = ctype
        is_pdf = "pdf" in ctype or body[:5] == b"%PDF-"
        out["text"] = (self._pdf_to_text(io.BytesIO(body)) if is_pdf
                       else self._html_to_text(body))
        out["text"] = out["text"][: self.MAX_FULLTEXT_CHARS]
        out["chars"] = len(out["text"])
        if not out["text"].strip():
            out["error"] = "no-text-extracted"
        return out

    @staticmethod
    def _pdf_to_text(fp, max_pages: int = 15) -> str:
        """Extract text from a PDF byte stream. pypdf primary, pdfplumber fallback.
        (PyPDF2 is NOT installed here; pypdf is its supported successor.)"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(fp)
            parts = [(reader.pages[i].extract_text() or "")
                     for i in range(min(max_pages, len(reader.pages)))]
            txt = "\n\n".join(p for p in parts if p)
            if txt.strip():
                return txt
        except Exception:
            pass
        try:
            import pdfplumber
            fp.seek(0)
            with pdfplumber.open(fp) as pdf:
                parts = [(pdf.pages[i].extract_text() or "")
                         for i in range(min(max_pages, len(pdf.pages)))]
            return "\n\n".join(p for p in parts if p)
        except Exception:
            return ""

    @staticmethod
    def _html_to_text(body: bytes) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(body, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n")).strip()
        except Exception:
            return ""

    _READER_PROMPT = (
        "You are a research librarian. Read the paper text below and assess how "
        "relevant it is to the RESEARCH TARGET. Do not evaluate the target's truth; "
        "only judge whether this paper bears on it, and distil what it says.\n\n"
        "RESEARCH TARGET:\n{target}\n\n"
        "PAPER TITLE: {title}\nPAPER TEXT (may be truncated):\n{body}\n\n"
        "Respond with EXACTLY two lines:\n"
        "RELEVANCE: <HIGH|MEDIUM|LOW|NONE>\n"
        "BRIEF: <=120 words distilling the paper's bearing on the target; "
        "if NONE, say why in one clause"
    )

    def _cheap_reader_read(self, target: str, paper: Dict[str, str],
                           body: str) -> Dict[str, Any]:
        """Dispatch the librarian read to Haiku (primary) or DeepSeek (fallback).
        Deterministic extractive fallback if no backend is reachable. Never raises."""
        prompt = self._READER_PROMPT.format(
            target=(target or "")[:800], title=(paper.get("title", "") or "")[:300],
            body=(body or paper.get("abstract", ""))[: self.MAX_FULLTEXT_CHARS])
        model_used, raw, err, elapsed = "", "", "", 0.0

        if self.reader_backend == "haiku":
            try:
                from bench.cc2_manager import _dispatch_cli, HAIKU_MODEL
                model_used = self.reader_model or HAIKU_MODEL
                raw, elapsed = self._run_with_timeout(
                    _dispatch_cli, model_used, prompt, 60, timeout_s=75.0) or ("", 0.0)
            except Exception as e:  # noqa: BLE001 — degrade to extractive brief
                err = f"haiku:{type(e).__name__}:{str(e)[:80]}"
        elif self.reader_backend == "deepseek":
            try:
                from bench.experiment_11_orchestrator import call_deepseek
                model_used = self.reader_model or "deepseek-chat"
                raw = self._run_with_timeout(
                    call_deepseek, model_used, None, prompt, timeout_s=75.0) or ""
            except Exception as e:  # noqa: BLE001 — degrade to extractive brief
                err = f"deepseek:{type(e).__name__}:{str(e)[:80]}"

        if not raw:  # deterministic extractive fallback — keeps the brief real
            rel, brief = self._extractive_brief(target, body or paper.get("abstract", ""))
            return {"relevance": rel, "brief": brief, "raw": "",
                    "reader_model": model_used or "extractive_fallback",
                    "elapsed_s": round(elapsed, 1), "error": err or "no-backend"}

        rel_m = re.search(r"RELEVANCE:\s*(HIGH|MEDIUM|LOW|NONE)", raw, re.I)
        br_m = re.search(r"BRIEF:\s*(.+)", raw, re.I | re.S)
        return {
            "relevance": (rel_m.group(1).upper() if rel_m else "LOW"),
            "brief": (br_m.group(1).strip()[:1200] if br_m else raw.strip()[:1200]),
            "raw": raw[:4000], "reader_model": model_used,
            "elapsed_s": round(elapsed, 1), "error": err,
        }

    @staticmethod
    def _extractive_brief(target: str, text: str):
        """No-LLM fallback: pick the sentences with most target-term overlap."""
        terms = {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", target or "")}
        sents = re.split(r"(?<=[.!?])\s+", text or "")
        scored = sorted(sents, key=lambda s: -len(terms & {w.lower()
                        for w in re.findall(r"[a-zA-Z]{4,}", s)}))
        top = " ".join(scored[:3]).strip()
        overlap = len(terms & {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", text or '')})
        rel = "MEDIUM" if overlap >= 3 else ("LOW" if overlap else "NONE")
        return rel, (top[:600] or "(no extractable overlap with target)")

    def _read_and_brief(self, queries, metadata) -> List[Dict[str, Any]]:
        """For each query's top paper: resolve OA -> download -> extract -> read.
        Returns brief records for the shadow log. Bounded + best-effort; never raises."""
        briefs, fetches, reads = [], 0, 0
        for q, mres in zip(queries, metadata):
            target = q.get("target", "")
            papers = (mres.get("papers", []) or []) if isinstance(mres, dict) else []
            if not papers:
                continue
            paper = papers[0]
            rec = {"target": target, "source_ref": paper.get("url", ""),
                   "title": paper.get("title", ""), "via": "abstract_only",
                   "fulltext_chars": 0, "source_hash": "", "relevance": "",
                   "brief": "", "reader_model": "", "raw_reader_response": "",
                   "elapsed_s": 0.0, "error": ""}
            body = ""
            if self.enable_fulltext and fetches < self.MAX_FULLTEXT_FETCHES_PER_ROUND:
                res = self.resolve_fulltext_url(paper)
                if res["url"]:
                    fetches += 1
                    dl = self._download_and_extract(res["url"])
                    if dl["chars"]:
                        body = dl["text"]
                        rec["via"] = res["via"]
                        rec["fulltext_chars"] = dl["chars"]
                        rec["source_ref"] = res["source_ref"] or rec["source_ref"]
                        rec["source_hash"] = hashlib.sha256(
                            body.encode("utf-8", "ignore")).hexdigest()
                    else:
                        rec["error"] = f"fetch:{dl['error']}"
            if reads < self.MAX_READER_CALLS_PER_ROUND:
                reads += 1
                r = self._cheap_reader_read(target, paper, body)
                rec.update({k: r[k] for k in
                            ("relevance", "brief", "reader_model", "elapsed_s")})
                rec["raw_reader_response"] = r["raw"]
                if r["error"]:
                    rec["error"] = (rec["error"] + "; " + r["error"]).strip("; ")
            briefs.append(rec)
        return briefs

    def _generate_candidates(
        self,
        targets: List[str],
        metadata: List[Dict[str, Any]],
        round_idx: int,
        briefs: Optional[List[Dict[str, Any]]] = None,
    ) -> List[OuroborosCandidateClaim]:
        """Build candidate claims from REAL briefs (was a placeholder before 2026-07-12).

        Each candidate's description is the distilled librarian brief, not a synthetic
        stub; provenance carries the cited source_ref, content hash, and a real
        source_diversity (1.0 iff full text was actually parsed). Falls back to nothing
        when no relevant brief exists — it never re-emits the old placeholder string.
        """
        briefs = briefs or []
        candidates: List[OuroborosCandidateClaim] = []
        rel_map = {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}
        for rec in briefs[: self.MAX_CANDIDATE_CLAIMS]:
            if rec.get("relevance") in ("", "NONE"):
                continue
            provenance = ProvenancePacket(
                origin_type="external_ouroboros",
                source_ref=rec.get("source_ref", ""),
                retrieval_query=self._target_to_query(rec.get("target", "")),
                retrieved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                source_hash=rec.get("source_hash", ""),
                source_diversity=1.0 if rec.get("fulltext_chars", 0) else 0.0,
            )
            candidates.append(OuroborosCandidateClaim(
                claim_id=self._next_claim_id(),
                description=(rec.get("brief") or "")[:800],
                provenance=provenance,
                relevance_score=rel_map.get(rec.get("relevance", "LOW"), 0.3),
                falsification_debt="high",
                round_observed=round_idx,
            ))
        return candidates

    def get_activity_metrics(self) -> Dict[str, Any]:
        """Return activity metrics for Macrophage monitoring.

        The Macrophage monitors these metrics to detect Ouroboros
        pathologies (source monoculture, excessive querying, etc.).
        """
        if not self._round_logs:
            return {
                "queries_total": 0,
                "claims_proposed_total": 0,
                "rounds_active": 0,
                "diversity_score": 1.0,
            }

        total_queries = sum(len(log.queries_issued) for log in self._round_logs)
        total_claims = sum(len(log.candidate_claims) for log in self._round_logs)

        # Compute source diversity across all queries
        all_sources = []
        for log in self._round_logs:
            for q in log.queries_issued:
                all_sources.append(q.get("source", "unknown"))

        if all_sources:
            unique = len(set(all_sources))
            diversity = unique / len(all_sources)
        else:
            diversity = 1.0

        return {
            "queries_total": total_queries,
            "claims_proposed_total": total_claims,
            "rounds_active": len(self._round_logs),
            "diversity_score": diversity,
            "queries_this_round": (
                len(self._round_logs[-1].queries_issued) if self._round_logs else 0
            ),
            "claims_this_round": (
                len(self._round_logs[-1].candidate_claims) if self._round_logs else 0
            ),
        }

    def sign_shadow_log(
        self,
        shadow_log: OuroborosShadowLog,
        chain: Any,  # VerificationChain
    ) -> Optional[dict]:
        """Sign a shadow log entry into the verification chain.

        L1 (provenance): proves this research cycle was executed at this
        time by the Ouroboros. L2/L3 operate downstream.

        Returns the chain record, or None if signing fails.
        """
        try:
            record = chain.append_record(
                artifact_type="ouroboros_shadow_log",
                payload=shadow_log.to_dict(),
                recorded_by="ouroboros_o1",
                metadata={
                    "shadow": self.shadow,
                    "round_idx": shadow_log.round_idx,
                    "would_have_injected": shadow_log.would_have_injected,
                },
            )
            return record
        except Exception as exc:
            logger.warning("Failed to sign shadow log for round %d: %s",
                          shadow_log.round_idx, exc)
            return None
