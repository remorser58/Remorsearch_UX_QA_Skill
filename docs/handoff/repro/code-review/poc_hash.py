import hashlib, json, sys, unittest
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T
from test_ux_read import ServerCase
setUpModule, tearDownModule = T.setUpModule, T.tearDownModule

class P(ServerCase):
    def test_hash(self):
        self.server.page("pii.test", "/p", "pii-post.html")
        self.start()
        code, summary, out = self.read(self.url("pii.test", "/p"))
        req = [e for e in self.ledger_entries() if e["kind"] == "request" and e.get("purpose") == "page"][-1]
        outc = [e for e in self.ledger_entries() if e["kind"] == "outcome"][-1]
        saved = self.page_files()[0].read_text(encoding="utf-8")
        print("\nrequest entry sha256:", req["content_sha256"][:16], "text_chars", req["text_chars"])
        print("outcome entry sha256:", outc["content_sha256"][:16], "text_chars", outc["text_chars"])
        print("saved page sha256   :", hashlib.sha256(saved.encode()).hexdigest()[:16])
        closed = json.loads(self.cli("close", "--run", self.run_dir)[1])
        kept = [json.loads(l) for l in (self.run_dir / "access-ledger.jsonl").read_text().splitlines()]
        print("after close, request hash kept:", any(e.get("content_sha256") == req["content_sha256"] for e in kept))

if __name__ == "__main__":
    unittest.main(verbosity=0)
