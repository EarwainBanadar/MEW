import mew_semantic


SVG = """<svg xmlns="http://www.w3.org/2000/svg">
  <g id="process" data-element-id="process-1" data-bpmn-type="process">
    <g id="a" data-element-id="task-a" data-bpmn-type="task" data-role-ref="missing-role">
      <text>Prepare</text>
    </g>
    <g id="b" data-element-id="task-b" data-bpmn-type="task" />
    <g id="orphan" data-element-id="task-orphan" data-bpmn-type="task">
      <text>Orphan</text>
    </g>
    <path id="f1" data-element-id="flow-1" data-flow-type="sequenceFlow"
          data-source-ref="task-a" data-target-ref="task-b" />
  </g>
</svg>
"""


def _document(tmp_path):
    path = tmp_path / "quality.svg"
    path.write_text(SVG, encoding="utf-8")
    return mew_semantic.parse_svg(path)


def test_default_profile_fails_on_unresolved_reference(tmp_path):
    result = mew_semantic.validate_quality(_document(tmp_path))

    assert result.passed is False
    assert result.counts["error"] == 1
    assert result.counts["warning"] == 2
    assert result.score == 75
    assert [finding.rule_id for finding in result.findings] == [
        "QF-REF-001",
        "QF-GRAPH-001",
        "QF-NAME-001",
    ]


def test_profile_controls_gate_and_rule_activation(tmp_path):
    profile = mew_semantic.QualityProfile(
        profile_id="advisory",
        fail_at=mew_semantic.QualitySeverity.CRITICAL,
        disabled_rules=frozenset({"QF-GRAPH-001"}),
        severity_overrides={
            "QF-REF-001": mew_semantic.QualitySeverity.WARNING,
        },
    )
    result = mew_semantic.validate_quality(_document(tmp_path), profile)

    assert result.profile_id == "advisory"
    assert result.passed is True
    assert result.counts["error"] == 0
    assert result.counts["warning"] == 2


def test_quality_report_is_deterministic_and_serializable(tmp_path):
    first = mew_semantic.validate_quality(_document(tmp_path))
    second = mew_semantic.validate_quality(_document(tmp_path))

    assert first == second
    payload = first.to_dict()
    assert payload["passed"] is False
    assert payload["findings"][0]["severity"] == "error"
    assert payload["findings"][0]["element_ref"] == "task-a"
