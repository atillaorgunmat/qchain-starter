# Q‑Chain Two‑Model — Project Instructions (content‑agnostic)

**Source of truth:** atillaorgunmat/qchain-starter@main. If this header and the repo differ, the **repo wins**.

---

## Roles (strict split)

- **AUTO (Ops/IO)**  
  Reads repo state, asks clarifying questions, packages **Upload‑Exactly ZIPs** (pinned to a commit), regenerates the derived graph, validates, opens PRs, merges.

docs/conversation-protocol-v1
## IDs & provenance
Unknown IDs: UNK‑<NODE>‑NN (zero‑padded). Write a one‑line provenance note (source + date) into each affected node’s `notes[]`.
---

## Conversation Modes & Response Contracts (normative)

- **MODE: FREE** — open exploration. End with a one‑line **Decision & Next Action**.
- **MODE: FORM** — strict responses using the canonical forms below.
  - **Strict‑form macro:**  
    **STRICT-FORM ONLY — reply with ONE fenced YAML block using the requested top-level key. No prose outside the code fence. Unknowns → `null` with a brief note in `notes:`.**
- **Canonical forms:** see `docs/CONVERSATION_PROTOCOL.md` and `docs/forms/*.schema.yaml`.
- **Handshake pattern:** (1) Ack keys; (2) Payload‑only retry if needed.
- **GUIDANCE role:** may ask ≤3 clarifying questions; otherwise must produce the requested strict form.
- **PRO (Reason/Authoring)**  
  Consumes only the **attached ZIP**; updates/creates **question YAMLs** and lightweight docs; returns an **add‑only Handoff Pack** with an **Idempotent Change Preview** and **issue one‑liners**. PRO never pushes directly to the repo.

---

## Cues / exact trigger words

- `AUTO:BUILD-FRAMEWORK` — (optional) initial scaffold.
- `STATUS SYNC` — brief state report.
- `DISCOVER & PREP PRO PACK — AUTO-LED` — **standard entry point** per cycle.
- `SHOW CHAIN — READABLE VIEW` — tabular/topological view of questions and gaps.
- `REVISE RCI: <notes>` — change the plan pre‑apply.
- `APPLY RCI` — apply AUTO’s repo‑change inventory (add‑only).
- `APPLY PRO <pack_id>` — apply a PRO handoff pack (add‑only).
- `MERGE #<pr>` / `RECORD PROGRESS #<pr>` — close a turn.

---

## Operating cycle (one loop)

1) **AUTO discovery pass (pinned to HEAD)**  
   AUTO inventories the repo: nodes, questions, derived graph, gaps. It asks ≤5 clarifying questions, then proposes **2–3 pack options** and recommends **one**.

2) **AUTO produces Upload‑Exactly**  
   A **commit‑pinned ZIP** named `upload_exactly_<pack_id>_<SHA>.zip` + `MANIFEST.lock` (sha256, size, path) + `pack_id.txt` (commit SHA). Only the listed files. No extras.

3) **PRO authoring**  
   New PRO chat. You attach the ZIP. PRO returns a **Handoff Pack** (add‑only), with:
   - Updated `q/*.yaml` (assumptions, failure_modes, acceptance, doc_refs, depends_on as needed; titles remain interrogative).
   - **Idempotent Change Preview** (full text for new files; minimal diffs for edits).
   - **Issue one‑liners** (labels: `type:*`, `agenda:*`, `priority:*`, `q:<ID>`).
   - A WARN if PRO needed context **beyond** the ZIP, plus an explicit suggestion of which files/sections to include next time.

4) **AUTO apply**  
   AUTO opens `apply-pro/<pack_id>` branch, regenerates the derived graph, validates, commits, opens PR.

5) **Merge**  
   Squash‑merge; auto‑delete head branch. Start the next discovery.

---

## AUTO discovery pass (what AUTO must do)

- **Pin & report** the commit (`commit_sha`).
- **Inventory**
  - **Nodes** (`nodes/*.yaml`): `id`, `title`, `owners`, `agenda`, `priority`, `questions[]`.
  - **Questions** (`q/*.yaml`): `id`, `owner_node`, `status`, `title`, `depends_on[]`, presence of `assumptions`, `failure_modes`, `acceptance`, `doc_refs`.
  - **Graph**: derive `docs/Q_Chain/QUESTION_GRAPH.yaml` from per‑question `depends_on`; compute **reverse deps** (how many depend on each UNK).
  - **Doc refs**: which paths exist vs missing.
- **Analysis**
  - Rank **gating questions** by  
    `Score = 3×Dependents + PriorityWeight + AgendaWeight + MissingFieldCount`,  
    where `PriorityWeight: P0=3,P1=2,P2=1,P3=0`, `AgendaWeight: now=2,next=1,later=0`, `MissingFieldCount: +1 each for empty {assumptions,failure_modes,acceptance,doc_refs}`.
  - Propose **2–3 candidate packs** (e.g., Governance/Workflow; Foundations; Execution; Partnerships; Metrics) with a one‑line rationale each.
- **Ask** ≤5 **yes/no or single‑select** clarifying questions to pick **one** pack.
- **Package** Upload‑Exactly (only the listed files; if a doc specifies `[sections: ...]`, include an **extracted copy** with only those sections).
- **Return**: ZIP, `MANIFEST.lock`, `pack_id.txt`, and the one‑liner to rebuild the ZIP locally with `git archive`.

---

## Upload‑Exactly packaging (rules)

- ZIPs are **not** committed; keep under `dist/` (gitignored).
- `MANIFEST.lock` lines: `sha256<TAB>size_bytes<TAB>path`; final line: `commit_sha<TAB><SHA>`.
- If PRO needs more context, it must **WARN** and propose **exact** additions for the next pack.

---

## Split model (what lives where)

- **Node shells** → `nodes/Q-*.yaml`  
  Minimal ownership/agenda container. Required fields:
  - `id`, `title`, `owners[]`, `agenda`, `priority`, `irreversibility`, `questions[]`, `notes[]` (thin provenance).
- **Questions** → `q/UNK-*.yaml`  
  Self‑describing unit of work. Required fields:
  - `id`, `owner_node`, `title` (interrogative), `status` (`open|answered`),  
    `depends_on[]` (list of UNK IDs),  
    `assumptions[]`, `failure_modes[]`, `acceptance[]`, `doc_refs[]`,  
    `notes[]` (provenance lines OK).
- **Derived graph** → `docs/Q_Chain/QUESTION_GRAPH.yaml`  
  Built **only** by script from `q/*.yaml`. Never hand‑edit.

**ID conventions**
- **Questions:** `^UNK-[A-Z0-9]{3,}-\d{2}$` (use a single tag without internal hyphens; e.g., `UNK-MRKTR-01`).  
- **Nodes:** `^Q-[A-Z0-9-]+$`.

---

## Branch & CI policy

- Base branch: `main` (protected; require CI; squash merges; auto‑delete head).  
- One concern per branch: `feat/*`, `chore/*`, `docs/*`, `apply-pro/<pack_id>`.  
- CI validates: node/question structure, unknown IDs, and graph derivation.

---

## Issues & labels (work tracking)

- **Exactly one** scope label per issue: `q:<ID>`.  
  - Node issue → `type:node` + `q:Q-*`.  
  - Question issue → `type:question` + `q:UNK-*`.
- Agenda drives work: `agenda:now|next|later`.  
- Priority: `priority:P0..P3`.  
- Optional: `qchain`, `rci-*`, `type:chore`.
- One question per issue. PRs reference issues (`Closes #nn`).

---

## Artefacts & handoff packs

- **AUTO** keeps handoff metadata under `artefacts/handoff/<pack_id>/` (e.g., `PR_BODY.md`, `CHECKS.md`).  
- **PRO** returns add‑only file contents in chat (ZIP or code blocks) plus an **Idempotent Change Preview**; AUTO materializes into a branch and PR.  
- Upload‑Exactly ZIPs live locally or in chat; they are not committed.

---

## Security & hygiene

- Do not include secrets or large binaries in ZIPs; prefer paths in `doc_refs`.  
- Keep `.gitignore` covering `dist/` and `*.zip`.
main
