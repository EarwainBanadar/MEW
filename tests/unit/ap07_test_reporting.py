from pathlib import Path
import json, pytest
from mew_reporting import ReportingEngine, ReportMetadata, ReportingError
SOURCE = Path('/mnt/data/AP9_3_4_STANDARD_RULE_SET/reports/AP9.3.4_Standard_Rule_Set_Baseline.json')
def engine(): return ReportingEngine()
def meta(): return ReportMetadata(report_id='TEST-001', title='Test Report', source_name='fixture.json')
def test_load_and_summary():
    s=engine().summarize(engine().load_evaluation(SOURCE)); assert s['selected_rule_count']==36 and s['finding_count']==69 and s['error_count']==0
def test_severity_counts():
    s=engine().summarize(engine().load_evaluation(SOURCE)); assert s['severity_counts']['warning']==66 and s['severity_counts']['info']==3
def test_json_valid():
    o=json.loads(engine().render_json(engine().load_evaluation(SOURCE),meta())); assert o['report_metadata']['report_id']=='TEST-001'
def test_markdown():
    t=engine().render_markdown(engine().load_evaluation(SOURCE),meta()); assert 'Management Summary' in t and 'KB-BPMN-015' in t
def test_html():
    t=engine().render_html(engine().load_evaluation(SOURCE),meta()); assert '<!doctype html>' in t and '<style>' in t and 'KB-BPMN-015' in t
def test_deterministic_json():
    d=engine().load_evaluation(SOURCE); m=meta(); assert engine().render_json(d,m) == engine().render_json(d,m)
def test_write_all(tmp_path):
    o=engine().write_all(engine().load_evaluation(SOURCE),meta(),tmp_path,'report'); assert set(o)=={'json','markdown','html'} and all(Path(p).exists() for p in o.values())
def test_missing_fields():
    with pytest.raises(ReportingError): engine().validate({'results':[]})
def test_count_mismatch():
    d=engine().load_evaluation(SOURCE); d['finding_count']=0
    with pytest.raises(ReportingError): engine().validate(d)
