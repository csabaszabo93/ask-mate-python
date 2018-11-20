import csv
from datetime import datetime


DATA_FILE_PATH = 'sample_data/'

def read_file(file_name):
    file_path = DATA_FILE_PATH + file_name + ".csv"
    all_data = []

    with open(file_path) as data:
        reader = csv.DictReader(data)
        for data_dict in reader:
            ts = int(data_dict["submission_time"])
            data_dict["submission_time"] = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            all_data.append(data_dict)

    return all_data