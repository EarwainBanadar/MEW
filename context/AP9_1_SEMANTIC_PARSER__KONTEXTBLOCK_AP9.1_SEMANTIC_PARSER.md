# KONTEXTBLOCK – AP9.1 Semantic Parser

## KB-SEMANTIC-001 – Semantisches Modell als fachliche Wahrheit
Das semantische Objektmodell wird zur führenden fachlichen Repräsentation ausgebaut.

## KB-SEMANTIC-002 – SVG als Import- und Ausgabeformat
SVG ist in AP9.1 eine explizite Importquelle; direkte fachliche Änderungen am XML sind nach Aufbau des Objektmodells nicht zulässig.

## KB-SEMANTIC-003 – Explizite Semantik vor visueller Heuristik
Der Parser übernimmt primär explizite `data-*`-Annotationen. Er erfindet keine BPMN-Semantik allein aus Farbe oder Form.

## KB-SEMANTIC-004 – Identitätstrennung
SVG-ID und Engineering-ID werden getrennt gespeichert.

## KB-SEMANTIC-005 – Stabile Engineering-ID
Jedes semantische Objekt und jeder Flow benötigt eine stabile Engineering-ID.

## KB-SEMANTIC-006 – Referenzintegrität
Source- und Target-Referenzen werden gegen den Objektindex validiert.

## KB-SEMANTIC-007 – Trennung fachlicher und grafischer Eigenschaften
Typ, Name und Beziehungen werden getrennt von Geometrie, Stil und SVG-Primitiven gespeichert.

## KB-SEMANTIC-008 – Verlustarme Provenienz
Quellpfad, XPath, Metadaten, SVG-Primitiven und Prüfsumme bleiben erhalten.

## KB-SEMANTIC-009 – Diagnose statt stiller Korrektur
Unvollständige Annotationen, doppelte IDs und ungelöste Referenzen werden diagnostiziert und nicht stillschweigend verändert.

## KB-SEMANTIC-010 – AP9.1 Scope
AP9.1 extrahiert ein neutrales semantisches Zwischenmodell. Die vollständige BPMN-Domänenstruktur wird in AP9.2 normiert.
