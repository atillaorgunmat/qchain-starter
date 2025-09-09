#!/usr/bin/env bash
set -euo pipefail

# Ensure we're inside a Git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Run this from your repository root."; exit 1
fi

# Require GitHub CLI and auth
if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' not found. Install via 'brew install gh'."; exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run 'gh auth login'."; exit 1
fi

# Helper: create a label if missing (idempotent)
mk() {
  local name="$1"; local color="${2:-#ededed}"; local desc="${3:-}"
  if [[ -n "${DRY_RUN:-}" ]]; then
    echo "DRY_RUN: gh label create \"$name\" -c \"$color\" ${desc:+-d \"$desc\"}"
    return
  fi
  gh label create "$name" -c "$color" ${desc:+-d "$desc"} >/dev/null 2>&1 || true
}

# Base taxonomy
mk "type:node"     "#0366d6" "Node shell"
mk "type:question" "#8a63d2" "Question (UNK-*)"
mk "type:pack"     "#0b7285" "Handoff pack"
mk "type:chore"    "#6a737d" "Chore / infra"

mk "priority:P0" "#b60205" "Critical"
mk "priority:P1" "#d93f0b" "High"
mk "priority:P2" "#fbca04" "Medium"
mk "priority:P3" "#0e8a16" "Low"

mk "agenda:now"   "#0052cc" "Work now"
mk "agenda:next"  "#2188ff" "Up next"
mk "agenda:later" "#c5def5" "Later"

# Project tags
mk "qchain" "#6f42c1" "Question Chain"
mk "rci-v2" "#e99695" "Handoff RCI v2"

# Dynamic scope labels: q:<ID> for all Node/Question IDs
ids=$(
  { grep -rhoE '^id:\s*(Q-[A-Z0-9-]+)' nodes 2>/dev/null;
    grep -rhoE '^id:\s*(UNK-[A-Z0-9-]+)' q 2>/dev/null; } \
  | awk '{print $2}' | sort -u
)
for id in $ids; do
  mk "q:$id" "#ededed" "Scope label for $id"
done

echo "Labels bootstrapped."
