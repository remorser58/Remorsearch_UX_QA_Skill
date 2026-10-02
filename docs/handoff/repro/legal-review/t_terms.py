import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harness import run, summary, NET_LOG  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="r1-terms-", dir=str(Path(__file__).parent)))

URLS = [
    # DC Inside
    "https://gall.dcinside.com/board/view/?id=baseball_new11&no=1",
    "https://gall.dcinside.com/mgallery/board/view/?id=x&no=1",
    "https://m.dcinside.com/board/baseball_new11/1",
    "https://dcinside.com/",
    "https://search.dcinside.com/post/q/test",
    "https://GALL.DCINSIDE.COM./board/view/?id=a&no=2",
    # Naver
    "https://cafe.naver.com/imsanbu/123",
    "https://m.cafe.naver.com/ca-fe/web/cafes/123/articles/456",
    "https://section.cafe.naver.com/ca-fe/",
    "https://blog.naver.com/someone/223000000000",
    "https://m.blog.naver.com/someone/223000000000",
    "https://rss.blog.naver.com/someone.xml",
    "https://kin.naver.com/qna/detail.naver?d1id=1&docId=2",
    "https://m.place.naver.com/restaurant/123/review/visitor",
    "https://smartstore.naver.com/shop/products/1",
    "https://naver.com/",
    "https://naver.me/xAbCdE",
    "https://me2.do/xAbCdE",
    # Coupang
    "https://www.coupang.com/vp/products/123",
    "https://m.coupang.com/vm/products/123",
    "https://link.coupang.com/a/abc",
    "https://coupa.ng/abc",
    # YouTube
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/@somechannel",
    "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv",
    # Instagram / Threads / Facebook
    "https://www.instagram.com/p/abc/",
    "https://instagram.com/someone",
    "https://instagr.am/p/abc",
    "https://www.threads.com/@someone/post/abc",
    "https://threads.net/@someone",
    "https://www.threads.net/@someone/post/abc",
    "https://www.facebook.com/somepage",
    "https://m.facebook.com/story.php?story_fbid=1&id=2",
    "https://fb.com/somepage",
    "https://fb.me/abc",
    "https://fb.watch/abc",
    "https://web.facebook.com/somepage",
    "https://l.facebook.com/l.php?u=https%3A%2F%2Fexample.org",
    "https://www.facebook.com/groups/123",
]


def start(name, brief=None, extra=()):
    folder = WORK / name
    argv = ["start", "--run", str(folder)]
    if brief is not None:
        path = WORK / f"{name}-brief.json"
        path.write_text(json.dumps(brief, ensure_ascii=False))
        argv += ["--brief", str(path)]
    code, out, err, net = run(argv + list(extra))
    assert code == 0, (code, out, err)
    return folder, json.loads(out)


def check(folder, urls, label):
    capture = WORK / "capture.html"
    capture.write_text("<html><body><main><p>" + "사용자 후기 본문입니다. " * 40 + "</p></main></body></html>")
    rows = []
    for url in urls:
        code_r, out_r, err_r, net_r = run(["read", url, "--run", str(folder), "--max-wait", "0"])
        s = summary(err_r) or {}
        code_b, out_b, err_b, net_b = run(["robots", url, "--run", str(folder), "--max-wait", "0"])
        b = json.loads(out_b) if out_b.strip().startswith("{") else {}
        code_i, out_i, err_i, net_i = run(["ingest", "--run", str(folder), "--url", url, "--file", str(capture),
                                           "--context", "anonymous"])
        i = summary(err_i) or {}
        rows.append({
            "url": url,
            "read": [code_r, s.get("bucket"), s.get("stop_class"), (s.get("reasons") or [])[:4], s.get("error")],
            "read_net": net_r,
            "robots": [code_b, b.get("stop_class"), (b.get("reasons") or [])[:3], b.get("error")],
            "robots_net": net_b,
            "ingest": [code_i, i.get("bucket"), (i.get("reasons") or [""])[0][:140]],
            "ingest_net": net_i,
        })
    print(f"===== {label}")
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))


base_brief = {"schema_version": "ux-research-brief.v1", "product": {"name": "Test"}}
folder, started = start("plain", base_brief)
print("keys:", started.get("keys"))
check(folder, URLS, "no terms checks")

# A check the user wrote for Naver's general terms, and a check for YouTube (confirmed) and DC Inside.
brief2 = dict(base_brief, access_policy={"terms_checked": [
    {"host": "naver.com", "terms_url": "https://policy.naver.com/rules/service.html", "checked_on": "2026-09-29",
     "result": "permits_this_reading"},
    {"host": "youtube.com", "terms_url": "https://www.youtube.com/static?template=terms", "checked_on": "2026-09-29",
     "result": "permits_this_reading"},
]})
folder2, started2 = start("naver-lift", brief2)
print("terms_checked effects:", json.dumps(started2.get("terms_checked"), ensure_ascii=False))
# Only scope decisions; hosts that are lifted would go to the network (refused by the harness).
check(folder2, ["https://cafe.naver.com/imsanbu/123", "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://blog.naver.com/someone/223000000000"], "naver.com check lifts?")

brief3 = dict(base_brief, access_policy={"terms_checked": [
    {"host": "cafe.naver.com", "terms_url": "https://cafe.naver.com/notice", "checked_on": "2026-09-29",
     "result": "permits_this_reading"}]})
folder3, started3 = start("cafe-lift", brief3)
print("terms_checked effects:", json.dumps(started3.get("terms_checked"), ensure_ascii=False))
check(folder3, ["https://cafe.naver.com/imsanbu/123", "https://blog.naver.com/someone/223000000000"],
      "cafe.naver.com check lifts naver-terms for cafe too?")
print("TOTAL NET EVENTS:", len(NET_LOG))
