import csv, json
from typing import Callable, Dict, Any, Tuple, List, Optional
from wikitree import get_profile

def get_children(
    input_csv: str,
    fetch_profile: Callable[[str], Dict[str, Any]],
    nodes_path: Optional[str] = None,
    edges_path: Optional[str] = None
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []

    with open(input_csv, newline='', encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # get profile key from each row in task_1.csv
            pid = (row.get("profile_key") or "").strip()
            if not pid:
                continue

            def to_year(val) -> Optional[int]:
                s = str(val or "")[:4]
                return int(s) if s.isdigit() else None
            
            # checkpoint
            print(f"[INFO] Processing {pid} ({row.get('query_name', 'Unknown')})...")

            # get profile
            p = fetch_profile(profile_key=pid) or {}

            if not p:
                print(f"[WARN] No profile data returned for {pid}")

            p_birth = to_year(p.get("BirthDate")) # isolate birth date
            # add person to nodes dictionary
            parent_id = (p.get("Name") or pid).strip()
            nodes[parent_id] = {
                "person_id": parent_id,
                "name": p.get("RealName") or p.get("PreferredName") or p.get("Name"),
                "birth_year": p_birth,
                "birth_location": (p.get("BirthLocation") or None),
                "sources": ["wikitree"]
            }

            children = p.get("Children") or p.get("children") or p.get("Child") or []
            if isinstance(children, dict):
                children = [
                    ({"Id": k, **v} if isinstance(v, dict) else {"Id": k, "Name": v})
                    for k, v in children.items()
                ]

            for ch in children:
                cid = (ch.get("Name") or str(ch.get("Id") or "")).strip()
                if not cid:
                    continue
                c_birth = str(ch.get("BirthDate") or "")[:4]
                nodes[cid] = {
                    "person_id": cid,
                    "name": ch.get("Name"),
                    "birth_year": int(c_birth) if c_birth.isdigit() else None,
                    "birth_location": (ch.get("BirthLocation") or None),
                    "sources": ["wikitree"]
                }
                edges.append({"parent_id": pid, "child_id": cid, "relationship": "biological", "gen_depth": 1})

            print(f"[INFO]   Found {len(children)} children for {parent_id}")

    if nodes_path:
        with open(nodes_path, "w", encoding="utf-8") as f:
            json.dump(nodes, f, indent=2, ensure_ascii=False)
    if edges_path:
        with open(edges_path, "w", encoding="utf-8") as f:
            json.dump(edges, f, indent=2, ensure_ascii=False)

    return nodes, edges

if __name__ == "__main__":
    nodes, edges = get_children(
        input_csv="results/task_1.csv",
        fetch_profile=get_profile,
        nodes_path="results/nodes_task_2.json",
        edges_path="results/edges_task_2.json"
    )    

    print(f"[DONE] Total nodes: {len(nodes)}, total edges: {len(edges)}")