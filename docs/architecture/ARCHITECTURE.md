# MEW-Architektur

## Leitprinzip

Das BPMN Object Model ist die zentrale fachliche Repräsentation. Parser, Regeln,
Berichte und Release-Prozesse greifen über explizite Schnittstellen darauf zu.

## Schichten

1. **Acquisition** – SVG und semantische Annotationen
2. **Semantic Parsing** – Extraktion und Normalisierung
3. **Domain Model** – typisierte BPMN-Objekte und Beziehungen
4. **Rule System** – deklarative Rule-KB und ausführbare Regeln
5. **Evaluation** – deterministischer Dispatcher und Policy-Auswertung
6. **Reporting** – JSON, Markdown und HTML
7. **Release** – Manifest, Prüfsummen, Paketierung und Verifikation

## Nichtfunktionale Anforderungen

- reproduzierbar
- testbar
- nachvollziehbar
- offline ausführbar
- CI-fähig
- releasefähig
