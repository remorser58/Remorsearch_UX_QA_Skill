import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/remorsearch-ux-qa"))
from uxpersonas.model_router import ModelRoute, ModelRouter, RoutedScaleProvider
from uxpersonas.swarm_providers import ProviderSpec

class Response:
    status = 200
    def __init__(self, value): self.value=json.dumps(value).encode()
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, size): return self.value

class RouterTests(unittest.TestCase):
    def setUp(self):
        # Every test uses a mocked HTTP opener; never depend on a developer key.
        auth = patch.dict(os.environ, {"PROXY_API_KEY": "offline-router-test-key"})
        auth.start()
        self.addCleanup(auth.stop)

    def test_usage_and_model_route_recorded(self):
        def opener(req, timeout):
            body=json.loads(req.data)
            self.assertEqual(body["model"],"TOKENMAXX/deepseek-v4.1-flash-free")
            self.assertEqual(body["response_format"],{"type":"json_object"})
            self.assertEqual(body["tool_choice"], "none")
            return Response({"id":"r1","model":"deepseek-v4.1-flash-free","choices":[{"message":{"content":"ok"}}],"usage":{"prompt_tokens":11,"completion_tokens":7}})
        router=ModelRouter("http://127.0.0.1:10100/v1",[ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free")],opener=opener)
        content, receipt=router.complete([{"role":"user","content":"test"}])
        self.assertEqual(content,"ok")
        self.assertEqual((receipt["input_tokens"],receipt["output_tokens"]),(11,7))

    def test_429_retries_then_falls_back(self):
        calls=[]; waits=[]
        def opener(req, timeout):
            model=json.loads(req.data)["model"]; calls.append(model)
            if model.startswith("TOKENMAXX"): raise HTTPError(req.full_url,429,"limited",{},None)
            return Response({"id":"r2","model":"deepseek-v4.1-flash","choices":[{"message":{"content":"ok"}}],"usage":{"prompt_tokens":9,"completion_tokens":3}})
        router=ModelRouter("http://127.0.0.1:10100/v1",[
            ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free",allowed_served_models=("deepseek-v4.1-flash-free","deepseek-v4.1-flash")),
            ModelRoute("InferHub","inferhub/combo/deepseek-4-1-flash")],opener=opener,sleep=waits.append,max_retries=1,respect_rpm=False)
        _, receipt=router.complete([{"role":"user","content":"test"}])
        self.assertEqual(receipt["provider"],"InferHub")
        self.assertEqual(len(calls),3)
        self.assertEqual(waits,[1.0])
        self.assertEqual(router.report()["routes"]["TOKENMAXX/deepseek-v4.1-flash-free"]["rate_limits"],2)

    def test_retry_after_cooldown_is_shared_and_not_clamped_to_backoff_max(self):
        waits=[]; calls=[]
        def opener(req, timeout):
            calls.append(1)
            if len(calls)==1:
                raise HTTPError(req.full_url,429,"limited",{"Retry-After":"60"},None)
            return Response({"id":"r-after","model":"deepseek-v4.1-flash-free","choices":[{"message":{"content":"ok"}}],"usage":{"prompt_tokens":1,"completion_tokens":1}})
        router=ModelRouter("http://127.0.0.1:10100/v1",[
            ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free",requests_per_minute=600,
                allowed_served_models=("deepseek-v4.1-flash-free","deepseek-v4.1-flash"))],
            opener=opener,sleep=waits.append,max_retries=1,backoff_max=5)
        _, receipt=router.complete([{"role":"user","content":"test"}])
        self.assertEqual(receipt["provider"],"TOKENMAXX")
        self.assertEqual(len(calls),2)
        self.assertTrue(any(wait>=59 for wait in waits),waits)
        self.assertEqual(router.report()["routes"]["TOKENMAXX/deepseek-v4.1-flash-free"]["rate_limits"],1)

    def test_quality_failure_uses_configured_fallback(self):
        def opener(req, timeout):
            model=json.loads(req.data)["model"]
            content="not-json" if model.startswith("TOKENMAXX") else "valid-json"
            return Response({"id":"quality","model":model,"choices":[{"message":{"content":content}}],"usage":{"prompt_tokens":5,"completion_tokens":2}})
        router=ModelRouter("http://127.0.0.1:10100/v1",[
            ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free"),
            ModelRoute("InferHub","inferhub/combo/deepseek-4-1-flash")],opener=opener,max_retries=0)
        _, receipt=router.complete([{"role":"user","content":"x"}],quality_check=lambda value:value=="valid-json")
        self.assertEqual(receipt["provider"],"InferHub")
        self.assertTrue(any(e.get("status")=="quality_rejected" for e in router.report()["events"]))

    def test_scale_provider_adapter_aggregates_all_fallback_attempt_usage(self):
        class Router:
            routes=[ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free"),
                    ModelRoute("InferHub","inferhub/combo/deepseek-4-1-flash","0.075","0.30")]
            def __init__(self): self.events=[]
            def complete(self,messages,**kwargs):
                call_id=kwargs["call_id"]
                self.events=[
                    {"call_id":call_id,"provider":"TOKENMAXX","requested_model":"TOKENMAXX/deepseek-v4.1-flash-free",
                     "served_model":"deepseek-v4.1-flash-free","response_id":"r-free","input_tokens":31,"output_tokens":9,
                     "provider_cost_microusd":0,"cost_basis":"configured_rate_estimate","status":"success"},
                    {"call_id":call_id,"provider":"TOKENMAXX","requested_model":"TOKENMAXX/deepseek-v4.1-flash-free",
                     "served_model":"deepseek-v4.1-flash-free","response_id":"r-free","input_tokens":31,"output_tokens":9,
                     "provider_cost_microusd":0,"cost_basis":"configured_rate_estimate","status":"quality_rejected"},
                    {"call_id":call_id,"provider":"InferHub","requested_model":"inferhub/combo/deepseek-4-1-flash",
                     "served_model":"deepseek-v4.1-flash","response_id":"r-paid","input_tokens":41,"output_tokens":12,
                     "provider_cost_microusd":7,"cost_basis":"configured_rate_estimate","status":"success"},
                ]
                return '{"kind":"final","judgment":{"reason":"observed","criteria":[]}}', {
                    "provider":"InferHub","requested_model":"inferhub/combo/deepseek-4-1-flash",
                    "served_model":"deepseek-v4.1-flash","response_id":"r-paid",
                    "input_tokens":41,"output_tokens":12,"provider_cost_microusd":7,"cost_basis":"configured_rate_estimate"}
            def report(self): return {"events":self.events}
        spec=ProviderSpec(key="router",protocol="callback",model="local-router",input_price_per_million=75000,
            output_price_per_million=300000,input_token_cap=262144,output_token_cap=8192)
        provider=RoutedScaleProvider(spec,Router())
        import asyncio
        request={"operation_id":"op-aggregate","context_id":"ctx-aggregate","request_sha256":"a"*64,"deadline":9999999999,
            "payload":{"phase":"model","persona":{"label":"synthetic"}}}
        reply=asyncio.run(provider.call(request))
        self.assertEqual(reply["operation_id"],"op-aggregate")
        self.assertEqual(reply["trace_id"],"r-paid")
        self.assertEqual(reply["usage"]["provider"],"InferHub+TOKENMAXX")
        self.assertEqual(reply["usage"]["model"],"deepseek-v4.1-flash+deepseek-v4.1-flash-free")
        self.assertEqual(reply["usage"]["input_tokens"],72)
        self.assertEqual(reply["usage"]["output_tokens"],21)
        self.assertEqual(reply["usage"]["provider_cost_microusd"],7)
        self.assertEqual(reply["usage"]["cost_basis"],"aggregated_rate_estimate")

    def test_local_gateway_uses_existing_proxy_api_key_without_exposing_it(self):
        from unittest.mock import patch
        seen=[]
        def opener(req, timeout):
            seen.append(req.get_header("Authorization"))
            return Response({"id":"auth-ok","model":"deepseek-v4.1-flash-free",
                "choices":[{"message":{"content":"ok"}}],
                "usage":{"prompt_tokens":2,"completion_tokens":1,"cost":0}})
        route=ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free","0","0",30,
            ("deepseek-v4.1-flash-free",))
        with patch.dict(os.environ,{"PROXY_API_KEY":"test-secret-never-print"}):
            router=ModelRouter("http://127.0.0.1:10100/v1",[route],opener=opener)
            content,receipt=router.complete([{"role":"user","content":"test"}])
        self.assertEqual(content,"ok")
        self.assertEqual(seen,["Bearer test-secret-never-print"])
        self.assertEqual(receipt["provider_cost_microusd"],0)
        self.assertNotIn("test-secret-never-print",json.dumps(router.report()))

    def test_tokenmaxx_free_selector_accepts_two_documented_served_names_and_preserves_cost(self):
        from unittest.mock import patch
        for served, usage in (
            ("deepseek-v4.1-flash-free", {"prompt_tokens":3,"completion_tokens":2,"cost":0,"billing_source":"free"}),
            ("deepseek-v4.1-flash", {"prompt_tokens":4,"completion_tokens":2}),
        ):
            with self.subTest(served=served):
                route=ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free","0","0",30)
                def opener(req, timeout):
                    body=json.loads(req.data)
                    self.assertEqual(body["model"],"TOKENMAXX/deepseek-v4.1-flash-free")
                    self.assertEqual(body["response_format"],{"type":"json_object"})
                    return Response({"id":"response-"+served,"model":served,
                        "choices":[{"message":{"content":"ok"}}],"usage":usage})
                with patch.dict(os.environ,{"PROXY_API_KEY":"test-secret"}):
                    router=ModelRouter("http://127.0.0.1:10100/v1",[route],opener=opener)
                    content,receipt=router.complete([{"role":"user","content":"test"}])
                self.assertEqual(content,"ok")
                self.assertEqual(receipt["served_model"],served)
                self.assertEqual(receipt.get("provider_reported_cost"),usage.get("cost"))
                self.assertEqual(receipt.get("billing_source"),usage.get("billing_source"))
                self.assertEqual(receipt["provider_cost_microusd"],0 if "cost" in usage else None)

    def test_tokenmaxx_structured_tool_call_is_normalized_to_reviewed_envelope(self):
        from unittest.mock import patch
        route=ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free","0","0",30,
            ("deepseek-v4.1-flash",))
        def opener(req,timeout):
            body=json.loads(req.data)
            self.assertEqual(body["response_format"],{"type":"json_object"})
            return Response({"id":"tool-call","model":"deepseek-v4.1-flash",
                "choices":[{"finish_reason":"tool_calls","message":{"role":"assistant","content":None,
                    "tool_calls":[{"id":"call-1","type":"function","function":{"name":"click",
                        "arguments":"{\"selector\":\"#sample\",\"label\":\"샘플\"}"}}]}}],
                "usage":{"prompt_tokens":5,"completion_tokens":8}})
        with patch.dict(os.environ,{"PROXY_API_KEY":"test-secret"}):
            router=ModelRouter("http://127.0.0.1:10100/v1",[route],opener=opener)
            content,receipt=router.complete([{"role":"user","content":"test"}])
        self.assertEqual(json.loads(content),{"kind":"tool","tool":"click",
            "arguments":{"selector":"#sample","label":"샘플"},
            "decision":"Model selected the tool from the current observations."})
        self.assertEqual(receipt["served_model"],"deepseek-v4.1-flash")

    def test_tokenmaxx_flash_1m_is_not_an_allowed_route(self):
        from unittest.mock import patch
        called=[]
        route=ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-1m","0","0",30,
            ("TOKENMAXX/deepseek-v4.1-flash-1m",))
        def opener(req,timeout):
            called.append(True)
            return Response({"id":"wrong","model":"deepseek-v4.1-flash-1m",
                "choices":[{"message":{"content":"no"}}],"usage":{"prompt_tokens":1,"completion_tokens":1}})
        with patch.dict(os.environ,{"PROXY_API_KEY":"test-secret"}):
            router=ModelRouter("http://127.0.0.1:10100/v1",[route],opener=opener)
            with self.assertRaises(RuntimeError): router.complete([{"role":"user","content":"test"}])
        self.assertEqual(called,[True])
        self.assertEqual(router.report()["events"][0]["status"],"served_model_mismatch")

    def test_missing_local_gateway_key_fails_before_dispatch(self):
        from unittest.mock import patch
        called=[]
        route=ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free")
        with patch.dict(os.environ,{},clear=True):
            router=ModelRouter("http://127.0.0.1:10100/v1",[route],opener=lambda *a,**k:called.append(True))
            with self.assertRaisesRegex(RuntimeError,"local_opencodex_auth_unavailable"):
                router.complete([{"role":"user","content":"test"}])
        self.assertEqual(called,[])

    def test_free_route_rejects_unapproved_served_model_without_fallback(self):
        route=ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free","0","0",30,
            ("TOKENMAXX/deepseek-v4.1-flash-free","deepseek-v4.1-flash-free"))
        router=ModelRouter("http://127.0.0.1:10100/v1",[route],
            opener=lambda *a,**k: Response({"id":"wrong-model","model":"deepseek-v4.1-flash-1m",
                "choices":[{"message":{"content":"should-not-run"}}],
                "usage":{"prompt_tokens":17,"completion_tokens":5}}),max_retries=2)
        with self.assertRaises(RuntimeError):
            router.complete([{"role":"user","content":"x"}])
        report=router.report()
        self.assertEqual(report["fallback_order"],["TOKENMAXX/deepseek-v4.1-flash-free"])
        self.assertEqual(report["events"][0]["status"],"served_model_mismatch")
        self.assertEqual(report["events"][0]["input_tokens"],17)
        self.assertEqual(report["events"][0]["output_tokens"],5)

    def test_rejects_remote_endpoint_and_missing_usage(self):
        with self.assertRaises(ValueError): ModelRouter("https://remote.invalid/v1",[ModelRoute("x","m")])
        router=ModelRouter("http://127.0.0.1:10100/v1",[ModelRoute("x","m")],
            opener=lambda *a,**k: Response({"choices":[{"message":{"content":"ok"}}]}),max_retries=0)
        with self.assertRaises(RuntimeError): router.complete([{"role":"user","content":"x"}])

if __name__ == "__main__": unittest.main()
