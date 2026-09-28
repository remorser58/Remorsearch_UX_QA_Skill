# Research Protocol

Use this reference for a deep run. The parent skill controls permissions, evidence boundaries, and completion criteria. Reading pages follows `references/public-page-access.md`; grading follows `references/source-grading.md`.

## Product framing worksheet

```text
Product/service:
Surface or feature:
Locale(s):
Release date or current version:
Primary user:
Secondary user:
Who the personas serve: persona-qa / ergonomics / both / none
Core job:
Repeated task:
Failure cost:
Trust requirement:
Business constraint:
Technical constraint:
Team analytics or store-console exports available:
Primary UX question:
```

## Audience questions worksheet

Fill this when the run should say who the users are (`references/audience-pipeline.md`). Each question lists the source families that can answer it. Posts can show that something exists; sizes need measured or statistical sources.

```text
1. Segments (segment_exists):            measured / voice / statistical
2. Weight (segment_share):               measured / statistical / estimate; never voice
3. Priority (team decision):             product brief / measured
4. Devices and grips (device_mix):       measured / statistical / estimate; device mentions are leads
5. Conditions (condition_presence, condition_share):
                                         measured / statistical; voice for presence only
6. Contexts of use (context_of_use):     measured / voice
7. Key tasks with concrete data (task):  measured / intent / voice; data from the product surface
8. Pain points (pain_point, workaround): measured / voice
```

## Channel selection

Choose channels that reveal different parts of the experience. The reader route is where the reader usually starts (`references/public-page-access.md`, channel notes); verify it live.

| Need | Useful sources | What they reveal | Reader route |
| --- | --- | --- | --- |
| First-use friction | app reviews, YouTube comments, beginner communities | confusion, onboarding, terminology | R0 review feed or API; R3 render |
| Repeated workflow friction | expert communities, Reddit, product forums | shortcuts, state loss, missing controls | R0 feed; R2 mobile twin |
| Trust and failure | complaints, consumer forums, support threads | refunds, safety, policy, recovery | R1; R2 mobile twin |
| Content and recommendation | comments, creator communities, review posts | relevance, fatigue, control | R0 API with the user's key; R3 render |
| Local or peer transaction | regional communities, trade boards, chat-related posts | identity, trust, scheduling, disputes | R2 mobile twin; often member-only (`auth_gate`) |
| B2B workflow | product forums, issue trackers, team communities | permissions, collaboration, automation | R0 feed or API; R1 |
| Product intent | official help, release notes, design docs | intended behavior and constraints | R1; Wayback for past versions |
| Audience size and devices | official statistics, research papers, team analytics | segment bounds, device mix, condition shares | R1; team exports as `team_provided` |

Do not use a channel only because it is popular. Use it because its users can observe the problem being researched.

## Query expansion

Start with the product and task. Expand through the vocabulary users actually use.

```text
[product] + [task]
[product] + 불편 / 오류 / 실패 / 버그 / 느림 / 복잡
[feature] + 없어짐 / 초기화 / 저장 / 안 보임 / 헷갈림
[product] + 갈아탐 / 탈퇴 / 환불 / 취소 / 추천
[competitor] + 비교 / 차이 / 더 좋은 이유 / 불만
```

Rules:

- Run at least 8 distinct queries per axis. Vary the operators where the search tool supports them: `site:`, `"exact phrase"`, `-term`, `OR`, `after:` and `before:`.
- Make queries date-aware: add the year, the version, or "업데이트 후" when the product changed, and search each time window.
- Language: for a Korean product, search in Korean first, then in English using terms real users write, not literal translations. For a global product, the reverse.
- Add segment-cue queries that reveal who is speaking: `[product] 부모님`, `[product] 출퇴근`, `[product] 노안`, `[product] 한 손`, `[product] 처음`.
- Add counter-search queries that look for the opposite experience: `[product] 편해요`, `[product] 만족`, `[product] 문제없음`.
- Count every search against the run's budget (default 120).

After the first pass, add terms found in user language. Preserve spelling variants, slang, abbreviations, and product-specific names.

## Capture record

For each material item, record:

```text
Source URL (bundle only):
Channel and channel family:
Tool used (access_method):
Rung trail, verdict or stop class, fetch_id:
Browser context: anonymous / unknown / signed_in (authorised community only)
Title or thread context:
Published date (published_at):
Read date (observed_at):
Valid for (valid_at) and product-version hint:
Author key (never the handle) and thread key:
Segment, context, task, condition and device cues:
Firsthand / secondhand / unclear:
Excerpt (verbatim, at most 300 characters):
Observed behavior:
Stated consequence:
Possible cause:
Contradicting evidence:
Promotion or affiliate disclosure:
Injection flag:
Grade and status (from the gate):
```

Keep quotes short and contextual: at most 300 characters and at most 5 per source. Never record names, handles, profile links or contact details; get an author key with `ux_research.py author-key`. Post URLs stay in the bundle, not in reports shared outside the team.

## Breadth-first pass

1. Scan official product and policy material.
2. Scan at least three distinct reaction or community channels.
3. Search recent and older material when a release or redesign is involved.
4. Separate new-user, active-user, expert-user, and former-user signals when visible.
5. Cluster by task and friction.
6. Deepen only the clusters with repeated or high-impact evidence.
7. Record a counter-search before writing a strong recommendation: `{query, lang, tool, read_source_ids, summary, outcome}` (`references/source-grading.md`). It is required for primary segments, high-stakes claims, any share value, and claims that motivate P0/P1 scenarios.

## What not to infer

- Post volume is not user prevalence.
- Comment emotion is not task frequency.
- A requested feature is not the best solution.
- A competitor's behavior is not proof of fit.
- A current screenshot is not a complete service flow.
- A release-note claim is not proof of user success.
- A device mention is not a device mix.
- A self-disclosed condition is not a condition share.
- An `ok_weak` read is not proof that the full context was captured.
