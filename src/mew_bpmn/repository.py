
from __future__ import annotations

from contextlib import AbstractContextManager
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Set

from .model import EngineeringObject, Flow, FlowNode, ObjectKind


class RepositoryError(RuntimeError):
    pass

class DuplicateEngineeringId(RepositoryError):
    pass

class UnresolvedReference(RepositoryError):
    pass

@dataclass
class GraphAnalysis:
    node_count: int
    edge_count: int
    roots: List[str]
    sinks: List[str]
    unreachable: List[str]
    cycles: List[List[str]]

class BPMNRepository:
    """Single access point for typed BPMN engineering objects."""
    def __init__(self) -> None:
        self._objects: Dict[str, EngineeringObject] = {}
        self._version: int = 0

    @property
    def version(self) -> int:
        return self._version

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[EngineeringObject]:
        return iter(self._objects.values())

    def add(self, obj: EngineeringObject) -> None:
        if obj.engineering_id in self._objects:
            raise DuplicateEngineeringId(obj.engineering_id)
        self._objects[obj.engineering_id] = obj

    def get(self, engineering_id: str) -> EngineeringObject:
        try:
            return self._objects[engineering_id]
        except KeyError as exc:
            raise KeyError(f"Unknown engineering ID: {engineering_id}") from exc

    def find(self, *, object_kind: Optional[ObjectKind] = None,
             bpmn_type: Optional[str] = None) -> List[EngineeringObject]:
        result = list(self._objects.values())
        if object_kind is not None:
            result = [o for o in result if o.object_kind == object_kind]
        if bpmn_type is not None:
            result = [o for o in result if o.bpmn_type == bpmn_type]
        return result

    def flows(self) -> List[Flow]:
        return [o for o in self._objects.values() if isinstance(o, Flow)]

    def flow_nodes(self) -> List[FlowNode]:
        return [o for o in self._objects.values() if isinstance(o, FlowNode)]

    def resolve_relationships(self) -> None:
        for obj in self._objects.values():
            obj.incoming.clear()
            obj.outgoing.clear()
        missing: List[str] = []
        for flow in self.flows():
            if flow.source_ref not in self._objects:
                missing.append(f"{flow.engineering_id}.source_ref={flow.source_ref}")
            if flow.target_ref not in self._objects:
                missing.append(f"{flow.engineering_id}.target_ref={flow.target_ref}")
        if missing:
            raise UnresolvedReference("; ".join(missing))
        for flow in self.flows():
            self._objects[flow.source_ref].outgoing.append(flow.engineering_id)
            self._objects[flow.target_ref].incoming.append(flow.engineering_id)

    def validate(self) -> List[str]:
        errors: List[str] = []
        seen: Set[str] = set()
        for obj in self._objects.values():
            if obj.engineering_id in seen:
                errors.append(f"Duplicate ID: {obj.engineering_id}")
            seen.add(obj.engineering_id)
        for flow in self.flows():
            if flow.source_ref not in self._objects:
                errors.append(f"Missing source: {flow.engineering_id}->{flow.source_ref}")
            if flow.target_ref not in self._objects:
                errors.append(f"Missing target: {flow.engineering_id}->{flow.target_ref}")
        return errors

    def graph_analysis(self) -> GraphAnalysis:
        nodes = {n.engineering_id for n in self.flow_nodes()}
        adj: Dict[str, List[str]] = {n: [] for n in nodes}
        indegree = {n: 0 for n in nodes}
        sequence_edges = 0
        for f in self.flows():
            if f.flow_kind.value != "sequence":
                continue
            if f.source_ref in nodes and f.target_ref in nodes:
                adj[f.source_ref].append(f.target_ref)
                indegree[f.target_ref] += 1
                sequence_edges += 1
        roots = sorted([n for n in nodes if indegree[n] == 0])
        sinks = sorted([n for n in nodes if not adj[n]])

        reachable: Set[str] = set()
        stack = list(roots)
        while stack:
            n = stack.pop()
            if n in reachable:
                continue
            reachable.add(n)
            stack.extend(adj[n])
        unreachable = sorted(nodes - reachable)

        cycles: List[List[str]] = []
        color = {n: 0 for n in nodes}
        trail: List[str] = []
        def dfs(n: str) -> None:
            color[n] = 1
            trail.append(n)
            for nxt in adj[n]:
                if color[nxt] == 0:
                    dfs(nxt)
                elif color[nxt] == 1 and nxt in trail:
                    i = trail.index(nxt)
                    cycle = trail[i:] + [nxt]
                    if cycle not in cycles:
                        cycles.append(cycle)
            trail.pop()
            color[n] = 2
        for n in sorted(nodes):
            if color[n] == 0:
                dfs(n)

        return GraphAnalysis(
            node_count=len(nodes), edge_count=sequence_edges,
            roots=roots, sinks=sinks, unreachable=unreachable, cycles=cycles
        )

    def to_dict(self) -> dict:
        return {
            "repository_version": self._version,
            "objects": [self._objects[k].to_dict() for k in sorted(self._objects)]
        }

    def transaction(self) -> "RepositoryTransaction":
        return RepositoryTransaction(self)

class RepositoryTransaction(AbstractContextManager):
    """Atomic in-memory transaction with rollback on exception."""
    def __init__(self, repository: BPMNRepository) -> None:
        self.repository = repository
        self._snapshot = None

    def __enter__(self) -> BPMNRepository:
        self._snapshot = deepcopy(self.repository._objects)
        return self.repository

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.repository._objects = self._snapshot
            return False
        self.repository.resolve_relationships()
        errors = self.repository.validate()
        if errors:
            self.repository._objects = self._snapshot
            raise RepositoryError("; ".join(errors))
        self.repository._version += 1
        return False
