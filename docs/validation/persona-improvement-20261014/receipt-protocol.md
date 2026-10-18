# Same-recording analysis-receipt ablation

Fixed before either reviewer starts. This is a separate diagnostic experiment after the live operator pilot, not a replacement for its incomplete coverage or a broad full-skill comparison.

Question: on the same completed browser recording, does exposing the existing deterministic analyzer's finish artifacts help a fresh reviewer find more supported issues without adding unsupported/false positives?

Use exactly the original old-arm P1-page1 recording (22 executed steps, Galaxy S24, AP-01), its images/state/run receipts, the same product brief, and a one-profile wrapper preserving the original composed profile. Copy these to a neutral directory. No new UI interaction, page source or key access for either reviewer. One fresh native qa-reviewer per condition, same configured model/effort, 15minutes including reading and report-only closeout afterwards. Same concise rubric and output structure. No skill instructions or previous findings are provided. Control receives the raw recording; assisted additionally receives the existing analyzer's raw findings/analysis/report. Both can inspect original artifacts but cannot invoke other analyzers or inspect code/keys.

Adjudicate anonymously against frozen source/key and own cited evidence. Count unique seeded issues on this recorded variant (12 total), supported extras, unsupported/false positives and unsupported physical/condition claims. Deduplicate repeated elements/profile observations. Stronger supported coverage with no increase in unsupported/false positives is the bounded success criterion. Report all negative results, time and available token counters. One case and one reviewer per condition cannot establish generalization, real-user benefit or dollar-cost savings. This tests artifact exposure, not actual live automatic-hook operation; the hook requires separate real driver acceptance checks.

The analyzer and underlying rules are unchanged by the metadata export repair. There is no new execution harness, new product fixture, altered key or tuned threshold. Exact source/copy hashes and prompts are retained.
