# Local release candidate

The distribution installs one `remorsearch-ux-qa/` folder with exactly one
discoverable `SKILL.md`. The engine, workflows, discovery metadata and scripts
keep their normal paths. The original insane-search toolkit is included under
`references/insane-search/`; its SKILL.md is retained unchanged as `SOURCE.md`.
Both the repository-folder installation and the release ZIP include the toolkit.
Users need no separate search-skill installation.

## Build and verify

Use Python 3.10+ on macOS, Linux or WSL. Run from this repository. The default
input is the checked-in toolkit; no network or installed-skill lookup is needed.

```sh
python3 scripts/build_insane_search_bundle.py --output dist/remorsearch-rc
python3 scripts/build_insane_search_bundle.py --verify dist/remorsearch-rc
python3 dist/remorsearch-rc/remorsearch-ux-qa/scripts/remorsearch.py smoke
```

The output contains the installable `remorsearch-ux-qa/` tree and
`remorsearch-ux-qa.zip`. SHA-256 receipts record the original inputs and shipped
content. Identical inputs produce identical ZIP bytes. Verification detects
missing, changed and extra files; it is an integrity check, not a publisher signature.

Maintainers may explicitly replace the toolkit with an existing local input:

```sh
python3 scripts/build_insane_search_bundle.py --base-skill /path/to/insane-search --output dist/remorsearch-custom
```

This option reads the input without changing it. The output keeps Remorsearch as
the installed skill and records whether the input matches the checked-in snapshot.
It retains supplied licenses and does not assign the upstream license to
unrelated or independently modified input.

After extracting the ZIP elsewhere, use the launcher's absolute path from any
working directory:

```sh
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py paths
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py verify
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py research --help
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py ref references/insane-search/SOURCE.md phase-0-특수-엔드포인트-인덱스
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py ref references/insane-search/references/public-api.md stack-exchange-v23
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py smoke
```

An omitted section ID lists headings only. The two reference commands above
load the source index body and an actual linked platform method body.

## Complete local check

Prepare the web driver's pinned dependencies and Chromium using Node.js 22:

```sh
(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium)
python3 scripts/check_release.py --output dist/release-check
```

The checker runs the Python suite, release-file checks, the offline build,
tree/ZIP verification, extraction, relocated CLI and reference reads, both
synthetic smoke workflows, and the Chromium driver selftest from the extracted
installation. It copies already prepared driver dependencies into that disposable
installation and performs no downloads or install hooks. It verifies package
integrity again after the browser test and compares the candidate with current
inputs. `validation.json` records each check and its log.

The extracted installation also runs `examples/journey/run_fixture.py`. This
starts from an empty directory, prepares three reviewed sample files, reuses two
pre-authored PRD hypotheses, invokes actual local Python adapters and verifies
current report/readback with the original Library preserved. Expected product
verdicts are one failed and one inconclusive; the diagnostic passes only when
those known synthetic outcomes are reported honestly. It is not a browser or
real-user check. Existing diagnostic output is never overwritten.

The same extracted launcher also runs the `--research` variant in a separate
new directory. It exercises the existing offline research input, real merge,
gate, authored export, persistent Library import, reviewed research scope,
current adapter execution and report/readback. Original research bytes, modes
and modification times remain unchanged. Its live-mode contract fields and
source grades belong to invented diagnostic inputs, not actual acquisition or
user evidence. Both original and research diagnostics retain zero product passes.

The browser gate also runs the pure bridge/owned-upload contract tests and the extracted
`examples/journey/run_browser_fixture.py --research` diagnostic. It reuses the
prepared Node 22 / Playwright 1.56.1 / Chromium runtime, starts owned headless
sessions over reviewed synthetic static bytes, and admits native checkpoints,
logs and PNGs through the real saved-persona receipt/audit path. The intentional
input-loss task must fail while the normal control passes. Earlier failure
survives final recovery, and repeated readback preserves the report and originals
without another dispatch. This is actual browser execution of an authored
diagnostic, not actual-user evidence, Peekly QA or measured UX improvement.

Actual Peekly UI validation has a separate frozen protocol and fresh-build
provenance under benchmarks/peekly-headless-pilot. It uses owned synthetic
archives, the existing Chromium headless shell and the frozen macOS network-denial
launcher. The release checker does not rebuild or rerun that product experiment;
its contract and packaging tests must remain distinguishable from product results.

The output must be a new directory. Failed checks return nonzero. `--skip-web`
produces a partial report with `ready: false`. Synthetic tests establish local
behavior and packaging; live community access, real-user preferences, Figma access
and accessibility certification remain outside this check.

## Research and distribution boundary

Research plans its questions and discovers candidate URLs, then loads the bundled
search source and appropriate linked method for acquisition. Every selected method
follows Remorsearch's access, provenance and privacy controls. Supported captures
enter the existing reader/ingest checks; unsupported output remains a lead.
A site/run stop stays final across every toolkit method.

The build excludes dependencies, caches, local run state and internal handoff
records. It preserves Remorsearch's MIT license and third-party notices.
`references/insane-search/PROVENANCE.json` records the attributed original snapshot.
The installed original contained no license. The separately retrieved
[upstream MIT license](https://github.com/fivetaku/insane-search/blob/main/LICENSE)
is retained verbatim as `references/insane-search/upstream-LICENSE` and in the
repository at `integrations/insane-search/upstream-LICENSE`. Its retrieval date is
2026-10-02 (Asia/Seoul). Local hash matches prove byte identity with the recorded
snapshot; they do not prove current upstream authenticity or confer rights on a
different maintainer input.

These commands create local artifacts. Publishing, pushing commits and changing
installed skills are separate actions. Internal source-checkout records are
excluded from the distribution.
