"""PoC: a --routes table can turn the confirmed YouTube terms stop into a read through any host."""
import copy, json, os, sys, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T  # reuse the fixture server and the network guard
from test_ux_read import ServerCase, spec, net

setUpModule = T.setUpModule
tearDownModule = T.tearDownModule
PACKAGED = T.SKILL / "uxresearch" / "data" / "routes.json"

class P(ServerCase):
    def test_custom_youtube_platform_reads_a_mirror(self):
        env = {net.ENV_TEST_RESOLVE: os.environ[net.ENV_TEST_RESOLVE] + ",mirror.test=127.0.0.1"}
        with mock.patch.dict(os.environ, env):
            feed = ('<?xml version="1.0"?><rss><channel><title>c</title><item><title>v</title>'
                    '<link>https://www.youtube.com/watch?v=dQw4w9WgXcQ</link>'
                    '<description>MIRRORED-YOUTUBE-COMMENTS-SENTINEL 댓글 본문입니다.</description></item></channel></rss>')
            self.server.add("mirror.test", "/feed", spec(body=feed, ctype="application/rss+xml"))
            routes = copy.deepcopy(json.loads(PACKAGED.read_text(encoding="utf-8")))
            yt = next(p for p in routes["platforms"] if p["id"] == "youtube")
            # the same platform id the packaged youtube-terms entry names as its official_route
            yt["official"] = [{"kind": "feed", "url": self.url("mirror.test", "/feed?v={video}"), "scope": "all"}]
            path = self.tmp / "routes.custom.json"
            path.write_text(json.dumps(routes, ensure_ascii=False), encoding="utf-8")
            code, out, err = self.cli("start", "--run", self.run_dir, "--routes", path)
            self.assertEqual(code, 0, out)
            code, summary, out = self.read("https://www.youtube.com/shorts/dQw4w9WgXcQ")
            print("\nexit", code, summary["bucket"], summary["rung"], summary["reasons"], summary.get("terms"))
            print("text has sentinel:", "MIRRORED-YOUTUBE-COMMENTS-SENTINEL" in out)
            print("mirror hits:", self.server.hits("mirror.test"))

if __name__ == "__main__":
    unittest.main(verbosity=1)
