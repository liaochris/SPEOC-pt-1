#!/usr/bin/env python3
import requests

def main():
    # 1. Point this at wherever your service is running:
    url = "http://127.0.0.1:5000/reconcile"
    
    # 2. Build a minimal “queries” payload:
    payload = {
      "queries": {
        "q0": {
          "query": "Smith",
          # if your service expects properties, include one or leave empty
          "properties": [
            {"pid": "state", "v": "NY"}
          ]
        }
      }
    }
    
    # 3. POST it and dump the result:
    resp = requests.post(url, json=payload)
    print("HTTP", resp.status_code)
    try:
        print(resp.json())
    except ValueError:
        print("Non-JSON response:", resp.text)

    # 4. (Optional) basic assertion so `pytest` can pick it up:
    assert resp.status_code == 200, "Service didn’t return 200 OK"
    res = resp.json()
    assert "results" in res and "q0" in res["results"], "Unexpected payload shape"

if __name__ == "__main__":
    main()