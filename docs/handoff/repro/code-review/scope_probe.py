import sys
sys.path.insert(0, "/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
from uxresearch import scope, net
lists = scope.lists_for(scope.packaged())
policy = {"deny_hosts": [], "terms_checked": []}
urls = [
 "https://WWW.YOUTUBE.COM/watch?v=dQw4w9WgXcQ",
 "https://www.youtube.com./watch?v=dQw4w9WgXcQ",
 "https://www.youtube.com:443/watch?v=dQw4w9WgXcQ",
 "https://www.youtube.com:8443/watch?v=dQw4w9WgXcQ",
 "https://ｗｗｗ．ｙｏｕｔｕｂｅ．ｃｏｍ/watch?v=dQw4w9WgXcQ",
 "https://www.youtube。com/watch?v=dQw4w9WgXcQ",
 "https://xn--www-youtube.com/",
 "https://www.google.com/%73earch?q=x",
 "https://www.google.com/./search?q=x",
 "https://www.google.com/a/../search?q=x",
 "https://www.google.com//search?q=x",
 "https://www.google.com/search;x?q=x",
 "https://www.google.com/Search?q=x",
 "https://www.google.com/searchx?q=x",
 "https://www.google.com/search/?q=x",
 "https://www.google.com/search",
 "https://www.google.com/webhp?q=x",
 "https://www.google.com/?q=x",
 "https://duckduckgo.com/?Q=x",
 "https://duckduckgo.com/?q",
 "https://duckduckgo.com/html/?q=x",
 "https://html.duckduckgo.com/html?q=x",
 "https://duckduckgo.com/?%71=x",
 "https://openapi.naver.com/v1/%73earch/blog.json?query=x",
 "https://dapi.kakao.com/v2/%73earch/web?query=x",
 "https://dapi.kakao.com/V2/search/web?query=x",
 "https://dapi.kakao.com/v2/search/../search/web?query=x",
 "https://www.googleapis.com/youtube/v3/%73earch?part=snippet&q=x",
 "https://www.googleapis.com/youtube/v3/search?part=snippet&q=x",
 "https://www.facebook.com/%67roups/123",
 "https://discord.com./channels/1",
 "http://[::ffff:1.2.3.4]/",
]
for u in urls:
    try:
        p = net.parse_url(u)
    except net.NetError as e:
        print(f"{u!r:70} parse_url -> NetError {e.kind}")
        continue
    stop, lift = scope.evaluate(p, policy, lists)
    print(f"{u!r:70} -> {p!r:60} {stop.kind if stop else None} {stop.reasons[:2] if stop else ''}")
