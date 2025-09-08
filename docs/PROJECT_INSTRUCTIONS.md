# Q‑Chain Two‑Model — Project Instructions (context‑agnostic)

## Triggers & cues (exact words)
- AUTO:BUILD‑FRAMEWORK → Intake + Question Chain Draft (atomic unknown IDs + blocks|informs edges), Now/Next/Later, two process‑only Handoff Manifests, Repo‑Change Inventory (RCI), Idempotent Change Preview (chain artifacts only: node YAML unknowns + QUESTION_GRAPH). **No PRs.**
- REVISE RCI: <notes> → Revise the plan.
- APPLY RCI → Open add‑only PR(s) and write a Handoff Pack under `artefacts/handoff/<pack_id>/`.
- APPLY PRO <pack_id> → Apply PRO’s diffs/issues/agenda/notes; update graph if IDs changed.
- MERGE #<pr> / RECORD PROGRESS #<pr> → Close the turn.

## Mapping heuristic (context‑agnostic)
Route unknowns by function: POL rules/authority; REV offers; BD prospects/pitches; PLAT channels; WF steps/roles; RSCH validation; AN metrics; OPS automation.

## Cross‑node invariants (context‑agnostic)
POL → blocks → BD; REV → blocks → BD; PLAT → informs → WF; RSCH → informs → REV; WF → informs → BD; AN → informs → REV|WF.

## Upload discipline (PRO)
PRO consumes only files listed in `upload_exactly`. If PRO used extra context, it must WARN “framework relation missing; please update” and suggest exactly what to add to nodes/graph.

## IDs & provenance
Unknown IDs: UNK‑<NODE>‑NN (zero‑padded). Write a one‑line provenance note (source + date) into each affected node’s `notes[]`.
