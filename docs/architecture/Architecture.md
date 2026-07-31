# MEW Target Architecture

## Architectural intent

MEW separates generic BPMN processing from domain-specific engineering rules and document generation.

## Logical layers

1. **Input and persistence** — BPMN/XML, configuration and generated artifacts.
2. **Semantic engine** — normalized object model, references, scopes and graphs.
3. **Quality and consolidation services** — validation, diagnostics, comparison, merge and repair proposals.
4. **Domain modules** — template management, GMCM, requirement assessment and related methods.
5. **Traceability and requirements** — links between process elements, roles, systems, requirements and evidence.
6. **Output services** — corrected BPMN, reports and requirement specifications.

## Core principles

- Standards-based BPMN 2.0 processing.
- Deterministic and reproducible transformations.
- Explicit diagnostics instead of silent repair.
- Generic core with independently extensible domain modules.
- Backward-compatible evolution where practical.
- GitHub as the persistent source of truth.

## Current boundary

The current implementation is a technical foundation, not yet the complete workbench. The roadmap defines the controlled transition from the existing parser and semantic services to production-ready model maintenance and consolidation.
