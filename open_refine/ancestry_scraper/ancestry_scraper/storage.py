import os, csv, json
from .config import OUTPUT_CSV, CHECKPOINT_FILE

def load_progress(): # get current checkpoint file
    try:
        return json.load(open(CHECKPOINT_FILE, 'r'))
    except:
        return {}


def save_progress(data): # store data in checkpoint file 
    json.dump(data, open(CHECKPOINT_FILE, 'w'))


def append_result(row): # append row to csv file 
    need_header = not os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline='') as f:
        w = csv.writer(f)
        if need_header: # add header if csv file is empty 
            w.writerow(['name', 'search_url', 'residence_county'])
        w.writerow(row)