# Evidence Bundle Contract

This contract is shared by the research and QA skills. It makes provenance explicit without turning a research bundle into a claim that the sample is representative.

The copies in `references/research/` and `references/persona-qa/` are identical. Change both together.

## Permission record

```json
{
  "permissions": {
    "requested": ["read_only", "design_write"],
    "granted": ["read_only"],
    "blocked": [
      {"capability": "design_write", "reason": "No Figma write approval for this run"}
    ]
  }
}
```

Allowed capabilities are `read_only`, `design_write`, `test_data_write`, and `code_write`. A blocked capability stays blocked even when a proposal recommends that action.

## Record graph

The top-level `records` object contains arrays named `sources`, `evidence`, `claims`, `personas`, `scenarios`, `runs`, `observations`, `findings`, `proposals`, and `figma`. Every record has a unique `id`.

```text
source → evidence → claim
persona → scenario → run → observation → finding → proposal
figma → finding or proposal
```

Use `source_id`, `evidence_ids`, `persona_id`, `scenario_id`, `run_id`, `observation_ids`, `finding_ids`, and `figma_id` for the links. A missing link is a validation error.

## Epistemic status

Every evidence item, claim, observation, and finding uses `epistemic_status`:

- `observed`: directly captured from a source or the product surface;
- `inferred`: reasoned from observed material;
- `unknown`: not established by the available evidence.

Use `verification_status: "verified"` only when the required observed support exists. Inference can guide a hypothesis and a next test. It cannot be the only support for a verified claim or finding.

## Source policy

Every source records `channel`, `source_ref`, `access_basis`, `access_method`, `public_scope`, and `retention_status`. Keep `withdrawn`, `deleted`, and `redacted` states visible. A withdrawn or deleted source must not continue to support a verified claim.

- `access_basis`: research runs use `public_anonymous`, `public_teaser`, `official_api`, `team_provided`, `fixture` or `authorised_member`. Older bundles may say `public`.
- `access_method`: the tool that read the page, such as `ux_research_read`, `aside`, `claude_in_chrome`, `claude_app_browser`, `playwright_mcp`, `chrome_devtools_mcp`, `drivers_web`, `web_search`, `web_fetch` or `team_export` (`references/research/public-page-access.md`, section 16).
- In shared outputs, a source with `access_basis: authorised_member` carries an authored summary only: no excerpt, no post URL and no member's personal data.

Optional fields for research sources:

| Field | Content |
| --- | --- |
| `source_type` | An `ergo-audience.v1` source type (`official_statistics`, `product_analytics`, `app_store_reviews`, `community`, `survey`, `interview`, `usability_test`, `support_tickets`, `official_docs`, `competitor`, `market_report`, `research_paper`, `product_brief`, `expert_judgment`), or `news`, `llm_output` or `synthetic` |
| `access` | `{rung, presentation, verdict, stop_class, fetch_id, fetched_at, content_sha256, robots, context, engine_version}`, copied from the reader's run ledger |
| `published_at`, `observed_at`, `valid_at` | When the author published, when the reader read it, and when the content was true |
| `platform_family`, `org` | The channel family and the organisation used to count independence |
| `author_key`, `thread_key` | Salted keys from the run. Never a handle or a name. |
| `promo_flags`, `injection_flags` | Promotion or affiliate disclosures, and injection signals |

Values in the `access` block:

- `rung`: `R0` to `R4` for pages that were read; `search_snippet` or `summarizing_fetch` for leads;
- `presentation`: `official_route`, `honest_ua`, `site_alternate`, `real_browser` or `browser_equivalent_tls`;
- `verdict`: `ok_strong`, `ok_weak`, `suspect`, `js_shell`, `js_check` or `bot_filter`;
- `stop_class`: `none`, or one of `opted_out`, `gone`, `auth_gate`, `paywall`, `human_check`, `rate_limit`, `geo_block`, `legal_block`, `budget`, `host_stopped`;
- `robots`: the robots.txt decision for the path (`allowed` or `disallowed`) and the file's status (`ok`, `unavailable`, `unavailable_bot_filtered` or `unreachable`);
- `context`: `anonymous`, `unknown` or `signed_in`.

## Claims

- `claim_kind` uses the kinds in `references/research/source-grading.md`: `segment_exists`, `segment_share`, `device_mix`, `condition_presence`, `condition_share`, `context_of_use`, `task`, `pain_point`, `workaround`, `product_behavior`, `intended_behavior`, and the population kinds `prevalence`, `user_preference`, `real_user_preference` and `discomfort`.
- Optional fields: `segment_hint`, `counter_search` `{query, lang, tool, read_source_ids, summary, outcome, resolution}`, `counter_evidence_ids`, `context_evidence_ids`, `about_current_version`, and `observation_ids`.
- For research claims, `verification_status` is written only by `ux_research.py gate --write-bundle` (planned). Evidence that did not count toward the status moves to `context_evidence_ids`, so every `evidence_ids` entry of a verified claim is eligible support.

## Synthetic persona boundary

Synthetic personas require an adapter revision, schema fingerprint, seed, shard or config, maximum rows or bytes, timeout, selected record IDs, filled and unfilled strata, stop reason, `original_attributes`, and `scenario_assumptions`. Keep original attributes separate from assumptions added for a test. Synthetic personas produce bounded scenarios; they do not support claims about real-user preference, prevalence, or discomfort.

A persona composed from an audience file keeps `basis: "synthetic"` and adds `audience_ref` `{audience_id, segment_id, facet, claim_ids}`. The reference explains where the test condition came from. It never turns the persona into evidence about real users.

## Findings

A finding may carry `segments_affected`: an array of segment IDs whose composed personas triggered it. It names segments, never the share of users affected.

## Validator checks for the new fields

`scripts/validate_bundle.py` will add these checks (planned). Each applies only when its field is present, so existing bundles keep passing:

- `sources[].access` has the shape and values listed above;
- a verified claim cannot rely on a source that hit a stop, on a lead (`search_snippet` or `summarizing_fetch`), or on an `llm_output` or `synthetic` source;
- a verified `segment_share`, `condition_share`, `device_mix` or `prevalence` claim needs evidence whose `evidence_type` is `quantitative` or `statistic`;
- a persona with `audience_ref` must have `basis: "synthetic"`, and every ID in its `claim_ids` must exist;
- `segments_affected` must be an array of strings.

One separate tightening is also planned: a verified `product_behavior` claim needs `observation_ids` that link observed observations from completed runs.

## Loop intake

The loop's intake rejects excerpt and raw text fields. Run `ux_research.py minimize` (planned) first: it removes them and keeps authored summaries.

## Figma comparison

When comparing implementation with Figma, record `file_key`, `branch_key`, `baseline_version`, `node_ids`, `read_at`, `readback_artifact_ref`, and `design_status`. Classify the difference as `implementation_defect`, `design_defect`, `spec_conflict`, or `approved_deviation`. A baseline and readback version conflict keeps comparison unverified until resolved.
