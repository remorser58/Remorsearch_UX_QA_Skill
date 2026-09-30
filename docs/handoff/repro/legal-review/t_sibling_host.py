"""Does a host-wide stop (human check, second rate-limit signal) cover the same site's other hosts?
www.site.test answers with a captcha widget page (then 429s); m.site.test serves the same post.
Loopback only."""
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.environ["REMORSEARCH_ALLOW_PRIVATE"] = "1"
os.environ["HARNESS_ALLOW_LOOPBACK"] = "1"
HITS = []
CAPTCHA = (b"<html><head><title>Security check</title></head><body><form><div class='g-recaptcha' "
           b"data-sitekey='x'></div></form><p>Please verify you are human</p></body></html>")
POST = ("<html><head><title>post</title></head><body><main><p>" + "결제 화면이 자꾸 멈춰서 불편해요. " * 30 +
        "</p></main></body></html>").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        HITS.append((host, self.path))
        if self.path == "/robots.txt":
            body, status, ctype = b"User-agent: *\nAllow: /\n", 200, "text/plain"
        elif host == "www.site.test" and self.path.startswith("/p"):
            body, status, ctype = CAPTCHA, 200, "text/html"
        elif host == "www.rl.test":
            body, status, ctype = b"slow down", 429, "text/plain"
        else:
            body, status, ctype = POST, 200, "text/html; charset=utf-8"
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
PORT = server.server_address[1]
os.environ["REMORSEARCH_TEST_RESOLVE"] = ",".join(f"{h}=127.0.0.1" for h in (
    "www.site.test", "m.site.test", "site.test", "www.rl.test", "m.rl.test"))

sys.path.insert(0, str(Path(__file__).parent))
from harness import run, summary  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="r1-sib-", dir=str(Path(__file__).parent)))
folder = WORK / "run"
run(["start", "--run", str(folder)])


def read(url):
    code, out, err, net = run(["read", url, "--run", str(folder), "--max-wait", "600"])
    s = summary(err) or {}
    return code, s.get("bucket"), s.get("stop_class"), (s.get("reasons") or [])[:3], (s.get("host_stop") or {}).get("class")


print("www p1:", read(f"http://www.site.test:{PORT}/p1"))
print("www p2:", read(f"http://www.site.test:{PORT}/p2"))
print("m   p2:", read(f"http://m.site.test:{PORT}/p2"))
print("apex p2:", read(f"http://site.test:{PORT}/p2"))
print("rate-limited www:", read(f"http://www.rl.test:{PORT}/a"))
print("rate-limited www again:", read(f"http://www.rl.test:{PORT}/b"))
print("rate-limited www third:", read(f"http://www.rl.test:{PORT}/c"))
print("m. of the rate-limited site:", read(f"http://m.rl.test:{PORT}/b"))
server.shutdown()
