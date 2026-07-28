import hashlib
import json
from pathlib import Path

import pytest
from mew_bpmn import SemanticModelBuilder
from mew_release import ReleaseBuilder, ReleaseDescriptor
from mew_reporting import ReportMetadata, ReportingEngine
from mew_rules.baseline_rules import create_baseline_registry
from mew_rules.evaluator import RuleEvaluator
from mew_rules.model import RuleContext
from mew_semantic import parse_svg

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "bpmn"
REFERENCE_SVG = FIXTURES / "reference_process.svg"
GOLDEN = FIXTURES / "reference_process.golden.json"
FIXED_TIME = "2026-01-01T00:00:00+00:00"


def _semantic_projection(document):
    data = document.to_dict()
    return {
        "elements": [
            {"engineering_id": item["engineering_id"], "bpmn_type": item["bpmn_type"]}
            for item in data["elements"]
        ],
        "flows": [
            {
                "engineering_id": item["engineering_id"],
                "flow_type": item["flow_type"],
                "source_ref": item["source_ref"],
                "target_ref": item["target_ref"],
            }
            for item in data["flows"]
        ],
        "diagnostics": data["diagnostics"],
        "statistics": {
            "semanticElementCount": data["statistics"]["semanticElementCount"],
            "flowCount": data["statistics"]["flowCount"],
        },
    }


def _evaluation_projection(summary):
    data = summary.to_dict()
    return {
        "selected_rule_count": data["selected_rule_count"],
        "finding_count": data["finding_count"],
        "error_count": data["error_count"],
        "overall_status": data["overall_status"],
        "results": [
            {
                "rule_id": result["rule_id"],
                "status": result["status"],
                "finding_count": result["finding_count"],
            }
            for result in data["results"]
        ],
    }


def _normalized_evaluation(summary):
    data = summary.to_dict()
    data["evaluation_id"] = "EVAL-FIXED"
    data["started_at_utc"] = FIXED_TIME
    data["completed_at_utc"] = FIXED_TIME
    for result in data["results"]:
        result["duration_ms"] = 0.0
        result["executed_at_utc"] = FIXED_TIME
    return data


def _evaluate(document):
    repository = SemanticModelBuilder().build(document.to_dict())
    return RuleEvaluator(create_baseline_registry()).evaluate(RuleContext(repository))


def test_reference_pipeline_matches_golden_and_builds_verified_release(tmp_path):
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))

    first_document = parse_svg(REFERENCE_SVG, strict=True)
    second_document = parse_svg(REFERENCE_SVG, strict=True)
    assert _semantic_projection(first_document) == golden["semantic"]
    assert _semantic_projection(second_document) == _semantic_projection(first_document)

    first_summary = _evaluate(first_document)
    second_summary = _evaluate(second_document)
    assert _evaluation_projection(first_summary) == golden["evaluation"]
    assert _evaluation_projection(second_summary) == _evaluation_projection(first_summary)

    source = tmp_path / "source"
    reports = source / "reports"
    reports.mkdir(parents=True)
    (source / "semantic.json").write_text(
        json.dumps(first_document.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    evaluation = _normalized_evaluation(first_summary)
    (source / "evaluation.json").write_text(
        json.dumps(evaluation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    reporting = ReportingEngine()
    metadata = ReportMetadata(
        report_id="BPMN-REGRESSION-001",
        title="BPMN Regression Report",
        source_name=REFERENCE_SVG.name,
        generated_at_utc=FIXED_TIME,
    )
    outputs = reporting.write_all(evaluation, metadata, reports, "bpmn-regression")
    assert set(outputs) == {"json", "markdown", "html"}
    assert reporting.render_json(evaluation, metadata) == reporting.render_json(
        evaluation, metadata
    )

    release = ReleaseBuilder()
    files = release.discover(source, ["**/*"])
    records = release.inventory(
        source,
        files,
        ["semantic.json", "evaluation.json", "reports/bpmn-regression.json"],
    )
    descriptor = ReleaseDescriptor(
        "REL_BPMN_REGRESSION",
        "0.10.0",
        "Deterministic BPMN regression reference",
        "Issue #5",
        "TEST",
        FIXED_TIME,
        str(source),
    )
    result = release.build(descriptor, records, tmp_path / "dist")
    verification = release.verify(Path(result.release_directory))
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))

    assert verification == {"status": "PASS", "checked": len(records), "failures": []}
    assert [item["logical_path"] for item in manifest["artifacts"]] == sorted(
        item["logical_path"] for item in manifest["artifacts"]
    )
    assert len(manifest["manifest_payload_sha256"]) == 64
    archive_sha256 = hashlib.sha256(Path(result.archive_path).read_bytes()).hexdigest()
    assert archive_sha256 == result.release_sha256

    tampered = Path(result.release_directory) / "artifacts" / "evaluation.json"
    tampered.write_text("{}\n", encoding="utf-8")
    failed = release.verify(Path(result.release_directory))
    assert failed["status"] == "FAIL"
    assert failed["failures"][0]["path"] == "evaluation.json"


def test_invalid_semantic_input_is_rejected_in_strict_mode(tmp_path):
    invalid = tmp_path / "invalid.svg"
    invalid.write_text(
        """<svg xmlns=\"http://www.w3.org/2000/svg\">
        <g id=\"start\" data-bpmn-type=\"startEvent\" data-element-id=\"start\"/>
        <path id=\"broken\" data-flow-type=\"sequenceFlow\" data-element-id=\"broken\"
              data-source-ref=\"start\" data-target-ref=\"missing\"/>
        </svg>""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Semantic parsing failed"):
        parse_svg(invalid, strict=True)
