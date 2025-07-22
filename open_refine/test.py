import requests

# Test case 1: expect matches for “Smith” in “NY”
payload = {
    "queries": {
        "q0": {
            "query": "JOHN SMITH||PA"
        }
    }
}
resp = requests.post("http://127.0.0.1:5000/reconcile", json=payload)
print("ABEL SAWYER||NH →", resp.json())