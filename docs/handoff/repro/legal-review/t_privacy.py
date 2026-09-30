"""Author-key refusals, and what a capture's signed-in greeting line leaves in outputs and the ledger.
Loopback only (a local server for the anonymous pre-read)."""
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.environ["REMORSEARCH_ALLOW_PRIVATE"] = "1"
os.environ["HARNESS_ALLOW_LOOPBACK"] = "1"

PAGE = ("<html><head><title>짧은 공지</title></head><body><main><p>" + "이 제품 결제 화면이 자꾸 멈춰요. " * 30 +
        "</p></main></body></html>").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"User-agent: *\nAllow: /\n" if self.path == "/robots.txt" else PAGE
        self.send_response(200)
        self.send_header("Content-Type", "text/plain" if self.path == "/robots.txt" else "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
PORT = server.server_address[1]
os.environ["REMORSEARCH_TEST_RESOLVE"] = "board.test=127.0.0.1"

sys.path.insert(0, str(Path(__file__).parent))
from harness import run, summary  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="r1-priv-", dir=str(Path(__file__).parent)))
folder = WORK / "run"
run(["start", "--run", str(folder)])

for handle in ["ㅇㅇ(118.235)", "ㅇㅇ", " ㅇㅇ ", "ㅇㅇ（118.235）", "고양이(1.2)", "고양이 (118.235)", "(118.235)고양이",
               "고양이[118.235]", "고양이 118.235", "익명", "고양이"]:
    code, out, err, net = run(["author-key", "--run", str(folder), "--platform", "community.test", "--handle-stdin"],
                              stdin_text=handle + "\n")
    print(repr(handle), "->", code, out.strip().replace("\n", " ")[:160])

url = f"http://board.test:{PORT}/post/1"
code, out, err, net = run(["read", url, "--run", str(folder), "--max-wait", "60"])
print("read:", code, (summary(err) or {}).get("bucket"))
capture = WORK / "capture.html"
capture.write_text("<html><body><header><div>김민지님 환영합니다</div><a href='/logout'>로그아웃</a></header>"
                   "<main><p>" + "결제 화면이 멈춥니다. " * 40 + "</p></main></body></html>", encoding="utf-8")
code, out, err, net = run(["ingest", "--run", str(folder), "--url", url, "--file", str(capture), "--context", "anonymous"])
s = summary(err) or {}
print("ingest:", code, s.get("bucket"), s.get("stop_class"), s.get("reasons"))
ledger = (folder / "access-ledger.jsonl").read_text(encoding="utf-8")
print("name in stderr summary:", "김민지" in err, "| name in ledger:", "김민지" in ledger)
code, out, err, net = run(["close", "--run", str(folder)])
ledger = (folder / "access-ledger.jsonl").read_text(encoding="utf-8")
print("after close, name still in ledger:", "김민지" in ledger)
server.shutdown()
