from pathlib import Path

from revenue_kun import __version__


def test_version_file_matches_package_version():
    version_file = Path(__file__).resolve().parents[1] / "VERSION"
    version_file_value = version_file.read_text(encoding="utf-8").strip()

    assert version_file_value.lstrip("v") == __version__
