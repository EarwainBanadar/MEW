# KONTEXTBLOCK – AP9.3.1 Rule Framework

## KB-RULE-FRAMEWORK-001
Jede ausführbare Regel besitzt eine eindeutige Rule-ID und eine explizite Version.

## KB-RULE-FRAMEWORK-002
Regelmetadaten sind von der ausführbaren Implementierung getrennt.

## KB-RULE-FRAMEWORK-003
Jede Regel liefert ausschließlich strukturierte Findings.

## KB-RULE-FRAMEWORK-004
Ausnahmen innerhalb einer Regel werden als RuleStatus.ERROR gekapselt.

## KB-RULE-FRAMEWORK-005
Das Rule Registry weist doppelte Rule-IDs zurück.

## KB-RULE-FRAMEWORK-006
Die Registry-Reihenfolge ist deterministisch nach Rule-ID.

## KB-RULE-FRAMEWORK-007
Schweregrad, Kategorie und Scope sind typisiert.

## KB-RULE-FRAMEWORK-008
Eine Regel darf keine direkte Änderung am BPMNRepository durchführen.

## KB-RULE-FRAMEWORK-009
Alle Resultate enthalten Ausführungsdauer und Zeitstempel.

## KB-RULE-FRAMEWORK-010
Neue Regeln müssen mindestens einen automatisierten Test besitzen.
