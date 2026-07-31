from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .graph import SemanticGraph, build_dependency_graph, build_model_graph
from .model import SemanticDocument


@dataclass(frozen=True)
class ImpactResult:
    origin_ref: str
    downstream: tuple[str, ...]
    upstream: tuple[str, ...]


class SemanticQueryService:
    def __init__(self, document: SemanticDocument):
        self.document = document
        self.model_graph = build_model_graph(document)
        self.dependency_graph = build_dependency_graph(document)

    def exists(self, engineering_id: str) -> bool:
        return engineering_id in self.document.index

    def children_of(self, engineering_id: str) -> tuple[str, ...]:
        record = self.document.index.get(engineering_id, {})
        return tuple(record.get("children", ()))

    def members_of_scope(self, scope_ref: str) -> tuple[str, ...]:
        scope = self.document.scopes.get(scope_ref)
        return tuple(scope.member_refs) if scope else ()

    def dependencies_of(
        self,
        engineering_id: str,
        *,
        transitive: bool = False,
        relations: Iterable[str] | None = None,
    ) -> tuple[str, ...]:
        if transitive:
            return self.dependency_graph.reachable(
                engineering_id,
                direction="outgoing",
                relations=relations,
            )
        return tuple(
            sorted(
                {
                    edge.target_ref
                    for edge in self.dependency_graph.outgoing(engineering_id, relations)
                }
            )
        )

    def dependants_of(
        self,
        engineering_id: str,
        *,
        transitive: bool = False,
        relations: Iterable[str] | None = None,
    ) -> tuple[str, ...]:
        if transitive:
            return self.dependency_graph.reachable(
                engineering_id,
                direction="incoming",
                relations=relations,
            )
        return tuple(
            sorted(
                {
                    edge.source_ref
                    for edge in self.dependency_graph.incoming(engineering_id, relations)
                }
            )
        )

    def impact_of(self, engineering_id: str) -> ImpactResult:
        return ImpactResult(
            origin_ref=engineering_id,
            downstream=self.dependency_graph.reachable(engineering_id, direction="outgoing"),
            upstream=self.dependency_graph.reachable(engineering_id, direction="incoming"),
        )

    def path(
        self,
        source_ref: str,
        target_ref: str,
        *,
        dependency_only: bool = True,
        relations: Iterable[str] | None = None,
    ) -> tuple[str, ...]:
        graph: SemanticGraph = self.dependency_graph if dependency_only else self.model_graph
        return graph.shortest_path(source_ref, target_ref, relations)
