# Remorsearch UX QA

**Research before release. No remorse after.**

Remorsearch (*ree-mor-search*, 리모서치) UX QA is an evidence-first agent skill for
Claude Code and Codex. It researches what real users say, tests your product on the
real screen with personas, checks ergonomics and accessibility, and replays the same
scenario after a fix. It keeps observed facts, inference and synthetic personas
apart, so a report never passes off a simulation as user research.

## What it does

One skill, four modes. The skill picks the mode from your request.

| Mode | What it does |
| --- | --- |
| **research** | Collects real user experiences from communities, comments, app reviews and official sources; separates firsthand evidence from inference; traces root causes; proposes Figma-ready flows. |
| **persona-qa** | Builds persona scenarios, runs them on the real product in a browser, compares against Figma, and reports P0–P3 findings with reproduction steps and root causes. |
| **ergonomics** *(experimental)* | Persona agents with body and sense profiles (one-handed or left-handed grip, thumb reach, tremor, walking, colour vision deficiency, presbyopia) operate the real screen; deterministic human-factors models score reach, touch accuracy, gaze, contrast, reading time, game timing and flashing. Results are coverage over simulated profiles, never prevalence. |
| **loop** | Composes research and QA into a bounded, resumable goal: an explicitly authorised fix, then a same-scenario replay, then an evidence-backed stop report. |

## Install

Copy one folder into your skills directory.

```sh
git clone https://github.com/remorser58/ux-research-qa-skills.git
# Claude Code (personal); use .claude/skills/ inside a project to share it with a team
cp -R ux-research-qa-skills/skills/remorsearch-ux-qa ~/.claude/skills/
# Codex
cp -R ux-research-qa-skills/skills/remorsearch-ux-qa ~/.codex/skills/
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
```

**First run.** If the run needs subagents (persona agents, parallel research,
judges), the skill first looks for a subagent model mapping your harness already
has (`CLAUDE_CODE_SUBAGENT_MODEL`, agent definitions, plugin agents) and follows
it without asking. Only if there is none does it ask once, with the host's
selection prompt, which model and reasoning effort to use, and it saves the answer
in `~/.config/remorsearch-ux-qa/config.json`. Say "change the agent model" to be
asked again.

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
cross-references, permission records, synthetic-persona misuse and unsupported
verified findings:

```sh
python3 ~/.claude/skills/remorsearch-ux-qa/scripts/validate_bundle.py bundle.json
```

## Repository layout

```text
skills/remorsearch-ux-qa/    the installable skill (copy this folder)
  SKILL.md                   entry point: modes, shared rules, tools
  references/                mode workflows and reference material
  scripts/                   CLIs: validate_bundle, ux_loop, ergo_qa, benchmarks
  uxloop/ ergoqa/ schemas/   Python packages and JSON schemas used by the CLIs
  drivers/web/               live Playwright driver (Node.js)
  examples/loop/             synthetic demo fixture for the loop CLI
tests/                       unit tests and fixtures
benchmarks/                  blind benchmark suites with answer keys
docs/                        design notes, human-factors research, validation records
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

## Limits

- Live Aside, Figma and browser collection for the loop mode are provided by you or
  your agent host; the loop CLI imports their receipts and never launches them.
- The ergonomics mode's thumb-reach model is uncalibrated, and its benchmark suites
  are small and authored by agents. Treat its findings as screening, not
  certification. See `docs/validation/`.
- Only Chromium device emulation is exercised by the web driver; no real iOS
  Safari, native apps or real devices.

## License

MIT, see [`LICENSE`](LICENSE). Third-party material and references are listed in
[`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md).

## 한국어 요약

Remorsearch UX QA는 근거 중심의 UX 리서치·QA 스킬입니다. 커뮤니티와 리뷰에서 실제
사용자 경험을 모으고(research), 페르소나로 실제 화면을 테스트하고(persona-qa),
한 손 조작·색각·노안 같은 인체공학 조건을 점검하고(ergonomics, 실험적), 권한을
받은 수정 뒤 같은 시나리오로 다시 확인합니다(loop). 관찰된 사실, 추론, 합성
페르소나를 끝까지 구분해서, 시뮬레이션을 실제 사용자 조사처럼 보고하지 않습니다.
설치는 `skills/remorsearch-ux-qa` 폴더 하나를 `~/.claude/skills/`나
`~/.codex/skills/`에 복사하면 됩니다.
