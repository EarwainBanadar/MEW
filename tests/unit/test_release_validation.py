from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.validate_release import validate


def _project(root: Path, version: str = "1.2.3") -> None:
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "mew"\nversion = "{version}"\n', encoding="utf-8"
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{version}] - 2026-01-01\n", encoding="utf-8"
    )


def test_release_metadata_is_consistent(tmp_path):
    _project(tmp_path)
    archive = tmp_path / "MEW_v1.2.3_source.zip"
    archive.write_bytes(b"release")
    manifest = tmp_path / "MEW_v1.2.3_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "version": "1.2.3",
                "archive": archive.name,
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "files": [{"path": "README.md"}],
            }
        ),
        encoding="utf-8",
    )
    assert validate(tmp_path, "v1.2.3", manifest) == []


def test_release_rejects_tag_changelog_and_checksum_mismatches(tmp_path):
    _project(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    archive = tmp_path / "release.zip"
    archive.write_bytes(b"release")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "version": "9.9.9",
                "archive": archive.name,
                "archive_sha256": "0" * 64,
                "files": [],
            }
        ),
        encoding="utf-8",
    )
    errors = validate(tmp_path, "v2.0.0", manifest)
    assert any("tag" in error for error in errors)
    assert any("CHANGELOG" in error for error in errors)
    assert any("manifest version" in error for error in errors)
    assert any("checksum" in error for error in errors)
    assert any("inventory" in error for error in errors)
