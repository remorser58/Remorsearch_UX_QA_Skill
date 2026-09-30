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

Copy one folder into your skills directory.

```sh
git clone https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
# Claude Code (personal); use .claude/skills/ inside a project to share it with a team
cp -R Remorsearch_UX_QA_Skill/skills/remorsearch-ux-qa ~/.claude/skills/
# Codex
cp -R Remorsearch_UX_QA_Skill/skills/remorsearch-ux-qa ~/.codex/skills/
```

The folder contains everything the skill runs: Python tools (3.10+, standard
library only), JSON schemas, a demo fixture and the live web driver.

The live web driver (persona-qa and ergonomics on real web pages) also needs Node.js
22 and Playwright:

```sh
cd ~/.claude/skills/remorsearch-ux-qa/drivers/web
npm install && npx playwright install chromium
```

## Use

Ask in plain words, or call it by name:

```text
/remorsearch-ux-qa Find out why people abandon our checkout, from reviews and community posts.
/remorsearch-ux-qa 결제 화면을 처음 쓰는 사용자 페르소나로 QA해 줘. Figma 파일은 이거야.
/remorsearch-ux-qa Check one-handed and colour-blind usability of the signup flow on a Galaxy S24.
/remorsearch-ux-qa 간편결제 실패 경험을 한국어 커뮤니티와 앱 리뷰에서 근거 붙여서 정리해 줘.
```

**First run.** If the run needs subagents (persona agents, parallel research,
judges), the skill first looks for a subagent model mapping your harness already
has (`CLAUDE_CODE_SUBAGENT_MODEL`, agent definitions, plugin agents) and follows
it without asking. Only if there is none does it ask once, with the host's
selection prompt, which model and reasoning effort to use, and it saves the answer
in `~/.config/remorsearch-ux-qa/config.json`. Say "change the agent model" to be
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

**Terms stops.** Where a platform's terms restrict automated collection, the reader
stops before it sends any request, also for the platform's short links. YouTube
pages, Instagram, Threads and Facebook are marked `confirmed` (the restricting
clause was found) and are never lifted. DC Inside, Naver (including Naver Cafe),
Coupang and X are marked `reported` (press reports and quotes). Their terms ask for
prior written permission, so one is lifted only for a run in which you have read
the host's current terms yourself, hold that permission, and recorded both in the
brief (`access_policy.terms_checked`, with `permission`). The Naver Cafe notice has
no recorded address yet, so it cannot be lifted. A lifted entry is read for at most
10 documents per run across its hosts. An agent never writes that entry.

**YouTube comments** come only through the YouTube Data API, with your own key in
the environment variable `REMORSEARCH_YOUTUBE_API_KEY` (`YOUTUBE_API_KEY` is
accepted as an alias). Keys are read from environment variables only, never from a
file. A missing key is a coverage gap and a question to you, never a reason to read
the page another way. As the key holder you follow YouTube's API terms and
developer policies. The reader stamps each API item with `retention_until`, 30 days
after the fetch, and deletes its own page text when the run closes; you must delete
or re-read each item kept in bundles or reports by its `retention_until`
(`validate_bundle.py` reports one that is past it), and no bundle items are deleted
automatically yet.

**Plain limits.** Most Naver content ends as a coverage gap. Press reports and
quotes say that Naver's terms and a cafe notice of 2026-08-31 restrict automated
collection, and the pack treats that as a stop until you record your own terms
check with the written permission the terms ask for. The Naver and Kakao search APIs are switched off until the owner has read
their current terms. Fill the gaps with your team's own data (VOC, support tickets,
store-console exports), other channel families, surveys and interviews. Most
platform facts in the pack come from search summaries and are marked 미확인
(unverified).

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
- Only Chromium device emulation is exercised by the web driver; no real iOS
  Safari, native apps or real devices.

## License

MIT, see [`LICENSE`](LICENSE). Third-party material and references are listed in
[`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md).

Credits: the public-page reader and the research gate were designed after studying
fivetaku's [insane-search](https://github.com/fivetaku/insane-search) and
[insane-research](https://github.com/fivetaku/insane-research) (both MIT). Ideas
only; no code or text from them is included, and the skill does not depend on or
call either project. The Korean pack and this README's bilingual layout also draw
ideas from [K-skill](https://github.com/NomaDamas/k-skill) (MIT), DaleSeo's
[korean-skills](https://github.com/DaleSeo/korean-skills) (MIT),
[SoDam-Persona-Codex](https://github.com/sodam-ai/SoDam-Persona-Codex) (Apache-2.0)
and fivetaku's [gptaku_plugins](https://github.com/fivetaku/gptaku_plugins) (MIT),
again ideas only. Platform names are descriptive; there is no affiliation with
any of them.
