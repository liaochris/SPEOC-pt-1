from pathlib import Path
import csv, json
from source.scrape.wikitree.wikitree import GetProfile

OUTDIR = Path("output/scrape/wikitree")


def Main():
    nodes, edges = GetChildren(
        input_csv=OUTDIR / "candidates.csv",
        fetch_profile=GetProfile,
        nodes_path=OUTDIR / "family_graph_nodes.json",
        edges_path=OUTDIR / "family_graph_edges.json"
    )
    print(f"[DONE] Total nodes: {len(nodes)}, total edges: {len(edges)}")


def ToYear(val):
    s = str(val or "")[:4]
    return int(s) if s.isdigit() else None


def GetChildren(input_csv, fetch_profile, nodes_path=None, edges_path=None):
    nodes = {}
    edges = []

    with open(input_csv, newline='', encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = (row.get("profile_key") or "").strip()
            if not pid:
                continue

            print(f"[INFO] Processing {pid} ({row.get('query_name', 'Unknown')})...")

            p = fetch_profile(profile_key=pid) or {}
            if not p:
                print(f"[WARN] No profile data returned for {pid}")

            p_birth = ToYear(p.get("BirthDate"))
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
    Main()
