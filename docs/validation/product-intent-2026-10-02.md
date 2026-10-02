# Product intent implementation verification — 2026-10-02

Implemented on the selected Mac mini (`REVOLAR_MINI`, user `m4mini`, macOS 27.2,
arm64) in a separate checkout. The existing working checkout was not edited.
Handoff: `078654ffdaa05994c2b34d264e59149d29102373` on
`codex/product-led-rem-20261002`. Authoritative PRD baseline:
`ad5b461dd592c84b857ee99a2fc35bfa4ed5d99e`.

## Behavior verified

- Provider conflict IDs/actors and generic `code_write` grants cannot approve an
  intent change. Separate operator decisions bind the context ID/hash, goal,
  exact fix digest and constraint/conflict, with dated reference and reason.
  Application receipts retain the preceding decision IDs.
- No-edit runs and unchanged goal constraints require fresh intent review.
  Each scoped scenario needs its own replay row. Inspected path mappings bind
  files to scenarios; unmapped changed paths conservatively affect all scenarios.
- Malformed context/review types and dates stop with controlled results. Invalid
  persisted decision ledgers fail contract validation before further writes.
- `improve` requires context through the existing `uxloop` engine. Legacy packets
  remain usable and explicitly report that intent was not checked. Goal/context
  bindings remain immutable on resume.
- A conflicting patch can be deferred while an independently applicable reviewed
  patch proceeds. Full-tree before/after revision checks remain mandatory. A
  later approval cannot silently rebase a deferred patch; after a sibling write,
  a new reviewed goal/checkpoint may be necessary.
- Installed instructions and CLI/provider references describe these fields and
  limits. No reading limits were increased. Stale component-anchor/README tests
  and the quoted skill-description scalar from the draft were corrected.

## Executed checks

Python 3.12.14 and Node 22.23.3 used the existing dependencies and Playwright
browsers on the Mac. Tests requiring loopback fixture servers ran with that
access after initial sandbox-denial logs were preserved.

| Check | Result | Log under artifact root |
| --- | --- | --- |
| Initial handoff intent tests | 9 tests; 5 failures, 1 error retained | `initial/handoff-focused.log` |
| Final focused intent suite | 23 tests passed, including negative subcases | `final/intent-focused.log` |
| Final aggregate Python suite | 982 tests passed, no skips; includes existing loop, distribution, reading and reference tests | `final/python-all.log` |
| Handoff reproductions | 15 cases matched expected outcomes; no tracebacks | `final/reproductions.log`, `final/*repro-r1.json`, `final/reproduce-r1.json` |
| Web driver suite | 559 checks passed, 0 failed | `final/web-selftest.log` |
| Retained gaze/typography group | 21 checks passed, including captured-font Python analysis | `final/web-captures.log` |
| Retained painted-state group | 20 checks passed; captures also fed final Python suite | `final/web-painted.log`, `final/browser-captures/` |
| Relocated installation | 7 checks passed; 228 files; integrity, help, bounded reference, loop/research smoke, required-context rejection and explicit-decision patch | `final/relocated-results.json`, `final/relocated.log` |
| Reading/distribution/reference selection | 73 tests passed; limits unchanged | `final/instruction-distribution-reference.log` |
| Distribution file scan | 225 source release files accepted | `final/release-files.log` |

Artifact root on the selected Mac is the checkout's sibling `rem-validation/`
in `/Users/m4mini/Documents/Codex/2026-10-02/task/`. Original supplied r1 logs,
initial local failure logs and intermediate failed verification logs are retained.
The relocated skill payload was written directly; no archive is delivered.
Source hashes and the final delivery SHA are recorded in the local evidence.

## Limits

All loop browser/Figma receipts in these checks are explicitly synthetic fixture
records. Local browser captures exercise synthetic HTML. Every fixture report
keeps `product_complete: false`; these results do not establish actual product
improvement completion, human accuracy or real Figma changes. No real external
accounts, messages, payments, Figma files or global settings were changed.

The shared-browser endpoint handshake group was not exercised because no
`REMORSEARCH_BROWSER_WS` endpoint was configured. Python captured-font analysis
and the capture-dependent Python test were subsequently exercised with retained
local captures. A live URL-to-improvement run with real project/Figma evidence
and current access to the six candidate platforms remains outside this test.

The CLI validates imported records and hashes, not independent authenticity or
human identity. Existing Figma, permissions, same-scenario and adjacent-regression
gates remain in force; it does not launch browsers, collect research, edit Figma,
rebuild, deploy or schedule work itself.

The existing PR #1 targets a different head branch. This handoff branch has no
automatic push-triggered CI under the current workflow (push is limited to main).
Final delivery checks must query check runs and workflow runs at the pushed SHA;
absence of runs is a CI limitation, not a CI pass. The PR is left unchanged.
