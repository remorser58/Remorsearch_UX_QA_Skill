# Third-party notices

Remorsearch UX QA is released under the MIT License (`LICENSE`). This file lists
material from other projects that is included in this folder, and projects that
were studied or can be used alongside it without any of their code being included.

## Included material

### Colour vision deficiency matrices (colour-science)

`ergoqa/hf/machado_data.py` contains the colour vision deficiency simulation
matrices of Machado, Oliveira and Fernandes, tabulated per severity, transcribed
from the colour-science package (`colour/blindness/datasets/machado2010.py`).

- Source model: Machado, G. M., Oliveira, M. M. and Fernandes, L. A. F. (2009).
  "A Physiologically-based Model for Simulation of Color Vision Deficiency".
  IEEE Transactions on Visualization and Computer Graphics 15(6), 1291-1298.
- Transcribed from: colour-science, https://github.com/colour-science/colour

```text
BSD 3-Clause License

Copyright 2013 Colour Developers

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## Installed separately by the user (not included)

- **Playwright** (Apache License 2.0) and its Chromium build, installed with
  `npm install` in `drivers/web/` for the live web driver.
- **Aside** (optional browser research tool), installed and licensed by its own
  distributor.
- Other browser tools that an agent host provides, such as Claude in Chrome,
  Playwright MCP or Chrome DevTools MCP, are used through the host. They are not
  part of this folder.

## Studied as references only (no code included)

- **MiroFish** (github.com/666ghj/MiroFish, AGPL-3.0): the ergonomics mode borrows
  the structure of seed → personas → parallel agents → report → interviews. No
  MiroFish code is used.
- **OASIS** (camel-ai/oasis, Apache-2.0): the social simulation engine under
  MiroFish; reviewed, not used.
- **OMO** (sisyphuslabs/omo): its goal, checkpoint and continuation design was
  inspected for the loop mode; no OMO code or installation is redistributed.
- **Nemotron-Personas-Korea** (NVIDIA, CC BY 4.0): persona records may be linked
  at run time by the user; no dataset rows are included in this folder.
- **insane-search** (github.com/fivetaku/insane-search, part of the gptaku-plugins
  collection, MIT License, Copyright (c) 2026 fivetaku). Ideas used in the
  public-page reader (`scripts/ux_research.py`, `uxresearch/`) and
  `references/research/public-page-access.md`: official routes first, with
  cheapest-first escalation; graded verdicts, because HTTP 200 is not success;
  honest reporting of untried routes; an SSRF guard that re-checks every redirect;
  an untrusted-content envelope for page text; and the rule that generic code
  names no sites. We deliberately did not adopt its TLS-impersonation grid,
  stealth browsers, cookie and clearance bridging, search-page scraping or archive
  sidecars. Nothing in this folder calls, installs or depends on it.
- **insane-research** (github.com/fivetaku/insane-research, MIT License, Copyright
  (c) 2026 fivetaku). Ideas used in `references/research/audience-pipeline.md` and
  `references/research/source-grading.md`: phase contracts; claim status computed
  by a gate with a data-flow lock; independence counting; the EXPAND lead loop;
  schema-forced reader returns merged by code; and a report gate with an annex. We
  changed its grading, so grades depend on the claim kind, and its unit of
  independence, so people count and not only organisations.
- **K-skill** (github.com/NomaDamas/k-skill, MIT License at the repository root;
  its AGPL-3.0-only proxy packages were not used). Studied from 2026-09-28 to
  2026-09-30. Ideas used in the Korean research pack
  (`references/research/korea/`), in the reader's key handling (`uxresearch/`) and
  in the README:
  - a dated per-source registry: the official surface, the route, the
    authentication, the licence and the date it was observed;
  - the missing-credential rule: a missing key is recorded as a gap and a question
    to the user, and the reader never switches to another route;
  - namespaced key names, here `REMORSEARCH_<SERVICE>_<ITEM>`;
  - provenance cards for official statistics: publisher, table, reference period,
    unit, address and retrieval date;
  - the staged order for retrieving statistics from KOSIS: find the table, read
    its metadata, pull a small slice, then widen (from its kosis-stats skill);
  - a detect-only mode and a review threshold at a 30% change ratio for the
    Korean prose check (from its korean-humanizer document, which credits
    github.com/epoko77-ai/im-not-ai, MIT License; that project's README was read
    on 2026-09-30);
  - a capability table with a requirements column in the README;
  - "Done when" and "Failure modes" sections in each reference, and natural Korean
    requests as triggers.

  We deliberately did not adopt its hosted proxy with operator-held keys,
  instructions loaded at run time, reading of search-result pages or undocumented
  endpoints.
- **DaleSeo/korean-skills** (github.com/DaleSeo/korean-skills, MIT License).
  Ideas: the register follows the document type, and translationese patterns (for
  example ~에 대해, ~를 통해) form a lint category. The pattern list in
  `references/research/korea/report-template.md` is our own.
- **SoDam-Persona-Codex** (github.com/sodam-ai/SoDam-Persona-Codex, Apache License
  2.0). Ideas: Korean cue words that change how deep a run goes, and the 미확인
  label for statements that were not verified.
- **gptaku_plugins** (github.com/fivetaku/gptaku_plugins, MIT License; the
  collection that also holds insane-search and insane-research). Idea: the
  bilingual README pattern, an English README, a README.ko.md with the same section
  skeleton, and a language switcher line at the top.

No code, text, marker lists, word lists or tables from the projects above are
included in this folder, and the skill does not depend on, install or call any of
them.

## Cited or read for facts (nothing reproduced)

- Research papers, standards and guidelines cited in the references (for example
  WCAG 2.2, ISO 9241, RFC 9309, the TDM Reservation Protocol and human-factors
  studies) are cited, not reproduced.
- The Korean pack (`references/research/korea/`,
  `references/persona-qa/kwcag-2.2.md`) cites KWCAG 2.2 (KS X OT0003:2022), the
  Korea Fair Trade Commission's guidelines on endorsements and testimonials,
  guides of the Personal Information Protection Commission, official statistics
  and surveys, and statutes, administrative rules and judgments as read in the
  public legalize-kr mirrors (github.com/legalize-kr). Each is cited with its
  version or date, and marked 미확인 where it was not compared with the primary
  source. None of it is legal advice.
- Field names, limits and error codes of the KOSIS OpenAPI were read in two
  third-party documents (github.com/WooilJeong/PublicDataReader and
  github.com/rubatoyd/kosis-openapi-mcp). No text or code from them is included.
- Platform, agency and company names in the Korean pack are descriptive. There is
  no affiliation with any of them.
