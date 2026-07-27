# MEW v0.10.0 Stable Public API

This document defines the compatibility boundary for MEW v0.10.0.

## Python packages

Only names listed in a package's `__all__` are public and stable. Direct imports from implementation modules such as `parser`, `builder`, `engine`, `models`, `repository`, or `cli` are internal unless explicitly listed below.

### `mew_semantic`

- `parse_svg`
- `SemanticSvgParser`
- `SemanticDocument`
- `SemanticElement`
- `SemanticFlow`
- `Diagnostic`

Parser failures caused by malformed XML or strict semantic diagnostics are raised as exceptions. `SemanticDocument.to_dict()` is the stable serialization boundary.

### `mew_bpmn`

- `SemanticModelBuilder`
- `BPMNRepository`

`SemanticModelBuilder.build()` accepts a semantic document dictionary and returns a resolved, validated repository. Invalid repositories raise `ValueError`.

### `mew_rules`

The public names are exactly those listed in `mew_rules.__all__`, including rule definitions, findings, contexts, registries, evaluators, policies and documented rule-repository errors.

### `mew_reporting`

- `ReportMetadata`
- `ReportingEngine`
- `ReportingError`

JSON output is UTF-8, newline-terminated and key-sorted. Markdown and HTML output are deterministic for identical normalized inputs and metadata.

### `mew_release`

- `ArtifactRecord`
- `ReleaseBuildResult`
- `ReleaseBuilder`
- `ReleaseDescriptor`
- `ReleaseError`

Release manifests and archives are deterministic for identical source artifacts and descriptors. Integrity verification reports `PASS` or `FAIL` and identifies failing logical paths.

## Command-line contracts

The installed commands are:

| Command | Purpose | Success | Operational failure | Usage error |
|---|---|---:|---:|---:|
| `mew-semantic` | Parse annotated SVG into semantic JSON | 0 | 2 | argparse default 2 |
| `mew-bpmn` | Build and inspect the BPMN repository | 0 | 2 | argparse default 2 |
| `mew-rules` | Evaluate the standard rule set | 0 | 2 | argparse default 2 |
| `mew-report` | Render JSON, Markdown and HTML reports | 0 | 2 | argparse default 2 |
| `mew-release` | Build or verify a release package | 0 | 2 | argparse default 2 |

Each command supports `--help`, writes primary output to the declared output path, and emits machine-readable status information where implemented. Error details go to standard error. Existing argument names and exit-code meanings are stable throughout the v0.10.x line.

## Compatibility policy

- Patch releases may fix defects without changing documented signatures, serialized field meanings, CLI argument names or exit-code meanings.
- Minor releases may add optional arguments, fields or public names, but must preserve existing behavior.
- Removing or renaming a public name, required field, command, argument or status meaning is a breaking change and requires a new major version.
- A planned removal must first be documented and emit `DeprecationWarning` for at least one minor release.
- Internal modules and names absent from `__all__` may change without deprecation.
- Golden files, API smoke tests and the cross-platform CI matrix are the executable contract for these rules.
