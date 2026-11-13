"""Offline regressions for failures observed in the real Peekly run."""
import asyncio
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

import _paths
from uxpersonas import swarm
from uxpersonas.model_router import ModelRoute, ModelRouter, RoutedScaleProvider
from uxpersonas.scale_browser_host import ScaleBrowserHost
from uxpersonas.swarm_providers import ProviderSpec


class CaptureRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_pre_dispatch_rejection_becomes_observed_failure_not_fake_click(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            picture = root / "rejected.png"
            picture.write_bytes(b"capture")
            picture.chmod(0o600)
            observation = {"text": "Current visible page", "facts": {}, "checks": [],
                "captures": [{"path": picture.name, "sha256": hashlib.sha256(b"capture").hexdigest()}]}
            host = object.__new__(ScaleBrowserHost)
            host.processes = {"context": object()}
            host._exchange = AsyncMock(side_effect=[
                RuntimeError("browser_action_failed:click_target_not_allowed_or_visible"), observation])
            request = {"operation_id": "operation", "context_id": "context",
                "request_sha256": "a" * 64, "payload": {"name": "click",
                    "arguments": {"selector": "#stale", "label": "Stale"}, "evidence_path": str(root)}}
            reply = await host.call("tool", request)
            self.assertIn("rejected before dispatch", reply["result"]["text"])
            self.assertEqual(reply["result"]["facts"]["tool_outcome"]["status"], "rejected_before_dispatch")
            self.assertEqual(host._exchange.call_args_list[-1].args[2], {"name": "observe", "arguments": {}})
            host._exchange = AsyncMock(side_effect=RuntimeError("browser_action_failed:fixture_integrity"))
            with self.assertRaisesRegex(RuntimeError, "fixture_integrity"):
                await host.call("tool", request)
            self.assertEqual(host._exchange.call_count, 1)

    async def test_scrub_text_without_corrupting_hash_and_still_reject_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            data = b"capture-regression-20"
            sha = hashlib.sha256(data).hexdigest()
            self.assertNotEqual(swarm.clean(sha), sha, "Regression must exercise a card-like hash")
            picture = root / "browser-00001.png"
            picture.write_bytes(data)
            picture.chmod(0o600)
            result = {"text": "Account @synthetic.test", "facts": {},
                "captures": [{"path": picture.name, "sha256": sha}], "checks": []}
            host = object.__new__(ScaleBrowserHost)
            host.processes = {"context": object()}
            host._exchange = AsyncMock(side_effect=lambda *args: copy.deepcopy(result))
            request = {"operation_id": "operation", "context_id": "context",
                "request_sha256": "a" * 64, "payload": {"name": "observe",
                    "arguments": {}, "evidence_path": str(root)}}
            reply = await host.call("tool", request)
            self.assertEqual(reply["result"]["captures"][0]["sha256"], sha)
            self.assertNotIn("@synthetic.test", reply["result"]["text"])
            picture.write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "capture_integrity:digest"):
                await host.call("tool", request)


class ProjectionRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_model_receives_explicit_zero_based_criteria_and_targeted_feedback(self):
        class Router:
            routes = [ModelRoute("TOKENMAXX", "TOKENMAXX/deepseek-v4.1-flash-free")]
            def report(self): return {"events": []}
            def complete(self, messages, **kwargs):
                self.projected = json.loads(messages[1]["content"])
                invalid = {"kind": "final", "judgment": {"reason": "Not tested",
                    "criteria": [{"kind": "success", "index": 2, "status": "not_run",
                        "observation": "Not tested", "observation_ids": []}]}}
                self.feedback = kwargs["quality_check"](json.dumps(invalid))
                valid = {"kind": "final", "judgment": {"reason": "Not tested",
                    "criteria": [{"kind": kind, "index": index, "status": "not_run",
                        "observation": "Not tested", "observation_ids": []}
                        for kind, index in (("success", 0), ("success", 1), ("recovery", 0))]}}
                return json.dumps(valid), {"provider": "TOKENMAXX", "requested_model": self.routes[0].model,
                    "served_model": "deepseek-v4.1-flash", "response_id": "review"}
        router = Router()
        provider = RoutedScaleProvider(ProviderSpec(key="route", protocol="callback", model="free"), router)
        await provider.call({"operation_id": "review", "context_id": "persona", "request_sha256": "a"*64,
            "payload": {"phase": "review", "observations": [],
                "task": {"success_criteria": ["A", "B"], "recovery_criteria": ["C"]}}})
        self.assertEqual([(r["kind"], r["index"]) for r in router.projected["expected_criterion_bindings"]],
            [("success", 0), ("success", 1), ("recovery", 0)])
        self.assertIn("success[0]", router.feedback)
        self.assertIn("recovery[0]", router.feedback)

    async def test_each_request_contains_one_checkpoint_without_duplicate_history(self):
        class Router:
            routes = [ModelRoute("TOKENMAXX", "TOKENMAXX/deepseek-v4.1-flash-free")]
            def __init__(self):
                self.inputs, self.events = [], []
            def complete(self, messages, **kwargs):
                self.inputs.append(copy.deepcopy(messages))
                event = {"call_id": kwargs["call_id"], "response_id": kwargs["call_id"],
                    "provider": "TOKENMAXX", "requested_model": self.routes[0].model,
                    "served_model": "deepseek-v4.1-flash", "input_tokens": 10,
                    "output_tokens": 3, "provider_cost_microusd": None,
                    "cost_basis": "provider_cost_not_reported"}
                self.events.append(event)
                return json.dumps({"kind": "tool", "tool": "observe",
                    "arguments": {}, "decision": "Observe only"}), event
            def report(self):
                return {"events": self.events}
        router = Router()
        provider = RoutedScaleProvider(ProviderSpec(key="route", protocol="callback", model="free"), router)
        payload = {"phase": "model", "observations": [
            {"id": "obs-1", "text": "Original evidence", "facts": {"controls": ["stale"], "text": "Original evidence"}},
            {"id": "obs-2", "text": "Current evidence", "facts": {"controls": ["current"], "text": "Current evidence"}}]}
        for index in range(2):
            await provider.call({"operation_id": "op-" + str(index), "context_id": "same-persona",
                "request_sha256": "a" * 64, "payload": payload})
        self.assertEqual(len(router.inputs[1]), 2)
        projected = json.loads(router.inputs[1][1]["content"])
        self.assertEqual(len(projected["observations"]), 2)
        self.assertNotIn("controls", projected["observations"][0]["facts"])
        self.assertEqual(projected["observations"][1]["facts"]["controls"], ["current"])
        self.assertEqual(payload["observations"][0]["facts"]["controls"], ["stale"])
        self.assertEqual(provider.conversations, {})


class ProtocolRecoveryTests(unittest.TestCase):
    def test_explicit_recovery_excludes_completed_personas_and_requires_closed_browsers(self):
        path = Path(__file__).resolve().parents[1] / "skills/remorsearch-ux-qa/scripts/live_scale_browser.py"
        spec = importlib.util.spec_from_file_location("recover_stage_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            stage = root / "stage-16"
            stage.mkdir()
            summary = stage / "stage-summary.json"
            summary.write_text(json.dumps({"stage_cumulative_sessions": 16, "browser_shutdown_confirmed": True}))
            summary.chmod(0o600)
            build = root / "build.json"
            build.write_bytes(b"build")
            args = SimpleNamespace(recover_stage=stage, product_id="peekly", goal="goal", target="target",
                library=root / "library", build_artifact=build, stages=[16])
            queue = SimpleNamespace(plan_sha256="a"*64, plan={"product_id": "peekly", "goal": "goal",
                "target": "target", "library_path": str(args.library),
                "build": {"sha256": hashlib.sha256(b"build").hexdigest()}})
            report = {"counts": {"running": 0}, "control": "running", "tasks": [
                {"persona_id": "done", "status": "complete", "result": {"operational_completed": True}, "current_valid": True},
                {"persona_id": "failed", "status": "uncertain", "result": None},
                {"persona_id": "waiting", "status": "queued", "result": None}]}
            with patch.object(module, "Queue", return_value=queue), patch.object(module, "current_report", return_value=report):
                selected, info = module.recovery_selection(args)
                self.assertEqual(selected, ["failed", "waiting"])
                self.assertEqual(info["retained_completed_personas"], ["done"])
                self.assertFalse(info["original_queue_modified"])
                summary.write_text(json.dumps({"browser_shutdown_confirmed": False}))
                with self.assertRaisesRegex(RuntimeError, "closed_source_browsers"):
                    module.recovery_selection(args)

    def test_live_limits_fit_the_existing_queue_ceiling(self):
        path = Path(__file__).resolve().parents[1] / "skills/remorsearch-ux-qa/scripts/live_scale_browser.py"
        spec = importlib.util.spec_from_file_location("live_scale_recovery_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for count in (4, 12, 16):
            limits = module.live_limits(count)
            self.assertEqual(limits.validate()["call_seconds"], 180)
            self.assertEqual(limits.max_model_calls, count * 17)
            self.assertEqual(limits.budget_microusd, 0)
            self.assertLess(3 * 50 + 2 + 4 + 6, limits.call_seconds)

    def test_expired_deadline_does_not_dispatch_or_count_an_attempt(self):
        calls = []
        router = ModelRouter("http://127.0.0.1:10100/v1",
            [ModelRoute("TOKENMAXX", "TOKENMAXX/deepseek-v4.1-flash-free")],
            opener=lambda *args, **kwargs: calls.append(True), respect_rpm=False)
        with patch("uxpersonas.model_router.time.time", return_value=100):
            with self.assertRaisesRegex(RuntimeError, "deadline_before_dispatch"):
                router.complete([{"role": "user", "content": "test"}], deadline=99)
        self.assertEqual(calls, [])
        self.assertEqual(router.report()["routes"][router.routes[0].model]["attempts"], 0)

    def test_error_receipt_keeps_usage_served_name_and_native_tool_diagnostic(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, size):
                return json.dumps({"id": "rejected-response", "model": "deepseek-v4.1-flash",
                    "usage": {"prompt_tokens": 9, "completion_tokens": 4, "cost": 0, "billing_source": "free"},
                    "choices": [{"message": {"content": None, "tool_calls": [{"function": {
                        "name": "unknown_tool", "arguments": "{}"}}]}}]}).encode()
        router = ModelRouter("http://127.0.0.1:10100/v1",
            [ModelRoute("TOKENMAXX", "TOKENMAXX/deepseek-v4.1-flash-free")],
            opener=lambda *args, **kw: Response(), max_retries=0)
        with patch.dict(os.environ, {"PROXY_API_KEY": "offline-test-key"}):
            with self.assertRaises(RuntimeError):
                router.complete([{"role": "user", "content": "test"}])
        event = router.report()["events"][0]
        self.assertEqual(event["native_tool_names"], ["unknown_tool"])
        self.assertEqual(event["response_id"], "rejected-response")
        self.assertEqual(event["served_model"], "deepseek-v4.1-flash")
        self.assertEqual(event["provider_reported_cost"], 0)
        self.assertEqual(event["billing_source"], "free")
        self.assertEqual(event["input_tokens"], 9)
        self.assertNotIn("offline-test-key", json.dumps(event))


if __name__ == "__main__":
    unittest.main()
