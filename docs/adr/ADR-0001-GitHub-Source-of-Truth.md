# ADR-0001: GitHub Is the Source of Truth

- **Status:** Accepted
- **Date:** 2026-07-31

## Context

MEW requires a persistent and reproducible basis for code, documentation, planning and architecture decisions. Chat context and local file copies are not sufficiently reliable as the authoritative project record.

## Decision

The `EarwainBanadar/MEW` GitHub repository is the single source of truth for the MEW product. Relevant code, product documentation, roadmap information and accepted architecture decisions shall be versioned there.

## Consequences

- Work is performed through branches, commits, pull requests and CI.
- Repository content takes precedence over conversational recollection.
- Important project decisions must be persisted before they are treated as established.
- Parallel unmanaged copies should not become competing baselines.
