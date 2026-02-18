### Overview

Post-1790 assumed state debt (ASD) records by state — federal securities issued to holders of state-issued revolutionary war debts after Hamilton's 1790 assumption plan converted state debts into federal obligations.

### Source

National Archives and Records Administration (NARA), T-series microfilm records. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

XLSX spreadsheets transcribed from National Archives T-series microfilm, obtained via Dropbox from the research team. Same T-series rolls as the CD records.

### Description

**`orig/`** — State XLSX files (one per state, in state-abbreviation subfolders):
- `CT/CT_post1790_ASD_ledger.xlsx`
- `MD/MD_post1790_ASD.xlsx`
- `NC/T695_R3_NC_ASD.xlsx`
- `NH/T652_New_Hampshire_ASD.xlsx`
- `NY/NY_1790_ASD.xlsx`
- `RI/T653_Rhode_Island_ASD.xlsx`
- `SC/Post_1790_South_Carolina_ASD_transfers_removed.xlsx`
- `VA/VA_ASD.xlsx`

**`docs/`** — Documentation about the dataset (to be populated).

### Terms of Use

Academic research use. Data derived from public National Archives records.

### Notes

Not all states have ASD records — GA, NJ, and PA are absent from this collection. SC's file has transfers removed. No cleaning pipeline exists for ASD data yet; `cleaning_asd/clean_1.ipynb` was an empty placeholder. Building the ASD cleaning pipeline is a future task that should mirror the post-1790 CD pipeline structure.
