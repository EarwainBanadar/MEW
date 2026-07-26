# AP9.1 – Technischer QA-Bericht

## Ergebnis
- Runtime Discovery: PASS (Python 3.13.5)
- XML Parser: PASS (`lxml`)
- Unit Tests: PASS
- Referenz-Baseline-Lauf: PASS
- JSON-Ausgabe erzeugt: PASS
- SHA-256-Provenienz: PASS
- Diagnoseerzeugung: PASS

## Unit-Test-Ausgabe
```text
...                                                                      [100%]
3 passed in 0.06s


```

## Parser-Lauf
```text
{
  "status": "PASS",
  "output": "/mnt/data/AP9_1_SEMANTIC_PARSER/reports/Template_Management_RC1.12.6_semantic.json",
  "statistics": {
    "semanticElementCount": 201,
    "flowCount": 193,
    "elementTypes": {
      "dataStoreReference": 1,
      "endEvent": 11,
      "exclusiveGateway": 6,
      "intermediateCatchEvent": 33,
      "intermediateThrowEvent": 33,
      "participant": 1,
      "startEvent": 15,
      "task": 101
    },
    "flowTypes": {
      "message": 35,
      "process-interface-in": 33,
      "process-interface-out": 33,
      "sequence": 92
    },
    "diagnostics": {},
    "svgNodeCount": 1255,
    "svgIdCount": 1251
  }
}


```

## Status
**IMPLEMENTED – TECHNICAL QA PASSED – USER QA PENDING**
