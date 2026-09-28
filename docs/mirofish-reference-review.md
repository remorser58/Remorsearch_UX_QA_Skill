# MiroFish and related persona-simulation projects: reference review

Reviewed 2026-09-28 for the ergonomic persona swarm. Only public GitHub pages and
READMEs could be fetched from this environment; dates and star counts below are
from those pages unless marked secondary. No code from these projects is copied
into this repository.

## Answer to "the Chinese open-source persona simulation from about a year ago"

| Project | Origin | Released / notable | What it does | Relevance |
| --- | --- | --- | --- | --- |
| **MiroFish** (666ghj/MiroFish) | Guo Hangjiang (BUPT student), incubated by Shanda Group | v0.1.0 2025-12-22; GitHub global trending #1 around 2026-03-07 (secondary); ~75.2k stars, 11.6k forks on 2026-09-28; AGPL-3.0 | Seed text → GraphRAG graph (Zep) → LLM-written personas → parallel Twitter-like and Reddit-like simulations on OASIS → ReportAgent → chat/interview agents | Most likely the project meant. Architectural reference only: no UI, no screen operation, no published prediction validation. |
| **BettaFish** (微舆, 666ghj/BettaFish) | Same author | Trending #1 on 2025-11-02 (~20k stars in a week, secondary); GPL-2.0 | Multi-agent public-opinion analysis that crawls real platforms (Weibo, Xiaohongshu, Douyin) | Fits "about a year ago" best, but it analyses real posts; it is not persona simulation. |
| **OASIS** (camel-ai/oasis) | CAMEL-AI with Shanghai AI Laboratory and others | 2024-11-19 (arXiv 2411.11581); ~5.2k stars; Apache-2.0 | Up to 1M LLM agents on simulated X/Reddit; 21–23 social actions; Interview action (2025-06) | The engine under MiroFish. Agents herd more than humans, more so at larger scale (secondary). |
| AgentSociety | Tsinghua FIB Lab | 2025-02 (arXiv 2502.08691) | 10k+ agents with needs/emotions in a simulated city | Social science simulation, not UI QA. |
| SocioVerse (众生) | Fudan DISC lab | 2025-04 (arXiv 2504.10157); 215 stars | 10M real-user pool for survey-style "silicon samples" | Simulation code still "coming soon"; survey-style only. |
| YuLan-OneSim | Renmin University | 2025-05 | No-code social simulator | Social simulation. |
| Persona Hub | Tencent AI Lab | 2024-06 | 1B synthetic personas for data generation | Persona source, not a simulator. |
| UXAgent / AgentA/B (non-Chinese) | Northeastern, Amazon | 2025-02 / 2025-04 | LLM agents browse web pages as personas for usability/A-B tests | Closest to UI QA; reads simplified page structure, evaluated by 5 researchers; A/B agreement was direction-only. |
| TinyTroupe (non-Chinese) | Microsoft | 2024-11 | Persona simulation for business insights | Conversation/focus-group style. |

## What MiroFish does that matters here

- Personas are invented by an LLM from entities in the seed graph (age, gender,
  MBTI, bio, "memories"), not sampled from a population.
- Simulated posts are written back into the same knowledge graph as source
  facts; provenance survives only in metadata.
- The report prompt frames the output as "a rehearsal of the future"; no
  backtests or accuracy benchmarks are published, and the official FAQ says
  accuracy is not guaranteed. Critics (2026-03) point to plausibility vs accuracy
  and LLM herd bias.
- Impersonator sites exist (the FAQ names mirofish.ai as official and several
  other domains as unofficial).

## What this repository adopts and rejects

Adopted (structure): seed → many personas → parallel agents with memory →
shared record → report agent → interviews with individual agents.

Rejected (claims and data handling):

- Agents operate the real product surface, not a simulated platform.
- Ergonomics are computed by models; agents do not role-play bodies or senses.
- Ergonomic attributes are declared assumptions; persona datasets (for example
  Nemotron-Personas-Korea, CC BY 4.0, ages 19–99, no ergonomic fields) only add
  narrative context with a recorded revision.
- Counts are coverage over simulated profiles; no prediction, prevalence,
  sentiment share or market claim.
- Simulated discourse is stored separately, labelled in its text, and never
  written back into evidence.
- The report agent may only cite run/observation/finding IDs.

Detailed validity review: `docs/human-factors/llm-persona-simulation-validity.md`.
