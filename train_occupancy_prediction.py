from algos.pre_processing import filter_duplicates, filter_erroneous
from domain.occupancy import Occupancy
from domain.station import Station
from utils.file_utils import parse_csv_file_to_list, parse_json_file_to_list
import agate

OCCUPANCY_DATA_FILE = 'occupancy-until-20161029.newlinedelimitedjsonobjects'
STATIONS_DATA_FILE = 'stations.csv'


def main():
    occupancies_raw_data = parse_json_file_to_list(OCCUPANCY_DATA_FILE)
    stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)

    stations = {station.number: station for station in
                [Station(station_data) for station_data in stations_raw_data]}
    occupancies = [Occupancy(occupancy_data, stations) for occupancy_data in occupancies_raw_data]

    occupancies = filter_duplicates(filter_erroneous(occupancies))

    column_names = ['date', 'weekday', "from", "to", "vehicle", "vehicle_type", "occupancy"]

    column_types = [agate.DateTime(), agate.Text(), agate.Number(), agate.Number(), agate.Text(), agate.Text(),
                    agate.Text()]

    occupancies_list = []
    for occupancy in occupancies:
        occupancies_list.append(occupancy.to_list())

    occupancy_table = agate.Table(occupancies_list, column_names, column_types)
    occupancy_table.print_csv()
    print("Number of records after merging duplicates: ", len(occupancies))


if __name__ == "__main__":
    main()
