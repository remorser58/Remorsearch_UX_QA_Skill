# Implementation validation before actual coverage runs

Source revision: `125b7325ed60cdafa52546fee39492cb0279a3ce`.
Date: 2026-11-15 Asia/Seoul. No persona/model run had started during these checks.

| Check | Command | Result |
| --- | --- | --- |
| Whole unit suite and packaging | `PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 scripts/check_release.py --output dist/peekly-completion-check-20261115` | Checker exit 1, package ready false for the Node gate described below. Unit discovery: 1,834 tests, 1,813 passed, 21 optional skips, 0 failures, 229.570 s; unit subprocess exit 0. |
| Prepared optional agent runtime | `PYTHONDONTWRITEBYTECODE=1 REMORSEARCH_REQUIRE_AGENT_RUNTIME=1 .ux-loop/peekly-agent-venv/bin/python -m unittest discover -s tests -p 'test_agent_execution.py'` | 25 passed, 0 skipped, exit 0. |
| Loop smoke | `PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 skills/remorsearch-ux-qa/scripts/smoke_loop.py` | 18 expected command outcomes matched, passed true, exit 0, live integrations false. |
| Research fixture | `PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 skills/remorsearch-ux-qa/examples/research/run_fixture.py` | Passed true, exit 0, network requests 0, synthetic content. |
| Completion launcher preflight | `PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 scripts/run_peekly_completion.py smoke --check-only` | Offline preflight passed; 32 old queues, 327 forbidden old job IDs, 39 historical uncertain rows protected. |
| Local target | `curl -fsS --max-time 5 http://127.0.0.1:4174/ \| shasum -a 256` | Served index SHA matched fixed product build: 848b334a6affa5c6a578911819aaf127da34bc2e6ae2f04899022872b7d0f6f5. |

The release checker passed 18 of its 20 entries, including unit tests, release-file checks, bundle build and integrity, extracted CLI/reference/synthetic journeys, current-source match and stable validation inputs. Its Node-version entry failed because the default Node is 24.21.0 and the packaged Playwright driver gate requires Node 22. The prepared Playwright web-driver entry was therefore skipped. This is an incomplete packaging/browser gate, not a passing release check.

The authorized Peekly live runs use the existing owned CDP runner and its explicit Node executable (`/Users/m4mini/.aside/runtime/bin/node`, v26.5.0). The new real two-person smoke must independently establish that runner's seed, UI and coverage behavior. No installed skill was changed or release published.

## Durable evidence

- `dist/peekly-completion-check-20261115/validation.json` SHA-256: `16523077c669bc71b3ead33cbd8536a83a97014a0c51cd2a935413d64b654a33`.
- `dist/peekly-completion-check-20261115/logs/unit-tests.log` SHA-256: `0b6454f628c4f6ebbc0ae5740fa21a02faa422229c871b44d486845f7d5e949a`.
- `.ux-loop/peekly-completion-integration-20261115.log` contains compact checker results.
- Source stayed byte-identical throughout comprehensive validation. Later status/report documentation does not change runtime input hashes.
- Offline native product load/migration and helper tests are not evidence of live not_run reduction.
