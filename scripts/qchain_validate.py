import yaml, sys, re, pathlib
from collections import defaultdict, deque

root = pathlib.Path(".")
errors, warns = [], []

NODE_ID_RE = re.compile(r"^Q-[A-Z0-9]{3,}-\d{2}$")
UNK_ID_RE  = re.compile(r"^UNK-[A-Z0-9]{3,}-\d{2}$")

ALLOWED_NODE_STATUS = {"open","deciding","decided","paused"}
ALLOWED_PRIO = {"P0","P1","P2","P3"}
ALLOWED_Q_STATUS = {"open","blocked","answered","dropped"}
ALLOWED_DOC_STATUS = {"linked","placeholder"}

node_files = sorted(root.glob("q/*.yaml"))
if not node_files:
    warns.append("No node files under q/*.yaml yet.")

# First pass: gather question ids
unknown_map = {}  # UNK -> (node_id, file)
nodes_data = {}
for yml in node_files:
    data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
    nodes_data[yml] = data
    nid = (data.get("id") or "").strip()
    if not NODE_ID_RE.match(nid):
        errors.append(f"{yml}: bad node id '{nid}' (want Q-<UPPER+DIGITS>-NN)")
    for field in ["title","type","owner","status","priority","irreversibility"]:
        if field not in data:
            errors.append(f"{yml}: missing field '{field}'")
    if data.get("status") and data["status"] not in ALLOWED_NODE_STATUS:
        errors.append(f"{yml}: invalid node status '{data['status']}'")
    if data.get("priority") and data["priority"] not in ALLOWED_PRIO:
        errors.append(f"{yml}: invalid priority '{data['priority']}' (use P0..P3)")
    unks = data.get("unknowns") or []
    if not isinstance(unks, list):
        errors.append(f"{yml}: 'unknowns' must be a list")
    for u in unks:
        uid = (u.get("id") or "").strip()
        if not UNK_ID_RE.match(uid):
            errors.append(f"{yml}: bad unknown id '{uid}' (want UNK-<UPPER+DIGITS>-NN)")
        if uid in unknown_map:
            errors.append(f"{yml}: duplicate unknown id '{uid}' also in {unknown_map[uid][1]}")
        else:
            unknown_map[uid] = (nid, yml)

# Second pass: deep validation
adj = defaultdict(set)  # question-level depends_on graph
for yml, data in nodes_data.items():
    nid = data.get("id")
    for u in (data.get("unknowns") or []):
        uid = (u.get("id") or "").strip()
        text = (u.get("text") or "").strip()
        if not text.endswith("?"):
            errors.append(f"{yml}: unknown '{uid}' text must end with '?'")
        qstatus = (u.get("status") or "open").strip()
        if qstatus not in ALLOWED_Q_STATUS:
            errors.append(f"{yml}: unknown '{uid}' invalid status '{qstatus}'")
        # assumptions
        asum = u.get("assumptions")
        if not isinstance(asum, list) or len(asum) == 0:
            errors.append(f"{yml}: unknown '{uid}' needs at least 1 assumption")
        # failure modes
        fails = u.get("failure_modes")
        if not isinstance(fails, list) or len(fails) == 0:
            errors.append(f"{yml}: unknown '{uid}' needs at least 1 failure_mode")
        # acceptance
        if not (u.get("acceptance") or "").strip():
            errors.append(f"{yml}: unknown '{uid}' must define acceptance")
        # doc refs
        drefs = u.get("doc_refs")
        if not isinstance(drefs, list) or len(drefs) == 0:
            errors.append(f"{yml}: unknown '{uid}' must include doc_refs[]")
        else:
            for d in drefs:
                ref = (d.get("ref") or "").strip()
                status = (d.get("status") or "").strip()
                if status not in ALLOWED_DOC_STATUS:
                    errors.append(f"{yml}: unknown '{uid}' doc_ref status must be linked|placeholder")
                if status == "linked":
                    if not ref or ref.upper() == "TBD":
                        errors.append(f"{yml}: unknown '{uid}' doc_ref linked must specify a path")
                    else:
                        path = ref.split("#")[0]
                        if not (root / path).exists():
                            errors.append(f"{yml}: unknown '{uid}' doc_ref path not found: {path}")
        # depends_on
        deps = u.get("depends_on")
        if deps is None or not isinstance(deps, list):
            errors.append(f"{yml}: unknown '{uid}' depends_on must be a list (use [] if none)")
            deps = []
        for d in deps:
            if d == uid:
                errors.append(f"{yml}: unknown '{uid}' depends_on itself")
            elif d not in unknown_map:
                errors.append(f"{yml}: unknown '{uid}' depends_on missing id '{d}'")
            else:
                adj[uid].add(d)
        # informs (optional; validate if present)
        infs = u.get("informs", [])
        if infs is not None:
            if not isinstance(infs, list):
                errors.append(f"{yml}: unknown '{uid}' informs must be a list if present")
            else:
                for i in infs:
                    if i == uid:
                        errors.append(f"{yml}: unknown '{uid}' informs itself")
                    elif i not in unknown_map:
                        errors.append(f"{yml}: unknown '{uid}' informs missing id '{i}'")

# Cycle detection (DFS)
WHITE, GRAY, BLACK = 0, 1, 2
color = {u: WHITE for u in unknown_map.keys()}
stack = []
def dfs(u):
    color[u] = GRAY
    stack.append(u)
    for v in adj[u]:
        if color[v] == WHITE:
            if dfs(v): return True
        elif color[v] == GRAY:
            # found a back edge -> cycle
            cyc = stack[stack.index(v):] + [v]
            errors.append("Cycle in question depends_on: " + " -> ".join(cyc))
            return True
    stack.pop()
    color[u] = BLACK
    return False

for u in list(unknown_map.keys()):
    if color[u] == WHITE:
        dfs(u)

if errors:
    print("\n".join(errors))
    sys.exit(1)
if warns:
    print("\n".join("WARN: "+w for w in warns))
print("OK")
