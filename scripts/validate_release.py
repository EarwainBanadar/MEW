from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path


def project_version(root: Path) -> str:
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def changelog_has_version(root: Path, version: str) -> bool:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    return re.search(rf"^## \[{re.escape(version)}\](?:\s|$)", text, re.MULTILINE) is not None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path, tag: str | None, manifest_path: Path | None) -> list[str]:
    errors: list[str] = []
    version = project_version(root)
    if tag is not None and tag.removeprefix("v") != version:
        errors.append(f"tag {tag!r} does not match project version {version!r}")
    if not changelog_has_version(root, version):
        errors.append(f"CHANGELOG.md has no section for version {version}")
    if manifest_path is not None:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if str(manifest.get("version")) != version:
            errors.append("manifest version does not match project version")
        archive = manifest_path.parent / str(manifest.get("archive", ""))
        if not archive.is_file():
            errors.append(f"release archive is missing: {archive.name}")
        elif manifest.get("archive_sha256") != sha256(archive):
            errors.append("release archive checksum does not match manifest")
        files = manifest.get("files")
        if not isinstance(files, list) or not files:
            errors.append("manifest file inventory is empty")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MEW release consistency")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--tag")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)
    errors = validate(args.root.resolve(), args.tag, args.manifest)
    payload = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
