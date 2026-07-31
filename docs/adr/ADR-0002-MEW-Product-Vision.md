# ADR-0002: MEW Product Vision

- **Status:** Accepted
- **Date:** 2026-07-31

## Context

The repository has evolved beyond a BPMN parser. Its intended role is to provide a reusable execution environment for engineering models used in global MES/MOM and SCADA programs.

## Decision

MEW is developed as a Manufacturing Engineering Workbench. Its primary operational use case is maintenance, validation, consolidation and completion of the multisite template-management BPMN 2.0 model. The architecture shall remain extensible for GMCM, requirement assessment and requirement-specification generation.

## Consequences

- Generic BPMN capabilities remain separated from domain modules.
- Development priorities are driven first by production use of the template-management model.
- New functions should contribute to deterministic engineering, traceability or controlled document generation.
- Features outside the documented product scope require explicit prioritization.
