from algos.pre_processing import filter_duplicates, filter_erroneous
from algos.statistics import *
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

    print("\nOCCUPANCY BY VEHICLE_TYPE => \n")
    percent_occupancy_for_column(occupancy_table, 'vehicle_type', "THA")
    percent_occupancy_for_column(occupancy_table, 'vehicle_type', "IC")
    percent_occupancy_for_column(occupancy_table, 'vehicle_type', "L")
    percent_occupancy_for_column(occupancy_table, 'vehicle_type', "S")
    percent_occupancy_for_column(occupancy_table, 'vehicle_type', "P")

    print("\nOCCUPANCY BY WEEKDAY => \n")
    percent_occupancy_for_column(occupancy_table, 'weekday', "MONDAY")
    percent_occupancy_for_column(occupancy_table, 'weekday', "TUESDAY")
    percent_occupancy_for_column(occupancy_table, 'weekday', "WEDNESDAY")
    percent_occupancy_for_column(occupancy_table, 'weekday', "THURSDAY")
    percent_occupancy_for_column(occupancy_table, 'weekday', "FRIDAY")
    percent_occupancy_for_column(occupancy_table, 'weekday', "SATURDAY")
    percent_occupancy_for_column(occupancy_table, 'weekday', "SUNDAY")

    # entries_per_day = occupancy_table.pivot(['weekday'])
    #
    # monday_results = occupancy_table.where(lambda row: 'MONDAY' == row['weekday'])
    # tuesday_results = occupancy_table.where(lambda row: 'TUESDAY' == row['weekday'])
    # wednesday_results = occupancy_table.where(lambda row: 'WEDNESDAY' == row['weekday'])
    # thursday_results = occupancy_table.where(lambda row: 'THURSDAY' == row['weekday'])
    # friday_results = occupancy_table.where(lambda row: 'FRIDAY' == row['weekday'])
    # saturday_results = occupancy_table.where(lambda row: 'SATURDAY' == row['weekday'])
    # sunday_results = occupancy_table.where(lambda row: 'SUNDAY' == row['weekday'])
    #
    # # monday_results.order_by('date').print_table(max_rows=2000, max_columns=15)
    #
    # monday_results.group_by('occupancy').order_by('date').merge().print_table(max_rows=2000, max_columns=15)


if __name__ == "__main__":
    main()
