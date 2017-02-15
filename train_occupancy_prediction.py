from algos.pre_processing import filter_duplicates, filter_erroneous
from domain.occupancy import Occupancy
from domain.station import Station
from utils.file_utils import parse_csv_file_to_list, parse_json_file_to_list

OCCUPANCY_DATA_FILE = 'occupancy-until-20161029.newlinedelimitedjsonobjects'
STATIONS_DATA_FILE = 'stations.csv'


def main():
    occupancies_raw_data = parse_json_file_to_list(OCCUPANCY_DATA_FILE)
    stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)

    stations = {station.number: station for station in
                [Station(station_data) for station_data in stations_raw_data]}
    occupancies = [Occupancy(occupancy_data, stations) for occupancy_data in occupancies_raw_data]

    occupancies = filter_duplicates(filter_erroneous(occupancies))

    for occupancy in occupancies:
        occupancy.print_data()
    print("Number of records after merging duplicates: ", len(occupancies))


if __name__ == "__main__":
    main()
