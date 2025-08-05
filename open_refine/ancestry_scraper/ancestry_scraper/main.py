import csv
from .worker import process_name

if __name__ == '__main__':
    with open('names_to_lookup.csv', newline='') as f:
        for row in csv.reader(f):
            name = row[0].strip()
            if name:
                process_name(name, event_year=1777)
