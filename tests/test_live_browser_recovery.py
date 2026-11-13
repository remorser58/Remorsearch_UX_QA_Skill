"""Offline regressions for failures observed in the real Peekly run."""
import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import _paths
from uxpersonas import swarm
from uxpersonas.model_router import ModelRoute, ModelRouter, RoutedScaleProvider
from uxpersonas.scale_browser_host import ScaleBrowserHost
from uxpersonas.swarm_providers import ProviderSpec


class CaptureRecoveryTests(unittest.IsolatedAsyncioTestCase):
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
