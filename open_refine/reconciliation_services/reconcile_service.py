from flask import Flask, request, jsonify, Response
import requests, csv, io
import json, requests, csv, io

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5w51Mp_Gicnt35P4feuTkf8ikXwvHGh_c6ada4LUkKxxGTw72lI06rLhJd7iEnu5DtVbNMjGWiI7Y/pub?output=csv"



def load_rows():
    r = requests.get(CSV_URL) # try to fetch csv file from url
    r.raise_for_status() # raise any errors from fetching
    data = csv.DictReader(io.StringIO(r.text)) # convert each row into a dictionary
    return list(data) # return a list of dictionary rows

METADATA = {
    "name": "Post-1790 Sheet",
    "identifierSpace": "http://example.org/post1790#",
    "schemaSpace":     "http://example.org/schema#",
    "view": {
        "url":    "https://docs.google.com/spreadsheets/d/1KDLIV97UhLZV2HeFFqJHUZhK8GXrIqOmWRGGvUlhOQo"
               "/edit#gid=526825054&range={{id}}",
        "width":  600,
        "height": 400
    }
}


"""
# OpenRefine will call metadata service to retrieve name of reconciliation service
@app.route('/service-metadata', methods=['GET'])
def service_metadata():
    return jsonify({
        "name": "My Local Reconcile Service",
        "versions": ["0.1"],
        "identifierSpace": "http://127.0.0.1:5000/view/",
        "view": {
            "url": "http://127.0.0.1:5000/view/{{id}}",
            "altLabel": "View record"
        }
    })
"""

@app.route('/reconcile', methods=['GET','POST'])
def reconcile():
    # If this is a bare GET → return metadata
    if request.method == 'GET' and (not request.args.get('queries')):
        callback = request.args.get('callback')      # e.g. "jQuery123..."
        meta_json = json.dumps(METADATA)

        if callback:  # OpenRefine asked for JSON-P
            # Wrap:  callback(<metadata>);
            body = f'{callback}({meta_json});'
            return Response(body, mimetype='application/javascript')
        else:         # Plain JSON
            return Response(meta_json, mimetype='application/json')
        
    
    # 2) Extract queries no matter how they arrive
    queries = None

    # a. POST  -- form-urlencoded
    if 'queries' in request.form:
        queries = json.loads(request.form['queries'])

    # b. GET  ?queries=…
    elif 'queries' in request.args:
        queries = json.loads(request.args['queries'])

    # c. POST  raw JSON body  (only when “Always POST as JSON” is ticked)
    else:
        body = request.get_json(silent=True) or {}
        queries = body.get('queries')

    """
    # a. GET ?queries=… (URL-encoded JSON)
    if 'queries' in request.args:
        queries = json.loads(request.args['queries'])

    # b. POST body {"queries": …}
    if queries is None:
        body = request.get_json(force=True, silent=True) or {}
        queries = body.get('queries')
    """

    if queries is None:
        return jsonify({"error": "no queries supplied"})  # defensive guard


    # Pull the raw JSON payload (OpenRefine always sends a JSON body)
    #body = request.get_json(force=True, silent=True) or {}
    #queries = body.get('queries', {})

    # Pull an optional ?column=raw_name from the URL; default to "raw_name"
    column = request.args.get('column', 'raw_name')

    rows = load_rows()

    results = {}
    for key, q in queries.items(): # iterate over each query OpenRefine sent
        term = q.get('query', '').lower() # query is the value that's sent from OpenRefine (i.e. pre-1790) to search against; default to '' 
        candidates = [] # collects matching rows between both datasets
        
        # Enumerate gives us (index, row), starting at 2 so that the first data row → spreadsheet row 2
        for sheet_row_num, row in enumerate(rows, start=2): # iterate over each row
            cell = row.get(column, '') # grab cell value from post-1790 raw_name column
            if term in cell.lower(): # compare query with every row
                range_ref = f"A{sheet_row_num}:Z{sheet_row_num}"   # highlight full row
                candidates.append({ # if there is a match, create a candidate object 
                    "id":   range_ref,
                    "name": cell,
                    "score": 100,
                    "match": True,
                    "view": {
                        "url":   f"https://docs.google.com/spreadsheets/d/1KDLIV97UhLZV2HeFFqJHUZhK8GXrIqOmWRGGvUlhOQo/edit#gid=526825054&range=A{sheet_row_num}",
                        "label": "View in Sheet"
                    }
                })
        results[key] = {"result": candidates}
    return jsonify(results)

if __name__ == '__main__':
    # Optional sanity print so you know it got this far
    print("🔄  Starting Reconcile Service on http://127.0.0.1:5000")
    # Listen on localhost port 5000, with auto-reload in debug mode
    app.run(host='127.0.0.1', port=5000, debug=True)


