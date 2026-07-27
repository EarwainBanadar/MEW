from __future__ import annotations

import datetime
import hashlib
import json
import zipfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
VERSION = str(tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"])
OUT = ROOT / "releases"
OUT.mkdir(exist_ok=True)
ZIP = OUT / f"MEW_v{VERSION}_source.zip"

EXCLUDED = {".git", ".venv", ".pytest_cache", "__pycache__", "dist", "build"}

files = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED for part in rel.parts):
        continue
    if rel.parts and rel.parts[0] == "releases":
        continue
    files.append(path)

with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        rel = path.relative_to(ROOT)
        info = zipfile.ZipInfo(str(rel).replace("\\", "/"))
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, path.read_bytes())

manifest = {
    "project": "MEW",
    "version": VERSION,
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "archive": ZIP.name,
    "archive_sha256": hashlib.sha256(ZIP.read_bytes()).hexdigest(),
    "file_count": len(files),
    "files": [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "size": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in files
    ],
}
manifest_path = OUT / f"MEW_v{VERSION}_manifest.json"
manifest_path.write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(
    json.dumps(
        {
            "archive": str(ZIP),
            "manifest": str(manifest_path),
            "sha256": manifest["archive_sha256"],
            "file_count": len(files),
        },
        indent=2,
    )
)
