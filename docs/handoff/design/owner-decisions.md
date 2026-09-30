# Owner decisions for the Korean pack (K1 + K2), 2026-09-29

Inputs, in this folder: `design.json` (file-level outlines), `critique.json` (26
corrections, all mandatory), `research.json` (sources). Where the design and this
file disagree, this file wins. K0 (removal of the R4 insane-search rung) is DONE in
commit 1f910d8; do not redo it. The repository is at HEAD 628764b on branch
claude/admiring-goldberg-llu3f5 and already contains the swarm session's
`drivers/web/read_page.mjs` (R3 page reader).

The owner is SeongJu Kim (remorser58). His standing instruction: "DC Inside, mom
cafes (Naver Cafe), Danggeun, YouTube and the like must never give anyone a reason
to sue." Every decision below follows from that.

## Decisions

D1. terms_restricted. Route-table entries with status `reported` or `confirmed`.
    - Both stop by default, before any request, and on every redirect hop (short
      links such as youtu.be or naver.me that land on a restricted host stop too).
    - `reported` is lifted only by a brief `terms_checked` item for that host whose
      `result` says the terms permit this reading. Each item requires `host`,
      `terms_url` (with the clause identifier when there is one), `checked_on`,
      `result`, and may carry `note`. `confirmed` is never lifted.
    - YouTube pages and Meta platforms (Instagram, Threads on threads.com and
      threads.net, Facebook): try to read the primary terms (YouTube Terms of
      Service; Meta Automated Data Collection Terms) with WebFetch or WebSearch. If
      you can read the clause that bars automated collection without written
      permission, mark the entry `confirmed` with the URL, the clause and the date.
      If you cannot reach the primary text, mark it `reported` and list it as an
      open item. Either way the default is a stop.
    - DC Inside and Naver Cafe (including mom cafes): `reported` (the 2026-08-31
      Naver Cafe notice on bulk collection; DC Inside terms per design).
    - Danggeun: follow the design's row; if its web pages are public and no terms
      restriction is known, it is at least `unchecked` in the platform map, and the
      reader's normal stops apply. Do not invent a restriction and do not omit one
      the research found.
    - `ingest` refuses any URL on a terms_restricted host unless a reported entry
      was lifted. Official-only mode never admits captures.
    - After a lift, that host's page budget is 10 documents per run (not 30).
D2. robots.txt groups for AI agents that fetch pages on a user's behalf are honoured
    as if they named our own token, following the critique: the group that names
    RemorsearchUXQA decides alone; AI-agent rules apply only when the base decision
    came from `*`. Training or search-crawler groups are a recorded signal, not a
    stop. Token lists live in `uxresearch/data/agent-tokens.json`; tests use fixture
    tokens; verify token names against each operator's documentation where you can
    and mark the rest unverified.
D3. Researcher notes are OUT of this change: no `note` command, no doc text that
    offers them, no `researcher_note` route values in data files. (The critique
    found they could bring in member-only content.)
D4. The Naver Search API, NAVER API HUB, DataLab and the Kakao Daum Search API stay
    OFF: list them with `enabled: false` and the reason "off until the owner reads
    the current terms".
D5. Language: the Korean pack is written in Korean throughout:
    `references/research/korea/*.md`, `references/persona-qa/kwcag-2.2.md` and
    `README.ko.md`. English files stay English. JSON keys stay English; values may
    be Korean where natural (`name_ko`, notes).
D6. Keys come only from environment variables named `REMORSEARCH_*`. The YouTube key
    is `REMORSEARCH_YOUTUBE_API_KEY`; `YOUTUBE_API_KEY` is accepted as an alias. No
    secrets file.
D7. Incentivised reviews: an incentive flag caps satisfaction, preference, counter-
    search use and star averages at D. Complaints and workarounds inside
    incentivised reviews keep their voice grade minus at most one step (at least
    C). A seller or board notice is a per-review candidate for the verifier, not an
    automatic page-wide cap. Platform-wide review points are distinguished from
    seller-run review events.
D8. Reviews of a platform's own-brand items need corroboration from another channel
    family.
D9. Identifiers are scrubbed before the model sees page text: whatever `read` and
    `ingest` print or write for the agent to read has phone numbers, e-mail
    addresses, resident registration numbers, card and account numbers and partial
    IPs removed. Note in the docs that the planned merge verbatim check compares
    against the scrubbed text.
D10. 저작권법 제37조 (attribution) versus handle stripping, and 제94조② (for-profit
    use): mark as "needs counsel"; default to paraphrase and short quotes.
D11. The brief may carry an optional `ethics_review` object (status: none | exempt |
    approved | pending; optional body and reference). It is recorded, never
    enforced.
D12. The YouTube Data API adapter IS in scope (it is the only route to YouTube
    comments): R0 official route with the user's key; videos.list and
    commentThreads.list; injectable base URL for tests; quota counting; author
    names become salted author keys; no channel IDs stored; `retention_until` =
    fetch time + 30 days on every API-sourced item; no profiling by protected
    attributes (age, race, religion, political leaning, sexual orientation, health)
    against an author key.
D13. Deferred, not in this change: VOC scrub command, merge/gate/export, Codex
    openai.yaml Korean text, Claude Code when_to_use, plugin manifest.

## Absolute safety rules

S1. No evasion anywhere, in code, data or docs. Never describe or implement a way
    around a login, member wall, paywall, human check, rate limit, robots.txt,
    terms restriction or bot protection. Never suggest alternate hosts, mirrors,
    caches, archives, apps or tricks to get content a stop withheld. A stop is the
    answer; it becomes a coverage gap in the report. The platform map lists only
    legitimate routes (official APIs with the user's key, official feeds, the
    team's own exports, public pages read by the reader) and the stops to expect.
S2. Never name member-only or closed communities as audience leads (for example
    여성시대). Member-only content goes only through `signed_in_communities`, as
    summaries.
S3. A community's modelled gender, age or political lean is never attributed to a
    poster, a claim or a persona. Describe content norms at corpus level, evenly.
S4. Legal text is not legal advice (법률 자문 아님). Cite the article and its version
    or promulgation date; mark anything not checked on law.go.kr or the primary
    source as 미확인; mark contested applications as "counsel decides".
S5. Ideas only from K-skill, insane-search and insane-research: never copy their
    text, code, tables or lists. Credit them in THIRD_PARTY_NOTICES.md.
S6. Quotes stay short (at most 300 characters, paraphrase preferred); posters are
    never named; author handles become salted keys.

## Korean writing conventions (for the Korean files)

- 합니다체 in prose, 개조식 (~함, ~임) in tables and evidence lines. Short, plain
  sentences. No translationese (avoid ~에 의해, ~를 가지다, 그것은, needless 것이다).
- One term per concept: 사용자 (not 유저 or 이용자, except inside a quoted statistic).
- Fixed labels 관찰됨 / 추론 / 미확인. Claim statuses keep their English codes with a
  Korean gloss.
- ISO dates in tables; times as KST YYYY-MM-DD HH:mm.
- File and skill names stay ASCII kebab-case.

## File ownership

Do not touch: `references/ergonomics/`, `ergoqa/`, `drivers/`,
`docs/ergonomic-swarm-spec.md`, `docs/validation/experiments/`, `benchmarks/`,
`tests/test_ergo_*`, `COORDINATION.md` (the orchestrator writes it).

## House rules

- Python 3.10+, standard library only. Tests never touch the network: serve
  fixtures from a local http.server on 127.0.0.1 and use injectable clocks.
- Tests live in `tests/` and `import _paths` first.
- Never change the first line (`<!-- Mode: ... -->`) of `references/*/workflow.md`.
- Paths inside skill docs are relative to the skill folder. Inside
  `references/<mode>/`, a bare `references/x.md` means `references/<mode>/x.md`;
  files in `references/research/korea/` always write full skill-relative paths
  (`references/research/korea/promotion.md`, `references/research/source-grading.md`).
- Do not run git commit, add, checkout, reset or stash. Leave changes in the working
  tree.
- Full check: `cd /home/user/ux-research-qa-skills && python3 -m unittest discover -s
  tests -p 'test_*.py'` and `python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py`.
