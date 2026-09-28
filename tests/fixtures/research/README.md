# Research reader fixtures

Authored test inputs for `tests/test_ux_read.py`. Nothing here was captured from
a real site; every page is invented, and every host name uses the reserved
`.test` name, so no fixture can be mistaken for real community evidence.

The tests serve these files from a threaded `http.server` bound to 127.0.0.1.
`REMORSEARCH_ALLOW_PRIVATE=1` and `REMORSEARCH_TEST_RESOLVE` map the `.test` names
to that address for the reader; test names never reach real DNS or a proxy.

| Path | What it exercises |
| --- | --- |
| `pages/post-normal.html` | an ordinary community post (read) |
| `pages/post-header-login.html` | a login box in the header and a full post below (read, not auth_gate) |
| `pages/post-captcha-discussion.html` | a post that talks about captchas without a widget (read, not human_check) |
| `pages/login-wall.html`, `age-gate.html`, `member-only.html` | password form plus login word on thin content; age and membership walls (auth_gate) |
| `pages/paywall-jsonld.html` | JSON-LD `isAccessibleForFree: false` (paywall, metadata only) |
| `pages/deleted-post.html` | a removed post served with status 200 (gone) |
| `pages/noai-meta.html`, `tdm-meta.html` | robots `noai` and `tdm-reservation` meta tags (opted_out) |
| `pages/captcha-recaptcha.html`, `captcha-turnstile.html`, `captcha-ko.html` | interactive human checks, including a Korean 보안문자 form (human_check, host stop) |
| `pages/js-check.html` | a self-clearing interstitial (js_check, escalates) |
| `pages/js-shell-*.html`, `mobile-post.html` | JS shells with a same-site alternate, an other-site alternate, or none; the mobile twin |
| `pages/jsonld-shell.html` | a JS shell whose JSON-LD review body is longer than the visible text |
| `pages/blocked-403.html` | a plain block page (bot_filter) |
| `pages/euckr-page.utf8.html` | stored as UTF-8; the tests serve it as CP949 under EUC-KR, ks_c_5601-1987 and x-windows-949 labels |
| `pages/injection-post.html` | injection phrases (en and ko) and a forged envelope END line |
| `pages/feed.xml` | an RSS feed for the R0 route-table test |
| `captures/` | render captures for `ingest`: HTML, text, a ux-page-read.v1 document, and a signed-in view that must be refused |
| `robots/*.txt` | RFC 9309 precedence, product-token groups, wildcards, percent-encoding, Crawl-delay |
| `routes.test.json` | a route table with `.test` hosts only |
| `brief.json` | a ux-research-brief.v1 example |

The 10 MB page and the gzip bomb are generated inside the tests instead of being
stored here.
