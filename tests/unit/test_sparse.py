from src.indexing.sparse import text_to_sparse_vector, tokenize


def test_tokenize_lowercases_and_strips_accents():
    assert tokenize("Rémunération élevée") == ["remuneration", "elevee"]


def test_tokenize_splits_on_punctuation():
    assert tokenize("CNRS : concours, carrières !") == ["cnrs", "concours", "carrieres"]


def test_text_to_sparse_vector_counts_term_frequencies():
    vector = text_to_sparse_vector("chat chien chat")
    assert len(vector.indices) == 2
    counts = dict(zip(vector.indices, vector.values, strict=True))
    assert sorted(counts.values()) == [1.0, 2.0]


def test_text_to_sparse_vector_indices_are_stable():
    first = text_to_sparse_vector("recherche CNRS")
    second = text_to_sparse_vector("recherche CNRS")
    assert first.indices == second.indices
    assert first.values == second.values
