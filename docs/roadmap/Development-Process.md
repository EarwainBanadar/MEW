# Lean Development Process

MEW uses four planning levels only:

1. **Vision** — why the product exists.
2. **Development package** — a fachlich closed outcome.
3. **Batch** — a coherent implementation series within a package.
4. **Pull request** — a reviewable technical change.

## Standard flow

1. Select the next planned package and confirm its acceptance criteria.
2. Execute each batch in sequence.
3. Create one or more focused branches and pull requests per batch.
4. Require successful CI and resolve review findings before merge.
5. Verify the complete package after its final batch.
6. Update the roadmap and milestone status.

## Interruption criteria

Autonomous execution stops only for:

- failing CI that cannot be safely corrected;
- merge conflicts;
- unresolved ambiguity affecting scope or behavior;
- unsafe, destructive or irreversible changes;
- a material architecture decision not covered by existing ADRs.

## Change control

The process itself may evolve through normal change management. New governance elements are added only when a demonstrated need justifies their maintenance cost.
