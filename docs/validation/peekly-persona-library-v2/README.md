# Peekly persona library v2.0.0

Created 2026-11-13 on Mac mini because the previous MacBook-only library.json was unavailable offline. This is a new, versioned PRD-hypothesis library, not a recovery, copy, or regeneration of the earlier MacBook library. No original profile history or identity is claimed.

- Product source: insta-tracker at commit 58214441; current docs/PRD.md SHA-256: 5c18b75a9e4c5d31a1b8b45df60818a2391ea464d4010d976b94a0e908a6bb2d.
- Persona source: 32 newly authored synthetic task profiles, IDs PER-PEEKLY-V2-001 through PER-PEEKLY-V2-032.
- Provenance: prd_hypothesis. All claim_ids are empty. Public evidence records in public-research-evidence-v2.json motivate test hypotheses only; they do not establish user prevalence or product defects.
- Prior branch assets: reuses the committed Peekly headless journey protocol and sampleData.ts fixture-generation recipe. No ready-made persona library.json or committed binary ZIP fixture was found in the candidate remote branches.
- The persistent local library is stored outside the installed skill tree at .ux-loop/peekly-persona-library-v2/library.json; the reproducible input and public evidence remain in this versioned directory.
- Scope: sample-first entry, direct import, JSON/HTML and ZIP handling, missing/incorrect files, progress/cancellation, relation categories, two-snapshot comparison, privacy, retention and free/paid boundary.
- Safety: no Instagram login, cookies, account access, real personal data, social actions, or external data transmission. All browser uploads use synthetic fixtures.

## Versioned artifacts

- Exported Library snapshot: library-v2.json (SHA-256 ebb839c4fe2a37eb61c6b2d01484876f986498b489466d3ed971d0fbc1dd6cf1)
- Synthetic fixture manifest: fixtures/fixture-manifest.json (SHA-256 92620658e3364b0c963c1a956e473370fe3ffb1a519fddbffc73255c8e8517de)
- ZIP fixtures: peekly-sample-previous.zip (011a8bfa98d42741c24f586f3db88795b9b70c8445ab989e9cb059b669802871), peekly-sample-current.zip (1c0c3ec2ab70e6bcd98b69356f00128bb7163116988c6ab03f4674212c772e47)
- Regeneration: run generate-fixtures.mjs with the separate insta-tracker worktree as --product-root and a new, empty --output directory. The builder uses only src/core/sampleData.ts and the repository-pinned TypeScript/fflate dependencies.
- Runtime ZIP fixtures remain only in the private .ux-loop folder (mode 0700 directory, mode 0600 files). The repository commits the deterministic generator and hash manifest, not fixture contents.
