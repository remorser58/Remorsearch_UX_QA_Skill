"""Can a route table given with `start --routes` (or an edit of the run's routes.json) send a
confirmed terms_restricted URL (YouTube) to a third-party mirror in official-only mode?
Loopback only: mirror.test maps to 127.0.0.1 through the reader's own test hooks."""
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.environ["REMORSEARCH_ALLOW_PRIVATE"] = "1"
os.environ["HARNESS_ALLOW_LOOPBACK"] = "1"

HITS = []


class Mirror(BaseHTTPRequestHandler):
    def do_GET(self):
        HITS.append(self.path)
        if self.path == "/robots.txt":
            body, ctype = b"User-agent: *\nAllow: /\n", "text/plain"
        else:
            body = ("<?xml version='1.0'?><rss version='2.0'><channel><title>mirror of a YouTube video</title>"
                    "<item><title>comment 1</title><link>https://www.youtube.com/watch?v=dQw4w9WgXcQ</link>"
                    "<description>" + "a commenter's words copied by a third-party front end. " * 10 +
                    "</description></item></channel></rss>").encode()
            ctype = "application/rss+xml"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Mirror)
threading.Thread(target=server.serve_forever, daemon=True).start()
PORT = server.server_address[1]
os.environ["REMORSEARCH_TEST_RESOLVE"] = "mirror.test=127.0.0.1"

sys.path.insert(0, str(Path(__file__).parent))
from harness import run, summary, NET_LOG  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="r1-mirror-", dir=str(Path(__file__).parent)))
packaged = json.loads(Path("/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa/uxresearch/data/routes.json")
                      .read_text(encoding="utf-8"))
custom = json.loads(json.dumps(packaged))
for platform in custom["platforms"]:
    if platform["id"] == "youtube":
        platform["official"] = [{"kind": "feed", "scope": "all", "auth": "none",
                                 "url": f"http://mirror.test:{PORT}/feed/{{video}}"}]
        platform["path"] = "^/(?:watch|(?:shorts|live|embed)/(?P<video>[A-Za-z0-9_-]{11}))/?$"
routes_path = WORK / "custom-routes.json"
routes_path.write_text(json.dumps(custom))
folder = WORK / "run"
code, out, err, net = run(["start", "--run", str(folder), "--routes", str(routes_path)])
print("start:", code)
code, out, err, net = run(["read", "https://www.youtube.com/shorts/dQw4w9WgXcQ", "--run", str(folder),
                           "--max-wait", "60"])
s = summary(err)
print("read exit", code, {k: s.get(k) for k in ("bucket", "rung", "verdict", "stop_class", "reasons", "access_basis",
                                                "terms", "extraction_source", "text_chars")})
print("mirror hits:", HITS)
print("page text head:", out[:600])

# Second path: no --routes at all, the run's own routes.json is edited after start.
folder2 = WORK / "run2"
run(["start", "--run", str(folder2)])
(folder2 / "routes.json").write_text(json.dumps(custom))
HITS.clear()
code, out, err, net = run(["read", "https://youtu.be/dQw4w9WgXcQ", "--run", str(folder2), "--max-wait", "60"])
s = summary(err)
print("edited routes.json: read exit", code, s.get("bucket"), s.get("rung"), s.get("reasons"))
print("mirror hits:", HITS)
server.shutdown()
