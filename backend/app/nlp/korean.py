import re
from functools import lru_cache

from kiwipiepy import Kiwi

from app.nlp.skills import load_dictionary

NOUN_TAGS = frozenset({"NNG", "NNP", "XR", "SH"})
EXTRA_TERMS = frozenset({"백엔드", "프론트엔드", "풀스택", "데브옵스", "인프라", "플랫폼"})

_HANGUL_WORD = re.compile(r"^[가-힣]+$")
_LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[+#]+|\.[A-Za-z]+)?")


@lru_cache(maxsize=1)
def _kiwi() -> Kiwi:
    kiwi = Kiwi()
    terms = {t for entry in load_dictionary() for t in entry.terms if _HANGUL_WORD.match(t)}
    for word in terms | EXTRA_TERMS:
        kiwi.add_user_word(word, "NNP")
    return kiwi


def tokenize(text: str) -> list[str]:
    if not text.strip():
        return []
    korean = [t.form for t in _kiwi().tokenize(text) if t.tag.split("-")[0] in NOUN_TAGS]
    latin = [m.group().lower() for m in _LATIN_TOKEN.finditer(text)]
    return korean + latin
