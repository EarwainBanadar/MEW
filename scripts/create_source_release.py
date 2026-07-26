
from pathlib import Path
import hashlib
import json
import zipfile
import datetime

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.9.3"
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
        info.date_time = (2026, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
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
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "size": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in files
    ],
}
(OUT / f"MEW_v{VERSION}_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps({
    "archive": str(ZIP),
    "sha256": manifest["archive_sha256"],
    "file_count": len(files)
}, indent=2))
