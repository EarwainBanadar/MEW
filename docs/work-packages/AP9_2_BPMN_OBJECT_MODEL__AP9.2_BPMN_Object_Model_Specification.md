# AP9.2 – BPMN Object Model

## Ausführungsstatus

**AUSGEFÜHRT – IMPLEMENTIERT – TECHNISCHE QA BESTANDEN – BENUTZER-QA AUSSTEHEND**

## Zweck

AP9.2 materialisiert die AP9.1-Zwischenrepräsentation in ein typsicheres, semantisches BPMN-Objektmodell. Das Repository ist der zentrale Zugriffspunkt und bildet die Single Source of Truth für nachfolgende Regel-, Transformations-, Layout- und QA-Engines.

## Implementierte Bestandteile

- typsichere Engineering-Objekte
- Task-, Event-, Gateway-, Flow-, Participant- und Artifact-Klassen
- getrennte Modelle für Semantik, Geometrie, Darstellung, Provenienz und Engineering-Metadaten
- zentrales BPMNRepository
- explizite Source-/Target-Beziehungen
- Aufbau von Incoming-/Outgoing-Indizes
- transaktionale Änderungen mit Rollback
- gerichtete Graphanalyse für Sequence Flows
- JSON-Serialisierung
- CLI
- JSON-Schema
- Unit- und Integrationstests auf der freigegebenen Baseline

## Abgrenzung

AP9.2 verändert die SVG-Datei nicht. Lane-Strukturen können nur dann materialisiert werden, wenn AP9.1 entsprechende semantische Lane-Objekte liefert. Die aktuelle AP9.1-Ausgabe enthält Participant, Flow Nodes, Flows und Artefakte, jedoch keine expliziten Lane-Objekte.

## Verwendung

```bash
PYTHONPATH=src python -m mew_bpmn.cli   reports/Template_Management_RC1.12.6_semantic.json   -o reports/Template_Management_RC1.12.6_object_repository.json   --analysis reports/AP9.2_Graph_Analysis.json
```

## Exit Codes

- `0`: Objektmodell erfolgreich aufgebaut und referenziell valide
- `2`: Repositoryfehler
