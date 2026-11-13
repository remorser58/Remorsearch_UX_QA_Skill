"""Offline regressions for final-judgment binding errors in the live cohort."""
import copy
import json
import unittest

import _paths
from uxpersonas.model_router import ModelRoute, RoutedScaleProvider
from uxpersonas.swarm_providers import ProviderSpec


def decision():
    return {"kind": "final", "judgment": {"reason": "Not exercised.",
        "criteria": [{"kind": kind, "index": index, "status": "not_run",
            "observation": "Not exercised.", "observation_ids": []}
            for kind, index in [("success", 0), ("success", 1), ("recovery", 0)]]}}


class BindingTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, invalid, reason):
        case = self
        class Router:
            routes = [ModelRoute("TOKENMAXX", "TOKENMAXX/deepseek-v4.1-flash-free")]
            def __init__(self): self.events = []; self.projected = None
            def complete(self, messages, **options):
                self.projected = json.loads(messages[1]["content"])
                case.assertIn(reason, options["quality_check"](json.dumps(invalid)))
                value = decision()
                case.assertIs(options["quality_check"](json.dumps(value)), True)
                receipt = {"call_id": options["call_id"], "response_id": "offline-reply",
                    "provider": "TOKENMAXX", "requested_model": self.routes[0].model,
                    "served_model": "deepseek-v4.1-flash", "input_tokens": 12,
                    "output_tokens": 6, "provider_cost_microusd": None,
                    "cost_basis": "provider_cost_not_reported", "status": "success"}
                self.events.append(receipt)
                return json.dumps(value), receipt
            def report(self): return {"events": self.events}
        router = Router()
        provider = RoutedScaleProvider(ProviderSpec(key="local-router", protocol="callback", model="free"), router)
        request = {"operation_id": "offline-op", "context_id": "offline-context",
            "request_sha256": "a" * 64, "payload": {"phase": "model", "observations": [],
            "task": {"success_criteria": ["A", "B"], "recovery_criteria": ["Recovery"]}}}
        before = copy.deepcopy(request)
        reply = await provider.call(request)
        self.assertEqual(request, before)
        self.assertEqual(reply["result"], decision())
        self.assertEqual(router.projected["final_criterion_bindings"], [
            {"kind": "success", "index": 0, "requirement": "A"},
            {"kind": "success", "index": 1, "requirement": "B"},
            {"kind": "recovery", "index": 0, "requirement": "Recovery"}])

    async def test_recovery_index_is_independent_not_global(self):
        invalid = decision(); invalid["judgment"]["criteria"][-1]["index"] = 2
        await self.exercise(invalid, "criterion_binding_expected")

    async def test_string_index_is_not_silently_coerced(self):
        invalid = decision(); invalid["judgment"]["criteria"][0]["index"] = "0"
        await self.exercise(invalid, "criterion_binding_expected")

    async def test_duplicate_and_missing_bindings_remain_rejections(self):
        invalid = decision(); invalid["judgment"]["criteria"][-1] = copy.deepcopy(invalid["judgment"]["criteria"][0])
        await self.exercise(invalid, "criterion_binding_duplicate")
        missing = decision(); missing["judgment"]["criteria"].pop()
        await self.exercise(missing, "criterion_bindings_missing")

    async def test_invalid_status_is_not_rewritten_as_passed(self):
        invalid = decision(); invalid["judgment"]["criteria"][0]["status"] = "pass"
        await self.exercise(invalid, "criterion_status_requires")
