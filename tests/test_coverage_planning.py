"""Coverage planning regressions use only owned offline fixtures."""
import asyncio
import copy
import importlib.util
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import _paths
import test_scale_run as support
from uxpersonas.scale_entry import ScaleLimits, criterion_checklist, required_fixture_keys, _persona_journey_goal, scale_job_id
from uxpersonas import swarm
from uxpersonas.scale_report import completed_receipt_summary
from uxpersonas.scale_run import ScaleExecution, _criterion_progress, _validated_observation_facts
from uxpersonas.swarm_queue import Queue, checkpoint_data, CHECKPOINT_METADATA_BYTES, CHECKPOINT_OBSERVATION_BYTES
from uxresearch.canonical import EngineError, byte_digest, canonical

ENTRY = Path(__file__).resolve().parents[1] / "skills/remorsearch-ux-qa/scripts/live_scale_browser.py"
SPEC = importlib.util.spec_from_file_location("coverage_live_entry", ENTRY)
live = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live)


class ChecklistTests(unittest.TestCase):
    def test_only_reviewed_typed_hash_paths_bypass_prose_redaction(self):
        digest = "a" + "1234567890123456" + "b" * 47
        facts = {"storage_snapshot": {"available": True, "sha256": digest},
                 "import_attempt": {"fixture_sha256": digest,
                                    "storage_before": {"sha256": digest},
                                    "storage_after": {"sha256": digest}}}
        self.assertNotEqual(swarm.clean(facts), facts)
        self.assertEqual(_validated_observation_facts(facts), facts)
        for unsafe in ({**facts, "explanation": "customer@example.test"},
                       {**facts, "unreviewed": {"sha256": digest}},
                       {"storage_snapshot": {"sha256": "customer@example.test"}}):
            with self.assertRaises(EngineError) as raised:
                _validated_observation_facts(unsafe)
            self.assertEqual(raised.exception.issue["code"], "host_privacy")

    def test_fixture_group_keys_remain_typed_metadata_without_rejecting_task_privacy(self):
        ids = ["PRD-IMPORT-MULTI", "PRD-IMPORT-SIZE"]
        goal = _persona_journey_goal("Use an owned fixture.", ids)
        self.assertEqual(swarm.clean(goal), goal)
        self.assertIn("@group:peekly-loose-512-valid", required_fixture_keys(ids))
        self.assertIn("manifest group peekly-loose-512-valid", goal)

    def test_sample_before_import_and_deletion_last_without_changing_indices(self):
        ids = ["PRD-PRIVACY-DELETE", "PRD-PAYWALL-BOUNDARY",
               "PRD-SAMPLE-EXPORT", "PRD-SNAPSHOT-RETENTION"]
        rows = criterion_checklist(ids)
        self.assertEqual([r["requirement_id"] for r in rows],
                         ["PRD-SAMPLE-EXPORT", "PRD-SNAPSHOT-RETENTION",
                          "PRD-PAYWALL-BOUNDARY", "PRD-PRIVACY-DELETE"])
        self.assertEqual([r["index"] for r in rows], [2, 3, 1, 0])
        self.assertEqual(len(rows[1]["required_fixtures"]), 11)
        self.assertIn("peekly-retention-snapshot-11.zip", rows[1]["required_fixtures"])

    def test_native_failure_is_not_erased_by_later_pass_or_missing_fixture(self):
        task = {"requirement_ids": ["PRD-RESULT-SEARCH"]}
        observations = [{"id": "obs-1", "checks": [{"kind": "success", "index": 0, "status": "failed"}]},
                        {"id": "obs-2", "checks": [{"kind": "success", "index": 0, "status": "passed"}]}]
        row = _criterion_progress(task, observations, ["unrelated.zip"])[0]
        self.assertEqual(row["observed_status"], "failed")
        self.assertEqual(row["observation_ids"], ["obs-1"])
        self.assertEqual(row["missing_fixture_keys"], ["peekly-search-ready.zip"])
        self.assertEqual(_criterion_progress(task, [], [])[0]["observed_status"], "unobserved")

    def test_sample_import_navigation_preserves_visibility_and_task_bounds(self):
        ids = ["PRD-SAMPLE-EXPORT", "PRD-SNAPSHOT-RETENTION", "PRD-PAYWALL-BOUNDARY"]
        checklist = criterion_checklist(ids)
        self.assertIn("When a later criterion requires import", checklist[0]["steps"][-1])
        self.assertIn("do not add a separate 샘플 닫기 prerequisite", checklist[0]["steps"][-1])
        goal = _persona_journey_goal("Inspect the owned sample then import the reviewed fixtures.", ids)
        self.assertEqual(swarm.clean(goal), goal)
        self.assertLessEqual(len(goal), 8000)
        self.assertIn("모달이 없고 현재 More 관측", goal)
        self.assertIn("scroll(delta=-400) 후 반환된 최신 관측", goal)
        self.assertIn("필요하면 한 번 더 반복하고 visible:true가 확인된 뒤에만 클릭", goal)
        self.assertIn("다음 대상이 열린 모달 밖에 있을 때만", goal)
        self.assertIn("모달 안의 탭·날짜 선택기·Pro 설명을 확인할 때는 모달을 유지", goal)

    def test_paywall_dependencies_keep_indices_and_do_not_repeat_retention_seed(self):
        for ids in (["PRD-PAYWALL-BOUNDARY", "PRD-RESULT-SNAPSHOT", "PRD-SNAPSHOT-RETENTION"],
                    ["PRD-SNAPSHOT-RETENTION", "PRD-PAYWALL-BOUNDARY", "PRD-RESULT-SNAPSHOT"],
                    ["PRD-IDENTITY-LIMIT", "PRD-RESULT-SNAPSHOT", "PRD-PAYWALL-BOUNDARY",
                     "PRD-SNAPSHOT-RETENTION"]):
            with self.subTest(ids=ids):
                rows = criterion_checklist(ids)
                self.assertEqual(rows[0]["requirement_id"], "PRD-SNAPSHOT-RETENTION")
                self.assertEqual([r["index"] for r in rows],
                                 [ids.index(r["requirement_id"]) for r in rows])
                paywall = next(r for r in rows if r["requirement_id"] == "PRD-PAYWALL-BOUNDARY")
                self.assertIn("First complete PRD-SNAPSHOT-RETENTION", paywall["steps"][0])
                self.assertIn("Reuse that older history", paywall["steps"][0])
                self.assertIn("Do not import the pair before retention or repeat it", paywall["steps"][0])
                self.assertNotIn("Import peekly-retention-snapshot-01.zip", paywall["steps"][0])
                for dependent in (r for r in rows if r["requirement_id"] in
                                  {"PRD-RESULT-SNAPSHOT", "PRD-IDENTITY-LIMIT"}):
                    self.assertLess(rows.index(paywall), rows.index(dependent))
                    self.assertIn("reuse it without another upload", dependent["steps"][0])
                self.assertEqual(len(required_fixture_keys(ids)), 13)
        # Combined planning must not mutate the standalone paywall checklist.
        standalone = criterion_checklist(["PRD-PAYWALL-BOUNDARY"])[0]
        self.assertEqual(standalone["required_fixtures"],
                         ["peekly-retention-snapshot-01.zip", "peekly-sample-previous.zip",
                          "peekly-sample-current.zip"])
        self.assertTrue(standalone["steps"][0].startswith("Import peekly-retention-snapshot-01.zip"))
        shared = criterion_checklist(["PRD-RESULT-SNAPSHOT", "PRD-PAYWALL-BOUNDARY"])
        self.assertEqual(shared[0]["requirement_id"], "PRD-PAYWALL-BOUNDARY")
        self.assertTrue(shared[0]["steps"][0].startswith("Import peekly-retention-snapshot-01.zip"))
        self.assertIn("reuse it without another upload", shared[1]["steps"][0])

    def test_history_navigation_and_no_movement_escape_fit_bounded_goal(self):
        for ids in (["PRD-PAYWALL-BOUNDARY"],
                    ["PRD-SAMPLE-EXPORT", "PRD-PAYWALL-BOUNDARY", "PRD-SNAPSHOT-RETENTION"],
                    ["PRD-SNAPSHOT-RETENTION", "PRD-RESULT-SNAPSHOT", "PRD-PAYWALL-BOUNDARY"]):
            with self.subTest(ids=ids):
                goal = _persona_journey_goal("Inspect the owned history and preserve unresolved evidence.", ids)
                self.assertEqual(swarm.clean(goal), goal)
                self.assertLessEqual(len(goal), 8000)
                self.assertIn("scroll(delta=400) in the active modal body", goal)
                self.assertIn("Select the visible 기간 비교 tab", goal)
                self.assertIn("비교 시작 기록 / 비교 종료 기록", goal)
                self.assertIn("With older history present", goal)
                self.assertIn("2회 연속 그대로면 더 반복하지 않는다", goal)
                self.assertIn("해당 기준의 not_run을 남기고 다른 미완료 기준", goal)
                self.assertIn("같은 모달을 닫고 다시 열어도 횟수는 초기화하지 않", goal)
                self.assertIn("선행조건이나 화면 상태가 바뀐 뒤에만 재시도", goal)
                if "PRD-SNAPSHOT-RETENTION" in ids:
                    self.assertLess(goal.index("서로 다른 유효 합성 스냅샷 11개"),
                                    goal.index("그 뒤 previous/current pair"))

    def test_sixty_four_observations_fit_model_envelope_and_preserve_checks(self):
        observations = []
        for i in range(64):
            observations.append({"id": f"obs-{i+1}", "action": "Inspect owned result",
                "text": "관찰한 결과 " * 1000,
                "facts": {"text": "관찰한 결과 " * 1000,
                    "controls": [{"selector": f"#control-{n}", "label": "현재 화면 " * 20,
                                  "visible": True} for n in range(35)],
                    "fixture_uploads": [f"peekly-retention-snapshot-{n:02d}.zip" for n in range(1, min(i+2, 12))],
                    "available_fixtures": [f"peekly-retention-snapshot-{n:02d}.zip" for n in range(1, 12)],
                    "fixture_validation": [],
                    "list_rows": [{"key": f"synthetic-{n:02d}", "text": "합성 결과 " * 10} for n in range(40)],
                    "import_attempt": {"attempt_id": f"owned-{i}", "cancel_dispatched": False}},
                "checks": [{"kind": "success", "index": 0, "status": "not_run", "reason": "History not opened."}],
                "captures": [], "artifacts": []})
        original = copy.deepcopy(observations)
        execution = ScaleExecution.__new__(ScaleExecution)
        execution.plan = {"tools": [], "limits": {"turns": 64}}
        task = {"id": "S-test", "goal": "Inspect retention.", "requirement_ids": ["PRD-SNAPSHOT-RETENTION"]}
        record = {"profile": {}, "provenance": {"mode": "synthetic"},
                  "context": {"requirements": []}}
        payload = execution.payload({"job": {"task": task}},
                                    {"observations": observations, "turn": 60}, record, "model")
        self.assertLess(len(json.dumps(payload, ensure_ascii=False).encode()), 262144)
        self.assertEqual(sum(len(o["checks"]) for o in payload["observations"]), 64)
        self.assertEqual([o["id"] for o in payload["observations"]],
                         [o["id"] for o in observations])
        self.assertNotIn("controls", payload["observations"][0]["facts"])
        self.assertEqual(payload["observations"][-1]["facts"]["controls"], observations[-1]["facts"]["controls"])
        self.assertEqual(payload["observations"][0]["facts"]["import_attempt"], observations[0]["facts"]["import_attempt"])
        self.assertTrue(payload["observations"][0]["text_excerpt"])
        self.assertEqual(observations, original)

    def test_completed_summary_excludes_valid_partial_previews_and_keeps_duplicates_visible(self):
        def row(job, persona, status, outcome, complete):
            receipt = {"outcome": outcome, "criteria": [
                {"kind": "success", "index": 0, "status": "not_run"}]}
            return {"job_id": job, "persona_id": persona, "status": status,
                    "current_valid": True, "current_ux_outcome": outcome,
                    "result": {"operational_completed": True, "receipt": receipt} if complete else None,
                    "receipt_preview": None if complete else receipt}
        report = {"tasks": [row("a", "P-one", "complete", "inconclusive", True),
                            row("b", "P-one", "complete", "inconclusive", True),
                            row("c", "P-two", "uncertain", "failed", False),
                            row("d", "P-three", "queued", "inconclusive", False)]}
        original = copy.deepcopy(report)
        summary = completed_receipt_summary(report)
        self.assertEqual(summary["completed_sessions"], 2)
        self.assertEqual(summary["distinct_completed_personas"], 1)
        self.assertEqual(summary["session_outcomes"]["failed"], 0)
        self.assertEqual(summary["session_outcomes"]["inconclusive"], 2)
        self.assertEqual(summary["criteria_all"]["not_run"], 2)
        self.assertEqual(summary["excluded_attempt_statuses"], {"uncertain": 1, "queued": 1})
        self.assertEqual(report, original)


class ImportedCategoryPlanningTests(unittest.TestCase):
    categories = {
        "PRD-RESULT-RECIPROCITY": "나를 맞팔 안 한 사람",
        "PRD-RESULT-REVERSE": "내가 맞팔 안 한 사람",
        "PRD-RESULT-MUTUAL": "맞팔 중인 사람",
    }

    def test_each_category_requires_actual_current_import_and_its_own_list(self):
        for rid, label in self.categories.items():
            with self.subTest(requirement=rid):
                row = criterion_checklist([rid])[0]
                self.assertEqual(row["required_fixtures"], ["peekly-sample-current.zip"])
                self.assertIn("Import peekly-sample-current.zip once", row["steps"][0])
                self.assertIn("confirm completion", row["steps"][0])
                self.assertIn("Sample mode cannot satisfy", row["steps"][0])
                self.assertIn("Open the visible " + label + " category list", row["steps"][1])
                self.assertIn("actual row set", row["steps"][1])
                goal = _persona_journey_goal("Inspect the owned imported result.", [rid])
                self.assertNotIn("or enter sample mode", goal)
                self.assertNotIn("샘플로 둘러보기를 열고", goal)
                self.assertEqual(swarm.clean(goal), goal)
                self.assertLessEqual(len(goal), 8000)
        rows = criterion_checklist(list(self.categories))
        self.assertEqual(sum("Import peekly-sample-current.zip once" in r["steps"][0] for r in rows), 1)
        self.assertTrue(all("without another upload" in r["steps"][0] for r in rows[1:]))

    def test_saved_017_to_020_requirements_put_pair_before_three_distinct_lists(self):
        # These saved personas had only sample-list/card/departed-list observations.
        # Their actual requirement set needs three separate post-import list steps.
        original = [*self.categories, "PRD-RESULT-SNAPSHOT"]
        for ids in (original, list(reversed(original))):
            with self.subTest(ids=ids):
                rows = criterion_checklist(ids)
                self.assertEqual(rows[0]["requirement_id"], "PRD-RESULT-SNAPSHOT")
                self.assertEqual([r["index"] for r in rows],
                                 [ids.index(r["requirement_id"]) for r in rows])
                self.assertEqual(set(required_fixture_keys(ids)),
                                 {"peekly-sample-previous.zip", "peekly-sample-current.zip"})
                for row in rows[1:]:
                    self.assertIn("After PRD-RESULT-SNAPSHOT completes", row["steps"][0])
                    self.assertIn("active completed result", row["steps"][0])
                    self.assertIn("without another upload", row["steps"][0])
                    self.assertIn(self.categories[row["requirement_id"]] + " category list", row["steps"][1])
                goal = _persona_journey_goal("Reviewed fresh cohort. " + "bounded " * 95, ids)
                self.assertIn("목록을 각각 직접 열어", goal)
                self.assertIn("카드 숫자만 본 상태", goal)
                self.assertIn("대체 증거가 아니다", goal)
                self.assertEqual(swarm.clean(goal), goal)
                self.assertLessEqual(len(goal), 8000)

    def test_category_setup_preserves_export_retention_paywall_identity_and_deletion_order(self):
        for setup in (["PRD-RESULT-SNAPSHOT"], ["PRD-IDENTITY-LIMIT"],
                      ["PRD-PAYWALL-BOUNDARY"],
                      ["PRD-SNAPSHOT-RETENTION", "PRD-PAYWALL-BOUNDARY",
                       "PRD-RESULT-SNAPSHOT", "PRD-IDENTITY-LIMIT"]):
            ids = [*self.categories, "PRD-PRIVACY-DELETE", *reversed(setup), "PRD-SAMPLE-EXPORT"]
            with self.subTest(setup=setup):
                rows = criterion_checklist(ids)
                ordered = [r["requirement_id"] for r in rows]
                self.assertEqual(ordered[0], "PRD-SAMPLE-EXPORT")
                self.assertEqual(ordered[-1], "PRD-PRIVACY-DELETE")
                first_list = min(ordered.index(rid) for rid in self.categories)
                self.assertTrue(all(ordered.index(rid) < first_list for rid in setup))
                if "PRD-SNAPSHOT-RETENTION" in setup:
                    self.assertLess(ordered.index("PRD-SNAPSHOT-RETENTION"),
                                    ordered.index("PRD-PAYWALL-BOUNDARY"))
                if "PRD-PAYWALL-BOUNDARY" in setup:
                    for row in rows:
                        if row["requirement_id"] in {"PRD-RESULT-SNAPSHOT", "PRD-IDENTITY-LIMIT"}:
                            self.assertIn("reuse it without another upload", row["steps"][0])
                self.assertEqual([r["index"] for r in rows],
                                 [ids.index(r["requirement_id"]) for r in rows])
                for row in rows:
                    if row["requirement_id"] in self.categories:
                        self.assertIn("without another upload", row["steps"][0])

    def test_category_fixture_preflight_rejects_missing_current_and_verifies_it_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "fixture-manifest.json"
            manifest = dict(schema_version="peekly-synthetic-fixtures.v1", files=[], groups={})
            manifest_path.write_text(json.dumps(manifest))
            for rid in self.categories:
                with self.subTest(requirement=rid):
                    with self.assertRaisesRegex(RuntimeError, "required_fixture_missing:peekly-sample-current.zip"):
                        live.fixture_preflight(root, [rid])
            name = "peekly-sample-current.zip"
            data = b"owned-offline-current-fixture"
            (root / name).write_bytes(data)
            manifest["files"] = [dict(name=name, bytes=len(data), sha256=byte_digest(data))]
            manifest_path.write_text(json.dumps(manifest))
            checked = live.fixture_preflight(root, list(self.categories))
            self.assertEqual(checked["required_fixture_keys"], [name])
            self.assertEqual(checked["required_file_count"], 1)
            self.assertEqual(checked["verified_fixture_bytes"], len(data))


class LegacyUnknownPlanningTests(unittest.TestCase):
    def test_unavailable_legacy_setup_stays_not_run_without_known_empty_substitution(self):
        rid = "PRD-IMPORT-SNAPSHOT-UNKNOWN"
        row = criterion_checklist([rid])[0]
        self.assertEqual(row["required_fixtures"], [])
        self.assertEqual(required_fixture_keys([rid]), [])
        self.assertIn("legacy snapshot without includedFiles", row["steps"][0])
        self.assertIn("no reviewed setup", row["steps"][0])
        self.assertIn("Keep not_run: reviewed legacy-unknown setup unavailable", row["steps"][1])
        self.assertIn("Do not substitute peekly-empty-previous.zip", row["steps"][1])
        self.assertIn("Continue the other criteria", row["steps"][2])
        self.assertNotIn("not_applicable", " ".join(row["steps"]))
        goal = _persona_journey_goal("Inspect only the reviewed owned state.", [rid])
        self.assertIn("known-empty이므로 대체하지 않는다", goal)
        self.assertIn("그 사유와 함께 not_run으로 남기고 다른 기준을 계속", goal)
        self.assertNotIn("peekly-empty-previous.zip을 먼저 넣고", goal)
        self.assertNotIn("upload peekly-empty-previous.zip then", goal.lower())
        self.assertEqual(swarm.clean(goal), goal)
        self.assertLessEqual(len(goal), 8000)

    def test_unsupported_unknown_does_not_block_or_weaken_other_pair_preflight(self):
        unknown = "PRD-IMPORT-SNAPSHOT-UNKNOWN"
        normal = "PRD-RESULT-SNAPSHOT"
        normal_row = criterion_checklist([normal])[0]
        mixed_rows = criterion_checklist([unknown, normal])
        mixed_normal = next(row for row in mixed_rows if row["requirement_id"] == normal)
        self.assertEqual(mixed_normal["index"], 1)
        self.assertEqual({k: v for k, v in mixed_normal.items() if k != "index"},
                         {k: v for k, v in normal_row.items() if k != "index"})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "fixture-manifest.json"
            manifest = dict(schema_version="peekly-synthetic-fixtures.v1", files=[], groups={})
            manifest_path.write_text(json.dumps(manifest))
            unsupported = live.fixture_preflight(root, [unknown])
            self.assertEqual(unsupported["required_file_count"], 0)
            for name in ("peekly-sample-previous.zip", "peekly-sample-current.zip"):
                data = ("owned-normal-pair:" + name).encode()
                (root / name).write_bytes(data)
                manifest["files"].append(dict(name=name, bytes=len(data), sha256=byte_digest(data)))
            manifest_path.write_text(json.dumps(manifest))
            mixed = live.fixture_preflight(root, [unknown, normal])
            self.assertEqual(mixed, live.fixture_preflight(root, [normal]))
            self.assertEqual(mixed["required_file_count"], 2)
            self.assertNotIn("peekly-empty-previous.zip", mixed["required_fixture_keys"])
            manifest["files"] = manifest["files"][:1]
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(RuntimeError, "required_fixture_missing:peekly-sample-current.zip"):
                live.fixture_preflight(root, [unknown, normal])


class FixtureGateTests(unittest.IsolatedAsyncioTestCase):
    async def test_paywall_pair_without_older_history_blocks_before_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixtures = root / "fixtures"
            fixtures.mkdir()
            rows = []
            for name in ("peekly-sample-previous.zip", "peekly-sample-current.zip"):
                data = ("owned-fixture:" + name).encode()
                (fixtures / name).write_bytes(data)
                rows.append(dict(name=name, bytes=len(data), sha256=byte_digest(data)))
            manifest = dict(schema_version="peekly-synthetic-fixtures.v1", files=rows, groups={})
            manifest_path = fixtures / "fixture-manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            args = SimpleNamespace(run_root=root / "new-run", library=root / "library",
                                   product_id="peekly", fixtures=fixtures, turns=64)
            with patch.object(live, "Library") as library, patch.object(live, "_route") as route:
                context = library.return_value.__enter__.return_value
                context.list.return_value = {"personas": [{"persona_id": "PER-one", "revision": 2, "reusable": True}]}
                context.get.return_value = {"profile": {"requirement_ids": ["PRD-PAYWALL-BOUNDARY"]}}
                with self.assertRaisesRegex(RuntimeError, "required_fixture_missing:peekly-retention-snapshot-01.zip"):
                    await live.run_stage(args, ["PER-one"], 2)
                route.assert_not_called()
                self.assertFalse(args.run_root.exists())
            name = "peekly-retention-snapshot-01.zip"
            data = b"owned-older-same-account-fixture"
            (fixtures / name).write_bytes(data)
            rows.append(dict(name=name, bytes=len(data), sha256=byte_digest(data)))
            manifest_path.write_text(json.dumps(manifest))
            checked = live.fixture_preflight(fixtures, ["PRD-PAYWALL-BOUNDARY"])
            self.assertEqual(checked["required_file_count"], 3)
            self.assertEqual(set(checked["required_fixture_keys"]), {r["name"] for r in rows})

    async def test_tampered_required_fixture_blocks_before_provider_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            name = "peekly-search-ready.zip"
            original = b"owned-synthetic-data"
            (root / name).write_bytes(b"x" + original[1:])
            (root / "fixture-manifest.json").write_text(json.dumps({
                "schema_version": "peekly-synthetic-fixtures.v1",
                "files": [{"name": name, "bytes": len(original), "sha256": byte_digest(original)}],
                "groups": {}}))
            args = SimpleNamespace(run_root=root / "new-run", library=root / "library",
                                   product_id="peekly", fixtures=root, turns=64)
            with patch.object(live, "Library") as library, patch.object(live, "_route") as route:
                context = library.return_value.__enter__.return_value
                context.list.return_value = {"personas": [{"persona_id": "PER-one", "revision": 2, "reusable": True}]}
                context.get.return_value = {"profile": {"requirement_ids": ["PRD-RESULT-SEARCH"]}}
                with self.assertRaisesRegex(RuntimeError, "required_fixture_digest_mismatch"):
                    await live.run_stage(args, ["PER-one"], 2)
                route.assert_not_called()
                self.assertFalse(args.run_root.exists())

    async def test_prior_job_identity_blocks_even_with_fresh_output_before_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "fixture-manifest.json").write_text(json.dumps({
                "schema_version": "peekly-synthetic-fixtures.v1", "files": [], "groups": {}}))
            artifact = root / "owned-build.txt"
            artifact.write_bytes(b"owned-build")
            build = dict(id="coverage-build", artifact_path=str(artifact), sha256=byte_digest(artifact.read_bytes()))
            goal = "Inspect the reviewed owned flow."
            prior_id = scale_job_id("peekly", "PER-one", 2, goal, build)
            self.assertNotEqual(prior_id, scale_job_id("peekly", "PER-one", 2, goal + " Fresh cohort.", build))
            args = SimpleNamespace(run_root=root / "fresh-output", library=root / "library",
                                   product_id="peekly", fixtures=root, turns=64,
                                   build_artifact=artifact, build_id=build["id"], goal=goal,
                                   forbidden_job_ids={prior_id})
            with patch.object(live, "Library") as library, patch.object(live, "_route") as route:
                context = library.return_value.__enter__.return_value
                context.list.return_value = {"personas": [{"persona_id": "PER-one", "revision": 2, "reusable": True}]}
                context.get.return_value = {"profile": {"requirement_ids": ["PRD-START-SAMPLE"]}}
                with self.assertRaisesRegex(RuntimeError, "prior_job_identity_overlap:1"):
                    await live.run_stage(args, ["PER-one"], 2)
                route.assert_not_called()
                self.assertFalse(args.run_root.exists())

    async def test_missing_eleventh_retention_fixture_blocks_before_provider_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixtures = root / "fixtures"
            fixtures.mkdir()
            names = [f"peekly-retention-snapshot-{i:02d}.zip" for i in range(1, 11)]
            (fixtures / "fixture-manifest.json").write_text(json.dumps({
                "schema_version": "peekly-synthetic-fixtures.v1",
                "files": [{"name": name} for name in names], "groups": {}}))
            for name in names:
                (fixtures / name).write_bytes(b"owned-offline")
            args = SimpleNamespace(run_root=root / "new-run", library=root / "library",
                                   product_id="peekly", fixtures=fixtures, turns=64)
            with patch.object(live, "Library") as library, patch.object(live, "_route") as route:
                context = library.return_value.__enter__.return_value
                context.list.return_value = {"personas": [{"persona_id": "PER-one", "revision": 2, "reusable": True}]}
                context.get.return_value = {"profile": {"requirement_ids": ["PRD-SNAPSHOT-RETENTION"]}}
                with self.assertRaisesRegex(RuntimeError, "peekly-retention-snapshot-11.zip"):
                    await live.run_stage(args, ["PER-one"], 2)
                route.assert_not_called()
                self.assertFalse(args.run_root.exists())


class BoundedLongJourneyTests(unittest.IsolatedAsyncioTestCase):
    setUp = support.ScaleRunTests.setUp
    run_scale = support.ScaleRunTests.run_scale

    async def test_extended_budget_finishes_long_owned_fixture_but_rejects_unbounded_plan(self):
        loop = asyncio.get_running_loop()
        self.addCleanup(setattr, loop, "slow_callback_duration", loop.slow_callback_duration)
        loop.slow_callback_duration = 2.0
        plan = json.loads(json.dumps(self.queue.plan))
        plan["limits"].update(turns=64, max_model_calls=130, task_seconds=180)
        self.queue = Queue.create(self.root / "long-scale", plan)
        original = self.host.result
        fixture_catalog = [f"peekly-retention-owned-fixture-{i:03d}.zip" for i in range(543)]
        controls = [{"selector": f"#owned-control-{i}", "label": "현재 기록 확인 " + str(i),
                     "visible": True, "enabled": True, "type": "button"} for i in range(36)]
        payload_sizes = []
        async def result(kind, request):
            if kind in {"model", "review"}:
                payload_sizes.append(len(canonical(request["payload"])))
                if kind == "model" and len(request["payload"]["observations"]) < 59:
                    self.host.states.setdefault(request["context_id"], dict(stage="empty", note="", saved="", retained=None))
                    return {"kind": "tool", "tool": "inspect", "arguments": {},
                            "decision": "Inspect the next owned prerequisite."}
            response = await original(kind, request)
            if kind == "tool":
                response["text"] += " 현재 저장한 합성 기록을 확인하고 다음 단계로 이동합니다." * 20
                response["facts"].update(available_fixtures=fixture_catalog, controls=controls,
                    file_inputs=[{"selector": "#owned-file", "multiple": True}],
                    fixture_uploads=[f"peekly-retention-snapshot-{i:02d}.zip" for i in range(1, 12)],
                    fixture_validation=[], list_rows=[{"key": f"synthetic_row_{i}", "text": "합성 관계 항목"} for i in range(12)])
                response["facts"]["storage_snapshot"] = {
                    "available": True, "sha256": "a" + "1234567890123456" + "b" * 47}
                self.assertLess(len(canonical({k: response[k] for k in ("text", "facts", "checks")})), 65536)
            return response
        self.host.result = result
        report = await self.run_scale()
        self.assertEqual(report["counts"]["complete"], 2,
                         {"counts": report["counts"], "calls": report["authored_model_calls"],
                          "problems": [(row["job_id"], row.get("problem")) for row in report["tasks"]]})
        self.assertEqual(report["authored_model_calls"], 130)
        self.assertEqual(report["completed_receipt_summary"]["assessed_completed_sessions"], 2)
        self.assertLessEqual(max(payload_sizes), 262144)
        self.assertEqual(len(payload_sizes), 130)
        with sqlite3.connect(self.queue.path.as_uri() + "?mode=ro", uri=True) as db:
            checkpoints = db.execute("SELECT checkpoint FROM jobs ORDER BY ordinal").fetchall()
        for (raw,) in checkpoints:
            self.assertGreater(len(raw.encode()), 1024 * 1024)
            state = json.loads(raw)
            self.assertEqual(state["turn"], 64)
            self.assertEqual(len(state["observations"]), 63)
            for observation in state["observations"]:
                self.assertEqual(observation["facts"]["available_fixtures"], fixture_catalog)
                self.assertEqual(observation["facts"]["controls"], controls)
        # Full files remain unchanged after projection, checkpointing and final
        # admission; the durable receipt still binds every original byte.
        for row in report["tasks"]:
            evidence_root = Path(row["result"]["evidence_root"])
            for artifact in row["result"]["receipt"]["artifacts"]:
                self.assertEqual(byte_digest((evidence_root / artifact["path"]).read_bytes()), artifact["sha256"])
        invalid = copy.deepcopy(plan)
        invalid["limits"]["turns"] = 65
        with self.assertRaises(Exception):
            Queue.create(self.root / "too-long-scale", invalid)
        self.assertFalse((self.root / "too-long-scale").exists())
        self.assertEqual(ScaleLimits(turns=64).validate()["turns"], 64)
        with self.assertRaises(Exception):
            ScaleLimits(turns=65).validate()
        self.assertEqual(live.live_limits(32).max_model_calls, 32 * 17)
        self.assertEqual(live.live_limits(32, 64).max_model_calls, 32 * 65)
        self.assertEqual(live.live_limits(32, 64).budget_microusd, 0)

    async def test_checkpoint_budget_does_not_expand_other_envelopes_or_observation_count(self):
        plan = copy.deepcopy(self.queue.plan)
        plan["limits"].update(turns=64, max_model_calls=130)
        queue = Queue.create(self.root / "bounded-checkpoint-scale", plan)
        claim = queue.claim("checkpoint-regression")
        valid = {"turn": 64, "observations": [{"text": "Owned observation", "facts": {}, "checks": []}] * 64}
        queue.checkpoint(claim, valid)
        stored = queue.assert_claim(claim)["checkpoint"]
        for invalid in (
                {"observations": valid["observations"] + [valid["observations"][0]]},
                {"observations": [{"text": "owned", "facts": {"large": "x" * 65536}, "checks": []}]},
                {"observations": ["x" * CHECKPOINT_OBSERVATION_BYTES]},
                {"metadata": "x" * CHECKPOINT_METADATA_BYTES},
                {"observations": [], "metadata": float("nan")}):
            with self.assertRaises(EngineError):
                queue.checkpoint(claim, invalid)
            self.assertEqual(queue.assert_claim(claim)["checkpoint"], stored)
        with self.assertRaises(EngineError):
            queue.begin(claim, "model", "large-request", {"large": "x" * 262144})
        with self.assertRaises(EngineError):
            queue.complete(claim, {"large": "x" * CHECKPOINT_METADATA_BYTES})
        with self.assertRaises(EngineError):
            checkpoint_data(valid, 63)
