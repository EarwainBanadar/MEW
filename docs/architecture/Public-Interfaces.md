# Public Interfaces

This document defines the supported public entry points of the MEW core platform for milestone M1.

## Command-line interfaces

The following console commands are part of the supported platform interface:

| Command | Purpose |
|---|---|
| `mew-semantic` | Extract and inspect semantic information from supported source models. |
| `mew-bpmn` | Load and inspect the typed BPMN object model. |
| `mew-rules` | Execute the standard rule framework. |
| `mew-report` | Generate supported report formats. |
| `mew-release` | Build and verify deterministic release artifacts. |
| `mew-quality` | Execute the local quality gate. |

A command is considered stable when its documented arguments, exit-code behavior and produced artifacts are covered by regression tests. Changes that intentionally break this contract require an architecture decision or a major-version transition.

## Python package boundaries

The supported package-level boundaries are:

- `mew_semantic`: semantic extraction and semantic document services;
- `mew_bpmn`: BPMN model types, parsing and repository services;
- `mew_rules`: rule definitions, loading, dispatch and evaluation;
- `mew_reporting`: deterministic report generation;
- `mew_release`: release assembly, manifests and integrity verification;
- `mew_quality`: the repository quality-gate entry point.

Modules and names below these package boundaries are implementation details unless they are explicitly documented or imported by a package-level interface. Internal modules may be refactored without compatibility guarantees provided that the supported command-line and package-level behavior remains unchanged.

## Compatibility baseline

- Supported Python versions: 3.10 through 3.13.
- Supported CI operating systems: Ubuntu and Windows.
- Input and output behavior must be deterministic for identical source data, configuration and tool version.
- Findings and reports must retain stable identifiers where a rule or semantic object has not changed.
- Release artifacts must retain verifiable provenance and integrity metadata.

## Change control

A public-interface change shall be classified as one of the following:

1. compatible extension;
2. compatible correction;
3. deprecation;
4. breaking change.

Breaking changes require an explicit migration note and an appropriate version change. Deprecations must remain documented until removal.

## M1 verification

The M1 core-platform baseline is accepted when:

- the complete CI matrix succeeds;
- the local and CI quality gates are documented;
- the public command and package boundaries are documented;
- no known critical platform defect remains open;
- roadmap status is updated only after verification.
