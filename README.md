# Remorsearch UX QA

English | [한국어](README.ko.md)

**Research before release. No remorse after.**

Remorsearch (*ree-mor-search*, 리모서치) UX QA is an evidence-first agent skill for
Claude Code and Codex. It researches what real users say, tests your product on the
real screen with personas, checks ergonomics and accessibility, and replays the same
scenario after a fix. It keeps observed facts, inference and synthetic personas
apart, so a report never passes off a simulation as user research.

## What it does

One skill, four modes. The skill picks the mode from your request.

| Mode | What it does | Needs |
| --- | --- | --- |
| **research** | Collects real user experiences from communities, comments, app reviews and official sources; separates firsthand evidence from inference; traces root causes; proposes Figma-ready flows. Also researches who the users are, as audience segments that personas are built from. | Public pages need no account. YouTube comments need your own YouTube Data API key (`REMORSEARCH_YOUTUBE_API_KEY`). |
| **persona-qa** | Builds persona scenarios, runs them on the real product in a browser, compares against Figma, and reports P0–P3 findings with reproduction steps and root causes. | Node.js 22 and Playwright for live web pages. A Figma file is optional. |
| **ergonomics** *(experimental)* | Persona agents with body and sense profiles (one-handed or left-handed grip, thumb reach, tremor, walking, colour vision deficiency, presbyopia) operate the real screen; deterministic human-factors models score reach, touch accuracy, gaze, contrast, reading time, game timing and flashing. Results are coverage over simulated profiles, never prevalence. | Node.js 22 and Playwright for live web pages. Screening only. |
| **loop** | Composes research and QA into a bounded, resumable goal: an explicitly authorised fix, then a same-scenario replay, then an evidence-backed stop report. | A separate write grant for the fix. Browser and Figma receipts come from your agent host. |

## Install

Install one folder into your skills directory. It includes the original
insane-search toolkit as reference material for Remorsearch's research stage;
users do not install a separate search skill. The Python tools need Python 3.10+
on macOS, Linux or WSL and use the standard library and POSIX file locks.

The current candidate is on `codex/release-candidate-20261002`; use that branch
until the skill is merged into `main`.

```sh
git clone --branch codex/release-candidate-20261002 https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
# Claude Code (personal); use .claude/skills/ inside a project to share it with a team
cp -R Remorsearch_UX_QA_Skill/skills/remorsearch-ux-qa ~/.claude/skills/
# Codex
cp -R Remorsearch_UX_QA_Skill/skills/remorsearch-ux-qa ~/.codex/skills/
```

Copying the folder completes the skill installation. Maintainer-only packaging
and integrity checks are documented in [build and release checks](docs/release.md).

The folder contains the Python tools, JSON schemas, demo fixtures, live web
driver, and original search instructions with their references and provenance.

The live web driver (persona-qa and ergonomics on real web pages) also needs Node.js
22 and Playwright. The commands below select the Codex installation. For Claude
Code, set `REMORSEARCH_SKILL_DIR` to `~/.claude/skills/remorsearch-ux-qa`.

```sh
REMORSEARCH_SKILL_DIR="$HOME/.codex/skills/remorsearch-ux-qa"
cd "$REMORSEARCH_SKILL_DIR/drivers/web"
npm ci && npx playwright install chromium
```

Use Node.js 22. With the pinned Playwright 1.56.1, `npx playwright install` hangs after the
download on Node.js 24.16 or later and on Node.js 26
([microsoft/playwright#40724](https://github.com/microsoft/playwright/issues/40724);
Playwright 1.60 works).

## Use

Ask in plain words, or call it by name:

```text
/remorsearch-ux-qa Find out why people abandon our checkout, from reviews and community posts.
/remorsearch-ux-qa 결제 화면을 처음 쓰는 사용자 페르소나로 QA해 줘. Figma 파일은 이거야.
/remorsearch-ux-qa Check one-handed and colour-blind usability of the signup flow on a Galaxy S24.
/remorsearch-ux-qa 간편결제 실패 경험을 한국어 커뮤니티와 앱 리뷰에서 근거 붙여서 정리해 줘.
```

**First run.** If the run needs subagents (persona agents, parallel research,
judges), explicit model and effort choices in your request take precedence.
Otherwise, the skill looks for a subagent model mapping your harness already
has (`CLAUDE_CODE_SUBAGENT_MODEL`, agent definitions, plugin agents) and follows
it without asking. Only if there is none does it ask once, with the host's
selection prompt, which model and reasoning effort to use, and it saves the answer
in `~/.config/remorsearch-ux-qa/config.json` only if you ask to save it. Say "change the agent model" to be
asked again. The recommended default, Sonnet at max effort, comes from a blind
benchmark on 11 screens
([`docs/validation/subagent-model-benchmark.md`](docs/validation/subagent-model-benchmark.md)).
Claude Code applies a subagent's effort only through an agent definition, so the
skill offers to create two small ones in `~/.claude/agents/`.

## Evidence rules

- Every statement is `observed`, `inferred` or `unknown`; repetition does not make
  inference a fact.
- Synthetic personas and simulated profiles create test situations. They never
  show real-user preference, prevalence or discomfort.
- Community signals are hypotheses until the behaviour is confirmed on the real
  product.
- Read-only by default. Design, test-data and code writes each need an explicit
  grant.
- Figma is the design source of truth when it exists.

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
skills/remorsearch-ux-qa/    the installable skill (copy this folder)
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
- Only Chromium device emulation is exercised by the web driver; no real iOS
  Safari, native apps or real devices.

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
