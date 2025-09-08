#!/usr/bin/env python3
"""
Build docs/Q_Chain/QUESTION_GRAPH.yaml from split-model question files.

Rules:
- Read all q/UNK-*.yaml
- nodes list contains all UNK-* ids found
- edges map per question: id -> depends_on (deduplicated, sorted)
- Deterministic sort for idempotence
"""
import os, re, sys, glob
from typing import Dict, List, Any
try:
    import yaml
except Exception as e:
    print("ERROR: PyYAML not available. Install pyyaml.", file=sys.stderr)
    sys.exit(2)

Q_DIR = "q"
OUT = "docs/Q_Chain/QUESTION_GRAPH.yaml"

ID_RE = re.compile(r"^UNK-[A-Z0-9]{3,}-\d{2}$")

def load_yaml(path:str)->Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def main()->int:
    files = sorted(glob.glob(os.path.join(Q_DIR, "UNK-*.yaml")))
    if not files:
        print(f"WARNING: no question files under {Q_DIR}/", file=sys.stderr)
    nodes = []
    edges: Dict[str, Dict[str, List[str]]] = {}

    for fp in files:
        data = load_yaml(fp)
        qid = data.get("id", "").strip()
        if not ID_RE.match(qid):
            print(f"WARNING: skipping {fp} due to invalid id: {qid}", file=sys.stderr)
            continue
        nodes.append(qid)
        deps = data.get("depends_on") or []
        # normalize
        deps = [d.strip() for d in deps if isinstance(d, str) and d.strip()]
        deps = sorted(sorted(set(deps)))  # deterministic
        if deps:
            edges[qid] = {"depends_on": deps}

    nodes = sorted(sorted(set(nodes)))

    graph = {"nodes": nodes, "edges": edges}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        yaml.safe_dump(graph, f, sort_keys=False, allow_unicode=True)
    print(f"Wrote {OUT} with {len(nodes)} nodes and {len(edges)} edges.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
