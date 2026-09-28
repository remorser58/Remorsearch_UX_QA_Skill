"""Heuristic visual-attention (gaze priority) model for a screenshot + elements.

Model ``gaze-priority-v2`` (docs/human-factors/gaze-visual-attention.md). It is a
population-level PRIORITY model, not an eye tracker, and it is not validated
against eye-tracking data in this repository. It combines:

1. bottom-up conspicuity from the screenshot (Itti-Koch style centre-surround
   contrast on luminance and two colour-opponent channels on a coarse grid);
2. a layout position prior fitted to reported GUI eye-tracking tendencies:
   upper-left pull for every UI type in UEyes (CHI 2023) and Leiva et al.
   (MobileHCI 2020), left-half dominance on desktop web (NN/g 2010/2017), a
   two-band pattern for desktop apps; TV has no dataset (assumption);
3. element cues (size, text weight/size, contrast; text matters more than colour
   for mobile UIs per Leiva et al.);
4. a Monte Carlo scanpath: fixations are sampled with a distance penalty in
   visual degrees, inhibition of return and a slight rightward/downward bias,
   yielding P(element fixated within the first k fixations).

Gutenberg and Z-patterns have no eye-tracking support and are not encoded.
Every observation produced from this module is ``inferred`` (basis ``model``).
"""

from __future__ import annotations

import math
import random
from typing import Any, Sequence

from .. import params

MODEL_ID = "gaze-priority-v2"

Grid = list[list[float]]

# Position priors: mixtures of anisotropic Gaussians on the unit square
# (weight, mu_x, mu_y, sigma_x, sigma_y). [policy] fitted by hand to the reported
# tendencies; refit from UEyes per-type mean fixation maps before relying on them.
PRIORS: dict[str, list[tuple[float, float, float, float, float]]] = {
    "mobile": [(1.0, 0.35, 0.25, 0.30, 0.30)],
    "web": [(1.0, 0.26, 0.30, 0.25, 0.35)],  # mu_x 0.26 reproduces the ~80 % left-half share
    "desktop": [(0.6, 0.50, 0.40, 0.25, 0.15), (0.4, 0.15, 0.12, 0.12, 0.10)],
    "tv": [(1.0, 0.50, 0.42, 0.25, 0.25)],  # [assumption] no TV/game dataset; poster-like
}


def prior_kind(form_factor: str, surface_kind: str = "web") -> str:
    if form_factor in ("phone", "foldable", "tablet", "handheld_console"):
        return "mobile"
    if form_factor == "tv":
        return "tv"
    return "web" if surface_kind == "web" else "desktop"


def _box_blur(grid: Grid, radius: int) -> Grid:
    h = len(grid)
    w = len(grid[0]) if h else 0
    if radius <= 0 or h == 0:
        return [row[:] for row in grid]
    sat = [[0.0] * (w + 1) for _ in range(h + 1)]
    for y in range(h):
        acc = 0.0
        for x in range(w):
            acc += grid[y][x]
            sat[y + 1][x + 1] = sat[y][x + 1] + acc
    out = [[0.0] * w for _ in range(h)]
    for y in range(h):
        y0, y1 = max(0, y - radius), min(h, y + radius + 1)
        for x in range(w):
            x0, x1 = max(0, x - radius), min(w, x + radius + 1)
            total = sat[y1][x1] - sat[y0][x1] - sat[y1][x0] + sat[y0][x0]
            out[y][x] = total / ((y1 - y0) * (x1 - x0))
    return out


def _normalise(grid: Grid) -> Grid:
    flat = [v for row in grid for v in row]
    if not flat:
        return grid
    lo, hi = min(flat), max(flat)
    if hi - lo < 1e-9:
        return [[0.0 for _ in row] for row in grid]
    scaled = [[(v - lo) / (hi - lo) for v in row] for row in grid]
    mean = sum(v for row in scaled for v in row) / len(flat)
    weight = (1.0 - mean) ** 2  # promote maps with few strong peaks (Itti-Koch)
    return [[v * weight for v in row] for row in scaled]


def conspicuity_map(pixels: Sequence[Sequence[tuple[float, float, float]]]) -> Grid:
    """Bottom-up conspicuity for a coarse RGB grid (values 0..255) -> [0, 1]."""
    h = len(pixels)
    w = len(pixels[0]) if h else 0
    if h == 0 or w == 0:
        return []
    lum = [[(0.299 * r + 0.587 * g + 0.114 * b) / 255.0 for (r, g, b) in row] for row in pixels]
    rg = [[(r - g) / 255.0 for (r, g, b) in row] for row in pixels]
    by = [[(b - (r + g) / 2.0) / 255.0 for (r, g, b) in row] for row in pixels]
    maps: list[Grid] = []
    for channel in (lum, rg, by):
        for centre_r, surround_r in params.GAZE_CENTRE_SURROUND_CELLS:
            c = _box_blur(channel, centre_r)
            s = _box_blur(channel, surround_r)
            maps.append(_normalise([[abs(c[y][x] - s[y][x]) for x in range(w)] for y in range(h)]))
    total = [[sum(m[y][x] for m in maps) for x in range(w)] for y in range(h)]
    flat_max = max(max(row) for row in total) or 1.0
    return [[v / flat_max for v in row] for row in total]


def position_prior(x_frac: float, y_frac: float, kind: str) -> float:
    """Layout prior (unnormalised, peak ~1) for a normalised position (0,0 = top-left)."""
    comps = PRIORS.get(kind, PRIORS["web"])
    return sum(w * math.exp(-(((x_frac - mx) ** 2) / (2 * sx * sx) + ((y_frac - my) ** 2) / (2 * sy * sy)))
               for w, mx, my, sx, sy in comps)


def prior_peak(kind: str) -> tuple[float, float]:
    comps = PRIORS.get(kind, PRIORS["web"])
    w, mx, my, _, _ = max(comps, key=lambda c: c[0])
    return mx, my


def element_cue(element: dict[str, Any]) -> float:
    """Attention cue from the element itself (size, text emphasis, contrast)."""
    box = element.get("box") or {}
    area = max(1.0, float(box.get("w", 0)) * float(box.get("h", 0)))
    size_term = min(1.0, math.log10(area) / 5.0)
    font = float(element.get("font_size_px") or 0)
    weight = float(element.get("font_weight") or 400)
    text_term = min(1.0, font / 32.0) * (1.25 if weight >= 600 else 1.0)
    if (element.get("text") or "").strip():
        text_term = max(text_term, 0.2)
    contrast = float(element.get("_contrast") or 0.0)
    contrast_term = min(1.0, max(0.0, (contrast - 1.0) / 6.0))
    fill_term = float(element.get("_fill_contrast") or 0.0)
    return (
        params.GAZE_CUE_WEIGHTS["size"] * size_term
        + params.GAZE_CUE_WEIGHTS["text"] * text_term
        + params.GAZE_CUE_WEIGHTS["contrast"] * contrast_term
        + params.GAZE_CUE_WEIGHTS["fill"] * min(1.0, fill_term)
    )


def element_priorities(
    elements: Sequence[dict[str, Any]],
    viewport: tuple[float, float],
    kind: str,
    conspicuity: Grid | None = None,
) -> dict[str, float]:
    """Priority in [0, 1] per element id (visible, in-viewport elements only)."""
    vw, vh = viewport
    scores: dict[str, float] = {}
    gh = len(conspicuity) if conspicuity else 0
    gw = len(conspicuity[0]) if gh else 0
    peak = max(position_prior(x / 20, y / 20, kind) for x in range(21) for y in range(21)) or 1.0
    for element in elements:
        box = element.get("box")
        if not box or not element.get("visible", True) or element.get("in_viewport") is False:
            continue
        x0, y0 = max(0.0, box["x"]), max(0.0, box["y"])
        x1, y1 = min(vw, box["x"] + box["w"]), min(vh, box["y"] + box["h"])
        if x1 <= x0 or y1 <= y0:
            continue
        cx, cy = (x0 + x1) / 2 / vw, (y0 + y1) / 2 / vh
        bottom_up = 0.0
        if gh and gw:
            gx0 = int(x0 / vw * gw)
            gx1 = max(gx0 + 1, int(math.ceil(x1 / vw * gw)))
            gy0 = int(y0 / vh * gh)
            gy1 = max(gy0 + 1, int(math.ceil(y1 / vh * gh)))
            cells = [conspicuity[y][x] for y in range(gy0, min(gy1, gh)) for x in range(gx0, min(gx1, gw))]
            if cells:
                cells.sort(reverse=True)
                top = cells[: max(1, len(cells) // 4)]
                bottom_up = sum(top) / len(top)
        prior = position_prior(cx, cy, kind) / peak
        cue = element_cue(element)
        w = params.GAZE_COMBINE_WEIGHTS
        penalty = params.GAZE_AD_PENALTY if "ad_like" in (element.get("roles") or []) else 1.0
        scores[element["id"]] = (w["bottom_up"] * bottom_up + w["prior"] * prior + w["cue"] * cue) * penalty
    if scores:
        hi = max(scores.values()) or 1.0
        scores = {k: v / hi for k, v in scores.items()}
    return scores


def fixation_probabilities(
    centres_css: dict[str, tuple[float, float]],
    priorities: dict[str, float],
    start_css: tuple[float, float],
    mm_per_css_px: float,
    viewing_distance_mm: float,
    n_runs: int | None = None,
    n_fix: int | None = None,
    seed: int = 1,
) -> dict[str, list[float]]:
    """Monte Carlo scanpaths -> P(element first fixated within k fixations), k=1..n_fix."""
    n_runs = n_runs or params.GAZE_MC_RUNS
    n_fix = n_fix or params.GAZE_MC_FIXATIONS
    rng = random.Random(seed)
    ids = [i for i in centres_css if i in priorities]
    hits = {i: [0] * n_fix for i in ids}
    if not ids:
        return {}
    for _ in range(n_runs):
        pos = start_css
        seen: set[str] = set()
        for k in range(n_fix):
            weights = []
            for i in ids:
                c = centres_css[i]
                ecc = eccentricity_deg_css(pos, c, mm_per_css_px, viewing_distance_mm)
                wgt = (max(priorities[i], 1e-6) ** params.GAZE_MC_GAMMA) * math.exp(-ecc / params.GAZE_MC_LAMBDA_DEG)
                if i in seen:
                    wgt *= params.GAZE_MC_IOR
                if c[0] > pos[0] or c[1] > pos[1]:
                    wgt *= 1.0 + params.GAZE_MC_DIR_BIAS
                weights.append(wgt)
            total = sum(weights)
            pick = rng.random() * total
            acc = 0.0
            chosen = ids[-1]
            for i, wgt in zip(ids, weights):
                acc += wgt
                if acc >= pick:
                    chosen = i
                    break
            if chosen not in seen:
                for kk in range(k, n_fix):
                    hits[chosen][kk] += 1
            seen.add(chosen)
            pos = centres_css[chosen]
    return {i: [h / n_runs for h in hits[i]] for i in ids}


def predicted_scanpath(
    elements: Sequence[dict[str, Any]],
    priorities: dict[str, float],
    viewport: tuple[float, float],
    start: tuple[float, float] | None = None,
    max_fixations: int = 12,
) -> list[str]:
    """Deterministic greedy scanpath (for reports/heatmaps; checks use the Monte Carlo)."""
    by_id = {e["id"]: e for e in elements if e.get("id") in priorities}
    remaining = dict(priorities)
    vw, vh = viewport
    diag = math.hypot(vw, vh) or 1.0
    pos = start
    path: list[str] = []
    while remaining and len(path) < max_fixations:
        best_id, best_val = None, -1.0
        for element_id, value in remaining.items():
            box = by_id[element_id]["box"]
            cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
            if pos is not None:
                value = value * math.exp(-params.GAZE_SACCADE_DISCOUNT * math.hypot(cx - pos[0], cy - pos[1]) / diag)
            if value > best_val:
                best_id, best_val = element_id, value
        assert best_id is not None
        path.append(best_id)
        box = by_id[best_id]["box"]
        pos = (box["x"] + box["w"] / 2, box["y"] + box["h"] / 2)
        remaining.pop(best_id)
    return path


def eccentricity_deg_css(a: tuple[float, float], b: tuple[float, float], mm_per_css_px: float, viewing_distance_mm: float) -> float:
    d_mm = math.hypot(a[0] - b[0], a[1] - b[1]) * mm_per_css_px
    return math.degrees(math.atan2(d_mm, viewing_distance_mm))


def eccentricity_deg(point_a_mm: tuple[float, float], point_b_mm: tuple[float, float], viewing_distance_mm: float) -> float:
    """Angular separation (degrees) between two points on the display plane."""
    d = math.hypot(point_a_mm[0] - point_b_mm[0], point_a_mm[1] - point_b_mm[1])
    return math.degrees(math.atan2(d, viewing_distance_mm))


def notice_band(theta_deg: float, salient: bool, persona_scale: float = 1.0) -> str:
    """Feedback-noticing band: likely / uncertain / likely_missed ([policy] bands)."""
    likely, uncertain = params.NOTICE_BANDS_DEG["salient" if salient else "non_salient"]
    likely *= persona_scale
    uncertain *= persona_scale
    if theta_deg <= likely:
        return "likely"
    if theta_deg <= uncertain:
        return "uncertain"
    return "likely_missed"
