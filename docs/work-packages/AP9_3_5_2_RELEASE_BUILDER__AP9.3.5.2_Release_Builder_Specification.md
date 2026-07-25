# AP9.3.5.2 – Release Builder und Manifest Generator

## Zweck

Der Release Builder erzeugt aus einer explizit inventarisierten Artefaktmenge ein deterministisches, prüfbares Release. Jedes Artefakt wird über logischen Pfad, Größe, Medientyp und SHA-256 identifiziert.

## Funktionen

- deklarative Include- und Required-Listen
- deterministische Sortierung
- SHA-256-Inventarisierung
- atomarer Staging-Build
- maschinenlesbares Release-Manifest
- reproduzierbares ZIP mit normierten Zeitstempeln
- Integritätsprüfung eines gebauten Releases
- Manipulationserkennung
- CLI, JSON-Schema und Tests

## Release-Gate

Ein Release wird nur erzeugt, wenn alle Pflichtartefakte vorhanden sind und sich zwischen Inventarisierung und Build nicht geändert haben.
