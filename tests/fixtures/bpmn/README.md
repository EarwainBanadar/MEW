# BPMN regression fixture

`reference_process.svg` is the minimal end-to-end reference model for Issue #5.

The fixture intentionally contains one linear process:

`startEvent -> task -> endEvent`

`reference_process.golden.json` contains only stable, semantically relevant projections. Runtime timestamps, evaluation IDs, durations, absolute paths, file sizes and source hashes are deliberately excluded from Golden comparison. They are either normalized to fixed values before report generation or verified separately through the release manifest and SHA-256 integrity checks.

Golden files must only be updated after a reviewed, intentional change to the expected model semantics or rule results.
