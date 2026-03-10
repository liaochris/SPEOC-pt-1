from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from source.lib.SaveData import SaveData

INDIR_PRE1790 = Path("output/derived/prescrape/pre1790")
INDIR_POST1790 = Path("output/derived/postscrape/post1790_cd")
INDIR_RAW_PRE1790 = Path("source/raw/pre1790/orig")
INDIR_SHAPEFILE = Path("source/raw/shapefiles/orig/nhgis_state_1790/US_state_1790.shp")
OUTDIR = Path("output/analysis/pre1790/pierce")
OUTDIR.mkdir(parents=True, exist_ok=True)

STATE_ABBR_TO_NAME = {
    "RI": "Rhode Island", "PA": "Pennsylvania", "NY": "New York", "MA": "Massachusetts",
    "MD": "Maryland", "NH": "New Hampshire", "NJ": "New Jersey", "VA": "Virginia",
    "CT": "Connecticut", "DE": "Delaware", "NC": "North Carolina", "SC": "South Carolina",
    "GA": "Georgia",
}


def Main():
    gdf = LoadStateShapefile()
    pre1790 = LoadPre1790()
    post1790 = LoadPost1790()
    pierce_certs = LoadPierceCerts()

    MapPreDebtByState(gdf, pre1790)
    MapPostDebtByState(gdf, post1790)
    MapPierceCertsByState(gdf, pierce_certs)
    SavePierceCertsRegiment(pierce_certs)


def LoadStateShapefile():
    gdf = gpd.read_file(INDIR_SHAPEFILE)
    gdf["state_abbr"] = gdf["STATENAM"].map({v: k for k, v in STATE_ABBR_TO_NAME.items()})
    return gdf


def LoadPre1790():
    pre1790 = pd.read_csv(INDIR_PRE1790 / "pre1790_cleaned.csv")
    pre1790["dollars"] = pd.to_numeric(pre1790.get("amount | dollars"), errors="coerce").fillna(0)
    cents_raw = pre1790.get("amount | 90th", pd.Series(dtype=str))
    cents_raw = cents_raw.astype(str).str.split(".").str[0].str.replace("/", "")
    pre1790["cents"] = pd.to_numeric(cents_raw, errors="coerce").fillna(0) / 100
    pre1790.loc[pre1790["cents"] >= 100, "cents"] = 0
    pre1790["total_amt"] = pre1790["dollars"] + pre1790["cents"]
    pre1790 = pre1790.dropna(subset=["state"])
    pre1790 = pre1790[~pre1790["state"].isin(["cs", "f"])]
    return pre1790.groupby("state", as_index=False)["total_amt"].sum()


def LoadPost1790():
    post1790 = pd.read_csv(INDIR_POST1790 / "final_data_CD.csv")
    post1790 = post1790.dropna(subset=["Group State"])
    post1790_states = post1790.groupby("Group State", as_index=False)["final_total_adj"].sum()
    post1790_states.columns = ["state", "total_amt"]
    return post1790_states


def LoadPierceCerts():
    pierce = pd.read_excel(INDIR_RAW_PRE1790 / "Pierce_Certs_cleaned_2019.xlsx")
    pierce["Value"] = pd.to_numeric(pierce["Value"], errors="coerce").fillna(0)
    pierce = pierce.dropna(subset=["State"])
    pierce = pierce[~pierce["State"].isin(["CS", "F"])]
    return pierce


def MapPreDebtByState(gdf, pre1790):
    merged = gdf.merge(pre1790, left_on="state_abbr", right_on="state", how="left")
    merged["total_amt"] = merged["total_amt"].fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged.plot(column="total_amt", ax=ax, cmap="Blues", legend=True,
                legend_kwds={"label": "Total Debt (dollars)", "shrink": 0.6},
                edgecolor="black", linewidth=0.5, missing_kwds={"color": "lightgray"})
    ax.set_title("Pre-1790 Debt By State (dollars)")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUTDIR / "pre1790_debt_by_state.png", dpi=150)
    plt.close()


def MapPostDebtByState(gdf, post1790):
    merged = gdf.merge(post1790, left_on="state_abbr", right_on="state", how="left")
    merged["total_amt"] = merged["total_amt"].fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged.plot(column="total_amt", ax=ax, cmap="Oranges", legend=True,
                legend_kwds={"label": "Total Debt (dollars)", "shrink": 0.6},
                edgecolor="black", linewidth=0.5, missing_kwds={"color": "lightgray"})
    ax.set_title("Post-1790 Debt By State (dollars)")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUTDIR / "post1790_debt_by_state.png", dpi=150)
    plt.close()


def MapPierceCertsByState(gdf, pierce_certs):
    state_totals = pierce_certs.groupby("State", as_index=False)["Value"].sum()
    state_totals.columns = ["state", "total_amt"]
    merged = gdf.merge(state_totals, left_on="state_abbr", right_on="state", how="left")
    merged["total_amt"] = merged["total_amt"].fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged.plot(column="total_amt", ax=ax, cmap="Greens", legend=True,
                legend_kwds={"label": "Pierce Cert Value (dollars)", "shrink": 0.6},
                edgecolor="black", linewidth=0.5, missing_kwds={"color": "lightgray"})
    ax.set_title("Pierce Certificates by State")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(OUTDIR / "pierce_certs_by_state.png", dpi=150)
    plt.close()


def SavePierceCertsRegiment(pierce_certs):
    pierce_certs = pierce_certs.copy()
    pierce_certs["Value"] = pd.to_numeric(pierce_certs["Value"], errors="coerce").fillna(0)
    pierce_reg = pierce_certs.groupby("Group", as_index=False).agg(
        Value=("Value", "sum"),
        regiment=("To Whom Issued", "first"),
        State=("State", "first"),
    )
    pierce_reg["regiment"] = pierce_reg["regiment"].astype(str).str.replace(";", ":")
    total = pierce_reg["Value"].sum()
    pierce_reg["percent_owned"] = pierce_reg["Value"] / total * 100
    pierce_reg = pierce_reg.sort_values("Value", ascending=False)
    SaveData(pierce_reg, ["Group"], OUTDIR / "pierce_certs_reg.csv", log_file=OUTDIR / "pierce_certs_reg.log")


if __name__ == "__main__":
    Main()
