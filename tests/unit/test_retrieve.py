from unittest.mock import Mock

from src.indexing.retrieve import retrieve


def test_retrieve_encodes_query_and_returns_payloads():
    embedder = Mock()
    embedder.embed_query.return_value = [0.1, 0.2]
    store = Mock()
    point_a = Mock(payload={"chunk_id": "a"})
    point_b = Mock(payload={"chunk_id": "b"})
    store.hybrid_search.return_value = Mock(points=[point_a, point_b])

    results = retrieve("question test", embedder=embedder, store=store, limit=5)

    embedder.embed_query.assert_called_once_with("question test")
    store.hybrid_search.assert_called_once_with(
        dense_vector=[0.1, 0.2], query_text="question test", limit=5
    )
    assert results == [{"chunk_id": "a"}, {"chunk_id": "b"}]


def test_retrieve_uses_default_limit():
    embedder = Mock()
    embedder.embed_query.return_value = [0.1]
    store = Mock()
    store.hybrid_search.return_value = Mock(points=[])

    retrieve("question", embedder=embedder, store=store)

    _, kwargs = store.hybrid_search.call_args
    assert kwargs["limit"] == 10
