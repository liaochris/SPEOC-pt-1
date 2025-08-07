import os, csv, json
from .config import OUTPUT_CSV, CHECKPOINT_FILE

def load_progress(state): # get current checkpoint file
    try:
        return json.load(open("progress_" + state + ".json", 'r'))
        #return json.load(open(CHECKPOINT_FILE + "_" + state, 'r'))
    except:
        return {}


def save_progress(data, state): # store data in checkpoint file 
    json.dump(data, open("progress_" + state + ".json", 'w'))
    #json.dump(data, open(CHECKPOINT_FILE + "_" + state, 'w'))


def append_result(row, state): # append row to csv file 
    output_file = "results_" + state + ".csv" # new
    need_header = not os.path.exists(output_file)
    with open(output_file, 'a', newline='') as f:
        w = csv.writer(f)
        if need_header: # add header if csv file is empty 
            w.writerow(['name', 'url', 'county'])
        w.writerow(row)