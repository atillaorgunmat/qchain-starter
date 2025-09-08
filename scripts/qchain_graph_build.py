import yaml, sys, re, pathlib
from collections import defaultdict

root = pathlib.Path(".")
node_files = sorted(root.glob("q/*.yaml"))

NODE_ID_RE = re.compile(r"^Q-[A-Z0-9]{3,}-\d{2}$")
UNK_ID_RE  = re.compile(r"^UNK-[A-Z0-9]{3,}-\d{2}$")

# Gather maps
unk_to_node = {}
depends = []  # (from_unk, to_unk)
for yml in node_files:
    data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
    nid = (data.get("id") or "").strip()
    for u in (data.get("unknowns") or []):
        uid = (u.get("id") or "").strip()
        if UNK_ID_RE.match(uid):
            unk_to_node[uid] = nid

for yml in node_files:
    data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
    for u in (data.get("unknowns") or []):
        uid = (u.get("id") or "").strip()
        for d in (u.get("depends_on") or []):
            if uid and d:
                depends.append((uid, d))

# Build node edges from question edges
node_edges_set = set()
for frm, to in depends:
    n_from = unk_to_node.get(frm)
    n_to   = unk_to_node.get(to)
    if n_from and n_to and n_from != n_to:
        node_edges_set.add((n_from, n_to))

def sort_edges(edges):
    return sorted(edges, key=lambda e: (e["from"], e["to"], e.get("type","")))

question_edges = [{"from": f, "to": t, "type": "depends_on"} for f, t in depends]
node_edges     = [{"from": f, "to": t, "type": "depends_on"} for (f, t) in sorted(node_edges_set)]

out = {
    "spec_version": 1,
    "generated_by": "scripts/qchain_graph_build.py",
    "question_edges": sort_edges(question_edges),
    "node_edges": sort_edges(node_edges),
}

out_path = root / "docs" / "Q_Chain" / "QUESTION_GRAPH.yaml"
old = {}
if out_path.exists():
    try:
        old = yaml.safe_load(out_path.read_text(encoding="utf-8")) or {}
    except Exception:
        pass

# Write deterministically
text = yaml.safe_dump(out, sort_keys=False, allow_unicode=True)
out_path.write_text(text, encoding="utf-8")

# If called with --check, compare and fail if changed
if "--check" in sys.argv:
    old_text = yaml.safe_dump(old, sort_keys=False, allow_unicode=True)
    if old_text != text:
        print("QUESTION_GRAPH.yaml is out of date. Run: python scripts/qchain_graph_build.py")
        sys.exit(2)
print("GRAPH OK")
