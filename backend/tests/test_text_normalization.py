from app.services.text_normalization import normalize_token, tokenize_text


def test_normalize_token_matches_russian_word_forms() -> None:
    assert normalize_token("неделя") == normalize_token("недели")


def test_tokenize_text_normalizes_russian_schedule_terms() -> None:
    assert "недел" in tokenize_text("Недели 1-3")
    assert "недел" in tokenize_text("неделя")
