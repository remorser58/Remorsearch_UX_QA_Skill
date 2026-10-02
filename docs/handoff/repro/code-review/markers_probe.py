import sys
sys.path.insert(0, "/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
from uxresearch import verdict
def flags(text, title=""):
    f = verdict.content_flags(text, title)
    return ([(h["marker"], h["family"], h["position"]) for h in f["promotion_hits"]]
            + [(h["marker"], h["kind"], h["position"]) for h in f["incentive_flags"]]
            + [(h["marker"], "virtual", h["position"]) for h in f["virtual_person_flags"]])
filler = "충전 화면을 써 봤는데 버튼이 늦게 반응해서 불편했습니다. " * 12
cases = [
 # negations that should NOT be flagged
 "협찬 받지 않았습니다. 직접 샀어요.",
 "#광고 아님, 내돈내산",
 "광고인가요? 궁금해요",
 "경제적 대가를 받지 않고 작성한 솔직 후기입니다.",
 "경제적 대가를 받은 적 없는 솔직 후기입니다.",
 "경제적 대가를 받은 것이 아닌 내돈내산 후기",
 "업체로부터 제품을 제공받은 것이 아니라 직접 구매했습니다.",
 "제품을 제공받아 쓴 글이 아니에요. 직접 샀어요.",
 "제품을 제공받았다는 오해가 있는데 직접 샀습니다.",
 "원고료를 지급받지 않았고 직접 구매했습니다",
 "협찬받았습니다만 거짓말이고 직접 샀어요",
 "무상으로 제공받았으면 좋겠네요 ㅋㅋ",
 "혹시 협찬 받았어요",
 "#협찬 없이 내돈내산",
 "#협찬X 내돈내산",
 "#협찬✕",
 "광고 아닙니다",
 # positives that SHOULD be flagged (spacing, full-width, line breaks)
 "이 글은 업체로부터 제품을 제공받아 작성했습니다.",
 "경제적대가를받아 작성했습니다.",
 "경제적 대가를\n받아 작성",
 "＃협찬 받았어요",
 "＃광고 제품 리뷰",
 "［광고］ 충전기 후기",
 "（협찬） 충전기 후기",
 "#ＡＤ new charger",
 "협찬을\n받아 작성했습니다",
 "협 찬 받아 작성",
 "#광 고",
 filler + "이 포스팅은 광고입니다",
 "광고입니다 " + filler,
 filler + "이 포스팅은 광고입니다" + filler,
 "[가상인물] 이 모델은 AI입니다",
 "가상인간 광고 싫어요",
]
for c in cases:
    shown = c if len(c) < 60 else c[:25] + "..." + c[-25:]
    print(f"{shown!r:70} -> {flags(c)}")
