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

Research papers, standards and guidelines cited in the references (for example
WCAG 2.2, ISO 9241 and human-factors studies) are cited, not reproduced.
