from validate_docs import validate_docs


def test_validate_docs_passes_when_every_file_is_registered(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "a.mdx").write_text("# A\n", encoding="utf-8")
    (docs_dir / "docs.json").write_text(
        '{"tree": [{"id": "a", "label": "A", "path": "a.mdx"}]}', encoding="utf-8"
    )

    errors = validate_docs(str(docs_dir))

    assert errors == []


def test_validate_docs_flags_orphaned_file_not_in_docs_json(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "a.mdx").write_text("# A\n", encoding="utf-8")
    (docs_dir / "orphan.mdx").write_text("# Orphan\n", encoding="utf-8")
    (docs_dir / "docs.json").write_text(
        '{"tree": [{"id": "a", "label": "A", "path": "a.mdx"}]}', encoding="utf-8"
    )

    errors = validate_docs(str(docs_dir))

    assert len(errors) == 1
    assert "orphan.mdx" in errors[0]


def test_validate_docs_flags_dangling_docs_json_entry(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "docs.json").write_text(
        '{"tree": [{"id": "missing", "label": "Missing", "path": "missing.mdx"}]}',
        encoding="utf-8",
    )

    errors = validate_docs(str(docs_dir))

    assert len(errors) == 1
    assert "missing.mdx" in errors[0]


def test_validate_docs_handles_nested_tree_structure(tmp_path):
    docs_dir = tmp_path / "docs"
    (docs_dir / "guides").mkdir(parents=True)
    (docs_dir / "guides" / "nested.mdx").write_text("# Nested\n", encoding="utf-8")
    (docs_dir / "docs.json").write_text(
        '{"tree": [{"id": "guides", "label": "Guides", "children": '
        '[{"id": "nested", "label": "Nested", "path": "guides/nested.mdx"}]}]}',
        encoding="utf-8",
    )

    errors = validate_docs(str(docs_dir))

    assert errors == []
