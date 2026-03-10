from flask import Flask, request, jsonify, Response
import requests, csv, io, json

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5w51Mp_Gicnt35P4feuTkf8ikXwvHGh_c6ada4LUkKxxGTw72lI06rLhJd7iEnu5DtVbNMjGWiI7Y/pub?output=csv"

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


def Main():
    app.run(host='127.0.0.1', port=5000, debug=True)


def LoadRows():
    r = requests.get(CSV_URL)
    r.raise_for_status()
    return list(csv.DictReader(io.StringIO(r.text)))


@app.route('/reconcile', methods=['GET', 'POST'])
def Reconcile():
    if request.method == 'GET' and (not request.args.get('queries')):
        callback = request.args.get('callback')
        meta_json = json.dumps(METADATA)
        if callback:
            body = f'{callback}({meta_json});'
            return Response(body, mimetype='application/javascript')
        else:
            return Response(meta_json, mimetype='application/json')

    queries = None
    if 'queries' in request.form:
        queries = json.loads(request.form['queries'])
    elif 'queries' in request.args:
        queries = json.loads(request.args['queries'])
    else:
        body = request.get_json(silent=True) or {}
        queries = body.get('queries')

    if queries is None:
        return jsonify({"error": "no queries supplied"})

    column = request.args.get('column', 'raw_name')
    rows = LoadRows()
    results = {}
    for key, q in queries.items():
        term = q.get('query', '').lower()
        candidates = []
        for sheet_row_num, row in enumerate(rows, start=2):
            cell = row.get(column, '')
            if term in cell.lower():
                range_ref = f"A{sheet_row_num}:Z{sheet_row_num}"
                candidates.append({
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
    Main()
