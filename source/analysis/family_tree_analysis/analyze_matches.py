from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from source.lib.SaveData import SaveData

INDIR_RESULTS = Path("output/derived/postscrape/family_tree")
OUTDIR = Path("output/analysis/family_tree_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)


def Main():
    df = pd.read_csv(INDIR_RESULTS / "final_matches.csv")
    task_3_matches = pd.read_csv(INDIR_RESULTS / "candidate_matches.csv")

    summary_df, state_counts_df, top_child_names_df = ComputeSummaryStats(df)
    SaveData(summary_df, ['Statistic'], OUTDIR / "match_summary.csv", log_file=OUTDIR / "match_summary.log")
    SaveData(state_counts_df, ['State'], OUTDIR / "match_by_state.csv", log_file=OUTDIR / "match_by_state.log")
    SaveData(top_child_names_df, ['Child Name'], OUTDIR / "top_child_names.csv", log_file=OUTDIR / "top_child_names.log")

    matching_rates = ComputeMatchingRates(task_3_matches)
    SaveData(matching_rates, ['state'], OUTDIR / "matching_rates.csv", log_file=OUTDIR / "matching_rates.log")

    PlotMatchingRates(matching_rates)


def ComputeSummaryStats(df):
    stats = {
        'Total Matches': len(df),
        'Unique Parents': df['parent_id'].nunique(),
        'Rows with Errors': df['error'].notna().sum(),
        'Multi-Parent Count': df['multi_parent'].sum() if 'multi_parent' in df.columns else None,
    }
    summary_df = pd.DataFrame({
        "Statistic": list(stats.keys()),
        "Value": list(stats.values()),
    })

    state_counts_df = df['state'].value_counts().reset_index()
    state_counts_df.columns = ['State', 'Count']

    top_child_names_df = df['child_name'].value_counts().head(10).reset_index()
    top_child_names_df.columns = ['Child Name', 'Count']

    return summary_df, state_counts_df, top_child_names_df


def ComputeMatchingRates(task_3_matches):
    state_summary = (
        task_3_matches.groupby('state')['in_post1790']
        .mean()
        .sort_values(ascending=False)
        * 100
    )
    matching_rates = state_summary.reset_index()
    matching_rates.columns = ['state', 'match_rate']
    return matching_rates


def PlotMatchingRates(matching_rates):
    plt.figure(figsize=(10, 6))
    plt.bar(matching_rates['state'], matching_rates['match_rate'], color='steelblue')
    plt.ylabel("Match Rate (%)")
    plt.title("WikiTree Matching Rate by State")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTDIR / "matching_rate_by_state.png")
    plt.close()


if __name__ == "__main__":
    Main()
