# MEW – Model Engineering Workbench

MEW ist das konsolidierte Softwareprojekt für deterministisches BPMN-Engineering im
MES/MOM Solution Template Management.

## Architektur

```text
SVG
 └─ Semantic Parser
     └─ BPMN Object Model
         └─ Rule Repository / Loader
             └─ Evaluator / Dispatcher
                 └─ Standard Rule Set
                     └─ Reporting
                         └─ Release Builder
```

## Pakete

| Paket | Zweck |
|---|---|
| `mew_semantic` | Semantische Extraktion aus SVG |
| `mew_bpmn` | Typisiertes BPMN-Objektmodell und Repository |
| `mew_rules` | Rule Framework, KB-Loader, Evaluator und Standardregeln |
| `mew_reporting` | JSON-, Markdown- und HTML-Berichte |
| `mew_release` | Release Builder, Manifest und Integritätsprüfung |

## Lokale Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest
```

## Qualitätsprinzipien

- Single Source of Truth
- deterministische Ausgaben
- versionierte Regeln
- strukturierte Findings
- SHA-256-Provenienz
- automatisierte Tests
- reproduzierbare Releases

## Status

Konsolidierter Initialstand: `v0.9.3`.
