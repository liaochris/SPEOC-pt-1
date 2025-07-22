from flask import Flask, request, jsonify, Response
import requests, csv, io, json

app = Flask(__name__)

# ─── CONSTANTS 

#Name of reconciliation service
NAME = "final data CD"

# The “publish to web” CSV ID (the long token after /e/…/pub?output=csv)
PUBLISHED_CSV_ID    = "2PACX-1vT2OeiJxqYKunUQhZE07fzn1ThDaj-R0jdi4NZZN7QNOV7Ssj3KDrYxwCiYW93FPwzjU7Yfk8WUuGGg"

# The spreadsheet’s “edit” ID (the one after /d/…/edit)
SPREADSHEET_ID      = "1QmLNxHkKi_-nQc1V4xSAKGDpuUYvoA4EuPZj3Q_5Qq8"

# The specific sheet’s gid (found in the URL as &gid=…)
SHEET_GID           = "711348286"

# Buildable URLs
CSV_URL             = f"https://docs.google.com/spreadsheets/d/e/{PUBLISHED_CSV_ID}/pub?output=csv"
VIEW_URL_TEMPLATE   = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    f"/edit#gid={SHEET_GID}&range={{{{id}}}}"
)

# ─── METADATA ──────────────────────────────────────────────────────────────

METADATA = {
    "versions":       ["0.1"],
    "name":            NAME,
    "identifierSpace": "http://example.org/post1790#",
    "schemaSpace":     "http://example.org/schema#",
    "view": {
        "url":    VIEW_URL_TEMPLATE,   # leaves literal "{{id}}" for OpenRefine to replace
        "width":  600,
        "height": 400
    },
    "defaultTypes":   []
}

# ─── CSV LOADER ─────────────────────────────────────────────────────────────

def load_rows():
    r = requests.get(CSV_URL)
    r.raise_for_status()
    return list(csv.DictReader(io.StringIO(r.text)))

# ─── RECONCILE ENDPOINT ────────────────────────────────────────────────────

@app.route('/reconcile', methods=['GET','POST'])
def reconcile():
    # 1) Bare GET → return metadata
    if request.method == 'GET' and not request.args.get('queries'):
        
        meta_json = json.dumps(METADATA)
        callback  = request.args.get('callback')
        if callback:
            return Response(f'{callback}({meta_json});',
                                mimetype='application/javascript')
        else:
            return Response(meta_json, mimetype='application/json')        

    # 2) Parse queries (form-encoded, GET param, or raw JSON)
    qs = None
    if 'queries' in request.form:
        qs = json.loads(request.form['queries'])
    elif 'queries' in request.args:
        qs = json.loads(request.args['queries'])
    else:
        body = request.get_json(silent=True) or {}
        qs   = body.get('queries')

    if not qs:
        return jsonify({"error": "no queries supplied"})

    column = request.args.get('column', 'raw_name')
    rows   = load_rows()
    results = {}

    for key, q in qs.items():
        term = q.get('query', '').lower()
        comp = q.get('query','').split("||")
        term = comp[0].lower()

        state_prop = comp[1].lower() if len(comp)>1 else ""

        candidates = []
        for row_num, row in enumerate(rows, start=2):
            cell = row.get(column, '')
            row_state = row.get('state', '').lower()

            if term in cell.lower() and state_prop == row_state:
                range_ref = f"A{row_num}:Z{row_num}"
                candidates.append({
                    "id":    range_ref,
                    "name":  cell,
                    "score": 100,
                    "match": True,
                    "view": {
                        # replace the literal "{{id}}" in the template
                        "url":   VIEW_URL_TEMPLATE.replace("{{id}}", range_ref),
                        "label": "View in Sheet"
                    }
                })
        results[key] = {"result": candidates}

    return jsonify(results)

if __name__ == '__main__':
    print("🔄  Starting Reconcile Service on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
