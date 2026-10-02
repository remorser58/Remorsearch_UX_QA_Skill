import json, sys, unittest
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T
from test_ux_read import ServerCase
setUpModule, tearDownModule = T.setUpModule, T.tearDownModule

class P(ServerCase):
    def test_exit(self):
        self.start()
        code, out, _ = self.cli("robots", "--run", self.run_dir, "http://m.lonely.test/x")  # an unresolvable name
        print("\nrobots exit", code, json.loads(out))

if __name__ == "__main__":
    unittest.main(verbosity=0)
