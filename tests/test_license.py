import tomllib
from pathlib import Path


def test_license_file_contains_canonical_mpl2_text() -> None:
    text = Path("LICENSE").read_text(encoding="utf-8")

    assert text.startswith("Mozilla Public License Version 2.0\n")
    assert "1. Definitions" in text
    assert "Exhibit A - Source Code Form License Notice" in text
    assert 'Exhibit B - "Incompatible With Secondary Licenses" Notice' in text


def test_pyproject_declares_mpl2_license() -> None:
    with Path("pyproject.toml").open("rb") as file:
        project = tomllib.load(file)["project"]

    assert project["license"] == "MPL-2.0"
    assert project["license-files"] == ["LICENSE"]
