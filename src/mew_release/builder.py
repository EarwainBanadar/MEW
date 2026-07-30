from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import zipfile
from collections.abc import Iterable
from pathlib import Path

from .models import ArtifactRecord, ReleaseBuildResult, ReleaseDescriptor, ReleaseError

MANIFEST_NAME = "release-manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def media_type(path: Path) -> str:
    explicit = {".md":"text/markdown", ".json":"application/json", ".html":"text/html", ".py":"text/x-python", ".toml":"application/toml", ".zip":"application/zip"}
    return explicit.get(path.suffix.lower()) or mimetypes.guess_type(str(path))[0] or "application/octet-stream"


class ReleaseBuilder:
    """Builds a deterministic, checksummed release from declared artifacts."""

    def __init__(self, generator_version: str = "1.0.0") -> None:
        self.generator_version = generator_version

    def discover(self, source_root: Path, include: Iterable[str], exclude: Iterable[str] = ()) -> list[Path]:
        root = source_root.resolve()
        excluded = set(exclude)
        files: dict[str, Path] = {}
        for pattern in include:
            for path in root.glob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(root).as_posix()
                if any(path.match(x) or rel == x for x in excluded):
                    continue
                files[rel] = path
        return [files[key] for key in sorted(files)]

    def inventory(self, source_root: Path, files: Iterable[Path], required_paths: Iterable[str] = ()) -> list[ArtifactRecord]:
        root = source_root.resolve()
        required = set(required_paths)
        records: list[ArtifactRecord] = []
        seen = set()
        for path in files:
            path = path.resolve()
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise ReleaseError(f"Artifact outside source root: {path}") from exc
            if rel in seen:
                raise ReleaseError(f"Duplicate logical path: {rel}")
            seen.add(rel)
            records.append(ArtifactRecord(rel, str(path), path.stat().st_size, sha256_file(path), media_type(path), rel in required))
        missing = sorted(required - seen)
        if missing:
            raise ReleaseError("Missing required artifacts: " + ", ".join(missing))
        return sorted(records, key=lambda r: r.logical_path)

    def build(self, descriptor: ReleaseDescriptor, records: list[ArtifactRecord], output_root: Path, archive_name: str | None = None) -> ReleaseBuildResult:
        if not records:
            raise ReleaseError("Cannot build an empty release")
        output_root.mkdir(parents=True, exist_ok=True)
        release_dir = output_root / descriptor.release_id
        temp_dir = output_root / (descriptor.release_id + ".tmp")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        if release_dir.exists():
            shutil.rmtree(release_dir)
        temp_dir.mkdir(parents=True)

        for record in records:
            src = Path(record.source_path)
            if sha256_file(src) != record.sha256 or src.stat().st_size != record.size:
                raise ReleaseError(f"Artifact changed after inventory: {record.logical_path}")
            dst = temp_dir / "artifacts" / record.logical_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        manifest = {
            "schema_version":"1.0.0",
            "descriptor":descriptor.to_dict(),
            "artifact_count":len(records),
            "total_bytes":sum(r.size for r in records),
            "artifacts":[r.to_dict() for r in records],
        }
        canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        manifest["manifest_payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        (temp_dir/MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)+"\n",encoding="utf-8")
        temp_dir.rename(release_dir)

        archive = output_root/(archive_name or f"{descriptor.release_id}.zip")
        if archive.exists():
            archive.unlink()
        with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
            for path in sorted(release_dir.rglob("*")):
                if path.is_file():
                    info=zipfile.ZipInfo(path.relative_to(output_root).as_posix(), date_time=(1980,1,1,0,0,0))
                    info.compress_type=zipfile.ZIP_DEFLATED
                    info.external_attr=0o100644 << 16
                    z.writestr(info,path.read_bytes())
        return ReleaseBuildResult(str(release_dir),str(archive),str(release_dir/MANIFEST_NAME),len(records),sum(r.size for r in records),sha256_file(archive))

    def verify(self, release_directory: Path) -> dict[str, object]:
        manifest_path=release_directory/MANIFEST_NAME
        if not manifest_path.exists():
            raise ReleaseError("Release manifest missing")
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        failures=[]
        for item in manifest.get("artifacts",[]):
            path=release_directory/"artifacts"/item["logical_path"]
            if not path.exists():
                failures.append({"path":item["logical_path"],"reason":"missing"})
                continue
            if path.stat().st_size != item["size"]: failures.append({"path":item["logical_path"],"reason":"size"})
            elif sha256_file(path) != item["sha256"]: failures.append({"path":item["logical_path"],"reason":"sha256"})
        return {"status":"PASS" if not failures else "FAIL","checked":len(manifest.get("artifacts",[])),"failures":failures}
