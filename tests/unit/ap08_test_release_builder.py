from pathlib import Path
import json, zipfile, pytest
from mew_release.builder import ReleaseBuilder, sha256_file
from mew_release.models import ReleaseDescriptor, ReleaseError

@pytest.fixture
def source(tmp_path):
    root=tmp_path/"source"; (root/"reports").mkdir(parents=True); (root/"docs").mkdir()
    (root/"reports/a.json").write_text('{"ok":true}\n',encoding="utf-8")
    (root/"docs/a.md").write_text('# A\n',encoding="utf-8")
    return root

def descriptor(root):
    return ReleaseDescriptor("REL_TEST","1.0.0","Test","AP9.3.5.2","RC","2026-01-01T00:00:00+00:00",str(root))

def test_discover_is_sorted(source):
    files=ReleaseBuilder().discover(source,["**/*"])
    assert [p.relative_to(source).as_posix() for p in files]==["docs/a.md","reports/a.json"]

def test_inventory_hashes_and_types(source):
    records=ReleaseBuilder().inventory(source,ReleaseBuilder().discover(source,["**/*"]),["reports/a.json"])
    assert records[1].sha256==sha256_file(source/"reports/a.json")
    assert records[0].media_type=="text/markdown"

def test_missing_required_is_rejected(source):
    with pytest.raises(ReleaseError):
        ReleaseBuilder().inventory(source,ReleaseBuilder().discover(source,["**/*"]),["missing.txt"])

def test_empty_release_is_rejected(tmp_path):
    with pytest.raises(ReleaseError): ReleaseBuilder().build(descriptor(tmp_path),[],tmp_path/"out")

def test_build_verify_and_archive(source,tmp_path):
    b=ReleaseBuilder(); records=b.inventory(source,b.discover(source,["**/*"]),["reports/a.json"])
    result=b.build(descriptor(source),records,tmp_path/"dist")
    assert Path(result.archive_path).exists(); assert b.verify(Path(result.release_directory))["status"]=="PASS"
    with zipfile.ZipFile(result.archive_path) as z: assert any(x.endswith("release-manifest.json") for x in z.namelist())

def test_tamper_is_detected(source,tmp_path):
    b=ReleaseBuilder(); records=b.inventory(source,b.discover(source,["**/*"])); result=b.build(descriptor(source),records,tmp_path/"dist")
    (Path(result.release_directory)/"artifacts/reports/a.json").write_text("tampered",encoding="utf-8")
    assert b.verify(Path(result.release_directory))["status"]=="FAIL"

def test_manifest_is_deterministically_sorted(source,tmp_path):
    b=ReleaseBuilder(); records=b.inventory(source,b.discover(source,["**/*"])); result=b.build(descriptor(source),records,tmp_path/"dist")
    m=json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    paths=[a["logical_path"] for a in m["artifacts"]]
    assert paths==sorted(paths)

def test_changed_source_after_inventory_rejected(source,tmp_path):
    b=ReleaseBuilder(); records=b.inventory(source,b.discover(source,["**/*"])); (source/"docs/a.md").write_text("changed",encoding="utf-8")
    with pytest.raises(ReleaseError): b.build(descriptor(source),records,tmp_path/"dist")
