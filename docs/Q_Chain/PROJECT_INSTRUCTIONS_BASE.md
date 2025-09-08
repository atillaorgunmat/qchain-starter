# Project Instructions — Base (structure only)

## Node sufficiency (must have)
id · title · type · owner · status · priority · review_cadence · irreversibility ·
scope_in/out · risk_notes · unknowns(≥1) with:
- id(UNK-<NODE>-NN) · text(ends "?") · status(open|blocked|answered|dropped)
- assumptions(≥1) · failure_modes(≥1) · acceptance(one line)
- doc_refs[{ref, status(linked|placeholder), note}] (≥1)
- depends_on([UNK-...], may be empty for root) · informs([] optional; derived if omitted)
- notes (provenance)
Plus optional node_edges {blocks[], informs[]} for coarse gates.

## Linking model
- **Canonical edges** are at the **question level** (`depends_on`).
- The graph in `docs/Q_Chain/QUESTION_GRAPH.yaml` is **derived** by CI.
- Node-level edges are optional and **advisory**.

## Issues & AGENDA
Labels drive agenda: type:*, priority:P0..P3, agenda:{now|next|later}, status:*, q:<ID>. AGENDA.md is labels-driven; missed dates don’t block.
