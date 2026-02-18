from source.scrape.wikitree.build_family_graph import get_children
from source.scrape.wikitree.wikitree import get_profile

def test_children_count():
    # Fake get_profile to avoid API calls
    def fake_get_profile(profile_key):
        if profile_key == "Parent-1":
            return {
                "Name": "Parent-1",
                "Children": [
                    {"Name": "Child-1"},
                    {"Name": "Child-2"}
                ]
            }
        elif profile_key == "Parent-2":
            return {
                "Name": "Parent-2",
                "Children": [
                    {"Name": "Child-3"}
                ]
            }
        return {}

    # Create a fake CSV for testing
    import tempfile, csv
    tmp_csv = tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False)
    writer = csv.DictWriter(tmp_csv, fieldnames=["profile_key"])
    writer.writeheader()
    writer.writerow({"profile_key": "Parent-1"})
    writer.writerow({"profile_key": "Parent-2"})
    tmp_csv.close()

    # Run the function
    from source.scrape.wikitree.build_family_graph import get_children
    nodes, edges = get_children(tmp_csv.name, fetch_profile=fake_get_profile)

    # Count edges per parent
    from collections import Counter
    edge_counts = Counter(e["parent_id"] for e in edges)

    assert edge_counts["Parent-1"] == 2
    assert edge_counts["Parent-2"] == 1