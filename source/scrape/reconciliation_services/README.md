### OpenRefine Reconciliation Services

Flask-based reconciliation services for OpenRefine. Each service matches names from OpenRefine against the post-1790 CD dataset published via Google Sheets.

### Code

- `reconcile_service.py` — Matches on `raw_name` column using substring search. Runs on port 5000.
- `reconcile_last_name.py` — Matches on `last_name_state` column using exact equality.
- `reconcile_loan_office_final_data_CD.py` — Matches on `raw_name_state` column using exact equality.
- `test.py` — Manual smoke test that POSTs a sample query to the running service.

### Input

Data fetched live from Google Sheets on every request (no local input files).

### Output

Returns JSON responses to OpenRefine — no persistent output files.

### Usage

```bash
python reconcile_service.py
```

Then add `http://127.0.0.1:5000/reconcile` as a reconciliation service in OpenRefine.

### Notes

Services fetch data from Google Sheets on every request. This is a revisitable design choice (noted for future cleanup).
