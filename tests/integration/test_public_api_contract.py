from __future__ import annotations

import importlib
import subprocess
import sys

import pytest

PUBLIC_EXPORTS = {
    "mew_semantic": {
        "Diagnostic",
        "SemanticDocument",
        "SemanticElement",
        "SemanticFlow",
        "SemanticSvgParser",
        "parse_svg",
    },
    "mew_bpmn": {"BPMNRepository", "SemanticModelBuilder"},
    "mew_reporting": {"ReportMetadata", "ReportingEngine", "ReportingError"},
    "mew_release": {
        "ArtifactRecord",
        "ReleaseBuildResult",
        "ReleaseBuilder",
        "ReleaseDescriptor",
        "ReleaseError",
    },
}

CLI_MODULES = [
    "mew_semantic.cli",
    "mew_bpmn.cli",
    "mew_rules.standard_cli",
    "mew_reporting.cli",
    "mew_release.cli",
]


@pytest.mark.parametrize(("package_name", "expected"), PUBLIC_EXPORTS.items())
def test_package_exports_are_explicit_and_importable(package_name, expected):
    package = importlib.import_module(package_name)
    assert set(package.__all__) == expected
    for name in expected:
        assert getattr(package, name) is not None


def test_rules_package_exports_are_explicit_and_importable():
    package = importlib.import_module("mew_rules")
    assert package.__all__
    assert len(package.__all__) == len(set(package.__all__))
    for name in package.__all__:
        assert not name.startswith("_")
        assert getattr(package, name) is not None


@pytest.mark.parametrize("module_name", CLI_MODULES)
def test_cli_help_contract(module_name):
    result = subprocess.run(
        [sys.executable, "-m", module_name, "--help"],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


@pytest.mark.parametrize("module_name", CLI_MODULES)
def test_cli_usage_errors_return_exit_code_two(module_name):
    result = subprocess.run(
        [sys.executable, "-m", module_name],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 2
    assert "usage:" in result.stderr.lower()
