"""Game-play timing and photosensitivity models.

References: REF-wcag22 (2.3.1 Three Flashes or Below Threshold; general flash
definition), REF-itu-bt1702 (broadcast flash guidance), REF-xag (Xbox
Accessibility Guidelines), REF-der-deary2006 (reaction time by age).

Flash detection here is a screening heuristic on sampled frames. It is not a
certified Harding/PEAT analysis; a failure is a reason to run a certified tool,
and a pass is not a certification.
"""

from __future__ import annotations

import math
from typing import Sequence

from .. import params


def count_general_flashes(samples: Sequence[dict], window_ms: float = 1000.0) -> dict:
    """Count WCAG-style general flashes in a luminance time series.

    ``samples`` are ``{"t_ms": float, "mean_luminance": 0..1, "changed_fraction": 0..1}``
    (changed_fraction = share of the viewport whose luminance changed by >10 %
    since the previous frame). A *transition* is a change in relative luminance
    of at least 10 % of the maximum where the darker state is below 0.80; a flash
    is a pair of opposing transitions. Returns the maximum number of flashes in
    any window and the maximum changed area during those transitions.
    """
    pts = sorted((float(s["t_ms"]), float(s["mean_luminance"]), float(s.get("changed_fraction", 1.0))) for s in samples)
    transitions: list[tuple[float, int, float]] = []  # (t, direction, area)
    if len(pts) < 2:
        return {"max_flashes_per_window": 0.0, "max_area_fraction": 0.0, "transitions": 0}
    ref_t, ref_l, _ = pts[0]
    last_dir = 0
    for t, lum, area in pts[1:]:
        delta = lum - ref_l
        darker = min(lum, ref_l)
        if abs(delta) >= params.FLASH_DELTA and darker < params.FLASH_DARK_LIMIT:
            direction = 1 if delta > 0 else -1
            if direction != last_dir:
                transitions.append((t, direction, area))
                last_dir = direction
            ref_t, ref_l = t, lum
        elif (delta > 0 and last_dir == 1) or (delta < 0 and last_dir == -1):
            # Keep tracking the extreme of the current excursion.
            ref_t, ref_l = t, lum
    max_flashes = 0.0
    max_area = 0.0
    max_extended = 0.0
    for i, (t0, _, _) in enumerate(transitions):
        in_window = [tr for tr in transitions[i:] if tr[0] - t0 <= window_ms]
        flashes = len(in_window) / 2.0
        if flashes > max_flashes:
            max_flashes = flashes
            max_area = max((tr[2] for tr in in_window), default=0.0)
        in_long = [tr for tr in transitions[i:] if tr[0] - t0 <= params.FLASH_EXTENDED_WINDOW_MS]
        max_extended = max(max_extended, len(in_long) / 2.0)
    return {"max_flashes_per_window": max_flashes, "max_area_fraction": max_area, "transitions": len(transitions),
            "max_flashes_per_5s": max_extended,
            "extended": max_extended >= params.FLASH_EXTENDED_MIN_FLASHES}


def viewport_solid_angle_sr(display_w_mm: float, display_h_mm: float, viewing_distance_mm: float) -> float:
    """Approximate solid angle of a rectangular display centred on the line of sight."""
    a = display_w_mm / 2.0
    b = display_h_mm / 2.0
    d = viewing_distance_mm
    return 4.0 * math.asin((a * b) / math.sqrt((a * a + d * d) * (b * b + d * d)))


def flash_area_exceeds(changed_fraction: float, display_w_mm: float, display_h_mm: float, viewing_distance_mm: float) -> bool:
    """True when the flashing area exceeds WCAG's 0.006 sr combined-area threshold.

    Assumes the changed area is contiguous; the solid angle is approximated as the
    changed fraction of the display's solid angle.
    """
    return changed_fraction * viewport_solid_angle_sr(display_w_mm, display_h_mm, viewing_distance_mm) > params.FLASH_AREA_SR


def timing_window_margin_ms(window_ms: float, reaction_ms: float, input_latency_ms: float, motor_ms: float | None = None) -> float:
    """Remaining slack after perceiving, deciding, moving and system latency."""
    motor = params.QTE_MOTOR_MS if motor_ms is None else motor_ms
    return window_ms - (reaction_ms + motor + input_latency_ms)


def reaction_time_quantile_ms(mean_ms: float, sd_ms: float, quantile: float = 0.95) -> float:
    """Upper quantile of reaction time assuming a log-normal distribution."""
    if mean_ms <= 0 or sd_ms <= 0:
        return mean_ms
    sigma2 = math.log(1 + (sd_ms / mean_ms) ** 2)
    mu = math.log(mean_ms) - sigma2 / 2
    z = {0.5: 0.0, 0.9: 1.2816, 0.95: 1.6449, 0.99: 2.3263}.get(quantile, 1.6449)
    return math.exp(mu + z * math.sqrt(sigma2))
