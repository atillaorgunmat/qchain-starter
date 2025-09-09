# Conversation Protocol — Q‑Chain (Modes, Macros, Schemas)

**Repo source of truth:** atillaorgunmat/qchain-starter@main

This file defines conversation modes and strict form schemas used by GUIDANCE, AUTO, and PRO.

## Modes

- **MODE: FREE** — open exploration (brainstorming, critique).  
  **Discipline:** end with a one‑line **Decision & Next Action**.

- **MODE: FORM** — structured, machine‑checkable responses.  
  **Discipline:** reply with **one** fenced YAML block using the requested top‑level key.

### Strict‑form macro (verbatim)

> **STRICT-FORM ONLY — reply with ONE fenced YAML block using the requested top‑level key. No prose outside the code fence. Unknowns → `null` with a brief note in `notes:`.**

### Handshake pattern (recommended for critical turns)

1. **Ack step:** echo the keys you will output under `ack.keys`, then include the strict form.  
2. **Payload‑only step:** if ack is correct but payload is off‑schema, retry with “PAYLOAD ONLY” (no ack, just the form).

## Canonical Form Schemas (v1)
> The same schemas are versioned under `docs/forms/*.schema.yaml`. Keep keys stable; extend with optional fields if needed.

### 1) AUTO → GUIDANCE (`auto_response`)

```yaml
auto_response:
  repo: "atillaorgunmat/qchain-starter"
  commit_sha: null
  pr_status: { open: [], merged: [] }
  ci_checks: []                # [{pr, head_branch, conclusion}]
  inventory:
    nodes: []                  # [{id,title,owners,agenda,priority,questions:[]}]
    questions: []              # [{id,owner_node,status,title,depends_on:[],missing_fields:[]}]
  graph:
    reverse_deps: []           # [{id, dependents}]
  packs: []                    # [{id,name,rationale,includes:[]}]
  clarifying_questions: []
  upload_exactly:
    pack_id: null
    zip_name: null
    manifest_lock: null        # paste MANIFEST.lock content
    rebuild_one_liner: null
  notes: []
  errors: []
```

### 2) PRO → GUIDANCE (`pro_handoff`)

```yaml
pro_handoff:
  pack_id: null
  change_preview:
    summary: null
    new_files: []              # paths
    edited_files: []           # paths
    derived_graph_note: "derived-only"  # or "no-change"
  updated_questions: []        # [{id, fields_filled:[], minor_edits:[]}]
  issues_one_liners: []        # strings ready for gh CLI
  warnings: []                 # if PRO needed context beyond the ZIP
  notes: []
  errors: []
```

### 3) GUIDANCE → PRO (`pro_request`)

```yaml
pro_request:
  pack_id: null
  zip_name: null
  acceptance:
    - "Update only q/*.yaml in the ZIP: fill assumptions, failure_modes, acceptance, doc_refs."
    - "Keep interrogative titles; adjust depends_on only if clearly missing."
    - "Return add-only Idempotent Change Preview + gh issue one-liners (type:question, agenda:*, priority:*, q:<ID>)."
    - "Use only the ZIP; if more context is needed, WARN and list exact files/sections for next cycle."
  constraints:
    - "No destructive edits."
    - "QUESTION_GRAPH.yaml is derived by script; do not hand-edit."
  notes: []
```

### 4) GUIDANCE → AUTO (`auto_apply`)

```yaml
auto_apply:
  pack_id: null
  branch: null                 # e.g., apply-pro/2025-09-09-FOUNDATIONS
  steps:
    - "Regenerate graph from q/*.yaml"
    - "Run validator (fail on structure/id/graph parity)"
    - "Commit add-only changes"
    - "Open PR with PR_BODY.md + CHECKS.md"
  pr_title: null
  pr_body_summary: null
  labels: ["type:chore","qchain"]
  notes: []
```

## Triggers (action keywords)

AUTO: `STATUS SYNC`, `DISCOVER & PREP PRO PACK — AUTO-LED`, `APPLY RCI`, `APPLY PRO <pack_id>`, `MERGE #<pr>`, `RECORD PROGRESS #<pr>`.  
PRO: `APPLY RCI` (ZIP‑driven).  
GUIDANCE: PASTE forms only; outputs `pro_request` or `auto_apply`.
