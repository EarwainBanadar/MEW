from __future__ import annotations

import copy
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict

from .models import ReportingError, ReportMetadata

SEVERITY_ORDER = {"critical":0,"error":1,"warning":2,"info":3,"unknown":4}

class ReportingEngine:
    def __init__(self, generator_version: str = "1.0.0") -> None:
        self.generator_version = generator_version

    def load_evaluation(self, path: Path) -> Dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ReportingError(f"Cannot load evaluation: {exc}") from exc
        self.validate(data)
        return data

    def validate(self, data: Dict[str, Any]) -> None:
        required = {"evaluation_id","selected_rule_count","finding_count","error_count","overall_status","results"}
        missing = sorted(required - set(data))
        if missing:
            raise ReportingError("Missing evaluation fields: " + ", ".join(missing))
        if not isinstance(data["results"], list):
            raise ReportingError("results must be a list")
        actual = sum(len(r.get("findings", [])) for r in data["results"])
        if actual != data["finding_count"]:
            raise ReportingError(f"finding_count mismatch: declared={data['finding_count']} actual={actual}")

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.validate(data)
        out = copy.deepcopy(data)
        out["results"] = sorted(out["results"], key=lambda r: (r.get("rule_id", ""), r.get("rule_version", "")))
        for result in out["results"]:
            result["findings"] = sorted(result.get("findings", []), key=lambda f: (
                SEVERITY_ORDER.get(f.get("severity", "unknown"), 99),
                f.get("rule_id", ""), f.get("object_id") or "", f.get("message", "")
            ))
        return out

    def summarize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        d = self.normalize(data)
        findings = [f for r in d["results"] for f in r.get("findings", [])]
        severity = Counter(f.get("severity", "unknown") for f in findings)
        status = Counter(r.get("status", "unknown") for r in d["results"])
        attention = []
        for r in d["results"]:
            if r.get("findings") or r.get("status") == "error":
                attention.append({
                    "rule_id": r.get("rule_id"), "version": r.get("rule_version"),
                    "status": r.get("status"), "finding_count": len(r.get("findings", [])),
                    "error_message": r.get("error_message")
                })
        return {
            "evaluation_id": d["evaluation_id"], "overall_status": d["overall_status"],
            "selected_rule_count": d["selected_rule_count"], "finding_count": d["finding_count"],
            "error_count": d["error_count"],
            "severity_counts": dict(sorted(severity.items(), key=lambda kv: SEVERITY_ORDER.get(kv[0], 99))),
            "rule_status_counts": dict(sorted(status.items())),
            "rules_requiring_attention": attention,
        }

    def build_document(self, data: Dict[str, Any], metadata: ReportMetadata) -> Dict[str, Any]:
        normalized = self.normalize(data)
        return {"report_metadata": metadata.to_dict(), "summary": self.summarize(normalized), "evaluation": normalized}

    def render_json(self, data: Dict[str, Any], metadata: ReportMetadata) -> str:
        return json.dumps(self.build_document(data, metadata), indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    def render_markdown(self, data: Dict[str, Any], metadata: ReportMetadata) -> str:
        doc = self.build_document(data, metadata); s = doc["summary"]; e = doc["evaluation"]
        lines = [f"# {metadata.title}", "", f"**Report-ID:** `{metadata.report_id}`  ",
                 f"**Evaluation-ID:** `{s['evaluation_id']}`  ", f"**Status:** **{s['overall_status']}**  ",
                 f"**Generator:** {metadata.generator_version}", "", "## Management Summary", "",
                 "| Kennzahl | Wert |", "|---|---:|", f"| Ausgeführte Regeln | {s['selected_rule_count']} |",
                 f"| Findings | {s['finding_count']} |", f"| technische Fehler | {s['error_count']} |", "",
                 "## Findings nach Severity", "", "| Severity | Anzahl |", "|---|---:|"]
        for key, value in s["severity_counts"].items():
            lines.append(f"| {key} | {value} |")
        lines += ["", "## Regeln mit Handlungsbedarf", "", "| Rule-ID | Version | Status | Findings |", "|---|---|---|---:|"]
        if s["rules_requiring_attention"]:
            for r in s["rules_requiring_attention"]:
                lines.append(f"| {r['rule_id']} | {r['version']} | {r['status']} | {r['finding_count']} |")
        else:
            lines.append("| – | – | PASS | 0 |")
        lines += ["", "## Detaillierte Findings", ""]
        number = 0
        for result in e["results"]:
            for finding in result.get("findings", []):
                number += 1
                lines += [f"### {number}. {finding.get('rule_id')} – {finding.get('severity','unknown').upper()}", "",
                          f"- **Objekt:** `{finding.get('object_id') or '–'}`",
                          f"- **Meldung:** {finding.get('message','')}",
                          f"- **Empfehlung:** {finding.get('recommendation') or '–'}", ""]
        if number == 0:
            lines.append("Keine Findings.")
        lines += ["", "## Reproduzierbarkeit", "", f"Quelle: `{metadata.source_name or 'nicht angegeben'}`", ""]
        return "\n".join(lines)

    def render_html(self, data: Dict[str, Any], metadata: ReportMetadata) -> str:
        doc = self.build_document(data, metadata); s = doc["summary"]; e = doc["evaluation"]
        esc = html.escape
        sev_rows = "".join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>" for k,v in s["severity_counts"].items()) or "<tr><td>none</td><td>0</td></tr>"
        rule_rows = "".join(f"<tr><td>{esc(str(r['rule_id']))}</td><td>{esc(str(r['version']))}</td><td>{esc(str(r['status']))}</td><td>{r['finding_count']}</td></tr>" for r in s["rules_requiring_attention"]) or "<tr><td colspan='4'>Keine Regeln mit Handlungsbedarf</td></tr>"
        cards = []
        for result in e["results"]:
            for f in result.get("findings", []):
                cards.append("<article class='finding'><h3>{} · {}</h3><dl><dt>Objekt</dt><dd>{}</dd><dt>Meldung</dt><dd>{}</dd><dt>Empfehlung</dt><dd>{}</dd></dl></article>".format(
                    esc(str(f.get("rule_id"))), esc(str(f.get("severity","unknown")).upper()),
                    esc(str(f.get("object_id") or "–")), esc(str(f.get("message", ""))),
                    esc(str(f.get("recommendation") or "–"))))
        cards_html = "".join(cards) or "<p>Keine Findings.</p>"
        return """<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title><style>
body{{font-family:Arial,sans-serif;margin:0;background:#f5f6f8;color:#20242a}}main{{max-width:1200px;margin:auto;padding:32px}}header,.panel,.finding{{background:white;border:1px solid #d9dde3;border-radius:8px;padding:20px;margin-bottom:18px}}h1,h2{{margin-top:0}}.status{{font-weight:700;font-size:1.2rem}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #d9dde3;padding:8px;text-align:left}}th{{background:#eef1f4}}dt{{font-weight:700}}dd{{margin:0 0 8px 0}}code{{word-break:break-all}}</style></head><body><main>
<header><h1>{title}</h1><p>Report-ID: <code>{report_id}</code></p><p>Evaluation-ID: <code>{evaluation_id}</code></p><p class='status'>Status: {status}</p></header>
<section class='panel'><h2>Management Summary</h2><table><tr><th>Kennzahl</th><th>Wert</th></tr><tr><td>Ausgeführte Regeln</td><td>{rules}</td></tr><tr><td>Findings</td><td>{findings}</td></tr><tr><td>Technische Fehler</td><td>{errors}</td></tr></table></section>
<section class='panel'><h2>Findings nach Severity</h2><table><tr><th>Severity</th><th>Anzahl</th></tr>{sev_rows}</table></section>
<section class='panel'><h2>Regeln mit Handlungsbedarf</h2><table><tr><th>Rule-ID</th><th>Version</th><th>Status</th><th>Findings</th></tr>{rule_rows}</table></section>
<section><h2>Detaillierte Findings</h2>{cards}</section>
<footer class='panel'>Generator {generator} · Quelle <code>{source}</code></footer>
</main></body></html>""".format(title=esc(metadata.title),report_id=esc(metadata.report_id),evaluation_id=esc(s["evaluation_id"]),status=esc(s["overall_status"]),rules=s["selected_rule_count"],findings=s["finding_count"],errors=s["error_count"],sev_rows=sev_rows,rule_rows=rule_rows,cards=cards_html,generator=esc(metadata.generator_version),source=esc(metadata.source_name or "nicht angegeben"))

    def write_all(self, data: Dict[str, Any], metadata: ReportMetadata, output_dir: Path, stem: str = "evaluation-report") -> Dict[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = {"json": output_dir/f"{stem}.json", "markdown": output_dir/f"{stem}.md", "html": output_dir/f"{stem}.html"}
        outputs["json"].write_text(self.render_json(data, metadata), encoding="utf-8")
        outputs["markdown"].write_text(self.render_markdown(data, metadata), encoding="utf-8")
        outputs["html"].write_text(self.render_html(data, metadata), encoding="utf-8")
        return {key: str(value) for key, value in outputs.items()}
