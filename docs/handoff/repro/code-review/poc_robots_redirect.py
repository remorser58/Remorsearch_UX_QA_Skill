import json, sys, unittest
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T
from test_ux_read import ServerCase
setUpModule, tearDownModule = T.setUpModule, T.tearDownModule

class P(ServerCase):
    def test_robots_redirect(self):
        # hop.test's robots.txt redirects to a terms_restricted host, a deny-listed host and a switched-off endpoint
        self.server.redirect("hop.test", "/robots.txt", self.url("confirmed.test", "/robots.txt"))
        self.server.page("hop.test", "/p", "post-normal.html")
        self.server.redirect("hop2.test", "/robots.txt", self.url("denied.test", "/robots.txt"))
        self.server.page("hop2.test", "/p", "post-normal.html")
        self.server.redirect("redir.test", "/robots.txt", self.url("disabled-api.test", "/v1/search/robots.txt"))
        self.server.page("redir.test", "/p", "post-normal.html")
        self.start("--deny-host", "denied.test")
        for host in ("hop.test", "hop2.test", "redir.test"):
            code, summary, _ = self.read(self.url(host, "/p"))
            print("\n", host, "read exit", code, summary["bucket"])
        print("confirmed.test (terms_restricted, confirmed) hits:", self.server.hits("confirmed.test"))
        print("denied.test (deny list) hits:", self.server.hits("denied.test"))
        print("disabled-api.test (never_call) hits:", self.server.hits("disabled-api.test"))
        robots_entries = [e for e in self.ledger_entries() if e.get("purpose") == "robots"]
        print("ledger robots entries:", [(e["host"], e.get("redirects")) for e in robots_entries])

if __name__ == "__main__":
    unittest.main(verbosity=0)
