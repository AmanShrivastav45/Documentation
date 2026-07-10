import json
import os
import sys


def find_mdx_files(docs_dir):
    paths = set()
    for root, _, files in os.walk(docs_dir):
        for name in files:
            if name.endswith(".mdx"):
                rel = os.path.relpath(os.path.join(root, name), docs_dir)
                paths.add(rel.replace("\\", "/"))
    return paths


def collect_tree_paths(nodes):
    paths = set()
    for node in nodes:
        if "path" in node:
            paths.add(node["path"])
        if "children" in node:
            paths |= collect_tree_paths(node["children"])
    return paths


def validate_docs(docs_dir):
    docs_json_path = os.path.join(docs_dir, "docs.json")
    with open(docs_json_path, encoding="utf-8") as f:
        docs_json = json.load(f)

    files_on_disk = find_mdx_files(docs_dir)
    paths_in_json = collect_tree_paths(docs_json["tree"])

    orphaned_files = sorted(files_on_disk - paths_in_json)
    dangling_entries = sorted(paths_in_json - files_on_disk)

    errors = []
    if orphaned_files:
        errors.append(
            "Files on disk with no docs.json entry: " + ", ".join(orphaned_files)
        )
    if dangling_entries:
        errors.append(
            "docs.json entries with no matching file: " + ", ".join(dangling_entries)
        )
    return errors


def main():
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    errors = validate_docs(docs_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: all .mdx files in {docs_dir} are registered in docs.json")
    sys.exit(0)


if __name__ == "__main__":
    main()
