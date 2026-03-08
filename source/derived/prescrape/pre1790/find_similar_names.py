#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import pandas as pd
from rapidfuzz import process
from source.lib.SaveData import SaveData

OUTDIR = Path("output/derived/prescrape/pre1790")


def Main():
    agg_debt = pd.read_csv(OUTDIR / 'agg_debt_grouped.csv')

    agg_debt['full name'] = [' '.join([str(fn), str(ln)]) for fn, ln in zip(agg_debt['to whom due | first name'], agg_debt['to whom due | last name'])]

    agg_debt_filtered = agg_debt[(agg_debt['state'] != 'cs') & (agg_debt['state'] != 'f') & (agg_debt['state'] != 'de')]

    (OUTDIR / 'similar_names').mkdir(parents=True, exist_ok=True)

    agg_debt_sp = agg_debt_filtered.groupby('state')
    for state in agg_debt_sp.groups:
        agg_debt_st = agg_debt_sp.get_group(state).copy()
        agg_debt_st['matches'] = agg_debt_st['full name'].apply(
            lambda full_name: FilterMatches(process.extract(full_name, agg_debt_st['full name'], score_cutoff=90))
        )
        agg_debt_st_clean = agg_debt_st[agg_debt_st['matches'].apply(len) > 0].copy()
        agg_debt_st_clean['matches'] = agg_debt_st_clean['matches'].apply(str)
        agg_debt_st_clean = agg_debt_st_clean.reset_index(drop=True)
        agg_debt_st_clean['row_id'] = agg_debt_st_clean.index
        SaveData(agg_debt_st_clean, ['row_id'], OUTDIR / f'similar_names/similar_names_{state}.csv')


def FilterMatches(matches):
    seen = set()
    filtered = []
    for name, score, index in matches:
        if score < 100 and name not in seen:
            seen.add(name)
            filtered.append((name, score, index))
    return filtered


if __name__ == "__main__":
    Main()
