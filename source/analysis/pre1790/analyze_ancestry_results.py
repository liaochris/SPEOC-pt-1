from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe

INDIR_RESULTS = Path("output/scrape/ancestry_loan_office_scraper/results")
INDIR_NAMES = Path("output/scrape/ancestry_loan_office_scraper/names_to_lookup")
OUTDIR_MAPS = Path("output/analysis/pre1790/ancestry_loan_office")
INDIR_SHAPEFILE = Path("source/raw/shapefiles/orig/historicalcounties/COUNTY_1790_US_SL050_Coast_Clipped.shp")
CERT_YEAR = 1777

STATE_NAMES = {
    "DE": "Delaware", "PA": "Pennsylvania", "NY": "New York", "MA": "Massachusetts",
    "MD": "Maryland", "NH": "New Hampshire", "NJ": "New Jersey", "VA": "Virginia",
    "CT": "Connecticut", "RI": "Rhode Island",
}

COLONIES_13 = ["MA", "NH", "CT", "NY", "NJ", "PA", "DE", "MD", "VA"]


def Main():
    OUTDIR_MAPS.mkdir(parents=True, exist_ok=True)
    for state in COLONIES_13:
        csv_path = INDIR_RESULTS / f"results_{state.lower()}.csv"
        if not csv_path.exists():
            print(f"Skipping {state}: results file not found")
            continue
        counts = SummarizeResults(state, CERT_YEAR)
        earliest, latest = GetCertYearRange(state)
        PlotChoropleth(state, counts, CERT_YEAR,
                       earliest_year=earliest, latest_year=latest)
    PlotNationalChoropleth(cert_year=CERT_YEAR)


def ExtractCounty(loc, state_code):
    if not isinstance(loc, str) or not loc.strip():
        return ""
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    state_name = STATE_NAMES.get(state_code.upper(), "").upper()

    if len(parts) == 3:
        county = parts[1]
    elif len(parts) == 2:
        if state_name and parts[1].upper().startswith(state_name):
            county = parts[0]
        else:
            county = parts[1]
    elif len(parts) == 1:
        county = parts[0]
    else:
        return ""

    county = county.upper().replace("COUNTY", "").strip()
    county = county.replace("'s", "s").replace("'S", "S").strip()
    return county


def SummarizeResults(state_code, cert_year, results_dir=INDIR_RESULTS):
    state_code = state_code.upper()
    csv_path = Path(results_dir) / f"results_{state_code.lower()}.csv"
    df = pd.read_csv(csv_path)
    df["county"] = df["county"].apply(lambda x: ExtractCounty(x, state_code))

    total = df["name"].nunique()
    has_county = df["county"].notna() & df["county"].str.strip().ne("")
    matched = has_county.sum()
    pct = matched / total * 100 if total else 0

    print(f"{state_code} - {total} names, {matched} with counties ({pct:.1f}%)")
    county_counts = (
        df[has_county]
          .groupby("county").size().reset_index(name="count")
          .assign(county=lambda d: d["county"].str.upper())
          .sort_values("count", ascending=False)
    )
    print("\nPer-county counts:")
    print(county_counts.to_string(index=False))
    return county_counts


def PlotChoropleth(state_code, county_counts, cert_year, shapefile_path=INDIR_SHAPEFILE,
                   map_out_dir=OUTDIR_MAPS, earliest_year=None, latest_year=None):
    state_code = state_code.upper()
    state_name = STATE_NAMES[state_code]

    gdf = gpd.read_file(shapefile_path)
    gdf["START_YEAR"] = gdf["START_DATE"].str.split("/").str[0].astype(int)
    gdf["END_YEAR"] = gdf["END_DATE"].str.split("/").str[0].astype(int)

    sel = (
        (gdf["STATE_TERR"] == state_name)
        & (gdf["START_YEAR"] <= cert_year)
        & ((gdf["END_YEAR"] >= cert_year) | (gdf["END_YEAR"] == 9999))
    )
    sub = gdf[sel]
    sub["NAME"] = sub["NAME"].astype(str).str.upper().str.strip()
    sub = sub.dissolve(by="NAME", as_index=False)

    merged = sub.merge(county_counts, left_on="NAME", right_on="county", how="left").fillna({"count": 0})
    QaChoropleth(county_counts, merged)

    bounds = merged[merged["count"] > 0].total_bounds
    ax = merged.plot(column="count", cmap="OrRd", scheme="Quantiles", k=5,
                     legend=False, figsize=(8, 6), edgecolor="black", linewidth=0.5)
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])

    cmap = plt.get_cmap("OrRd")
    norm = mcolors.Normalize(vmin=merged["count"].min(), vmax=merged["count"].max())

    for idx, row in merged.iterrows():
        if row['geometry'] is None or row['geometry'].is_empty or int(row["count"]) == 0:
            continue
        x, y = row['geometry'].centroid.coords[0]
        label = f"{row['NAME']}\n{int(row['count'])}"
        r, g, b, _ = cmap(norm(row["count"]))
        brightness = (0.299 * r + 0.587 * g + 0.114 * b)
        text_color = "white" if brightness < 0.9 else "black"
        ax.annotate(text=label, xy=(x, y), ha='center', fontsize=6, color=text_color)

    if earliest_year is not None and latest_year is not None:
        title_suffix = f" ({earliest_year}-{latest_year})"
    else:
        title_suffix = f" ({cert_year})"

    ax.set_title(f"{state_name} Residency Counts{title_suffix}")
    ax.set_axis_off()
    plt.tight_layout()

    out = Path(map_out_dir) / f"{state_code.lower()}_choropleth_{cert_year}.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Map saved to {out}")


def QaChoropleth(county_counts, merged):
    counts_set = set(county_counts["county"])
    shape_set = set(merged["NAME"])
    print("[QA] Missing in shapefile:", counts_set - shape_set)
    expected_total = county_counts["count"].sum()
    matched_total = merged["count"].sum()
    print(f"[QA] Expected total: {expected_total}")
    print(f"[QA] Matched total:  {matched_total}")
    print(f"[QA] Missing people: {expected_total - matched_total}")
    print("[QA] Counties plotted with 0:", merged[merged["count"] == 0]["NAME"].tolist())


def GetCertYearRange(state_code):
    path = INDIR_NAMES / f"names_to_lookup_{state_code.lower()}.csv"
    df = pd.read_csv(path, header=None, dtype=str)
    years = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().astype(int)
    if years.empty:
        return None, None
    return int(years.min()), int(years.max())


def BuildNationalCounts(state_codes, results_dir=INDIR_RESULTS):
    frames = []
    for sc in state_codes:
        sc_u = sc.upper()
        csv_path = Path(results_dir) / f"results_{sc_u.lower()}.csv"
        if not csv_path.exists():
            print(f"[WARN] Missing results file for {sc_u}, skipping.")
            continue
        df = pd.read_csv(csv_path)
        df["county"] = (
            df["county"].fillna("").astype(str)
            .apply(lambda s: ExtractCounty(s, sc_u)).str.upper().str.strip()
        )
        has_county = df["county"].ne("")
        cc = df[has_county].groupby("county", as_index=False).size().rename(columns={"size": "count"})
        if cc.empty:
            continue
        cc["state_code"] = sc_u
        cc["state_name"] = STATE_NAMES[sc_u].upper()
        frames.append(cc)

    if not frames:
        return pd.DataFrame(columns=["state_code", "state_name", "county", "count"])
    out = pd.concat(frames, ignore_index=True)
    out = out.groupby(["state_code", "state_name", "county"], as_index=False)["count"].sum()
    return out


def PlotNationalChoropleth(cert_year, shapefile_path=INDIR_SHAPEFILE,
                            results_dir=INDIR_RESULTS, states=COLONIES_13):
    county_counts = BuildNationalCounts(states, results_dir=results_dir)

    gdf = gpd.read_file(shapefile_path)
    gdf["START_YEAR"] = gdf["START_DATE"].str.split("/").str[0].astype(int)
    gdf["END_YEAR"] = gdf["END_DATE"].str.split("/").str[0].astype(int)

    want_states = {STATE_NAMES[s].upper() for s in [s.upper() for s in states]}
    sub = gdf[
        (gdf["STATE_TERR"].str.upper().isin(want_states))
        & (gdf["START_YEAR"] <= cert_year)
        & ((gdf["END_YEAR"] >= cert_year) | (gdf["END_YEAR"] == 9999))
    ].copy()

    sub["STATE_TERR"] = sub["STATE_TERR"].astype(str).str.upper().str.strip()
    sub["NAME"] = sub["NAME"].astype(str).str.upper().str.strip()
    sub = sub.dissolve(by=["STATE_TERR", "NAME"], as_index=False)

    counts = county_counts.rename(columns={"state_name": "STATE_TERR", "county": "NAME"})
    merged = sub.merge(counts[["STATE_TERR", "NAME", "count"]], on=["STATE_TERR", "NAME"],
                       how="left").fillna({"count": 0})

    ax = merged.plot(column="count", cmap="OrRd", scheme="UserDefined",
                     classification_kwds={"bins": [1, 5, 10, 20, 50, 100, 200, 1000]},
                     legend=True, figsize=(10, 10), edgecolor="black", linewidth=0.2,
                     legend_kwds={"fmt": "{:.0f}", "title": "Residents"})

    sub_states = sub.copy()
    sub_states["STATE_TERR"] = sub_states["STATE_TERR"].astype(str).str.upper().str.strip()
    sub_states = sub_states.dissolve(by="STATE_TERR", as_index=False)
    sub_states.boundary.plot(ax=ax, color="black", linewidth=1.0)

    ax.set_title("Residency Counts by County - Thirteen Colonies", fontsize=12)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUTDIR_MAPS / "national_13_colonies.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    Main()
