
from pathlib import Path
import importlib

PACKAGES = ["mew_semantic", "mew_bpmn", "mew_rules", "mew_reporting", "mew_release"]

def test_all_packages_import():
    for package in PACKAGES:
        assert importlib.import_module(package) is not None

def test_repository_has_required_structure():
    root = Path(__file__).resolve().parents[2]
    for name in ["src", "tests", "docs", "schemas", ".github"]:
        assert (root / name).exists()

def test_core_modules_exist():
    root = Path(__file__).resolve().parents[2] / "src"
    expected = [
        "mew_semantic/parser.py",
        "mew_bpmn/repository.py",
        "mew_rules/evaluator.py",
        "mew_rules/standard_rules.py",
        "mew_reporting/engine.py",
        "mew_release/builder.py",
    ]
    for rel in expected:
        assert (root / rel).is_file(), rel
