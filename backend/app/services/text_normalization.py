from __future__ import annotations

from functools import lru_cache


STOPWORDS = {
    "a",
    "about",
    "and",
    "are",
    "for",
    "how",
    "the",
    "what",
    "when",
    "where",
    "which",
    "with",
    "about",
    "does",
    "into",
    "many",
    "much",
    "that",
    "their",
    "there",
    "these",
    "this",
    "those",
    "was",
    "were",
    "who",
    "why",
    "would",
    "а",
    "в",
    "для",
    "и",
    "или",
    "как",
    "какая",
    "какие",
    "какой",
    "кейс",
    "на",
    "о",
    "об",
    "по",
    "с",
    "что",
    "это",
}

INTENT_TERMS = {
    "aim",
    "deliverable",
    "goal",
    "result",
    "skill",
    "task",
    "задач",
    "компетенц",
    "результат",
    "требован",
    "цель",
}

RUSSIAN_SUFFIX_FALLBACK = (
    "иями",
    "ями",
    "ами",
    "ией",
    "ей",
    "ого",
    "ему",
    "ыми",
    "ими",
    "ий",
    "ый",
    "ой",
    "ая",
    "ое",
    "ые",
    "их",
    "ых",
    "ам",
    "ям",
    "ах",
    "ях",
    "ом",
    "ем",
    "ия",
    "ие",
    "ии",
    "й",
    "а",
    "у",
    "е",
    "ы",
    "и",
    "ю",
    "я",
)

ENGLISH_SUFFIX_FALLBACK = (
    "ations",
    "ation",
    "ated",
    "ment",
    "ing",
    "ed",
    "es",
    "s",
)


def tokenize_text(text: str) -> set[str]:
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return {
        normalize_token(token)
        for token in cleaned.split()
        if len(token) > 2 and token not in STOPWORDS
    }


def weighted_overlap_score(query_terms: set[str], candidate_terms: set[str]) -> float:
    if not query_terms or not candidate_terms:
        return 0.0

    overlap = query_terms & candidate_terms
    if not overlap:
        return 0.0

    weighted_overlap = sum(2.0 if term in INTENT_TERMS else 1.0 for term in overlap)
    weighted_query = sum(2.0 if term in INTENT_TERMS else 1.0 for term in query_terms)
    return weighted_overlap / weighted_query


def normalize_token(token: str) -> str:
    stemmer = _get_stemmer(token)
    if stemmer is not None:
        try:
            stemmed = stemmer.stemWord(token)
            if stemmed:
                return stemmed
        except Exception:
            pass

    suffixes = RUSSIAN_SUFFIX_FALLBACK if _looks_cyrillic(token) else ENGLISH_SUFFIX_FALLBACK
    for suffix in suffixes:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


@lru_cache(maxsize=2)
def _load_snowball_stemmer(language: str):
    try:
        import snowballstemmer
    except ImportError:
        return None
    return snowballstemmer.stemmer(language)


def _get_stemmer(token: str):
    if _looks_cyrillic(token):
        return _load_snowball_stemmer("russian")
    if token.isascii():
        return _load_snowball_stemmer("english")
    return None


def _looks_cyrillic(token: str) -> bool:
    return any(0x0400 <= ord(char) <= 0x04FF for char in token)


__all__ = [
    "INTENT_TERMS",
    "STOPWORDS",
    "normalize_token",
    "tokenize_text",
    "weighted_overlap_score",
]
