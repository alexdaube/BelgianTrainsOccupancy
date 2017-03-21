from algos.pre_processing import filter_duplicates, filter_erroneous
from algos.data_transformation import calculateRushHourConfidence
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

    column_names = ['date', 'hour', 'weekday', "from", "to", "vehicle", "vehicle_type", "occupancy"]

    column_types = [agate.DateTime(), agate.Number(), agate.Text(), agate.Number(), agate.Number(), agate.Text(),
                    agate.Text(),
                    agate.Text()]

    occupancies_list = []
    for occupancy in occupancies:
        occupancies_list.append(occupancy.to_list())

    occupancy_table = agate.Table(occupancies_list, column_names, column_types)

    entries_per_day = occupancy_table.pivot(['weekday'])

    monday_results = occupancy_table.where(lambda row: 'MONDAY' == row['weekday'])
    tuesday_results = occupancy_table.where(lambda row: 'TUESDAY' == row['weekday'])
    wednesday_results = occupancy_table.where(lambda row: 'WEDNESDAY' == row['weekday'])
    thursday_results = occupancy_table.where(lambda row: 'THURSDAY' == row['weekday'])
    friday_results = occupancy_table.where(lambda row: 'FRIDAY' == row['weekday'])
    saturday_results = occupancy_table.where(lambda row: 'SATURDAY' == row['weekday'])
    sunday_results = occupancy_table.where(lambda row: 'SUNDAY' == row['weekday'])

    # Possible to inspect datetime object with lambda...
    new_table = monday_results.where(lambda row: 6 <= row['date'].hour <= 8)

    analyzeDay(monday_results)
    # high_occ = monday_results.where(lambda row: 'HIGH' == row['occupancy'])
    #
    # low = monday_results.where(lambda row: 'LOW' == row['occupancy'])
    # binned_hours = high_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)
    # binned_hours2 = low.bins('hour', 23, 0, 23).print_bars('hour', width=80)


def analyzeDay(daily_results):
    # Print graph of entry / hour
    # daily_results.bins('hour', 23, 0, 23).print_bars('hour', width=80)

    # Print count of occupancy level / hour
    occupency_per_hour = daily_results.pivot(['hour', 'occupancy']).order_by('hour')
    # occupency_per_hour.print_table(max_rows=2000, max_columns=15)

    calculateRushHourConfidence(daily_results)


if __name__ == "__main__":
    main()
