# Community inputs for generated-UI preflight

Research date: 2026-10-13. Scope: public discussions of AI-assisted web UI quality, concrete repairs and counterexamples; then reusable preflight instructions in the existing Remorsearch skill. The user requested DC Inside, X, Reddit and Threads. Channel coverage is recorded below with the exact reading boundary.

## Coverage

All four requested channels were attempted. Aside supplied DC Inside, X and Threads reads; the web tool supplied Reddit reads after the Aside model route returned quota error 429/1310. Aside's direct browser controls remained available. A supplemental Brave search connector returned `SUBSCRIPTION_TOKEN_INVALID` and supplied no evidence.

| Channel | Actual reading | Limits |
| --- | --- | --- |
| DC Inside | Two full posts and their visible replies in the AI-utilization gallery | One discovery query; not a gallery census |
| X | One article body and one status with visible replies, through the existing signed-in profile | Summaries only; article images/replies and status video not reviewed; promotional claim distinguished |
| Reddit | Public thread bodies and visible replies for R01–R04 and R06 | R03 search/body mismatch; R05 excerpt only; exact publication dates often index-only |
| Threads | Public tag-feed context, one reply body, three parts of one developer experiment | Conversation views hit a login wall; one post unavailable; missing replies not counted |

Discovery queries: `site:dcinside.com 바이브코딩 UI`, `site:x.com "vibe coding" UI broken buttons`, `site:threads.net "vibe coding" UI`, and the Reddit query below. Follow-up searches resolved post URLs. No claim of exhaustive coverage, representative prevalence or current behavior of the linked products. Read-only browsing used research tabs; no posts, reactions or account changes were made.

## DC Inside, X and Threads source ledger

All observations below were collected on 2026-10-13 with Aside. The supervising review checked the returned source notes; these are qualitative reports, not independently reproduced product failures.

| ID | Source | Publication and reading scope | Observation | Preflight consequence and limit |
| --- | --- | --- | --- | --- |
| D1 | [Incremental AI UI changes](https://gall.dcinside.com/mgallery/board/view/?id=ai_utilize&no=116963) | 2026-10-07 22:12 in page header; post and visible replies | A builder reports that an initially impressive UI deteriorated through repeated feature additions and tweaks, making quality harder to judge. Replies include a similar experience and requesting fresh mockups. | Keep an accepted visual/behavior baseline and compare subsequent edits with it. Generating alternative mockups is a reported workaround, not a command to redesign or discard approved work. |
| D2 | [Manual adjustment of UI values](https://gall.dcinside.com/mgallery/board/view/?id=ai_utilize&no=39551) | 2026-08-22 16:21 in page header; post and visible replies | A builder finds small position, size and color adjustments easier after asking AI to locate the relevant code or extract values, then editing directly. | Prefer a precise, inspectable repair using existing tokens; verify the resulting layout. This reported workflow does not establish a universal limitation of AI. |
| X1 | [Signs of vibe coded UI](https://x.com/yuwen_lu_/article/2041187936738447565) | Page shows Apr 7, edited; year unverified. Article text read through an existing signed-in session; images and replies unread. | Opinion catalog discusses weak hierarchy, excessive nested containers, readability problems from glass/shadows, decorative icons, border artifacts and animations that leave content missing. It also describes changing defaults and improving quality. | Inspect hierarchy, readability, unnecessary containers and scroll visibility in the actual product. Numeric palette recipes and blanket font/color bans remain advice, not acceptance rules. Summarized without quoted member text. |
| X2 | [QA before shipping a generated MVP](https://x.com/Hartdrawss/status/2082398323323830744) | 2026-07-29 18:30; post and visible replies via existing signed-in session; video unplayed. | Promotional QA-tool advocacy claims discovery of a mobile redirect to a dead route, broken back navigation after payment, missing API-error state and a first-tap race. A reply questions false positives. | Candidate scenarios: mobile route, back/recovery, API failure and first activation. These remain promotional, unverified claims; no payment or production actions were performed. |
| T1 | [Public vibe-coding tag feed](https://www.threads.com/tag/vibe-coding) | Public feed read; individual dates shown; replies gated. | A question asks how readers recognize a vibe-coded website. Most other feed material is humor or economic opinion. | Vocabulary/context only. Off-topic security anecdotes and engagement counts do not support UI findings. |
| T2 | [Reply about perceived visual tells](https://www.threads.com/@christyhuu/post/DaMB1vPGe2c/yes-text-color-drop-shadows-outlines) | 2026-06-29; one public reply body; broader conversation gated. | Reply points to text, color, shadows and outlines as perceived tells. | Weak opinion about appearance. Use only as a prompt to inspect actual hierarchy/readability, never proof of authorship or defect. |
| T3 | [UI rewrite experiment, part 1](https://www.threads.com/@skuwamoto/post/DbCKxfzmQ7j), [part 2](https://www.threads.com/@skuwamoto/post/DbCKx6GGVfF), [later reflection](https://www.threads.com/@skuwamoto/post/DbCKyznmenF) | Search index: 2026-07-14; page date unverified. Three individual post bodies read from public page-title text; missing part and replies unread. | A developer describes an incomplete behavior inventory during an AI UI rewrite. Human review found changed behavior and obvious visual mistakes, which were added back to the inventory. The author also values AI's ability to map behaviors. | Preserve an explicit inventory of accepted behavior and check regressions after each patch. This is a firsthand experiment with a positive counterpoint, not a measured success rate. |

A Threads post reporting illegibility redirected to `?error=invalid_post`; it was excluded as unavailable. Another reply appeared only in a search snippet and contributes no full-post evidence. Login walls were not bypassed. Counterpoints are retained in X1, T3, R04 and R06.

## Reddit source ledger

Purpose: qualitative inputs for Remorsearch generated-UI preflight. Public web-tool reads supplemented Aside after its GLM Flash execution failed with provider quota error 429/1310. No product linked from these posts was tested; no prevalence, causal AI attribution, or formal Remorsearch gate status is established. Search result dates are recorded separately from exact-date verification. Summaries omit identities and avoid verbatim quotations.

| ID | Source | Date and scope | Observation | QA implication and limit |
| --- | --- | --- | --- | --- |
| R01 | [Vibe coding sucks](https://www.reddit.com/r/webdev/comments/1l1agmo/vibe_coding_sucks/) | Search index: 2025-06-02; opened post and comments, relative date only. Specific relevant comment read at lines 800–805. | A builder reports repeated attempts to obtain a working mobile-menu exit button. | Exercise open, close, outside click/Escape if intended, scroll unlock and focus return. Firsthand report of a problem; present-day product behavior untested. General hostile opinions in the thread are not evidence. |
| R02 | [How difficult would it be to make my own no code vibecoding website?](https://www.reddit.com/r/vibecoding/comments/1r5dt4a/how_difficult_would_it_be_to_make_my_own_no_code/) | Search index: 2026-02-15; opened thread and visible replies; relative dates in retrieved body. Lines 119–140. | A reviewer reports leftover placeholders, a preview and transparency step doing nothing, enabled buttons in invalid states, and a model-size input contradicted by the generated output. | Compare promised action and supplied values with final result; test disabled/invalid/loading/error states and placeholders. Reviewer report, not independently reproduced. Builder's later mobile acknowledgment was visible only in search output, so excluded from confirmed body summary. |
| R03 | [What's your most beautiful vibe coded website?](https://www.reddit.com/r/vibecoding/comments/1x1kqoa/whats_your_most_beautiful_vibe_coded_website/) | Search index: 2026-10-09 to 11; opened body showed only a subset of comments and relative times. | Opened reply reports large empty space while scrolling a mobile page. Search output additionally reports overlapping iPhone buttons and author acknowledgment, but those replies were absent from the opened body. | Inspect scroll transitions and short viewports. The overlapping-buttons claim remains a search lead, not full-post evidence. This snapshot mismatch is retained explicitly. |
| R04 | [How to vibe code with good UI/UX?](https://www.reddit.com/r/vibecoding/comments/1r0lamy/how_to_vibe_code_with_good_uiux/) | Search index: 2026-02-10; opened post and visible replies. | Contributors suggest explicit spacing, typography, layout, platform patterns, user intent and design references instead of vague appearance requests. | Preserve approved design intent and concrete component rules; aesthetic similarity alone cannot fail QA. Advice/counterpoint, not measured evidence of a fix. |
| R05 | [If you're vibe coding a website, look out for these signs](https://www.reddit.com/r/SaaS/comments/1miq0ea) | Search index: 2025-08-06; direct open returned Internal Error. Search excerpt only. | Excerpt mentions dead social links, unsupported testimonials, absent loading states, distracting animations and mobile neglect alongside subjective style preferences. | Lead-only checklist input. Do not cite as a fully read thread or convert purple/Inter/gradients into blanket bans. |
| R06 | [How to create a UI which doesn't scream AI slop](https://www.reddit.com/r/vibecoding/comments/1tzie7q/how_to_create_a_ui_which_doesnt_scream_ai_slop/) | Search index: 2026-06-07; opened post and visible replies. | After revising the appearance, the author still receives unsupported AI-look criticism. Replies disagree: some dislike the palette, while others prioritize truthful content, working options and links, hierarchy and usability. | Explicit counterevidence to appearance-based attribution or universal palette bans. This is a debate and design feedback, not measured user preference or conversion. |

Discovery query: `site.reddit.com "vibe coding" "buttons" "mobile"`. Counter-search/read: R04. Different defects and accounts from self-selected threads do not establish population frequency. Repeated source references count once. No formal research gate was run.

## Decisions and verification

Observed on 2026-10-13. These are engineering decisions for the requested skill update, not population findings or formal research-gate outputs.

| Decision | Support | Consequence in the skill |
| --- | --- | --- |
| Check real completion before aesthetic polish | R01 menu close failure; R02 inert preview and input/output mismatch | Complete a priority task; inspect final state, error/recovery, and back/reload behavior using owned safe fixtures. |
| Review content over full scroll and each hold/transition | Portfolio captures show OGC title/CAUSE collision, METHOD graph labels through body copy and fixed HUD/media intersections; R03 mobile empty-space report | Capture scene entry, stable state, transition and exit; distinguish visual occlusion/intended labels from rect intersections. |
| Inspect painted images in the requested engine | Portfolio fresh Safari baseline hides contain-fit images; filter reorder paints them | An HTTP 200, complete=true or naturalWidth>0 alone cannot pass visible-image QA. Chromium mobile is not Safari verification. |
| Keep identity and preference separate from defects | R04 explicit design constraints; R06 disagreements about visual style; W3C standards supply concrete accessibility criteria | No AI-origin classifier, slop score, purple/Inter/card blanket ban or invented user preference. Preserve user's Figma design and explicit restrictions. |
| Review copy and proof together | R02 leftover placeholders; R05 source is only an excerpt lead | Check product claims, metrics/testimonials provenance, action labels and realistic long content. Never invent replacement numbers or testimonials. |
| Preserve uncertainty in evidence | R03 search/open mismatch; R05 open error; provider quota and missing Brave token | Record accessed scope/date; snippets and promotional claims stay leads; missing channels never count as completed research. |

### Primary technical references read

- [WCAG 2.2 Reflow, 1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html): vertical content at 320 CSS px; equivalent to 1280 px at 400% zoom. Necessary two-dimensional layouts have scoped exceptions.
- [Resize Text, 1.4.4](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html): up to 200% text resizing without losing content or function; distinct from the 320 px reflow check.
- [Text Spacing, 1.4.12](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html): changed line, paragraph, letter and word spacing must not cause loss of content/function.
- [Focus Not Obscured (Minimum), 2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html): focused control is not entirely hidden by authored content; task readability can require a stronger product criterion.
- [Status Messages, 4.1.3](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html): applicable status messages are programmatically available without moving focus; visual messages alone do not prove screen-reader behavior.

These documents do not prove that AI causes the listed defects, or establish universal visual preferences. Platform-specific behavior still needs same-build testing.

## Skill verification

The preflight is invoked from persona QA and whole-product improvement after the first product observation and before baseline conclusions. Affected checks recur after fixes. The entrypoint and all byte limits are unchanged; the new reference is a bounded lookup. No new runner, dependency or generated test harness was added.

- Existing reading-budget tests: 13 passed.
- Existing skill-packaging tests: 32 passed.
- Existing release-file tests: 12 passed.
- Distribution-file check passed; it excludes this repository-only research record and includes the runtime preflight.
- Independent read-only forward review found no material deficiencies for three cases: a working purple-branded UI with only screenshots, an image decoded but not painted in Safari, and a scrolling Korean-title collision plus a menu that cannot close. It retained untested interactions, rejected appearance-only failures and treated geometrical overlaps behind opaque covers as candidates. This was a reasoning review, not a live-browser test.
- The standalone skill-creator quick validator could not run because PyYAML is unavailable in both checked Python runtimes. The repository packaging checks passed, including frontmatter and relocated-reference checks. No dependency was added for this optional tool.
- Existing numeric limits were retained. No claim that the checklist detects every UI defect or that community feedback measures user prevalence.
