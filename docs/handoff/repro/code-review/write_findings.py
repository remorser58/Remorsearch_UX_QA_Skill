import json
from pathlib import Path

POC = "scratchpad/r2code/"
U = "skills/remorsearch-ux-qa/uxresearch/"
findings = [
 {"id": "C-01", "severity": "blocker", "file": U + "ladder.py", "line": 947,
  "problem": "Official-only mode takes the official route from the run's own route table. _terms_stop resolves the packaged "
             "entry's official_route id ('youtube') with st.routes.match(st.url), and Routes.platforms come only from the table "
             "given to `start --routes`. A custom table that redefines the 'youtube' platform with any feed, oEmbed or api route "
             "turns the confirmed, never-lifted youtube-terms stop into an R0 read through whatever host that route names (a "
             "mirror or a scraper API), labelled 'route:youtube' and 'official_only'. This contradicts D1 (confirmed is never "
             "lifted), S1 (no alternate hosts or mirrors) and the docs' claim that another table 'can add entries, never "
             "remove them'. test_the_packaged_scope_lists_apply_with_any_route_table never exercises platforms or routes.",
  "evidence": POC + "poc_routes_weaken.py: copy data/routes.json, set platforms[id=youtube].official = [{\"kind\": \"feed\", "
              "\"url\": \"http://mirror.test:PORT/feed?v={video}\", \"scope\": \"all\"}], `start --routes` it, then `read "
              "https://www.youtube.com/shorts/dQw4w9WgXcQ` -> exit 0, bucket read, rung R0, reasons ['official:feed', "
              "'route:youtube', 'official_only'], terms {status: confirmed, lifted: false, not_lifted_because: "
              "confirmed_never_lifted, mode: official_only}; mirror.test served ['/robots.txt', '/feed?v=dQw4w9WgXcQ'] and "
              "the printed text holds the mirror's sentinel.",
  "fix": "Resolve a terms entry's official_route only against the packaged table's platforms (scope.packaged()), or refuse "
         "official-only mode when the run's platform or route differs from the packaged one (for example compare the hosts "
         "their url templates name). Add a test: a --routes table that redefines the youtube platform still ends "
         "terms_restricted with no request."},
 {"id": "C-02", "severity": "major", "file": U + "scope.py", "line": 183,
  "problem": "A host covered by several terms_restricted entries is judged by the first entry only, and a check lifts whatever "
             "entry comes first for the URL's host. cafe.naver.com is covered by naver-cafe-bulk-notice (the Cafe "
             "bulk-collection notice D1 names for mom cafes) and by naver-terms. One check for 'naver.com' (the general "
             "terms) lifts the Cafe notice too, while `start` says only 'lifts naver-terms'; a check for 'cafe.naver.com' "
             "lifts the host although naver-terms, which also covers it, was never checked. The close summary counts "
             "urls_under_lift by the check's entry, so cafe reads under a naver.com check are not counted.",
  "evidence": POC + "poc_overlap.py: terms_checked=[{host: 'naver.com', result: 'permits_this_reading', ...}] -> "
              "describe_checks: [('naver-terms', 'lifts naver-terms (reported) for this run; ...')]; scope.evaluate("
              "'https://cafe.naver.com/momcafe/123') -> lifted, entry 'naver-cafe-bulk-notice' (m.cafe.naver.com the same). "
              "With host 'cafe.naver.com' only, cafe URLs are lifted although the entries covering cafe.naver.com are "
              "['naver-cafe-bulk-notice', 'naver-terms']. ledger.summary: row['urls_under_lift'] = lifted.get(row['entry']) "
              "keys on 'naver-terms' while the cafe outcomes carry 'naver-cafe-bulk-notice'.",
  "fix": "Evaluate every entry that covers the host: stop if any is confirmed or not lifted. Let a check lift an entry only "
         "when its host is the entry's host or a subdomain of it (a parent-domain check never lifts a more specific notice), "
         "or make checks name the entry id. describe_checks should list every entry a check lifts, and urls_under_lift "
         "should count per lifted entry. Add a test with two overlapping entries."},
 {"id": "C-03", "severity": "major", "file": U + "ladder.py", "line": 446,
  "problem": "robots.txt fetches follow redirects to any host with no scope check. robots_decision calls net.fetch(origin + "
             "'/robots.txt', ...) without on_redirect, so net.fetch follows up to five cross-origin hops. When a site's "
             "robots.txt redirects to a terms_restricted host (for example a brand or short-link domain that redirects "
             "everything to youtube.com or facebook.com), a deny-listed host or a switched-off API endpoint, that host is "
             "requested. This breaks 'A terms_restricted host is never requested, not even for robots.txt' and 'every "
             "redirect hop goes through the same checks'. No test covers robots.txt redirects.",
  "evidence": POC + "poc_robots_redirect.py: hop.test/robots.txt 302 -> confirmed.test/robots.txt (the fixture confirmed "
              "terms host); hop2.test -> denied.test (start --deny-host denied.test); redir.test -> "
              "disabled-api.test/v1/search/robots.txt (a never_call endpoint). `read` of /p on each exits 0, and the fixture "
              "server logged confirmed.test ['/robots.txt'], denied.test ['/robots.txt'], disabled-api.test "
              "['/v1/search/robots.txt']; the ledger's robots entries show the cross-host redirects.",
  "fix": "Pass an on_redirect callback to the robots fetch that refuses any hop for which scope_stop() returns a stop, then "
         "treat the file as unreachable (disallow and defer) or stop the URL with the hop's scope reasons. Add a test for "
         "each scope kind."},
 {"id": "C-04", "severity": "major", "file": U + "privacy.py", "line": 193,
  "problem": "author-key's refusal of logged-out posters (critique 16) never fires on the handles the agent actually has. "
             "read and ingest scrub page text first (D9), so 'ㅇㅇ(118.235)' reaches the agent as 'ㅇㅇ([ip])'. _TRAILING_IP "
             "matches digits only, so the scrubbed handle is keyed: every logged-out 'ㅇㅇ' poster gets the same author key "
             "(distinct people merged into one 'author'), and typed nicknames of logged-out posters become identities. "
             "Partial IPv6 groups such as '(2001:2d8)', the form DC Inside shows for posters on IPv6 mobile networks, are "
             "neither scrubbed nor refused. The AuthorKeyTests use raw forms only, so they pass without covering this path.",
  "evidence": POC + "poc_scrubbed_handle.py: a post with '닉네임(118.235)' is printed as '닉네임([ip])'; `author-key --handle "
              "'닉네임(118.235)'` exits 2, but `author-key --handle '닉네임([ip])'` exits 0 with a key. "
              "privacy.author_key(salt, 'dcinside', privacy.scrub(h)[0]) for h in 'ㅇㅇ(118.235)', 'ㅇㅇ(211.36)', 'ㅇㅇ(39.7)' "
              "-> the same key c1c9d321f090f7d4 for all three. author_key(salt, 'dcinside', 'ㅇㅇ(2001:2d8)') -> keyed, and "
              "scrub('ㅇㅇ(2001:2d8)') leaves it unchanged (" + POC + "handle_probe.py, scrub_probe.py).",
  "fix": "Make normalize_handle/check_handle recognise the scrubber's placeholders ('([ip])', '[ip]') and partial IPv6 "
         "groups (for example r'\\(\\s*[0-9A-Fa-f]{1,4}(?::[0-9A-Fa-f]{0,4}){1,3}\\s*\\)$'), add the IPv6 form to the "
         "partial_ip scrub pattern, and test with the handle exactly as `read` prints it."},
 {"id": "C-05", "severity": "major", "file": U + "youtube.py", "line": 535,
  "problem": "For YouTube, lead and tail positions are measured over the description followed by the whole comment listing "
             "(page.main_text = description + listing). The last ~200 characters are therefore the last comment(s), not "
             "the uploader's text. A viewer's '이거 그냥 광고입니다' is reported as the video's promotion_placed disclosure at "
             "'tail', while the uploader's '이 영상은 협찬입니다' at the end of the description falls into 'body' and, being a "
             "placed marker, is dropped. Critique 7's end-of-post rule is inverted for every video with comments (false "
             "disclosure plus a missed one). HTML pages whose main element also holds comments are likely affected the same way.",
  "evidence": POC + "poc_yt_tail.py (fake Data API on 127.0.0.1): description = 10 sentences + '이 영상은 협찬입니다'; "
              "comments ['버튼이 늦게 반응해서 불편했어요. ' x6, '이거 그냥 광고입니다'] -> promotion_hits == [{'marker': "
              "'광고입니다', 'family': 'promotion_placed', 'position': 'tail'}]; the uploader's '협찬입니다' is absent.",
  "fix": "Scan the title and description as the post (lead and tail on the description only) and scan comments separately "
         "(per comment, never as the video's tail), or give promotion_scan only the description as main text. Add a test "
         "with a disclosure at the end of a description and a complaint in the last comment."},
 {"id": "C-06", "severity": "minor", "file": U + "scope.py", "line": 75,
  "problem": "search_pages, never_call and out_of_scope path prefixes are compared on the raw path. Percent-encoded unreserved "
             "characters, dot segments, empty segments and ';' parameters pass the check, and a server that normalises the "
             "path then serves the search page or the switched-off endpoint (a request D4 says is never made). For "
             "'/./search', '/a/../search' and '//search', robots.txt matching does not normalise either, so Google's "
             "'Disallow: /search' does not catch them.",
  "evidence": POC + "scope_probe.py: scope.evaluate returns no stop for 'https://www.google.com/%73earch?q=x', "
              "'/./search?q=x', '/a/../search?q=x', '//search?q=x', '/search;x?q=x', "
              "'https://dapi.kakao.com/v2/%73earch/web?query=x' (kakao-daum-search) and "
              "'https://www.googleapis.com/youtube/v3/%73earch?part=snippet&q=x' (youtube-data-api-search). robots.decide "
              "with 'Disallow: /search' allows '/./search', '/a/../search' and '//search'.",
  "fix": "Normalise the path before prefix matching (decode %XX of unreserved characters, remove dot segments per RFC 3986 "
         "5.2.4, collapse empty segments, cut ';' parameters), or refuse URLs whose path is not already normal; apply the "
         "same normalisation in robots.target_of."},
 {"id": "C-07", "severity": "minor", "file": U + "data/markers.json", "line": 214,
  "problem": "The negation guard misses common negated disclaimers, so the stems critique 7 flagged still fire on 'not "
             "sponsored' texts: '-은 적 없는', '-은 것이 아닌/아니라', '#협찬 없이', '-다는 오해', '참여는 안 했지만'. "
             "KoreanMarkerTests.test_labelled_cases_keep_full_precision asserts precision 1.0, but only because the "
             "fixture has none of these forms.",
  "evidence": POC + "markers_probe.py, verdict.content_flags: '경제적 대가를 받은 적 없는 솔직 후기입니다.' -> "
              "[('경제적 대가를 받', 'promotion', 'lead')]; '경제적 대가를 받은 것이 아닌 내돈내산 후기' -> the same; "
              "'업체로부터 제품을 제공받은 것이 아니라 직접 구매했습니다.' -> [('업체로부터 제품을 제공받', ...)]; "
              "'제품을 제공받았다는 오해가 있는데 직접 샀습니다.' -> [('제품을 제공받았', ...)]; '#협찬 없이 내돈내산' -> "
              "[('#협찬', ...)]; '리뷰 이벤트 참여는 안 했지만 맛은 좋아요' -> [('리뷰 이벤트 참여', 'seller_event')].",
  "fix": "Use complete forms for the stems ('경제적 대가를 받아', '제공받아 작성') or extend negation_after/negation_clause "
         "(for example '은 적 없', '은 (것|게|거)[이가]? 아니', '없이', '는 안 '), and add these as fixture negatives."},
 {"id": "C-08", "severity": "minor", "file": U + "verdict.py", "line": 110,
  "problem": "Neither the marker matcher nor the scrubber (privacy.py _PATTERNS) folds width or dash variants. Full-width "
             "disclosure labels are missed, and full-width or dash-variant identifiers pass the D9 scrub, although "
             "normalize_handle already applies NFKC to handles.",
  "evidence": POC + "markers_probe.py / scrub_probe.py: content_flags('＃광고 제품 리뷰') == [], '［광고］ 충전기 후기' -> [], "
              "'（협찬） 충전기 후기' -> [], '#ＡＤ new charger' -> []. scrub leaves unchanged: '주민 ９００１０１-１２３４５６７', "
              "'메일 kim＠naver.com', 'ㅇㅇ（118.235）', '연락 010–1234–5678' (en dash), '연락 010ㅡ1234ㅡ5678', "
              "'신한 110222333444'.",
  "fix": "Match and scrub on an NFKC-folded copy (keeping an offset map, or scrub the folded text), and accept – — ― ㅡ as "
         "phone and account separators."},
 {"id": "C-09", "severity": "minor", "file": U + "privacy.py", "line": 83,
  "problem": "The partial_ip pattern matches any parenthesised decimal, so star ratings and version numbers in reviews are "
             "replaced by '([ip])', losing data the research needs and inflating scrubbed.partial_ip.",
  "evidence": POC + "scrub_probe.py: scrub('평점 (4.5)') -> '평점 ([ip])'; '별점(4.8) 만점' -> '별점([ip]) 만점'; "
              "'버전 (3.2) 업데이트' -> '버전 ([ip]) 업데이트'; '(1.5)배속' -> '([ip])배속'.",
  "fix": "Scrub the group only when it follows a handle-like token (for example r'[^\\s()]{1,20}\\s?\\(\\d{1,3}\\.\\d{1,3}\\)'), "
         "or require two-or-three-digit octets, and add ratings to the kept cases in the tests."},
 {"id": "C-10", "severity": "minor", "file": U + "scope.py", "line": 191,
  "problem": "Conflicting checks for one host are accepted and the first one wins: a brief that lists permits_this_reading "
             "and restricts_this_reading for dcinside.com lifts the entry, and `start` prints both 'lifts dcinside-terms' and "
             "'does not lift dcinside-terms'.",
  "evidence": "validate_checks accepts [{host: 'dcinside.com', result: 'permits_this_reading'}, {host: 'dcinside.com', "
              "result: 'restricts_this_reading'}] (same terms_url and date); scope.evaluate("
              "'https://gall.dcinside.com/board/view/?id=x&no=1') -> lifted; describe_checks -> ['lifts dcinside-terms "
              "(reported) ...', 'does not lift dcinside-terms: the result is restricts_this_reading'].",
  "fix": "Refuse duplicate hosts in validate_checks, or let any covering check whose result is not permits_this_reading "
         "block the lift."},
 {"id": "C-11", "severity": "minor", "file": U + "ledger.py", "line": 304,
  "problem": "deny_hosts entries are only stripped and lower-cased: a trailing dot, a scheme or a trailing slash passes "
             "validate_brief and silently denies nothing (pre-existing, but the deny list is the first scope list and trailing "
             "dots are in the review scope; terms_checked and signed_in_communities hosts are normalised and validated).",
  "evidence": "Briefs with deny_hosts ['example.com.'], ['https://example.com'] or ['example.com/'] validate, and "
              "scope.evaluate('https://www.example.com/p', build_policy(brief, {}), lists) returns no stop for each.",
  "fix": "rstrip('.') and validate deny hosts with the same host-name pattern terms_checked uses (refuse schemes and "
         "paths), for the brief and for --deny-host."},
 {"id": "C-12", "severity": "minor", "file": U + "ladder.py", "line": 1222,
  "problem": "Refused ingest outcomes carry no url_key, so Run.summary (keyed by url_key or url) counts them as another URL. "
             "The new terms flow (read stops, the agent tries ingest, it is refused) shows one URL as two in the close totals "
             "and host rows.",
  "evidence": POC + "poc_totals.py: read reported.test/p (exit 3), ingest twice (exit 2), close -> totals {'urls': 2, "
              "'terms_restricted': 1, 'refused': 1, ...}; host row urls 2.",
  "fix": "Log url_key in _ingest_refused (and _refused) and count a refusal of a URL that already has an outcome without "
         "adding to urls."},
 {"id": "C-13", "severity": "minor", "file": U + "ladder.py", "line": 1190,
  "problem": "The robots command exits 4 when robots.txt cannot be fetched because of a DNS or TLS failure; "
             "public-page-access.md section 9 (rewritten in this change) documents 0, 2, 3 and 5 only.",
  "evidence": POC + "poc_robots_exit.py: `robots http://m.lonely.test/x` -> exit 4 {'error': 'dns_error', 'allowed': false}.",
  "fix": "Document exit 4 for `robots`, or map these failures to 5 (deferred)."},
 {"id": "C-14", "severity": "minor", "file": U + "verdict.py", "line": 391,
  "problem": "A signed-in capture's greeting line is copied verbatim into reasons ('line:<text>'), which ingest prints and "
             "the ledger keeps after close. It is never scrubbed, so a login ID or e-mail in the greeting reaches the agent, "
             "against D9 (pre-existing code, new promise).",
  "evidence": "verdict.classify(capture=True) on '<div>kim1234@naver.com님 환영합니다</div><main>...</main>' -> reasons "
              "['capture:signed_in_view', 'line:kim1234@naver.com님 환영합니다'].",
  "fix": "Record only the marker ('line:greeting') or scrub the value before it becomes a reason."},
 {"id": "C-15", "severity": "minor", "file": U + "ladder.py", "line": 595,
  "problem": "_log_attempt hashes and counts the unscrubbed page text, while the outcome and the saved page use the scrubbed "
             "text. The ledger keeps, after close, a hash of text that still held identifiers, and the request hash matches "
             "nothing the run keeps (D9: hashes and checks refer to the scrubbed text).",
  "evidence": POC + "poc_hash.py (fixture pii-post.html): request entry sha256 8cbbc5a6..., text_chars 396; outcome sha256 "
              "c2d93ec6..., text_chars 351, equal to the saved page; after close the request hash is still in the ledger.",
  "fix": "Hash the scrubbed text in _log_attempt, or drop content_sha256 from request entries."},
 {"id": "C-16", "severity": "minor", "file": U + "data/routes.json", "line": 234,
  "problem": "youtube-nocookie.com is in the youtube-terms entry, whose official_route is 'youtube', but the youtube "
             "platform's hosts lack it, so embed URLs on that host always stop with official_route_does_not_fit, even with "
             "a key (a safe but needless coverage gap; embed/ paths already parse).",
  "evidence": "ladder.Routes(scope.packaged()).match(net.parse_url('https://www.youtube-nocookie.com/embed/Vid0000001A')) -> "
              "(None, {}); the same for youtube-nocookie.com without www.",
  "fix": "Add youtube-nocookie.com to the youtube platform's hosts."},
 {"id": "C-17", "severity": "minor", "file": U + "verdict.py", "line": 452,
  "problem": "_scan calls _dropped for every match before the per-family limit applies, and _quoted/_question scan to the "
             "sentence ends, so content_flags (run on every read and ingest) is quadratic on long text without sentence "
             "ends. A hostile page can stall `read` for minutes.",
  "evidence": "verdict.content_flags('#광고 ' * n + '맞나요?'): 40K chars 0.54 s, 80K 1.73 s, 160K 6.75 s (x4 per "
              "doubling); about 40 s per marker family at the 400 KB text cap.",
  "fix": "Bound the sentence window (for example 300 characters either side of the match), cap the candidates examined per "
         "family, or compute sentence boundaries once per text."},
]

summary = (
 "1 blocker, 4 major, 12 minor. Blocker: a `start --routes` table can redefine the youtube platform, and official-only mode "
 "then reads YouTube content through any host it names, although youtube-terms is confirmed and never lifted (C-01). "
 "Major: a naver.com terms check also lifts the Naver Cafe bulk-collection entry, because only the first covering entry "
 "counts (C-02); robots.txt fetches follow cross-host redirects to terms-restricted, deny-listed and switched-off hosts "
 "(C-03); author-key accepts the scrubbed partial-IP handle the agent actually sees, merging logged-out posters into one "
 "key, and IPv6 fragments are neither scrubbed nor refused (C-04); YouTube tail positions come from the last comment, not "
 "the uploader's description (C-05). Verified sound: host matching (case, trailing dots, ports, userinfo refused, "
 "IDN/full-width hosts through parse_url's IDNA); redirect hops, R0 routes and R2 alternates are scope-checked in "
 "_request; only reported entries lift, only permits_this_reading, terms_url and dates validated; the lifted budget of 10 "
 "holds across two concurrent processes (10 reads and 2 budget stops, " + POC + "concurrency.py); robots AI-agent groups "
 "(an own-token group decides alone, agent rules add disallows only, per-token evaluation is never looser than a merged "
 "group, the format bump refetches, training groups are recorded only); the YouTube key is masked in every recorded URL, "
 "trail and ledger entry and never printed; video-ID parsing, page caps, quota counting, error mapping, retention_until "
 "and quota holds behave as documented; route_adapter imports only uxresearch submodules and needs ADAPTER_API plus "
 "read_route. Full suite: 601 tests OK; no stray files in the repository after the runs (the empty .ux-loop comes from "
 "the loop tests). Several tests pass without covering the failing path: marker precision 1.0 (C-07), author-key raw "
 "forms only (C-04), the packaged-lists test never touches platforms (C-01), and no test covers robots.txt redirects (C-03).")

out = Path("/tmp/claude-0/-home-user-ux-research-qa-skills/e780fd74-671a-5856-a21d-1181ebfa73fb/scratchpad/review/r2-code.json")
out.write_text(json.dumps({"findings": findings, "summary": summary}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
data = json.loads(out.read_text(encoding="utf-8"))
from collections import Counter
print(Counter(f["severity"] for f in data["findings"]), len(data["findings"]))
