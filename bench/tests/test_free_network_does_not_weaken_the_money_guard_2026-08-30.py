"""The free-network window must never open a PAID endpoint.

Founder ruling 2026-08-30: "the internet here is always enabled... ouroboros
outreach clearly only needs to cost money during a real experimental run.
Testing it here... clearly needs to cost nothing more than my Max subscription."

So `free_network` tests run by default and reach the wire. The guard's real
subject -- spending money -- is unchanged, and this file is the proof. It is
written the way the guard's own tests are: assert the DENIAL, not the intent.

WHY AN ALLOW-LIST WAS THE WRONG SHAPE, MEASURED. The first attempt enumerated
free hosts (arxiv.org, api.semanticscholar.org, ...). Literature retrieval
follows a DOI to whichever publisher hosts the paper, and the run immediately
hit www.mdpi.com, which no such list would have contained. An allow-list
therefore passes by DENYING the fetch the test exists to exercise -- which is
precisely how these 3 tests spent 49 days reporting success without ever
running.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import conftest as G


class TestThePaidDenyList:
    def test_paid_hosts_are_denied_even_inside_the_window(self):
        G.set_free_window(True)
        try:
            for host in ("openrouter.ai", "api.openai.com", "api.anthropic.com",
                         "api.deepseek.com"):
                assert not G._free_allowed(host), (
                    f"{host} is a metered endpoint and the free window allowed it"
                )
        finally:
            G.set_free_window(False)

    def test_a_subdomain_of_a_paid_host_is_also_denied(self):
        G.set_free_window(True)
        try:
            assert not G._free_allowed("eu.api.openai.com")
        finally:
            G.set_free_window(False)

    def test_free_hosts_are_allowed_inside_the_window(self):
        G.set_free_window(True)
        try:
            for host in ("arxiv.org", "export.arxiv.org", "www.mdpi.com",
                         "api.semanticscholar.org", "doi.org"):
                assert G._free_allowed(host), host
        finally:
            G.set_free_window(False)

    def test_nothing_is_allowed_with_the_window_shut(self):
        G.set_free_window(False)
        for host in ("arxiv.org", "www.mdpi.com", "openrouter.ai"):
            assert not G._free_allowed(host), (
                f"{host} allowed outside a free_network test — the window is "
                f"leaking into the ordinary offline suite"
            )

    def test_a_bytes_hostname_is_normalised_not_waved_through(self):
        """Measured: the guard records b'api.semanticscholar.org'."""
        G.set_free_window(True)
        try:
            assert not G._free_allowed("b'api.openai.com'")
        finally:
            G.set_free_window(False)


class TestMeteredBinaries:
    def test_metered_clis_are_named(self):
        assert {"codex", "gemini", "chatgpt", "llm"} <= set(G._PAID_BINARIES)

    def test_claude_is_deliberately_not_metered(self):
        """Max-plan CLI: the ruling names it as the permitted cost floor."""
        assert "claude" not in G._PAID_BINARIES
        assert "claude" in G._NETWORK_BINARIES     # still blocked OUTSIDE a window


class TestTheWindowAlwaysCloses:
    def test_set_free_window_false_clears_resolved_ips(self):
        G.set_free_window(True)
        G._free_ips.add("1.2.3.4")
        G.set_free_window(False)
        assert G._free_ips == set(), "resolved IPs leaked past the window"
