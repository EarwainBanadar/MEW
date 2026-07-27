from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class ReportingError(RuntimeError):
    pass

@dataclass(frozen=True)
class ReportMetadata:
    report_id: str
    title: str
    generator_version: str = "1.0.0"
    source_name: Optional[str] = None
    generated_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
