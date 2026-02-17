import csv
import sys
from pathlib import Path
import argparse
from ancestry_scraper.worker import process_name

def main():
    p = argparse.ArgumentParser(
        description="Lookup names for a given state and run ancestry_scraper"
    )
    p.add_argument(
        "state",
        help="Two‐letter state code (e.g. DE, PA).  This will load names_to_lookup_<state>.csv"
    )
    p.add_argument(
        "--dir",
        default="names_to_lookup",
        help="Directory where your names_to_lookup files live"
    )
    p.add_argument(
        "--event-x",
        type=int,
        default=10,
        help="Optional fuzziness window (default: 10)"
    )
    p.add_argument(
        "--year",
        help="Year you want to search (useful for 1790 census)"
    )
    args = p.parse_args()

    lookup_file = Path(args.dir) / f"names_to_lookup_{args.state.lower()}.csv"
    if not lookup_file.exists():
        print(f"❌  File not found: {lookup_file}", file=sys.stderr)
        sys.exit(1)

    with lookup_file.open(newline="") as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            year, name = row[0].strip(), row[1].strip()
            if not name:
                continue
            print(f"→ {args.state} • {year} • {name}")
            if (args.year is not None):
                year = args.year

            process_name(name, args.state, event_year=int(year), event_x=args.event_x)

if __name__ == "__main__":
    main()
