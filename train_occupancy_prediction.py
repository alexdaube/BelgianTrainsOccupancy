from algos.pre_processing import filter_duplicates, filter_erroneous
from algos.statistics import *
from algos.data_transformation import calculateRushHourConfidence
from domain.occupancy import Occupancy
from domain.station import Station
from domain.city import City
from utils.file_utils import parse_csv_file_to_list, parse_json_file_to_list
import agate

OCCUPANCY_DATA_FILE = 'occupancy-until-20161029.newlinedelimitedjsonobjects'
STATIONS_DATA_FILE = 'stations.csv'


def main():
    occupancies_raw_data = parse_json_file_to_list(OCCUPANCY_DATA_FILE)
    stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)

    cities = [City("Brussels", 50.786350, 50.918930, 4.276428, 4.4991348),
              City("Antwerp", 51.173693, 51.317015, 4.254456, 4.507141),
              City("Ghent", 51.002832, 51.103832, 3.69072, 3.766251),
              City("Charleroi", 50.403524, 50.418660, 4.434013, 4.457359),
              City("Liège", 50.581055, 50.647440, 5.557022, 5.596504),
              City("Bruges", 51.195129, 51.223843, 3.212128, 3.24337),
              City("Namur", 50.461298, 50.470258, 4.848919, 4.878101),
              City("Leuven", 50.867048, 50.890551, 4.681377, 4.716396),
              City("Mons", 50.445013, 50.461189, 3.9382, 3.961773),
              City("Aalst", 50.927354, 50.949854, 4.015331, 4.054985),
              City("Lille", 50.615894, 50.651607, 3.028107, 3.08527)]

    stations = {station.number: station for station in
                [Station(station_data, cities) for station_data in stations_raw_data]}
    occupancies = [Occupancy(occupancy_data, stations) for occupancy_data in occupancies_raw_data]

    occupancies = filter_duplicates(filter_erroneous(occupancies))

    column_names = ['date', 'hour', 'weekday', "from", "from_urban", "to", "to_urban", "in_morning_rush",
                    "in_evening_rush", "vehicle", "vehicle_type",
                    "occupancy"]

    column_types = [agate.DateTime(), agate.Number(), agate.Text(), agate.Number(), agate.Number(), agate.Number(),
                    agate.Number(), agate.Number(), agate.Number(), agate.Text(),
                    agate.Text(),
                    agate.Text()]

    occupancies_list = []
    for occupancy in occupancies:
        occupancies_list.append(occupancy.to_list())

    occupancy_table = agate.Table(occupancies_list, column_names, column_types)

    occupancy_table.order_by('to').print_csv()
    print(len(occupancy_table))

    print("Occupancy in both rush")
    #
    # occupancy_table.where(lambda row: 1 == row['in_morning_rush']).where(
    #     lambda row: 'SATURDAY' != row['weekday'] and 'SUNDAY' != row['weekday']).pivot('to_urban',
    #                                                                                    'occupancy').print_csv()
    # print("\n")
    #
    # occupancy_table.where(lambda row: 1 == row['in_morning_rush']).where(
    #     lambda row: 'SATURDAY' != row['weekday'] and 'SUNDAY' != row['weekday']).pivot('from_urban',
    #                                                                                    'occupancy').print_csv()
    # print("\n")
    #
    # occupancy_table.where(lambda row: 1 == row['in_evening_rush']).where(
    #     lambda row: 'SATURDAY' != row['weekday'] and 'SUNDAY' != row['weekday']).pivot('from_urban',
    #                                                                                    'occupancy').print_csv()
    # print("\n")
    #
    # occupancy_table.where(lambda row: 'FRIDAY' == row['weekday']).pivot('from_urban', 'occupancy').print_csv()
    # print("\n")
    # occupancy_table.where(lambda row: 'SUNDAY' == row['weekday']).pivot('to_urban', 'occupancy').print_csv()
    #
    # print("\n")

    am_early_entries = occupancy_table.where(lambda row: 3 <= row['date'].hour or row['date'].hour < 6)
    am_entries = occupancy_table.where(lambda row: 6 <= row['date'].hour < 12)
    pm_entries = occupancy_table.where(lambda row: 12 <= row['date'].hour <= 22)
    pm_late_entries = occupancy_table.where(lambda row: 22 < row['date'].hour or row['date'].hour < 3)

    print("\nAM entries")
    data = am_early_entries.pivot('vehicle', 'occupancy').order_by('vehicle')

    data.print_table(max_rows=2000, max_columns=15)

    allo = data.columns['LOW']
    print(allo)

    # am_entries.pivot('vehicle', 'occupancy').order_by('vehicle').print_table(max_rows=2000, max_columns=15)
    # pm_entries.pivot('vehicle', 'occupancy').order_by('vehicle').print_table(max_rows=2000, max_columns=15)
    # pm_late_entries.pivot('vehicle', 'occupancy').order_by('vehicle').print_table(max_rows=2000, max_columns=15)
    # am_entries.pivot('to_urban').print_table()
    # am_entries.pivot('in_morning_rush', 'to_urban').print_table()
    #
    # print("\nPM entries")
    # pm_entries.pivot('to_urban').print_table()
    # pm_entries.pivot('in_evening_rush', 'to_urban').print_table()



    # occupancy_table.pivot('in_evening_rush', 'to_urban').print_table()

    #
    # print("\nOCCUPANCY BY VEHICLE_TYPE => \n")
    # percent_occupancy_for_column(occupancy_table, 'vehicle_type', "THA")
    # percent_occupancy_for_column(occupancy_table, 'vehicle_type', "IC")
    # percent_occupancy_for_column(occupancy_table, 'vehicle_type', "L")
    # percent_occupancy_for_column(occupancy_table, 'vehicle_type', "S")
    # percent_occupancy_for_column(occupancy_table, 'vehicle_type', "P")
    #
    # print("\nOCCUPANCY BY WEEKDAY => \n")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "MONDAY")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "TUESDAY")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "WEDNESDAY")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "THURSDAY")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "FRIDAY")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "SATURDAY")
    # percent_occupancy_for_column(occupancy_table, 'weekday', "SUNDAY")
    #
    # g_by = occupancy_table.group_by("to")
    # for t in g_by:
    #     print("\n")
    #     t.print_csv()
    #
    # # entries_per_day = occupancy_table.pivot(['weekday'])
    # #git s
    # monday_results = occupancy_table.where(lambda row: 'MONDAY' == row['weekday'])
    # tuesday_results = occupancy_table.where(lambda row: 'TUESDAY' == row['weekday'])
    # wednesday_results = occupancy_table.where(lambda row: 'WEDNESDAY' == row['weekday'])
    # thursday_results = occupancy_table.where(lambda row: 'THURSDAY' == row['weekday'])
    # friday_results = occupancy_table.where(lambda row: 'FRIDAY' == row['weekday'])
    # saturday_results = occupancy_table.where(lambda row: 'SATURDAY' == row['weekday'])
    # sunday_results = occupancy_table.where(lambda row: 'SUNDAY' == row['weekday'])
    # #
    # # # monday_results.order_by('date').print_table(max_rows=2000, max_columns=15)
    # #
    # # monday_results.group_by('occupancy').order_by('date').merge().print_table(max_rows=2000, max_columns=15)
    #
    # # Possible to inspect datetime object with lambda...
    # new_table = monday_results.where(lambda row: 6 <= row['date'].hour <= 8)
    #
    # print("\n############MONDAY###############")
    # analyzeDay(monday_results)
    # print("\n############TUESDAY###############")
    # analyzeDay(tuesday_results)
    # print("\n############WEDNESDAY###############")
    # analyzeDay(wednesday_results)
    # print("\n############THURSDAY###############")
    # analyzeDay(thursday_results)
    # print("\n############FRIDAY###############")
    # analyzeDay(friday_results)
    # print("\n############SATURDAY###############")
    # analyzeDay(saturday_results)
    # print("\n############SUNDAY###############")
    # analyzeDay(sunday_results)
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
