import re
import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import unittest
import matplotlib.colors as mcolors

# map two-letter → full state name for your shapefile
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

def extract_county(loc: str, state_code: str) -> str:
    """Extract county from a location string based on simple comma rules."""
    if not isinstance(loc, str) or not loc.strip():
        return ""
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    state_name = STATE_NAMES.get(state_code.upper(), "").upper()

    # Case 1: two commas → take middle part (index 1)
    if len(parts) == 3:
        county = parts[1]

    # Case 2: one comma
    elif len(parts) == 2:
        if state_name and parts[1].upper().startswith(state_name):
            county = parts[0]  # before comma if second part is state
        else:
            county = parts[1]  # after comma otherwise

    # Case 3: no comma → take as-is
    elif len(parts) == 1:
        county = parts[0]
    else:
        return ""  # unexpected format

    # Remove the word "county" if present
    county = county.upper().replace("COUNTY", "").strip()

    # Remove possessive "'s" (e.g., QUEEN ANNE'S → QUEEN ANNE)
    county = county.replace("'s", "s").replace("'S", "S").strip()

    return county

def summarize_results(state_code: str, cert_year: int, results_dir: str = "results"):
    state_code = state_code.upper()
    csv_path = f"{results_dir}/results_{state_code.lower()}.csv"
    df = pd.read_csv(csv_path)

    df["county"] = df["county"].apply(lambda x: extract_county(x, state_code))

    total = df["name"].nunique()
    has_county = df["county"].notna() & df["county"].str.strip().ne("")
    matched = has_county.sum()
    pct = matched / total * 100 if total else 0

    print(f"{state_code} – {total} names, {matched} with counties ({pct:.1f}%)")

    county_counts = (
        df[has_county]
          .groupby("county")
          .size()
          .reset_index(name="count")
          .assign(county=lambda d: d["county"].str.upper())
          .sort_values("count", ascending=False)
    )
    print("\nPer-county counts:")
    print(county_counts.to_string(index=False))
    return county_counts

def plot_choropleth(
    state_code: str,
    county_counts: pd.DataFrame,
    cert_year: int,
    shapefile_path: str,
    map_out_dir: str = "maps",
    earliest_year: int | None = None,
    latest_year: int | None = None
):
    state_code = state_code.upper()
    state_name = STATE_NAMES[state_code]

    gdf = gpd.read_file(shapefile_path)
    gdf["START_YEAR"] = gdf["START_DATE"].str.split("/").str[0].astype(int)
    gdf["END_YEAR"]   = gdf["END_DATE"].str.split("/").str[0].astype(int)

    sel = (
        (gdf["STATE_TERR"] == state_name)
        & (gdf["START_YEAR"] <= cert_year)
        & ((gdf["END_YEAR"] >= cert_year) | (gdf["END_YEAR"] == 9999))
    )
    sub = gdf[sel]

    # dissolve by NAME before merging
    sub["NAME"] = sub["NAME"].astype(str).str.upper().str.strip()     # CHANGE
    sub = sub.dissolve(by="NAME", as_index=False)     

    merged = sub.merge(
        county_counts, left_on="NAME", right_on="county", how="left"
    ).fillna({"count": 0})

    qa_choropleth(county_counts, merged)

    # Get bounds of only counties with > 0 residents
    bounds = merged[merged["count"] > 0].total_bounds  # (minx, miny, maxx, maxy)

    ax = merged.plot(
        column="count",
        cmap="OrRd",
        scheme="Quantiles",
        k=5,
        legend=False,
        figsize=(8, 6),
        edgecolor="black",
        linewidth=0.5
    )

    # Zoom to counties of interest
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])

    cmap = plt.get_cmap("OrRd")  # Same as plot
    norm = mcolors.Normalize(vmin=merged["count"].min(), vmax=merged["count"].max())

    # === ADD LABELS HERE ===
    for idx, row in merged.iterrows():
        if row['geometry'] is None or row['geometry'].is_empty:
            continue
        # Get a point in the middle of the polygon
        x, y = row['geometry'].centroid.coords[0]
        # Annotate with name + count
        label = f"{row['NAME']}\n{int(row['count'])}"

        # Get background color and compute brightness
        r, g, b, _ = cmap(norm(row["count"]))
        brightness = (0.299 * r + 0.587 * g + 0.114 * b)  # perceived luminance

        # Choose text color
        text_color = "white" if brightness < 0.9 else "black"

        ax.annotate(
            text=label,
            xy=(x, y),
            ha='center',
            fontsize=6,  # keep small so it fits
            color=text_color
        )
    # =======================

    # Title uses provided year range if available
    if earliest_year is not None and latest_year is not None:        
        title_suffix = f" ({earliest_year}–{latest_year})"           
    else:
        title_suffix = f" ({cert_year})"  

    ax.set_title(f"{state_name} Residency Counts {title_suffix}")
    ax.set_axis_off()
    plt.tight_layout()

    out = f"{map_out_dir}/{state_code.lower()}_choropleth_{cert_year}.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Map saved to {out}")

def qa_choropleth(county_counts, merged):
    counts_set = set(county_counts["county"])
    shape_set = set(merged["NAME"])
    
    missing_in_shape = counts_set - shape_set
    print("[QA] Missing in shapefile:", missing_in_shape)
    
    expected_total = county_counts["count"].sum()
    matched_total = merged["count"].sum()
    print(f"[QA] Expected total: {expected_total}")
    print(f"[QA] Matched total:  {matched_total}")
    print(f"[QA] Missing people: {expected_total - matched_total}")
    
    zero_counties = merged[merged["count"] == 0]["NAME"].tolist()
    print("[QA] Counties plotted with 0:", zero_counties)

def get_cert_year_range(state_code: str):
    """
    Read names_to_lookup_{state}.csv and return (earliest_year, latest_year).
    Assumes first column is year (e.g., 1780), with or without a header.
    """
    path = f"names_to_lookup/names_to_lookup_{state_code.lower()}.csv"  # CHANGE
    # Read without assuming headers; fall back gracefully
    df = pd.read_csv(path, header=None, dtype=str)  # CHANGE
    years = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().astype(int)  # CHANGE
    if years.empty:
        return None, None
    return int(years.min()), int(years.max())

def main():
    p = argparse.ArgumentParser(
        description="Summarize & map loan-office results by state"
    )
    p.add_argument("state", help="Two-letter code, e.g. DE, PA")
    p.add_argument(
        "--year", type=int, default=1777,
        help="Certificate year to filter historic counties"
    )
    p.add_argument(
        "--results-dir", default="results",
        help="Where results_<state>.csv lives"
    )
    p.add_argument(
        "--shapefile",
        default="data/data/US_AtlasHCB_Counties_Gen01/US_HistCounties_Gen01_Shapefile/US_HistCounties_Gen01.shp",
        help="Path to your historic-counties shapefile"
    )
    p.add_argument(
        "--out-dir", default="maps",
        help="Where to write your PNG"
    )
    args = p.parse_args()

    counts = summarize_results(
        args.state, args.year, results_dir=args.results_dir
    )

    earliest, latest = get_cert_year_range(args.state)

    plot_choropleth(
        args.state, counts, args.year,
        shapefile_path=args.shapefile,
        map_out_dir=args.out_dir,
        earliest_year=earliest,
        latest_year=latest
    )


if __name__ == "__main__":
    main()
