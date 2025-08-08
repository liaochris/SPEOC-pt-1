"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# analyze delaware results

# 1. Load your Delaware results
results_df = pd.read_csv("results/results_de.csv")

# 2. Count how many unique names were looked up
unique_names = results_df["name"].nunique()
print(f"Unique names in DE results: {unique_names}")

# 3. Count how many lookups returned a non-empty county
has_county = results_df["county"].notna() & (results_df["county"].str.strip() != "")
count_with_county = has_county.sum()
print(f"Names with county information: {count_with_county}")

# print percentage
print(f"percent of names with location information: {count_with_county / unique_names * 100}")

# 4. Build a per-county summary table
county_counts = (
    results_df[has_county]
      .groupby("county")
      .size()
      .reset_index(name="count")
      .sort_values("count", ascending=False)
)

county_counts["county"] = county_counts["county"].str.upper()

print("\nPer-county counts:")
print(county_counts.to_string(index=False))

# 5. Plot a choropleth of Delaware counties
#    — replace this with the path to your local Delaware counties shapefile
shapefile_path = "data/data/US_AtlasHCB_Counties_Gen01/US_HistCounties_Gen01_Shapefile/US_HistCounties_Gen01.shp"

gdf = gpd.read_file(shapefile_path)

gdf["START_YEAR"] = gdf["START_DATE"].str.split("/").str[0].astype(int)
gdf["END_YEAR"]   = gdf["END_DATE"].str.split("/").str[0].astype(int)

# filter to DE and active in 1777
de_1777 = (
    gdf[
      (gdf.STATE_TERR == 'Delaware')        # Delaware
      & (gdf.START_YEAR <= 1777)
      & ((gdf.END_YEAR  >= 1777) | (gdf.END_YEAR == 9999))
    ]
)

de_1777 = de_1777.merge(
    county_counts,
    left_on="NAME",      # or whatever your county‐name column is
    right_on="county",
    how="left"
).fillna({"count": 0})

# plot choropleth
ax = de_1777.plot(
    column="count",
    cmap="OrRd",
    scheme="Quantiles",
    k=5,
    legend=True,
    figsize=(8, 6),
    edgecolor="black",
    linewidth=0.5,
    legend_kwds={
        "fmt" : "{:.0f}",              # format bins as integers
        "loc" : "upper left",          # anchor inside the axes…
        "bbox_to_anchor": (1.02, 1),   # …then push it to the right
        "title": "Residents"
    }
)
ax.set_title("Delaware Loan Certificate Resident Count (1777-1780)")
ax.set_axis_off()

plt.tight_layout()

# save to disk
plt.savefig("maps/de_choropleth.png", 
            dpi=300,            # resolution
            bbox_inches="tight" # include everything
)

# plt.show()
"""

import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

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

def summarize_results(state_code: str, cert_year: int, results_dir: str = "results"):
    state_code = state_code.upper()
    csv_path = f"{results_dir}/results_{state_code.lower()}.csv"
    df = pd.read_csv(csv_path)

    df["county"] = (
        df["county"]
          .fillna("") 
          .astype(str)
          .str.split(",", n=1)
          .str[0]
          .str.strip()
    )

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
    map_out_dir: str = "maps"
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

    merged = sub.merge(
        county_counts, left_on="NAME", right_on="county", how="left"
    ).fillna({"count": 0})

    ax = merged.plot(
        column="count",
        cmap="OrRd",
        scheme="Quantiles",
        k=5,
        legend=True,
        figsize=(8, 6),
        edgecolor="black",
        linewidth=0.5,
        legend_kwds={
            "fmt"           : "{:.0f}",
            "loc"           : "upper left",
            "bbox_to_anchor": (1.02, 1),
            "title"         : "Residents"
        }
    )
    ax.set_title(f"{state_name} Residency Counts ({cert_year})")
    ax.set_axis_off()
    plt.tight_layout()

    out = f"{map_out_dir}/{state_code.lower()}_choropleth_{cert_year}.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Map saved to {out}")

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

    plot_choropleth(
        args.state, counts, args.year,
        shapefile_path=args.shapefile,
        map_out_dir=args.out_dir
    )

if __name__ == "__main__":
    main()