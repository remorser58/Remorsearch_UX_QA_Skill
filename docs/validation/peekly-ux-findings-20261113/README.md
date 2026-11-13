# Peekly synthetic-persona UX findings

Date: 2026-11-13 (Mac mini, local owned production-preview build)

## Scope and interpretation

- Product source: isolated Peekly worktree, commit 58214441. The original
  insta-tracker worktree was not modified.
- Target: owned local preview at http://127.0.0.1:4173/.
- Library: existing peekly-persona-library-v2 with 32 PER-PEEKLY-V2 records.
  These are synthetic PRD-hypothesis personas, not research participants.
- Model: TOKENMAXX/deepseek-v4.1-flash-free only. Served model names are
  retained verbatim. No paid fallback, InferHub, Haiku or flash-1m route.
- Browser tasks used synthetic Peekly ZIP fixtures only. No Instagram login,
  account connection, real account data, external page or credential.
- Operational completion is not a UX pass.

## Highest-priority observed UX issues (16-persona cohort)

### P2 — Imported results are not brought into the visible viewport

After a successful synthetic ZIP upload, the app displays “결과를 불러왔어요.”
but the three relationship-result controls were outside the visible viewport in
14 of 16 distinct persona journeys (87.5%). At the tested 756×413 viewport,
the page retained a lower scroll position; the user sees the lower-page
connection/reminder area rather than the newly imported relationship summary.
This is a reproducible presentation/scroll-position issue, not a parser or
upload failure. Recommended follow-up: after import, move focus and scroll to
the result heading/summary (without stealing focus from an active user action),
and verify the three counts are visible before showing the success toast.

Representative evidence:

- Persona 003, obs-10:
  ../../../.worktrees/peekly-scale-evidence-20261113/.ux-loop/peekly-verified-20261113-r3/stage-4/sessions/S-jllonbpmnldohibgbiplcegm/evidence/S-jllonbpmnldohibgbiplcegm/1/agent-observation-10.json
  and browser-00075.png (SHA-256
  425547d4b38da985bdc7ede65d7dcd8a2fc8f99e76fc3464d8f3a11bc397bfac).
- Persona 006, obs-11:
  ../../../.worktrees/peekly-scale-evidence-20261113/.ux-loop/peekly-verified-20261113-r3/stage-16/sessions/S-mnipbkpeohkngpdkgnnmagne/evidence/S-mnipbkpeohkngpdkgnnmagne/1/agent-observation-11.json
  and browser-00079.png (same screenshot digest).

### P2 — The manual-import entry is easy to miss and is not where some users look

The supported “이미 받은 자료로 확인하기” entry is nested under
“연결 관리와 다른 방법” on the sample/results screen. That disclosure was
outside the viewport in all 16 observed sample-result journeys. In 11 of 16
journeys, personas first searched the “더보기” tab for an import action; it is
not present there, so they had to return to the result/sample screen, scroll,
and open the disclosure. The path is functional, but its location and
below-the-fold placement create avoidable discovery work.

Representative evidence:

- Persona 003, obs-3 (More-tab search; no import entry):
  ../../../.worktrees/peekly-scale-evidence-20261113/.ux-loop/peekly-verified-20261113-r3/stage-4/sessions/S-jllonbpmnldohibgbiplcegm/evidence/S-jllonbpmnldohibgbiplcegm/1/agent-observation-3.json
  and browser-00027.png.
- Persona 003, obs-5/obs-6 (disclosure below viewport, scroll required):
  same directory, agent-observation-5.json, agent-observation-6.json,
  browser-00040.png and browser-00045.png.
- Persona 007, obs-4 through obs-7 (repeated detour while searching More):
  ../../../.worktrees/peekly-scale-evidence-20261113/.ux-loop/peekly-verified-20261113-r3/stage-16/sessions/S-knflfidaobfbommkeknoohdl/evidence/S-knflfidaobfbommkeknoohdl/1/agent-observation-4.json
  through agent-observation-7.json.

Recommended follow-up: retain the simple primary screen, but add a contextual
“이미 받은 파일이 있어요” entry near the sample/result action area or in the
More tab; ensure it is visible without scrolling at common mobile viewports.
Avoid duplicating competing import paths with different names.

## Observations deliberately not promoted to defects

- After import, the “인스타를 한 번 연결해 두세요” / future-unfollow message
  appeared in 16/16 runs. This matches the current PRD for a single imported
  snapshot without automatic rechecks; it is an intentional next-step prompt.
- The import wizard says “받은 파일 바로 넣기” where the PRD says
  “이미 파일을 받았어요”. The control did navigate directly to step 3, so
  this is wording drift rather than a demonstrated functional failure.
- The personas used one synthetic ZIP path. HTML/JSON parity, malformed-file
  handling, wrong-account rejection, iOS share-sheet behavior, assistive
  technology and real Instagram authentication were not established.

## 16-persona recovery and model execution

The first 16-endpoint attempt did not finish all 16 tasks. Eight of the 12
new-batch tasks completed; two became uncertain and two remained queued.
Those four incomplete persona IDs (009, 013, 014, 016) were rerun in a fresh,
isolated recovery run. The prior run, attempts and receipts were preserved.
The recovery batch completed 4/4, with 4 valid evidence sessions and confirmed
browser shutdown. The resulting distinct cohort is personas 001–016.

The first run's two uncertainty causes were:

1. Persona 009: model final judgment was rejected because criterion kind/index
   bindings were not explicit in the model contract; retries then timed out.
   This was an adapter/model-contract issue, not an app error.
2. Persona 014: browser driver rejected a click target as not allowed or
   visible before dispatch. The original queue correctly marked the outcome
   uncertain rather than replaying a possibly dispatched action. A later
   isolated recovery completed without mutating the original queue.

Other repairs:

- A privacy scrubber could mistake numeric runs in SHA-256 strings for card
  numbers and mutate the digest. Capture bytes are now verified before
  text-only privacy scrubbing; digests stay immutable.
- Final-judgment contracts now provide exact expected criterion bindings,
  use independent zero-based indices for success and recovery, and reject
  missing, duplicate, string-valued or invalid status bindings.
- A pre-dispatch click rejection is recorded as a failed action plus a fresh
  observation; the click is not automatically replayed. Unknown transport
  failures still remain uncertain.

## Model usage and limits

Requested model: TOKENMAXX/deepseek-v4.1-flash-free. Provider: TOKENMAXX.
Served model names are recorded verbatim per response. Policy cost: USD 0
under the user's free-route authorization. Provider cost and billing_source
fields that were absent remain null; no invoice verification is claimed.
HTTP 429 counts and known token usage are retained in the machine-readable
evidence index.

This is browser QA of one fixed web preview and synthetic fixtures. It is not
real-user evidence, population prevalence, satisfaction measurement, iOS
validation, or product readiness. The P2 findings should be reproduced with
ordinary human participants and additional viewport sizes before claims about
prevalence or impact.

## Machine-readable evidence

- evidence-index-16.json: rehashed observation logs and PNG evidence anchors
  from the 16 distinct personas; includes attempt lineage and limitations.
- The raw PNGs and full queue/model ledgers remain in the private local
  .ux-loop evidence trees and are not committed as user imagery.

## Supplemental: final 32-persona cohort and third finding

### P3 — The primary relationship label omits an important inclusion rule

The PRD defines “나를 맞팔 안 한 사람” as including accounts that used to
follow back but no longer do. The visible result hint only says
“내가 팔로우하는데 나를 팔로우하지 않아요”, which does not communicate that
historical mutuals are included. One of 32 personas explicitly flagged the
missing qualification. This is independently confirmed by comparing the
current PRD and rendered source copy; it is a content-accuracy gap, not a
calculation defect. Recommended follow-up: add a short clarification such as
“예전에 맞팔이었지만 지금은 나를 팔로우하지 않는 계정도 포함해요.”

Evidence:

- Persona 020, obs-2:
  ../../../.ux-loop/peekly-final32-r1/stage-32/sessions/S-diebhlnikcjjpepiglcicgpc/evidence/S-diebhlnikcjjpepiglcicgpc/1/agent-observation-2.json
  (PNG browser-00019.png, SHA-256
  af7e9524110ed26fceb8e6deff6023fe2595614fd6542e3ec6feef9939abcdd0).
- PRD definition: Peekly source worktree, docs/PRD.md line 68.
- Current visible copy: Peekly source worktree, src/components/ResultsTab.tsx
  line 196.

The 32-persona expansion executed the remaining distinct personas 017–032.
All 16 tasks reached operational completion, all 16 current evidence sets
validated, all owned browser contexts shut down, and the expansion gate passed.
No uncertain, queued, blocked or cancelled tasks remained. The 32 distinct
personas are 001–032; the four-persona recovery attempts are lineage and are
not counted as additional distinct personas.

The final 32-persona cohort has 32 operationally completed sessions and 32
valid evidence sessions. Model UX outcomes were 2 failed and 30 inconclusive,
with zero passed. Manual review shows the two failed judgments are not two
functional product defects: one is the copy mismatch above and the other
included a criterion for an import list the persona did not open.

Across the 4 → 16 → 32 progression and the isolated four-persona recovery:

- 32 distinct personas; 4, 12, 4 recovery, then 16 newly executed sessions.
- 379 accepted model decisions from 401 dispatch attempts; 22 failed attempts
  (14 timeouts with unknown token usage, 8 response/criterion rejections).
- 2,667,049 input tokens and 210,680 output tokens with provider usage.
- 314 admitted browser tool actions; 0 HTTP 429 responses.
- Requested model was TOKENMAXX/deepseek-v4.1-flash-free only. Served name
  was deepseek-v4.1-flash when returned. No fallback model was used.
- Policy cost is USD 0 under the user's free-route authorization. Provider
  reported cost and billing_source were null on all 401 attempts; this is not
  an independently verified invoice.

Signals across the 32 distinct personas:

- Result summary outside viewport after import: 29/32.
- Manual import disclosure initially outside viewport: 32/32.
- First searching the More tab for an import action: 20/32.
- Post-import Instagram connection prompt: 31/32 (expected PRD behavior).
- “받은 파일 바로 넣기” shortcut visible in the wizard request step: 31/32
  (functionally navigates to step 3; not a defect).

The final evidence index is evidence-index-32.json. It contains the final
32-persona observation anchors, including rehashed screenshots and logs.

Machine-readable aggregate execution and usage details are in
run-summary-32.json. It includes the 4, 16-initial, 16-recovery and 32 stages;
401 dispatch attempts are distinct from 379 accepted model decisions.
The final 32-stage run had eight timeouts and one truncated/invalid JSON
judgment response; all were contained within retry/attempt bounds, and the
stage still ended with 16/16 operationally complete tasks and no uncertain
or queued work. Token usage for timed-out requests is unknown, not zero.
