
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

class ObjectKind(str, Enum):
    PROCESS = "process"
    PARTICIPANT = "participant"
    LANE_SET = "laneSet"
    LANE = "lane"
    TASK = "task"
    EVENT = "event"
    GATEWAY = "gateway"
    FLOW = "flow"
    ARTIFACT = "artifact"
    UNKNOWN = "unknown"

class EventKind(str, Enum):
    START = "startEvent"
    INTERMEDIATE_CATCH = "intermediateCatchEvent"
    INTERMEDIATE_THROW = "intermediateThrowEvent"
    BOUNDARY = "boundaryEvent"
    END = "endEvent"

class GatewayKind(str, Enum):
    EXCLUSIVE = "exclusiveGateway"
    INCLUSIVE = "inclusiveGateway"
    PARALLEL = "parallelGateway"
    COMPLEX = "complexGateway"
    EVENT_BASED = "eventBasedGateway"

class TaskKind(str, Enum):
    GENERIC = "task"
    USER = "userTask"
    MANUAL = "manualTask"
    SERVICE = "serviceTask"
    SCRIPT = "scriptTask"
    BUSINESS_RULE = "businessRuleTask"
    RECEIVE = "receiveTask"
    SEND = "sendTask"
    CALL_ACTIVITY = "callActivity"
    SUB_PROCESS = "subProcess"

class FlowKind(str, Enum):
    SEQUENCE = "sequence"
    MESSAGE = "message"
    ASSOCIATION = "association"
    INTERFACE_IN = "process-interface-in"
    INTERFACE_OUT = "process-interface-out"

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Bounds:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains(self, other: "Bounds") -> bool:
        return (self.x <= other.x and self.y <= other.y and
                self.right >= other.right and self.bottom >= other.bottom)

@dataclass
class Geometry:
    bounds: Optional[Bounds] = None
    points: List[Point] = field(default_factory=list)
    path_data: Optional[str] = None
    transform: Optional[str] = None

@dataclass
class Presentation:
    style: Dict[str, str] = field(default_factory=dict)
    primitives: List[Dict[str, Any]] = field(default_factory=list)
    visible: bool = True
    layer: Optional[str] = None

@dataclass
class Provenance:
    svg_id: Optional[str] = None
    source_xpath: Optional[str] = None
    parent_svg_id: Optional[str] = None
    source_sha256: Optional[str] = None

@dataclass
class EngineeringMetadata:
    version: str = "1.0"
    review_status: str = "UNREVIEWED"
    qa_status: str = "UNTESTED"
    release_status: str = "DRAFT"
    custom: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EngineeringObject:
    engineering_id: str
    object_kind: ObjectKind
    bpmn_type: str
    name: Optional[str] = None
    documentation: Optional[str] = None
    geometry: Geometry = field(default_factory=Geometry)
    presentation: Presentation = field(default_factory=Presentation)
    provenance: Provenance = field(default_factory=Provenance)
    metadata: EngineeringMetadata = field(default_factory=EngineeringMetadata)
    incoming: List[str] = field(default_factory=list)
    outgoing: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["object_kind"] = self.object_kind.value
        return data

@dataclass
class Process(EngineeringObject):
    participant_ids: List[str] = field(default_factory=list)
    lane_set_ids: List[str] = field(default_factory=list)
    flow_node_ids: List[str] = field(default_factory=list)
    flow_ids: List[str] = field(default_factory=list)
    artifact_ids: List[str] = field(default_factory=list)

@dataclass
class Participant(EngineeringObject):
    process_ref: Optional[str] = None

@dataclass
class LaneSet(EngineeringObject):
    lane_ids: List[str] = field(default_factory=list)

@dataclass
class Lane(EngineeringObject):
    parent_lane_id: Optional[str] = None
    child_lane_ids: List[str] = field(default_factory=list)
    flow_node_ids: List[str] = field(default_factory=list)

@dataclass
class FlowNode(EngineeringObject):
    lane_id: Optional[str] = None

@dataclass
class Task(FlowNode):
    task_kind: TaskKind = TaskKind.GENERIC

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["task_kind"] = self.task_kind.value
        return data

@dataclass
class Event(FlowNode):
    event_kind: EventKind = EventKind.START

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["event_kind"] = self.event_kind.value
        return data

@dataclass
class Gateway(FlowNode):
    gateway_kind: GatewayKind = GatewayKind.EXCLUSIVE

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["gateway_kind"] = self.gateway_kind.value
        return data

@dataclass
class Flow(EngineeringObject):
    flow_kind: FlowKind = FlowKind.SEQUENCE
    source_ref: str = ""
    target_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["flow_kind"] = self.flow_kind.value
        return data

@dataclass
class Artifact(EngineeringObject):
    artifact_kind: str = "artifact"
