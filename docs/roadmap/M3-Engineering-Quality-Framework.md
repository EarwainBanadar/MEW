# M3 – Engineering Quality Framework

Status: **Verified**

## Objective

Provide reproducible, deterministic, and configurable engineering-quality assessment for semantic BPMN models.

## Completed batches

### Batch 3.1 – Quality model

- stable severity taxonomy
- immutable findings and profiles
- deterministic quality results
- transparent scoring and severity counts

### Batch 3.2 – Engineering validators

- unresolved-reference validation
- missing-name validation
- orphan-element validation
- cross-scope-flow validation
- rule disabling and severity overrides through profiles

### Batch 3.3 – Reports and quality gates

- serializable quality reports
- configurable fail threshold
- deterministic ordering
- public API contract and regression coverage
- CI verification on supported Python and operating-system matrix

## Acceptance evidence

M3 is complete when all rules, profile behavior, score calculation, reporting, public exports, and quality-gate outcomes are covered by automated tests and the repository CI passes without exceptions.
