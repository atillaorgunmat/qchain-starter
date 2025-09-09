# Project Profile Overlay (content‑agnostic)

language_policy: { internal: EN, external: TR+EN mirror (if relevant) }

lanes:
  gate_first: []
  revenue_lane: []
  supports: []

cadence:
  agenda_refresh: "each working session"
  meeting_notes: "append-only per session"

policy:
  pr_branch: "one concern per branch; Conventional Commits; squash"
  issues_labels: ["type:","priority:P0..P3","agenda:{now|next|later}","q:<ID>"]

branch_policy:
  default_base: main
  merge: squash
  auto_delete_head: true
  one_concern_per_branch: true

labels_required:
  - type:node
  - type:question
  - agenda:now
  - agenda:next
  - agenda:later
  - priority:P0
  - priority:P1
  - priority:P2
  - priority:P3

artefact_rules:
  packages: "Upload‑Exactly zips are not committed; keep under dist/ (gitignored)"
  graph: "docs/Q_Chain/QUESTION_GRAPH.yaml is derived by script from q/*.yaml; never edit by hand"

packaging:
  upload_exactly_zip: true
  manifest_lock: true
  pack_id_txt: true
  pin_to_commit: true
