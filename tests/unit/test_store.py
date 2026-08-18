from unittest.mock import Mock

from src.indexing.settings import QdrantSettings
from src.indexing.sparse import text_to_sparse_vector
from src.indexing.store import QdrantStore, point_id_for


def make_store(collection_exists: bool = False) -> tuple[QdrantStore, Mock]:
    client = Mock()
    client.collection_exists.return_value = collection_exists
    store = QdrantStore(settings=QdrantSettings(), client=client)
    return store, client


def test_ensure_collection_creates_dense_and_sparse_vectors():
    store, client = make_store(collection_exists=False)

    store.ensure_collection(vector_size=4)

    client.create_collection.assert_called_once()
    _, kwargs = client.create_collection.call_args
    assert store.settings.dense_vector_name in kwargs["vectors_config"]
    assert kwargs["vectors_config"][store.settings.dense_vector_name].size == 4
    assert store.settings.sparse_vector_name in kwargs["sparse_vectors_config"]


def test_ensure_collection_skips_if_already_exists():
    store, client = make_store(collection_exists=True)

    store.ensure_collection(vector_size=4)

    client.create_collection.assert_not_called()


def test_upsert_chunks_builds_dense_and_sparse_vectors_per_point():
    store, client = make_store()
    chunks = [{"chunk_id": "a"}, {"chunk_id": "b"}]
    vectors = [[0.1, 0.2], [0.3, 0.4]]
    texts = ["chat chien", "cnrs concours"]

    store.upsert_chunks(chunks, vectors, texts)

    client.upsert.assert_called_once()
    _, kwargs = client.upsert.call_args
    points = kwargs["points"]
    assert [p.id for p in points] == [point_id_for("a"), point_id_for("b")]
    for point, vector, text in zip(points, vectors, texts, strict=True):
        assert point.vector[store.settings.dense_vector_name] == vector
        expected_sparse = text_to_sparse_vector(text)
        assert point.vector[store.settings.sparse_vector_name].indices == expected_sparse.indices
        assert point.vector[store.settings.sparse_vector_name].values == expected_sparse.values
