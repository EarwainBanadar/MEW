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
```

Vor jedem Commit ist das lokale Quality Gate auszuführen:

```bash
mew-quality
```

Der Befehl führt in dieser Reihenfolge aus:

1. `python -m ruff check src tests --fix`
2. `python -m ruff check src tests`
3. `python -m pytest`

Für eine rein prüfende Ausführung ohne automatische Ruff-Korrekturen steht zur Verfügung:

```bash
mew-quality --check-only
```

Ein Commit gilt nur dann als freigabefähig, wenn das lokale Quality Gate mit Exit-Code `0`
endet. GitHub Actions bestätigt anschließend denselben Qualitätsstand auf Python 3.10 bis
3.13 sowie unter Linux und Windows.

## Ruff-Qualitätsgate

Die Ruff-Konfiguration wird in `pyproject.toml` schrittweise erweitert. Der aktuell aktive
Stand umfasst:

| Regelgruppe | Zweck |
|---|---|
| `E9` | schwerwiegende Syntax- und Laufzeitfehler |
| `F401`, `F63`, `F7`, `F82` | ungenutzte Imports und ausgewählte Pyflakes-Fehler |
| `I` | deterministische Importreihenfolge |
| `UP006`, `UP035`, `UP045` | Python-3.10-kompatible Typing-Modernisierung |

Pauschale dateiweite `noqa`-Umgehungen sind nicht zulässig. Notwendige punktuelle
Ausnahmen müssen eng begrenzt und fachlich begründet werden. Neue Ruff-Regelgruppen werden
jeweils in einem separaten Pull Request aktiviert, bereinigt und durch das vollständige
Quality Gate validiert.

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
