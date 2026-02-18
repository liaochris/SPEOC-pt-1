import pandas as pd

# 1. Load dataset
df = pd.read_csv("data/loan_office_certificates_cleaned.csv")

# 2. Create 'raw_name_state' and drop duplicates
df["raw_name_state"] = df["raw_name"].astype(str).str.strip() + "||" + df["state"].astype(str).str.strip()
df = df.drop_duplicates(subset=["raw_name_state"]).reset_index(drop=True)

# 3. Print total number of rows after dropping duplicates
print(f"Total unique rows: {len(df)}")

# 4. Allow user to search for a name and see its position
while True:
    name = input("\nEnter a raw_name_state to search (or 'q' to quit): ").strip()
    if name.lower() == "q":
        break
    matches = df.index[df["raw_name_state"].str.lower() == name.lower()].tolist()
    if matches:
        print(f"Found at position(s): {', '.join(str(i) for i in matches)} (0-based index)")
    else:
        print("Not found.")