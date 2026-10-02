import json, sys, unittest
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T
from test_ux_read import ServerCase, CAPTURES
setUpModule, tearDownModule = T.setUpModule, T.tearDownModule

class P(ServerCase):
    def test_totals(self):
        self.start()
        url = self.url("reported.test", "/p")
        print("\nread:", self.read(url)[0])
        print("ingest:", self.ingest(url, CAPTURES / "capture-full.html", "--context", "anonymous")[0])
        print("ingest again:", self.ingest(url, CAPTURES / "capture-full.html", "--context", "anonymous")[0])
        closed = json.loads(self.cli("close", "--run", self.run_dir)[1])
        print("totals for ONE url:", closed["totals"])
        print("host rows:", [(r["host"], r["urls"], r["refused"], r["stopped"]) for r in closed["hosts"]])

if __name__ == "__main__":
    unittest.main(verbosity=0)
