import pytest

from app.services.chunking import chunk_text


def test_short_text_single_chunk():
    chunks = chunk_text("hello world", chunk_size=200, overlap=50)
    assert chunks == ["hello world"]


def test_long_text_has_overlap():
    words = [f"word{i}" for i in range(500)]
    chunks = chunk_text(" ".join(words), chunk_size=200, overlap=50)
    assert len(chunks) > 1
    first_tail = chunks[0].split()[-50:]
    second_head = chunks[1].split()[:50]
    assert first_tail == second_head


def test_empty_text():
    assert chunk_text("", chunk_size=200, overlap=50) == []


def test_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=50, overlap=50)
