from algos.pre_processing import filter_duplicates, filter_erroneous
from algos.statistics import *
from algos.data_transformation import *
from domain.occupancy import Occupancy
from domain.station import Station
from domain.stationEntry import StationEntry
from domain.city import City
from domain.entry import Entry
from utils.file_utils import parse_csv_file_to_list, parse_json_file_to_list
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree
import numpy as np
import agate

OCCUPANCY_DATA_FILE = 'occupancy-until-20161029.newlinedelimitedjsonobjects'
STATIONS_DATA_FILE = 'stations.csv'
OCCUPANCY_TEST_FILE = 'trains_test.csv'

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

occupancies_raw_data = parse_json_file_to_list(OCCUPANCY_DATA_FILE)
stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)
test_data_raw = agate.Table.from_csv(OCCUPANCY_TEST_FILE)


def main():
    days = ['MONDAY',
            'TUESDAY',
            'WEDNESDAY',
            'THURSDAY',
            'FRIDAY',
            'SATURDAY',
            'SUNDAY']

    daily_decision_trees = []
    for day in days:
        daily_decision_trees.append(trainTreeForSpecificDay(day))

    hell = '';
    clf_gini, clf_entropy = trainTreeForSpecificDay('TUESDAY')
    # predictTestData(clf_gini, clf_entropy)

    # y_pred = clf_gini.predict(X_test)
    # y_pred_ent = clf_entropy.predict(X_test)
    # print("Accuracy GINI is ", accuracy_score(y_test, y_pred) * 100)

    # print("Accuracy ENTROPY is ", accuracy_score(y_test, y_pred_ent) * 100)
    hell = ""


def trainTree():
    stations = {station.number: station for station in
                [Station(station_data, cities) for station_data in stations_raw_data]}
    occupancies = [Occupancy(occupancy_data, stations) for occupancy_data in occupancies_raw_data]

    occupancies = filter_duplicates(filter_erroneous(occupancies))

    column_names = ['day_period', 'is_weekday', "from_urban", "to_urban", "in_morning_rush",
                    "in_evening_rush", "vehicle_type",
                    "occupancy"]

    column_types = [agate.Number(), agate.Number(), agate.Number(), agate.Number(), agate.Number(), agate.Number(),
                    agate.Number(), agate.Text()]

    occupancy_attributes = []
    for occupancy in occupancies:
        occupancy_attributes.append(occupancy.to_attribute_list())

    occupancy_table = agate.Table(occupancy_attributes, column_names, column_types)

    level_column = ['occupancy']
    occupancy_level = occupancy_table.select(level_column)
    occupancy_level.print_table(max_rows=3000, max_columns=15)

    occupancy_table.print_table(max_rows=3000, max_columns=15)

    all_rows = np.array([[value for value in row.values()] for row in occupancy_table.rows])
    x = all_rows[:, 0:6]
    y = all_rows[:, 7]

    x_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=100)

    clf_gini = DecisionTreeClassifier(criterion="gini", max_depth=5, min_samples_leaf=1)
    clf_gini.fit(x_train, y_train)

    clf_entropy = DecisionTreeClassifier(criterion="entropy", max_depth=5, min_samples_leaf=2)
    clf_entropy.fit(x_train, y_train)

    feature_names = ['day_period', "from_urban", "to_urban", "in_morning_rush",
                     "in_evening_rush", "vehicle_type"]
    class_names = ['HIGH', 'LOW', 'MEDIUM']

    with open("iris.dot", 'w') as f:
        f = tree.export_graphviz(clf_entropy, feature_names=feature_names, class_names=class_names, filled=True,
                                 out_file=f)

    y_pred_ent = clf_entropy.predict(X_test)
    print("Accuracy is ", accuracy_score(y_test, y_pred_ent) * 100)

    return clf_gini, clf_entropy


def trainTreeForSpecificDay(day):
    occupancies_raw_data = parse_json_file_to_list(OCCUPANCY_DATA_FILE)
    stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)
    # test_data_raw = agate.Table.from_csv(OCCUPANCY_TEST_FILE)


    stations = {station.number: station for station in
                [Station(station_data, cities) for station_data in stations_raw_data]}
    occupancies = [Occupancy(occupancy_data, stations) for occupancy_data in occupancies_raw_data]

    occupancies = filter_erroneous(occupancies)

    column_names = ['day_period', "weekday", "from_urban", "to_urban", "vehicle_type",
                    "occupancy"]

    column_types = [agate.Number(), agate.Text(), agate.Number(), agate.Number(),
                    agate.Number(), agate.Text()]

    occupancy_attributes = []
    for occupancy in occupancies:
        occupancy_attributes.append(occupancy.to_numerical_attribute_list())

    occupancy_table = agate.Table(occupancy_attributes, column_names, column_types)

    target_column_names = ['day_period', "from_urban", "to_urban", "vehicle_type",
                           "occupancy"]

    occupancy_day = occupancy_table.where(lambda row: day == row['weekday'])

    occupancy_day.print_table(max_rows=3000, max_columns=15)

    occupancy_daily = occupancy_day.select(target_column_names)

    occupancy_daily.print_table(max_rows=3000, max_columns=15)

    all_rows = np.array([[value for value in row.values()] for row in occupancy_daily.rows])
    x = all_rows[:, 0:3]
    y = all_rows[:, 4]

    x_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=100)

    clf_gini = DecisionTreeClassifier(criterion="gini", max_depth=6, min_samples_leaf=3)
    clf_gini.fit(x_train, y_train)

    clf_entropy = DecisionTreeClassifier(criterion="entropy", max_depth=6, min_samples_leaf=3)
    clf_entropy.fit(x_train, y_train)

    feature_names = ['day_period', "from_urban", "to_urban", "vehicle_type"]
    class_names = ['HIGH', 'LOW', 'MEDIUM']

    # Code to export .dot to pdf:
    # dot -Tpdf iris.dot -o iris.pdf
    with open("iris.dot", 'w') as f:
        f = tree.export_graphviz(clf_entropy, feature_names=feature_names, class_names=class_names, filled=True,
                                 out_file=f)

    y_pred_ent = clf_entropy.predict(X_test)
    print("Accuracy is ", accuracy_score(y_test, y_pred_ent) * 100)

    return clf_gini, clf_entropy


def predictTestData(clf_gini, clf_entropy):
    stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)
    test_data_raw = agate.Table.from_csv(OCCUPANCY_TEST_FILE)

    stations = {station.number: station for station in
                [StationEntry(station_data, cities) for station_data in stations_raw_data]}

    test_entries = [Entry(occupancy_data, stations) for occupancy_data in test_data_raw]

    test_data_column_names = ['is_weekday', 'day_period', 'from_urban', 'to_urban',
                              'in_morning_rush', 'in_evening_rush',
                              "vehicle_type"
                              ]

    test_data_column_types = [agate.Number(), agate.Number(), agate.Number(), agate.Number(),
                              agate.Number(),
                              agate.Number(),
                              agate.Number()
                              ]

    test_list = []

    for occupancy in test_entries:
        test_list.append(occupancy.to_attribute_list())

    test_data_occupancy_table = agate.Table(test_list, test_data_column_names, test_data_column_types)

    test_data_occupancy_table.print_table(max_rows=3000, max_columns=15)

    all_rows = np.array([[value for value in row.values()] for row in test_data_occupancy_table.rows])

    x_test = all_rows[:, 0:6]

    y_pred_ent = clf_entropy.predict(x_test)

    # OCCUPANCY RATING:
    # 0 --> LOW
    # 1--> MEDIUM
    # 2--> HIGH

    LOW_OCCUPANCY = 0
    MEDIUM_OCCUPANCY = 1
    HIGH_OCCUPANCY = 2

    final_occupancies = []
    index = 0

    for prediction in y_pred_ent:
        if (prediction == 'LOW'):
            temp_occupancy = LOW_OCCUPANCY
        elif (prediction == 'MEDIUM'):
            temp_occupancy = MEDIUM_OCCUPANCY
        elif (prediction == 'HIGH'):
            temp_occupancy = HIGH_OCCUPANCY
        final_occupancies.append([index, temp_occupancy])
        index += 1

    columns = ['id', 'occupancy']
    columns_types = [agate.Number(), agate.Number()]

    results = agate.Table(final_occupancies, columns, columns_types)
    results.print_table(max_rows=3000, max_columns=15)

    results.to_csv('test_1.csv')


def predictData():
    stations_raw_data = parse_csv_file_to_list(STATIONS_DATA_FILE)
    test_data_raw = agate.Table.from_csv(OCCUPANCY_TEST_FILE)

    stations = {station.number: station for station in
                [Station(station_data, cities) for station_data in stations_raw_data]}

    test_entries = [Entry(occupancy_data, stations) for occupancy_data in test_data_raw]

    test_data_column_names = ['hour', 'is_weekday', 'from_urban', 'to_urban',
                              'in_morning_rush', 'in_evening_rush',
                              "vehicle_type"
                              ]

    test_data_column_types = [agate.Number(), agate.Number(), agate.Number(), agate.Number(),
                              agate.Number(),
                              agate.Number(),
                              agate.Number()
                              ]

    test_list = []

    for occupancy in test_entries:
        test_list.append(occupancy.to_attribute_list())

    test_data_occupancy_table = agate.Table(test_list, test_data_column_names, test_data_column_types)
    # test_data_occupancy_table.print_table(max_rows=1000, max_columns=15)

    final_occupancies = []

    # OCCUPANCY RATING:
    # 0 --> LOW
    # 1--> MEDIUM
    # 2--> HIGH

    LOW_OCCUPANCY = 0
    MEDIUM_OCCUPANCY = 1
    HIGH_OCCUPANCY = 2

    columns = ['id', 'occupancy']
    columns_types = [agate.Number(), agate.Number()]

    index = 0

    for test_entry in test_data_occupancy_table:
        if isEarlyMorning(test_entry):
            if (isSunday(test_entry) or isMonday(test_entry)) and isGoingUrban(test_entry):
                temp_occupency = HIGH_OCCUPANCY
            else:
                temp_occupency = LOW_OCCUPANCY

        if isLateEvening(test_entry):
            if isSunday(test_entry) and isGoingUrban(test_entry):
                temp_occupency = HIGH_OCCUPANCY
            if isMonday(test_entry) and isGoingUrban(test_entry) and isFromUrban(test_entry):
                temp_occupency = MEDIUM_OCCUPANCY
            else:
                temp_occupency = LOW_OCCUPANCY

        elif isBeforeNoon(test_entry):
            if isWeekend(test_entry):
                if isSunday(test_entry) and isFromUrban(test_entry) and isGoingUrban(test_entry):
                    temp_occupency = MEDIUM_OCCUPANCY
                else:
                    temp_occupency = LOW_OCCUPANCY

            elif isMorningRush(test_entry):
                if isFromUrban(test_entry) and isGoingUrban(test_entry):
                    if isWednesday(test_entry):
                        temp_occupency = HIGH_OCCUPANCY
                    else:
                        temp_occupency = MEDIUM_OCCUPANCY

                elif isFromUrban(test_entry) and not isGoingUrban(test_entry):
                    temp_occupency = LOW_OCCUPANCY
                else:
                    temp_occupency = LOW_OCCUPANCY
            else:
                temp_occupency = LOW_OCCUPANCY

        elif isAfternoon(test_entry):
            if isWeekend(test_entry):
                if isSunday(test_entry) and isFromUrban(test_entry) and not isGoingUrban(test_entry):
                    temp_occupency = MEDIUM_OCCUPANCY
                else:
                    temp_occupency = LOW_OCCUPANCY

            elif isEveningRush(test_entry):
                if isFromUrban(test_entry) and isGoingUrban(test_entry):
                    temp_occupency = HIGH_OCCUPANCY

                elif isFromUrban(test_entry) and not isGoingUrban(test_entry):
                    if isFriday(test_entry) or isMonday(test_entry) or isTuesday(test_entry):
                        temp_occupency = HIGH_OCCUPANCY
                    elif isWednesday(test_entry):
                        temp_occupency = MEDIUM_OCCUPANCY
                    else:
                        temp_occupency = MEDIUM_OCCUPANCY

                elif isGoingUrban(test_entry) and not isFromUrban(test_entry):
                    if isThursday(test_entry):
                        temp_occupency = HIGH_OCCUPANCY
                    elif isTuesday(test_entry) and isFriday(test_entry):
                        temp_occupency = LOW_OCCUPANCY
                    else:
                        temp_occupency = MEDIUM_OCCUPANCY
                else:
                    temp_occupency = LOW_OCCUPANCY

            else:
                if isFromUrban(test_entry) and isGoingUrban(test_entry):
                    if isMonday(test_entry):
                        temp_occupency = MEDIUM_OCCUPANCY
                    else:
                        temp_occupency = LOW_OCCUPANCY
                else:
                    temp_occupency = LOW_OCCUPANCY

        elif isLateEvening(test_entry):
            if isWednesday(test_entry) or isSunday(test_entry):
                temp_occupency = HIGH_OCCUPANCY
            elif isMonday(test_entry):
                temp_occupency = MEDIUM_OCCUPANCY
            else:
                temp_occupency = LOW_OCCUPANCY
        else:
            temp_occupency = LOW_OCCUPANCY

        final_occupancies.append([index, temp_occupency])
        index += 1

    results = agate.Table(final_occupancies, columns, columns_types)
    results.print_table(max_rows=3000, max_columns=15)

    results.to_csv('test_1.csv')


def analyzeDay(daily_results):
    # Print graph of entry / hour
    # daily_results.bins('hour', 23, 0, 23).print_bars('hour', width=80)

    # Print count of occupancy level / hour
    occupency_per_hour = daily_results.pivot(['hour', 'occupancy']).order_by('hour')
    # occupency_per_hour.print_table(max_rows=2000, max_columns=15)

    calculateRushHourConfidence(daily_results)


if __name__ == "__main__":
    main()
