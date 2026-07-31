from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from .model import SemanticDocument


@dataclass(frozen=True, order=True)
class GraphEdge:
    source_ref: str
    target_ref: str
    relation: str
    evidence_ref: str | None = None


@dataclass(frozen=True)
class SemanticGraph:
    nodes: tuple[str, ...]
    edges: tuple[GraphEdge, ...]

    def outgoing(self, node_ref: str, relations: Iterable[str] | None = None) -> tuple[GraphEdge, ...]:
        allowed = set(relations) if relations is not None else None
        return tuple(
            edge
            for edge in self.edges
            if edge.source_ref == node_ref and (allowed is None or edge.relation in allowed)
        )

    def incoming(self, node_ref: str, relations: Iterable[str] | None = None) -> tuple[GraphEdge, ...]:
        allowed = set(relations) if relations is not None else None
        return tuple(
            edge
            for edge in self.edges
            if edge.target_ref == node_ref and (allowed is None or edge.relation in allowed)
        )

    def reachable(
        self,
        start_ref: str,
        *,
        direction: str = "outgoing",
        relations: Iterable[str] | None = None,
        max_depth: int | None = None,
    ) -> tuple[str, ...]:
        if start_ref not in self.nodes:
            return ()
        if direction not in {"outgoing", "incoming"}:
            raise ValueError("direction must be 'outgoing' or 'incoming'")

        visited = {start_ref}
        result: list[str] = []
        queue: deque[tuple[str, int]] = deque([(start_ref, 0)])
        while queue:
            current, depth = queue.popleft()
            if max_depth is not None and depth >= max_depth:
                continue
            edges = (
                self.outgoing(current, relations)
                if direction == "outgoing"
                else self.incoming(current, relations)
            )
            neighbours = sorted(
                edge.target_ref if direction == "outgoing" else edge.source_ref for edge in edges
            )
            for neighbour in neighbours:
                if neighbour in visited:
                    continue
                visited.add(neighbour)
                result.append(neighbour)
                queue.append((neighbour, depth + 1))
        return tuple(result)

    def shortest_path(
        self,
        source_ref: str,
        target_ref: str,
        relations: Iterable[str] | None = None,
    ) -> tuple[str, ...]:
        if source_ref not in self.nodes or target_ref not in self.nodes:
            return ()
        if source_ref == target_ref:
            return (source_ref,)

        queue: deque[tuple[str, tuple[str, ...]]] = deque([(source_ref, (source_ref,))])
        visited = {source_ref}
        while queue:
            current, path = queue.popleft()
            neighbours = sorted(edge.target_ref for edge in self.outgoing(current, relations))
            for neighbour in neighbours:
                if neighbour in visited:
                    continue
                next_path = (*path, neighbour)
                if neighbour == target_ref:
                    return next_path
                visited.add(neighbour)
                queue.append((neighbour, next_path))
        return ()


def build_model_graph(document: SemanticDocument) -> SemanticGraph:
    nodes = sorted(document.index)
    edges: set[GraphEdge] = set()

    for element in document.elements:
        if element.parent_ref:
            edges.add(GraphEdge(element.parent_ref, element.engineering_id, "contains"))

    for flow in document.flows:
        if flow.source_ref in document.index and flow.target_ref in document.index:
            edges.add(
                GraphEdge(
                    flow.source_ref,
                    flow.target_ref,
                    "flow",
                    evidence_ref=flow.engineering_id,
                )
            )

    for reference in document.references:
        if reference.resolved:
            edges.add(
                GraphEdge(
                    reference.source_ref,
                    reference.target_ref,
                    "reference",
                    evidence_ref=reference.attribute,
                )
            )

    return SemanticGraph(tuple(nodes), tuple(sorted(edges)))


def build_dependency_graph(document: SemanticDocument) -> SemanticGraph:
    model_graph = build_model_graph(document)
    dependency_edges = tuple(
        edge for edge in model_graph.edges if edge.relation in {"flow", "reference"}
    )
    return SemanticGraph(model_graph.nodes, dependency_edges)
