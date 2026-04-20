from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def test_knowledge_directory_exists() -> None:
    assert KNOWLEDGE_DIR.exists()
    assert KNOWLEDGE_DIR.is_dir()


def test_at_least_three_document_types() -> None:
    suffixes = {path.suffix.lower() for path in KNOWLEDGE_DIR.iterdir() if path.is_file()}
    assert ".json" in suffixes
    assert ".csv" in suffixes
    assert ".md" in suffixes
