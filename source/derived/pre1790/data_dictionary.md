## Pre-1790 Certificate Data Dictionary

Documentation for all columns in `agg_debt_grouped.csv`, the cleaned and compiled dataset of pre-1790 certificates.

### Variables

| Column | Name | Description | dtype |
|---|---|---|---|
| A | `index` | Index (starts at 0) | int64 |
| B | `letter` | Imported from data files. Currently unsure what it means. | object (string) |
| C | `date of the certificate \| Month` | Month when the certificate was issued | float64 |
| D | `date of the certificate \| day` | Day when the certificate was issued | float64 |
| E | `date of the certificate \| year` | Year when the certificate was issued | float64 |
| F | `to whom due \| first name` | First name of person to whom the certificate was issued | object (string) |
| G | `to whom due \| last name` | Last name of person to whom the certificate was issued | object (string) |
| H | `to whom due \| title` | Title of the person (e.g., 'Esq', 'Rev') | object (string) |
| I | `time when the debt became due \| month` | Month when the original claim was due. The government issued these liquidated debt certificates since it could not immediately pay the original claim. | float64 |
| J | `time when the debt became due \| day` | Day when the original claim was due | object |
| K | `time when the debt became due \| year` | Year when original claim was due | object |
| L | `amount \| dollars` | Face value of the certificate (dollars) | float64 |
| M | `amount \| 90th` | Face value (cents). Cents are out of 90, not 100. Half a dollar is 45, not 50 cents. | object |
| N | `line strike through? \| yes?` | From uncleaned dataset (physical debt records). '1' if name was crossed off. Reason unknown. | float64 |
| O | `line strike through? \| note` | From uncleaned dataset. Meaning unknown. | object |
| P | `notes` | Transcriber notes from the original physical-to-digital conversion | object (string) |
| Q | `state` | The state from which the debt record originated | object (string) |
| R | `org_file` | Original CSV file where the record came from. Example: `liquidated_debt_certificates_NH.xlsx` | object (string) |
| S | `org_index` | Rows merged during grouping. Example: `1 \| 2` means rows 1 and 2 in `final_agg_debt.csv` were merged. | object (string) |
| T | `to whom due \| title.1` | Duplicate title column. May ignore. | object (string) |
| U | `to whom due \| first name.1` | First name of 2nd person (co-ownership) | object (string) |
| V | `to whom due \| last name.1` | Last name of 2nd person (co-ownership) | object (string) |
| W | `amount \| 10th` | Face value (cents). Cents are out of 10. Example: 2 = 20 cents. | float64 |
| X | `exchange` | Exchange rate, most likely between dollars and specie. Mostly Pennsylvania records. | object (string) |
| Y | `amount in specie \| dollars` | Certificate dollar amount converted to specie value | float64 |
| Z | `amount in specie \| cents` | Certificate cents amount converted to specie value | float64 |
| AA | `amount \| 8th` | Face value (cents). Cents are out of 8. | float64 |
| AB | `delivered \| month` | Delivery month (when certificate was handed to buyer) | float64 |
| AC | `delivered \| day` | Delivery day | float64 |
| AD | `delivered \| year` | Delivery year | float64 |
| AE | `total dollars \| notes` | From original dataset. Meaning unsure. | object (string) |
| AF | `total dollars \| notes.1` | Ignore. Carried over by mistake. | float64 |
| AG | `final_agg_debt index` | Index location of the row in `final_agg_debt.csv` | object |
