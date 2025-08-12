import pandas as pd

df = pd.read_csv("results/task_4_matches_filtered_nosamenames.csv")

# 1) Valid states only
valid_states = {"CT","DE","MA","MD","NH","NJ","NY","PA","VA"}
df = df[df["state"].isin(valid_states)]

# 2) Deduplicate child_id
df = df.sort_values(["child_id"]).drop_duplicates("child_id", keep="first")

# 3) Flag multi-parent
df["multi_parent"] = df["parent_ids_all"].fillna("").str.contains(";")

# 4) Split into keep vs. review
review_mask = df["multi_parent"] | df["state"].isna()
keep = df[~review_mask].copy()
review = df[review_mask].copy()

keep.to_csv("results/task_4_final.csv", index=False)
review.to_csv("results/task_4_review.csv", index=False)

print(f"Final: {len(keep)} | Review: {len(review)}")