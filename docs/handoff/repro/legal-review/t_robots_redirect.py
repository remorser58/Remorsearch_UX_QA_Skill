"""Does the robots.txt fetch follow a redirect into a terms_restricted host (or a denied host)?
And what does `robots` say when robots.txt is answered by a challenge page?
Loopback only: *.test names map to 127.0.0.1; any other lookup is refused and logged by the harness."""
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

CHALLENGE = (b"<!doctype html><html><head><title>Just a moment...</title></head><body>"
             b"<div id='challenge-running'>Checking your browser before accessing the site.</div>"
             b"<noscript>Please enable JavaScript and cookies to continue</noscript></body></html>")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        HITS.append((host, self.path))
        if host == "short.test" and self.path == "/robots.txt":
            self.send_response(302)
            self.send_header("Location", "https://www.youtube.com/robots.txt")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if host == "denyhop.test" and self.path == "/robots.txt":
            self.send_response(301)
            self.send_header("Location", "http://denied.test:%d/robots.txt" % self.server.server_address[1])
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if host == "guarded.test" and self.path == "/robots.txt":
            body = CHALLENGE
            self.send_response(403)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = b"User-agent: *\nAllow: /\n" if self.path == "/robots.txt" else b"<html><body><main>" + b"x " * 400 + b"</main></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain" if self.path == "/robots.txt" else "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
PORT = server.server_address[1]
os.environ["REMORSEARCH_TEST_RESOLVE"] = "short.test=127.0.0.1,denyhop.test=127.0.0.1,denied.test=127.0.0.1,guarded.test=127.0.0.1"

sys.path.insert(0, str(Path(__file__).parent))
from harness import run, summary, NET_LOG  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="r1-robots-", dir=str(Path(__file__).parent)))
folder = WORK / "run"
code, out, err, net = run(["start", "--run", str(folder), "--deny-host", "denied.test"])
print("start", code)

code, out, err, net = run(["read", f"http://short.test:{PORT}/post/1", "--run", str(folder), "--max-wait", "60"])
s = summary(err) or {}
print("read short.test ->", code, s.get("bucket"), s.get("stop_class"), (s.get("reasons") or [])[:3], s.get("error"))
print("  network events during read:", net)

code, out, err, net = run(["robots", f"http://denyhop.test:{PORT}/page", "--run", str(folder), "--max-wait", "60"])
print("robots denyhop.test ->", code, out.strip()[:300].replace("\n", " "))
print("  server hits so far:", HITS)

code, out, err, net = run(["robots", f"http://guarded.test:{PORT}/page", "--run", str(folder), "--max-wait", "60"])
value = json.loads(out)
print("robots guarded.test (challenge page served for robots.txt) ->", code,
      {k: value.get(k) for k in ("allowed", "robots_status", "decision", "stop_class", "http_status")})
server.shutdown()
