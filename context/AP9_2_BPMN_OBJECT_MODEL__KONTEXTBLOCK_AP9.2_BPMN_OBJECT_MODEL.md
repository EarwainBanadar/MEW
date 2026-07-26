# KONTEXTBLOCK – AP9.2 BPMN Object Model

## KB-OBJECT-001 – Stabile Engineering-ID
Jedes Engineering-Objekt besitzt eine eindeutige und über Layoutänderungen stabile Engineering-ID.

## KB-OBJECT-002 – Keine fachliche Referenz über SVG-ID
Fachliche Beziehungen referenzieren ausschließlich Engineering-IDs.

## KB-OBJECT-003 – Explizite Beziehungen
Source-, Target-, Incoming- und Outgoing-Beziehungen werden explizit modelliert.

## KB-OBJECT-004 – Geometrie ist keine Semantik
Geometrische Lage darf nicht als Ersatz für fachliche Beziehungen verwendet werden.

## KB-OBJECT-005 – Trennung von Darstellung und Geometrie
Presentation und Geometry sind eigenständige Modellbereiche.

## KB-OBJECT-006 – Provenienz bleibt erhalten
SVG-ID, XPath und Quellprüfsumme werden am Objekt dokumentiert.

## KB-OBJECT-007 – Repository als Zugriffspunkt
Alle Objektzugriffe erfolgen über das BPMNRepository.

## KB-OBJECT-008 – Transaktionale Änderung
Änderungen am Objektmodell erfolgen transaktional und werden bei Fehlern zurückgerollt.

## KB-OBJECT-009 – Fail Closed
Ungelöste Referenzen oder doppelte Engineering-IDs blockieren die Materialisierung.

## KB-OBJECT-010 – Deterministische Serialisierung
Repository-Ausgaben werden nach Engineering-ID sortiert serialisiert.
