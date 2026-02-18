### Overview

Membership lists of the Society of the Cincinnati by state. Used in analysis to identify military officers among debt certificate holders.

### Source

Society of the Cincinnati historical records. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

Text files obtained via the research team. One file per state plus an aggregated officers list.

### Description

**`orig/`** — Original data files:
- `all_officers_ari.txt` — Aggregated list of all officers (6,864 lines). Format: `LastName, FirstName(s), Title, (State)`. This is the only non-empty file and the primary source used in analysis. <!-- ORIGIN UNKNOWN: source/compilation method of this aggregated list is unclear. -->
- State-specific files (`connecticut.txt`, `delaware.txt`, `georgia.txt`, `maryland.txt`, `massachusetts.txt`, `new_hampshire.txt`, `new_jersey.txt`, `new_york.txt`, `north_carolina.txt`, `pennsylvania.txt`, `rhode_island.txt`, `virginia.txt`) — **All empty** (0 lines), except `rhode_island.txt` (2 lines). These are placeholder files; `all_officers_ari.txt` is the authoritative source for all states. Consider populating state files from `all_officers_ari.txt` or removing them in a future task.

**`docs/`** — Documentation about the dataset (to be populated).

### Terms of Use

Academic research use.

### Notes

Only `all_officers_ari.txt` contains actual data. The 12 state-specific .txt files are empty placeholders and should not be relied upon. Used in the pre-1790 analysis pipeline to cross-reference certificate holders against known military officers.
