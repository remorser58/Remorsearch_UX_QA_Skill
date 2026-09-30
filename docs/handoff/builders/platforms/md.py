"""Render references/research/korea/platform-map.md from build.ROWS (same ids, order and URL set)."""

import re

import build

LABEL = build.READ_VIA

SCOPE_KO = {"public": "공개", "mixed": "혼합", "app_heavy": "앱 중심", "app_only": "앱 전용", "private": "비공개"}
FAMILY_KO = {"blog": "블로그", "community": "커뮤니티", "qna": "질문·답변", "video": "영상 댓글",
             "app_store_reviews": "스토어 리뷰", "microblog": "마이크로블로그", "commerce_reviews": "상거래 리뷰"}

data = build.build()
rows = data["platforms"]

norms = data["corpus_norms"]

# Source keys in order of first appearance: the rows first, then the section 4 notes.
urls = []
build.walk_urls(rows, urls)
build.walk_urls(norms, urls)
KEY = {u: f"P{i + 1:02d}" for i, u in enumerate(urls)}


def keys(*names):
    return ", ".join(sorted(KEY[build.U[n]] for n in names))


def cite(item):
    out = f" — {LABEL[item['read_via']]}"
    if item.get("sources"):
        out += " [" + ", ".join(sorted(KEY[u] for u in item["sources"])) + "]"
    if item.get("rule_ref") and item["rule_ref"] != build.SELF:
        out += f" (`{item['rule_ref']}`)"
    if item.get("legal_ref"):
        out += f" (`{item['legal_ref'].split(' ')[0]}` {item['legal_ref'].split(' ', 1)[1]})"
    return out


def code_list(values):
    return ", ".join(f"`{v}`" for v in values) if values else "없음"


def channel_section(r):
    lines = [f"### `{r['id']}` {r['name_ko']}", ""]
    hosts = code_list(r["hosts"]) if r["hosts"] else "없음(앱 전용)"
    lines.append(f"- 호스트: {hosts} · route table id: {code_list(r['route_ids'])}")
    s = r["scope_note"]
    lines.append(f"- 계열 `{r['family']}` · 공개 범위 `{r['public_scope']}`: {s['text']}{cite(s)}")
    lines.append("- 정당한 경로(선호 순): " + " → ".join(f"`{x}`" for x in r["routes"]))
    for n in r["route_notes"]:
        lines.append(f"  - {n['text']}{cite(n)}")
    lines.append(f"- 예상 중단: {code_list(r['expected_stops'])}")
    rb = r["robots"]
    lines.append(f"- robots 예상 `{rb['expectation']}`: {rb['text']}{cite(rb)}")
    t = r["terms"]
    head = f"- 약관 `{t['status']}`"
    if t.get("routes_entry"):
        head += f"(routes.json `{t['routes_entry']}`)"
    if t["restricts"]:
        head += f", 제한 {code_list(t['restricts'])}"
    if t.get("clause"):
        lines.append(head)
        lines.append(f"  - 조항: {t['clause']}")
        lines.append(f"  - 확인: {t['note']}{cite(t)}")
    else:
        lines.append(f"{head}: {t['note']}{cite(t)}")
    a = r["audience"]
    lines.append(f"- 사용자 단서(신뢰도 `{a['confidence']}`): {a['text']}{cite(a)}")
    if r["voice_notes"]:
        lines.append("- 콘텐츠 규범:")
        for v in r["voice_notes"]:
            lines.append(f"  - {v['text']}{cite(v)}")
    if r["privacy_notes"]:
        lines.append("- 개인정보:")
        for v in r["privacy_notes"]:
            lines.append(f"  - {v['text']}{cite(v)}")
    if r["discontinuities"]:
        lines.append("- 불연속:")
        for d in r["discontinuities"]:
            lines.append(f"  - {d['date']}: {d['what']}{cite(d)}")
    lines.append(f"- 확인일 {r['checked_at']} · verified_at 없음(null)")
    lines.append("")
    return "\n".join(lines)


def overview_table():
    out = ["| id | 채널 | 계열 | 공개 범위 | 정당한 경로 | 예상 중단 | 약관 | 단서 신뢰도 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append("| `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
            r["id"], r["name_ko"], FAMILY_KO[r["family"]], SCOPE_KO[r["public_scope"]],
            ", ".join(f"`{x}`" for x in r["routes"]), ", ".join(f"`{x}`" for x in r["expected_stops"]) or "-",
            f"`{r['terms']['status']}`", r["audience"]["confidence"]))
    return "\n".join(out)


def discontinuity_table():
    grouped, order = {}, []
    for r in rows:
        for d in r["discontinuities"]:
            k = (d["date"], d["what"])
            if k not in grouped:
                grouped[k] = {"ids": [], "d": d}
                order.append(k)
            grouped[k]["ids"].append(r["id"])
    order.sort(key=lambda k: k[0])
    out = ["| 날짜 | 채널 | 내용 | 근거 |", "| --- | --- | --- | --- |"]
    for k in order:
        g = grouped[k]
        d = g["d"]
        src = LABEL[d["read_via"]] + " " + ", ".join(sorted(KEY[u] for u in d["sources"]))
        out.append(f"| {d['date']} | {', '.join(f'`{i}`' for i in g['ids'])} | {d['what']} | {src} |")
    return "\n".join(out)


def sources_list():
    return "\n".join(f"- {KEY[u]} {u}" for u in urls)


HEAD = """# 한국 플랫폼 지도

이 문서는 한국 채널 27곳에서 리서치를 계획할 때 쓰는 지도입니다. 채널마다 공개 범위, 정당한 경로, 예상 중단, 약관
상태, 콘텐츠 규범, 개인정보 주의점, 불연속 날짜를 적습니다. 데이터 원본은 `uxresearch/data/korea-platforms.json`이고,
이 문서는 같은 내용을 사람이 읽기 좋게 옮긴 판입니다. 한국 리서치 팩의 흐름은
`references/research/korea/overview.md`에서 시작합니다.

이 문서의 어떤 내용도 중단을 넘는 방법이 아닙니다. 멈춘 페이지는 다른 길로 가져오지 않고 수집 공백으로 적습니다.

## 1. 이 지도의 성격

- 계획용 지식입니다. 실제로 무엇을 읽고 어디서 멈출지는 reader 정책인 `uxresearch/data/routes.json`이 정합니다. 두
  파일이 어긋나면 routes.json을 따르고 이 지도를 고칩니다.
- 사용자 단서는 플랫폼 전체 사용자에 관한 조사·패널 값입니다. 채널을 고르는 단서일 뿐 세그먼트 비율이 아니고, 글쓴이
  구성도 아닙니다(`references/research/source-grading.md` 6절). 단서 신뢰도(high, medium, low)는 채널 선택 단서로서
  그 값을 얼마나 믿을 만한지를 뜻합니다.
- 커뮤니티의 성별·연령·정치 성향 추정치는 싣지 않습니다. 그런 추정치는 게시자, 주장, 페르소나 어디에도 붙이지
  않습니다(4절).
- 회원 전용이거나 닫힌 커뮤니티는 사용자 단서로 이름을 대지 않습니다. 회원 전용 글은 사용자가 브리프의
  `access_policy.signed_in_communities`에 직접 승인한 커뮤니티에서만, 요약으로만 다룹니다.
- 경로는 정당한 경로만 적습니다. 사용자 본인 키로 부르는 공식 API, 공식 피드, 팀 자체 자료, reader가 읽는 공개
  페이지, 사용자가 승인한 커뮤니티의 로그인 읽기입니다. 멈춘 페이지를 다른 호스트, 미러, 캐시, 아카이브, 앱, 요령으로
  가져오는 방법은 적지 않습니다. 중단은 그 자체로 답이며 보고서의 수집 공백이 됩니다.
- 플랫폼 이름은 설명을 위해 씁니다. 이 스킬은 어떤 운영사와도 제휴 관계가 없습니다.
- 모든 행의 확인일(checked_at)은 2026-09-29입니다. 사람이 실시간 확인(robots 확인과 약관 원문 읽기)을 마치기
  전까지 verified_at은 비워 둡니다(null).
- 이번 확인에서 원문을 직접 연 출처는 네이버 오픈 API 명세(GitHub)뿐입니다. 운영사 약관 페이지, 기관 누리집, 언론사
  누리집, 커뮤니티 사이트는 네트워크 정책 때문에 열리지 않아 검색 결과 요약으로 읽었습니다. 그래서 대부분의 사실은
  미확인(요약)입니다.
- 이 문서는 법률 자문이 아닙니다. 약관 문구는 읽은 방식과 함께 적고, 법적 적용은 판단하지 않습니다. 법령 근거는
  `references/research/korea/legal-checklist.md`에 있습니다.

확인 표시는 `references/research/korea/promotion.md`, `references/research/korea/statistics.md`,
`references/research/korea/query-craft.md`와 같습니다.

| 표시 | 뜻 | JSON `read_via` |
| --- | --- | --- |
| 관찰됨 | 1차 출처의 원문을 직접 열어 읽음. 이번 확인에서는 네이버 오픈 API 명세뿐임 | `direct_fetch` |
| 미확인(요약) | 검색 결과 요약으로만 봄. 운영사·기관 도메인으로 한정한 검색, 보도, 제3자 인용도 여기에 넣음 | `search_index`, `search_summary`, `third_party_quote` |
| 미확인(미러) | 법령 원문을 옮긴 공개 저장소 사본으로 읽음. law.go.kr 원문과 대조하지 못함 | `mirror` |
| 미확인 | 이번 확인에서 쓸 만한 자료를 찾지 못함 | `not_found` |
| 추론 | 위 사실에서 이 스킬이 끌어낸 판단 | `inference` |
| 규칙 | 이 스킬의 규칙. 규칙 문서를 함께 적음 | `skill_rule` |

값의 뜻은 다음과 같습니다.

| 항목 | 값 | 뜻 |
| --- | --- | --- |
| 정당한 경로 | `official_api_user_key` | 사용자 본인 키로 부르는 공식 API. 키는 `REMORSEARCH_*` 환경 변수로만 받음 |
| 정당한 경로 | `official_feed` | 운영사가 내놓은 공식 피드(RSS 등). reader의 R0 경로 |
| 정당한 경로 | `team_export` | 팀이 가진 자체 자료(VOC, 고객센터 기록, 스토어·판매자 콘솔 내보내기). 파일로 받으며 `team_provided` 출처가 됨. 개인 식별 정보를 지운 뒤 받음 |
| 정당한 경로 | `reader_public_page` | reader가 읽는 공개 페이지(`scripts/ux_research.py read`, 필요하면 익명 브라우저 렌더 뒤 `ingest`). 로그인, 사람 확인, 속도 제한 같은 중단은 넘지 않음 |
| 정당한 경로 | `signed_in_authorised` | 사용자가 브리프의 `access_policy.signed_in_communities`에 직접 적은 커뮤니티만 로그인해 읽고 요약만 남김. 에이전트는 이 목록에 더하지 않음 |
| 정당한 경로 | `none` | 이 스킬이 쓸 경로가 없음. 설문, 인터뷰, 팀 자료로 대신함 |
| 약관 상태 | `confirmed` | 자동 수집을 막는 조항 문구를 운영사 도메인에서 읽은 항목. 브리프로 풀 수 없음. 이번에는 운영사 도메인 한정 검색으로 읽었으므로 사람이 원문을 다시 읽기 전까지 verified_at은 null임 |
| 약관 상태 | `reported` | 보도·인용·검색 요약으로 제한이 알려진 항목, 또는 이 스킬이 reported로 두는 항목. 사용자가 약관을 직접 읽고 브리프의 `access_policy.terms_checked`에 result `permits_this_reading`으로 적은 실행에서만 풀림. 풀린 호스트는 실행당 문서 10건까지 |
| 약관 상태 | `checked_by_user` | 사용자가 직접 확인해 기록한 상태(이 지도에는 아직 없음) |
| 약관 상태 | `unchecked` | 확인하지 못함. 제한이 없다는 뜻이 아님. reader의 일반 중단 규칙만 적용됨 |
| robots 예상 | `unknown` | 실행 때 robots 확인 전까지 모름 |
| robots 예상 | `reported_closed` | 보도상 우리 토큰에 적용될 그룹이 막혀 있음 |
| robots 예상 | `not_reached` | 약관 중단(confirmed)이나 범위 밖 중단이 먼저라 robots.txt를 요청하지 않음 |
| 공개 범위 | `public`, `mixed`, `app_heavy`, `app_only`, `private` | 공개, 공개·회원 전용 혼합, 앱 중심, 앱 전용, 비공개 |

예상 중단 값은 `references/research/public-page-access.md` 5절의 중단 유형에 약관 중단 `terms_restricted`를 더한
것입니다(`uxresearch/scope.py`). `terms_restricted`는 요청 전에, 그리고 리디렉션 단계마다 판정하므로 짧은 주소가 제한
호스트로 넘어가도 멈춥니다. `reported` 항목이 풀린 실행에서도 그 호스트는 실행당 문서 10건까지만 읽습니다. 공식
경로가 있는 제한 호스트(유튜브)는 그 공식 경로만 씁니다. 페이지 요청과 렌더 캡처는 하지 않고, `ingest`도 그 호스트의
캡처를 받지 않습니다. 검색 결과 페이지는 `read`가 시작할 때 exit 2로 거절하고, 리디렉션 중에 만나면 중단으로
기록합니다. 브라우저 도구도 멈춘 호스트를 열지 않습니다.

## 2. 한눈에 보기

행 순서는 JSON과 같습니다.

"""

AFTER_TABLE = """
## 3. 채널별 상세

"""

NORMS_HEAD = """## 4. 커뮤니티 콘텐츠 규범(코퍼스 수준)

커뮤니티 사이의 차이는 사람의 특성이 아니라 콘텐츠 규범으로 적습니다. 커뮤니티의 성별·연령·정치 성향 추정치는
게시자, 주장, 페르소나 어디에도 붙이지 않습니다. 웹 트래픽 패널이 모델로 추정한 커뮤니티 성비나 위키가 인용한
성비는 커뮤니티 구성을 재는 자료가 아니므로 이 지도에 싣지 않습니다. 아래 항목은 JSON의 `corpus_norms`와
같습니다.

"""

NORMS = """
## 5. 공개 웹에서 덜 잡히는 사용자

- 50-60대: 밴드와 카카오톡 비중이 큼(한국언론진흥재단 2024, 만 19세 이상: 밴드를 쓰는 비율 50대 40.6%, 60대 31.1%.
  한국갤럽 2025, 만 13세 이상: 밴드 48%). 두 채널 모두 이 스킬이 읽지 않는 비공개 채널임 — 미확인(요약) [{band}]
- 학생: 에브리타임 사용자의 77.5%가 20대(와이즈앱, 2026-02). 재학생 인증 뒤에 있어 읽지 않음 — 미확인(요약)
  [{age}]
- 닫힌 카페와 회원 전용 게시판: 승인된 커뮤니티가 아니면 읽지 않고 요약하지도 않음. 이 지도는 그런 커뮤니티를 단서로
  이름 대지 않음 — 규칙 (`references/research/public-page-access.md`)

이 사용자 집단은 설문, 인터뷰, 팀 자체 자료로 조사합니다. 공개 웹에서 결과가 적다고 그 집단이 없다고 보지 않습니다.
보고서에는 덜 잡힌 집단을 수집 공백으로 적습니다.

## 6. 스토어·리뷰 편향

- 스마트폰 브랜드: 한국갤럽 2025-07 조사(스마트폰 사용자 986명)에서 주로 쓰는 스마트폰은 삼성 72%, 애플 24%임.
  애플은 18-29세에서 60%, 60세 이상에서 4%이고, 여성 27%·남성 21%가 애플을 쓴다고 보도됨. 아이폰 사용자는 더 젊은
  층에 몰리고 여성 비중이 상대적으로 높지만, 이 값은 스마트폰 사용자 기준이며 리뷰 작성자 구성이 아님. 리뷰
  작성자는 스스로 쓴 사람이고 구성은 측정된 적이 없음(단서만). 스토어별로 나눠 읽되 사람 구성을 추정하지 않음 —
  미확인(요약) [{phone}]
- 배달앱 리뷰 이벤트: 한국소비자원 2024-07-23 설문(자기 보고)에서 리뷰 이벤트 참여자 504명 가운데 401명(79.6%)이
  이벤트가 별점에 영향을 줬다고 했고, 그중 394명(98.3%)이 실제 만족도보다 높은 별점을 줬다고 답함. 394명은 참여자
  504명의 약 78%임. 이벤트가 도는 곳의 별점 평균은 만족도 근거가 아님 — 미확인(요약) [{kca}]
- 리뷰 보상 표시가 있는 리뷰는 만족·선호·반대 근거 검색·별점 평균에서 D까지만 인정함. 불만과 대처 방법은 한 단계만
  낮춤(최소 C). 판매자나 게시판의 보상 공지는 리뷰별 후보로 검증자에게 넘기며 페이지 전체를 자동으로 낮추지 않음.
  플랫폼 전체의 리뷰 적립 제도와 판매자가 여는 리뷰 이벤트는 구분함 — 규칙
  (`references/research/korea/promotion.md`)
- 자체 브랜드 상품 리뷰: 공정위는 쿠팡이 임직원을 동원해 자체 브랜드 상품에 후기를 달았다는 혐의 등으로 과징금을
  부과했고 소송이 이어지고 있음 — 미확인(요약) [{coupang}]. 플랫폼 자체 브랜드 상품의 리뷰는 다른 채널 계열의
  근거가 있어야 셈 — 규칙 (`references/research/korea/promotion.md`)
- 리뷰 폭주: 카카오톡 2025-09-23 개편 직후 두 스토어 평점이 급락함. 폭주 기간은 사용성 발견이 아니라 맥락이며, 날짜
  구간을 나눠 읽음 — 미확인(요약) [{kakaotalk}]
- 업주가 고르는 평균 별점: 네이버 플레이스의 평균 별점은 업주가 노출을 켜고 끄며, 설명 없는 3점 미만 별점은 금지
  행위로 정해졌다고 보도됨. 보이는 평균 별점을 장소끼리 비교하지 않음 — 미확인(요약) [{place}]
- 일부만 보이는 후기: 카카오맵 웹은 후기를 일부만 보여 준다는 보도가 있음. 보이는 후기는 대표성이 없음 —
  미확인(요약) [{kakaomap}]

## 7. 불연속 날짜표

날짜 앞뒤로 같은 지표를 비교하지 않습니다. 비교가 필요하면 구간을 나눕니다.

"""

UPDATE = """
## 8. 행을 고치는 방법

1. `python3 scripts/ux_research.py robots --run RUN URL`로 그 호스트의 robots 판정을 봅니다. 이 명령은 페이지를 읽지
   않습니다. 약관 제한 호스트는 요청 전에 멈추므로(exit 3) robots.txt도 읽지 않습니다. AI 에이전트 토큰 목록은
   `uxresearch/data/agent-tokens.json`에 있습니다.
2. 사람이 약관 원문을 읽고 URL, 조항 번호, 읽은 날짜를 적습니다.
3. 약관 상태가 바뀌면 `uxresearch/data/routes.json`의 `terms_restricted` 항목을 먼저 고칩니다. reader는
   routes.json만 봅니다.
4. 그다음 `uxresearch/data/korea-platforms.json`을 고치고(`terms.routes_entry` 포함) 이 문서를 맞춥니다. checked_at을
   바꾸고, 사람이 실시간 확인을 마친 경우에만 verified_at을 채웁니다. 행 순서와 출처 URL 목록은 두 파일이 같아야
   합니다.
5. 문서화되지 않은 엔드포인트, 검색 결과 페이지, 다른 호스트·미러·캐시·아카이브·앱은 경로로 추가하지 않습니다.
   회원 전용이나 닫힌 커뮤니티를 사용자 단서로 추가하지 않습니다.
6. 사용자 단서에는 조사·패널 값만 넣습니다. 커뮤니티 성비·연령·정치 성향 추정치는 넣지 않습니다.

## 9. 완료 기준(Done when)

- 실행에 쓴 채널마다 정당한 경로, 예상 중단, 약관 상태를 계획(`plan.md`)에 적음.
- `reported`·`confirmed` 채널은 routes.json의 `terms_restricted` 항목과 상태가 같음.
- 접근 표에 `terms_restricted` 중단을 다른 중단과 나눠 적고, out_of_scope 채널은 따로 셈.
- 사용자 단서를 세그먼트 비율로 쓰지 않았고, 커뮤니티 구성 추정치를 사람·주장·페르소나에 붙이지 않음.
- 공개 웹에서 덜 잡힌 집단을 수집 공백으로 적음.
- 확인일이 90일을 넘은 행은 다시 확인함.

## 10. 실패 유형(Failure modes)

- 네이버 채널 대부분이 `terms_restricted`에서 멈춤: 예상된 결과임. 보고서에 수집 공백으로 적고 팀 자료와 다른 채널
  계열로 보완함. 우회하지 않음.
- 전역 검색 도구가 네이버 글을 잘 찾지 못할 수 있음(미확인): 결과가 없다고 논의가 없다는 뜻이 아님.
- 커뮤니티 구성 수치가 서로 어긋남: 이 지도에 싣지 않으며, 다른 곳에서 보더라도 단서로만 씀.
- 리뷰 폭주 기간이나 업주가 고른 평균 별점, 이벤트로 부풀린 별점을 만족도로 읽음: 날짜 구간을 나누고 별점 평균을
  만족도 근거로 쓰지 않음.
- 오래된 행을 그대로 믿음: 확인일이 90일을 넘으면 다시 확인함.
- 운영사·약관 변경을 놓침: 디시인사이드 매각(2026), 다음 운영사 변경(2025-12, 2026-05, 2026-07), 다음의 외부 AI
  크롤링 정책 개정(2026-09 보도), 네이버 카페 공지(2026-08) 뒤에는 약관과 robots를 다시 확인함.
- 앱스토어 RSS가 비어 있음: 읽기 성공으로 보지 않고 수집 공백으로 적음. 팀의 App Store Connect 자료로 보완함.
- 유튜브 키가 없음: 수집 공백이자 사용자에게 묻는 질문임. 페이지를 읽지 않음.

## 11. 출처

확인일은 모두 2026-09-29입니다. 원문을 직접 열지 못한 출처는 본문에서 미확인으로 표시했습니다. 약관 URL은 3절의
약관 줄과 JSON의 `terms.terms_url`에 있습니다.

"""


def render():
    fmt = {
        "band": keys("kpf_sns_2024", "journalist_kpf_2024", "gallup_media_2025"),
        "age": keys("wiseapp_age_2026", "daum_age_apps"),
        "phone": keys("gallup_phone_2025", "datanews_phone_2025", "daum_phone_2025"),
        "kca": keys("kmib_kca_delivery", "daum_kca_delivery", "khan_kca_delivery"),
        "coupang": keys("hk_coupang_kftc", "newsis_coupang_suit"),
        "kakaotalk": keys("mtn_kakaotalk_play", "daum_kakaotalk_redesign"),
        "place": keys("naver_place_release", "daum_place_policy"),
        "kakaomap": keys("mt_kakaomap_web", "daum_kakaomap_web"),
    }
    parts = [HEAD, overview_table(), "\n", AFTER_TABLE]
    parts += [channel_section(r) + "\n" for r in rows]
    parts.append(NORMS_HEAD)
    parts.append("\n".join(f"- {n['text']}{cite(n)}" for n in norms) + "\n")
    parts.append(NORMS.format(**fmt))
    parts.append(discontinuity_table())
    parts.append("\n")
    parts.append(UPDATE)
    parts.append(sources_list())
    parts.append("\n")
    text = "".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


if __name__ == "__main__":
    text = render()
    body = text.split("## 11. 출처")[0]
    assert "http" not in body, "URL outside the source list"
    build.MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    build.MD_OUT.write_text(text, encoding="utf-8")
    md_urls = re.findall(r"https?://[^\s)>\]]+", text)
    json_urls = []
    build.walk_urls(build.build(), json_urls)
    assert set(md_urls) == set(json_urls), set(md_urls) ^ set(json_urls)
    print("wrote", build.MD_OUT, len(text), "chars;", len(set(md_urls)), "urls")
