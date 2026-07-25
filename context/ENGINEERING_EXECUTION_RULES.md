# Engineering Execution Rules

## EXEC-RULE-001 – Environment Readiness

Bei jeder Ausführungsanweisung wird vor der Implementierung obligatorisch geprüft,
ob eine lauffähige Ausführungsumgebung vorhanden ist.

## EXEC-RULE-002 – Environment Reconstruction

Ist keine Ausführungsumgebung vorhanden, wird eine neue Umgebung initialisiert.
Danach wird der freigegebene Projektbestand rekonstruiert und auf Integrität geprüft.

## EXEC-RULE-003 – Status Truthfulness

Ein Arbeitspaket erhält den Status `AUSGEFÜHRT` nur, wenn Quellcode erzeugt,
tatsächlich ausgeführt und technisch getestet wurde.

## EXEC-RULE-004 – Persistent Checkpoint

Nach jedem abgeschlossenen Arbeitspaket wird ein vollständiges, prüfsummengesichertes
Projektarchiv erzeugt.
