import json, sys, unittest
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T
from test_ux_read import ServerCase, spec
setUpModule, tearDownModule = T.setUpModule, T.tearDownModule

class P(ServerCase):
    def test_scrubbed_handle(self):
        body = ("<html><body><main><article><h1>충전 앱 질문</h1><p class='writer'>닉네임(118.235)</p>"
                "<p>" + "충전 버튼이 늦게 반응해서 여러 번 눌렀어요. " * 12 + "</p></article></main></body></html>")
        self.server.add("board.test", "/p", spec(body=body))
        self.start()
        code, summary, out = self.read(self.url("board.test", "/p"))
        line = next(l for l in out.splitlines() if l.startswith("닉네임"))
        print("\nthe agent sees the handle:", repr(line))
        for handle in ("닉네임(118.235)", line):
            code, out, _ = self.cli("author-key", "--run", self.run_dir, "--platform", "board.test", "--handle", handle)
            print(f"author-key {handle!r}: exit {code} {json.loads(out)}")

if __name__ == "__main__":
    unittest.main(verbosity=0)
