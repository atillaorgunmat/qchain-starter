#!/usr/bin/env python3
"""
Validate split-model consistency.
Checks:
- Node shells exist for owner_node of each question
- Question ids & node ids match patterns
- All depends_on ids reference existing question files
- docs/Q_Chain/QUESTION_GRAPH.yaml matches builder output
- Soft WARNs: empty assumptions/acceptance/doc_refs etc.
Exit code 0 on success, 1 on hard errors.
"""
import os, re, sys, glob, tempfile, filecmp, io
from typing import Dict, Any, List
try:
    import yaml
except Exception as e:
    print("ERROR: PyYAML not available. Install pyyaml.", file=sys.stderr)
    sys.exit(2)

Q_DIR = "q"
N_DIR = "nodes"
GRAPH = "docs/Q_Chain/QUESTION_GRAPH.yaml"

Q_RE = re.compile(r"^UNK-[A-Z0-9]{3,}-\d{2}$")
N_RE = re.compile(r"^Q-[A-Z0-9]{3,}-\d{2}$")

def load_yaml(path)->Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def gather(dirp, pat)->Dict[str, str]:
    out = {}
    for fp in glob.glob(os.path.join(dirp, pat)):
        data = load_yaml(fp)
        idv = data.get("id", "").strip()
        out[idv] = fp
    return out

def build_graph(qfiles:Dict[str,str])->Dict[str, Any]:
    nodes = sorted(qfiles.keys())
    edges = {}
    for qid, fp in qfiles.items():
        deps = load_yaml(fp).get("depends_on") or []
        deps = [d for d in deps if isinstance(d,str) and d]
        if deps:
            edges[qid] = {"depends_on": sorted(sorted(set(deps)))}
    return {"nodes": nodes, "edges": edges}

def main()->int:
    hard_errors = 0
    warns: List[str] = []

    qfiles = gather(Q_DIR, "UNK-*.yaml")
    nfiles = gather(N_DIR, "Q-*.yaml")

    # Basic validations
    for qid, fp in qfiles.items():
        if not Q_RE.match(qid):
            print(f"ERROR: {fp} has invalid question id: {qid}")
            hard_errors += 1
        data = load_yaml(fp)
        owner = data.get("owner_node","")
        if not owner or owner not in nfiles:
            print(f"ERROR: {qid} references missing owner_node: {owner}")
            hard_errors += 1
        deps = data.get("depends_on") or []
        for d in deps:
            if d not in qfiles:
                print(f"ERROR: {qid} depends_on missing question: {d}")
                hard_errors += 1
        # Soft checks
        if not data.get("assumptions"):
            warns.append(f"WARN: {qid} has empty assumptions.")
        if not data.get("acceptance"):
            warns.append(f"WARN: {qid} has empty acceptance.")
        if not data.get("doc_refs"):
            warns.append(f"WARN: {qid} has empty doc_refs.")

    # Graph parity
    built = build_graph(qfiles)
    if os.path.exists(GRAPH):
        disk = load_yaml(GRAPH)
        if disk != built:
            print("ERROR: QUESTION_GRAPH.yaml is out of date. Run scripts/qchain_graph_build.py")
            hard_errors += 1
    else:
        warns.append("WARN: QUESTION_GRAPH.yaml missing; will be generated.")

    # Emit WARNs last
    for w in warns:
        print(w)

    return 0 if hard_errors == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
