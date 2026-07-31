import mew_semantic


SVG = """<svg xmlns="http://www.w3.org/2000/svg">
  <g id="process" data-element-id="process-1" data-bpmn-type="process">
    <g id="a" data-element-id="task-a" data-bpmn-type="task" data-role-ref="role-1" />
    <g id="b" data-element-id="task-b" data-bpmn-type="task" />
    <g id="c" data-element-id="task-c" data-bpmn-type="task" />
    <g id="role" data-element-id="role-1" data-bpmn-type="role" />
    <path id="f1" data-element-id="flow-1" data-flow-type="sequenceFlow"
          data-source-ref="task-a" data-target-ref="task-b" />
    <path id="f2" data-element-id="flow-2" data-flow-type="sequenceFlow"
          data-source-ref="task-b" data-target-ref="task-c" />
  </g>
</svg>
"""


def _document(tmp_path):
    path = tmp_path / "graph.svg"
    path.write_text(SVG, encoding="utf-8")
    return mew_semantic.parse_svg(path)


def test_dependency_graph_is_deterministic(tmp_path):
    graph = mew_semantic.build_dependency_graph(_document(tmp_path))

    assert graph.nodes == tuple(sorted(graph.nodes))
    assert graph.edges == tuple(sorted(graph.edges))
    assert graph.shortest_path("task-a", "task-c") == ("task-a", "task-b", "task-c")
    assert graph.reachable("task-a") == ("role-1", "task-b", "task-c")


def test_query_service_exposes_dependencies_and_dependants(tmp_path):
    service = mew_semantic.SemanticQueryService(_document(tmp_path))

    assert service.dependencies_of("task-a") == ("role-1", "task-b")
    assert service.dependencies_of("task-a", transitive=True) == (
        "role-1",
        "task-b",
        "task-c",
    )
    assert service.dependants_of("task-c", transitive=True) == ("task-b", "task-a")


def test_impact_and_scope_queries(tmp_path):
    service = mew_semantic.SemanticQueryService(_document(tmp_path))
    impact = service.impact_of("task-b")

    assert impact.downstream == ("task-c",)
    assert impact.upstream == ("task-a",)
    assert service.children_of("process-1") == ("role-1", "task-a", "task-b", "task-c")
    assert service.members_of_scope("process-1") == (
        "flow-1",
        "flow-2",
        "process-1",
        "role-1",
        "task-a",
        "task-b",
        "task-c",
    )
    assert service.path("process-1", "task-c", dependency_only=False) == (
        "process-1",
        "task-c",
    )
