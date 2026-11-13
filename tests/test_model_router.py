import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/remorsearch-ux-qa"))
from uxpersonas.model_router import ModelRoute, ModelRouter

class Response:
    status = 200
    def __init__(self, value): self.value=json.dumps(value).encode()
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, size): return self.value

class RouterTests(unittest.TestCase):
    def test_usage_and_model_route_recorded(self):
        def opener(req, timeout):
            body=json.loads(req.data)
            self.assertEqual(body["model"],"TOKENMAXX/deepseek-v4.1-flash-free")
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
            ModelRoute("TOKENMAXX","TOKENMAXX/deepseek-v4.1-flash-free"),
            ModelRoute("InferHub","inferhub/combo/deepseek-4-1-flash")],opener=opener,sleep=waits.append,max_retries=1)
        _, receipt=router.complete([{"role":"user","content":"test"}])
        self.assertEqual(receipt["provider"],"InferHub")
        self.assertEqual(len(calls),3)
        self.assertEqual(waits,[1.0])
        self.assertEqual(router.report()["routes"]["TOKENMAXX/deepseek-v4.1-flash-free"]["rate_limits"],2)

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

    def test_rejects_remote_endpoint_and_missing_usage(self):
        with self.assertRaises(ValueError): ModelRouter("https://remote.invalid/v1",[ModelRoute("x","m")])
        router=ModelRouter("http://127.0.0.1:10100/v1",[ModelRoute("x","m")],
            opener=lambda *a,**k: Response({"choices":[{"message":{"content":"ok"}}]}),max_retries=0)
        with self.assertRaises(RuntimeError): router.complete([{"role":"user","content":"x"}])

if __name__ == "__main__": unittest.main()
