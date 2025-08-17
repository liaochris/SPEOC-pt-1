import pandas as pd
import matplotlib.pyplot as plt

# Load the provided CSV
file_path = "../results/task_4_final.csv"
df = pd.read_csv(file_path)

task_3_matches = pd.read_csv("../results/task_3_matches.csv")

# Basic statistics
stats = {}

# Total number of rows
stats['Total Matches'] = len(df)

# Matches per state
state_counts = df['state'].value_counts()

# Unique parent count
stats['Unique Parents'] = df['parent_id'].nunique()

# Matches with errors
stats['Rows with Errors'] = df['error'].notna().sum()

# Top names (children)
top_child_names = df['child_name'].value_counts().head(10)

# Multi-parent occurrences
if 'multi_parent' in df.columns:
    stats['Multi-Parent Count'] = df['multi_parent'].sum()
else:
    stats['Multi-Parent Count'] = "Column not found"

# Present results
summary_df = pd.DataFrame({
    "Statistic": list(stats.keys()),
    "Value": list(stats.values())
})

print(summary_df)
latex_str = summary_df.to_latex(index=False)  # index=False if you don't want row numbers
print(latex_str)

# Also return top states and top child names for more insight
state_counts_df = state_counts.reset_index()
state_counts_df.columns = ['State', 'Count']

top_child_names_df = top_child_names.reset_index()
top_child_names_df.columns = ['Child Name', 'Count']

summary_dfs = {
    "Top States": state_counts_df,
    "Top Child Names": top_child_names_df
}

print(summary_dfs)


# Count children per parent
child_counts = df.groupby('parent_id')['child_id'].nunique().reset_index(name='num_children')

# Sort by number of children descending
child_counts_sorted = child_counts.sort_values(by='num_children', ascending=False)

# Display the dataframe
greater_than_two = child_counts_sorted[child_counts_sorted["num_children"] >= 2]
print(len(greater_than_two))
latex_str = greater_than_two.head(10).to_latex(index=False)
print(latex_str)

# Overall distribution
summary = task_3_matches['in_post1790'].value_counts(normalize=True).rename({True: "Matched", False: "Not Matched"}) * 100
print("Overall Matching Rate (%):")
print(summary)

# Distribution by state
state_summary = task_3_matches.groupby('state')['in_post1790'].mean().sort_values(ascending=False) * 100
print("\nMatching Rate by State (%):")
print(state_summary)

# Plot
plt.figure(figsize=(10,6))
state_summary.plot(kind='bar', color='steelblue')
plt.ylabel("Match Rate (%)")
plt.title("WikiTree Matching Rate by State")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

