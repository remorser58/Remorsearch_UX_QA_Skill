# Remorsearch UX QA

English | [한국어](README.ko.md) | [PRD · 제품 요구사항](PRD.md)

Remorsearch (*ree-mor-search*, 리모서치) UX QA helps developers improve the UX of
an existing product in Claude Code or Codex. Provide a URL or repository and ask
for improvement. The host agent inspects the product and relevant developer
decisions, discovers questions through baseline QA, researches related user
experiences, applies scoped reversible fixes and replays the affected tasks.
A prepared problem list, persona set or research brief is optional.

## What it does

Four components support that workflow; you do not need to select modes or pass
artifacts between them. A research-only or review-only request keeps its scope.

| Component | What it does | Needs |
| --- | --- | --- |
| **research** | Finds task-specific experiences, workarounds and counterexamples in communities, comments, reviews and official sources; preserves source context and gaps. | A permitted source route. YouTube comments use your own YouTube Data API key (`REMORSEARCH_YOUTUBE_API_KEY`). |
| **persona-qa** | Exercises completion, input preservation, errors/recovery, keyboard and accessibility on the real product with synthetic test conditions. | An accessible product and safe fixtures; the bundled web driver needs Node.js 22 and Playwright. |
| **ergonomics** *(experimental)* | Screens reach, touch, perception, timing and layout with simulated profiles. | Relevant scenarios; model results remain separate from real-device and human evidence. |
| **loop** | Records bounded fixes, current-build replay, regression and preserved-intent checks. | Host browser/Figma tools and actual receipts. Existing improvement authority is recorded explicitly for scoped local patches. |

The host-agent instructions implement this integrated entry path. The CLI validates
imported evidence and applies bounded local text patches; the host performs
browser actions, Figma work and builds. Whole-product execution from request to
verified improvement still needs a separate live acceptance run. Existing fixture
and component tests do not establish that result.

## Install

Install one folder with one command. It contains every component: research,
persona-qa, ergonomics and loop with their references and schemas, the bundled
insane-search toolkit and the portable launcher. The same command prepares
the pinned web driver and Chromium. All features are included; references load per task. You supply a
URL or repository, not prepared packets; the bundled examples are maintainer
fixtures for the shipped self-tests. The Python tools need Python 3.10+ on
macOS, Linux or WSL. If the default `python3` is older (the macOS system Python
is 3.9), the host runs `python3 scripts/find_runtime.py` from the skill folder.
It prints JSON with the highest supported Python, a Node.js 22 path and any
gaps; it installs nothing.

```sh
git clone https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
cd Remorsearch_UX_QA_Skill
python3 scripts/install.py --target codex
```

`--target claude` installs into `~/.claude/skills/remorsearch-ux-qa`; the
default is `codex` (`~/.codex/skills/remorsearch-ux-qa`). Pass
`--destination /path/to/folder` for an explicit path, for isolated testing.
Maintainer-only packaging and integrity checks are documented in
[build and release checks](docs/release.md).

Python 3.10+, Node.js 22 (>=22 <23) and npm are checked before anything is
written. The installer runs `npm ci` inside a staged copy's `drivers/web`,
downloads Chromium through Playwright into its browser cache
(`~/Library/Caches/ms-playwright` by default on macOS; set
`PLAYWRIGHT_BROWSERS_PATH` first for another location), and finishes with an
actual Chromium launch. It changes no global runtime or account. Use Node.js
22. With the pinned Playwright 1.56.1, `npx playwright install` hangs after the
download on Node.js 24.16 or later and on Node.js 26
([microsoft/playwright#40724](https://github.com/microsoft/playwright/issues/40724);
Playwright 1.60 works).

Destinations are guarded: symlinked paths, the source repository, unrelated
existing folders, the filesystem root and the home directory are refused.
Driver preparation happens on a staged copy, so a failed npm or Chromium
download leaves an existing installation unchanged; fix Node.js, npm or the
network and rerun the same command. Updating an owned installation first
archives the complete previous folder, including run records and symlinks, as
`remorsearch-ux-qa.backup-<timestamp>.tar.gz` beside the skill. Accounts stay
user prerequisites: YouTube comments need your own YouTube Data API key
(`REMORSEARCH_YOUTUBE_API_KEY`), and Figma comparison needs your Figma access.

## Use

Ask in plain words, or call it by name:

```text
/remorsearch-ux-qa Improve our app UX. URL: https://app.example.test or repository: /path/to/product
/remorsearch-ux-qa 우리 앱 UX 개선해줘. URL 또는 저장소는 여기야.
/remorsearch-ux-qa Find out why people abandon our checkout, from reviews and community posts.
/remorsearch-ux-qa 결제 화면을 처음 쓰는 사용자 페르소나로 QA해 줘. Figma 파일은 이거야.
/remorsearch-ux-qa Check one-handed and colour-blind usability of the signup flow on a Galaxy S24.
/remorsearch-ux-qa 간편결제 실패 경험을 한국어 커뮤니티와 앱 리뷰에서 근거 붙여서 정리해 줘.
```

The agent derives tasks, questions and scenarios from the product, inspects
relevant project documents and accessible intent memory, and preserves confirmed
decisions through replay. It asks only for material missing access or unresolved
decisions and continues unaffected work. Subagents are optional and inherit the
current session's model; you are asked only if you want to choose one.

One request is enough: a URL or repository, optionally a task. The agent first
writes a scoped baseline assessment of the tasks it actually reached, which is
useful on its own, then researches only the questions that assessment raised. It
makes a fix only when one is warranted and replays it. A missing optional source
or tool limits only the affected result. When it prepares a loop packet, the
host writes the observed facts and marks mechanical fields `@auto`;
`python3 scripts/ux_loop.py fill DRAFT.json --evidence-root EVIDENCE [--workspace PRODUCT] --out packet.json`
computes only hashes, digests, run links and fix revisions. It never fills
context, intent, grants, outcomes or severity, and a refused or invalid result is
not acceptance. A passed task shows that task only; it is not whole-product
readiness or measured user benefit.

Default research candidates are 당근 (Karrot), 디시인사이드 (DC Inside), 유튜브 댓글
(YouTube comments), X, 인스타그램 (Instagram) and Threads(쓰레드). The agent selects
those relevant to observed tasks; availability and collection are not guaranteed.
After URL discovery, the bundled insane-search methods remain subject to the
existing access/evidence rules. See the [operational checklist](skills/remorsearch-ux-qa/references/loop/product-improvement.md)
for the product-to-replay workflow and existing plan/bundle/loop commands.

## Evidence rules

- Every statement is `observed`, `inferred` or `unknown`; repetition does not make
  inference a fact.
- Synthetic personas and simulated profiles create test situations. They never
  show real-user preference, prevalence or discomfort.
- Community signals are hypotheses until the behaviour is confirmed on the real
  product.
- Research/review requests remain read-only. An improvement request authorizes
  ordinary reversible fixes within its scope; the agent records that existing
  authority in CLI grants. Deployment, publication and real account changes need
  their own authorization.
- Screen composition and UX changes are created in Figma first, with actual file,
  node, version and readback records. Missing access blocks the affected change
  while feasible investigation and QA continue.
- Complete improvement requires current-build replay, adjacent regression and
  preserved-intent checks. If scoped QA finds no reproducible issue, inspection
  can finish without changes; missing required evidence stays incomplete.

Research and QA runs can exchange a machine-readable **evidence bundle**
(`schemas/ux-evidence-bundle.v1.schema.json`). The offline validator checks IDs,
cross-references, permission records, synthetic-persona misuse, unsupported
verified findings and retention dates that have passed. The skill ships a small
valid bundle to try it on:

```sh
python3 ~/.claude/skills/remorsearch-ux-qa/scripts/validate_bundle.py bundle.json
python3 ~/.claude/skills/remorsearch-ux-qa/scripts/validate_bundle.py ~/.claude/skills/remorsearch-ux-qa/examples/bundle/minimal.json
```

## Reading public pages

Research and persona-qa read what anyone can read without an account.

- **Tools.** The skill uses the best browser tool your agent host has: first an
  agentic tool that drives your own browser (Aside, Claude in Chrome, the Claude
  app's built-in browser), then an automation browser (Playwright MCP, Chrome
  DevTools MCP, or the bundled page reader `read_page.mjs`; the bundled live web
  driver tests your product, it does not read community pages), then its own
  reader, and last plain web search and fetch, whose results are leads only. It
  records which tool read each source.
- **The reader** (`scripts/ux_research.py`) climbs a short ladder only as far as
  needed: an official feed or API, one honestly identified request, the site's
  own mobile or feed version, then a real-browser render.
- **Stops.** It stops at logins, paywalls, member-only groups, age checks, human
  checks such as CAPTCHAs, bot blocks and "checking your browser" pages (it
  never waits one out), robots.txt and AI or TDM opt-outs, rate limits and
  removed posts, and reports each as a coverage gap. A check, a block or a rate
  limit stops the whole site for the run, and no browser render follows. It also
  stops where a
  platform's published terms or an official notice restrict automated collection
  or AI use (`terms_restricted`), and it honours robots.txt rules for AI agents
  that fetch pages on a user's behalf. It never reads search results pages. It
  never disguises itself, and it reads one page at a time per host, at least 8
  seconds apart by default, within a budget.
- **Privacy.** Quotes are short, authors become salted keys, and temporary page
  text is kept outside your project and deleted when the run closes. Phone
  numbers, e-mail addresses, ID numbers, card and account numbers and IP addresses
  are removed before the agent sees the text. Signed-in reading happens only in
  communities you authorise for the run, and keeps summaries only.

Details: [`public-page-access.md`](skills/remorsearch-ux-qa/references/research/public-page-access.md).

## Korean research

For a Korean product, Korean-speaking users or a report in Korean, research mode
also follows the Korean pack, which starts at
[`overview.md`](skills/remorsearch-ux-qa/references/research/korea/overview.md).
persona-qa adds the accessibility notes in
[`kwcag-2.2.md`](skills/remorsearch-ux-qa/references/persona-qa/kwcag-2.2.md). The
pack is written in Korean and adds:

- a map of 27 Korean channels: how public each is, the legitimate way to read it,
  the stops to expect and its terms status;
- Korean query craft and user-language reading (초성체, sarcasm, register);
- disclosure and review-reward markers, and the grading rules that follow from them;
- provenance cards and population frames for Korean statistics;
- a legal checklist (not legal advice) and a report template in Korean;
- KWCAG 2.2 and WCAG 2.2 accessibility results, reported apart.

**Terms stops.** Restricted hosts and their short links stop before any request.
Evidence status (`reported` or `confirmed`) is separate from `lift_requires`:
`never` prohibits a page lift; `written_permission` needs your current terms
check and applicable prior written permission; `terms_check` needs your current
check. Every covering entry must be lifted separately, with at most 10 documents
per entry across its hosts. Open-run commands revalidate the 365-day limit and
`effective_from`; older runs must restart. An agent never records a user's check.

YouTube pages, Meta, TikTok, Clien and App Store pages/feeds use `never`.
DC Inside, Naver, Coupang, X, Daangn and Reddit require written permission; the
Naver Cafe notice has its own terms URL and needs a separate current user check
and applicable prior written permission. YouTube keeps its
official-only Data API route. HN pages use `never`, and its official-only API
reports `official_route_unavailable` until an adapter exists. X oEmbed is removed
after an unauthenticated HTML response on 2026-09-30; no retirement notice was
found. Own-app App Store Connect exports remain `team_provided`.
See [the entries and checks](skills/remorsearch-ux-qa/references/research/public-page-access.md#171-entries).

**YouTube comments** come only through the YouTube Data API, with your own key in
the environment variable `REMORSEARCH_YOUTUBE_API_KEY` (`YOUTUBE_API_KEY` is
accepted as an alias). Keys are read from environment variables only, never from a
file. A missing key is a coverage gap and a question to you, never a reason to read
the page another way. As the key holder you follow YouTube's API terms and
developer policies. [Developer Policies III.E.4.d](https://developers.google.com/youtube/terms/developer-policies), read on 2026-09-30,
requires stored Non-Authorized Data to be deleted or refreshed after 30 calendar days.
The reader stamps each API item with `retention_until`, 30 days
after the fetch, and deletes its own page text when the run closes; you must delete
or re-read each item kept in bundles or reports by its `retention_until`
(`validate_bundle.py` reports one that is past it), and no bundle items are deleted
automatically yet.

**Plain limits.** Most Naver posts cannot be read by the agent. The automation
restrictions in [Naver’s terms](https://policy.naver.com/rules/service.html) and the
[cafe notice dated 2026-08-25](https://notice.naver.com/notices/cafe/33743) were read from the primary pages on 2026-10-01.
2026-08-31 was the press date. Each entry requires its own user check and applicable
prior written permission under `lift_requires: written_permission`. Naver and Kakao
search APIs stay off until the owner reads their current terms. Coverage gaps are
filled with team data, other channel families, surveys and interviews. Directly read
facts are marked 관찰됨; facts not reached in the primary source remain 미확인(...).
`verified_at` stays null until a person reads the primary page.

## Repository layout

```text
skills/remorsearch-ux-qa/    the installable skill (installed by scripts/install.py)
  SKILL.md                   entry point: modes, shared rules, tools
  references/                mode workflows and reference material
    research/korea/          Korean research pack (in Korean): platform map, query craft, markers, statistics, legal checklist, report template
    persona-qa/kwcag-2.2.md  KWCAG 2.2 and WCAG 2.2 notes for Korean products (in Korean)
  scripts/                   CLIs: validate_bundle, ux_loop, ux_research, ergo_qa, benchmarks
  uxloop/ uxresearch/        Python packages behind the loop CLI and the public-page reader
  ergoqa/ schemas/           ergonomics package and the JSON schemas used by the CLIs
  drivers/web/               live Playwright driver (Node.js)
  examples/loop/             synthetic demo fixture for the loop CLI
tests/                       unit tests and fixtures
benchmarks/                  blind benchmark suites with answer keys
docs/                        design notes, human-factors research, validation records
README.md, README.ko.md      this page in English and in Korean
```

## Development

From a repository checkout:

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
(cd skills/remorsearch-ux-qa/drivers/web && npm install && node selftest.mjs)
python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/heldout-mixed --out .ergo-bench/heldout
```

The loop CLI's full reference, including resume, exit codes and trust limits, is
in [`references/loop/cli.md`](skills/remorsearch-ux-qa/references/loop/cli.md).

The tests never reach the network. The reader tests serve their pages from a local
server on 127.0.0.1.

Run the complete package check with Python 3.10+ and the pinned web
driver dependencies installed. The report records test results and verifies the
extracted ZIP from another working directory. See [release checks](docs/release.md).

```sh
python3 scripts/check_release.py --output dist/release-check
```

## Limits

The [QA performance criterion](PRD.md#91-일반-omo-대비-qa-성능) compares ordinary OMO with the same OMO plus Remorsearch under matched models, tools, tasks and budgets. Required rendered checks cover alignment, clipping and component occlusion. The [OMO pilot and mobile QA](docs/validation/design-qa-20261015/report.md) records a final access-matched Astra medium result: 5 versus 6 supported issue families, 1 versus 0 unsupported suggestions, and report time of 5m07s versus 10m08s. An earlier access-mismatched attempt is retained separately. InferHub GLM 5.3 high failed upstream; no QA score is assigned. This small result does not establish general superiority.

The [skill-on / skill-off pilot](docs/validation/skill-ab-20261014/report.md) compares two repetitions on existing local fixtures with the same model and browser tools. It reports detection, unsupported warnings, task completion, time and tokens separately from installation/self-tests; it does not establish general superiority.

The [QA speed evaluation](docs/validation/qa-speed-20261015/report.md) tested an instruction-only speed revision with GPT-6.1 Sol high. It was rejected: the candidate was 4.1% slower by median report-save time and 1.5% slower by median final response time across two valid repetitions. Its second repetition covered the six core areas, but left the observed omitted-sauce feedback failure in recovery observations instead of giving it a separate finding card. The candidate produced no speed win and was not accepted.

- Live browser research (Aside or another agentic browser), Figma and browser
  collection for the loop mode are provided by you or your agent host; the loop
  CLI imports their receipts and never launches them.
- The reader honours robots.txt and AI or TDM opt-outs and stops at bot blocks
  and browser checks, so some sites end up as coverage gaps. Renders never click, so long comment threads and "more reviews"
  lists are only partly read.
- Many Korean platforms restrict automated collection, so DC Inside, Naver and
  Coupang end as coverage gaps unless you record a terms check with their written
  permission, and YouTube is read
  only through its API with your key. The Korean pack is not legal advice.
- The ergonomics mode's thumb-reach model is uncalibrated, and its benchmark suites
  are small and authored by agents. Treat its findings as screening, not
  certification. See `docs/validation/`.
  The [recorded held-out evaluation](docs/validation/experiments/heldout-2-results.md)
  missed its confirmatory noise limit (1.75 P0–P2 units per clean scenario;
  limit 0.35) and condition-identification target. Later fixes do not establish
  that those original targets now pass; review findings before acting on them.
- The bundled web driver runs Chromium device emulation only. Mobile Safari is
  checked through a documented host route (safaridriver with an iOS Simulator) and
  native iOS apps through imported XCUITest evidence; real devices are not exercised.

## License

MIT, see [`LICENSE`](LICENSE). Third-party material and references are listed in
[`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md).

Credits: the public-page reader and the research gate were designed after studying
fivetaku's [insane-search](https://github.com/fivetaku/insane-search) and
[insane-research](https://github.com/fivetaku/insane-research) (both MIT). The original insane-search toolkit is bundled as reference material and invoked
during research acquisition. Its bytes, provenance and upstream license are
preserved. The gate draws ideas from insane-research; none of its code or text is included. The Korean pack and this README's bilingual layout also draw
ideas from [K-skill](https://github.com/NomaDamas/k-skill) (MIT), DaleSeo's
[korean-skills](https://github.com/DaleSeo/korean-skills) (MIT),
[SoDam-Persona-Codex](https://github.com/sodam-ai/SoDam-Persona-Codex) (Apache-2.0)
and fivetaku's [gptaku_plugins](https://github.com/fivetaku/gptaku_plugins) (MIT),
again ideas only. Platform names are descriptive; there is no affiliation with
any of them.
