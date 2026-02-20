import csv
import pandas as pd
from pathlib import Path
from source.lib.ancestry_scraper.worker import ProcessName
from source.lib.ancestry_scraper.config import STATE_COLLECTION_URLS

INDIR_DERIVED = Path("output/derived/pre1790")
OUTDIR_NAMES = Path("output/scrape/ancestry_loan_office_scraper/names_to_lookup")
STATES = list(STATE_COLLECTION_URLS.keys())


def Main():
    GenerateNameFiles()
    ScrapeNames()


def GenerateNameFiles():
    df = pd.read_csv(INDIR_DERIVED / "loan_office_certificates_cleaned.csv")
    OUTDIR_NAMES.mkdir(parents=True, exist_ok=True)
    for state in sorted(df["state"].dropna().unique()):
        sub = df[df["state"] == state]
        to_lookup = (
            sub[["Year", "raw_name"]]
              .sort_values("Year", ascending=True)
              .drop_duplicates(subset=["raw_name"], keep="first")
              .rename(columns={"Year": "year", "raw_name": "name"})
        )
        out_file = OUTDIR_NAMES / f"names_to_lookup_{state.lower()}.csv"
        to_lookup.to_csv(out_file, index=False)
        print(f"Wrote {len(to_lookup)} rows -> {out_file}")


def ScrapeNames():
    for state in STATES:
        lookup_file = OUTDIR_NAMES / f"names_to_lookup_{state.lower()}.csv"
        if not lookup_file.exists():
            print(f"Skipping {state}: no lookup file for {state}")
            continue
        with lookup_file.open(newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                year, name = row[0].strip(), row[1].strip()
                if not name:
                    continue
                print(f"-> {state} * {year} * {name}")
                ProcessName(name, state, event_year=int(year))


if __name__ == "__main__":
    Main()
