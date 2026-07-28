from pathlib import Path

import pytest

from mew_rules.kb_loader import KnowledgeBaseLoader, parse_markdown_rule
from mew_rules.kb_repository import *
from mew_rules.model import RuleCategory, RuleSeverity

ROOT=Path(__file__).resolve().parents[1];KB=ROOT/'examples'/'kb'
def test_semver():
 assert parse_semver('1.2.3')==(1,2,3)
 with pytest.raises(InvalidKnowledgeRule):parse_semver('1.2')
def test_load_formats():
 loader=KnowledgeBaseLoader();assert loader.load_file(KB/'KB-RULE-001_v1.0.0.json').source_format=='json';assert loader.load_file(KB/'KB-RULE-002_v1.0.0.md').source_format=='markdown'
def test_versions_latest():
 r=KnowledgeBaseLoader().load_directory(KB);assert len(r)==4;assert r.versions('KB-RULE-001')==['1.0.0','1.1.0'];assert r.get('KB-RULE-001').definition.version=='1.1.0'
def test_manifest_latest(): assert KnowledgeBaseLoader().load_directory(KB).manifest(True)['rule_count']==3
def test_filters():
 r=KnowledgeBaseLoader().load_directory(KB);assert len(r.list(category=RuleCategory.GOVERNANCE))==1;assert len(r.list(severity=RuleSeverity.CRITICAL))==2
def test_duplicate():
 loader=KnowledgeBaseLoader();x=loader.load_file(KB/'KB-RULE-001_v1.0.0.json');r=KnowledgeBaseRepository();r.add(x)
 with pytest.raises(DuplicateKnowledgeRule):r.add(x)
def test_bad_markdown():
 with pytest.raises(InvalidKnowledgeRule):parse_markdown_rule('#bad')
