from pathlib import Path
import pandas as pd
import csv
from source.scrape.wikitree.wikitree import SearchCandidatesForName
from source.lib.ancestry_scraper.config import STATE_ABBREVIATIONS

INDIR_DERIVED = Path("output/derived/pre1790")
OUTDIR = Path("output/scrape/wikitree/results")


def Main():
    WriteCandidates(
        names_csv=INDIR_DERIVED / "loan_office_certificates_cleaned.csv",
        out_csv=OUTDIR / "task_1.csv"
    )


def WriteCandidates(names_csv, out_csv, max_candidates=10):
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(names_csv)
    df["raw_name"] = df["raw_name"].astype(str).str.strip()
    df["state"] = df["state"].astype(str).str.strip()

    unique_df = (
        df.dropna(subset=["raw_name", "state"])
          .drop_duplicates(subset=["raw_name_state"])
    )

    fieldnames = [
        "query_name", "state", "range_lo", "range_hi",
        "profile_key", "birth_year", "birth_place", "url"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(f_out, fieldnames=fieldnames)
        w.writeheader()
        for row in unique_df.itertuples(index=False):
            name = getattr(row, "raw_name")
            state = getattr(row, "state")
            cands = SearchCandidatesForName(
                name=name,
                state=STATE_ABBREVIATIONS[state],
                max_candidates=max_candidates,
            )
            for c in cands:
                w.writerow(c)


if __name__ == "__main__":
    Main()
