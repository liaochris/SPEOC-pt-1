#!/usr/bin/env python
# coding: utf-8

import sys
from pathlib import Path
import pandas as pd
from rapidfuzz import process
from source.lib.SaveData import SaveData

OUTDIR = Path("output/derived/prescrape/pre1790")


def Main():
    state_filter = sys.argv[1] if len(sys.argv) > 1 else None

    agg_debt = pd.read_csv(OUTDIR / 'pre1790_cleaned.csv')

    agg_debt['full name'] = [' '.join([str(fn), str(ln)]) for fn, ln in zip(agg_debt['to whom due | first name'], agg_debt['to whom due | last name'])]

    agg_debt_filtered = agg_debt[(agg_debt['state'] != 'cs') & (agg_debt['state'] != 'f') & (agg_debt['state'] != 'de')]

    (OUTDIR / 'similar_names').mkdir(parents=True, exist_ok=True)

    agg_debt_sp = agg_debt_filtered.groupby('state')
    first_state = True
    for state in agg_debt_sp.groups:
        if state_filter and state != state_filter:
            continue
        agg_debt_st = agg_debt_sp.get_group(state).copy()
        names = agg_debt_st['full name'].tolist()
        scores = process.cdist(names, names, score_cutoff=90, workers=-1)
        matches_list = [FilterMatches(names, scores[i]) for i in range(len(names))]
        agg_debt_st['matches'] = matches_list
        agg_debt_st_clean = agg_debt_st[agg_debt_st['matches'].apply(len) > 0].copy()
        agg_debt_st_clean['matches'] = agg_debt_st_clean['matches'].apply(str)
        agg_debt_st_clean = agg_debt_st_clean.reset_index(drop=True)
        agg_debt_st_clean['row_id'] = agg_debt_st_clean.index
        log_file = OUTDIR / f'similar_names/similar_names_{state}.log' if state_filter else OUTDIR / 'similar_names/similar_names.log'
        SaveData(agg_debt_st_clean, ['row_id'], OUTDIR / f'similar_names/similar_names_{state}.csv',
                 log_file=log_file, append=not first_state)
        first_state = False


def FilterMatches(names, row_scores):
    seen = set()
    filtered = []
    for j, score in enumerate(row_scores):
        if 90 <= score < 100 and names[j] not in seen:
            seen.add(names[j])
            filtered.append((names[j], score, j))
    return filtered


if __name__ == "__main__":
    Main()
