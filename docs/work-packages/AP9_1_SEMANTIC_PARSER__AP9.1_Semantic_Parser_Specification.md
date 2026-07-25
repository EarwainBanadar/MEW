# AP9.1 – SVG Semantic Parser

## Zweck
Der Parser überführt das freigegebene, semantisch annotierte BPMN-SVG in eine deterministische, maschinenlesbare Zwischenrepräsentation. Diese Repräsentation ist die Eingangsgrundlage für AP9.2 und spätere Rule-, Layout-, QA- und Release-Engines.

## Unterstützte Semantik
- `data-bpmn-type` für BPMN-Knoten
- `data-element-id` als Engineering-ID
- `data-flow-type`, `data-source-ref`, `data-target-ref` für Beziehungen
- alle weiteren `data-*`-Attribute als Provenienz-/Engineering-Metadaten
- Text, elementare Geometrie, Styles, SVG-Primitiven und XPath

## Bewusste Grenzen
- Keine spekulative Ableitung eines BPMN-Typs nur aus der Darstellung.
- Keine fachliche Modelländerung.
- Keine vollständige Bézier-Bounding-Box oder Transformationsmatrix; dies wird in AP10 präzisiert.
- Keine vollständige BPMN-2.0-XML-Serialisierung; dies folgt nach AP9.2.

## CLI
```bash
PYTHONPATH=src python -m mew_semantic.cli input.svg -o semantic.json --pretty
```

## Diagnosen
- `SEM-ID-001`: doppelte SVG-ID
- `SEM-ID-002`: doppelte Engineering-ID
- `SEM-ELEM-001`: semantisches Element ohne ID
- `SEM-FLOW-001`: Flow ohne ID
- `SEM-FLOW-002`: Flow ohne Source/Target
- `SEM-REF-001`: ungelöste Source-Referenz
- `SEM-REF-002`: ungelöste Target-Referenz

## Abnahmekriterien
1. XML wird ohne Recovery-Modus gelesen.
2. Explizit annotierte Elemente und Flows werden vollständig extrahiert.
3. IDs und Referenzen werden geprüft.
4. Quellprovenienz bleibt erhalten.
5. Ausgabe ist deterministisch und JSON-serialisierbar.
6. Der Referenz-Baseline-Lauf ist reproduzierbar.
