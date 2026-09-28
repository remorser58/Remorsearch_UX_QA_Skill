"""End-to-end offline pipeline: recorded run -> analyze -> swarm -> bundle/report/bench."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ergoqa import analyze, bench, bundle, png, report, swarm  # noqa: E402
from ergoqa.profiles import sample_profiles  # noqa: E402
from ergoqa.snapshot import sha256_file  # noqa: E402
from validate_bundle import validate_bundle  # noqa: E402

W, H = 360, 780


def el(eid, role, box, *, name="", text="", selector=None, interactive=False, roles=(), fg="#111111", bg="#ffffff",
       size=16, weight=400, tag="div", border=None):
    return {
        "id": eid, "role": role, "name": name, "text": text, "tag": tag, "selector": selector or f"#{eid}",
        "box": dict(zip("xywh", box)), "interactive": interactive, "visible": True, "enabled": True, "in_viewport": True,
        "font_size_px": size, "font_weight": weight, "color_fg": fg, "color_bg": bg, "border_color": border,
        "roles": list(roles), "source": "dom",
    }


def base_elements():
    options = [
        el(f"opt-{i}", "button", (10 + (i % 4) * 86, 420 + (i // 4) * 50, 80, 44), name=f"옵션 {i}", text=f"옵션 {i}",
           interactive=True, tag="button", bg="#eeeeee")
        for i in range(12)
    ]
    return [
        el("title", "heading", (16, 70, 200, 28), text="주문 확인", size=20, weight=700),
        el("pay", "button", (10, 250, 90, 44), name="결제하기", text="결제하기", interactive=True, roles=("primary",),
           fg="#ffffff", bg="#1a73e8", tag="button", weight=700),
        el("delete", "button", (102, 250, 90, 44), name="전체 삭제", text="전체 삭제", interactive=True,
           roles=("destructive",), fg="#ffffff", bg="#d93025", tag="button"),
        el("close", "button", (336, 8, 16, 16), name="닫기", interactive=True, tag="button"),
        el("help", "button", (316, 8, 16, 16), name="도움말", interactive=True, tag="button"),
        el("hint", "text", (16, 310, 300, 14), text="배송은 영업일 기준 2~3일 소요됩니다.", size=11, fg="#9e9e9e"),
        el("dot-ok", "status", (16, 360, 12, 12), fg="#111111", bg="#388e3c"),
        el("dot-bad", "status", (36, 360, 12, 12), fg="#111111", bg="#d32f2f"),
        *options,
    ]


def write_png(path: Path) -> str:
    image = png.new_image(W, H, 3, (255, 255, 255))
    data = bytearray(image.data)
    for y in range(250, 294):
        for x in range(10, 100):
            i = (y * W + x) * 3
            data[i:i + 3] = bytes((26, 115, 232))
    png.write_png(path, png.make_image(W, H, 3, bytes(data)))
    return sha256_file(path)


def make_run(root: Path) -> Path:
    run_dir = root / "R-1"
    run_dir.mkdir()
    snaps = []
    for index in range(2):
        sid = f"S-R-1-{index:03d}"
        sha = write_png(run_dir / f"{sid}.png")
        elements = base_elements()
        if index == 1:
            elements.append(el("error", "alert", (16, 740, 200, 16), text="카드 정보를 확인해 주세요", size=12,
                               fg="#b3261e", roles=("error_message",)))
        snaps.append({
            "schema_version": "ergo-snapshot.v1", "snapshot_id": sid, "run_id": "R-1", "step_index": index,
            "captured_at": "2026-09-28T12:00:00Z",
            "surface": {"kind": "web", "url": "http://127.0.0.1/checkout.html", "title": "checkout", "app_id": None},
            "device": {"id": "galaxy-s24", "viewport_css": [W, H], "dpr": 1.0, "orientation": "portrait"},
            "screenshot": {"path": f"{sid}.png", "sha256": sha, "width_px": W, "height_px": H},
            "elements": elements,
            "focus_point": None if index == 0 else {"x": 55, "y": 272},
            "console_errors": [], "notes": [],
        })
    for snap in snaps:
        (run_dir / f"{snap['snapshot_id']}.json").write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
    run = {
        "schema_version": "ergo-run.v1", "run_id": "R-1", "scenario_id": "SC-checkout", "profile_id": "EP-01",
        "driver": {"name": "test-fixture", "version": "0", "browser": None},
        "device": {"id": "galaxy-s24", "viewport_css": [W, H], "dpr": 1.0, "orientation": "portrait"},
        "mode": "scripted", "started_at": "2026-09-28T12:00:00Z", "ended_at": "2026-09-28T12:00:05Z",
        "status": "completed", "success": True,
        "steps": [{
            "step_index": 1, "action": {"action": "tap", "target": "#pay"}, "target_element_id": "pay",
            "point": {"x": 55, "y": 272}, "before": "S-R-1-000", "after": "S-R-1-001", "t_start_ms": 100,
            "t_end_ms": 180, "feedback_latency_ms": 1500, "result": "ok", "error": None,
        }],
        "timing_windows": [{"id": "toast-1", "selector": "#toast", "kind": "transient_text", "visible_ms": 1500,
                            "text": "쿠폰이 적용되었습니다. 결제 금액과 배송 예정일을 다시 한 번 확인해 주세요."}],
        "persona_notes": [{"step_index": 1, "intent": "결제", "expected": "결제 진행", "observed": "아래에 오류가 떠서 못 봄", "confusion": True}],
    }
    (run_dir / "run.json").write_text(json.dumps(run, ensure_ascii=False), encoding="utf-8")
    return run_dir


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.run_dir = make_run(cls.root)
        cls.profiles = sample_profiles(14, 3, ["galaxy-s24"])
        cls.analysis = analyze.analyze_run(cls.run_dir, cls.profiles, None, cross_profile=True)
        cls.findings = swarm.aggregate([cls.analysis], cls.profiles)
        cls.by_check = {}
        for f in cls.findings:
            cls.by_check.setdefault(f["check_id"], []).append(f)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def find(self, check_id, selector):
        return [f for f in self.by_check.get(check_id, []) if f["element_key"].startswith(selector + "|") or selector in f.get("selectors", [])]

    def test_all_profiles_evaluated(self) -> None:
        self.assertEqual(len(self.analysis["profiles_evaluated"]), 14)

    def test_reach_is_right_one_hand_specific(self) -> None:
        found = self.find("RH-01", "#pay")
        self.assertTrue(found)
        self.assertEqual(found[0]["profile_specific"].get("grip"), "one_hand_right")
        self.assertEqual(found[0]["epistemic_status"], "inferred")
        self.assertIn(found[0]["severity"], ("P2", "P3"))

    def test_destructive_neighbour(self) -> None:
        found = self.find("PT-03", "#delete")
        self.assertTrue(found)
        self.assertIn(found[0]["severity"], ("P1", "P2", "P3"))

    def test_small_crowded_icons(self) -> None:
        self.assertTrue(self.find("PT-01", "#close"))
        self.assertEqual(self.find("PT-01", "#close")[0]["epistemic_status"], "observed")

    def test_contrast_and_text_size(self) -> None:
        self.assertTrue(self.find("PC-01", "#hint"))
        size = self.find("PC-04", "#hint")
        self.assertTrue(size)
        # 11 px on a Galaxy S24 at 30 cm is ~23 arcmin: above the 16' floor, below the
        # Hangul critical print size (24.6'), so it is a P3 comfort finding for everyone.
        self.assertEqual(size[0]["severity"], "P3")
        self.assertEqual(size[0]["measurement"]["tier"], "critical_print_size")

    def test_colour_only_is_cvd_specific(self) -> None:
        found = self.by_check.get("PC-03", [])
        self.assertTrue(found)
        for f in found:
            for pid in f["triggered_profiles"]:
                profile = next(p for p in self.profiles if p["profile_id"] == pid)
                self.assertNotEqual(profile["attributes"]["vision"]["cvd"], "none")

    def test_choice_overload_latency_toast_and_note(self) -> None:
        self.assertTrue(self.by_check.get("CG-01"))
        self.assertTrue(self.by_check.get("CG-03"))
        self.assertTrue(self.by_check.get("CG-02"))
        notes = self.by_check.get("PJ-01", [])
        self.assertTrue(notes)
        self.assertEqual(notes[0]["triggered_profiles"], ["EP-01"])
        self.assertEqual(notes[0]["basis"], "judgment")

    def test_feedback_far_from_touch(self) -> None:
        self.assertTrue(self.find("GZ-02", "#error"))

    def test_coverage_label_is_not_prevalence(self) -> None:
        for f in self.findings:
            self.assertIn("coverage, not prevalence", f["coverage_label"])

    def test_bundle_validates(self) -> None:
        doc = bundle.to_evidence_bundle("ergo-test", [self.analysis], self.findings, self.profiles, seed=3)
        self.assertEqual(validate_bundle(doc), [])
        verified = [f for f in doc["records"]["findings"] if f["verification_status"] == "verified"]
        self.assertTrue(verified)
        obs = {o["id"]: o for o in doc["records"]["observations"]}
        for f in verified:
            self.assertTrue(all(obs[o]["basis"] == "measured" for o in f["observation_ids"]))
        inferred = [f for f in doc["records"]["findings"] if f["check_id"] == "RH-01"]
        self.assertTrue(all(f["verification_status"] == "unverified" for f in inferred))

    def test_report_renders_korean(self) -> None:
        text = report.render(self.findings, self.profiles, [self.analysis])
        self.assertIn("커버리지", text)
        self.assertIn("RH-01", text)

    def test_bench_scoring(self) -> None:
        key = {
            "suite": "unit",
            "defects": [
                {"id": "D-1", "scenario_id": "SC-checkout", "category": "reach", "element_selector": "#pay",
                 "profile_condition": {"grip": "one_hand_right"}, "severity_min": "P3"},
                {"id": "D-2", "scenario_id": "SC-checkout", "category": "perception", "element_selector": "#hint", "profile_condition": {}, "severity_min": "P2"},
                {"id": "D-3", "scenario_id": "SC-checkout", "category": "gaze", "element_selector": "#nothing", "profile_condition": {}, "severity_min": "P3"},
            ],
            "decoys": [{"id": "N-1", "scenario_id": "SC-checkout", "category": "pointing", "element_selector": "#title"}],
            "clean_controls": [],
        }
        result = bench.score(key, self.findings, self.profiles)
        self.assertAlmostEqual(result["recall_strict"], 2 / 3, places=3)
        self.assertEqual(result["decoys_flagged"], 0)


if __name__ == "__main__":
    unittest.main()
