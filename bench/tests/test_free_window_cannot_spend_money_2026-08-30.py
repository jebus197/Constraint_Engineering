"""Fable's three breach falsifiers, kept and INVERTED.

PROVENANCE. Written by Fable during the third-pass panel review on 2026-08-30
against the FIRST version of the free-network window, and all three succeeded:

  1. `curl https://openrouter.ai/api/v1/models` returned HTTP 200 from inside a
     `free_network` test, because curl was not on the metered-BINARY list.
  2. `dig` resolved openrouter.ai out-of-process and a raw-IP
     `create_connection(("104.18.2.115", 443))` connected, because the deny-list
     holds NAMES and an IP matches none of them.
  3. api.x.ai, api.together.xyz, api.fireworks.ai, api.perplexity.ai and AWS
     Bedrock were all permitted — a deny-list of paid providers cannot be
     completed, because the set grows without notice.

Fable's session then died on a CLI trust error, and its work survived only
because the panel harness extracts a reviewer's files BEFORE tearing the sandbox
down (founder directive, 2026-08-30). Without that, these three would have been
deleted unread and the breach would have shipped.

The guard was rebuilt to bound by CAPABILITY rather than by enumeration, and
these tests now assert the closure rather than the breach.
"""
import ipaddress
import os
import socket
import subprocess
import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import conftest as G


class TestBreach1_MeteredBinaries:
    def test_curl_is_not_launchable_inside_the_window(self):
        """An allow-list of one, not a deny-list of the ones we thought of."""
        assert "curl" not in G._FREE_WINDOW_BINARIES
        assert G._FREE_WINDOW_BINARIES == {"claude"}

    def test_curl_is_still_a_known_network_binary(self):
        assert "curl" in G._NETWORK_BINARIES


class TestBreach2_RawIpBypass:
    def test_an_unresolved_ip_is_refused_inside_the_window(self):
        """The exact bypass: resolve out-of-process, connect to the address."""
        G.set_free_window(True)
        try:
            assert not G._free_allowed("104.18.2.115"), (
                "a raw IP obtained outside this guard was permitted — the "
                "hostname deny-list can be walked around with dig"
            )
        finally:
            G.set_free_window(False)

    def test_an_ip_this_guard_resolved_is_permitted(self):
        """The property that makes the rule usable: ordinary HTTP clients
        resolve through getaddrinfo first, so their addresses ARE known."""
        G.set_free_window(True)
        try:
            G._free_ips.add("93.184.216.34")
            assert G._free_allowed("93.184.216.34")
        finally:
            G.set_free_window(False)

    def test_ipv6_is_treated_as_an_address_not_a_name(self):
        G.set_free_window(True)
        try:
            assert not G._free_allowed("2606:4700::6812:215")
        finally:
            G.set_free_window(False)


class TestBreach3_ProvidersNobodyListed:
    """Closed by capability, not by a longer list."""

    METERED = ("api.x.ai", "api.together.xyz", "api.fireworks.ai",
               "api.perplexity.ai", "bedrock-runtime.us-east-1.amazonaws.com")

    def test_a_known_providers_key_is_held_for_the_window(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-test"
        G.set_free_window(True)
        try:
            assert "OPENROUTER_API_KEY" not in os.environ
        finally:
            G.set_free_window(False)
        assert os.environ.pop("OPENROUTER_API_KEY", None) == "sk-test"

    def test_an_UNKNOWN_providers_key_is_held_too(self):
        """This is the whole point: no list of providers is required."""
        os.environ["VENDOR_NOBODY_LISTED_API_KEY"] = "sk-unknown"
        G.set_free_window(True)
        try:
            assert "VENDOR_NOBODY_LISTED_API_KEY" not in os.environ, (
                "an unlisted provider's credential survived the window, so "
                "reaching its endpoint could still bill"
            )
        finally:
            G.set_free_window(False)
        assert os.environ.pop("VENDOR_NOBODY_LISTED_API_KEY", None) == "sk-unknown"

    def test_credentials_are_restored_afterwards(self):
        os.environ["SOME_API_KEY"] = "v"
        G.set_free_window(True)
        G.set_free_window(False)
        assert os.environ.pop("SOME_API_KEY", None) == "v"

    def test_the_paid_host_list_is_defence_in_depth_only(self):
        """Recorded honestly: it is NOT claimed to be exhaustive."""
        G.set_free_window(True)
        try:
            unlisted = [h for h in self.METERED if G._free_allowed(h)]
        finally:
            G.set_free_window(False)
        assert unlisted, (
            "if this ever becomes empty the docstring claiming the list is "
            "non-exhaustive should be revisited"
        )


class TestTheWindowIsShutByDefault:
    def test_nothing_is_permitted_outside_a_free_network_test(self):
        G.set_free_window(False)
        for h in ("arxiv.org", "openrouter.ai", "104.18.2.115"):
            assert not G._free_allowed(h)


class TestEnforcementNotJustPolicy:
    """CC2's methodological finding, third-pass review 2026-08-30.

    The first eight guard tests all called `_free_allowed(host)` -- the pure
    name predicate -- and never exercised `_guard_popen_init` or `_guard_connect`
    with the window open. They asserted the POLICY; both breaches were in the
    ENFORCEMENT. A test file titled "does not weaken the money guard" that only
    checks a predicate is not evidence for its own title.
    """

    def test_curl_to_a_paid_host_is_DENIED_by_the_popen_guard(self):
        G.set_free_window(True)
        try:
            with pytest.raises(Exception) as exc:
                subprocess.Popen(["curl", "-sS", "https://api.openai.com/v1/models"])
            assert "netguard" in str(exc.value).lower() or "denied" in str(exc.value).lower(), exc.value
        finally:
            G.set_free_window(False)

    def test_curl_to_a_FREE_host_is_also_denied_inside_the_window(self):
        """The allow-list is one binary. Free hosts are reached in-process."""
        G.set_free_window(True)
        try:
            with pytest.raises(Exception):
                subprocess.Popen(["curl", "-sS", "https://arxiv.org/"])
        finally:
            G.set_free_window(False)

    def test_a_raw_ip_socket_connect_is_DENIED_by_the_connect_guard(self):
        """The second breach, at the enforcement layer rather than the predicate."""
        G.set_free_window(True)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with pytest.raises(Exception) as exc:
                s.connect(("172.66.0.243", 443))
            assert "netguard" in str(exc.value).lower() or "denied" in str(exc.value).lower(), exc.value
            s.close()
        finally:
            G.set_free_window(False)

    def test_a_named_paid_host_is_DENIED_by_the_resolver_guard(self):
        G.set_free_window(True)
        try:
            with pytest.raises(Exception) as exc:
                socket.getaddrinfo("api.openai.com", 443)
            assert "netguard" in str(exc.value).lower() or "denied" in str(exc.value).lower(), exc.value
        finally:
            G.set_free_window(False)

    def test_a_free_host_resolves_inside_the_window(self):
        """The permission the whole change exists to grant."""
        if not G._network_is_up():
            pytest.skip("no route to the internet")
        G.set_free_window(True)
        try:
            res = socket.getaddrinfo("export.arxiv.org", 443)
            assert res
        finally:
            G.set_free_window(False)


class TestOneCanonicalPaidHostList:
    """CC2, third-pass 2026-08-30: the netguard and the simulated-run tripwire
    each held a hand-maintained copy, they had already diverged 8 vs 5, and BOTH
    omitted api.groq.com and models.inference.ai.azure.com — which
    bench/run_benchmark.py actually dispatches to."""

    def test_the_guard_uses_the_canonical_list(self):
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
        from live_dispatch_policy import PAID_HOSTS
        assert G._PAID_HOSTS is PAID_HOSTS, "the netguard has its own copy again"

    def test_the_hosts_this_repo_actually_dispatches_to_are_in_it(self):
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
        from live_dispatch_policy import PAID_HOSTS
        for h in ("api.groq.com", "models.inference.ai.azure.com"):
            assert h in PAID_HOSTS, f"{h} is dispatched to by this repo and is not listed"

    def test_the_sim_harness_imports_it_rather_than_copying(self):
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "tools" / "run_simulated_experiment.py").read_text(encoding="utf-8")
        assert "from live_dispatch_policy import PAID_HOSTS" in src, (
            "the simulated-run tripwire is maintaining its own paid-host list again"
        )
