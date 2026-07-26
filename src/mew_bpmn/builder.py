from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import (
    Artifact,
    Bounds,
    EngineeringMetadata,
    EngineeringObject,
    Event,
    EventKind,
    Flow,
    FlowKind,
    Gateway,
    GatewayKind,
    Geometry,
    ObjectKind,
    Participant,
    Point,
    Presentation,
    Provenance,
    Task,
    TaskKind,
)
from .repository import BPMNRepository

EVENT_TYPES = {event.value: event for event in EventKind}
GATEWAY_TYPES = {gateway.value: gateway for gateway in GatewayKind}
TASK_TYPES = {task.value: task for task in TaskKind}
FLOW_TYPES = {flow.value: flow for flow in FlowKind}


def geometry_from(data: dict[str, Any]) -> Geometry:
    bbox = data.get("bbox")
    bounds = None
    if bbox and all(bbox.get(key) is not None for key in ("x", "y", "width", "height")):
        bounds = Bounds(
            float(bbox["x"]),
            float(bbox["y"]),
            float(bbox["width"]),
            float(bbox["height"]),
        )
    points = [
        Point(float(point["x"]), float(point["y"]))
        for point in data.get("points", [])
        if point.get("x") is not None and point.get("y") is not None
    ]
    return Geometry(
        bounds=bounds,
        points=points,
        path_data=data.get("path_data"),
        transform=data.get("transform"),
    )


class SemanticModelBuilder:
    """Build the AP9.2 typed object repository from AP9.1 semantic JSON."""

    def build_from_path(self, path: Path) -> BPMNRepository:
        return self.build(json.loads(path.read_text(encoding="utf-8")))

    def build(self, document: dict[str, Any]) -> BPMNRepository:
        repository = BPMNRepository()
        source_sha = document.get("source", {}).get("sha256")

        for raw in document.get("elements", []):
            repository.add(self._element(raw, source_sha))
        for raw in document.get("flows", []):
            repository.add(self._flow(raw, source_sha))

        repository.resolve_relationships()
        errors = repository.validate()
        if errors:
            raise ValueError("; ".join(errors))
        return repository

    def _common(self, raw: dict[str, Any], source_sha: str | None) -> dict[str, Any]:
        return {
            "engineering_id": raw["engineering_id"],
            "bpmn_type": raw.get("bpmn_type") or raw.get("flow_type") or "unknown",
            "name": raw.get("name"),
            "documentation": raw.get("text"),
            "geometry": geometry_from(raw.get("geometry", {})),
            "presentation": Presentation(
                style=dict(raw.get("style", {})),
                primitives=list(raw.get("primitives", [])),
            ),
            "provenance": Provenance(
                svg_id=raw.get("svg_id"),
                source_xpath=raw.get("source_xpath"),
                parent_svg_id=raw.get("parent_svg_id"),
                source_sha256=source_sha,
            ),
            "metadata": EngineeringMetadata(custom=dict(raw.get("metadata", {}))),
        }

    def _element(self, raw: dict[str, Any], source_sha: str | None) -> EngineeringObject:
        bpmn_type = raw.get("bpmn_type", "unknown")
        common = self._common(raw, source_sha)

        if bpmn_type in TASK_TYPES:
            return Task(
                object_kind=ObjectKind.TASK,
                task_kind=TASK_TYPES[bpmn_type],
                **common,
            )
        if bpmn_type in EVENT_TYPES:
            return Event(
                object_kind=ObjectKind.EVENT,
                event_kind=EVENT_TYPES[bpmn_type],
                **common,
            )
        if bpmn_type in GATEWAY_TYPES:
            return Gateway(
                object_kind=ObjectKind.GATEWAY,
                gateway_kind=GATEWAY_TYPES[bpmn_type],
                **common,
            )
        if bpmn_type == "participant":
            return Participant(object_kind=ObjectKind.PARTICIPANT, **common)
        if bpmn_type in (
            "dataStoreReference",
            "dataObjectReference",
            "textAnnotation",
            "group",
        ):
            return Artifact(
                object_kind=ObjectKind.ARTIFACT,
                artifact_kind=bpmn_type,
                **common,
            )
        return EngineeringObject(object_kind=ObjectKind.UNKNOWN, **common)

    def _flow(self, raw: dict[str, Any], source_sha: str | None) -> Flow:
        common = self._common(raw, source_sha)
        kind = FLOW_TYPES.get(raw.get("flow_type"), FlowKind.ASSOCIATION)
        return Flow(
            object_kind=ObjectKind.FLOW,
            flow_kind=kind,
            source_ref=raw["source_ref"],
            target_ref=raw["target_ref"],
            **common,
        )
