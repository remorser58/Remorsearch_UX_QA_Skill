import sys
sys.path.insert(0, "/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
from uxresearch import privacy
salt = b"s" * 32
for h in ["ㅇㅇ(118.235)", "ㅇㅇ (118.235)", "ㅇㅇ（118.235）", "ㅇㅇ ( 118 . 235 )", " ㅇㅇ　(118.235) ",
          "ㅇㅇ(2001:2d8)", "ㅇㅇ(2001:e60)", "닉네임(2001:2d8)", "ㅇㅇ(118.235)​", "ㅇㅇ​", "ㅇ ㅇ", "ㅇㅇ　",
          "ᄋᄋ", "ㅇㅇ(118.*)", "ㅇㅇ(118.235.*.*)", "익명 12", "익명12345", "알 수 없음", "(알 수 없음)", "Anonymous",
          "Deleted User", "홍길동(118.235)", "홍길동", "홍길동 ", "ＨＯＮＧ"]:
    try:
        print(f"{h!r:28} -> key {privacy.author_key(salt, 'dcinside', h)}   normalize={privacy.normalize_handle(h)}")
    except ValueError as e:
        print(f"{h!r:28} -> REFUSED ({str(e)[:50]})")
