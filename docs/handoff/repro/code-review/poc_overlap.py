import sys, json
sys.path.insert(0, "/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
from uxresearch import scope
lists = scope.lists_for(scope.packaged())
def check(host):
    return {"host": host, "terms_url": "https://policy.naver.com/policy/service.html", "checked_on": "2026-09-29",
            "result": "permits_this_reading"}
for checked in ("naver.com", "cafe.naver.com"):
    policy = {"deny_hosts": [], "terms_checked": [check(checked)]}
    print("== check for", checked)
    print("  start says:", [(r["entry"], r["effect"]) for r in scope.describe_checks(policy, lists)])
    for url in ("https://cafe.naver.com/momcafe/123", "https://m.cafe.naver.com/ca-fe/web/cafes/1/articles/2",
                "https://blog.naver.com/x/1"):
        stop, lift = scope.evaluate(url, policy, lists)
        print("  ", url, "->", "STOP " + str(stop.reasons[:3]) if stop else "LIFTED entry=" + str(lift and lift["entry"]))
print("entries covering cafe.naver.com:",
      [e["id"] for e in lists.terms if any(__import__('uxresearch').verdict.host_matches("cafe.naver.com", [h]) for h in e["hosts"])])
