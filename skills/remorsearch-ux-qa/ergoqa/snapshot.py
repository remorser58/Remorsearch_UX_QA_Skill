"""Validation and loading for ergo-snapshot/run/scenario/profile v1 documents.

Validators return a list of human-readable error strings (empty = valid) and
fail closed: wrong types, unknown enum values and unknown ``schema_version`` are
errors. Unknown extra keys are tolerated so drivers can attach native metadata
(e.g. ``native`` on Android elements) without a schema bump.

``load_run_dir`` resolves screenshot paths inside the run directory only
(no absolute paths, ``..``, or symlinks) and, by default, verifies that each
declared screenshot exists and matches its declared SHA-256 and PNG dimensions.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence

SNAPSHOT_SCHEMA = "ergo-snapshot.v1"
RUN_SCHEMA = "ergo-run.v1"
SCENARIO_SCHEMA = "ergo-scenario.v1"
PROFILE_SCHEMA = "ergo-profile.v1"

SURFACE_KINDS = ("web", "android", "ios", "desktop", "game")
ROLES = ("primary", "destructive", "irreversible", "critical_message", "error_message", "status",
         "navigation", "ad_like", "hud", "game_control", "timed")
ELEMENT_SOURCES = ("dom", "uiautomator", "a11y", "vision", "manual")
ORIENTATIONS = ("portrait", "landscape")
ACTIONS = ("tap", "click", "double_tap", "long_press", "swipe", "drag", "type", "press",
           "scroll", "wait", "snapshot", "gamepad")
TARGETED_ACTIONS = ("tap", "click", "double_tap", "long_press")
RUN_MODES = ("scripted", "interactive")
RUN_STATUSES = ("completed", "failed", "blocked")
STEP_RESULTS = ("ok", "error", "no_target")
PROFILE_ORIGINS = ("stratified_coverage", "base_rate_sample", "manual")
AGE_BANDS = ("10s", "20s", "30s", "40s", "50s", "60s", "70s+")
HANDEDNESS = ("right", "left", "mixed")
GRIPS = ("one_hand_right", "one_hand_left", "cradle_right", "cradle_left", "two_thumbs",
         "mouse_right", "mouse_left", "keyboard_only", "gamepad", "remote")
MAX_JSON_BYTES = 8 * 1024 * 1024
_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")
_SHA256 = re.compile(r"[0-9a-f]{64}")


class SnapshotError(ValueError):
    """Invalid ergo document, unsafe path or evidence mismatch."""


# --------------------------------------------------------------------------- primitives

def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _timestamp_ok(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


class _Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, path: str, message: str) -> None:
        self.items.append(f"{path}: {message}")

    def require(self, cond: bool, path: str, message: str) -> bool:
        if not cond:
            self.add(path, message)
        return cond

    def string(self, obj: dict, key: str, path: str, *, required: bool = True, nullable: bool = False,
               nonempty: bool = True) -> None:
        if key not in obj:
            if required:
                self.add(f"{path}.{key}", "is required")
            return
        value = obj[key]
        if value is None and nullable:
            return
        ok = _nonempty_str(value) if nonempty else isinstance(value, str)
        self.require(ok, f"{path}.{key}", "must be a non-empty string" if nonempty else "must be a string")

    def enum(self, obj: dict, key: str, allowed: Sequence[str], path: str, *, required: bool = True,
             nullable: bool = False) -> None:
        if key not in obj:
            if required:
                self.add(f"{path}.{key}", "is required")
            return
        value = obj[key]
        if value is None and nullable:
            return
        self.require(value in allowed, f"{path}.{key}", f"must be one of {list(allowed)} (got {value!r})")

    def number(self, obj: dict, key: str, path: str, *, required: bool = True, nullable: bool = False,
               minimum: float | None = None, maximum: float | None = None, integer: bool = False) -> None:
        if key not in obj:
            if required:
                self.add(f"{path}.{key}", "is required")
            return
        value = obj[key]
        if value is None and nullable:
            return
        ok = _is_int(value) if integer else is_number(value)
        if not ok:
            self.add(f"{path}.{key}", "must be an integer" if integer else "must be a finite number")
            return
        if minimum is not None and value < minimum:
            self.add(f"{path}.{key}", f"must be >= {minimum}")
        if maximum is not None and value > maximum:
            self.add(f"{path}.{key}", f"must be <= {maximum}")

    def boolean(self, obj: dict, key: str, path: str, *, required: bool = True, nullable: bool = False) -> None:
        if key not in obj:
            if required:
                self.add(f"{path}.{key}", "is required")
            return
        value = obj[key]
        if value is None and nullable:
            return
        self.require(isinstance(value, bool), f"{path}.{key}", "must be a boolean")

    def obj(self, parent: dict, key: str, path: str, *, required: bool = True, nullable: bool = False) -> dict | None:
        if key not in parent:
            if required:
                self.add(f"{path}.{key}", "is required")
            return None
        value = parent[key]
        if value is None and nullable:
            return None
        if not isinstance(value, dict):
            self.add(f"{path}.{key}", "must be an object")
            return None
        return value

    def array(self, parent: dict, key: str, path: str, *, required: bool = True) -> list | None:
        if key not in parent:
            if required:
                self.add(f"{path}.{key}", "is required")
            return None
        value = parent[key]
        if not isinstance(value, list):
            self.add(f"{path}.{key}", "must be an array")
            return None
        return value

    def timestamp(self, obj: dict, key: str, path: str, *, required: bool = True, nullable: bool = False) -> None:
        if key not in obj:
            if required:
                self.add(f"{path}.{key}", "is required")
            return
        value = obj[key]
        if value is None and nullable:
            return
        self.require(_timestamp_ok(value), f"{path}.{key}", "must be an ISO-8601 timestamp with timezone")


def _schema(doc: Any, expected: str, errors: _Errors) -> bool:
    if not isinstance(doc, dict):
        errors.add("$", "document must be a JSON object")
        return False
    version = doc.get("schema_version")
    if version != expected:
        errors.add("$.schema_version", f"must be {expected!r} (got {version!r}); unknown versions are rejected")
        return False
    return True


def _box(errors: _Errors, box: Any, path: str) -> None:
    if not isinstance(box, dict):
        errors.add(path, "must be an object {x, y, w, h}")
        return
    for key in ("x", "y"):
        errors.number(box, key, path)
    for key in ("w", "h"):
        errors.number(box, key, path, minimum=0)


def _point(errors: _Errors, point: Any, path: str) -> None:
    if not isinstance(point, dict):
        errors.add(path, "must be an object {x, y}")
        return
    errors.number(point, "x", path)
    errors.number(point, "y", path)


def _color(errors: _Errors, obj: dict, key: str, path: str) -> None:
    if key not in obj or obj[key] is None:
        return
    errors.require(isinstance(obj[key], str) and bool(_HEX.fullmatch(obj[key])), f"{path}.{key}",
                   "must be a hex colour (#rgb, #rrggbb or #rrggbbaa) or null")


def _roles(errors: _Errors, value: Any, path: str) -> None:
    if not isinstance(value, list):
        errors.add(path, "must be an array")
        return
    for i, role in enumerate(value):
        errors.require(role in ROLES, f"{path}[{i}]", f"unknown role {role!r}; allowed {list(ROLES)}")


def safe_relative_path(value: Any) -> bool:
    """True for a portable relative path without traversal, drive letters or backslashes."""
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    p = PurePosixPath(value)
    return not p.is_absolute() and all(part not in ("", ".", "..") for part in value.split("/"))


# --------------------------------------------------------------------------- snapshot

def _device_block(errors: _Errors, device: dict | None, path: str) -> None:
    if device is None:
        return
    errors.string(device, "id", path)
    vp = device.get("viewport_css")
    errors.require(isinstance(vp, list) and len(vp) == 2 and all(is_number(v) and v > 0 for v in vp),
                   f"{path}.viewport_css", "must be [width, height] positive numbers")
    errors.number(device, "dpr", path, minimum=0.1)
    errors.enum(device, "orientation", ORIENTATIONS, path)


def _element(errors: _Errors, el: Any, path: str) -> None:
    if not isinstance(el, dict):
        errors.add(path, "must be an object")
        return
    errors.string(el, "id", path)
    errors.string(el, "role", path)
    errors.string(el, "name", path, required=False, nullable=True, nonempty=False)
    for key in ("text", "tag", "selector"):
        errors.string(el, key, path, required=False, nullable=True, nonempty=False)
    _box(errors, el.get("box"), f"{path}.box")
    for key in ("interactive", "visible"):
        errors.boolean(el, key, path)
    for key in ("enabled", "in_viewport"):
        errors.boolean(el, key, path, required=False)
    errors.number(el, "font_size_px", path, required=False, nullable=True, minimum=0)
    errors.number(el, "font_weight", path, required=False, nullable=True, minimum=1, maximum=1000)
    for key in ("color_fg", "color_bg", "border_color"):
        _color(errors, el, key, path)
    _roles(errors, el.get("roles"), f"{path}.roles")
    errors.enum(el, "source", ELEMENT_SOURCES, path)


def validate_snapshot(doc: Any) -> list[str]:
    errors = _Errors()
    if not _schema(doc, SNAPSHOT_SCHEMA, errors):
        return errors.items
    errors.string(doc, "snapshot_id", "$")
    errors.string(doc, "run_id", "$")
    errors.number(doc, "step_index", "$", integer=True, minimum=0)
    errors.timestamp(doc, "captured_at", "$")
    surface = errors.obj(doc, "surface", "$")
    if surface is not None:
        errors.enum(surface, "kind", SURFACE_KINDS, "$.surface")
        for key in ("url", "title", "app_id"):
            errors.string(surface, key, "$.surface", required=False, nullable=True, nonempty=False)
    _device_block(errors, errors.obj(doc, "device", "$"), "$.device")
    shot = errors.obj(doc, "screenshot", "$")
    if shot is not None:
        errors.require(safe_relative_path(shot.get("path")), "$.screenshot.path",
                       "must be a safe relative path (no absolute path, '..' or backslash)")
        sha = shot.get("sha256")
        errors.require(sha is None or (isinstance(sha, str) and bool(_SHA256.fullmatch(sha))),
                       "$.screenshot.sha256", "must be 64 lowercase hex characters or null")
        errors.number(shot, "width_px", "$.screenshot", integer=True, minimum=1)
        errors.number(shot, "height_px", "$.screenshot", integer=True, minimum=1)
    elements = errors.array(doc, "elements", "$")
    if elements is not None:
        seen: set[str] = set()
        for i, el in enumerate(elements):
            _element(errors, el, f"$.elements[{i}]")
            if isinstance(el, dict) and isinstance(el.get("id"), str):
                errors.require(el["id"] not in seen, f"$.elements[{i}].id", f"duplicate element id {el['id']!r}")
                seen.add(el["id"])
    if "focus_point" not in doc:
        errors.add("$.focus_point", "is required (null on the first snapshot)")
    elif doc["focus_point"] is not None:
        _point(errors, doc["focus_point"], "$.focus_point")
    console = errors.array(doc, "console_errors", "$", required=False)
    if console is not None:
        for i, item in enumerate(console):
            errors.require(isinstance(item, (str, dict)), f"$.console_errors[{i}]", "must be a string or object")
    notes = errors.array(doc, "notes", "$", required=False)
    if notes is not None:
        for i, item in enumerate(notes):
            errors.require(isinstance(item, str), f"$.notes[{i}]", "must be a string")
    return errors.items


# --------------------------------------------------------------------------- run

def validate_run(doc: Any) -> list[str]:
    errors = _Errors()
    if not _schema(doc, RUN_SCHEMA, errors):
        return errors.items
    for key in ("run_id", "scenario_id", "profile_id"):
        errors.string(doc, key, "$")
    driver = errors.obj(doc, "driver", "$")
    if driver is not None:
        errors.string(driver, "name", "$.driver")
        for key in ("version", "browser"):
            errors.string(driver, key, "$.driver", required=False, nullable=True)
    _device_block(errors, errors.obj(doc, "device", "$"), "$.device")
    errors.enum(doc, "mode", RUN_MODES, "$")
    errors.timestamp(doc, "started_at", "$")
    errors.timestamp(doc, "ended_at", "$", nullable=doc.get("status") != "completed")
    if _timestamp_ok(doc.get("started_at")) and _timestamp_ok(doc.get("ended_at")):
        start = datetime.fromisoformat(doc["started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(doc["ended_at"].replace("Z", "+00:00"))
        errors.require(end >= start, "$.ended_at", "must be >= started_at")
    errors.enum(doc, "status", RUN_STATUSES, "$")
    errors.boolean(doc, "success", "$", nullable=True)
    steps = errors.array(doc, "steps", "$")
    for i, step in enumerate(steps or []):
        path = f"$.steps[{i}]"
        if not isinstance(step, dict):
            errors.add(path, "must be an object")
            continue
        errors.number(step, "step_index", path, integer=True, minimum=0)
        action = errors.obj(step, "action", path)
        if action is not None:
            errors.enum(action, "action", ACTIONS, f"{path}.action")
        errors.string(step, "target_element_id", path, required=False, nullable=True)
        if step.get("point") is not None:
            _point(errors, step["point"], f"{path}.point")
        for key in ("before", "after"):
            errors.string(step, key, path, required=False, nullable=True)
        for key in ("t_start_ms", "t_end_ms", "feedback_latency_ms"):
            errors.number(step, key, path, required=False, nullable=True, minimum=0)
        if is_number(step.get("t_start_ms")) and is_number(step.get("t_end_ms")):
            errors.require(step["t_end_ms"] >= step["t_start_ms"], f"{path}.t_end_ms", "must be >= t_start_ms")
        errors.enum(step, "result", STEP_RESULTS, path)
        errors.string(step, "error", path, required=False, nullable=True, nonempty=False)
    for i, window in enumerate(errors.array(doc, "timing_windows", "$", required=False) or []):
        path = f"$.timing_windows[{i}]"
        if not isinstance(window, dict):
            errors.add(path, "must be an object")
            continue
        errors.string(window, "id", path)
        errors.number(window, "visible_ms", path, nullable=True, minimum=0)
    for i, sample in enumerate(errors.array(doc, "flash_samples", "$", required=False) or []):
        path = f"$.flash_samples[{i}]"
        if not isinstance(sample, dict):
            errors.add(path, "must be an object")
            continue
        errors.number(sample, "t_ms", path, minimum=0)
        errors.number(sample, "mean_luminance", path, minimum=0, maximum=1)
    for i, note in enumerate(errors.array(doc, "persona_notes", "$", required=False) or []):
        path = f"$.persona_notes[{i}]"
        if not isinstance(note, dict):
            errors.add(path, "must be an object")
            continue
        errors.number(note, "step_index", path, integer=True, minimum=0)
        for key in ("intent", "expected", "observed"):
            errors.string(note, key, path, nonempty=False)
        errors.boolean(note, "confusion", path)
    return errors.items


# --------------------------------------------------------------------------- scenario

def _target(errors: _Errors, target: Any, path: str, hotspot_ids: set[str]) -> None:
    if isinstance(target, str):
        if not errors.require(target.strip() != "", path, "must be a non-empty selector"):
            return
        if target.startswith("hotspot:"):
            errors.require(target[len("hotspot:"):] in hotspot_ids, path, f"unknown hotspot {target!r}")
    elif isinstance(target, dict):
        _point(errors, target, path)
    else:
        errors.add(path, "must be a selector string, 'hotspot:<id>' or {x, y}")


def validate_scenario(doc: Any) -> list[str]:
    errors = _Errors()
    if not _schema(doc, SCENARIO_SCHEMA, errors):
        return errors.items
    errors.string(doc, "scenario_id", "$")
    surface = errors.obj(doc, "surface", "$")
    if surface is not None:
        errors.enum(surface, "kind", SURFACE_KINDS, "$.surface")
        errors.string(surface, "url", "$.surface", required=surface.get("kind") == "web", nullable=surface.get("kind") != "web")
        errors.string(surface, "app_id", "$.surface", required=False, nullable=True)
    errors.string(doc, "task_goal_ko", "$")
    device_ids = errors.array(doc, "device_ids", "$")
    if device_ids is not None:
        errors.require(len(device_ids) > 0, "$.device_ids", "must list at least one device")
        for i, dev in enumerate(device_ids):
            errors.require(_nonempty_str(dev), f"$.device_ids[{i}]", "must be a non-empty string")
    hotspot_ids: set[str] = set()
    for i, spot in enumerate(errors.array(doc, "hotspots", "$", required=False) or []):
        path = f"$.hotspots[{i}]"
        if not isinstance(spot, dict):
            errors.add(path, "must be an object")
            continue
        errors.string(spot, "id", path)
        errors.string(spot, "name", path, required=False, nonempty=False)
        _box(errors, spot.get("box"), f"{path}.box")
        _roles(errors, spot.get("roles", []), f"{path}.roles")
        if isinstance(spot.get("id"), str):
            errors.require(spot["id"] not in hotspot_ids, f"{path}.id", "duplicate hotspot id")
            hotspot_ids.add(spot["id"])
    targets = errors.obj(doc, "targets", "$", required=False)
    for role, selectors in (targets or {}).items():
        path = f"$.targets.{role}"
        errors.require(role in ROLES, path, f"unknown role; allowed {list(ROLES)}")
        if not isinstance(selectors, list):
            errors.add(path, "must be an array of selectors")
            continue
        for i, sel in enumerate(selectors):
            if isinstance(sel, str):
                _target(errors, sel, f"{path}[{i}]", hotspot_ids)
            else:
                errors.add(f"{path}[{i}]", "must be a selector string")
    steps = errors.array(doc, "steps", "$")
    for i, step in enumerate(steps or []):
        path = f"$.steps[{i}]"
        if not isinstance(step, dict):
            errors.add(path, "must be an object")
            continue
        errors.enum(step, "action", ACTIONS, path)
        action = step.get("action")
        if action in TARGETED_ACTIONS or "target" in step:
            if "target" not in step:
                errors.add(f"{path}.target", f"is required for {action}")
            else:
                _target(errors, step["target"], f"{path}.target", hotspot_ids)
        errors.number(step, "ms", path, required=action == "wait", minimum=0)
        errors.string(step, "text", path, required=action == "type", nonempty=False)
        errors.string(step, "key", path, required=action == "press")
        if "to" in step:
            _target(errors, step["to"], f"{path}.to", hotspot_ids)
    for i, window in enumerate(errors.array(doc, "timing_windows", "$", required=False) or []):
        path = f"$.timing_windows[{i}]"
        if not isinstance(window, dict):
            errors.add(path, "must be an object")
            continue
        errors.string(window, "id", path)
        errors.string(window, "selector", path)
        errors.string(window, "measure", path)
    success = errors.obj(doc, "success", "$", required=False, nullable=True)
    if success is not None:
        errors.require(len(success) > 0, "$.success", "must declare at least one success condition")
    return errors.items


# --------------------------------------------------------------------------- profile

def validate_profile(doc: Any, *, known_device_ids: Iterable[str] | None = None) -> list[str]:
    """Structural check of ergo-profile.v1 (ergoqa.profiles owns generation)."""
    errors = _Errors()
    if not _schema(doc, PROFILE_SCHEMA, errors):
        return errors.items
    errors.string(doc, "profile_id", "$")
    errors.enum(doc, "origin", PROFILE_ORIGINS, "$")
    ref = errors.obj(doc, "persona_ref", "$", required=False, nullable=True)
    if ref is not None:
        for key in ("dataset", "revision", "record_id"):
            errors.string(ref, key, "$.persona_ref")
    errors.string(doc, "label_ko", "$", required=False, nonempty=False)
    attrs = errors.obj(doc, "attributes", "$")
    if attrs is not None:
        p = "$.attributes"
        errors.enum(attrs, "age_band", AGE_BANDS, p)
        errors.enum(attrs, "handedness", HANDEDNESS, p)
        errors.enum(attrs, "grip", GRIPS, p)
        errors.number(attrs, "thumb_length_mm", p, minimum=1)
        errors.number(attrs, "hand_percentile", p, minimum=0, maximum=100)
        errors.string(attrs, "device_id", p)
        if known_device_ids is None:
            from .devices import list_devices
            known_device_ids = [d.id for d in list_devices()]
        known = set(known_device_ids)
        if isinstance(attrs.get("device_id"), str):
            errors.require(attrs["device_id"] in known, f"{p}.device_id", f"unknown device {attrs['device_id']!r}")
        errors.enum(attrs, "orientation", ORIENTATIONS, p)
        vision = errors.obj(attrs, "vision", p)
        if vision is not None:
            errors.enum(vision, "acuity", ("normal", "reduced", "low"), f"{p}.vision")
            errors.boolean(vision, "presbyopia", f"{p}.vision")
            errors.enum(vision, "cvd", ("none", "protan", "deutan", "tritan"), f"{p}.vision")
            errors.number(vision, "cvd_severity", f"{p}.vision", minimum=0, maximum=1)
            errors.number(vision, "viewing_distance_mm", f"{p}.vision", minimum=0)
        motor = errors.obj(attrs, "motor", p)
        if motor is not None:
            errors.enum(motor, "tremor", ("none", "mild", "moderate"), f"{p}.motor")
            errors.number(motor, "touch_sigma_mm", f"{p}.motor", minimum=0)
        context = errors.obj(attrs, "context", p)
        if context is not None:
            errors.enum(context, "mobility", ("seated", "walking", "transit"), f"{p}.context")
            errors.enum(context, "lighting", ("indoor", "bright_sun", "dark"), f"{p}.context")
            errors.number(context, "free_hands", f"{p}.context", integer=True, minimum=0, maximum=2)
            errors.boolean(context, "interruptions", f"{p}.context")
        cognition = errors.obj(attrs, "cognition", p)
        if cognition is not None:
            errors.enum(cognition, "familiarity", ("first_use", "returning", "expert"), f"{p}.cognition")
            errors.enum(cognition, "time_pressure", ("low", "high"), f"{p}.cognition")
            errors.number(cognition, "reading_wpm_ko", f"{p}.cognition", minimum=0)
        errors.number(attrs, "reaction_time_ms", p, minimum=0)
    fields = errors.array(doc, "assumption_fields", "$")
    for i, name in enumerate(fields or []):
        errors.require(_nonempty_str(name), f"$.assumption_fields[{i}]", "must be a non-empty string")
    refs = errors.obj(doc, "base_rate_refs", "$", required=False)
    for key, value in (refs or {}).items():
        errors.require(isinstance(value, (str, list)), f"$.base_rate_refs.{key}", "must be a reference id string or list")
    return errors.items


VALIDATORS = {
    SNAPSHOT_SCHEMA: validate_snapshot,
    RUN_SCHEMA: validate_run,
    SCENARIO_SCHEMA: validate_scenario,
    PROFILE_SCHEMA: validate_profile,
}


def validate(doc: Any) -> list[str]:
    """Dispatch on ``schema_version``; unknown versions are errors."""
    if not isinstance(doc, dict):
        return ["$: document must be a JSON object"]
    validator = VALIDATORS.get(doc.get("schema_version"))
    if validator is None:
        return [f"$.schema_version: unknown schema_version {doc.get('schema_version')!r}"]
    return validator(doc)


# --------------------------------------------------------------------------- loading

def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(raw: str | bytes) -> Any:
    def bad_constant(value: str) -> None:
        raise SnapshotError(f"non-finite JSON number: {value}")
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=bad_constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, SnapshotError):
            raise
        raise SnapshotError(f"invalid JSON: {exc}") from exc


def load_json(path: str | Path) -> Any:
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise SnapshotError(f"not a regular file: {p}")
    if p.stat().st_size > MAX_JSON_BYTES:
        raise SnapshotError(f"JSON input exceeds {MAX_JSON_BYTES} bytes: {p}")
    return parse_json(p.read_bytes())


def load_document(path: str | Path, schema_version: str | None = None) -> dict:
    doc = load_json(path)
    if schema_version is not None and isinstance(doc, dict) and doc.get("schema_version") != schema_version:
        raise SnapshotError(f"{path}: expected {schema_version}, got {doc.get('schema_version')!r}")
    problems = validate(doc)
    if problems:
        raise SnapshotError(f"{path}: " + "; ".join(problems))
    return doc


def resolve_within(root: str | Path, relative: str) -> Path:
    """Join ``relative`` under ``root``; reject traversal, absolute paths and symlinks."""
    if not safe_relative_path(relative):
        raise SnapshotError(f"unsafe relative path: {relative!r}")
    base = Path(root).resolve()
    current = base
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink():
            raise SnapshotError(f"symlink not allowed: {relative!r}")
    if not current.resolve().is_relative_to(base):
        raise SnapshotError(f"path escapes run directory: {relative!r}")
    return current


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_screenshot(run_dir: Path, snapshot: dict) -> Path:
    from .png import PNGError, read_header

    shot = snapshot["screenshot"]
    path = resolve_within(run_dir, shot["path"])
    sid = snapshot["snapshot_id"]
    if not path.is_file():
        raise SnapshotError(f"{sid}: screenshot not found: {shot['path']}")
    if shot.get("sha256") is not None and sha256_file(path) != shot["sha256"]:
        raise SnapshotError(f"{sid}: screenshot SHA-256 mismatch: {shot['path']}")
    try:
        header = read_header(path)
    except (PNGError, OSError) as exc:
        raise SnapshotError(f"{sid}: screenshot is not a readable PNG: {exc}") from exc
    if (header.width, header.height) != (shot["width_px"], shot["height_px"]):
        raise SnapshotError(f"{sid}: screenshot is {header.width}x{header.height}, snapshot declares "
                            f"{shot['width_px']}x{shot['height_px']}")
    return path


def load_run_dir(path: str | Path, *, verify_screenshots: bool = True) -> tuple[dict, list[dict]]:
    """Load ``run.json`` and every ``S-*.json`` snapshot in a run directory.

    Snapshots are returned sorted by (step_index, snapshot_id); each screenshot
    block gains ``resolved_path`` (absolute path inside the run directory).
    Raises :class:`SnapshotError` on any invalid document, cross-run snapshot,
    dangling step reference, unsafe path or screenshot mismatch.
    """
    run_dir = Path(path)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise SnapshotError(f"run directory not found: {run_dir}")
    run_dir = run_dir.resolve()
    run = load_document(run_dir / "run.json", RUN_SCHEMA)
    snapshots: list[dict] = []
    seen: set[str] = set()
    for file in sorted(run_dir.glob("S-*.json")):
        if file.is_symlink():
            raise SnapshotError(f"symlink not allowed: {file.name}")
        snap = load_document(file, SNAPSHOT_SCHEMA)
        if snap["run_id"] != run["run_id"]:
            raise SnapshotError(f"{file.name}: run_id {snap['run_id']!r} != {run['run_id']!r}")
        if snap["snapshot_id"] in seen:
            raise SnapshotError(f"duplicate snapshot_id {snap['snapshot_id']!r}")
        for key in ("id", "orientation"):
            if snap["device"][key] != run["device"][key]:
                raise SnapshotError(f"{file.name}: device.{key} {snap['device'][key]!r} differs from "
                                    f"run device.{key} {run['device'][key]!r}")
        # Auxiliary reflow/focus measurements may vary viewport/DPR; their
        # original device and probe metadata stays intact.
        captured = datetime.fromisoformat(snap["captured_at"].replace("Z", "+00:00"))
        started = datetime.fromisoformat(run["started_at"].replace("Z", "+00:00"))
        if captured < started:
            raise SnapshotError(f"{file.name}: captured_at predates run start")
        if run.get("ended_at") and captured > datetime.fromisoformat(run["ended_at"].replace("Z", "+00:00")):
            raise SnapshotError(f"{file.name}: captured_at is after run end")
        seen.add(snap["snapshot_id"])
        if verify_screenshots:
            snap["screenshot"]["resolved_path"] = str(_verify_screenshot(run_dir, snap))
        else:
            snap["screenshot"]["resolved_path"] = str(resolve_within(run_dir, snap["screenshot"]["path"]))
        snapshots.append(snap)
    for step in run["steps"]:
        for key in ("before", "after"):
            ref = step.get(key)
            if ref is not None and ref not in seen:
                raise SnapshotError(f"run step {step.get('step_index')} references missing snapshot {ref!r} ({key})")
    snapshots.sort(key=lambda s: (s["step_index"], s["snapshot_id"]))
    return run, snapshots


# --------------------------------------------------------------------------- geometry

def _as_box(obj: Any) -> tuple[float, float, float, float]:
    if isinstance(obj, dict) and "box" in obj:
        obj = obj["box"]
    if isinstance(obj, dict):
        return float(obj["x"]), float(obj["y"]), float(obj["w"]), float(obj["h"])
    if isinstance(obj, (list, tuple)) and len(obj) == 4:
        x, y, w, h = obj
        return float(x), float(y), float(w), float(h)
    raise TypeError("expected an element, a box {x,y,w,h} or an (x, y, w, h) sequence")


def box_edges(box: Any) -> tuple[float, float, float, float]:
    """(left, top, right, bottom) of an element or box."""
    x, y, w, h = _as_box(box)
    return x, y, x + w, y + h


def element_center(element: Any) -> tuple[float, float]:
    x, y, w, h = _as_box(element)
    return x + w / 2, y + h / 2


def box_gap(a: Any, b: Any) -> float:
    """Minimum edge-to-edge Euclidean distance between two boxes (0 if they touch/overlap)."""
    al, at, ar, ab = box_edges(a)
    bl, bt, br, bb = box_edges(b)
    dx = max(0.0, bl - ar, al - br)
    dy = max(0.0, bt - ab, at - bb)
    return math.hypot(dx, dy)


def box_overlap_area(a: Any, b: Any) -> float:
    al, at, ar, ab = box_edges(a)
    bl, bt, br, bb = box_edges(b)
    return max(0.0, min(ar, br) - max(al, bl)) * max(0.0, min(ab, bb) - max(at, bt))


def box_contains(box: Any, x: float, y: float) -> bool:
    left, top, right, bottom = box_edges(box)
    return left <= x <= right and top <= y <= bottom


def elements_by_role(snapshot: dict, role: str, *, field: str = "roles") -> list[dict]:
    """Elements carrying ergo ``role`` in ``roles`` (default) or, with field="role", that ARIA-like role."""
    if field not in ("roles", "role"):
        raise ValueError("field must be 'roles' or 'role'")
    result = []
    for el in snapshot.get("elements", []):
        if field == "roles" and role in (el.get("roles") or []):
            result.append(el)
        elif field == "role" and el.get("role") == role:
            result.append(el)
    return result


def element_by_id(snapshot: dict, element_id: str) -> dict | None:
    return next((el for el in snapshot.get("elements", []) if el.get("id") == element_id), None)


def element_key(element: dict) -> str:
    """Stable cross-profile key ``selector|name`` (spec section 6)."""
    name = element.get("name") or element.get("text") or ""
    return f"{element.get('selector') or ''}|{name}"


def parse_hex_color(value: str) -> tuple[int, ...]:
    """'#rgb'/'#rgba'/'#rrggbb'/'#rrggbbaa' -> (r, g, b) or (r, g, b, a)."""
    if not isinstance(value, str) or not _HEX.fullmatch(value):
        raise ValueError(f"not a hex colour: {value!r}")
    digits = value[1:]
    if len(digits) in (3, 4):
        digits = "".join(c * 2 for c in digits)
    return tuple(int(digits[i:i + 2], 16) for i in range(0, len(digits), 2))
