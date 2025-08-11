import pandas as pd  # CHANGE: use pandas for grouping/dedup
import csv
import os
from wikitree import search_candidates_for_name

STATE_NAMES = {
    "DE": "Delaware",
    "PA": "Pennsylvania",
    "NY": "New York",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "VA": "Virginia",
    "CT": "Connecticut",
}

def task1_write_candidates(names_csv: str, out_csv: str, max_candidates: int = 10):
    """
    For each unique (raw_name, state), collect all WikiTree candidates whose
    birth year exists and falls within [Year-90, Year-20]. Writes to out_csv.
    Expects columns: raw_name, state, Year
    """
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

    # --- LOAD + BUILD KEY ---
    df = pd.read_csv(names_csv)  # read names_to_lookup_{state}.csv as a DataFrame
    # Normalize whitespace/case (optional but helps dedup)
    df["raw_name"] = df["raw_name"].astype(str).str.strip()
    df["state"]    = df["state"].astype(str).str.strip()

    # --- DEDUPE BY KEY ---
    # Keep the first occurrence per key (you could also choose min/median Year etc.)
    unique_df = (
        df.dropna(subset=["raw_name", "state"])
          .drop_duplicates(subset=["raw_name_state"])
    )

    # --- WRITE OUTPUT ---
    fieldnames = [
        "query_name", "state", "range_lo", "range_hi",
        "profile_key", "birth_year", "birth_place", "url"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(f_out, fieldnames=fieldnames)
        w.writeheader()

        # Iterate unique rows
        for row in unique_df.itertuples(index=False):
            name  = getattr(row, "raw_name")
            state = getattr(row, "state")

            # Collect ALL candidates (no ranking) with middle names handled upstream
            cands = search_candidates_for_name(
                name=name,
                state=STATE_NAMES[state],
                max_candidates=max_candidates,
            )

            # add row to 'out_csv'
            for c in cands:
                w.writerow(c)

if __name__ == "__main__":
    task1_write_candidates(
        names_csv="data/loan_office_certificates_cleaned.csv",
        out_csv="results/task_1.csv"
    )