# ADR-0003: Lean Delivery Governance

- **Status:** Accepted
- **Date:** 2026-07-31

## Context

MEW needs enough structure for reproducible autonomous development, but excessive project-control functions would create avoidable administrative work.

## Decision

MEW uses a lean hierarchy of vision, development package, batch and pull request. Milestones summarize product outcomes. Essential architecture decisions are recorded as ADRs; additional governance artifacts are introduced only after a demonstrated need.

A development package is a closed fachlich outcome. Large packages are divided into ordered batches and may use multiple focused pull requests. The package is marked complete only after package-level verification.

## Consequences

- No separate bureaucracy for routine status reporting is required.
- CI and pull-request history provide the technical execution record.
- Roadmap status is updated at meaningful package or milestone transitions.
- The governance model can later be extended through controlled change management.
