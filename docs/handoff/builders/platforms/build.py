"""Single source of truth for uxresearch/data/korea-platforms.json and the generated
parts of references/research/korea/platform-map.md (ids, order and URL set identical).

Every fact below was checked on 2026-09-29/30 from this session with WebSearch (search-result
summaries, some restricted to the operator's own domain), one direct read of Naver's own GitHub
swagger, and the legal lane's mirror copy of the PIPA text. No community site and no platform
terms page could be opened directly (egress policy), so nearly everything is labelled
미확인(요약)."""

import json
import pathlib
import re
import sys

SKILL = pathlib.Path("/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
JSON_OUT = SKILL / "uxresearch/data/korea-platforms.json"
MD_OUT = SKILL / "references/research/korea/platform-map.md"
HERE = pathlib.Path(__file__).parent

CHECKED = "2026-09-29"

# ---------------------------------------------------------------- sources
U = {
    # Naver: robots, terms, API
    "etnews_ai_block": "https://www.etnews.com/20250716000347",
    "daum_ai_block": "https://v.daum.net/v/20250716143440337",
    "naver_terms": "https://policy.naver.com/rules/service.html",
    "nate_naver_terms_2024": "https://news.nate.com/view/20241028n06350",
    "naver_terms_quote": "https://github.com/EST-team-project/Qurious/issues/57",
    "mt_naver_terms_2025": "https://www.mt.co.kr/tech/2025/07/10/2025071010042598666",
    "nate_naver_terms_2025": "https://news.nate.com/view/20250711n01759",
    "newsway_api_terms": "https://www.newsway.co.kr/news/view?ud=2026090215314059117",
    "tokenpost_api_terms": "https://www.tokenpost.kr/news/ai/403521",
    "dataeconomy_api_terms": "https://www.dataeconomy.co.kr/news/articleView.html?idxno=42307",
    "hub_pr": "https://github.com/Mode1221/CoursePilot/pull/406",
    "hub_guide": "https://waffleboard.io/blog/naver-search-api-hub-migration-guide",
    "naver_openapi_swagger": "https://github.com/naver/naver-openapi-guide/blob/master/ko/naver-openapi-swagger.yaml",
    # Naver blog
    "daum_blog_report": "https://v.daum.net/v/20251222105605977",
    "zdnet_blog_report": "https://zdnet.co.kr/view/?no=20251222220821",
    "fnnews_blog_mz": "https://www.fnnews.com/news/202511071741487257",
    "hk_blog_feed": "https://www.hankyung.com/article/202512155313g",
    # KFTC
    "kftc_2024_monitoring": "https://www.korea.kr/briefing/pressReleaseView.do?newsId=156679064",
    "zdnet_kftc_2024": "https://zdnet.co.kr/view/?no=20250317092935",
    "kftc_2024_revision": "https://www.korea.kr/briefing/pressReleaseView.do?newsId=156660604",
    # Naver Cafe
    "newsis_cafe_notice": "https://www.newsis.com/view/NISX20260831_0003769836",
    "daum_cafe_notice": "https://v.daum.net/v/20260831151156866",
    "wiseapp_sns_2026": "https://www.wiseapp.co.kr/insight/detail/997",
    "platum_sns_2026": "https://platum.kr/archives/286798",
    "hk_momcafe_2020": "https://www.hankyung.com/society/article/2020100565571",
    "sbs_momcafe": "https://news.sbs.co.kr/news/endPage.do?news_id=N1006281658",
    "nate_momcafe_smear": "https://news.nate.com/view/20260419n07489",
    # Naver KnowledgeiN
    "byline_kin_2022": "https://byline.network/2022/10/%EC%A7%80%EC%8B%9Din-%EC%82%B4%EC%95%84%EC%9E%88%EB%84%A4-%EC%8B%A0%EA%B7%9C-%EC%82%AC%EC%9A%A9%EC%9E%90-56%EA%B0%80-1020/",
    "zdnet_kin_2022": "https://zdnet.co.kr/view/?no=20221006105245",
    "newspim_kin_2024": "https://www.newspim.com/news/view/20240425000333",
    "mt_kin_2024": "https://www.mt.co.kr/tech/2024/04/25/2024042509581150389",
    "newstree_kin_ai": "https://www.newstree.kr/newsView/ntr202408290017",
    "newsis_kin_ai_end": "https://www.newsis.com/view/NISX20260427_0003608405",
    "hk_kin_2026": "https://www.hankyung.com/article/2026042453671",
    "asiae_kin_incident": "https://www.asiae.co.kr/article/2026020517015841527",
    "daum_kin_incident": "https://v.daum.net/v/20260205143407660",
    # Naver Place
    "naver_place_release": "https://www.navercorp.com/media/pressReleasesDetail?seq=10034317",
    "newspim_place_2026": "https://www.newspim.com/news/view/20260601001153",
    "edaily_place_2026": "https://edaily.co.kr/News/Read?mediaCodeNo=257&newsId=03325926645477456",
    "etnews_place_2026": "https://www.etnews.com/20260715000174",
    "daum_place_policy": "https://v.daum.net/v/20260331161500211",
    "fnnews_place_2021": "https://www.fnnews.com/news/202110271247564428",
    "iboss_place_2025": "https://www.i-boss.co.kr/ab-6141-66992",
    # app panels
    "wiseapp_apps_2025": "https://www.wiseapp.co.kr/insight/detail/884/2025-top-user-time-sessions-app-trend",
    "kbench_apps_2025": "https://kbench.com/?q=node%2F274790",
    # Kakao Map
    "mt_kakaomap_web": "https://www.mt.co.kr/amp/tech/2025/03/15/2025031418022011568",
    "daum_kakaomap_web": "https://v.daum.net/v/20250315080001376",
    "kakao_local_api": "https://developers.kakao.com/docs/latest/en/local/dev-guide",
    # Daum
    "daum_cafe_help1": "https://cs.daum.net/faq/service/15/category/4122/detail/29058",
    "daum_cafe_help2": "https://cs.daum.net/faq/service/36/category/6029/detail/32516",
    "daum_axz": "https://v.daum.net/v/20251201111330982",
    "kyeonggi_axz": "https://www.kyeonggi.com/article/20251201580062",
    "fnnews_upstage_done": "https://www.fnnews.com/news/202605070819041556",
    "asiae_upstage_done": "https://view.asiae.co.kr/article/2026050708124400944",
    "etoday_daum_rename": "https://www.etoday.co.kr/news/view/2607642",
    "asiae_daum_rename": "https://view.asiae.co.kr/article/2026072709372724707",
    "aitimes_daum_rename": "https://www.aitimes.com/news/articleView.html?idxno=213198",
    "hk_portal_ai": "https://www.hankyung.com/article/2026092800641",
    "seoulfn_portal_ai": "https://www.seoulfn.com/news/articleView.html?idxno=638901",
    # DC Inside
    "koreaherald_dc": "https://www.koreaherald.com/article/10416369",
    "dc_terms": "https://nstatic.dcinside.com/dc/w/policy/policy_index.html",
    "dc_terms_mobile": "https://nstatic.dcinside.com/dc/m/policy/policy.html",
    "daum_dc_sale": "https://v.daum.net/v/20260209160127574",
    "kmnanews_dc_sale": "https://www.kmnanews.com/news/articleView.html?idxno=10005",
    # corpus study
    "plos_hate": "https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0300530",
    "pubmed_hate": "https://pubmed.ncbi.nlm.nih.gov/38709721/",
    # FM Korea
    "fmkorea_rules": "https://www.fmkorea.com/567222051",
    "fmkorea_terms": "https://www.fmkorea.com/policy",
    "fmkorea_best": "https://www.fmkorea.com/best",
    "mediaus_fmkorea": "https://www.mediaus.co.kr/news/articleView.html?idxno=197845",
    # theqoo, Nate Pann, Clien, Ruliweb, Instiz
    "namu_theqoo": "https://namu.wiki/w/%EB%8D%94%EC%BF%A0",
    "kci_pann": "https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART002317859",
    "clien_guide": "https://www.clien.net/service/board/park/18388326",
    "clien_boards": "https://m.clien.net/service/group/community",
    "kowiki_ruliweb": "https://ko.wikipedia.org/wiki/%EB%A3%A8%EB%A6%AC%EC%9B%B9",
    "namu_instiz": "https://namu.wiki/w/%EC%9D%B8%EC%8A%A4%ED%8B%B0%EC%A6%88",
    "appstore_instiz": "https://apps.apple.com/kr/app/%EC%9D%B8%EC%8A%A4%ED%8B%B0%EC%A6%88-%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD-%EC%B5%9C%EB%8C%80%EC%9D%98-%EC%97%B0%EC%98%88-%EC%98%A4%EB%9D%BD-%EC%BB%A4%EB%AE%A4%EB%8B%88%ED%8B%B0/id1218109903",
    # Blind, Everytime, Band
    "mt_blind": "https://www.mt.co.kr/future/2025/03/12/2025031209550036521",
    "edaily_blind": "https://edaily.co.kr/News/Read?mediaCodeNo=257&newsId=02118886642102664",
    "namu_everytime": "https://namu.wiki/w/%EC%97%90%EB%B8%8C%EB%A6%AC%ED%83%80%EC%9E%84/%ED%95%99%EC%83%9D%20%EC%BB%A4%EB%AE%A4%EB%8B%88%ED%8B%B0",
    "wiseapp_age_2026": "https://www.wiseapp.co.kr/insight/detail/956/app-usage-ranking-by-age",
    "daum_age_apps": "https://v.daum.net/v/20260331101146406",
    "gallup_media_2025": "https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=1586",
    "kpf_sns_2024": "https://www.kpf.or.kr/front/board/boardContentsView.do?board_id=246&contents_id=940a3bc4be914ac2a065b8922021728e",
    "journalist_kpf_2024": "http://m.journalist.or.kr/m/m_article.html?no=57805",
    # Danggeun
    "wiseapp_resale_2025": "https://www.wiseapp.co.kr/insight/detail/848/secondhand-resale-app-trend-2025-carrot-bunjang-joonggonara",
    "datanews_daangn_2026": "https://datanews.co.kr/news/article.html?no=146423",
    # YouTube
    "yt_terms": "https://www.youtube.com/static?template=terms",
    "yt_commentthreads": "https://developers.google.com/youtube/v3/docs/commentThreads/list",
    "yt_getting_started": "https://developers.google.com/youtube/v3/getting-started",
    "yt_quota_cost": "https://developers.google.com/youtube/v3/determine_quota_cost",
    "yt_dev_policies": "https://developers.google.com/youtube/terms/developer-policies",
    # Meta
    "meta_adc": "https://www.facebook.com/legal/automated_data_collection_terms",
    "ig_terms": "https://help.instagram.com/581066165581870/",
    "threads_terms": "https://help.instagram.com/769983657850450",
    "meta_research_tools": "https://about.fb.com/news/2023/11/new-tools-to-support-independent-research/",
    "icpsr_meta": "https://www.icpsr.umich.edu/sites/icpsr/news/icpsr-to-facilitate-researcher-access-to-metas-api-products",
    "meta_mcl": "https://transparency.meta.com/researchtools/meta-content-library",
    "threads_keyword_api": "https://developers.facebook.com/docs/threads/keyword-search/",
    "herald_threads": "https://biz.heraldcorp.com/article/10546627",
    "daum_threads_banmal": "https://v.daum.net/v/3bSk2vLxgE?f=p",
    "tc_threads_com": "https://techcrunch.com/2025/04/24/threads-officially-moves-to-threads-com-and-updates-its-web-app/",
    # stores
    "devto_appstore_rss": "https://dev.to/antonio_fernandorincond/how-to-pull-app-store-reviews-via-apples-official-rss-feed-no-api-key-1hkk",
    "asc_customer_reviews": "https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps-_id_-customerreviews",
    "gallup_phone_2025": "https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=1566",
    "datanews_phone_2025": "https://www.datanews.co.kr/news/article.html?no=139581",
    "daum_phone_2025": "https://v.daum.net/v/20250708091125354",
    "mtn_kakaotalk_play": "https://news.mtn.co.kr/news-detail/2025100215420069531",
    "daum_kakaotalk_redesign": "https://v.daum.net/v/20250928072646243",
    "play_reviews_list": "https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/list",
    "play_reply_reviews": "https://developers.google.com/android-publisher/reply-to-reviews",
    "google_terms": "https://policies.google.com/terms/embedded?hl=en-US",
    # Coupang
    "byline_coupang_robots": "https://byline.network/2026/04/27_1928774/",
    "digitalmarketer_coupang": "https://www.digitalmarketer.co.kr/insights/coupang-robots-txt-partners-strategy",
    "coupang_terms": "https://www.coupang.com/np/policies/terms",
    "aboutcoupang_terms": "https://www.aboutcoupang.com/ko/terms/",
    "hk_coupang_kftc": "https://www.hankyung.com/article/202408078618g",
    "newsis_coupang_suit": "https://www.newsis.com/view/NISX20241014_0002918847",
    "economist_coupang_stay": "https://economist.co.kr/article/view/ecn202502200054",
    # delivery apps
    "kmib_kca_delivery": "https://www.kmib.co.kr/article/view.asp?arcid=0020341507",
    "daum_kca_delivery": "https://v.daum.net/v/20240723120031511",
    "khan_kca_delivery": "https://www.khan.co.kr/article/202407240600005",
    # law (section 4 only)
    "law_pipa": "https://www.law.go.kr/법령/개인정보보호법",
    "mirror_pipa": "https://raw.githubusercontent.com/legalize-kr/legalize-kr/main/kr/개인정보보호법/법률.md",
}

# How each claim was read. The Korean labels follow the pack's shared convention
# (references/research/korea/promotion.md, statistics.md, query-craft.md).
READ_VIA = {
    "direct_fetch": "관찰됨",
    "search_index": "미확인(요약)",
    "search_summary": "미확인(요약)",
    "third_party_quote": "미확인(요약)",
    "mirror": "미확인(미러)",
    "not_found": "미확인",
    "inference": "추론",
    "skill_rule": "규칙",
}

PPA = "references/research/public-page-access.md"
PROMO = "references/research/korea/promotion.md"
QUERY = "references/research/korea/query-craft.md"
REPORT = "references/research/korea/report-template.md"
LEGAL = "references/research/korea/legal-checklist.md"
ROUTES = "uxresearch/data/routes.json"
GRADING = "references/research/source-grading.md"
SELF = "references/research/korea/platform-map.md"


def C(text, via, *keys):
    """A claim with its sources."""
    assert via in READ_VIA and via != "skill_rule", via
    if via in ("inference", "not_found"):
        assert not keys, text
    else:
        assert keys, text
    return {"text": text, "read_via": via, "sources": [U[k] for k in keys]}


def R(text, ref):
    """A rule of this skill, with the document that holds it."""
    return {"text": text, "read_via": "skill_rule", "sources": [], "rule_ref": ref}


def D(date, what, via, *keys):
    item = C(what, via, *keys)
    return {"date": date, "what": item["text"], "read_via": via, "sources": item["sources"]}


def robots(expectation, item):
    return {"expectation": expectation, **item}


def terms(status, restricts, via, note, *keys, clause=None, terms_url=None, entry=None, rule_ref=None):
    assert status in ("reported", "confirmed", "checked_by_user", "unchecked")
    assert (entry is not None) == (status in ("reported", "confirmed")), (status, entry)
    assert via in READ_VIA, via
    assert (via == "skill_rule") == (rule_ref is not None), (via, rule_ref)
    assert bool(keys) == (via not in ("skill_rule", "inference", "not_found")), (via, keys)
    item = {"status": status, "routes_entry": entry, "restricts": restricts, "terms_url": terms_url,
            "clause": clause, "read_via": via, "sources": [U[k] for k in keys], "note": note}
    if rule_ref:
        item["rule_ref"] = rule_ref
    return item


def audience(text, confidence, via, *keys):
    item = C(text, via, *keys)
    return {"text": item["text"], "confidence": confidence, "read_via": via, "sources": item["sources"]}


# ---------------------------------------------------------------- shared items
LIFT_NOTE = ("사용자가 약관을 직접 읽고 브리프의 access_policy.terms_checked에 result permits_this_reading으로 적은 "
             "실행에서만 요청함. 풀린 호스트는 실행당 문서 10건까지 읽음.")

NAVER_API_OFF = C(
    "네이버 검색 API와 NAVER API HUB는 꺼 둠(소유자가 현행 약관을 읽기 전까지). 2026-09-07 시행으로 보도된 검색 API "
    "특약은 네이버 검색 결과를 보여 주는 용도로만 쓰게 하고, 결과를 AI에 넣거나 학습·개선·평가·노출에 쓰는 행위, "
    "복사·저장·캐싱, 제3자 제공·판매, 광고 수익화를 금지함.",
    "search_summary", "newsway_api_terms", "tokenpost_api_terms", "dataeconomy_api_terms")
NAVER_API_HUB = C(
    "검색 API는 NAVER API HUB(네이버 클라우드 플랫폼)로 옮겨 감. 개발자센터의 신규 키 발급은 2026-07-31에 끝났고 "
    "기존 키는 2027-06-30까지만 동작한다고 알려짐.",
    "search_summary", "hub_pr", "hub_guide")

NAVER_API_DATES = [
    D("2026-07-31", "네이버 검색 API 신규 키 발급 종료, NAVER API HUB로 이전", "search_summary", "hub_pr", "hub_guide"),
    D("2026-09-07", "네이버 검색 API 특약 개정 시행 보도: 결과를 AI에 넣거나 저장·제3자 제공하는 행위 금지",
      "search_summary", "newsway_api_terms", "tokenpost_api_terms"),
    D("2027-06-30", "개발자센터에서 받은 기존 네이버 검색 API 키 종료 예정", "search_summary", "hub_pr"),
]
KFTC_2024_RULE = D(
    "2024-12-01", "블로그·카페 추천·보증 글의 이해관계 표시를 제목이나 첫 부분에 두도록 한 공정위 지침 개정 시행",
    "search_index", "kftc_2024_revision")
NAVER_TERMS_2025 = D(
    "2025-07-10", "네이버 이용약관 개정 시행: 사용자가 삭제·비공개로 돌린 글은 그 뒤 AI 연구 개발에 쓰지 않는다는 내용 보도",
    "search_summary", "mt_naver_terms_2025", "nate_naver_terms_2025")
NAVER_ROBOTS_2025 = D(
    "2025-07", "네이버 블로그·카페 등에서 AI 봇 크롤링을 robots.txt로 막는다는 보도", "search_summary",
    "etnews_ai_block", "daum_ai_block")

NAVER_TERMS = terms(
    "reported", ["automated_collection"], "search_summary",
    "약관 원문은 이 환경에서 열리지 않음(미확인). routes.json의 naver-terms 항목과 같은 상태임. 사용자가 약관을 직접 "
    "읽고 브리프에 기록하기 전까지 요청하지 않음.",
    "nate_naver_terms_2024", "naver_terms_quote", "naver_terms",
    clause="2024-10-28 보도가 인용한 네이버 약관: 네이버 서비스로 쌓이는 데이터베이스를 robots.txt 같은 장치로 "
           "보호하며, robots.txt로 보호되는 데이터베이스를 네이버 로봇이 아닌 다른 검색 로봇이 수집하는 것을 허락하지 "
           "않음. 네이버의 사전 허락 없이 자동화된 수단(매크로, 로봇, 스파이더, 스크래퍼)으로 회원의 게시물 등을 "
           "수집하는 행위를 금지한다는 제3자 인용도 있으나 이번 확인에서 다시 열지 못함.",
    terms_url=U["naver_terms"], entry="naver-terms")

NAVER_ROBOTS = robots("unknown", C(
    "실시간 robots 확인 전까지 모름. 2025-07 보도에 따르면 네이버는 블로그에서 OpenAI, Perplexity, Google, "
    "Anthropic(Claude), Meta, Apple의 AI 봇을, 카페에서는 여기에 더해 Amazon과 Microsoft Bing의 AI 봇을 robots.txt로 "
    "막음. 보도가 이름을 댄 봇은 학습·검색 크롤러이며, 이런 그룹은 기록용 신호(ai_training_disallow)일 뿐 중단 사유가 "
    "아님. 사용자 요청으로 페이지를 여는 AI 에이전트 토큰을 막는지는 미확인. 약관 제한이 먼저 멈추므로 robots는 제한이 "
    "풀린 실행에서만 확인함.",
    "search_summary", "etnews_ai_block", "daum_ai_block"))

UNKNOWN_ROBOTS = robots("unknown", C("보고된 robots 정보를 찾지 못함. 실행 때 robots 확인이 판정함.", "not_found"))
NOT_REACHED_OOS = robots("not_reached", R("out_of_scope 채널이라 요청하지 않음.", ROUTES))
NOT_REACHED_CONFIRMED = robots("not_reached", R("약관 제한(confirmed)이 요청 전에 멈추므로 이 호스트의 robots.txt를 "
                                                 "요청하지 않음.", ROUTES))

NO_AUDIENCE = "공개 사용자 구성 자료를 이번 확인에서 찾지 못함. 커뮤니티 성별·연령·정치 성향 추정치는 싣지 않음(4절)."

STD_PRIVACY = R("작성자 이름·닉네임은 author-key로 바꾸고, 글 URL은 번들의 source_ref에만 둠. 인용은 300자 이하이고 "
                "풀어 쓰기를 먼저 씀.", PPA)
ANON_THREAD = R("로그인 없는 익명 게시판은 사람 단위가 아니라 스레드 단위로 셈.", GRADING)
PUBLIC_ONLY = R("공개 페이지만 읽음. 로그인, 회원 전용, 사람 확인, 속도 제한이 나오면 그 자리에서 멈추고 수집 공백으로 "
                "적음.", PPA)
STORE_SPIKES = C("스토어 리뷰는 업데이트나 장애 직후 몰림. 리뷰가 몰린 기간은 사용성 발견이 아니라 맥락이며, 날짜 구간을 "
                 "나눠 읽음.", "inference")
DAUM_OPERATOR = [
    D("2025-12-01", "카카오가 다음 서비스(카페·티스토리 포함) 운영을 자회사 AXZ로 넘김", "search_summary", "daum_axz",
      "kyeonggi_axz"),
    D("2026-05-07", "업스테이지가 AXZ 인수를 마침(보도)", "search_summary", "fnnews_upstage_done", "asiae_upstage_done"),
    D("2026-07-27", "AXZ가 사명을 '주식회사 다음'으로 바꿨다고 발표(2026-07-20 임시주주총회 의결)", "search_summary",
      "etoday_daum_rename", "asiae_daum_rename", "aitimes_daum_rename"),
    D("2026-09-28", "다음이 외부 AI 크롤링 허용 범위를 다시 정하는 중이라는 보도(시행일 미확인)", "search_summary",
      "hk_portal_ai", "seoulfn_portal_ai"),
]
DAUM_ROBOTS = robots("unknown", C(
    "실시간 robots 확인 전까지 모름. 2026-09-28 보도: 다음이 포털·카페·티스토리 공개 글을 외부 AI가 가져가는 범위를 "
    "다시 정하는 중이며, AI 검색·학습 크롤러와 AI 답변 에이전트까지 막는 방향이라고 함(시행일 미확인). 시행되면 "
    "사용자 요청으로 페이지를 여는 에이전트 그룹도 막힐 수 있음(추론).",
    "search_summary", "hk_portal_ai", "seoulfn_portal_ai"))

KAKAOTALK_DATE = D("2025-09-23", "카카오톡 대규모 개편 직후 두 스토어 평점이 급락함(보도 시점마다 수치가 다름)",
                   "search_summary", "mtn_kakaotalk_play", "daum_kakaotalk_redesign")

INCENTIVE_RULE = R("리뷰 보상 표시가 있는 리뷰는 만족·선호·반대 근거 검색·별점 평균에서 D까지만 인정하고, 불만과 대처 "
                   "방법은 한 단계만 낮춤(최소 C). 판매자나 게시판의 보상 공지는 리뷰별 후보로 검증자에게 넘기며 페이지 "
                   "전체를 자동으로 낮추지 않음. 플랫폼 전체의 리뷰 적립 제도와 판매자가 여는 리뷰 이벤트는 구분함.", PROMO)


def row(**kw):
    base = {
        "id": None, "name_ko": None, "hosts": [], "route_ids": [], "family": None, "public_scope": None,
        "scope_note": None, "routes": [], "route_notes": [], "expected_stops": [], "robots": None, "terms": None,
        "audience": None, "voice_notes": [], "privacy_notes": [], "discontinuities": [],
        "checked_at": CHECKED, "verified_at": None,
    }
    for k, v in kw.items():
        assert k in base, k
        base[k] = v
    for k in ("id", "name_ko", "family", "public_scope", "scope_note", "robots", "terms", "audience"):
        assert base[k] is not None, (kw.get("id"), k)
    return base


ROWS = [
    # 1
    row(
        id="naver-blog", name_ko="네이버 블로그",
        hosts=["blog.naver.com", "m.blog.naver.com"], route_ids=["naver-blog", "naver-blog-postview"],
        family="blog", public_scope="public",
        scope_note=R("전체공개 글만 공개 페이지로 봄. 이웃공개·서로이웃공개·비공개 글은 로그인하지 않은 방문자가 읽을 수 "
                     "없으므로 공개가 아님.", PPA),
        routes=["official_feed", "reader_public_page"],
        route_notes=[
            R("routes.json의 naver-terms 항목(reported)이 네이버 호스트 전체를 덮으므로 RSS 피드와 공개 페이지 모두 " +
              LIFT_NOTE + " RSS 제공 여부와 주소 형태는 실시간 확인 전임.", ROUTES),
            NAVER_API_OFF,
            NAVER_API_HUB,
        ],
        expected_stops=["terms_restricted"],
        robots=NAVER_ROBOTS, terms=NAVER_TERMS,
        audience=audience("네이버 발표를 전한 보도(2025-12): 2025년 블로그 새 글 3억 3천만 건, 순방문자 4,500만 명 이상. "
                          "2025-09 기준 10-30대가 작성자의 약 70%. 회사 자체 수치이며 한 작성자의 나이를 짐작하는 근거로 "
                          "쓰지 않음.", "medium", "search_summary", "daum_blog_report", "zdnet_blog_report",
                          "fnnews_blog_mz"),
        voice_notes=[
            C("협찬·체험단 글이 많은 채널임. 공정위 2024년 SNS 뒷광고 모니터링에서 네이버 블로그 의심 게시물은 9,423건"
              "(전체 22,011건). 적발 건수일 뿐 비율이나 분모가 아님.",
              "search_summary", "kftc_2024_monitoring", "zdnet_kftc_2024"),
            C("2024-12-01부터 블로그·카페의 추천·보증 글은 경제적 이해관계를 제목이나 첫 부분에 적어야 함(공정위 추천·보증 "
              "심사지침 개정). 그 전 글은 표시 위치가 다를 수 있으므로 게시일을 함께 봄.",
              "search_index", "kftc_2024_revision"),
            R("표시가 없다고 협찬이 없는 글로 보지 않음. '내돈내산'은 자기 선언일 뿐 독립성의 근거가 아님.", PROMO),
        ],
        privacy_notes=[R("블로그 ID가 URL에 들어 있음. 작성자는 author-key로 바꾸고 글 URL은 번들의 source_ref에만 둠.", PPA)],
        discontinuities=[
            KFTC_2024_RULE,
            NAVER_ROBOTS_2025,
            NAVER_TERMS_2025,
            D("2025-12", "블로그 앱 추천 피드 개편 시험 보도(주제별 '내돈내산' 글 모아 보기 포함)", "search_summary",
              "hk_blog_feed"),
        ] + NAVER_API_DATES,
    ),
    # 2
    row(
        id="naver-cafe", name_ko="네이버 카페(육아·지역 카페 포함)",
        hosts=["cafe.naver.com", "m.cafe.naver.com"], route_ids=["naver-cafe"],
        family="community", public_scope="mixed",
        scope_note=R("카페마다 공개 게시판과 회원 전용 게시판이 섞여 있고, 등급(등업) 조건이 붙은 게시판도 있음. 회원 "
                     "전용·등업 게시판은 공개가 아님(auth_gate).", PPA),
        routes=["reader_public_page", "signed_in_authorised"],
        route_notes=[
            R("routes.json의 naver-cafe-bulk-notice 항목(reported)이 먼저 적용됨. 공개 게시판 읽기와 승인된 카페의 로그인 "
              "읽기 모두 " + LIFT_NOTE, ROUTES),
            R("로그인 읽기는 사용자가 브리프의 access_policy.signed_in_communities에 카페 경로(path_prefix)와 함께 직접 적은 "
              "카페만 해당함. 요약만 남기고 회원 정보는 남기지 않음. 에이전트는 이 목록에 카페를 더하지 않음.", PPA),
            NAVER_API_OFF,
            NAVER_API_HUB,
        ],
        expected_stops=["terms_restricted", "auth_gate"],
        robots=NAVER_ROBOTS,
        terms=terms(
            "reported", ["bulk_collection", "automated_collection"], "search_summary",
            "공지 원문은 읽지 못함(미확인). 네이버 이용약관(naver-terms, reported)도 함께 걸림. 사용자가 공지와 약관을 "
            "직접 읽고 브리프에 기록하기 전까지 요청하지 않음.",
            "newsis_cafe_notice", "daum_cafe_notice",
            clause="2026-08-31 보도된 카페 공지: 회원과 카페의 동의 없이 게시글·댓글을 대량 수집하거나 외부 사이트에 "
                   "옮겨 쓰는 행위를 금지함. 크롤러·봇·스크립트 같은 자동화 방식의 대량 조회·수집, 공식 경로가 아닌 "
                   "접근, 접근 차단 뒤에도 수집을 이어가는 행위, 수집한 글을 네이버 밖에 싣거나 가공해 다시 제공하는 "
                   "행위를 예로 듦. 이미 수집한 경우 멈추고 데이터를 지우라고 요구함.",
            entry="naver-cafe-bulk-notice"),
        audience=audience("와이즈앱 추정 네이버 카페 앱 월평균 사용자 904만 명(2026-01~04). 앱 사용자 수는 글쓴이 수도 "
                          "세그먼트 비율도 아님. 육아·지역 카페 구성원의 성별·연령·정치 성향 추정치는 싣지 않음(4절).",
                          "low", "search_summary", "wiseapp_sns_2026", "platum_sns_2026"),
        voice_notes=[
            C("업체가 회원인 척 쓴 가짜 후기와 숨은 마케팅 사례가 여러 차례 보도된 채널임. 공동구매·업체 홍보 글은 "
              "promotion 표지로 먼저 거름.", "search_summary", "hk_momcafe_2020", "sbs_momcafe"),
            C("경쟁 업체를 깎아내리는 댓글 사례도 보도됨(2026-04). 부정적인 글도 판촉일 수 있음.", "search_summary",
              "nate_momcafe_smear"),
        ],
        privacy_notes=[
            R("아이 이름·학교·병원·동네 같은 세부는 남기지 않음. 미성년자로 보이는 사람의 글은 건너뜀. 공유 산출물에는 "
              "풀어 쓴 요약만 둠.", LEGAL),
        ],
        discontinuities=[
            KFTC_2024_RULE,
            NAVER_ROBOTS_2025,
            NAVER_TERMS_2025,
            D("2026-08-31", "게시글·댓글 대량 수집 금지 카페 공지 보도", "search_summary", "newsis_cafe_notice",
              "daum_cafe_notice"),
        ] + NAVER_API_DATES,
    ),
    # 3
    row(
        id="naver-kin", name_ko="네이버 지식iN",
        hosts=["kin.naver.com", "m.kin.naver.com"], route_ids=["naver-kin"],
        family="qna", public_scope="public",
        scope_note=R("질문과 답변이 한 페이지에 공개됨. 질문자와 답변자는 서로 다른 사람으로 셈.", PPA),
        routes=["reader_public_page"],
        route_notes=[
            R("routes.json의 naver-terms 항목(reported)이 덮음. 공개 페이지는 " + LIFT_NOTE, ROUTES),
            NAVER_API_OFF,
            NAVER_API_HUB,
        ],
        expected_stops=["terms_restricted"],
        robots=NAVER_ROBOTS, terms=NAVER_TERMS,
        audience=audience("2022-10-06 발표를 전한 보도: 2021년 신규 사용자의 56%가 10-20대. 20년 누적 사용자 3,200만 명, "
                          "문답 8억 건. 글쓴이 구성으로 쓰지 않음.", "medium", "search_summary", "byline_kin_2022",
                          "zdnet_kin_2022"),
        voice_notes=[
            C("2024-04-25 개편으로 질문 마감이 없어지고 여러 답변을 채택할 수 있게 됨. 누구나 답변에 UP/DOWN 투표를 할 수 "
              "있고 UP이 많은 답변이 위에 보임. 눈에 띄는 답변은 투표로 골라진 답변임.",
              "search_summary", "newspim_kin_2024", "mt_kin_2024"),
            C("AI 자동 답변 '지식이'는 2024-08 시범 시작 뒤 약 100만 건의 질문에 답했고 2026-05-24 종료됨. 이 기간의 "
              "답변은 AI가 썼을 수 있으므로 답변마다 작성 주체를 따로 적음.",
              "search_summary", "newstree_kin_ai", "newsis_kin_ai_end", "hk_kin_2026"),
        ],
        privacy_notes=[
            C("2026-02-04 인물 정보와 지식iN 계정이 잘못 이어져 유명인의 과거 답변이 한때 드러났다는 보도가 있음. 답변 "
              "이력은 신원으로 이어질 수 있으므로 특정인의 질문·답변 이력을 모으지 않음.",
              "search_summary", "asiae_kin_incident", "daum_kin_incident"),
        ],
        discontinuities=[
            D("2024-04-25", "지식iN 개편: 질문 마감 폐지, 여러 답변 채택, 답변 UP/DOWN 투표", "search_summary",
              "newspim_kin_2024", "mt_kin_2024"),
            D("2024-08", "지식iN AI 자동 답변 '지식이' 시범 시작", "search_summary", "newstree_kin_ai"),
            NAVER_ROBOTS_2025,
            NAVER_TERMS_2025,
            D("2026-05-24", "지식iN AI 자동 답변 '지식이' 종료", "search_summary", "newsis_kin_ai_end", "hk_kin_2026"),
        ] + NAVER_API_DATES,
    ),
    # 4
    row(
        id="naver-place", name_ko="네이버 플레이스 리뷰",
        hosts=["m.place.naver.com"], route_ids=["naver-place"],
        family="commerce_reviews", public_scope="app_heavy",
        scope_note=C("장소 리뷰는 앱과 지도 화면이 중심임. 웹 주소 형태는 route table 기준이며 실시간 확인 전임.",
                     "inference"),
        routes=["team_export", "reader_public_page"],
        route_notes=[
            C("업주인 팀은 스마트플레이스에서 자기 업체 리뷰를 먼저 봄(내보내기 형식은 확인하지 못함).", "inference"),
            C("네이버 오픈 API 명세에는 리뷰 본문을 주는 경로가 없음. 지역 검색 API는 업체 목록만 주며 정렬 옵션은 "
              "random(유사도순)과 comment(카페/블로그 리뷰 개수 순)뿐임.", "direct_fetch", "naver_openapi_swagger"),
            R("routes.json의 naver-terms 항목(reported)이 덮음. 공개 페이지는 " + LIFT_NOTE +
              " 페이지 뒤의 내부 데이터 경로는 부르지 않음.", PPA),
        ],
        expected_stops=["terms_restricted"],
        robots=robots("unknown", C("보고된 robots 정보를 찾지 못함. 약관 제한이 풀린 실행에서 robots 확인이 판정함.",
                                   "not_found")),
        terms=NAVER_TERMS,
        audience=audience("와이즈앱 추정 네이버지도 앱 월평균 사용자 3,044만 명(2025-01~11). 리뷰 작성자 구성은 측정된 적 "
                          "없음.", "medium", "search_summary", "wiseapp_apps_2025", "kbench_apps_2025"),
        voice_notes=[
            C("2026-04-06부터 별점을 다시 기록하고, 3개월 검토 뒤 2026-07-09부터 평균 별점과 사용자별 별점을 공개함. 업주가 "
              "평균 별점 노출을 켜고 끌 수 있고, 2021-10 이후 개업한 업체는 기본값이 미노출임. 보이는 평균 별점은 업주가 "
              "고른 것이므로 장소끼리 비교하지 않음.",
              "search_summary", "naver_place_release", "newspim_place_2026", "edaily_place_2026"),
            C("2026-03-31 보도: 리뷰 이용정책을 고쳐 설명 없이 3점 미만 별점을 무분별하게 주는 행위를 금지 행위에 넣고, "
              "리뷰 수정은 작성 뒤 3개월 안에만 가능하게 함. 낮은 별점의 분포는 이 정책의 영향을 받음.",
              "search_summary", "daum_place_policy", "edaily_place_2026"),
            C("리뷰는 방문 인증에 묶임. 2024-10 위치·영수증·실명 인증 강화와 2025-05-12 네이버 POS 연동 인증 추가가 "
              "마케팅 커뮤니티 글에 정리돼 있음(신뢰도 낮음).", "search_summary", "iboss_place_2025"),
        ],
        privacy_notes=[R("리뷰에 방문 날짜·동행인·위치가 섞임. 작성자는 author-key로 바꾸고 방문 정보는 요약만 둠.", PPA)],
        discontinuities=[
            D("2021-10-25", "네이버 플레이스 별점 신규 수집 중단(키워드 리뷰 도입)", "search_summary",
              "fnnews_place_2021"),
            D("2024-10", "네이버 플레이스 리뷰 방문 인증 강화(마케팅 커뮤니티 정리, 신뢰도 낮음)", "search_summary",
              "iboss_place_2025"),
            D("2025-05-12", "네이버 플레이스 리뷰에 네이버 POS 연동 인증 추가(마케팅 커뮤니티 정리, 신뢰도 낮음)",
              "search_summary", "iboss_place_2025"),
            NAVER_TERMS_2025,
            D("2026-04-06", "네이버 플레이스 별점 기록 재개", "search_summary", "naver_place_release",
              "newspim_place_2026"),
            D("2026-07-09", "네이버 플레이스 평균 별점·사용자별 별점 공개 시작. 평균 별점 노출은 업주가 켜고 끔",
              "search_summary", "naver_place_release", "etnews_place_2026"),
        ],
    ),
    # 5
    row(
        id="kakao-map", name_ko="카카오맵 리뷰",
        hosts=["place.map.kakao.com"], route_ids=["kakao-map"],
        family="commerce_reviews", public_scope="app_heavy",
        scope_note=C("2025-02 말 웹 개편 뒤 웹에서 '맛집' 평가가 사라지고, 후기는 PC 웹에 최대 3개, 모바일 웹에는 "
                     "최신·업주 선정·본인 후기만 보인다는 보도가 있음(2025-03-15). 지금의 웹 노출은 확인하지 못함.",
                     "search_summary", "mt_kakaomap_web", "daum_kakaomap_web"),
        routes=["reader_public_page"],
        route_notes=[
            C("카카오 로컬 API는 장소 이름·주소·도로명 주소·전화·분류·좌표·place_url 같은 장소 정보만 주고 리뷰 필드는 "
              "없음. 이 스킬은 로컬 API를 쓰지 않음.", "search_index", "kakao_local_api"),
            R("웹에 보이는 후기는 일부뿐이므로 대표성이 없음. 보이지 않는 후기는 수집 공백이며 다른 경로로 메우지 않음.",
              PPA),
        ],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found",
                    "카카오맵 약관의 자동 수집 조항은 확인하지 못함. 제한이 없다는 뜻이 아니므로 reader의 일반 중단 "
                    "규칙을 그대로 적용함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[C("후기 화면이 개편마다 바뀜. 개편 날짜로 구간을 나눠 읽음.", "inference")],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[
            D("2025-02", "카카오맵 웹 개편: 웹에서 '맛집' 평가가 사라지고 후기 노출이 줄었다는 보도(2025-03-15)",
              "search_summary", "mt_kakaomap_web", "daum_kakaomap_web"),
        ],
    ),
    # 6
    row(
        id="daum-cafe", name_ko="다음 카페",
        hosts=["cafe.daum.net", "m.cafe.daum.net"], route_ids=["daum-cafe"],
        family="community", public_scope="mixed",
        scope_note=C("공개 카페와 회원 전용 카페가 있음. 다음 도움말은 카페글 검색이 공개 카페의 검색 공개 게시판 글만 "
                     "대상으로 한다고 설명함.", "search_index", "daum_cafe_help1", "daum_cafe_help2"),
        routes=["reader_public_page", "signed_in_authorised"],
        route_notes=[
            R("공개 카페의 공개 게시판만 읽음. 회원 전용 카페와 게시판은 auth_gate로 멈추며 읽거나 요약하지 않음.", PPA),
            R("회원 전용 카페는 사용자가 브리프에 직접 승인한 카페만 로그인으로 읽고 요약만 남김.", PPA),
            R("카카오 다음 검색 API는 꺼 둠(소유자가 현행 약관을 읽기 전까지).", ROUTES),
        ],
        expected_stops=["auth_gate"],
        robots=DAUM_ROBOTS,
        terms=terms("unchecked", [], "not_found",
                    "카페 약관의 자동 수집 조항은 확인하지 못함. 운영사가 카카오에서 AXZ(현 주식회사 다음)로 바뀌었으므로 "
                    "실행 전에 약관을 다시 확인함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[C("카페마다 운영 규칙과 말투가 다름. 카페 단위로 문맥을 읽음.", "inference")],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[KFTC_2024_RULE] + list(DAUM_OPERATOR),
    ),
    # 7
    row(
        id="tistory", name_ko="티스토리",
        hosts=["*.tistory.com"], route_ids=["tistory"],
        family="blog", public_scope="public",
        scope_note=R("블로그마다 하위 도메인이 따로 있음. 공개 글만 읽음.", ROUTES),
        routes=["official_feed", "reader_public_page"],
        route_notes=[R("블로그별 /rss 피드는 최근 글만 담음(route table 기준, 실시간 확인 전).", ROUTES)],
        expected_stops=[],
        robots=DAUM_ROBOTS,
        terms=terms("unchecked", [], "not_found",
                    "티스토리 약관의 자동 수집 조항은 확인하지 못함. 운영사가 바뀌었으므로 실행 전에 다시 확인함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[R("하위 도메인 하나가 작성자 한 명임.", GRADING)],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[KFTC_2024_RULE] + list(DAUM_OPERATOR),
    ),
    # 8
    row(
        id="dcinside", name_ko="디시인사이드",
        hosts=["gall.dcinside.com", "m.dcinside.com"], route_ids=["dcinside"],
        family="community", public_scope="public",
        scope_note=C("갤러리 글은 로그인 없이 읽히고, 로그인 없이 글과 댓글도 쓸 수 있다고 보도됨.", "search_index",
                     "koreaherald_dc"),
        routes=["reader_public_page"],
        route_notes=[
            R("routes.json의 dcinside-terms 항목(reported)이 dcinside.com 전체를 덮음. 공개 페이지는 " + LIFT_NOTE +
              " 이 스킬은 약관이 그 읽기를 허용하는지 판단하지 않음(법률 자문 아님).", ROUTES),
        ],
        expected_stops=["terms_restricted"],
        robots=robots("unknown", R("약관 제한이 풀린 실행에서만 robots를 확인함. 보고된 robots 정보 없음.", ROUTES)),
        terms=terms(
            "reported", ["automated_collection"], "search_index",
            "조항 문구는 dcinside.com 도메인 한정 검색으로 읽음(원문 페이지 직접 열람은 이 환경에서 막힘). 이 스킬은 이 "
            "항목을 reported로 둠. 사용자가 원문을 읽고 이번 읽기가 허용된다고 판단해 기록한 실행에서만 풀림.",
            "dc_terms", "dc_terms_mobile",
            clause="이용약관 제16조(크롤링 및 인공지능 학습) ①: robots.txt에 적용한 일부 사이트에만 크롤링을 허용하며, "
                   "사전 서면 동의 없이 어떤 형태·목적으로든 서비스를 크롤링하는 행위를 금지함. ②: 콘텐츠를 인공지능 "
                   "학습용 데이터로 쓰려면 공익·비영리 목적이라도 사전 합의가 필요함.",
            terms_url=U["dc_terms"], entry="dcinside-terms"),
        audience=audience("2025-02-10 보도: 2024-12 기준 국내 방문 순위 8위, 하루 약 300만 명이 쓰고 하루 게시글·댓글이 "
                          "300만 건에 가까움. " + "성별·연령·정치 성향 추정치는 싣지 않음(4절).", "medium",
                          "search_index", "koreaherald_dc"),
        voice_notes=[
            C("갤러리마다 문화와 규범이 따로 자란다고 보도됨. 갤러리 단위로 문맥을 읽음.", "search_index",
              "koreaherald_dc"),
            ANON_THREAD,
        ],
        privacy_notes=[
            R("로그인하지 않은 작성자는 닉네임 옆에 IP 일부가 보임. IP는 지우고, 기본 닉네임 'ㅇㅇ'과 IP가 붙은 닉네임은 "
              "author-key가 거절하므로 스레드 키(`author-key --thread-url`)로 셈.", ROUTES),
        ],
        discontinuities=[
            D("2026-02-09", "디시인사이드 경영권 매각 본계약(에이치PE, 약 2,000억 원). 3월 중 대금 납입 예정으로 보도, "
              "종결 여부 미확인", "search_summary", "daum_dc_sale", "kmnanews_dc_sale"),
        ],
    ),
    # 9
    row(
        id="fmkorea", name_ko="에펨코리아",
        hosts=["www.fmkorea.com", "fmkorea.com", "m.fmkorea.com"], route_ids=["fmkorea"],
        family="community", public_scope="public",
        scope_note=C("공개 게시판 기준. 로그인 없이 읽히는 범위는 실시간 확인 전까지 정하지 않음.", "inference"),
        routes=["reader_public_page"],
        route_notes=[PUBLIC_ONLY],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "search_index",
                    "통합 규정은 인공지능·자동화 도구로 글과 댓글 문구를 만드는 행위를 금지하고(25번 항목), 이용약관은 "
                    "자동화 프로그램·봇으로 로그인하거나 로그인 사용자 기능을 쓰는 행위를 금지한다고 요약됨. 로그인하지 "
                    "않은 읽기에 관한 수집 조항은 찾지 못함.",
                    "fmkorea_rules", "fmkorea_terms", terms_url=U["fmkorea_terms"]),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[
            C("게시판마다 정한 추천 수를 넘은 글이 첫 화면인 '포텐 터짐' 게시판에 모임. 눈에 띄는 글은 투표로 골라진 "
              "글이므로 어떤 목록과 정렬에서 읽었는지 기록함.", "search_summary", "fmkorea_best", "mediaus_fmkorea"),
        ],
        privacy_notes=[STD_PRIVACY],
    ),
    # 10
    row(
        id="theqoo", name_ko="더쿠",
        hosts=["theqoo.net", "www.theqoo.net"], route_ids=["theqoo"],
        family="community", public_scope="mixed",
        scope_note=C("대부분 게시판은 로그인 없이 읽히지만 일상 토크·연애 같은 일부 분류는 로그인해야 읽힘. 로그인하지 "
                     "않으면 검색이 안 되고 쓴 지 1시간이 안 된 댓글은 보이지 않는다고 알려짐. 가입은 정해진 기간에만 "
                     "열림(위키 수준 정보).", "search_summary", "namu_theqoo"),
        routes=["reader_public_page"],
        route_notes=[R("공개 게시판만 읽음. 로그인이 필요한 분류는 auth_gate이며 수집 공백임. 로그인하지 않은 방문자에게 "
                       "보이지 않는 최근 댓글도 수집 공백으로 적음.", PPA)],
        expected_stops=["auth_gate"],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "약관의 자동 수집 조항은 확인하지 못함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[C("연예·드라마 같은 대중문화 이야기가 많은 커뮤니티로 소개됨.", "search_summary", "namu_theqoo")],
        privacy_notes=[STD_PRIVACY],
    ),
    # 11
    row(
        id="nate-pann", name_ko="네이트판",
        hosts=["pann.nate.com"], route_ids=["nate-pann"],
        family="community", public_scope="public",
        scope_note=C("공개 게시판으로 봄. 로그인 규칙은 실시간 확인 전까지 정하지 않음.", "inference"),
        routes=["reader_public_page"],
        route_notes=[PUBLIC_ONLY],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "약관·로그인 규칙은 확인하지 못함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[
            C("일상에 관한 고백적 사연 글이 중심인 커뮤니티로 연구됨. 같은 연구는 독자가 사연 조작을 의심하는 반응과 "
              "글쓴이가 진정성을 보이려는 서사 전략을 다룸(대중서사연구 24권 1호, 2018). 익명 1인칭 사연은 어느 게시판에서든 4절의 규칙을 따름.",
              "search_summary", "kci_pann"),
        ],
        privacy_notes=[R("사연 속 가족·직장·지역 정보는 요약에서 뺌.", PPA)],
    ),
    # 12
    row(
        id="clien", name_ko="클리앙",
        hosts=["www.clien.net", "clien.net"], route_ids=["clien"],
        family="community", public_scope="public",
        scope_note=C("로그인하지 않아도 글을 읽을 수 있고, 댓글에는 로그인이, 글쓰기·댓글 활동에는 이메일 인증이 "
                     "필요하다고 안내됨.", "search_index", "clien_guide", "clien_boards"),
        routes=["reader_public_page"],
        route_notes=[PUBLIC_ONLY],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "약관의 자동 수집 조항은 확인하지 못함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[C("IT·기기 이야기가 많은 게시판 구성으로 알려짐.", "search_summary", "clien_boards")],
        privacy_notes=[STD_PRIVACY],
    ),
    # 13
    row(
        id="ppomppu", name_ko="뽐뿌",
        hosts=["www.ppomppu.co.kr", "ppomppu.co.kr", "m.ppomppu.co.kr"], route_ids=["ppomppu"],
        family="community", public_scope="public",
        scope_note=R("공개 게시판 중심으로 봄. 성인·본인 인증이 필요한 게시판은 auth_gate로 멈춤.", PPA),
        routes=["reader_public_page"],
        route_notes=[R("모바일 대체 주소가 route table에 있음(실시간 확인 전).", ROUTES), PUBLIC_ONLY],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "약관의 자동 수집 조항은 확인하지 못함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[R("핫딜 게시판에는 판매 홍보와 제휴 링크 글이 섞임. promotion 표지를 먼저 확인함.", ROUTES)],
        privacy_notes=[STD_PRIVACY],
    ),
    # 14
    row(
        id="ruliweb", name_ko="루리웹",
        hosts=["bbs.ruliweb.com", "m.ruliweb.com"], route_ids=["ruliweb"],
        family="community", public_scope="public",
        scope_note=C("공개 게시판 기준. 로그인 규칙은 실시간 확인 전까지 정하지 않음.", "inference"),
        routes=["reader_public_page"],
        route_notes=[R("모바일 대체 주소도 게시판 경로를 그대로 씀(route table 기준).", ROUTES), PUBLIC_ONLY],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "약관의 자동 수집 조항은 확인하지 못함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[C("콘솔·휴대용 비디오 게임을 주로 다루는 커뮤니티이며 애니메이션·만화·프라모델 게시판도 있음. "
                       "게임마다 공략 게시판이 따로 있음.", "search_summary", "kowiki_ruliweb")],
        privacy_notes=[STD_PRIVACY],
    ),
    # 15
    row(
        id="instiz", name_ko="인스티즈",
        hosts=["www.instiz.net", "instiz.net"], route_ids=["instiz"],
        family="community", public_scope="mixed",
        scope_note=C("대부분 글은 로그인 없이 읽히지만 공포·성인 인증 게시판 같은 일부 게시판은 회원 전용이라고 알려짐"
                     "(위키 수준 정보).", "search_summary", "namu_instiz"),
        routes=["reader_public_page"],
        route_notes=[R("공개 게시판만 읽음. 회원 전용 게시판은 auth_gate이며 수집 공백임.", PPA)],
        expected_stops=["auth_gate"],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "약관의 자동 수집 조항은 확인하지 못함."),
        audience=audience(NO_AUDIENCE, "low", "not_found"),
        voice_notes=[C("앱스토어 소개에서 연예계·아이돌 이슈 커뮤니티로 스스로를 소개함.", "search_summary",
                       "appstore_instiz")],
        privacy_notes=[STD_PRIVACY],
    ),
    # 16
    row(
        id="blind", name_ko="블라인드",
        hosts=["www.teamblind.com", "teamblind.com"], route_ids=["blind"],
        family="community", public_scope="mixed",
        scope_note=R("로그인하지 않으면 일부 글만 보임. 회사 채널과 대부분 주제는 회원 전용(auth_gate)임(route table "
                     "기준, 실시간 확인 전).", ROUTES),
        routes=["reader_public_page"],
        route_notes=[R("로그인 없이 보이는 글만 읽음. 로그인 읽기는 사용자가 브리프에 직접 승인한 경우에만 가능하며, "
                       "에이전트는 이 목록에 커뮤니티를 더하지 않음.", PPA)],
        expected_stops=["auth_gate"],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "수집 관련 약관은 확인하지 못함."),
        audience=audience("회사 발표(2025-03-12): 전 세계 가입자 1,200만 명. 2025-01 기준 국내 10대 그룹 재직자 10명 중 "
                          "9명 이상이 가입. 회사 자체 수치임.", "medium", "search_summary", "mt_blind", "edaily_blind"),
        voice_notes=[
            C("재직 인증을 거친 직장인 익명 커뮤니티임.", "search_summary", "mt_blind"),
            C("직장 불만이 모이기 쉬운 구조이므로 일반 대중을 대표하지 않음.", "inference"),
        ],
        privacy_notes=[R("회사 이름·직무·사건을 합치면 사람을 알아볼 수 있음. 회사명과 세부 사건은 요약에서 뺌.", PPA)],
    ),
    # 17
    row(
        id="everytime", name_ko="에브리타임",
        hosts=["everytime.kr"], route_ids=[],
        family="community", public_scope="private",
        scope_note=C("학교별 게시판은 학생증 등으로 재학생 인증을 거친 회원만 읽고 쓸 수 있다고 알려짐(위키 수준 정보).",
                     "search_summary", "namu_everytime"),
        routes=["none"],
        route_notes=[R("route table의 out_of_scope 채널임. 읽지 않고 요약하지 않음. 학생 사용자는 설문·인터뷰로 조사함.",
                       ROUTES)],
        expected_stops=["auth_gate"],
        robots=NOT_REACHED_OOS,
        terms=terms("unchecked", [], "skill_rule", "읽지 않는 채널이라 약관을 확인하지 않음.", rule_ref=ROUTES),
        audience=audience("공개 웹에서 덜 잡히는 집단을 알려 주는 단서이며 이 채널은 읽지 않음. 와이즈앱 연령별 분석"
                          "(2026-02, 월 사용자 100만 명 이상 앱): 사용자의 77.5%가 20대. 와이즈앱 추정 2026-01~04 월평균 "
                          "사용자 477만 명.", "medium", "search_summary", "wiseapp_age_2026", "daum_age_apps",
                          "wiseapp_sns_2026"),
    ),
    # 18
    row(
        id="band", name_ko="네이버 밴드",
        hosts=["band.us"], route_ids=[],
        family="community", public_scope="private",
        scope_note=R("모임 단위 멤버 전용 서비스로 다룸. route table은 band.us 전체를 out_of_scope로 둠.", ROUTES),
        routes=["none"],
        route_notes=[R("읽지 않고 요약하지 않음. 50-60대 사용자는 공개 웹 글보다 설문·인터뷰로 조사함.", ROUTES)],
        expected_stops=["auth_gate"],
        robots=NOT_REACHED_OOS,
        terms=terms("unchecked", [], "skill_rule", "읽지 않는 채널이라 약관을 확인하지 않음.", rule_ref=ROUTES),
        audience=audience("공개 웹에서 덜 잡히는 집단의 단서이며 이 채널은 읽지 않음. 한국갤럽 2025(만 13세 이상): 밴드를 "
                          "쓴다는 응답 48%. 한국언론진흥재단 2024(만 19세 이상 3,000명): 50대 40.6%, 60대 31.1%가 씀. "
                          "와이즈앱 추정 2026-01~04 월평균 사용자 1,559만 명.", "medium", "search_summary",
                          "gallup_media_2025", "kpf_sns_2024", "journalist_kpf_2024", "wiseapp_sns_2026"),
    ),
    # 19
    row(
        id="kakaotalk-openchat", name_ko="카카오톡 오픈채팅",
        hosts=["open.kakao.com"], route_ids=[],
        family="community", public_scope="private",
        scope_note=R("채팅방은 참여해야 보임. route table은 out_of_scope로 둠.", ROUTES),
        routes=["none"],
        route_notes=[R("읽지 않고 요약하지 않음.", ROUTES)],
        expected_stops=["auth_gate"],
        robots=NOT_REACHED_OOS,
        terms=terms("unchecked", [], "skill_rule", "읽지 않는 채널이라 약관을 확인하지 않음.", rule_ref=ROUTES),
        audience=audience("공개 웹에서 덜 잡히는 집단의 단서이며 이 채널은 읽지 않음. 카카오톡 자체는 거의 모든 연령이 씀"
                          "(한국언론진흥재단 2024, 만 19세 이상: 98.9%). 오픈채팅 사용자 구성 자료는 찾지 못함.", "medium",
                          "search_summary", "kpf_sns_2024", "journalist_kpf_2024"),
    ),
    # 20
    row(
        id="daangn", name_ko="당근(동네생활)",
        hosts=["www.daangn.com", "daangn.com"], route_ids=["daangn"],
        family="community", public_scope="app_heavy",
        scope_note=C("앱이 중심이며 공개 웹 페이지가 있는 글만 대상임. 공개 범위는 실시간 확인 전까지 정하지 않음.",
                     "inference"),
        routes=["reader_public_page"],
        route_notes=[R("공개 웹 페이지만 읽고 사이트 내부 데이터 경로는 부르지 않음. 로그인, 사람 확인, 속도 제한이 "
                       "나오면 그 자리에서 멈추고 수집 공백으로 적음.", ROUTES)],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found",
                    "검색으로 자동 수집 조항을 찾지 못함. 제한이 없다는 뜻이 아니므로 reader의 일반 중단 규칙을 그대로 "
                    "적용함."),
        audience=audience("와이즈앱: 2025-08 사용자 2,185만 명, 40대 비중 30.3%로 가장 큼. 2026-08 사용자 2,317만 명"
                          "(보도). 앱 사용자 수이며 글쓴이 구성이 아님.", "medium", "search_summary",
                          "wiseapp_resale_2025", "datanews_daangn_2026"),
        voice_notes=[C("중고거래·동네 이야기·동네 가게 홍보가 섞인 동네 단위 채널임.", "inference")],
        privacy_notes=[R("동네 이름·닉네임·거래 장소는 개인 정보에 가까움. 공유 산출물에서 뺌.", ROUTES)],
    ),
    # 21
    row(
        id="youtube", name_ko="유튜브 댓글",
        hosts=["www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be"], route_ids=["youtube"],
        family="video", public_scope="public",
        scope_note=R("영상과 댓글은 공개지만 약관이 자동화 접근을 막으므로 페이지는 읽지 않음. 댓글은 Data API로만 받음.",
                     ROUTES),
        routes=["official_api_user_key"],
        route_notes=[
            R("YouTube Data API v3를 사용자 본인의 키로 부르는 공식 경로(R0)만 씀. 영상 주소(watch, youtu.be, shorts, "
              "live, embed)에서 영상 ID만 읽고 페이지는 요청하지 않음. 키는 환경 변수 REMORSEARCH_YOUTUBE_API_KEY에서 "
              "읽고 예전 이름 YOUTUBE_API_KEY도 받음. videos.list와 commentThreads.list를 쓰며, 렌더 캡처는 하지 않고 "
              "ingest도 그 캡처를 받지 않음. 채널·커뮤니티·재생목록·검색 페이지는 경로가 없어 terms_restricted 수집 "
              "공백으로 남음.", ROUTES),
            R("댓글은 관련도 순으로 받은 최상위 댓글이며 한 영상에 정해진 쪽 수까지만 받음(쪽 크기와 쪽 수는 routes.json의 "
              "youtube 경로 설정). 답글과 그 뒤의 댓글은 수집 공백으로 적음.", ROUTES),
            C("commentThreads.list는 호출당 1단위임. 기본 할당은 search.list 하루 100회, videos.insert 하루 100회와 "
              "별도로 나머지 엔드포인트를 합쳐 하루 10,000단위이며, 일일 할당량은 태평양 시간 자정에 초기화됨.",
              "search_index", "yt_commentthreads", "yt_getting_started", "yt_quota_cost"),
            C("API 클라이언트는 사용자가 허락하지 않은 데이터를 최대 30일만 저장하고 그 뒤 지우거나 새로 받아야 함.",
              "search_index", "yt_dev_policies"),
            C("나이·인종·종교·정치 성향·성적 지향·건강 상태 같은 보호 속성으로 사용자를 프로파일링하거나 시청자·제작자의 "
              "이런 속성을 추정해서는 안 됨.", "search_index", "yt_dev_policies"),
            R("키가 없으면 official_route_needs_key로 수집 공백이 되고 사용자에게 묻는 질문이 됨. 키 거절이나 그 밖의 "
              "실패로 공식 경로가 끝나면 그 주소는 terms_restricted로 끝나며 페이지로 바꾸지 않음. 댓글을 막은 영상은 "
              "gone(comments_disabled)으로 기록함.", ROUTES),
        ],
        expected_stops=["terms_restricted"],
        robots=NOT_REACHED_CONFIRMED,
        terms=terms(
            "confirmed", ["automated_collection"], "search_index",
            "youtube.com 도메인 한정 검색으로 조항 문구를 읽음(원문 페이지 직접 열람은 이 환경에서 막힘). confirmed "
            "항목은 브리프로 풀 수 없음. verified_at은 사람이 원문을 다시 읽은 뒤 채움. routes.json의 youtube-terms "
            "항목은 youtu.be 짧은 주소와 youtube-nocookie.com도 덮음.",
            "yt_terms",
            clause="서비스 약관 '권한 및 제한사항': 공개 검색엔진이 YouTube의 robots.txt에 따라 접근하는 경우나 YouTube의 "
                   "사전 서면 허가가 있는 경우를 빼고 자동화 수단(로봇, 봇넷, 스크레이퍼 등)으로 서비스에 접근할 수 없음.",
            terms_url=U["yt_terms"], entry="youtube-terms"),
        audience=audience("와이즈앱 추정 월평균 사용자 4,678만 명(2025-01~11). 한국갤럽 2025(만 13세 이상): 유튜브를 쓴다는 "
                          "응답 95%. 한국언론진흥재단 2024(만 19세 이상): 84.9%. 조사마다 정의가 다름. 댓글 작성자는 그 "
                          "영상을 본 사람 가운데 스스로 쓴 사람임.", "medium", "search_summary", "wiseapp_apps_2025",
                          "gallup_media_2025", "kpf_sns_2024"),
        voice_notes=[
            C("댓글은 특정 영상에 묶이고 정렬 순서에 따라 보이는 댓글이 달라짐. 어떤 정렬로 받았는지 기록함.", "inference"),
            C("공정위 2024년 SNS 뒷광고 모니터링에서 유튜브 의심 게시물은 1,409건. 적발 건수일 뿐 비율이 아님.",
              "search_summary", "kftc_2024_monitoring", "zdnet_kftc_2024"),
        ],
        privacy_notes=[
            R("작성자 이름은 솔트를 넣은 작성자 키로 바꾸고 채널 ID와 프로필 URL은 저장하지 않음. API로 받은 항목마다 "
              "retention_until(받은 시각 + 30일)을 두고 그 뒤 지움.", ROUTES),
            R("작성자 키에 나이·건강·정치 같은 단서를 붙이지 않음. 이런 단서는 세그먼트 수준 주장에만 씀.", ROUTES),
        ],
    ),
    # 22
    row(
        id="instagram", name_ko="인스타그램",
        hosts=["www.instagram.com", "instagram.com"], route_ids=["instagram"],
        family="microblog", public_scope="mixed",
        scope_note=C("공개 계정과 비공개 계정이 있음. 공개 계정도 약관 때문에 읽지 않음.", "inference"),
        routes=["none"],
        route_notes=[
            C("Meta Content Library와 API는 자격을 갖춘 학술·비영리 연구자가 ICPSR 심사를 거쳐 쓰는 별도 경로이며, 이 "
              "스킬의 경로가 아님.", "search_summary", "meta_research_tools", "icpsr_meta", "meta_mcl"),
        ],
        expected_stops=["terms_restricted"],
        robots=NOT_REACHED_CONFIRMED,
        terms=terms(
            "confirmed", ["automated_collection"], "search_index",
            "facebook.com과 help.instagram.com 도메인 한정 검색으로 문구를 읽음(원문 페이지 직접 열람은 이 환경에서 "
            "막힘). confirmed 항목은 브리프로 풀 수 없음. verified_at은 사람이 원문을 다시 읽은 뒤 채움.",
            "meta_adc", "ig_terms",
            clause="Meta 자동 데이터 수집 약관(2024-10-07 시행): Meta의 명시적 서면 허가 없이 자동 데이터 수집을 하지 "
                   "않음. 약관에 동의한 것만으로는 허가가 아님. 인스타그램 이용약관: 로그인 여부와 관계없이 명시적 허가 "
                   "없이 자동화된 방식으로 정보에 접근하거나 수집할 수 없음.",
            terms_url=U["meta_adc"], entry="meta-instagram"),
        audience=audience("한국언론진흥재단 2024(만 19세 이상): 20대 80.9%, 30대 70.7%가 씀. 와이즈앱 추정 2026-01~04 "
                          "월평균 사용자 2,808만 명.", "medium", "search_summary", "kpf_sns_2024", "journalist_kpf_2024",
                          "wiseapp_sns_2026"),
        voice_notes=[
            C("공정위 2024년 모니터링에서 뒷광고 의심 게시물이 가장 많았던 채널임(10,195건). 적발 건수일 뿐 비율이 아님.",
              "search_summary", "kftc_2024_monitoring", "zdnet_kftc_2024"),
        ],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[D("2024-10-07", "Meta 자동 데이터 수집 약관 현행본 시행", "search_index", "meta_adc")],
    ),
    # 23
    row(
        id="threads", name_ko="스레드",
        hosts=["threads.com", "www.threads.com", "threads.net", "www.threads.net"], route_ids=["threads"],
        family="microblog", public_scope="mixed",
        scope_note=C("공개·비공개 프로필이 있음. 공개 프로필도 약관 때문에 읽지 않음.", "inference"),
        routes=["none"],
        route_notes=[
            C("Threads API의 키워드 검색은 threads_keyword_search 권한이 필요하고, 그 권한을 승인받지 못한 앱은 인증한 "
              "사용자 자신의 글만 검색함. 이 스킬은 구현하지 않음.", "search_index", "threads_keyword_api"),
        ],
        expected_stops=["terms_restricted"],
        robots=NOT_REACHED_CONFIRMED,
        terms=terms(
            "confirmed", ["automated_collection"], "search_index",
            "facebook.com과 help.instagram.com 도메인 한정 검색으로 읽음(원문 페이지 직접 열람은 이 환경에서 막힘). "
            "confirmed 항목은 브리프로 풀 수 없음. threads.com과 threads.net 모두 routes.json의 meta-threads 항목에 "
            "들어 있음.",
            "meta_adc", "threads_terms", "ig_terms",
            clause="Meta 자동 데이터 수집 약관이 적용되며, 스레드 이용약관은 인스타그램 이용약관을 함께 적용함(인스타그램 "
                   "약관은 명시적 허가 없는 자동 접근·수집을 금지함).",
            terms_url=U["meta_adc"], entry="meta-threads"),
        audience=audience("와이즈앱: 2026-01~04 월평균 사용자 729만 명, 전년 같은 기간보다 21.0% 늘어남.", "medium",
                          "search_summary", "wiseapp_sns_2026", "platum_sns_2026"),
        voice_notes=[
            C("반말 중심의 가벼운 말투가 퍼졌다는 보도가 있음.", "search_summary", "herald_threads", "daum_threads_banmal"),
            R("말투와 높임 수준은 나이·성별 단서가 아님.", QUERY),
        ],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[
            D("2025-04-24", "스레드 기본 주소가 threads.com으로 바뀌고 threads.net은 threads.com으로 넘어감",
              "search_summary", "tc_threads_com"),
        ],
    ),
    # 24
    row(
        id="app-store-kr", name_ko="앱스토어 리뷰(한국)",
        hosts=["apps.apple.com"], route_ids=["app-store"],
        family="app_store_reviews", public_scope="public",
        scope_note=C("앱 페이지의 리뷰는 공개임. 나라(스토어)마다 리뷰가 따로 모임.", "inference"),
        routes=["official_feed", "team_export"],
        route_notes=[
            C("공개 고객 리뷰 RSS는 나라별 최근 리뷰를 한 쪽에 50개씩 최대 10쪽(약 500개)까지 준다고 알려짐. Apple의 "
              "공식 문서는 찾지 못함. route table은 1쪽만 읽음.", "search_summary", "devto_appstore_rss"),
            R("피드가 비어 있으면 읽기 성공이 아님. 비공식 경로로 바꾸지 않고 수집 공백으로 적음.", PPA),
            C("팀 자기 앱의 리뷰는 App Store Connect API(앱별 customerReviews 목록)나 콘솔 자료로 받음(team_export).",
              "search_index", "asc_customer_reviews"),
        ],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "not_found", "Apple의 RSS 이용 조건은 확인하지 못함."),
        audience=audience("한국갤럽 2025-07 조사(만 18세 이상 1,001명, 스마트폰 사용자 986명): 주로 쓰는 스마트폰은 삼성 "
                          "72%, 애플 24%. 애플은 18-29세에서 60%, 60세 이상에서 4%. 여성 27%, 남성 21%가 애플을 쓴다고 "
                          "보도됨. 스마트폰 사용자 기준이며 리뷰 작성자 구성이 아님. 리뷰 작성자 구성은 측정된 적 없음"
                          "(단서만).", "medium", "search_summary", "gallup_phone_2025", "datanews_phone_2025",
                          "daum_phone_2025"),
        voice_notes=[STORE_SPIKES],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[KAKAOTALK_DATE],
    ),
    # 25
    row(
        id="google-play-kr", name_ko="구글 플레이 리뷰(한국)",
        hosts=["play.google.com"], route_ids=["google-play"],
        family="app_store_reviews", public_scope="public",
        scope_note=C("앱 페이지의 리뷰는 공개지만 클릭 없이 보이는 리뷰는 일부임.", "inference"),
        routes=["team_export", "reader_public_page"],
        route_notes=[
            C("Play Developer API의 reviews.list는 팀 자기 앱에서 최근 1주일 안에 쓰이거나 고친 리뷰만 줌. 더 긴 기간은 "
              "Play Console의 CSV 내보내기로 받음.", "search_index", "play_reviews_list", "play_reply_reviews"),
            R("공개 페이지는 클릭 없이 처음 몇 개 리뷰만 보여 줌. 렌더는 스크롤만 하고 더 보기 버튼을 누르지 않음.", PPA),
        ],
        expected_stops=[],
        robots=UNKNOWN_ROBOTS,
        terms=terms("unchecked", [], "search_index",
                    "Google 서비스 약관은 robots.txt 같은 기계 판독 지시를 어기는 자동 접근을 금지함. reader는 "
                    "robots.txt를 따르므로 별도 약관 중단은 두지 않음.", "google_terms", terms_url=U["google_terms"]),
        audience=audience("한국갤럽 2025-07 조사(스마트폰 사용자 986명): 삼성 72%. 50대·60대는 90% 안팎이 삼성. 남성 76%, "
                          "여성 67%가 삼성을 쓴다고 보도됨. 스마트폰 사용자 기준이며 리뷰 작성자 구성은 측정된 적 없음"
                          "(단서만).", "medium", "search_summary", "gallup_phone_2025", "datanews_phone_2025",
                          "daum_phone_2025"),
        voice_notes=[STORE_SPIKES],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[
            KAKAOTALK_DATE,
            D("2025-10-02", "카카오톡 구글 플레이 평점 1.0 보도: 평가자 318만 5,098명 중 312만 4,788명(98.11%)이 1점",
              "search_summary", "mtn_kakaotalk_play"),
        ],
    ),
    # 26
    row(
        id="coupang", name_ko="쿠팡 상품 리뷰",
        hosts=["www.coupang.com", "m.coupang.com"], route_ids=["coupang"],
        family="commerce_reviews", public_scope="public",
        scope_note=C("상품 페이지의 리뷰는 공개지만 reader가 읽을 수 있는지는 약관과 robots가 정함.", "inference"),
        routes=["team_export", "reader_public_page"],
        route_notes=[
            C("판매자인 팀은 자기 상품 리뷰 자료를 먼저 씀(형식은 확인하지 못함).", "inference"),
            R("routes.json의 coupang-terms 항목(reported)이 덮음. 공개 페이지는 " + LIFT_NOTE +
              " 그 뒤에도 robots.txt가 허용할 때만 읽음.", ROUTES),
        ],
        expected_stops=["terms_restricted", "opted_out"],
        robots=robots("reported_closed", C(
            "보도(2026-04-27 분석, 2026-09-02 기준 분석): robots.txt가 검색엔진 봇에만 상품 경로를 열고 나머지 봇은 "
            "막으며, OpenAI의 GPTBot·ChatGPT-User·OAI-SearchBot을 이름으로 막음. 그대로라면 reader는 opted_out에서 멈춤. "
            "실행 때 robots 확인이 판정함.", "search_summary", "byline_coupang_robots", "digitalmarketer_coupang")),
        terms=terms(
            "reported", ["automated_collection"], "search_summary",
            "원문은 이 환경에서 열리지 않음(미확인). routes.json의 coupang-terms 항목과 같은 상태임. 사용자가 약관을 "
            "직접 읽고 브리프에 기록하기 전까지 요청하지 않음.",
            "aboutcoupang_terms", "coupang_terms",
            clause="쿠팡 기업 사이트(aboutcoupang.com) 이용약관: 자동화된 에이전트나 스크립트로 자동 검색·요청·쿼리를 "
                   "만들거나 데이터를 마이닝하는 행위를 금지하고, robots.txt를 따르는 공용 검색엔진 스파이더에만 색인용 "
                   "복사를 조건부로 허락함. 쇼핑 사이트(coupang.com) 회원 약관의 같은 취지 조항은 검색 요약으로만 봄.",
            terms_url=U["coupang_terms"], entry="coupang-terms"),
        audience=audience("와이즈앱 추정 월평균 사용자 3,388만 명(2025-01~11).", "medium", "search_summary",
                          "wiseapp_apps_2025", "kbench_apps_2025"),
        voice_notes=[
            C("공정위(2024-08)는 쿠팡이 검색 순위를 조작하고 임직원 약 2,000명을 동원해 자체 브랜드(PB) 상품에 후기 약 7만 "
              "개를 달았다는 혐의로 과징금 1,628억 원을 부과함. 쿠팡은 서울고법에 취소 소송을 냈고, 시정명령은 집행정지로 "
              "효력이 멈췄으나 과징금은 내도록 했다는 보도가 있음. 본안 결과는 확인하지 못함.",
              "search_summary", "hk_coupang_kftc", "newsis_coupang_suit", "economist_coupang_stay"),
            R("플랫폼 자체 브랜드 상품의 리뷰는 다른 채널 계열의 근거가 있어야 셈.", PROMO),
            INCENTIVE_RULE,
        ],
        privacy_notes=[STD_PRIVACY],
        discontinuities=[
            D("2024-08", "자체 브랜드 상품 검색 순위 조작·임직원 후기 혐의로 공정위 과징금 부과", "search_summary",
              "hk_coupang_kftc"),
            D("2024-09", "쿠팡이 서울고법에 과징금·시정명령 취소 소송 제기", "search_summary", "newsis_coupang_suit"),
        ],
    ),
    # 27
    row(
        id="delivery-apps", name_ko="배달앱 리뷰(배달의민족·쿠팡이츠·요기요)",
        hosts=[], route_ids=[],
        family="commerce_reviews", public_scope="app_only",
        scope_note=C("리뷰는 앱 안에서만 보임.", "inference"),
        routes=["team_export"],
        route_notes=[R("입점 업주인 팀은 자기 가게 리뷰를 먼저 씀(내보내기 형식은 확인하지 못함). 앱 트래픽이나 내부 "
                       "API는 쓰지 않음.", PPA)],
        expected_stops=[],
        robots=robots("not_reached", R("공개 웹 페이지가 없어 요청하지 않음.", PPA)),
        terms=terms("unchecked", [], "skill_rule", "읽지 않는 채널이라 약관을 확인하지 않음.", rule_ref=ROUTES),
        audience=audience("와이즈앱 추정 배달의민족 월평균 사용자 2,226만 명(2025-01~11).", "medium", "search_summary",
                          "wiseapp_apps_2025", "kbench_apps_2025"),
        voice_notes=[
            C("한국소비자원 2024-07-23 발표(최근 1년 안에 배달앱을 쓴 소비자 1,000명 설문, 자기 보고): 773명(77.3%)이 "
              "리뷰를 썼고, 그중 504명(65.2%)이 리뷰 이벤트 참여를 위해 씀. 참여자 가운데 401명(79.6%)은 이벤트가 별점에 "
              "영향을 줬다고 했고, 그중 394명(98.3%)은 실제 만족도보다 높은 별점을 줬다고 답함. 394명은 이벤트 참여자 "
              "504명의 약 78%임.", "search_summary", "kmib_kca_delivery", "daum_kca_delivery", "khan_kca_delivery"),
            R("리뷰 이벤트가 도는 곳의 별점 평균은 만족도 근거로 쓰지 않음. 보상 표시가 있는 리뷰의 등급은 promotion.md "
              "4d를 따름.", PROMO),
        ],
        privacy_notes=[R("리뷰에 주소·동·주문 내용이 섞임. 요약에서 뺌.", PPA)],
    ),
]

CORPUS_NORMS = [
    {"id": "sensitive-data",
     **C("정치적 견해는 민감정보임(개인정보 보호법 제23조①. 법률 제21445호, 2026-09-11 시행판을 공개 저장소 사본으로 "
         "읽음. 문구는 2016-03-29 개정 뒤 그대로임). 커뮤니티 성향 추정치를 한 사람에게 붙이면 그 사람의 정치적 견해를 "
         "새로 추정하는 셈이 될 수 있으므로 하지 않음(추론). 법률 자문 아님.",
         "mirror", "law_pipa", "mirror_pipa"),
     "legal_ref": LEGAL + " L10"},
    {"id": "hate-speech-corpus",
     **C("국내 방문자가 많은 커뮤니티 11곳의 2015-2022년 글과 댓글 396,496건으로 만든 혐오 표현 코퍼스 연구(PLOS ONE "
         "19권 5호, 2024)는 대부분의 커뮤니티에서 정치 성향과 연령 차이에 따른 양극화가 혐오 표현을 이끌고, 다른 "
         "커뮤니티에서는 사회적 소수자에 대한 주변화가 두드러진다고 보고함. 성별을 겨냥한 혐오 글의 비중은 2018년에 "
         "크게 늘었다가 2019년 이후 줄었고, 연령을 겨냥한 혐오는 2021년에 치솟음. 코퍼스 전체의 경향이며 어느 "
         "커뮤니티의 사람도 설명하지 않음.", "search_index", "plos_hate", "pubmed_hate")},
    {"id": "no-community-placement",
     **R("이 지도는 커뮤니티별 성향 위치(어느 커뮤니티가 어느 쪽인지)를 싣지 않음. 연구가 커뮤니티 이름을 들더라도 그 "
         "결과를 한 게시자, 한 주장, 한 페르소나로 옮기지 않음.", SELF)},
    {"id": "uncertain-polarity",
     **R("비꼼, 반어, 밈이 흔한 게시판에서는 글의 극성(칭찬인지 비꼼인지)을 부모 글과 앞뒤 댓글과 함께 판단하고, 판단이 "
         "서지 않으면 극성 불확실로 둠.", QUERY)},
    {"id": "narrative_unverified",
     **R("익명 1인칭 사연은 어느 게시판에서든 사실 확인이 안 된 진술로 다루고 narrative_unverified 주의 표시를 붙임. "
         "존재 근거로만 쓰고, 보고서에는 \"작성자는 ~라고 적었습니다 (작성자 진술, 사실 여부 미확인)\"처럼 적음.",
         REPORT)},
    {"id": "register-not-demographics",
     **R("말투(반말·존댓말), 호칭, 은어는 나이·성별·정치 성향의 단서가 아님.", QUERY)},
    {"id": "anonymous-threads",
     **R("로그인 없는 익명 게시판은 스레드 단위로 셈. 기본 익명 닉네임(ㅇㅇ 등, uxresearch/data/markers.json의 "
         "anonymous_handles)과 IP 일부가 붙은 닉네임은 신원이 아니며 scripts/ux_research.py author-key가 거절함. 이런 "
         "글은 --thread-url로 스레드 키를 받음.", GRADING)},
    {"id": "vote-selection",
     **R("추천으로 골라진 목록(예: 에펨코리아의 '포텐 터짐', 지식iN의 UP 투표 정렬)과 정렬 순서는 눈에 띄는 글을 바꿈. "
         "어떤 목록과 정렬에서 읽었는지 기록함.", SELF)},
    {"id": "promotion-first",
     **R("협찬·제휴·리뷰 보상 표지는 promotion.md에 따라 먼저 확인함. 표지가 없다고 순수 후기로 보지 않음. 경쟁 업체를 "
         "깎아내리는 글처럼 부정적인 판촉도 있음.", PROMO)},
    {"id": "minors",
     **R("미성년자로 보이는 사람의 글은 건너뛰고, 아이 이름·학교·병원·동네 같은 세부를 남기지 않음.", LEGAL)},
    {"id": "norms-not-traits",
     **R("이 규범은 모든 채널에 고르게 적용함. 채널별 콘텐츠 규범은 그 채널에서 확인된 글의 형식(투표 선별, 사연 중심, "
         "협찬 비중 등)이며 게시자의 특성이 아님.", SELF)},
]

VOCAB = {
    "family": ["blog", "community", "qna", "video", "app_store_reviews", "microblog", "commerce_reviews"],
    "public_scope": ["public", "mixed", "app_heavy", "app_only", "private"],
    "route": ["official_api_user_key", "official_feed", "team_export", "reader_public_page", "signed_in_authorised",
              "none"],
    "terms_status": ["reported", "confirmed", "checked_by_user", "unchecked"],
    "terms_restricts": ["automated_collection", "bulk_collection", "ai_input", "storage"],
    "confidence": ["high", "medium", "low"],
    "stop_class": ["auth_gate", "paywall", "human_check", "opted_out", "terms_restricted", "rate_limit", "geo_block",
                   "legal_block", "gone", "budget", "host_stopped"],
    "robots_expectation": ["unknown", "reported_closed", "not_reached"],
    "read_via": list(READ_VIA),
}

NOTE = (
    "계획용 지도임. 무엇을 읽고 어디서 멈출지는 reader 정책인 uxresearch/data/routes.json이 정하고, 두 파일이 "
    "어긋나면 routes.json을 따름. 사용자 규모·구성 수치는 채널을 고르는 단서일 뿐 세그먼트 비율이 아님"
    "(references/research/source-grading.md 6절). 커뮤니티의 성별·연령·정치 성향 추정치는 싣지 않으며 게시자·주장·"
    "페르소나에 붙이지 않음. 회원 전용이거나 닫힌 커뮤니티는 단서로 이름을 대지 않음. routes에는 정당한 경로만 적고, "
    "멈춘 페이지를 가져오는 다른 방법은 적지 않음. 플랫폼 이름은 설명용이며 어떤 운영사와도 제휴 관계가 없음. "
    "checked_at은 확인일이고, verified_at은 사람이 실시간 확인(robots 확인과 약관 원문 읽기)을 마친 뒤에만 채움. "
    "read_via는 labels의 한국어 표시와 짝을 이룸: direct_fetch는 원문을 직접 열어 읽음, search_index는 운영사·기관 "
    "도메인으로 한정한 검색 결과로 읽음, search_summary는 그 밖의 검색 결과 요약(보도 포함), third_party_quote는 "
    "제3자 인용, mirror는 법령 원문을 옮긴 공개 저장소 사본, not_found는 이번 확인에서 자료를 찾지 못함, inference는 "
    "추론, skill_rule은 이 스킬의 규칙(rule_ref가 규칙 문서를 가리킴). terms.routes_entry는 이 행의 호스트를 덮는 "
    "routes.json terms_restricted 항목 id임. 법률 자문이 아님. 사람이 읽는 판은 "
    "references/research/korea/platform-map.md임."
)


def build():
    for r in ROWS:
        r["discontinuities"] = sorted(r["discontinuities"], key=lambda d: d["date"])
    ids = [r["id"] for r in ROWS]
    assert len(ids) == 27 and len(set(ids)) == 27, ids
    for r in ROWS:
        assert r["family"] in VOCAB["family"], r["id"]
        assert r["public_scope"] in VOCAB["public_scope"], r["id"]
        assert r["routes"] and all(x in VOCAB["route"] for x in r["routes"]), r["id"]
        assert ("none" not in r["routes"]) or r["routes"] == ["none"], r["id"]
        assert "researcher_note" not in json.dumps(r, ensure_ascii=False), r["id"]
        assert all(s in VOCAB["stop_class"] for s in r["expected_stops"]), r["id"]
        assert r["robots"]["expectation"] in VOCAB["robots_expectation"], r["id"]
        assert r["terms"]["status"] in VOCAB["terms_status"], r["id"]
        assert all(x in VOCAB["terms_restricts"] for x in r["terms"]["restricts"]), r["id"]
        assert r["audience"]["confidence"] in VOCAB["confidence"], r["id"]
        if r["terms"]["status"] in ("reported", "confirmed"):
            assert "terms_restricted" in r["expected_stops"], r["id"]
        if r["public_scope"] == "app_only":
            assert not r["hosts"], r["id"]
    return {
        "schema_version": "ux-research-korea-platforms.v1",
        "version": "2026-09-29.1",
        "checked_at": CHECKED,
        "verified_at": None,
        "note": NOTE,
        "vocab": VOCAB,
        "labels": dict(READ_VIA),
        "corpus_norms": CORPUS_NORMS,
        "platforms": ROWS,
    }


def walk_urls(obj, out):
    if isinstance(obj, dict):
        for v in obj.values():
            walk_urls(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_urls(v, out)
    elif isinstance(obj, str) and re.match(r"https?://", obj):
        if obj not in out:
            out.append(obj)


if __name__ == "__main__":
    data = build()
    urls = []
    walk_urls(data, urls)
    unused = [k for k, v in U.items() if v not in urls]
    if unused:
        print("unused source keys:", unused, file=sys.stderr)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    JSON_OUT.write_text(text, encoding="utf-8")
    print("wrote", JSON_OUT, len(text), "bytes;", len(urls), "unique urls")
