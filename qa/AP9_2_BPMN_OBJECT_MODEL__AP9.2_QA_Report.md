# AP9.2 – Technischer QA-Bericht

## Ausführungsstatus

- Objektmodell implementiert: **PASS**
- AP9.1 → AP9.2 Materialisierung: **PASS**
- Referenzauflösung: **PASS**
- deterministische JSON-Ausgabe: **PASS**
- Graphanalyse: **PASS**
- Unit- und Integrationstests: **PASS**
- SVG unverändert: **PASS**

## Testausgabe

```text
[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                                                    [100%][0m
[32m[32m[1m5 passed[0m[32m in 0.15s[0m[0m

Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/generated/interface/models.py", line 30820, in hydrate_crdt_from_proto
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/rpc/remote.py", line 749, in __call__
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.

```

## CLI-Ausgabe

```text
{
  "object_count": 394,
  "flow_count": 193,
  "flow_node_count": 199,
  "repository_errors": [],
  "graph": {
    "node_count": 199,
    "edge_count": 92,
    "roots": [
      "EV_END_IF_001",
      "EV_END_IF_002",
      "EV_END_IF_003",
      "EV_END_IF_004",
      "EV_END_IF_005",
      "EV_END_IF_006_P100_P300",
      "EV_END_IF_007_P100_P300",
      "EV_END_IF_008_P300_P100",
      "EV_END_IF_009",
      "EV_END_IF_010",
      "EV_END_IF_011_P200_P100",
      "EV_END_IF_012_P100_P400",
      "EV_END_IF_013_P400_P500",
      "EV_END_IF_014_P500_P600",
      "EV_END_IF_015",
      "EV_END_IF_016",
      "EV_END_IF_017",
      "EV_END_IF_018",
      "EV_END_IF_019",
      "EV_END_IF_020",
      "EV_END_IF_021",
      "EV_END_IF_022",
      "EV_END_IF_023",
      "EV_END_IF_024",
      "EV_END_IF_025",
      "EV_END_IF_026",
      "EV_END_IF_027",
      "EV_END_IF_028",
      "EV_END_IF_029",
      "EV_END_IF_030",
      "EV_END_IF_031",
      "EV_END_IF_032",
      "EV_END_IF_033",
      "EV_START",
      "EV_START_A7_T054",
      "EV_START_A7_T065",
      "EV_START_A7_T076",
      "EV_START_A7_T079",
      "EV_START_A7_T082",
      "EV_START_A7_T085",
      "EV_START_A7_T088",
      "EV_START_A7_T091",
      "EV_START_A7_T094",
      "EV_START_A7_T097",
      "EV_START_A7_T100",
      "EV_START_IF_001",
      "EV_START_IF_002",
      "EV_START_IF_003",
      "EV_START_IF_004",
      "EV_START_IF_005",
      "EV_START_IF_006_P100_P300",
      "EV_START_IF_007_P100_P300",
      "EV_START_IF_008_P300_P100",
      "EV_START_IF_009",
      "EV_START_IF_010",
      "EV_START_IF_011_P200_P100",
      "EV_START_IF_012_P100_P400",
      "EV_START_IF_013_P400_P500",
      "EV_START_IF_014_P500_P600",
      "EV_START_IF_015",
      "EV_START_IF_016",
      "EV_START_IF_017",
      "EV_START_IF_018",
      "EV_START_IF_019",
      "EV_START_IF_020",
      "EV_START_IF_021",
      "EV_START_IF_022",
      "EV_START_IF_023",
      "EV_START_IF_024",
      "EV_START_IF_025",
      "EV_START_IF_026",
      "EV_START_IF_027",
      "EV_START_IF_028",
      "EV_START_IF_029",
      "EV_START_IF_030",
      "EV_START_IF_031",
      "EV_START_IF_032",
      "EV_START_IF_033",
      "EV_START_P100_02",
      "EV_START_P100_03",
      "EV_START_P100_TEMPLATE_DEVELOPMENT",
      "G005",
      "T004",
      "T005",
      "T007",
      "T008",
      "T011",
      "T017",
      "T018",
      "T019",
      "T020",
      "T025",
      "T031",
      "T032",
      "T033",
      "T036",
      "T037",
      "T044",
      "T051",
      "T062",
      "T063",
      "T064",
      "T068",
      "T070",
      "T071",
      "T072",
      "T073",
      "T074",
      "T087",
      "T089",
      "T090"
    ],
    "sinks": [
      "EV_END",
      "EV_END_A7_T036",
      "EV_END_A7_T078",
      "EV_END_A7_T081",
      "EV_END_A7_T084",
      "EV_END_A7_T087",
      "EV_END_A7_T090",
      "EV_END_A7_T093",
      "EV_END_A7_T096",
      "EV_END_A7_T099",
      "EV_END_A7_T101",
      "EV_END_IF_001",
      "EV_END_IF_002",
      "EV_END_IF_003",
      "EV_END_IF_004",
      "EV_END_IF_005",
      "EV_END_IF_006_P100_P300",
      "EV_END_IF_007_P100_P300",
      "EV_END_IF_008_P300_P100",
      "EV_END_IF_009",
      "EV_END_IF_010",
      "EV_END_IF_011_P200_P100",
      "EV_END_IF_012_P100_P400",
      "EV_END_IF_013_P400_P500",
      "EV_END_IF_014_P500_P600",
      "EV_END_IF_015",
      "EV_END_IF_016",
      "EV_END_IF_017",
      "EV_END_IF_018",
      "EV_END_IF_019",
      "EV_END_IF_020",
      "EV_END_IF_021",
      "EV_END_IF_022",
      "EV_END_IF_023",
      "EV_END_IF_024",
      "EV_END_IF_025",
      "EV_END_IF_026",
      "EV_END_IF_027",
      "EV_END_IF_028",
      "EV_END_IF_029",
      "EV_END_IF_030",
      "EV_END_IF_031",
      "EV_END_IF_032",
      "EV_END_IF_033",
      "EV_START_IF_001",
      "EV_START_IF_002",
      "EV_START_IF_003",
      "EV_START_IF_004",
      "EV_START_IF_005",
      "EV_START_IF_006_P100_P300",
      "EV_START_IF_007_P100_P300",
      "EV_START_IF_008_P300_P100",
      "EV_START_IF_009",
      "EV_START_IF_010",
      "EV_START_IF_011_P200_P100",
      "EV_START_IF_012_P100_P400",
      "EV_START_IF_013_P400_P500",
      "EV_START_IF_014_P500_P600",
      "EV_START_IF_015",
      "EV_START_IF_016",
      "EV_START_IF_017",
      "EV_START_IF_018",
      "EV_START_IF_019",
      "EV_START_IF_020",
      "EV_START_IF_021",
      "EV_START_IF_022",
      "EV_START_IF_023",
      "EV_START_IF_024",
      "EV_START_IF_025",
      "EV_START_IF_026",
      "EV_START_IF_027",
      "EV_START_IF_028",
      "EV_START_IF_029",
      "EV_START_IF_030",
      "EV_START_IF_031",
      "EV_START_IF_032",
      "EV_START_IF_033",
      "G004",
      "G006",
      "T004",
      "T006",
      "T007",
      "T010",
      "T016",
      "T017",
      "T018",
      "T019",
      "T024",
      "T026",
      "T031",
      "T032",
      "T043",
      "T050",
      "T051",
      "T053",
      "T061",
      "T062",
      "T063",
      "T067",
      "T069",
      "T070",
      "T071",
      "T072",
      "T073",
      "T075",
      "T086",
      "T088",
      "T089"
    ],
    "unreachable": [],
    "cycles": [
      [
        "T003",
        "G001",
        "T003"
      ],
      [
        "T030",
        "G002",
        "T030"
      ],
      [
        "G003",
        "T034",
        "T035",
        "G003"
      ]
    ]
  }
}

Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/generated/interface/models.py", line 30820, in hydrate_crdt_from_proto
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/rpc/remote.py", line 749, in __call__
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.

```

## Gesamtstatus

**AUSGEFÜHRT – IMPLEMENTIERT – TECHNISCHE QA BESTANDEN – BENUTZER-QA AUSSTEHEND**
