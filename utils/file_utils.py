import json
import csv


def parse_json_file_to_list(filename):
    with open(filename) as occupancy_data_file:
        lines = occupancy_data_file.readlines()
        return [json.loads(line) for line in lines]


def parse_csv_file_to_list(filename):
    # Open the Station data
    with open(filename) as stations_file:
        reader = csv.reader(stations_file)
        stations_data = [row for row in reader]
        return stations_data[1:] if len(stations_data) > 1 else stations_data
