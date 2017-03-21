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

    calculateOccupancyStatistics(daily_results)


def calculateOccupancyStatistics(occupancies):
    morning_rushhour_start = 7
    morning_rushhour_end = 9
    evening_rushhour_start = 16
    evening_rushhour_end = 20

    numberOfEntries = len(occupancies.rows)

    # Calculate % of HIGH level during rushhour period
    high_occ = occupancies.where(lambda row: 'HIGH' == row['occupancy'])

    entries_in_rushhour = high_occ.where(
        lambda row: morning_rushhour_start <= row['date'].hour <= morning_rushhour_end or evening_rushhour_start <= row[
            'date'].hour <= evening_rushhour_end)

    print(len(entries_in_rushhour) / len(high_occ))

    avg_occ = occupancies.where(lambda row: 'MEDIUM' == row['occupancy'])
    low_occ = occupancies.where(lambda row: 'LOW' == row['occupancy'])

    # Print graph of LOW occ / hour
    print("LOW OCCUPANCY")
    low_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)

    # Print graph of MEDIUM occ / hour
    print("MEDIUM OCCUPANCY")
    avg_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)

    # Print graph of HIGH occ / hour
    print("HIGH OCCUPANCY")
    high_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)


if __name__ == "__main__":
    main()
