import csv
from datetime import datetime


DATA_FILE_PATH = 'sample_data/'

def read_file(file_name, convert_stamp=True):
    file_path = DATA_FILE_PATH + file_name + ".csv"
    all_data = []

    with open(file_path) as data:
        reader = csv.DictReader(data)
        for data_dict in reader:
            if convert_stamp:
                ts = int(data_dict["submission_time"])
                data_dict["submission_time"] = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            all_data.append(data_dict)

    return all_data


def add_new_data(new_data, file_name):
    file_path = DATA_FILE_PATH + file_name + ".csv"

    with open(file_path, 'a') as data:
        writer = csv.DictWriter(data, fieldnames=get_fieldnames(file_path))
        writer.writerow(new_data)


def rewrite_data(new_data, file_name):
    file_path = DATA_FILE_PATH + file_name + ".csv"
    fieldnames = get_fieldnames(file_path)

    with open(file_path, 'w') as data:
        writer = csv.DictWriter(data, fieldnames=fieldnames)

        writer.writeheader()
        for row in new_data:
            writer.writerow(row)


def get_fieldnames(file_path):
    with open(file_path) as data:
        fieldnames = data.readline().strip().split(',')
        return fieldnames
