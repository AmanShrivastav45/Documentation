from rag_pipeline import VectorStore, cosine_similarity, mock_embed, mock_llm_answer


def test_mock_embed_is_deterministic_and_fixed_length():
    vec1 = mock_embed("hello world")
    vec2 = mock_embed("hello world")
    assert vec1 == vec2
    assert len(vec1) == 16


def test_mock_embed_differs_for_different_text():
    assert mock_embed("hello") != mock_embed("goodbye")


def test_cosine_similarity_of_identical_vectors_is_one():
    vec = mock_embed("some text")
    assert abs(cosine_similarity(vec, vec) - 1.0) < 1e-9


def test_vector_store_add_and_all():
    store = VectorStore()
    store.add({"file_path": "a.mdx"}, mock_embed("a"))
    store.add({"file_path": "b.mdx"}, mock_embed("b"))
    assert len(store.all()) == 2


def test_vector_store_clear_removes_all_records():
    store = VectorStore()
    store.add({"file_path": "a.mdx"}, mock_embed("a"))
    store.clear()
    assert store.all() == []


def test_retrieve_top_k_returns_most_similar_record_first():
    store = VectorStore()
    store.add(
        {"file_path": "install.mdx", "content": "installation steps"},
        mock_embed("installation steps"),
    )
    store.add(
        {"file_path": "alerting.mdx", "content": "alerting thresholds"},
        mock_embed("alerting thresholds"),
    )

    results = store.retrieve_top_k("installation steps", k=1)

    assert results[0]["file_path"] == "install.mdx"


def test_mock_llm_answer_includes_question_and_context():
    chunks = [
        {
            "heading": "Installation",
            "file_path": "install.mdx",
            "content": "Run npm install to get started.",
        }
    ]
    answer = mock_llm_answer("How do I install it?", chunks)
    assert "How do I install it?" in answer
    assert "Installation" in answer
    assert "npm install" in answer


def test_mock_llm_answer_handles_no_context():
    answer = mock_llm_answer("anything?", [])
    assert "couldn't find" in answer.lower()
