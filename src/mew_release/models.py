from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any, Dict

class ReleaseError(RuntimeError):
    pass

@dataclass(frozen=True)
class ReleaseDescriptor:
    release_id: str
    version: str
    title: str
    work_package: str
    status: str
    created_utc: str
    source_root: str
    generator_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ArtifactRecord:
    logical_path: str
    source_path: str
    size: int
    sha256: str
    media_type: str
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ReleaseBuildResult:
    release_directory: str
    archive_path: str
    manifest_path: str
    artifact_count: int
    total_bytes: int
    release_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
