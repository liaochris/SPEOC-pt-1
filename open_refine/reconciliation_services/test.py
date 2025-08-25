import requests

# Test case 1: expect matches for “Smith” in “NY”
payload = {
    "queries": {
        "q0": {
            "query": "AARON BOURN||RI"
        }
    }
}
resp = requests.post("http://127.0.0.1:5000/reconcile", json=payload)
print("AARON BOURN||RI →", resp.json())
