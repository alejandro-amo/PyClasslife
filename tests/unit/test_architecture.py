from pathlib import Path

from pyclasslife import DEFAULT_BASE_URL


def test_classlife_base_url_is_declared_only_in_constants() -> None:
    source_root = Path(__file__).parents[2] / "src" / "pyclasslife"
    for path in source_root.rglob("*.py"):
        if path.name == "constants.py":
            continue
        assert DEFAULT_BASE_URL not in path.read_text(encoding="utf-8")
