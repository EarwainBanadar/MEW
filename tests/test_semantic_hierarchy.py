from __future__ import annotations

from pathlib import Path

from mew_semantic import parse_svg


SVG = """<svg xmlns="http://www.w3.org/2000/svg">
  <g id="process-svg" data-element-id="process-1" data-bpmn-type="process">
    <g id="task-a-svg" data-element-id="task-a" data-bpmn-type="task"
       data-role-ref="role-1">
      <rect x="10" y="10" width="100" height="50" />
      <text>Task A</text>
    </g>
    <g id="role-svg" data-element-id="role-1" data-bpmn-type="role">
      <text>Operator</text>
    </g>
    <g id="subprocess-svg" data-element-id="sub-1" data-bpmn-type="subprocess">
      <g id="task-b-svg" data-element-id="task-b" data-bpmn-type="task"
         data-document-refs="doc-1 missing-doc">
        <rect x="150" y="10" width="100" height="50" />
      </g>
      <g id="doc-svg" data-element-id="doc-1" data-bpmn-type="document" />
    </g>
    <path id="flow-svg" data-element-id="flow-1" data-flow-type="sequenceFlow"
          data-source-ref="task-a" data-target-ref="task-b" d="M 110 35 L 150 35" />
  </g>
</svg>
"""


def _write_svg(tmp_path: Path) -> Path:
    path = tmp_path / "hierarchy.svg"
    path.write_text(SVG, encoding="utf-8")
    return path


def test_resolves_parent_and_scope_hierarchy(tmp_path: Path) -> None:
    document = parse_svg(_write_svg(tmp_path))

    assert document.schema_version == "0.2.0"
    assert document.index["task-a"]["parent"] == "process-1"
    assert document.index["task-a"]["scope"] == "process-1"
    assert document.index["task-b"]["parent"] == "sub-1"
    assert document.index["task-b"]["scope"] == "sub-1"
    assert document.index["flow-1"]["scope"] == "process-1"
    assert document.index["process-1"]["children"] == [
        "role-1",
        "sub-1",
        "task-a",
    ]


def test_builds_deterministic_scope_membership(tmp_path: Path) -> None:
    document = parse_svg(_write_svg(tmp_path))

    assert set(document.scopes) == {"process-1", "sub-1"}
    assert document.scopes["sub-1"].parent_scope_ref == "process-1"
    assert document.scopes["sub-1"].member_refs == ["doc-1", "sub-1", "task-b"]
    assert document.statistics["scopeCount"] == 2


def test_resolves_declared_and_flow_references(tmp_path: Path) -> None:
    document = parse_svg(_write_svg(tmp_path))

    references = {
        (reference.source_ref, reference.attribute, reference.target_ref): reference.resolved
        for reference in document.references
    }
    assert references[("flow-1", "data-source-ref", "task-a")] is True
    assert references[("flow-1", "data-target-ref", "task-b")] is True
    assert references[("task-a", "data-role-ref", "role-1")] is True
    assert references[("task-b", "data-document-refs", "doc-1")] is True
    assert references[("task-b", "data-document-refs", "missing-doc")] is False
    assert document.statistics["unresolvedReferenceCount"] == 1
    assert any(diagnostic.code == "SEM-REF-003" for diagnostic in document.diagnostics)
