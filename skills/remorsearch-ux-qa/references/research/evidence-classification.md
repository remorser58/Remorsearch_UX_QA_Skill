# Evidence Classification

## Evidence types

### Firsthand experience

The person describes what they tried, what the system did, and what happened next.

Strong for reconstructing task flow and friction.

### Repeated independent experience

Different people describe a similar situation without copying one another.

Count independence in three units (`references/source-grading.md`):

- per person: a salted author key, or one thread on anonymous boards;
- per channel family: one kind of channel, such as blogs, forums and communities, Q&A boards, video comments, app-store reviews, microblogs, or shopping and place reviews (`commerce_reviews`);
- per organisation: the registrable domain, with Korean second-level suffixes such as `co.kr` and `go.kr`. Blogs hosted by path or subdomain count per author.

Identical text counts once. Korean examples:

- `blog.naver.com/alice` and `blog.naver.com/bob` are two people in one channel family (blogs), not one voice from `naver.com`.
- `alice.tistory.com` and a Naver blog author are two people, still in one channel family (blogs).
- A Naver blog author and an App Store reviewer are two people in two channel families.
- Five anonymous replies in one DCInside thread are one unit.

Strong for forming a structural UX hypothesis. It still does not establish population prevalence.

### Quantitative evidence

Usage, error, conversion, support, search, or retention data.

Strong for scale and trend. It usually needs qualitative evidence to explain cause.

### Official product evidence

Help pages, policies, release notes, design systems, accessibility guidance, and product documentation.

Strong for intended behavior and constraints. It does not prove that users understand or accept the behavior.

### Promotion or incentive-driven content

Sponsored reviews, affiliate posts, event entries (including reviews written for a review event, 리뷰 이벤트), coordinated campaigns, repeated marketing language, and competitive attacks.

Useful for identifying messaging and perception. Weak as direct evidence of ordinary user experience. The caps are in `references/source-grading.md`, section 4:

- A confirmed promotion or affiliate disclosure caps the source at grade D, so it never counts toward a claim.
- A confirmed review-event incentive caps satisfaction, preference, counter-search use and star averages at D. A complaint or a workaround in the same review keeps its voice grade minus at most one step, and never drops below C because of the incentive.
- A seller's notice of a review event is a per-review candidate, never a cap on the whole page. Platform-wide review points are kept apart from seller-run events.
- A review of a platform's own-brand item, on that platform, needs corroboration from another channel family.
- A disclosed virtual person (an AI-generated persona, AI 가상인물) is not a user's voice: grade E.

A word alone is not a disclosure. A review that complains "광고가 너무 많다" (too many ads in the app) or "체험단 후기만 잔뜩이다" is a user complaint, not promotion. The reader flags complete disclosure and label forms only (the lists are in `uxresearch/data/markers.json`). Its flags are candidates that a verifier confirms before a cap applies. The Korean disclosure rules, how they changed over time, and worked examples are in `references/research/korea/promotion.md`.

### Lead

A search snippet, a teaser, or a summarising fetch: a tool that returns model-written text about a page instead of the page. A lead points to a source; it is not evidence. Read the source itself through the reader before quoting or grading it. Leads are graded at most D and never support a claim.

### Inference

An interpretation created by connecting multiple observations.

Useful for UX hypotheses. Always label it as inference and list the supporting evidence.

## Confidence rubric

The levels below explain what confidence means. In a research run the level is computed, not chosen: `ux_research.py gate` (planned) grades each source for each claim kind and computes each claim's status (`references/source-grading.md`). High corresponds to `supported_high`, medium to `supported_medium`, low to `single_voice` or `lead_only`, and blocked to `conflicting`, `stale`, `needs_product_check` or evidence behind a stop. Never write a status into a bundle by hand.

### High

- firsthand evidence appears across independent channels;
- the same friction is visible in the product or workflow;
- the user and task are identifiable;
- there is no strong contradictory evidence.

### Medium

- repeated firsthand evidence exists;
- the structural cause is plausible;
- behavioral or product verification is missing.

### Low

- a single post or comment;
- vague emotional language;
- sarcasm or irony that the thread does not resolve;
- one narrow community;
- unclear user context;
- a proposed cause without a reproduced situation.

### Blocked

- the relevant source is private or inaccessible, or its host's terms restrict automated collection (`terms_restricted`);
- the product state cannot be reproduced;
- sources disagree in a way that changes the recommendation;
- current evidence is too old for the claim.

## Source hygiene

- Keep source URLs and dates in the bundle: `source_ref`, `published_at` and `observed_at`. Reports shared outside the team cite community sources by channel, date and source ID, not by URL.
- Keep the smallest quote that preserves meaning: at most 300 characters, and at most 5 excerpts per source.
- Never store handles, display names, profile links, IPs (including partial IPs such as `(118.235)`), contact details or ID numbers. `read` and `ingest` scrub them from page text before the agent sees it; never restore a placeholder such as `[phone]`. Authors become salted keys (`ux_research.py author-key`), and `merge` (planned) checks excerpts against the scrubbed text.
- A default nickname such as ㅇㅇ on an anonymous board, or a nickname shown with a partial IP, is not an identity. Count those posts by thread.
- A community's modelled gender, age or political lean is never attributed to a poster, a claim or a persona.
- Items read through an official API, such as YouTube comments, carry `retention_until` and are deleted by then. Never record a protected attribute against their author keys.
- Health, disability and age details appear only in segment-level claims. Communities centred on health, disability, older adults or minors get paraphrase only in shared outputs.
- Skip content from apparent minors.
- Temporary page text lives outside the project at mode 0600 and is deleted at close or after 72 h.
- A post found removed on re-check marks its source `deleted` and drops its excerpt.
- Member-only content from a community the user authorised for signed-in reading appears in shared outputs as an authored summary only, with no member's personal data (`references/public-page-access.md`).
- Never merge multiple users into one invented persona.
- Never turn a paraphrase into a quotation.
- Never use a search snippet as if it were the full source.
